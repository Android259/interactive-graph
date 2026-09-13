# descriptors_head_family_neutral_lipprop_lcs.md + item D (files/reference_baselines_
# metrics_proposal.md section 3): --loss_type=pairwise_rank --rank_within_protein
# instead of --adversarial_grl (which item C rules out under descriptors_head). On
# geometric_edge_mlp under lcs this gave the same qualitative shift as advprot --
# pooled BA down, within-protein AUC up (lipid_coldsplit_architecture_direction.md
# section 7j/7n) -- but note descriptors_head under double_coldsplit's own rankprot
# variant behaved differently (sensitivity collapse on 4/9 families, see
# files/geometric_edge_descriptors_baseline_selection_results.md section 2.3) -- this
# is the first time rankprot is tried on descriptors_head under lcs specifically.
# --batch=32 leaves ~17 same-protein pairs per batch (vs ~4 at batch=16, 10% empty) --
# same reasoning as descriptors_head_family_neutral_lipprop_rankprot.md's own comment.

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

--loss_type=pairwise_rank
--rank_within_protein
--batch=32

--save_model_in_dynamics

--balanced_batches
--balanced_lipid_classes
--lipid_coldsplit
