#!/usr/bin/env python3
"""How much of a protein's lipid preference is predictable from the protein side alone,
without any lipid input -- three modes, sharing one target (class_profiles: one 34-wide
binding-profile vector per protein) and one reference baseline (esm3_neighbour_reference)
that all three used to recompute or re-import separately.

The pair task mixes two questions: what the protein is like, and how a given lipid fits
it. All three modes ask only the first. The target is the protein's binding PROFILE --
for each head-group class, the share of that class's lipids the protein binds -- so one
vector of 34 numbers per protein, 35 proteins in all, and no lipid input anywhere.

Shared reference, used by every mode: with a whole family held out, predicting its
proteins' profiles as the mean of the training proteins scores 0.169 by cosine on
average, and copying the three nearest neighbours in mean-pooled ESM3 space scores
0.190 -- on four families of seven the neighbours do worse than the mean. Those bracket
what any method reading only the protein side can reach here.

MODE `train` (default, no leading mode word needed -- was this module's own original
behaviour and stays byte-for-byte compatible with every existing invocation): actually
trains a small 34-wide linear head on the REAL branch, reached by hooking the pooling
module of a fully built InteractionClassification model, so a result here transfers to
the model that runs. A branch that lands on the mean reference is extracting nothing and
the fault is in the branch; one that reaches the neighbour line is extracting what there
is and the fault is in the input.

    python3 analysis/protein_profile_probe.py --excluded_groups=START --ep=200 \\
        --protein_disable_post_sa_mlp --lipid_disable_post_sa_mlp \\
        --third_layers_in_mlps --fast_attention --hiddim=64 --plm_compression_dim=64

(Holding out one PROTEIN instead of one family is a much easier problem -- its
relatives stay in training -- and reaches 0.259 and 0.335. Those numbers do not apply
to a family-held-out split.)

What `train` cannot do is add information. The bound belongs to the input, not to the
head.

MODE `similarity` -- no training, no model: does STRUCTURAL pocket comparison predict
the profile better than ESM3 sequence similarity does? files/reference/marginals_and_
cold_split.md 9 (C2) records two things that already failed to improve on ignoring the
protein: 13 aggregate pocket descriptors as a direct predictor of binding profile
(0.284, worse than the 0.259 single-protein-holdout mean baseline), and mean-pooled ESM3
restricted to pocket residues instead of the whole chain (0.192 cosine, worse than 0.227
for the whole chain). Both reduce a pocket to a handful of aggregate numbers -- means,
sums, one principal-axis ratio -- which is exactly the reduction structural
pocket-matching literature says throws away the signal: shared ligand binding correlates
with pocket SHAPE, not with sequence or aggregate statistics (Ito et al. 2012;
comparative review, Chikhi/Sael/Kihara BMC Bioinformatics 2018,
10.1186/s12859-018-2109-2; DeeplyTough, Simonovsky & Meyers, JCIM 2020,
10.1021/acs.jcim.9b00554).

What this measures: a structural comparison of pocket A against pocket B, in the
PocketMatch spirit (Yeturu & Chandra, BMC Bioinformatics 2008) -- describe a pocket by
the sorted list of ALL pairwise distances between its own pocket atoms, resample that
sorted list onto a common quantile grid so pockets of different atom counts become
comparable, and take the negative L2 distance between two pockets' resampled profiles
as their similarity. No structural alignment/superposition is attempted -- the
sorted-distance list is already invariant to rotation and translation by construction.
Distances are kept in Angstroms, not rescaled to a unit pocket, because scale is part
of what determines whether an acyl chain fits (this project's own `pocket_extent`
descriptor makes the same choice). Then run through the exact `train`-mode test (three
nearest neighbours, now by pocket shape instead of ESM3, vote by averaging, scored by
cosine) -- same anchors, so a result here is directly comparable without adjustment.

    python3 analysis/protein_profile_probe.py similarity
    python3 analysis/protein_profile_probe.py similarity --quantiles=100 --neighbours=5

MODE `correlate` -- no training, no model: do the cavity's own SHAPE descriptors
(preprocessing/pocket_shape_descriptors.py -- how far the cavity extends, how elongated it
is, how its enclosure is distributed) correlate with simpler, more interpretable
binding-derived targets (mean acyl chain length of a protein's positives; how many
distinct head-group classes it accepts), controlling for protein size and for protein
family? The older measurement this replaces correlated three size-like descriptors
(pocket SASA, volume, residue count) with chain length and reported that only SASA
survived -- on 32 proteins, where the 0.05 threshold sits at |r| = 0.355 and the three
candidates landed at 0.57, 0.33 and 0.32 (a threshold crossed or missed, not three
different findings). Every correlation here is reported with its confidence interval,
because on 32-35 points the interval is the finding and the point estimate is
decoration.

The confound this has to survive: within a family, proteins have similar pockets AND
bind similar lipids, so "longer cavity, longer chain" reads equally well as "this is a
GLTP". Two designs answer it, both run:
  * across all proteins, family's own contribution to the TARGET measured first (a
    target with no family structure at all still scores ~0.25 on this project's 9
    families over ~33 proteins, by arithmetic alone) -- a target family barely explains
    (head-group-class count, 0.22) is the clean one to read a descriptor's correlation
    against; one family mostly IS (sphingolipid share, 0.83) is not.
  * within one family at a time (lipocalin, CRAL-TRIO -- the only two large enough to
    try), where family is constant by construction and cannot be the explanation;
    nothing can reach significance at these sizes, so what is read is AGREEMENT: a
    descriptor pointing the same way inside both families and in the pooled result is
    saying something family cannot account for.

    python3 analysis/protein_profile_probe.py correlate

Usage note for `train`: config flags are read the same way training itself reads them
(training/read_configuration.py's own custom parser, not argparse) -- a flag never
starts with a bare word, so an explicit "train" before them is optional and the module
accepts the original bare-flag invocation unchanged.
"""

