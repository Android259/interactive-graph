"""The lipid axis cut BY PROJECT HEAD-GROUP CLASS SET, for --lipid_coldsplit.

The first of the four cuts on the lipid side, and the one the other three are
defined against:

  --lipid_coldsplit   four hand-built sets of project head-group classes (here)
  --lipid_isolation   a block chosen by Tanimoto distance to a target isolation
  --lipid_subclass    one subclass of Titeca et al. (a head-group row of Figure 3a)
  --lipid_species_coldsplit   a seeded draw of individual lipids

`lipid_classes_for_holdout` is the --double_coldsplit/--mixed_coldsplit form of the
same axis: the class set is read off the table per held-out family instead of being
fixed in advance.

Lives here rather than in dataloader/sampler.py because it decides WHICH chemistry
leaves training, not how negatives are drawn from the pool that stays.
"""
from dataloader.lipid_classes import lipid_class_series


# Lipid-class sets for --lipid_coldsplit: whole chemical families held out of training
# while every protein stays in it. The question they ask is the other one from the
# protein-family split -- a lipid of a chemistry never seen arrives, which of the known
# proteins bind it -- and it is the one that matters when the screening panel grows.
#
# Grouped by chemistry rather than by count, because a set is only cold if its close
# relatives leave with it. Measured on the compact Tanimoto matrix as the mean over the
# set's structures of the highest similarity to anything left in training:
#
#   sphingolipids    0.458   85 positives (11.2%)   sphingoid backbone, all of it
#   phosphorus_free  0.553   61 positives ( 8.1%)   no phosphate: neutral glycerolipids,
#                                                   free fatty acids, retinol
#   choline          0.653  258 positives (34.1%)   phosphocholine head, di- and lyso-
#   anionic          0.766  228 positives (30.2%)   anionic glycerophospholipid heads
#
# The first three are genuinely isolated. `anionic` is not, and cannot be: PA, PI, PS,
# PG and their relatives differ from the phosphatidylcholines that stay behind only in
# the head group, while a fingerprint sees mostly the two acyl chains, so 0.77 is what
# the chemistry allows. Splitting it makes that worse, not better (PG+LPG+PGP alone
# comes out at 0.872, BMP+cardiolipin alone at 0.946). Kept as the hardest of the four:
# it asks whether the model reads the head group at all.
#
# Phosphatidyl- and lysophosphatidylethanolamine are in no set. They would isolate no
# better than `anionic` (0.778) and there is no reason to spend a fifth run on them;
# they stay in training throughout.
LIPID_COLDSPLIT_SETS = {
    "sphingolipids": (
        "Sphingomyelin",
        "Ceramide",
        "Ceramide phosphate",
        "Hexosyl ceramide",
        "Dihexosyl ceramide",
        "Sulfohexosyl ceramide",
    ),
    "phosphorus_free": (
        "Diacylglycerol",
        "Triacylglycerol",
        "Retinol",
        "docosapentaenoate",
        "docosatetraenoate",
        "docosatrienoate",
        "eicosapentaenoate",
        "eicosatetraenoate",
        "eicosatrienoate",
        "heptadecenoate",
        "hexadecenoate",
        "nonadecenoate",
        "octadecadienoate",
        "octadecatrienoate",
        "octadecatrienol",
        "octadecenoate",
    ),
    "choline": (
        "Phosphatidylcholine",
        "Lysophosphatidylcholine",
    ),
    "anionic": (
        "Phosphatidate",
        "Phosphatidylinositol",
        "Phosphatidylserine",
        "Phosphatidylglycerol",
        "Lysophosphatidylglycerol",
        "Phosphatidylglycerophosphate",
        "Bismonoacylglycerolphosphate",
        "Cardiolipin",
    ),
}


COLDSPLIT_MINIMUM_TEST_POSITIVES = 20


def lipid_classes_for_holdout(csv, family, share):
    """The head-group classes to hold out of training when `family` is held out.

    The second axis of the cold split needs its own class set per family, not one shared
    set: a family's positives sit in its own classes -- START's in phosphatidylcholines,
    GLTP's in sphingolipids -- so any set fixed in advance is arbitrary for whichever
    family is being held out. Classes are scored by concentration,

        score(class) = family positives in class / (everyone else's positives there + 1)

    and taken by descending score until the family's covered positives reach `share` of
    its total. The numerator is what the held-out block gains, the denominator what
    training loses elsewhere, so what gets held out is what the family owns. GLTP comes
    out at two classes costing training a single positive; the three families that need
    phosphatidylcholine cost it 128-238.

    `share` is not cosmetic. Stopping early leaves only the cheap classes, and for a
    family whose cheap classes are thin on rows the held-out block ends up almost
    entirely familiar lipids -- the split looks two-axis while the per-lipid label prior
    still carries it. At 0.3 the lipocalin lookup baseline stays at 0.618; 0.7 is the
    smallest value at which no family sits further than one standard error from 0.5.

    Whether the rule worked is not decided here but by
    preprocessing/lipid_marginal_baseline.py, which measures that prior on the split it
    produces. Families too small for a test block at all (ML and OSBP, 10 and 8
    positives) come back with fewer than COLDSPLIT_MINIMUM_TEST_POSITIVES covered;
    callers that care report it, the split itself does not special-case them.
    """
    positives = csv[csv["Interaction"] == 1]
    lipid_classes = lipid_class_series(positives)
    family_rows = positives["ProteinDomain"].str.lower() == str(family).lower()

    everywhere = lipid_classes.value_counts()
    mine = lipid_classes[family_rows].value_counts()
    if mine.empty:
        return [], 0, 0

    elsewhere = everywhere.reindex(mine.index).fillna(0) - mine
    score = (mine / (elsewhere + 1)).sort_values(ascending=False)

    target = max(
        COLDSPLIT_MINIMUM_TEST_POSITIVES,
        int(round(int(family_rows.sum()) * share)),
    )
    chosen = []
    covered = 0
    for lipid_class in score.index:
        if covered >= target:
            break
        chosen.append(lipid_class)
        covered += int(mine[lipid_class])

    cost = int(everywhere.reindex(chosen).sum()) - covered
    return chosen, covered, cost
