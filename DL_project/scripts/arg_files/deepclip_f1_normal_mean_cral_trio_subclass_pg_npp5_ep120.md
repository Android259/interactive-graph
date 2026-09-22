# DeepCLIP on a lipid-side cold split that is actually big enough to read.
#
# Differs from deepclip_f1_normal_mean_cral_trio_warm_ep120.md by two lines:
# --lipid_subclass=PG (the block) and --negatives_per_positive=5 (its size). The arm
# itself is unchanged -- f1_normal_mean, the pick of the five in
# files/deepclip_results_and_hard_negatives.md section 6.
#
# WHAT IS WRONG WITH THE EXISTING POINTS
#
# Measured directly, per block, by analysis/split_similarity_vs_metric.py over the 41
# completed runs of deepclip_f1_normal_mean_ep120 (files/split_similarity_four_
# baselines_and_deepclip.md): all nine --family_only blocks sit at Tanimoto isolation
# 0.889-0.995 and hold 2-22 TEST ROWS. That is not a cold split failing, it is a warm
# split too small to read -- the axis is never exercised, and the per-cell seed spread
# (0.10-0.22 BA) is larger than any effect being looked for. The five cral_trio__iso*
# rungs fixed the isolation but not the size: they run at
# --negatives_per_positive=2 on 15-34 positives.
#
# WHY CRAL-TRIO x PG
#
# Counts from analysis/lipid_subclass_block_report.py --blocks fig3 --by_family all.
# A cell has to satisfy three things at once, and almost none do:
#
#   block held out        enough positives IN the block to measure on
#   train left behind     enough positives NOT in the block to still train on
#   lipid-only ceiling    the best AUC any lipid-only model could reach there at all
#                         (the same species is a positive with one protein of the family
#                         and a negative with another; DeepCLIP sees no protein and
#                         cannot be right on both)
#
#   cell                    block pos   train pos left   test rows npp=5   ceiling npp=5
#   CRAL-TRIO x PG               53         112               159              0.830
#   CRAL-TRIO x PE               40         125               108              0.919
#   START x PC                   90          60               114              0.844
#   CRAL-TRIO x PC               21         144                63              0.988
#   GLTP x sphingolipids         51          11                65              0.677
#   LBP_BPI_CETP x PC            40          13                76              0.989
#
# PG is the largest block that still leaves two thirds of the family's positives in
# training. GLTP x sphingolipids is the only chemically COLD cell in the table
# (head-group Tanimoto 0.262 against PG's 0.780) and is unusable for the opposite
# reason: it takes 51 of GLTP's 62 positives, leaving 11 to train on. That tension is
# not a choice being dodged here -- there is no cell in this dataset that is both cold
# and large, and this file takes size.
#
# --negatives_per_positive=5 rather than 2: it is what turns a 79-row test block into a
# 159-row one, and the block holds 316 negatives so 5 is inside what exists (at 5 the
# draw takes 265 of them). It is not free -- the lipid-only ceiling falls from 0.891 at
# 2:1 to 0.830 at 5:1, because a higher ratio actually draws the colliding species that
# a 2:1 draw skips. Both numbers are the ceiling, not a prediction: a result is to be
# read as a fraction of 0.830, not against 1.0.
#
# HOW TO RUN IT
#
# --family_only=cral-trio is VALUED, so this is one job per seed, not nine (see any
# cral_trio sibling's header). Ten seeds, not the default five: the point of the file is
# statistical readability, and seeds are what buys it on a 1960-parameter model --
#     scripts/run_cluster.sh --seeds=0,1,2,3,4,5,6,7,8,9 <this file>
# To move the block, change the one --lipid_subclass line to any spec in the table
# above (the grid keys the run directory on it, so the points do not collide).
#
# Reference points this run is read against, both already measured on the same family
# and the same arm: the warm anchor deepclip_f1_normal_mean_cral_trio_warm_ep120
# (BA 0.728 +/- 0.024, AUC 0.776, isolation ~1.0) and the two ladder rungs that are
# already subclass holdouts in disguise -- iso80 (phosphatidylcholines, 100%) at
# BA 0.544 and iso85 (phosphatidylethanolamines, 100%) at BA 0.777.
#
# Not yet run.

--ep=120
--family_only=cral-trio
--deepclip
--lipid_smiles_tokens
--deepclip_filters=1
--deepclip_widths=4,5,6,7,8
--deepclip_lstm=10
--deepclip_lstm_dropout=0.1
--deepclip_conv_init=normal
--deepclip_readout=mean

# Sampler fix of files/deepclip_results_and_hard_negatives.md section 4, with the ratio
# raised from the siblings' 2 to 5 -- see the header for what that buys and what it
# costs.
--balanced_proteins
--balanced_batches
--negatives_per_positive=5
--lipid_subclass=PG
