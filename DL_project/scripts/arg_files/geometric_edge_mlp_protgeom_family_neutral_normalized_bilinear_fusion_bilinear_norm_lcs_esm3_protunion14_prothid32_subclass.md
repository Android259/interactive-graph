# Exact sibling of geometric_edge_mlp_..._protunion14_prothid32.md, ONE line changed:
# --lipid_coldsplit -> bare --lipid_subclass. Every --protein_descriptors name, every
# other flag, is copied verbatim -- see that file's own header for the reasoning behind
# them (protunion14, --protein_edge_mlp, --protein_hiddim=32, --bilinear_fusion).
#
# WHY THIS FILE, SEPARATE FROM THAT ONE
#
# --lipid_coldsplit holds out one of four HAND-BUILT class sets (dataloader/sampler.py's
# LIPID_COLDSPLIT_SETS: sphingolipids, phosphorus_free, choline, anionic) -- a partition
# this project chose, not the one the collaborators asked for. --lipid_subclass, bare,
# holds out one Titeca-et-al. SUBCLASS at a time (nine blocks,
# dataloader/lipid_subclass_blocks.py's FIG3_SUBCLASS_BLOCKS: PC, PG, FA, PE,
# Cer+CerP+HexCer+Hex2Cer+SHexCer+SM, PI, LPC+LPE+LPG, PA, PS+PGP+DAG+TAG) -- the
# partition the task definition actually names: "See the third column in the attached
# CSV... being able to classify binders and non-binders by lipid subclass would be
# quite helpful already." Same axis, same mechanics (every protein stays in training,
# the held-out chemistry leaves for all of them at once), different, and now the
# RIGHT, partition.
#
# This is also the first test of that question on an architecture that actually reads
# the PROTEIN pocket. The one result so far on this axis
# (files/split_similarity_four_baselines_and_deepclip.md section 5,
# deepclip_f1_normal_mean_cral_trio_subclass_pg_npp5_ep120) is DeepCLIP -- a lipid-only
# branch, ~2000 parameters, no pocket input at all -- scoring at chance (mean AUC 0.545,
# collapse_fraction 0.78) on one block inside one family. It says nothing about whether
# a model that reads pocket chemistry can do better; this file is what answers that.
#
# HOW TO READ THE RESULT
#
# Rank by AUC_within_protein, not pooled BA/AUC -- the project's own rule for this axis
# (files/lipid_coldsplit_architecture_direction.md section 7j): every protein stays in
# training here, so "which protein is this" is free, and the pooled figure is largely
# that marginal. Read AUC_within_protein_proteins beside it -- a mean over 2 proteins
# and a mean over 16 are not the same kind of number. Sizes, per
# analysis/lipid_subclass_block_report.py --blocks fig3 (measured on the whole table,
# not restricted to any one family the way the DeepCLIP file's numbers are):
#
#   block                                positives  proteins-with-a-positive  headgroup-Tanimoto
#   PC                                         218                16                0.709
#   PG                                         113                13                0.780
#   FA                                          48                12                1.000 (no head group to hold out)
#   PE                                          80                11                0.719
#   Cer+CerP+HexCer+Hex2Cer+SHexCer+SM          66                 4                0.262 (only genuinely cold block)
#   PI                                          16                 6                0.635
#   LPC+LPE+LPG                                 32                 6                0.739
#   PA                                          26                 4                0.698
#   PS+PGP+DAG+TAG                              17                 6                0.674
#
# PI and PS+PGP+DAG+TAG were already unreadable on this same axis under Kron-RLS
# (files/fig3_lipid_subclass_coldsplit_results.md: PI's AUC_in_protein came out BELOW
# chance at n_proteins=2, PS+PGP alone reached n_proteins=0 before this file's four-way
# merge) -- read them with that history in mind, not as fresh surprises. FA's headgroup
# Tanimoto of 1.0000 is not cold at all: a free fatty acid has no head group to hold out,
# so a weak result there is a feature-coverage question, not a chemistry-generalisation
# one -- see files/binding_determinants_literature_and_feature_proposals.md.
#
# --no_groups/--groups do not apply to this axis (both name protein families); the
# launcher already prints that and runs all nine blocks regardless.
#
# Not yet run.

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
--save_model

--balanced_batches
--balanced_proteins
--lipid_subclass
