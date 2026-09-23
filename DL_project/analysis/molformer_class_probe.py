#!/usr/bin/env python3
"""Can the lipid class be read back out of the MolFormer embedding the network gets?

A standalone probe, built the way an adversarial head is built (a small classifier on a
frozen representation) but detached from the model: nothing here trains the interaction
task, touches a protein, or reads a split. The question is only about the LIPID INPUT --
if the 768-dim vector architecture/lipid_encoder.py projects through one
`torch.nn.Linear(768, hiddim)` does not even carry which head-group class the molecule
belongs to, then no amount of work downstream of that projection can recover it, and
every cold-split result that depends on recognising a novel head group is bounded by
that fact rather than by the model.

Detached rather than a head inside the run on purpose. A head attached to
InteractionClassification would answer the same question at the price of a full training
run per reading, and its number would be entangled with the split, the sampler and the
interaction loss -- none of which the question involves. This takes seconds and the
answer means one thing.

What it measures. One vector per FullIdentityOfLipid species (the network's own:
training.pair_baseline_common.molformer_lipid_features, mean-pooled over MolFormer's
tokens and over the species' candidate structures), against that species' class, scored
by stratified k-fold over SPECIES so no species is ever in both halves. Reported
against two reference points that make the number readable:

  * the majority-class rate -- what a model that ignores the input entirely scores;
  * the same probe on the project's own hand-built lipid descriptors
    (--features descriptors), which is the representation MolFormer would have to beat
    to justify its 768 dimensions.

Two probes, because they answer different questions: `linear` asks whether the class is
LINEARLY available (which is what the single Linear(768, hiddim) in the encoder can
use), `mlp` asks whether it is there at all.

    python3 analysis/molformer_class_probe.py
    python3 analysis/molformer_class_probe.py --target project_class
    python3 analysis/molformer_class_probe.py --features descriptors
    python3 analysis/molformer_class_probe.py --geometry --per_class

Results and what they do and do not say: files/molformer_expressivity_probe.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import training.pair_baseline_common as pbc  # noqa: E402

# The hand-built lipid descriptors the comparison runs on: LIPID_DESCRIPTOR_NAMES minus
# nothing -- the whole catalog, so the baseline is the best the project's own features
# can do rather than a subset chosen to lose.
from dataloader.pair_descriptors import LIPID_DESCRIPTOR_NAMES  # noqa: E402


def species_targets(table: pd.DataFrame, target: str) -> pd.Series:
    """{FullIdentityOfLipid: class label}, by whichever naming was asked for."""
    if target == "project_class":
        classes = pbc.csv_classes(table)
        return pd.Series(classes.values, index=table["FullIdentityOfLipid"].values).groupby(
            level=0
        ).first()
    lookup = pbc._article_subclass_lookup()
    assignment = {}
    for subclass, members in lookup.items():
        for species in members:
            assignment[species] = subclass.upper()
    return pd.Series(assignment)


def build_features(table: pd.DataFrame, kind: str) -> pd.DataFrame:
    if kind == "molformer":
        return pbc.molformer_lipid_features(table)
    if kind == "descriptors":
        return pbc.resolve_lipid_feature_subset(table, list(LIPID_DESCRIPTOR_NAMES))
    molformer = pbc.molformer_lipid_features(table)
    descriptors = pbc.resolve_lipid_feature_subset(table, list(LIPID_DESCRIPTOR_NAMES))
    descriptors.columns = [f"d_{name}" for name in descriptors.columns]
    return molformer.join(descriptors, how="inner")


def evaluate(features: np.ndarray, labels: np.ndarray, probe: str, folds: int, seed: int):
    """(balanced accuracy, macro F1, per-class recall) by stratified k-fold.

    Balanced accuracy, not plain accuracy: with --min_species 1 the class sizes run
    from 76 species (PC) down to 1, so a plain hit rate is decided by the few large
    classes and says nothing about the rest. Balanced accuracy is the mean of the
    per-class recalls below, so every class counts once whatever its size, and its
    chance level is 1 / number of classes.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import balanced_accuracy_score, f1_score, recall_score
    from sklearn.model_selection import StratifiedKFold
    from sklearn.neural_network import MLPClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    def make_model():
        if probe == "linear":
            # Strong L2 by default: 768 dimensions against a couple of hundred species
            # separates the training half perfectly at any regularisation weak enough to
            # let it, so an unregularised readout would measure the fold size, not the
            # representation.
            return make_pipeline(
                StandardScaler(),
                LogisticRegression(C=0.1, max_iter=5000, multi_class="multinomial"),
            )
        return make_pipeline(
            StandardScaler(),
            MLPClassifier(
                hidden_layer_sizes=(128,), alpha=1.0, max_iter=2000, random_state=seed
            ),
        )

    splitter = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    predicted = np.empty_like(labels)
    for train_index, test_index in splitter.split(features, labels):
        model = make_model()
        model.fit(features[train_index], labels[train_index])
        predicted[test_index] = model.predict(features[test_index])
    balanced = float(balanced_accuracy_score(labels, predicted))
    macro_f1 = float(f1_score(labels, predicted, average="macro", zero_division=0))
    classes = np.unique(labels)
    # One-vs-rest confusion per class: TP its species called by its own name, FN its
    # species called something else, FP other classes called by its name, TN everything
    # else. Counts are species, and every column sums to len(labels) across the four.
    per_class = {}
    for name in classes:
        is_class = labels == name
        called_class = predicted == name
        tp = int((is_class & called_class).sum())
        fn = int((is_class & ~called_class).sum())
        fp = int((~is_class & called_class).sum())
        tn = int((~is_class & ~called_class).sum())
        sensitivity = tp / (tp + fn) if tp + fn else 0.0
        specificity = tn / (tn + fp) if tn + fp else 0.0
        precision = tp / (tp + fp) if tp + fp else 0.0
        f1 = (
            2 * precision * sensitivity / (precision + sensitivity)
            if precision + sensitivity
            else 0.0
        )
        per_class[name] = {
            "species": int(is_class.sum()),
            "TP": tp, "FP": fp, "TN": tn, "FN": fn,
            "sensitivity": sensitivity,
            "specificity": specificity,
            "precision": precision,
            "F1": f1,
            "balanced_accuracy": (sensitivity + specificity) / 2.0,
        }
    return balanced, macro_f1, per_class


def geometry(features: np.ndarray, labels: np.ndarray) -> dict:
    """Is the class easy to read because the representation SEPARATES the classes, or
    because it barely separates anything and the probe is fitting noise?

    The same two questions preprocessing/protein_representation_identity_check.py asks
    of the protein representations, on the lipid side. That companion is the reason they
    are worth asking at all: ESM3 looks usable until you measure it and find median
    cosine 0.974 between any two of the 35 proteins, i.e. one point wearing 35 labels.
    A probe accuracy alone cannot tell those two situations apart.

      nearest_same_class   for each species, whether its nearest OTHER species shares
                           its class. Read against `chance`, the rate a random
                           neighbour would give.
      within / between     median cosine inside a class and across classes. The GAP is
                           what a linear probe has to work with.

    Columns are z-scored across species FIRST, because that is what the probe's own
    StandardScaler does and the two numbers have to describe the same space. Without it
    this measures column scale rather than geometry: on the raw hand-built descriptors
    every pair of species sits at cosine 0.997-1.000 purely because one large-magnitude
    column (a volume, a refractivity) dominates the dot product, while the probe -- which
    standardises -- separates the same species at 0.79 accuracy.
    """
    centred = features - features.mean(axis=0, keepdims=True)
    centred /= np.clip(centred.std(axis=0, keepdims=True), 1e-12, None)
    normalised = centred / np.clip(
        np.linalg.norm(centred, axis=1, keepdims=True), 1e-12, None
    )
    cosine = normalised @ normalised.T
    np.fill_diagonal(cosine, -np.inf)
    nearest = cosine.argmax(axis=1)
    same = labels[nearest] == labels
    pairs = np.triu(np.ones_like(cosine, dtype=bool), k=1)
    same_class = labels[:, None] == labels[None, :]
    chance = float(
        sum(
            count * (count - 1)
            for count in pd.Series(labels).value_counts()
        ) / (len(labels) * (len(labels) - 1))
    )
    return {
        "nearest_same_class": float(same.mean()),
        "chance": chance,
        "within_class_cosine": float(np.median(cosine[pairs & same_class])),
        "between_class_cosine": float(np.median(cosine[pairs & ~same_class])),
    }


def per_class_frame(per_class):
    """One row per class: the four counts plus the rates derived from them."""
    import pandas as pd

    frame = pd.DataFrame(
        [{"class": name, **values} for name, values in per_class.items()]
    )
    return frame.sort_values(
        ["balanced_accuracy", "species"], ascending=[False, False]
    ).reset_index(drop=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--target", choices=("subclass", "project_class"), default="subclass",
        help="subclass = Titeca et al.'s own abbreviation (data/lipid_article_"
             "classification.json); project_class = this project's head-group class",
    )
    parser.add_argument(
        "--features", choices=("molformer", "descriptors", "both", "all"),
        default="all",
        help="which representation the probe reads; 'all' runs each in turn so the "
             "comparison is in one table (default)",
    )
    parser.add_argument(
        "--probe", choices=("linear", "mlp", "all"), default="all",
        help="linear asks whether the class is linearly available -- which is what the "
             "encoder's single Linear(768, hiddim) can use; mlp asks whether it is "
             "present at all",
    )
    parser.add_argument(
        "--min_species", type=int, default=4,
        help="drop classes with fewer members than this: a class of one cannot be "
             "stratified across folds and its recall is a coin toss either way",
    )
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--geometry", action="store_true",
        help="also report how separated the classes are in each representation "
             "(nearest-neighbour same-class rate, within- vs between-class cosine) -- "
             "the check that tells a genuinely separating representation from a "
             "collapsed one, the way ESM3's median cosine 0.974 does on the protein side",
    )
    parser.add_argument(
        "--per_class", action="store_true",
        help="also print per-class recall for the best configuration",
    )
    parser.add_argument("--csv", type=Path, default=None, help="also write the table here")
    parser.add_argument(
        "--recall_csv", type=Path, default=None,
        help="write the best configuration's per-class table here: species, TP, FP, "
             "TN, FN and the rates derived from them",
    )
    args = parser.parse_args()

    table = pbc.read_interactions()
    targets = species_targets(table, args.target)

    feature_kinds = (
        ("molformer", "descriptors", "both") if args.features == "all" else (args.features,)
    )
    probes = ("linear", "mlp") if args.probe == "all" else (args.probe,)

    built = {kind: build_features(table, kind) for kind in feature_kinds}
    # One species set for every representation, so the rows compare: a species missing
    # an embedding must not be scored by the descriptor probe and not by MolFormer's.
    shared = set.intersection(*[set(frame.index) for frame in built.values()])
    shared &= set(targets.index)
    labels_all = targets.loc[sorted(shared)]
    counts = labels_all.value_counts()
    # min_species alone, not max(min_species, folds): at --min_species 1 a class with
    # fewer members than folds stays in, StratifiedKFold warns about it, and that class
    # simply never appears in a training half -- its recall comes out 0. That is the
    # honest reading of "can the representation place this class", not a reason to hide
    # the class from the table.
    keep = counts[counts >= args.min_species].index
    species = [name for name in sorted(shared) if labels_all[name] in set(keep)]
    labels = targets.loc[species].to_numpy()
    dropped = sorted(set(counts.index) - set(keep))

    majority = float(pd.Series(labels).value_counts(normalize=True).max())
    print(
        f"target={args.target}  {len(species)} species, {len(keep)} classes "
        f"(dropped {len(dropped)} class(es) with < "
        f"{args.min_species} species: {', '.join(dropped) or 'none'})"
    )
    print(f"majority-class rate (a model that ignores the input): {majority:.3f}")
    print(f"chance balanced accuracy (1 / classes): {1.0 / len(keep):.3f}")
    print()

    rows = []
    best = None
    for kind in feature_kinds:
        matrix = built[kind].loc[species].to_numpy(dtype=float)
        matrix = np.nan_to_num(matrix, nan=0.0, posinf=0.0, neginf=0.0)
        for probe in probes:
            balanced, macro_f1, recall = evaluate(
                matrix, labels, probe, args.folds, args.seed
            )
            rows.append({
                "features": kind,
                "columns": matrix.shape[1],
                "probe": probe,
                "balanced_accuracy": balanced,
                "macro_f1": macro_f1,
            })
            if best is None or macro_f1 > best[0]:
                best = (macro_f1, kind, probe, recall)
    frame = pd.DataFrame(rows)
    print(frame.to_string(index=False, float_format=lambda value: f"{value:.4f}"))

    if args.geometry:
        print("\nclass separation in each representation:")
        shape = pd.DataFrame([
            {
                "features": kind,
                **geometry(
                    np.nan_to_num(
                        built[kind].loc[species].to_numpy(dtype=float),
                        nan=0.0, posinf=0.0, neginf=0.0,
                    ),
                    labels,
                ),
            }
            for kind in feature_kinds
        ])
        print(shape.to_string(index=False, float_format=lambda value: f"{value:.4f}"))

    if args.per_class and best is not None:
        _, kind, probe, per_class = best
        print(f"\nper-class confusion, best configuration ({kind} / {probe}):")
        print(per_class_frame(per_class).to_string(
            index=False, float_format=lambda value: f"{value:.4f}"
        ))

    if args.recall_csv and best is not None:
        _, _, _, per_class = best
        per_class_frame(per_class).to_csv(args.recall_csv, index=False)
        print(f"\nper-class table written to {args.recall_csv}")

    if args.csv:
        frame.to_csv(args.csv, index=False)
        print(f"\nwritten to {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
