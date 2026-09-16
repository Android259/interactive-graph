# descriptors_head lcs baseline, measured on the plain random split.
#
# Differs from descriptors_head_family_neutral_lipprop_lcs_protbind6.md in ONE line:
# --lipid_coldsplit is gone and --random_split takes its place, so no chemical set leaves
# training. Every other flag -- the 17 descriptor names (the family-neutral 11 plus the
# six protein-binding ones), --lipid_propensity_weight, --balanced_lipid_classes, epochs
# -- is copied over untouched. `lcs` in the name is replaced by `rand` rather than
# appended to, because the label names the split the run actually used and
# metrics_summary.csv is keyed on it.
#
# --random_split is a launcher marker, not a trainer flag (same contract as the bare
# --lipid_coldsplit line it replaces): the grid drops it and appends NOTHING, so
# training/new_train.py runs with no --excluded_groups and no --lipid_coldsplit, and
# Dataloader._split_interactions takes its last branch -- csvt.sample(frac=0.85) for
# train, the remaining 15% halved label-by-label into validation and test. The reports
# land under exclusion_set "random", one directory per seed instead of four lipid sets.
#
# --balanced_lipid_classes is kept even though its own reason -- flattening the
# per-lipid-class positive prior the held-out chemistry would otherwise be scored by --
# is about the cold split. It stays because the whole point of this file is that ONE
# line differs from its sibling; changing the sampler too would make the pair unreadable
# as a split effect. What it does here is only what it always does: match negatives per
# (family, lipid class) in the pool.
#
# Why it is worth a run. Right-hand anchor of the similarity-vs-metric curve
# (analysis/split_similarity_vs_metric.py): Tanimoto isolation ~1.0 against 0.458-0.766
# for the four --lipid_coldsplit sets this configuration has already been run on.
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
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean

--save_model_in_dynamics

--balanced_batches
--balanced_lipid_classes
--random_split
