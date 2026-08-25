#!/usr/bin/env python3
"""Parameter count of a configured model, broken down by architectural part.

    python3 analysis/model_parameter_breakdown.py <label>
    python3 analysis/model_parameter_breakdown.py scripts/arg_files/<label>.md
    python3 analysis/model_parameter_breakdown.py <label> --excluded_groups=start

<label> is resolved the same three ways scripts/lib/args_file_lib.sh accepts: a
path, a bare stem under scripts/arg_files/, or a filename there. Its "--" lines
become the model's configuration, exactly as scripts/lib/args_file_lib.sh turns
them into a training command's argv -- this script does not shell out to that
file so that it works without a cluster checkout, but the parsing rule (only
lines starting with "--", quotes stripped) is copied from it on purpose, so a
label reads identically here and at submission time.

Building InteractionClassification(config) touches no file on disk -- weights
are freshly initialised, nothing is loaded -- so this runs anywhere the python
environment has torch and torch_geometric, no data/ or GPU required.

--excluded_groups and --seed are appended automatically when the label needs
them (double_coldsplit, mixed_coldsplit or test_group) and does not already set
them: architecture, and therefore parameter count, does not depend on which
family is held out or which seed is used, so any accepted value works. Override
either with an explicit flag on the command line if the label's own choice
would fail validate() for an unrelated reason.

The eight-part grouping mirrors the model's own module names
(architecture/interaction_classification.py: lipid1/2, protein1/2,
cross_attention1/2, final_layer) rather than being specific to any one
configuration, so it stays correct across --double_attention (lipid2/protein2
merge into their lipid1/protein1 counterparts) and most alternative protein
encoders. A row is added on the fly, immediately under the group it came from,
for parameters that do not fit the eight -- RNA-BAnG's adapter path or the
geometric transformer, say -- so a config the eight parts were not written for
still reports its true total rather than silently dropping a module.
"""

import argparse
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "training"))

ARGS_FILE_DIR = PROJECT_ROOT / "scripts" / "arg_files"


def resolve_args_file(name):
    """The three spellings scripts/lib/args_file_lib.sh accepts, in the same order."""
    candidate = Path(name)
    if candidate.is_file():
        return candidate
    candidate = ARGS_FILE_DIR / f"{name}.md"
    if candidate.is_file():
        return candidate
    candidate = ARGS_FILE_DIR / name
    if candidate.is_file():
        return candidate
    raise SystemExit(
        f"No arg_file for {name!r}: tried it as a path, as "
        f"{ARGS_FILE_DIR}/{name}.md, and as {ARGS_FILE_DIR}/{name}"
    )


def args_file_flags(path):
    """The '--' lines of an arg_file, quotes stripped -- args_file_flag_lines in bash.

    A line occasionally carries more than one flag space-separated on it (e.g.
    "--weight_decay=0 --bidirectional_edges"). The bash version does not split
    that itself; it works there only because its output string later crosses an
    unquoted shell expansion, which word-splits it. There is no such expansion
    here, so the split happens explicitly, on the line as a whole, to reach the
    same argv either way.
    """
    flags = []
    pattern = re.compile(r'^(--[^=\s]+=)"?([^"]*)"?$')
    for line in path.read_text().splitlines():
        if not line.startswith("--"):
            continue
        match = pattern.match(line)
        resolved = match.group(1) + match.group(2) if match else line
        flags.extend(resolved.split())
    return flags


def ensure_split_flags(flags, extra_excluded_groups, extra_seed):
    """Fill in what scripts/launch/submit_grid.sh would supply at submission time.

    None of --excluded_groups, --test_group, --lipid_coldsplit's group or --seed live
    in the arg_file itself; the submitter appends them once it knows which family (or
    lipid set) a given queued job is holding out. A label that needs one of them is
    therefore incomplete on its own, and nothing here changes which modules the model
    builds -- only which rows a data loader built from this config would later read --
    so any accepted value keeps the parameter count exact.
    """
    has_excluded = any(
        flag.startswith("--excluded_groups") or flag == "--excluded_groups"
        for flag in flags
    )
    has_test_group = any(flag.startswith("--test_group") for flag in flags)
    has_double = any(
        flag in ("--double_coldsplit", "--mixed_coldsplit") for flag in flags
    )
    has_cold_split = "--cold_split" in flags

    if has_cold_split and not has_test_group:
        # submit_grid.sh: "--excluded_groups=<TEST>,<VAL> --test_group=<TEST>". Any two
        # accepted, distinct family names satisfy validate(); which two is immaterial to
        # the architecture.
        flags = flags + ["--excluded_groups=cral-trio,gltp", "--test_group=cral-trio"]
    elif (has_double or has_test_group) and not has_excluded:
        flags = flags + [f"--excluded_groups={extra_excluded_groups}"]

    # A bare --lipid_coldsplit (no "=value") is how the arg_file marks that axis for
    # the submitter, which then strips the bare flag and appends its own
    # --lipid_coldsplit=<set>. Mirrored here rather than left for read_configuration.py,
    # which requires a value and would otherwise reject the bare flag as unknown.
    if "--lipid_coldsplit" in flags:
        flags = [flag for flag in flags if flag != "--lipid_coldsplit"]
        flags = flags + ["--lipid_coldsplit=sphingolipids"]

    has_seed = any(flag.startswith("--seed") for flag in flags)
    if not has_seed:
        flags = flags + [f"--seed={extra_seed}"]
    return flags


