# Adapts descriptors_head_family_neutral_lipprop.md (dcs) to --lipid_coldsplit --
# items A+B of files/reference_baselines_metrics_proposal.md section 3, the two
# mechanical/required flips only. That file's own summary states no descriptors_head
# run under lcs existed before this at all ("ни один реальный прогон descriptors_head
# под lcs не существует"). C (--adversarial_grl) is deliberately NOT added:
# descriptors_head has no pre-cross-attention pooled representation for it to attack --
# training/read_configuration.py lists adversarial_grl in descriptors_head's
# unsupported set and raises ValueError if both are set. D (rankprot), E (tail
# tokens instead of hbond/heavy), F (protgeom8 instead of family-neutral 7) are
# separate single-variable siblings of this file (see
# descriptors_head_family_neutral_lipprop_lcs_rankprot.md / _tailtokens.md /
# _protgeom8.md), not combined here.

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
--balanced_lipid_classes
--lipid_coldsplit
