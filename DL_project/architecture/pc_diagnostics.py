"""Principal-component diagnostics for any representation matrix in the model.

Answers one question: how many independent numbers does a `[rows, width]`
representation actually carry, and does it separate the things it is supposed to
separate. A width-128 tensor whose centered spectrum puts 62% of the variance on
one direction is a 128-column tensor carrying about four numbers per row, and no
downstream encoder can extract information that is not there.

The entry point is `analyze`, which accepts any 2-D float tensor:

    initial protein PLM rows           [N_prot, 1536]
    initial lipid rows                 [N_lip, 768] or [N_lip, 11]
    protein/lipid encoder output       [N, hiddim]
    lipid rows after self-attention    [N_lip, hiddim]
    lipid rows after cross-attention   [N_lip, hiddim]
    pooled protein or lipid vectors    [batch, hiddim]
    fused vector before the classifier [batch, width]

`group` turns a per-row matrix into a two-level analysis: variance inside each
group versus variance between group means. With `group = prot_batch` on protein
rows that is "how much does this representation vary between residues of one
protein versus between proteins", which is the pooling question -- a branch whose
between-group share is near zero hands the same vector to cross-attention for
every sample.

`PCProbe` captures the same matrices from a live forward pass by forward hook, so
stages that are not returned by `InteractionClassification.forward` -- inside the
attention blocks, after each MLP block, after the final MLP before the binary
logits -- can be measured without touching the architecture.

Nothing here holds parameters and nothing here is an `nn.Module`, so a probe can
never become a child of the model and inflate `number_of_parameters`, which names
run directories and is a column of `metrics_summary.csv`. All statistics are
computed detached, on CPU, in float64.
"""

import torch


DEFAULT_MAX_ROWS = 20000
DEFAULT_MAX_PAIRS = 4000
DEFAULT_TOP_K = 10


def _matrix(matrix):
    """Detach to a CPU float64 [rows, width] tensor, dropping non-finite rows."""
    tensor = torch.as_tensor(matrix).detach()
    if tensor.dim() == 1:
        tensor = tensor.unsqueeze(0)
    if tensor.dim() != 2:
        raise ValueError(
            f"expected a 2-D [rows, width] matrix, got shape {tuple(tensor.shape)}"
        )
    tensor = tensor.to(device="cpu", dtype=torch.float64)
    finite = torch.isfinite(tensor).all(dim=1)
    return tensor[finite], int((~finite).sum())


def _eigenvalues(tensor):
    """Centered covariance eigenvalues, largest first, via SVD of the centered rows."""
    rows = tensor.shape[0]
    if rows < 2:
        return torch.zeros(0, dtype=torch.float64)
    centered = tensor - tensor.mean(dim=0, keepdim=True)
    singular = torch.linalg.svdvals(centered)
    return (singular ** 2) / (rows - 1)


def pc_spectrum(matrix, top_k=DEFAULT_TOP_K):
    """Variance carried by each principal component, and how many components matter.

    `variance_ratio[k]` is the share of total centered variance on component k, so
    `variance_ratio[0]` is the fraction preserved by replacing the whole row with
    its single projection onto PC1.

    Two width-independent summaries of "how many numbers is this really":

    `effective_rank` -- exp of the Shannon entropy of the normalized spectrum.
    `participation_ratio` -- (sum of eigenvalues)^2 / sum of squared eigenvalues.

    Both equal the width for an isotropic representation and 1 for a rank-1 one.
    They disagree by design: entropy counts weakly-loaded directions, the
    participation ratio is dominated by the strong ones, so a large gap between
    them is itself the signature of one direction plus a long thin tail.
    """
    tensor, dropped = _matrix(matrix)
    rows, width = tensor.shape
    eigenvalues = _eigenvalues(tensor)
    total = float(eigenvalues.sum())
    report = {
        "rows": rows,
        "width": width,
        "non_finite_rows_dropped": dropped,
        "max_components": int(eigenvalues.numel()),
        "total_variance": total,
    }
    if eigenvalues.numel() == 0 or total <= 0.0:
        report.update(
            variance_ratio=[],
            cumulative_variance=[],
            effective_rank=0.0,
            participation_ratio=0.0,
            rank_90=0,
            rank_95=0,
            rank_99=0,
            degenerate=True,
        )
        return report
    ratio = eigenvalues / total
    cumulative = torch.cumsum(ratio, dim=0)
    positive = ratio[ratio > 0.0]
    entropy = float(-(positive * positive.log()).sum())
    report.update(
        variance_ratio=[float(v) for v in ratio[:top_k]],
        cumulative_variance=[float(v) for v in cumulative[:top_k]],
        effective_rank=float(torch.exp(torch.tensor(entropy))),
        participation_ratio=float(total ** 2 / float((eigenvalues ** 2).sum())),
        rank_90=int(torch.searchsorted(cumulative, torch.tensor(0.90)).item()) + 1,
        rank_95=int(torch.searchsorted(cumulative, torch.tensor(0.95)).item()) + 1,
        rank_99=int(torch.searchsorted(cumulative, torch.tensor(0.99)).item()) + 1,
        degenerate=False,
    )
    return report


