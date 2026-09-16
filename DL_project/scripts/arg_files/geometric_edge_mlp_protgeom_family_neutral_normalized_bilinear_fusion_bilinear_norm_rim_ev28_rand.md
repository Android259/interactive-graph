# geometric_edge dcs baseline, measured on the plain random split.
#
# Differs from geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_
# bilinear_norm_rim_ev28.md in ONE line: --double_coldsplit is gone and --random_split
# takes its place, so no protein family and no lipid class leaves training. Every other
# flag -- architecture, descriptors, sampler, epochs -- is copied over untouched, which
# is what makes the pair readable as a split effect rather than a configuration effect.
#
# --random_split is a launcher marker, not a trainer flag (same contract as the bare
# --lipid_coldsplit and --family_only lines in their own files): the grid drops it and
# appends NOTHING, so training/new_train.py runs with no --excluded_groups at all and
# Dataloader._split_interactions takes its last branch -- csvt.sample(frac=0.85) for
# train, the remaining 15% halved label-by-label into validation and test. The reports
# land under exclusion_set "random" (training/new_train.py's excluded_set_name).
#
# Why it is worth a run. Under this split every evaluated lipid is also in training,
# paired with some other protein, so the block sits at the far right of the
# similarity-to-train axis (Tanimoto isolation ~1.0 against 0.46-0.77 for the four
# --lipid_coldsplit sets). It is the anchor the cold-split numbers are read against:
# without it, "test BA falls as the block gets chemically further from train" is a
# statement about four points that never reach the easy end of the axis. Measured by
# analysis/split_similarity_vs_metric.py, which rebuilds each run's own split.
#
# It is NOT a baseline to compare configurations on: nothing is held out, so the
# per-lipid and per-protein label priors are both free, and the number is an upper
# bound, not a generalisation result.
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

--no_protein_embeddings

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim

--protein_edge_mlp

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--random_split