import glob
import os
import sys

import numpy as np
import pandas
import torch

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "training"))

from dataloader.Dataloader import PLIDataset
from dataloader.dataset_source import interaction_csv_path
from dataloader.sampler import lipid_class_series
from architecture.interaction_classification import InteractionClassification
from training.read_configuration import read_configuration
from forward_args import build_forward_args

# The seven families files/reference/marginals_and_cold_split.md reports throughout --
# ML and OSBP are excluded from --double_coldsplit for having too few positives for a
# test block (COLDSPLIT_MINIMUM_TEST_POSITIVES in dataloader/sampler.py), so no anchor
# number exists for them and adding them here would not be comparable to anything.
FAMILIES = ("CRAL-TRIO", "GLTP", "IP_trans", "LBP_BPI_CETP", "START", "lipocalin", "scp2")


# ========================================================================= shared


def class_profiles(csv):
    """One row per protein: the share of each head-group class's lipids it binds."""
    frame = csv.copy()
    frame["lipid_class"] = lipid_class_series(frame)
    table = (
        frame.pivot_table(
            index="LTPProtein",
            columns="lipid_class",
            values="Interaction",
            aggfunc="mean",
        )
        .fillna(0.0)
        .sort_index(axis=1)
    )
    return table


def cosine(a, b):
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    return float(a @ b / denominator) if denominator else 0.0


def esm3_neighbour_reference(train_names, held_names, profiles):
    """Profile cosine reached by copying the three nearest training proteins.

    The reference every mode has to beat, computed for THIS split rather than quoted
    from another one. Holding a whole family out is a different problem from holding
    one protein out: leave-one-protein-out leaves the protein's own relatives in
    training and reaches 0.335 on average, while leaving the family out reaches 0.190,
    and on four families of seven it does worse than ignoring the protein entirely.
    Printing the easier number next to a family-held-out result would flatter the head
    or damn it for no reason.
    """
    import pickle

    means = {}
    for path in glob.glob(os.path.join(PROJECT_ROOT, "data", "embedding_ESM3", "*")):
        name = os.path.basename(path).split("_")[0]
        with open(path, "rb") as handle:
            stored = pickle.load(handle)
        if isinstance(stored, dict):
            stored = next(iter(stored.values()))
        tensor = torch.as_tensor(stored).float()
        if tensor.dim() == 3:
            tensor = tensor[0]
        means[name] = tensor.numpy().mean(axis=0)

    usable = [n for n in train_names if n in means]
    scores = []
    for name in held_names:
        if name not in means:
            continue
        nearest = sorted(usable, key=lambda t: -cosine(means[name], means[t]))[:3]
        predicted = profiles.loc[nearest].to_numpy().mean(axis=0)
        scores.append(cosine(profiles.loc[name].to_numpy(), predicted))
    return float(np.mean(scores)) if scores else float("nan")