def group_variance(matrix, group):
    """Split variance into "inside each group" and "between group means".

    `within_trace` is the group-size-weighted mean over groups of the total
    per-dimension variance inside that group. `between_trace` is the same total
    variance of the group-mean vectors. Both are traces of covariance matrices, so
    they are in the same units and directly comparable.

    `between_over_within` is the ratio quoted for pooled branches: how much signal
    survives pooling relative to the variation pooling averages away. Near zero
    means every group pools to nearly the same vector.

    `between_fraction_of_total` is the same split as a fraction, the
    representation's one-way ANOVA share of variance explained by group identity.
    """
    tensor, dropped = _matrix(matrix)
    labels = torch.as_tensor(group).detach().to(device="cpu").reshape(-1)
    if labels.numel() != tensor.shape[0] + dropped:
        raise ValueError(
            f"group has {labels.numel()} entries, matrix has "
            f"{tensor.shape[0] + dropped} rows"
        )
    if dropped:
        finite = torch.isfinite(
            torch.as_tensor(matrix).detach().to(dtype=torch.float64)
        ).all(dim=1)
        labels = labels[finite]
    unique = torch.unique(labels)
    rows = tensor.shape[0]
    means = []
    sizes = []
    within = 0.0
    for value in unique:
        block = tensor[labels == value]
        sizes.append(block.shape[0])
        means.append(block.mean(dim=0))
        if block.shape[0] > 1:
            within += block.shape[0] * float(block.var(dim=0, unbiased=True).sum())
    within = within / rows if rows else 0.0
    stacked = torch.stack(means) if means else torch.zeros(0, tensor.shape[1])
    between = (
        float(stacked.var(dim=0, unbiased=True).sum()) if stacked.shape[0] > 1 else 0.0
    )
    return {
        "groups": int(unique.numel()),
        "rows": rows,
        "min_group_size": int(min(sizes)) if sizes else 0,
        "max_group_size": int(max(sizes)) if sizes else 0,
        "within_trace": within,
        "between_trace": between,
        "between_over_within": between / within if within > 0.0 else float("nan"),
        "between_fraction_of_total": (
            between / (between + within) if (between + within) > 0.0 else float("nan")
        ),
        "group_means": stacked,
        "group_labels": [
            int(v) if float(v).is_integer() else float(v) for v in unique
        ],
    }


def cosine_stats(matrix, max_pairs=DEFAULT_MAX_PAIRS, generator=None):
    """Pairwise cosine between rows, after L2-normalizing each row.

    Cosine ignores row length and reports direction only, which is what matters
    once a linear layer follows: near-1 mean cosine means every row points the
    same way and the layer sees one direction scaled differently per row.

    `spread` is max minus min and is the honest summary -- a high mean cosine with
    a wide spread still separates rows, a high mean with no spread does not. Pairs
    are subsampled above `max_pairs` to keep this O(max_pairs) rather than O(n^2).
    """
    tensor, _ = _matrix(matrix)
    rows = tensor.shape[0]
    if rows < 2:
        return {"pairs": 0, "mean": float("nan"), "min": float("nan"),
                "max": float("nan"), "std": float("nan"), "spread": float("nan")}
    normalized = tensor / tensor.norm(dim=1, keepdim=True).clamp_min(1e-12)
    total_pairs = rows * (rows - 1) // 2
    if total_pairs <= max_pairs:
        similarity = normalized @ normalized.T
        values = similarity[torch.triu_indices(rows, rows, offset=1).unbind()]
    else:
        left = torch.randint(rows, (max_pairs,), generator=generator)
        right = torch.randint(rows, (max_pairs,), generator=generator)
        keep = left != right
        values = (normalized[left[keep]] * normalized[right[keep]]).sum(dim=1)
    return {
        "pairs": int(values.numel()),
        "sampled": total_pairs > max_pairs,
        "mean": float(values.mean()),
        "min": float(values.min()),
        "max": float(values.max()),
        "std": float(values.std(unbiased=False)),
        "spread": float(values.max() - values.min()),
    }


def nearest_neighbours(matrix, names):
    """Cosine nearest neighbour of every row, excluding itself.

    Run on group-mean (pooled) vectors this is a label-free check that the
    representation keeps the topology it should: pooled protein vectors whose
    nearest neighbour sits in an unrelated fold have lost fold identity, whatever
    their absolute cosine happens to be.
    """
    tensor, _ = _matrix(matrix)
    rows = tensor.shape[0]
    if rows != len(names):
        raise ValueError(f"{len(names)} names for {rows} rows")
    if rows < 2:
        return []
    normalized = tensor / tensor.norm(dim=1, keepdim=True).clamp_min(1e-12)
    similarity = normalized @ normalized.T
    similarity.fill_diagonal_(-float("inf"))
    best = similarity.argmax(dim=1)
    return [
        (names[i], names[int(best[i])], float(similarity[i, int(best[i])]))
        for i in range(rows)
    ]


def scale_stats(matrix):
    """Row length and per-dimension spread, in absolute units.

    Needed whenever two representations are concatenated or summed: statistics
    that are scale-free (cosine, variance ratios) cannot see that one block of
    columns is numerically negligible next to another.
    """
    tensor, _ = _matrix(matrix)
    norms = tensor.norm(dim=1)
    return {
        "rows": int(tensor.shape[0]),
        "width": int(tensor.shape[1]),
        "mean_row_norm": float(norms.mean()),
        "median_row_norm": float(norms.median()),
        "mean_energy": float((norms ** 2).mean()),
        "mean_per_dim_std": float(tensor.std(dim=0, unbiased=True).mean()),
        "abs_max": float(tensor.abs().max()),
    }


def concat_energy_share(parts):
    """Share of squared row length each part contributes to their concatenation.

    `parts` maps a name to a `[rows, width_i]` matrix. Energy is the mean squared
    row norm, which is what a linear layer's input magnitude follows, so a part
    with a share of 1e-7 is numerically absent from the concatenated vector at
    standard initialization no matter how many columns it occupies.
    """
    energies = {}
    for name, part in parts.items():
        tensor, _ = _matrix(part)
        energies[name] = float((tensor.norm(dim=1) ** 2).mean())
    total = sum(energies.values())
    return {
        "energy": energies,
        "share": {
            name: (value / total if total > 0.0 else float("nan"))
            for name, value in energies.items()
        },
        "width": {name: int(_matrix(part)[0].shape[1]) for name, part in parts.items()},
    }


