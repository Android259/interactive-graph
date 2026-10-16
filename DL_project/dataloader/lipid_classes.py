"""Read lipid head-group classes from FullIdentityOfLipid.

This module has no torch dependency. Preprocessing and the loader share these
rules. dataloader.sampler re-exports them.
"""

import re

import pandas


def lipid_class_series(csv):
    """Return one head-group class per row, resolving ambiguous names."""
    names = csv["FullIdentityOfLipid"].astype(str).str.split(";")
    return names.map(_resolved_class)


# Resolve known ambiguities by shared candidate structures.
# Keep ambiguous species with the class sharing their structures to avoid split leakage.
# This choice does not establish their true chemical identity.
AMBIGUOUS_CLASS_RESOLUTION = {
    frozenset({"Bismonoacylglycerolphosphate", "Phosphatidylglycerol"}):
        "Phosphatidylglycerol",
    frozenset({"Lysophosphatidylcholine", "Phosphatidylcholine"}):
        "Phosphatidylcholine",
    frozenset({"Lysophosphatidylethanolamine", "Phosphatidylethanolamine"}):
        "Lysophosphatidylethanolamine",
}


def _resolved_class(names):
    classes = set()
    for name in names:
        name = re.sub(r"\s*\(.*", "", name)
        name = re.sub(r"^[^A-Za-z]+", "", name).strip()
        if name:
            classes.add(name)
    if not classes:
        return ""
    if len(classes) == 1:
        return classes.pop()
    resolved = AMBIGUOUS_CLASS_RESOLUTION.get(frozenset(classes))
    # Use sorted order for unknown ambiguities. Check structures before using a split.
    return resolved if resolved is not None else sorted(classes)[0]



def head_group_class(name):
    """Return the head-group class of one entry."""
    return _resolved_class(str(name).split(";"))


# Classes containing both ether and diacyl species in this dataset.
ETHER_SPLIT_ELIGIBLE_CLASSES = frozenset({
    "Phosphatidylcholine",
    "Phosphatidylethanolamine",
    "Lysophosphatidylethanolamine",
})


def ether_split_head_group_class(name):
    """Separate ether PC, PE, and LPE into -O classes.

    Use the ether marker of the resolved alternative.
    For equivalent splits, exclude both X and X-O instead of X.
    """
    names = str(name).split(";")
    resolved = _resolved_class(names)
    if resolved not in ETHER_SPLIT_ELIGIBLE_CLASSES:
        return resolved
    is_ether = False
    for raw in names:
        stripped = re.sub(r"\s*\(.*", "", raw)
        stripped = re.sub(r"^[^A-Za-z]+", "", stripped).strip()
        if stripped == resolved and re.search(r"\(O-", raw):
            is_ether = True
    return f"{resolved}-O" if is_ether else resolved


def ether_split_class_series(csv):
    """Return classes per row, with ether forms of PC, PE, and LPE separated."""
    return csv["FullIdentityOfLipid"].astype(str).map(ether_split_head_group_class)


def class_level_positive_labels(table):
    """Mark a row positive if its protein binds any lipid of that class.

    Use only training rows to avoid leaking held-out labels.
    """
    classes = lipid_class_series(table)
    return (
        table.assign(_lipid_class=classes)
        .groupby(["LTPProtein", "_lipid_class"])["Interaction"]
        .transform("max")
        .astype(int)
    )