# ========================================================================= mode `train`


def one_row_per_protein(dataset):
    """Positions in `dataset.csv` of the first row of each protein it holds."""
    seen = {}
    for position, protein in enumerate(dataset.csv["LTPProtein"].tolist()):
        seen.setdefault(protein, position)
    return seen


def pooled_protein_vectors(conf, model, loader, device):
    """Run the real branch over one loader pass and catch what its pooling produces.

    A forward hook rather than final_layer._pooled_partners: that one is detached and
    filled only outside training, and this needs gradients.
    """
    pooling = getattr(model.final_layer, "prot_gem_pool", None)
    if pooling is None:
        raise RuntimeError(
            "the probe reads the protein vector off prot_gem_pool, which only exists "
            "under --pool_type=gem; run it with the pooling the model uses"
        )
    captured = []
    handle = pooling.register_forward_hook(
        lambda _module, _inputs, output: captured.append(output)
    )
    try:
        for prot, lipid in loader:
            prot = prot.to(device)
            lipid = lipid.to(device)
            model(**build_forward_args(conf, prot, lipid))
        if not captured:
            raise RuntimeError("the pooling hook never fired")
        return torch.cat(captured, dim=0)
    finally:
        handle.remove()


def run_train():
    conf = read_configuration()
    conf.save_dynamics = False
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    csv = pandas.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data")))
    profiles = class_profiles(csv)

    # The loader joins root_dir with plain file names, so it wants the data directory
    # itself -- the trailing separator is what training/new_train.py passes too.
    train_dataset, valid_dataset, test_dataset = PLIDataset(
        root_dir=os.path.join(PROJECT_ROOT, "data") + os.sep,
        csv=csv,
        seed=conf.seed,
        excluded_subgroups=conf.excluded_subgroups,
        config=conf,
        excluded_groups=conf.excluded_groups,
    )

    train_positions = one_row_per_protein(train_dataset)
    held_positions = one_row_per_protein(test_dataset)
    print(f"proteins in train : {len(train_positions)}")
    print(f"proteins held out : {len(held_positions)} ({', '.join(sorted(held_positions))})")

    model = InteractionClassification(conf).to(device)
    head = torch.nn.Linear(conf.hiddim, profiles.shape[1]).to(device)
    optimiser = torch.optim.Adam(
        list(model.protein1.parameters()) + list(head.parameters()), lr=conf.lr
    )

    import torch_geometric

    # Micro-batched on purpose: all 32 protein graphs at once, each hundreds of
    # residues wide with a 1536-long embedding per residue, was enough to have the
    # frontend's OOM killer take the process before the first epoch. The hook collects
    # every batch's pooled vectors and they are concatenated, so the gradient is the
    # same as a single batch would give -- only the peak differs.
    probe_batch = max(1, int(getattr(conf, "batch", 8)))

    def loader_for(dataset, positions, names):
        subset = torch.utils.data.Subset(dataset, [positions[n] for n in names])
        return torch_geometric.loader.DataLoader(
            subset, batch_size=min(probe_batch, len(names)), shuffle=False
        )

    train_names = sorted(train_positions)
    held_names = sorted(held_positions)
    train_loader = loader_for(train_dataset, train_positions, train_names)
    held_loader = loader_for(test_dataset, held_positions, held_names)
    target = torch.tensor(
        profiles.loc[train_names].to_numpy(dtype="float32"), device=device
    )

    for epoch in range(conf.ep):
        model.train(True)
        optimiser.zero_grad(set_to_none=True)
        pooled = pooled_protein_vectors(conf, model, train_loader, device)
        loss = torch.nn.functional.mse_loss(head(pooled), target)
        loss.backward()
        optimiser.step()
        if (epoch + 1) % 25 == 0:
            print(f"epoch {epoch + 1:>4} : train mse {loss.item():.5f}")

    model.train(False)
    with torch.no_grad():
        predicted = head(
            pooled_protein_vectors(conf, model, held_loader, device)
        ).cpu().numpy()

    truth = profiles.loc[held_names].to_numpy()
    mean_profile = profiles.loc[train_names].to_numpy().mean(axis=0)
    learned = float(np.mean([cosine(t, p) for t, p in zip(truth, predicted)]))
    constant = float(np.mean([cosine(t, mean_profile) for t in truth]))
    print()
    neighbour = esm3_neighbour_reference(train_names, held_names, profiles)
    print(f"held-out profile cosine, learned head   : {learned:.3f}")
    print(f"held-out profile cosine, mean of train  : {constant:.3f}")
    print(f"held-out profile cosine, 3 nearest ESM3 : {neighbour:.3f}")