def feature_correlation(matrix, features, feature_names=None, components=2):
    """Pearson correlation of the leading PC projections with external features.

    Says what the dominant direction is made of. A PC1 that carries most of the
    variance while correlating with nothing interpretable is not evidence of a
    rich representation; a PC whose correlation sign flips between groups is a
    group-specific direction and cannot transfer to a held-out group.
    """
    tensor, dropped = _matrix(matrix)
    feature_tensor, _ = _matrix(features)
    if feature_tensor.shape[0] != tensor.shape[0]:
        raise ValueError(
            f"features have {feature_tensor.shape[0]} rows, matrix has "
            f"{tensor.shape[0]} usable rows ({dropped} dropped as non-finite)"
        )
    if tensor.shape[0] < 3:
        return {}
    centered = tensor - tensor.mean(dim=0, keepdim=True)
    _, _, basis = torch.linalg.svd(centered, full_matrices=False)
    names = feature_names or [f"feature_{i}" for i in range(feature_tensor.shape[1])]
    result = {}
    for k in range(min(components, basis.shape[0])):
        projection = centered @ basis[k]
        for index, name in enumerate(names):
            column = feature_tensor[:, index]
            pair = torch.stack((projection, column))
            if float(projection.std()) == 0.0 or float(column.std()) == 0.0:
                result[(f"PC{k + 1}", name)] = float("nan")
                continue
            result[(f"PC{k + 1}", name)] = float(torch.corrcoef(pair)[0, 1])
    return result


def analyze(
    matrix,
    group=None,
    names=None,
    features=None,
    feature_names=None,
    top_k=DEFAULT_TOP_K,
    max_pairs=DEFAULT_MAX_PAIRS,
    stage=None,
):
    """Full report for one representation matrix at one stage of the model.

    `group` -- per-row group id (`prot_batch` / `lip_batch` on node matrices,
    sample index on pooled matrices) enabling the within/between split and the
    nearest-neighbour check on group means.
    `names` -- one label per group when `group` is given, otherwise one per row.
    `features` -- `[rows, f]` external per-row quantities to correlate PCs with.
    """
    report = {"stage": stage, "spectrum": pc_spectrum(matrix, top_k=top_k),
              "scale": scale_stats(matrix), "rows": cosine_stats(matrix, max_pairs)}
    if group is not None:
        grouped = group_variance(matrix, group)
        pooled = grouped.pop("group_means")
        report["group"] = grouped
        report["pooled_cosine"] = cosine_stats(pooled, max_pairs)
        report["pooled_spectrum"] = pc_spectrum(pooled, top_k=top_k)
        labels = names if names is not None else [
            str(v) for v in grouped["group_labels"]
        ]
        if len(labels) == pooled.shape[0]:
            report["pooled_nearest"] = nearest_neighbours(pooled, labels)
    elif names is not None:
        report["nearest"] = nearest_neighbours(matrix, names)
    if features is not None:
        report["feature_correlation"] = feature_correlation(
            matrix, features, feature_names
        )
    return report