# (category, [prefixes matched against a dotted parameter name])
# Order matters: the first matching category wins, and enc_plm is listed before
# encodin1/encodin2 so protein1.enc_plm* is not mistaken for the GAT convolution.
CATEGORIES = [
    ("lipid: input projection", ["lipid1.encodin", "lipid2.encodin", "lipid1.mlp",
        "lipid2.mlp", "lipid1.gat_ln", "lipid2.gat_ln", "lipid1.head_gate",
        "lipid2.head_gate"]),
    ("lipid: self-attention, feed-forward, norms", ["lipid1.attention",
        "lipid2.attention", "lipid1.post_sa", "lipid2.post_sa", "lipid1.ln",
        "lipid2.ln"]),
    ("protein: ESM3 projection", ["protein1.enc_plm", "protein2.enc_plm"]),
    ("protein: GATv2 layer and norm", ["protein1.encodin1", "protein1.encodin2",
        "protein2.encodin1", "protein2.encodin2", "protein1.head_gate",
        "protein2.head_gate", "protein1.gat_ln", "protein2.gat_ln",
        "protein1.gine_residual", "protein2.gine_residual",
        "protein1.gat_residual", "protein2.gat_residual",
        "protein1.geometric_input", "protein2.geometric_input",
        "protein1.geometric_block", "protein2.geometric_block"]),
    ("protein: MLP", ["protein1.mlp", "protein2.mlp"]),
    ("protein: self-attention, feed-forward, norms", ["protein1.attention",
        "protein2.attention", "protein1.post_sa", "protein2.post_sa",
        "protein1.ln", "protein2.ln"]),
    ("cross-attention, both directions", ["cross_attention1.", "cross_attention2."]),
    # Listed before the "final_layer." catch-all below (order matters, first match
    # wins): --pair_descriptors' self-attention head lives on final_layer but is its
    # own module (architecture/pair_descriptor_head.py), not part of the pool/binar/
    # adversary-head parameters "pooling and classifier" means to summarise.
    ("pair descriptor head (self-attention)", ["final_layer.pair_descriptor_head."]),
    ("pooling and classifier", ["final_layer."]),
]

# The one submodule per shape-hint category whose Linear stack is the "core" of that
# category and safe to render as "in → ... → out" -- final_layer also holds adversary
# heads and pool projections that would otherwise pollute the chain.
SHAPE_HINT_SUBMODULE = {
    "lipid: input projection": ("lipid1", "encodin"),
    "protein: ESM3 projection": ("protein1", "enc_plm"),
    "protein: MLP": ("protein1", "mlp"),
    "pooling and classifier": ("final_layer", "binar"),
}


def categorize(name):
    for label, prefixes in CATEGORIES:
        if any(name.startswith(prefix) for prefix in prefixes):
            return label
    top = name.split(".")[0]
    second = name.split(".")[1] if "." in name else ""
    return f"other: {top}.{second}"


def shape_hint(model, category):
    location = SHAPE_HINT_SUBMODULE.get(category)
    if location is None:
        return ""
    owner, attr = location
    root = getattr(model, owner, None)
    submodule = getattr(root, attr, None) if root is not None else None
    if submodule is None:
        return ""
    import torch

    linears = [m for m in submodule.modules() if isinstance(m, torch.nn.Linear)]
    if not linears:
        return ""
    dims = [linears[0].in_features]
    for linear in linears:
        dims.append(linear.out_features)
    return " → ".join(str(d) for d in dims)


def build_model(label, excluded_groups, seed):
    import torch  # noqa: F401  (import here: --help must not require torch)
    from read_configuration import read_named_configuration
    from architecture.interaction_classification import InteractionClassification

    path = resolve_args_file(label)
    flags = args_file_flags(path)
    flags = ensure_split_flags(flags, excluded_groups, seed)
    config = read_named_configuration(["prog"] + flags)
    model = InteractionClassification(config)
    return model, path, flags


def main():
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("label", help="arg_file stem, filename, or path")
    parser.add_argument("--excluded_groups", default="cral-trio",
        help="used only if the label needs one and does not set its own")
    parser.add_argument("--seed", default="0",
        help="used only if the label needs one and does not set its own")
    parser.add_argument("--show-flags", action="store_true",
        help="print the resolved flag list before the table")
    arguments = parser.parse_args()

    model, path, flags = build_model(arguments.label, arguments.excluded_groups, arguments.seed)

    if arguments.show_flags:
        print(f"# {path}")
        for flag in flags:
            print(f"#   {flag}")
        print()

    totals = {}
    for name, parameter in model.named_parameters():
        totals[categorize(name)] = totals.get(categorize(name), 0) + parameter.numel()

    grand_total = sum(totals.values())
    order = [label for label, _ in CATEGORIES] + sorted(
        label for label in totals if label.startswith("other:")
    )
    rows = [(label, totals[label]) for label in order if totals.get(label)]

    name_width = max(len(f"{label}{(' (' + shape_hint(model, label) + ')') if shape_hint(model, label) else ''}") for label, _ in rows)
    for label, count in rows:
        hint = shape_hint(model, label)
        shown = f"{label} ({hint})" if hint else label
        print(f"{shown:<{name_width}}  {count:>8}  {100 * count / grand_total:5.1f}%")
    print(f"{'total':<{name_width}}  {grand_total:>8}")


if __name__ == "__main__":
    main()