# ===================================================================== mode `similarity`


def pocket_shape_profile(coordinates, quantiles):
    """Sorted intra-pocket atom-pair distances, resampled to `quantiles` order statistics.

    Rotation/translation-invariant by construction (only distances enter), and
    comparable across pockets of different atom counts because each one is read as its
    own empirical quantile function and resampled onto the same grid -- the same
    resampling `architecture.final_layer.SlicedWassersteinPool` applies to residue
    embeddings, applied here to a pocket's internal geometry instead.
    """
    if len(coordinates) < 2:
        raise ValueError("a pocket needs at least two atoms to have an internal distance")
    diff = coordinates[:, None, :] - coordinates[None, :, :]
    distances = np.sqrt((diff ** 2).sum(axis=-1))
    upper = distances[np.triu_indices(len(coordinates), k=1)]
    sorted_distances = np.sort(upper)
    positions = (np.arange(quantiles) + 0.5) / quantiles * len(sorted_distances)
    lower = np.clip(np.floor(positions).astype(int), 0, len(sorted_distances) - 1)
    upper_index = np.clip(lower + 1, 0, len(sorted_distances) - 1)
    weight = np.clip(positions - lower, 0.0, 1.0)
    return sorted_distances[lower] + weight * (sorted_distances[upper_index] - sorted_distances[lower])


def pocket_similarity_matrix(quantiles):
    """Negative-L2-distance similarity between every pair of the 35 proteins' pockets."""
    from preprocessing.compute_descriptors import pocket_atom_coordinates

    profiles = {}
    for path in sorted(glob.glob(os.path.join(PROJECT_ROOT, "data", "graphs", "*", "pocketness.pdb"))):
        name = os.path.basename(os.path.dirname(path))
        coordinates = pocket_atom_coordinates(path)
        profiles[name] = pocket_shape_profile(coordinates, quantiles)
    names = sorted(profiles)
    matrix = np.zeros((len(names), len(names)))
    for i, a in enumerate(names):
        for j, b in enumerate(names):
            matrix[i, j] = -float(np.linalg.norm(profiles[a] - profiles[b]))
    return pandas.DataFrame(matrix, index=names, columns=names)


def pocket_neighbour_reference(train_names, held_names, profiles, similarity, neighbours):
    """Profile cosine reached by copying the `neighbours` most pocket-similar proteins.

    Mirrors esm3_neighbour_reference exactly, substituting the similarity source --
    structural pocket shape instead of mean-pooled ESM3 -- so the two numbers differ
    only in what they read, not in how the test is scored.
    """
    usable = [n for n in train_names if n in similarity.index]
    scores = []
    for name in held_names:
        if name not in similarity.index:
            continue
        nearest = similarity.loc[name, usable].sort_values(ascending=False).index[:neighbours]
        predicted = profiles.loc[nearest].to_numpy().mean(axis=0)
        scores.append(cosine(profiles.loc[name].to_numpy(), predicted))
    return float(np.mean(scores)) if scores else float("nan")


