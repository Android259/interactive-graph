"""Define head-group class sets for --lipid_coldsplit.

Lipid-axis alternatives:
--lipid_coldsplit: four hand-built project class sets (here).
--lipid_isolation: blocks at a target Tanimoto isolation.
--lipid_subclass: a Titeca et al. Figure 3a subclass.
--lipid_species_coldsplit: a seeded draw of individual lipids.

lipid_classes_for_holdout derives family-specific class sets from the table
for --double_coldsplit/--mixed_coldsplit instead of using fixed sets.
This module selects excluded chemistry; sampler.py draws remaining negatives.
"""
from dataloader.lipid_classes import lipid_class_series


# Hold out whole chemical groups while retaining all proteins, testing known
# proteins on new chemistry as the screening panel grows.
# Group related chemistry, not counts, to exclude close relatives together.
# Recorded compact-Tanimoto mean best similarity to training, with positives:
#   sphingolipids   0.458   85 (11.2%): sphingoid backbones
#   phosphorus_free 0.553  61 (8.1%): neutral glycerolipids, fatty acids, retinol
#   choline        0.653  258 (34.1%): diacyl and lyso phosphocholine
#   anionic        0.766  228 (30.2%): anionic glycerophospholipids
# The first three are more isolated. Anionic PA/PI/PS/PG share acyl chains
# with retained PC, so fingerprints stay similar despite different heads.
# Smaller sets were less isolated: PG+LPG+PGP 0.872, BMP+cardiolipin 0.946.
# Keep anionic as the harder head-group test.
# PE/LPE remain in training: their isolation was 0.778, offering no improvement
# over anionic to justify a fifth set.
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
    """Select head-group classes to exclude when family is held out.

    Rank by family positives / (other-family positives + 1), then add classes
    until they cover share of family positives. The numerator is test gain;
    the denominator reflects training cost. START favors PC and GLTP favors
    sphingolipids, so one fixed class set would not suit every family.
    Recorded costs: two GLTP classes remove one other-family positive;
    three PC-dependent families cost 128-238 positives.

    Stopping early can leave familiar lipids dominating evaluation.
    At share=0.3 the lipocalin lookup scored 0.618. share=0.7 was the lowest
    checked value with every family within one standard error of 0.5.
    preprocessing/lipid_marginal_baseline.py measures this residual prior.

    ML and OSBP have only 10 and 8 positives, below
    COLDSPLIT_MINIMUM_TEST_POSITIVES. Return their small blocks unchanged;
    callers report insufficient coverage instead of special-casing the split.
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
