# Double the gradient-reversal strength, over ..._advprot. Sibling of ..._lambda05 --
# the two exist to give the knob a SLOPE rather than one point, the way --lipid_hiddim
# 32 and 64 did for lipid width (files/lipid_coldsplit_architecture_direction.md
# section 7k: two flat points is a different, stronger statement than one).
#
# Why this direction is not obviously wrong even though the model already underfits: the
# suppression target is the protein branch alone (--no_adv_lipid), and the diagnosis
# behind the whole line is that this split leaves the protein marginal free. If 1.0 is
# still on the slope, 2.0 removes more of it and the within-protein number rises further
# while pooled BA falls further -- pooled BA falling is expected under both siblings and
# is not evidence of anything by itself.
#
# WHAT TO EXPECT: at 2.0 either within-protein rises above advprot's 0.604 on choline
# (the knob is live and 1.0 was too weak), or train BA drops below 0.55 with
# within-protein flat or worse (1.0 was already past the optimum, and ..._lambda05 is the
# direction to keep).
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
--adv_lambda=2.0
--save_checkpoint
