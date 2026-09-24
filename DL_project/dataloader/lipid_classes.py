"""The head-group class of a lipid, read from its `FullIdentityOfLipid` entry.

Its own module, and free of torch, so the preprocessing scripts can hold themselves to
the same rule as the loader. `dataloader.sampler` re-exports what is here, so nothing
that already imports it has to change.
"""

import re

import pandas


def lipid_class_series(csv):
    """Return the head-group class of every row, e.g. 'Phosphatidylcholine (34:1)' -> 'Phosphatidylcholine'.

    `FullIdentityOfLipid` spells the class out in full and puts the acyl composition in
    a trailing parenthesis; stripping that leaves 34 chemical classes over the 312
    distinct lipids. The class, not the individual species, is the level a binding
    preference actually lives at (a protein that takes PC(32:1) takes PC(34:1) too).

    Two entries carry a stray ': ' prefix -- ': Phosphatidylcholine (32:2)' and
    ': Phosphatidylglycerol (32:1)', 35 rows each. Dropping only the parenthesis left
    them as classes of their own, so phosphatidylcholine and phosphatidylglycerol each
    came out split in two and the count read 36. That is harmless for a balancer, which
    merely matched two extra tiny cells, and not harmless at all for a split that holds
    whole classes out of training: the real class would land in one fold and its double
    in another, and the class prior would cross the cut through those 70 rows. Leading
    punctuation is therefore removed before the class is read.

    A species the spectrometer could not assign to one head group is written as both,
    joined by ';' -- 'Phosphatidylglycerol (33:1);Bismonoacylglycerolphosphate (33:1)'.
    The two names are not always written in the same order, and reading the class off the
    text up to the first parenthesis then made the class depend on that order: six
    species came out as phosphatidylglycerol under one spelling and
    bismonoacylglycerolphosphate under the other, 420 rows and 15 positives in all. Hold
    one of the two classes out and the species sat in training and in the held-out block
    at once, which is exactly the leak the paragraph above is about. Every name in the
    entry is therefore read, and AMBIGUOUS_CLASS_RESOLUTION names the class, so a species
    reaches the same class whichever way round its entry happens to be written.
    """
    names = csv["FullIdentityOfLipid"].astype(str).str.split(";")
    return names.map(_resolved_class)


# The three head-group ambiguities the table records, and the class each resolves to.
# Each is resolved to the class it actually shares candidate structures with, counted
# over the whole table: the 22 PG/BMP entries carry 102 structures that also belong to an
# unambiguous PG species and none belonging to BMP, the 13 PC(O-)/LPC entries 8 that
# belong to PC and none to LPC, and the 3 PE(O-)/LPE entries 4 that belong to LPE and
# none to PE. The last of the three goes to the smaller class, so class size is not the
# rule and guessing from the names would have got it wrong.
# Sending an entry to the class it does not share structures with breaks the split at
# the structure level even though no species is shared: hold out one class and the
# ambiguous species sits opposite its own structures, and PG/BMP(34:1) in the block then
# shares 18 candidate structures with PG(34:1) in training. Resolving to the larger class
# keeps every structure on one side of the cut.
#
# Which of the two the species really is remains unknown -- the measurement does not say.
# What the split needs is only that the answer never depends on the order the two names
# happen to be written in, which is what this table provides.
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
    # An ambiguity the table did not carry when the entry above was written. Sorted order
    # keeps it deterministic, which is the property the split cannot do without; check it
    # against its structures before trusting the block it produces.
    return resolved if resolved is not None else sorted(classes)[0]



def head_group_class(name):
    """The class of one entry, for callers that hold a name rather than a table."""
    return _resolved_class(str(name).split(";"))


# The only 3 project classes that mix an ether-linked ("(O-...)") and a diacyl species
# under one name -- verified once against the live table (data/Processed_Negative_
# Interaction_Corrected_Domains_SMILES_Fixed_CandidatesCompleted_Deduplicated.csv):
# Phosphatidylcholine (45 diacyl / 31 ether), Phosphatidylethanolamine (22/2),
# Lysophosphatidylethanolamine (9/1). Every other class's species are all-ether or
# all-diacyl already, so splitting them would produce an empty second class.
ETHER_SPLIT_ELIGIBLE_CLASSES = frozenset({
    "Phosphatidylcholine",
    "Phosphatidylethanolamine",
    "Lysophosphatidylethanolamine",
})


def ether_split_head_group_class(name):
    """head_group_class(name), except PC/PE/LPE keep the ether ("(O-...)") linkage as
    its own class ("Phosphatidylcholine-O", ...) instead of folding it into the diacyl
    one -- the variant lipid_class_series()/csv_classes() do NOT use by default (see
    files/data_source.md's own note on why PC-O/PE-O are folded into PC/PE there: the
    sn-1 linkage is not exposed to headgroup readout, and it is tracked separately as
    the continuous `ether_tail_count` descriptor, training.pair_baseline_common's
    lipid_chemistry_descriptors).

    Whether a name is "ether" is read off the SPECIFIC semicolon-segment that produced
    the resolved class, not the row as a whole -- an ambiguous entry like
    "Lysophosphatidylethanolamine (18:1);Phosphatidylethanolamine (O-18:1)" resolves to
    LPE (AMBIGUOUS_CLASS_RESOLUTION), and its LPE-side segment itself carries no "O-",
    so it stays plain LPE, not LPE-O -- the ether marker sat on the PE alternative the
    resolution already rejected. This mirrors the original class's own structure-
    verified ambiguity resolution instead of second-guessing it.

    No caller in this project uses this to build a split today -- --lipid_coldsplit's
    "choline" set and --lipid_subclass's PC/PE/LPC+LPE+LPG blocks still hold out the
    SAME species under the plain classes above; splitting those species between two
    classes here would silently shrink what a run built against the un-split names
    excludes unless the caller also names the "-O" sibling. Any caller adopting this
    classification must exclude both `X` and `X-O` wherever the un-split scheme named
    plain `X`, to keep held-out species sets unchanged.
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
    """lipid_class_series(csv), through ether_split_head_group_class per row."""
    return csv["FullIdentityOfLipid"].astype(str).map(ether_split_head_group_class)


def class_level_positive_labels(table):
    """Coarsen `Interaction` from "this exact lipid" to "this lipid's head-group class".

    A row reads positive here whenever its own protein (`LTPProtein`) has a measured
    positive against ANY lipid sharing this row's head-group class in `table` -- not
    only when the row's own species was screened positive. This is a training-target
    transform, not a re-labelling of the data: it exists so a model can be asked to
    predict "does this protein take this lipid's class" instead of "this exact
    molecule", while the (protein, lipid) pair fed in and scored out stay exactly what
    they are today. Callers must build this only from rows the model is allowed to
    train on (e.g. the train split alone) -- computing it over rows a cold split holds
    out would leak their positives into the classes those very rows supply.
    """
    classes = lipid_class_series(table)
    return (
        table.assign(_lipid_class=classes)
        .groupby(["LTPProtein", "_lipid_class"])["Interaction"]
        .transform("max")
        .astype(int)
    )
