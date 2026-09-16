# geometric_edge lcs baseline, measured on the plain random split.
#
# Differs from geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_
# bilinear_norm_lcs_esm3_protunion14_prothid32.md in ONE line: --lipid_coldsplit is gone
# and --random_split takes its place, so no chemical set leaves training. Every other
# flag -- the 14-descriptor protein union, --protein_hiddim=32, ESM3 embeddings left on,
# sampler, epochs -- is copied over untouched. `lcs` in the name is replaced by `rand`
# rather than appended to, because the label names the split the run actually used and
# metrics_summary.csv is keyed on it.
#
# --random_split is a launcher marker, not a trainer flag (same contract as the bare
# --lipid_coldsplit line it replaces): the grid drops it and appends NOTHING, so
# training/new_train.py runs with no --excluded_groups and no --lipid_coldsplit, and
# Dataloader._split_interactions takes its last branch -- csvt.sample(frac=0.85) for
# train, the remaining 15% halved label-by-label into validation and test. The reports
# land under exclusion_set "random", one directory per seed instead of four lipid sets.
#
# Why it is worth a run. The four --lipid_coldsplit sets cover Tanimoto isolation
# 0.458-0.766 and stop there; this run puts the same architecture at ~1.0, where every
# evaluated lipid is in training paired with another protein. That is the right-hand
# anchor of the similarity-vs-metric curve (analysis/split_similarity_vs_metric.py) and
# the only point on it that says what this configuration scores when the chemistry is
# not new at all.
#
# Read with the caveat that applies to every warm-lipid number here: with all 35
# proteins AND all lipids in training, both marginals are free, so pooled BA/F1 are an
# upper bound rather than a generalisation result. See the RULE box of
# files/lipid_coldsplit_architecture_direction.md.
#
# Run 2026-09-16; the point it contributes is the x = 1.000 anchor of
# graphics/<label>/split_similarity/ (see files/split_similarity_vs_metric.md).

--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent

--protein_edge_mlp
--protein_hiddim=32

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--random_split