def run_similarity(argv):
    import argparse

    from read_configuration import EXCLUDED_SUBGROUPS_BY_NAME

    parser = argparse.ArgumentParser(description="mode: similarity")
    parser.add_argument("--quantiles", type=int, default=50)
    parser.add_argument("--neighbours", type=int, default=3)
    args = parser.parse_args(argv)

    csv = pandas.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep))
    profiles = class_profiles(csv)
    similarity = pocket_similarity_matrix(args.quantiles)

    rows = []
    for family in FAMILIES:
        held_names = [
            name for name in EXCLUDED_SUBGROUPS_BY_NAME[family] if name in profiles.index
        ]
        train_names = [name for name in profiles.index if name not in held_names]
        mean_profile = profiles.loc[train_names].to_numpy().mean(axis=0)
        constant = float(np.mean(
            [cosine(profiles.loc[n].to_numpy(), mean_profile) for n in held_names]
        ))
        esm3 = esm3_neighbour_reference(train_names, held_names, profiles)
        pocket = pocket_neighbour_reference(
            train_names, held_names, profiles, similarity, args.neighbours
        )
        rows.append({
            "family": family,
            "proteins_held_out": len(held_names),
            "mean_of_train": constant,
            "esm3_3_nearest": esm3,
            "pocket_shape_nearest": pocket,
        })

    table = pandas.DataFrame(rows).set_index("family")
    pandas.set_option("display.width", 200)
    print(table.round(3).to_string())
    print()
    means = table[["mean_of_train", "esm3_3_nearest", "pocket_shape_nearest"]].mean()
    print("mean over seven families:")
    print(means.round(3).to_string())
    beats_mean = (table["pocket_shape_nearest"] > table["mean_of_train"]).sum()
    beats_esm3 = (table["pocket_shape_nearest"] > table["esm3_3_nearest"]).sum()
    print(f"\npocket shape beats mean-of-train on {beats_mean}/7 families")
    print(f"pocket shape beats ESM3-3-nearest on {beats_esm3}/7 families")


# ===================================================================== mode `correlate`


def chain_length_per_protein():
    """Mean longest-chain length over the positives of each protein."""
    from dataloader.pocket_lipid_compatibility import EMPTY
    from preprocessing.compute_descriptors import longest_acyl_chain

    table = pandas.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep))
    positives = table[table["Interaction"] == 1]
    lengths = {}
    for protein, rows in positives.groupby("LTPProtein"):
        values = []
        for _, row in rows.iterrows():
            for column in ("SmileGlobal", "SmileFragment"):
                text = str(row[column]).strip()
                if text in EMPTY:
                    continue
                first = text.split(";")[0].strip()
                length = longest_acyl_chain(first)
                if length:
                    values.append(length)
                break
        if values:
            lengths[protein] = float(np.mean(values))
    return pandas.Series(lengths, name="mean_chain_length")


def legacy_size_descriptors(protein_dir):
    """The size-like descriptors the model already has, for comparison on the same data.

    Recomputed here rather than imported so the old and the new are measured against
    the same target, on the same proteins, with the same test -- the whole point of the
    comparison. Definitions follow pocket_descriptor() in preprocessing/compute_descriptors.py.
    """
    from preprocessing.pocket_shape_descriptors import read_pocket_atoms

    nodes = pandas.read_csv(protein_dir / "coarse_graph_nodes.csv")
    _, pocket_residues, _ = read_pocket_atoms(protein_dir / "pocketness.pdb")
    key = [str(int(value)) if float(value).is_integer() else str(value)
           for value in nodes["ID_resSeq"]]
    mask = np.array([residue in pocket_residues for residue in key])
    if mask.sum() == 0:
        return None
    site = nodes[mask]
    sasa = float(site["residue_sas_area"].sum())
    volume = float(site["residue_volume"].sum())
    return {
        "protein": protein_dir.name,
        "OLD_pocket_sasa": sasa,
        "OLD_pocket_volume": volume,
        "OLD_pocket_residue_count": float(mask.sum()),
        "OLD_pocket_sasa_share": sasa / max(float(nodes["residue_sas_area"].sum()), 1e-9),
        "OLD_pocket_volume_share": volume / max(float(nodes["residue_volume"].sum()), 1e-9),
    }


