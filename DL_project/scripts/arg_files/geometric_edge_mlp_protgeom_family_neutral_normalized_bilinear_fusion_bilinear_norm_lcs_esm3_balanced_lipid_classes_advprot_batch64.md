# ..._advprot at --batch=64, to remove the one confound between the two marginal-removal
# mechanisms.
#
# Why. The ranking arms (..._rankprot, ..._rankprot_advprot) are forced to --batch=64:
# at 16 a batch rarely holds two rows of one protein with opposite labels, the pairwise
# loss returns a plain zero with no grad_fn and the run dies at epoch 1. The adversary
# arms run at 16. From the logs that is 18 balanced batches per epoch against 72 -- the
# rank arms take FOUR TIMES FEWER optimizer steps for the same 120 epochs.
#
# Every "rank moves anionic, the adversary moves choline" statement therefore compares
# two interventions at different step counts, in the adversary's favour. This run puts
# the adversary on the rank arms' step budget so the comparison is single-variable.
#
# WHAT TO EXPECT: if the set-level split of labour is real, advprot at 64 still moves
# choline and still does not move anionic. If it is a step-count artefact, advprot at 64
# starts to look like rankprot -- and then the two mechanisms were never doing different
# things.
#
# Read by AUC_within_protein_pairs.

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
--adversarial_grl
--no_adv_lipid
--batch=64
--save_checkpoint
