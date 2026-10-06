# geometric_edge on the plain random split, both encoder towers at width 32.
#
# Differs from geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_
# bilinear_norm_rand_esm3_protunion14_prothid32.md in the width lines ONLY: --hiddim goes
# 8 -> 32 and --protein_hiddim=32 is dropped. Everything else -- the 14-descriptor protein
# union, --protein_edge_mlp, ESM3 embeddings, --bilinear_fusion/--bilinear_pooled_norm,
# sampler, epochs, --random_split -- is copied over untouched.
#
# What that actually changes. There are exactly two encoder towers in this architecture,
# protein and lipid, and architecture/mlp_utils.py's branch_width gives each one
# --protein_hiddim/--lipid_hiddim, falling back to --hiddim when unset. The parent file
# set --hiddim=8 --protein_hiddim=32, so the protein tower ran at 32, the lipid tower at
# 8 (the fallback), and the hand-off to cross-attention stayed at config.hiddim=8 through
# the Linear(32 -> 8) width adapter InteractionClassification._width_adapter builds only
# when a tower's width differs from hiddim. Setting --hiddim=32 with no per-tower flag
# puts BOTH towers and the fusion/cross-attention width at 32 at once, and no width
# adapter is built on either side -- there is nothing left for it to convert.
#
# So this is not "the protein tower again, wider". It is three coupled changes the single
# --hiddim line makes at once: the lipid tower goes 8 -> 32, the cross-attention/fusion
# width goes 8 -> 32, and both width adapters disappear. Read a difference against the
# parent as the sum of those, not as a lipid-tower ablation.
#
# --random_split is a launcher marker, not a trainer flag (same contract as the bare
# --lipid_coldsplit line the parent's own header describes): the grid drops it and
# appends NOTHING, so training/new_train.py runs with no --excluded_groups and no
# --lipid_coldsplit, and Dataloader._split_interactions takes its last branch --
# csvt.sample(frac=0.85) for train, the remaining 15% halved label-by-label into
# validation and test. The reports land under exclusion_set "random", one directory per
# seed.
#
# Read with the caveat that applies to every warm-lipid number here: with all 35 proteins
# AND all lipids in training, both marginals are free, so pooled BA/F1 are an upper bound
# rather than a generalisation result. See the RULE box of
# files/lipid_coldsplit_architecture_direction.md. The parent scores test BA 0.822 /
# AUC 0.865 (5 seeds, graphics/<parent>/<parent>.md), which is the number to beat here --
# and beating it says the configuration is wider, not that it generalises.

--ep=120
--fast_attention

--hiddim=32

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent

--protein_edge_mlp

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--random_split