def head_classes_per_protein():
    """How many distinct head-group classes each protein's positives cover.

    The class is the shorthand prefix of the lipid name -- PC(34:1) is a
    phosphatidylcholine -- so this counts chemistry types, not molecules. Chosen as the
    second target because family barely determines it (0.22 against a 0.25 no-structure
    floor), unlike chain length (0.48) or the share of sphingolipids (0.83), which is
    the family itself: sphingolipid transfer proteins are a family.
    """
    table = pandas.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep))
    positives = table[table["Interaction"] == 1].copy()
    positives["head"] = (
        positives["Lipid"].astype(str).str.extract(r"^\s*([A-Za-z][A-Za-z0-9\-]*)\s*\(")[0]
    )
    positives = positives.dropna(subset=["head"])
    counts = positives.groupby("LTPProtein")["head"].nunique()
    counts.name = "head_classes"
    return counts


def protein_families_series():
    """Family of each protein, as a 'family'-named Series -- analysis.feature_identity_
    check.protein_family_map's own groupby/agg, reused rather than duplicated (it
    already returns one Series per protein, this only names it for the .join() below).
    """
    from analysis.feature_identity_check import protein_family_map

    csv = pandas.read_csv(interaction_csv_path(os.path.join(PROJECT_ROOT, "data") + os.sep))
    return protein_family_map(csv).rename("family")


def partial_spearman(x, y, control):
    """Spearman correlation of x and y with `control` regressed out of both (on ranks)."""
    from scipy import stats

    rx, ry, rc = (stats.rankdata(v) for v in (x, y, control))
    rc = np.column_stack([np.ones_like(rc), rc])
    resid_x = rx - rc @ np.linalg.lstsq(rc, rx, rcond=None)[0]
    resid_y = ry - rc @ np.linalg.lstsq(rc, ry, rcond=None)[0]
    r = float(np.corrcoef(resid_x, resid_y)[0, 1])
    n = len(x)
    return r, n


def interval(r, n, controls=1):
    """Fisher confidence interval and two-sided p for a (partial) correlation."""
    import math

    from scipy import stats

    if abs(r) >= 1 or n - 3 - controls <= 0:
        return float("nan"), float("nan"), float("nan")
    se = 1 / math.sqrt(n - 3 - controls)
    z = 0.5 * math.log((1 + r) / (1 - r))
    lo, hi = (math.tanh(z - 1.96 * se), math.tanh(z + 1.96 * se))
    df = n - 2 - controls
    t = r * math.sqrt(df / max(1 - r * r, 1e-12))
    p = 2 * stats.t.sf(abs(t), df)
    return lo, hi, p


CORRELATE_TARGET_COLUMNS = ("mean_chain_length", "head_classes")
CORRELATE_SKIP_AS_CANDIDATE = CORRELATE_TARGET_COLUMNS + ("family",)


def report_pooled(data, target_column):
    """Every descriptor against one target over all proteins, protein size controlled."""
    import math

    from scipy import stats

    candidates = [c for c in data.columns if c not in CORRELATE_SKIP_AS_CANDIDATE]
    control = data["protein_residues"].to_numpy(dtype=float)
    target_values = data[target_column].to_numpy(dtype=float)
    threshold = stats.t.ppf(0.975, len(data) - 3)
    print(f"\n=== all proteins, target: {target_column} (n = {len(data)}, "
          f"|r| for p<0.05 is "
          f"{threshold / math.sqrt(len(data) - 3 + threshold ** 2):.3f}) ===")

    results = []
    for name in candidates:
        values = data[name].to_numpy(dtype=float)
        if np.allclose(values, values[0]) or np.isnan(values).any():
            continue
        raw = stats.spearmanr(values, target_values).statistic
        partial, n = partial_spearman(values, target_values, control)
        lo, hi, p = interval(partial, n)
        results.append((name, raw, partial, lo, hi, p))
    results.sort(key=lambda row: -abs(row[2]))

    print(f"{'descriptor':<26}{'raw rho':>9}{'partial':>9}{'95% CI':>20}{'p':>9}{'BH':>7}")
    # Benjamini-Hochberg over everything tested here: with this many candidates on this
    # few proteins, the smallest p is expected to look impressive even under pure noise,
    # and the column says whether it still does after that is accounted for.
    tested = len(results)
    for rank, (name, raw, partial, lo, hi, p) in enumerate(results[:12], start=1):
        survives = "yes" if p <= 0.05 * rank / tested else "no"
        print(f"{name:<26}{raw:>9.3f}{partial:>9.3f}   [{lo:>6.3f},{hi:>6.3f}]"
              f"{p:>9.4f}{survives:>7}")
    print(f"top 12 of {tested} tested; BH at q = 0.05 over all {tested}.")
    return {name: partial for name, _, partial, _, _, _ in results}


