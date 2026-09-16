# descriptors_head dcs baseline, measured on the plain random split.
#
# Differs from descriptors_head_family_neutral_lipprop.md in ONE line: --double_coldsplit
# is gone and --random_split takes its place, so no protein family and no lipid class
# leaves training. Every other flag -- the 11 descriptor names, --lipid_propensity_weight,
# sampler, epochs -- is copied over untouched.
#
# --random_split is a launcher marker, not a trainer flag (same contract as the bare
# --lipid_coldsplit and --family_only lines in their own files): the grid drops it and
# appends NOTHING, so training/new_train.py runs with no --excluded_groups at all and
# Dataloader._split_interactions takes its last branch -- csvt.sample(frac=0.85) for
# train, the remaining 15% halved label-by-label into validation and test. The reports
# land under exclusion_set "random".
#
# Why it is worth a run. It is the right-hand anchor of the similarity-vs-metric curve
# (analysis/split_similarity_vs_metric.py): the block this run is tested on is chemistry
# already in training, Tanimoto isolation ~1.0, against 0.46-0.77 for the four
# --lipid_coldsplit sets and the per-family two-axis blocks. Without it the curve has no
# point at the easy end and its slope is read off cold blocks alone.
#
# Note what this architecture scores here and what it does not settle. On the two-axis
# split this configuration loses to the chemistry null model on AUC (0.529 against
# 0.596, files/dcs_lcs_final_baseline_decision.md §0); a high number on a warm split
# would not repair that, because with every lipid in training the per-lipid label prior
# -- the thing the null model is -- is free to replay.
#
# Run 2026-09-16; the point it contributes is the x = 1.000 anchor of
# graphics/<label>/split_similarity/ (see files/split_similarity_vs_metric.md).

--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptors_head
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--random_split