def format_report(report, max_neighbours=12):
    """Render one `analyze` result as plain text."""
    spectrum = report["spectrum"]
    scale = report["scale"]
    rows = report["rows"]
    lines = []
    stage = report.get("stage")
    lines.append(f"stage: {stage}" if stage else "stage: <unnamed>")
    lines.append(
        f"  shape                       {spectrum['rows']} x {spectrum['width']}"
        + (
            f"  ({spectrum['non_finite_rows_dropped']} non-finite rows dropped)"
            if spectrum["non_finite_rows_dropped"] else ""
        )
    )
    if spectrum["degenerate"]:
        lines.append("  degenerate: no variance to decompose")
        return "\n".join(lines)
    ratio = spectrum["variance_ratio"]
    cumulative = spectrum["cumulative_variance"]
    lines.append(
        "  variance on PC1..PC5        "
        + " ".join(f"{v:.3f}" for v in ratio[:5])
    )
    lines.append(
        "  cumulative PC1 / 3 / 5 / 10 "
        + " / ".join(
            f"{cumulative[i]:.3f}" for i in (0, 2, 4, 9) if i < len(cumulative)
        )
    )
    lines.append(
        f"  effective rank              {spectrum['effective_rank']:.1f}"
        f" of {spectrum['width']}"
        f"  ({spectrum['effective_rank'] / spectrum['width']:.1%} of width)"
    )
    lines.append(
        f"  participation ratio         {spectrum['participation_ratio']:.1f}"
    )
    lines.append(
        "  components for 90/95/99%    "
        f"{spectrum['rank_90']} / {spectrum['rank_95']} / {spectrum['rank_99']}"
    )
    lines.append(
        f"  mean row norm               {scale['mean_row_norm']:.4g}"
        f"   per-dim std {scale['mean_per_dim_std']:.4g}"
        f"   abs max {scale['abs_max']:.4g}"
    )
    lines.append(
        f"  cosine between rows         mean {rows['mean']:.4f}"
        f"  spread {rows['spread']:.4f}"
        + ("  (subsampled)" if rows.get("sampled") else "")
    )
    if "group" in report:
        grouped = report["group"]
        pooled_cosine = report["pooled_cosine"]
        pooled_spectrum = report["pooled_spectrum"]
        lines.append(
            f"  groups                      {grouped['groups']}"
            f"  (sizes {grouped['min_group_size']}..{grouped['max_group_size']})"
        )
        lines.append(
            f"  variance within group       {grouped['within_trace']:.4g}"
        )
        lines.append(
            f"  variance between groups     {grouped['between_trace']:.4g}"
        )
        lines.append(
            f"  between / within            {grouped['between_over_within']:.4f}"
            f"   (group identity explains"
            f" {grouped['between_fraction_of_total']:.2%} of total variance)"
        )
        lines.append(
            f"  cosine between pooled       mean {pooled_cosine['mean']:.4f}"
            f"  min {pooled_cosine['min']:.4f}"
            f"  spread {pooled_cosine['spread']:.4f}"
        )
        lines.append(
            f"  effective rank of pooled    "
            f"{pooled_spectrum['effective_rank']:.1f} of {pooled_spectrum['width']}"
        )
    for key in ("pooled_nearest", "nearest"):
        if key in report:
            neighbours = report[key]
            lines.append(f"  nearest neighbour ({key.split('_')[0]}):")
            for name, neighbour, similarity in neighbours[:max_neighbours]:
                lines.append(f"      {name:<14s} -> {neighbour:<14s} cos {similarity:.3f}")
            if len(neighbours) > max_neighbours:
                lines.append(f"      ... {len(neighbours) - max_neighbours} more")
    if report.get("feature_correlation"):
        lines.append("  correlation of PCs with external features:")
        for (component, feature), value in report["feature_correlation"].items():
            lines.append(f"      {component} x {feature:<24s} r = {value:+.3f}")
    return "\n".join(lines)