def report_within_family(data, target_column, pooled, minimum=8):
    """The same descriptors inside single families, where family cannot explain anything.

    No control variable and no partial correlation here: family is held constant by
    construction, which is the whole point, and protein size within one family is not
    the confound it is across families.

    Nothing can be significant at these sizes -- the thresholds are printed to make that
    concrete rather than to be cleared. What carries information is agreement: a
    descriptor pointing the same way inside both families and in the pooled result is
    saying something family cannot account for.
    """
    import math

    from scipy import stats

    families = data["family"]
    large = [f for f, count in families.value_counts().items() if count >= minimum]
    if not large:
        print("\nno family has enough proteins for a within-family look")
        return
    print(f"\n=== within families, target: {target_column} ===")
    header = f"{'descriptor':<26}" + "".join(
        f"{f'{family} (n={int((families == family).sum())})':>18}" for family in large
    ) + f"{'pooled':>10}"
    print(header)
    for family in large:
        n = int((families == family).sum())
        threshold = stats.t.ppf(0.975, n - 2)
        print(f"   {family}: |rho| would need {threshold / math.sqrt(n - 2 + threshold ** 2):.2f} "
              f"to be significant at n = {n}")

    candidates = [c for c in data.columns if c not in CORRELATE_SKIP_AS_CANDIDATE]
    rows = []
    for name in candidates:
        per_family = []
        for family in large:
            subset = data[families == family]
            values = subset[name].to_numpy(dtype=float)
            target_values = subset[target_column].to_numpy(dtype=float)
            if np.allclose(values, values[0]) or np.isnan(values).any():
                per_family.append(float("nan"))
                continue
            per_family.append(float(stats.spearmanr(values, target_values).statistic))
        if any(np.isnan(per_family)):
            continue
        agreement = min(abs(v) for v in per_family) if len(set(np.sign(per_family))) == 1 else 0.0
        rows.append((name, per_family, pooled.get(name, float("nan")), agreement))
    # Strongest first among those that at least agree in sign across the families.
    rows.sort(key=lambda row: -row[3])
    for name, per_family, pooled_value, _ in rows[:10]:
        cells = "".join(f"{value:>18.3f}" for value in per_family)
        print(f"{name:<26}{cells}{pooled_value:>10.3f}")


def run_correlate():
    from pathlib import Path

    from preprocessing.pocket_shape_descriptors import descriptors_for

    rows = []
    legacy_rows = []
    graphs = Path(PROJECT_ROOT) / "data" / "graphs"
    for protein_dir in sorted(graphs.iterdir()):
        if (protein_dir / "pocketness.pdb").is_file():
            row = descriptors_for(protein_dir)
            if row:
                rows.append(row)
                legacy = legacy_size_descriptors(protein_dir)
                if legacy:
                    legacy_rows.append(legacy)
    shape = pandas.DataFrame(rows).set_index("protein")
    shape = shape.join(pandas.DataFrame(legacy_rows).set_index("protein"))
    data = (
        shape.join(chain_length_per_protein(), how="inner")
        .join(head_classes_per_protein(), how="inner")
        .join(protein_families_series(), how="inner")
        .dropna(subset=list(CORRELATE_TARGET_COLUMNS))
    )
    for target_column in CORRELATE_TARGET_COLUMNS:
        pooled = report_pooled(data, target_column)
        report_within_family(data, target_column, pooled)


def main():
    # No subcommand collides with `train`'s own flags, which training/read_configuration.py
    # reads straight off sys.argv (a custom parser, not argparse) -- every flag starts
    # with "-", so a bare leading word can only be an explicit mode name, and the
    # original bare-flag invocation (no mode word at all) still defaults to `train`.
    mode = "train"
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        mode = sys.argv.pop(1)

    if mode == "train":
        run_train()
    elif mode == "similarity":
        run_similarity(sys.argv[1:])
    elif mode == "correlate":
        run_correlate()
    else:
        raise SystemExit(f"unknown mode {mode!r}; choose train (default) / similarity / correlate")


if __name__ == "__main__":
    main()
