# One intervention against ..._lcs_esm3_balanced_lipid_classes: the objective stops
# optimising the pooled block and starts optimising ranking WITHIN a protein.
#
# Why, from measurement rather than taste. On that baseline, scored on identical rows
# (files/lipid_coldsplit_architecture_direction.md section 7j): pooled test AUC 0.568,
# AUC inside a protein 0.480. On the two sets with enough protein blocks to read (11 and
# 10) it is 0.460 and 0.457 -- chance. Meanwhile AUC within a lipid class ACROSS proteins
# is 0.611 on anionic. The pooled number is the protein marginal, which is free under
# --lipid_coldsplit because every protein is in training, and it says nothing about which
# lipid a protein binds.
#
# --rank_within_protein pairs rows only with rows of the SAME protein, so that marginal
# cannot be what the loss improves. ModelConfig's own docstring for the flag states the
# same diagnosis: "Without it the ranking loss optimises the pooled-block AUC, which on
# this dataset is mostly the chemical marginal a protein-blind null model already
# answers. With it the loss optimises what ranks a protein's own lipids against each
# other, which is the interaction term."
#
# It has been run five times before -- bbp_dcs_smd_fa_nps_rankprot_*,
# geometric_edge_mlp_protgeom8_normalized_rankprot, descriptors_*_rankprot -- and every
# one was on the DOUBLE cold split, where the protein itself is held out and there is
# nothing to rank its own candidates by (test BA 0.51-0.58, nothing). Under the LIPID
# split it has never run, and that is the only split where it can work: the protein is in
# training, so within-protein ranking is learnable, and the marginal it removes is exactly
# the one the network is currently riding.
#
# Read the result by AUC_within_protein, not by test BA: --loss_type=pairwise_rank
# optimises an ordering, so a threshold metric at 0.5 is not what it is trying to move.
# validate() requires the two flags together.

--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim

--protein_edge_mlp

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--balanced_lipid_classes
--lipid_coldsplit
--loss_type=pairwise_rank
--rank_within_protein
# REQUIRED, and its absence is what killed the first attempt at this label: at batch=16
# a batch rarely holds two rows of the SAME protein with opposite labels, so
# pairwise_ranking_loss returns a plain zero with no grad_fn and the run died at epoch 1
# with "element 0 of tensors does not require grad". bbp_dcs_smd_fa_nps_rankprot_...
# carries the same flag for the same reason, with its own measurement in the file:
# "batch=16 leaves only 3.95 same-protein pairs per batch and 10% of batches with none
# at all; 32 gives 16.9 pairs and no empty batch". 64 rather than 32 because that
# measurement was on a PROTEIN cold split, where one family is out of train; here all 35
# proteins stay in, so the same batch is spread over more of them and pairs are rarer.
--batch=64