class PCProbe:
    """Capture representations from a live forward pass and report their spectra.

    Registers forward hooks, so any stage reachable as a submodule can be measured
    without editing the architecture -- the attention blocks, each MLP block, and
    the final MLP before the binary logits, none of which are returned by
    `InteractionClassification.forward`.

    Holds no parameters and is not an `nn.Module`: it cannot be assigned as a
    child of the model and cannot change `number_of_parameters`.

    Rows accumulate across batches up to `max_rows` per stage, subsampled without
    replacement once the cap is reached, so a whole validation pass can be
    summarized at bounded memory. Because the cap subsamples, reports over
    different runs are comparable only when `max_rows` and `seed` match.

        probe = PCProbe(max_rows=20000)
        probe.attach({
            "protein_encoder_out": model.protein_encoder,
            "lipid_after_sa": model.lipid_encoder.attention,
            "lipid_after_ca": model.cross_attention1,
            "final_mlp": model.final_layer.mlp,
        })
        with torch.no_grad():
            for batch in loader:
                model(**forward_args(batch))
                probe.tag_groups("protein_encoder_out", batch.prot_batch)
        print(probe.format())
        probe.detach()

    A stage whose module returns a tuple keeps element 0 unless `select` is given.
    Stages recorded by hand with `add` need no hook at all, which is the path for
    matrices the forward already returns.
    """

    def __init__(self, max_rows=DEFAULT_MAX_ROWS, seed=0, select=None):
        self.max_rows = int(max_rows)
        self.select = select
        self._generator = torch.Generator().manual_seed(int(seed))
        self._rows = {}
        self._groups = {}
        self._seen = {}
        self._handles = []

    def attach(self, modules, select=None):
        """Register a forward hook per `{stage_name: module}` entry."""
        for stage, module in modules.items():
            self._handles.append(
                module.register_forward_hook(self._make_hook(stage, select))
            )
        return self

    def detach(self):
        """Remove every hook. Captured rows stay available for reporting."""
        for handle in self._handles:
            handle.remove()
        self._handles = []
        return self

    def __enter__(self):
        return self

    def __exit__(self, *exception):
        self.detach()
        return False

    def _make_hook(self, stage, select):
        chooser = select or self.select

        def hook(module, inputs, output):
            tensor = chooser(output) if chooser else output
            if isinstance(tensor, (tuple, list)):
                tensor = tensor[0]
            if torch.is_tensor(tensor) and tensor.dim() >= 2:
                self.add(stage, tensor.reshape(-1, tensor.shape[-1]))

        return hook

    def add(self, stage, matrix, group=None):
        """Record rows for `stage`, subsampling once `max_rows` is reached."""
        tensor, _ = _matrix(matrix)
        labels = None
        if group is not None:
            labels = torch.as_tensor(group).detach().to("cpu").reshape(-1)
            if labels.numel() != tensor.shape[0]:
                raise ValueError(
                    f"{stage}: group has {labels.numel()} entries for "
                    f"{tensor.shape[0]} rows"
                )
        self._seen[stage] = self._seen.get(stage, 0) + tensor.shape[0]
        held = self._rows.get(stage)
        room = self.max_rows - (held.shape[0] if held is not None else 0)
        if room <= 0:
            return self
        if tensor.shape[0] > room:
            keep = torch.randperm(tensor.shape[0], generator=self._generator)[:room]
            tensor = tensor[keep]
            if labels is not None:
                labels = labels[keep]
        self._rows[stage] = tensor if held is None else torch.cat((held, tensor))
        if labels is not None:
            previous = self._groups.get(stage)
            self._groups[stage] = (
                labels if previous is None else torch.cat((previous, labels))
            )
        return self

    def tag_groups(self, stage, group):
        """Attach group ids to the rows most recently added for `stage`.

        Use when the group vector is only known outside the hook, which is the
        normal case: the hook sees the module output, the caller holds
        `prot_batch` / `lip_batch`. Ignored if the row count does not match, since
        a capped or subsampled stage cannot be aligned after the fact.
        """
        held = self._rows.get(stage)
        labels = torch.as_tensor(group).detach().to("cpu").reshape(-1)
        if held is None:
            return self
        existing = self._groups.get(stage)
        already = existing.numel() if existing is not None else 0
        if already + labels.numel() > held.shape[0]:
            return self
        self._groups[stage] = (
            labels if existing is None else torch.cat((existing, labels))
        )
        return self

    def stages(self):
        return list(self._rows)

    def report(self, names=None, **kwargs):
        """`analyze` every captured stage, using tagged groups where available."""
        reports = {}
        for stage, tensor in self._rows.items():
            group = self._groups.get(stage)
            if group is not None and group.numel() != tensor.shape[0]:
                group = None
            reports[stage] = analyze(
                tensor,
                group=group,
                names=(names or {}).get(stage) if isinstance(names, dict) else names,
                stage=stage,
                **kwargs,
            )
            reports[stage]["rows_seen"] = self._seen.get(stage, 0)
            reports[stage]["rows_kept"] = int(tensor.shape[0])
        return reports

    def format(self, **kwargs):
        blocks = []
        for stage, report in self.report(**kwargs).items():
            text = format_report(report)
            if report["rows_kept"] < report["rows_seen"]:
                text += (
                    f"\n  subsampled                  {report['rows_kept']}"
                    f" of {report['rows_seen']} rows seen"
                )
            blocks.append(text)
        return "\n\n".join(blocks)

    def reset(self):
        self._rows, self._groups, self._seen = {}, {}, {}
        return self
