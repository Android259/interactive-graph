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
