import numpy as np

# Share lipid-level means across candidates. Values below are fallbacks for
# lipids with no known candidate value; None requires an error.
LIPID_LEVEL_MEASURES = {
    "tail_double_bond_position": 0.0,  # no double bond: nothing to measure
    "experimental_lipid_volume": None,  # the sheet lists one isomer per lipid
}


def share_value_within_lipid(values, lipids, label, if_none_known):
    """Give every candidate of a lipid the mean of that lipid's known candidate values.

    `values` is one array per table row (one entry per candidate, NaN where unknown) and
    `lipids` the lipid name of every row. A lipid with no known value gets `if_none_known`.
    """
    known = {}
    for lipid, row in zip(lipids, values):
        known.setdefault(lipid, []).extend(row[~np.isnan(row)].tolist())
    means = {}
    for lipid, found in known.items():
        if found:
            means[lipid] = float(np.mean(found))
        elif if_none_known is None:
            raise ValueError(f"{label}: lipid {lipid!r} has no known value in any candidate")
        else:
            means[lipid] = if_none_known
    return [np.full(len(row), means[lipid]) for lipid, row in zip(lipids, values)]


def require_no_missing(values, label):
    """Raise if any candidate value is NaN (reported, not filled in)."""
    missing = sum(int(np.isnan(row).sum()) for row in values)
    if missing:
        raise ValueError(f"{label}: {missing} candidate values are missing")
    return values
