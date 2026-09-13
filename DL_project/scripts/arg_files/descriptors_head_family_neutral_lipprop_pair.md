# 2026-09-12: removed --zscore -- same bug as descriptors_pair_clean.md, same fix, same
# reason (training has no --zscore flag; it only exists on analysis/*.py null-model
# scripts). See files/geometric_edge_descriptors_baseline_selection_results.md section
# 1. Below unchanged otherwise: this label tests the full 21-feature combo (4 lipid + 7
# family-neutral protein + 10 pair) together.

--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptors_head
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,aromatic_contact,hbond_match,volume_fit,buriedness_match,aromatic_contact_min,hbond_match_min,tail_elongation_fit,hydropathy_rim_match,elongation_shape_match,flatness_shape_match

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit
