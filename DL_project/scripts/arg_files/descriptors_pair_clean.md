# 2026-09-12: removed --zscore, which was here from the first version of this file and
# never trained -- every seed/family failed at config parsing with
# `ValueError: Unknown parameter: --zscore` (training/read_configuration.py). --zscore
# is a real flag, but only on analysis/*.py null-model scripts (null_model.py,
# full_label_report.py, pair_descriptor_family_eta2.py, etc.), which standardise the
# multiplicative pair descriptors before multiplying via dataloader.chemistry_prior.
# raw_feature_matrix/feature_similarity. Training's own pair-descriptor path
# (dataloader/pair_descriptors.py:pair_descriptor_value, used by --pair_descriptors)
# always multiplies raw, non-standardised values with no toggle -- there is no
# training-side equivalent to wire up. See files/geometric_edge_descriptors_baseline_
# selection_results.md section 1. Below unchanged otherwise: this label tests whether
# the 10 PAIR_DESCRIPTOR_NAMES columns alone (no separate lipid/protein columns) carry
# signal on their own.

--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptors_head
--descriptor_names=aromatic_contact,hbond_match,volume_fit,buriedness_match,aromatic_contact_min,hbond_match_min,tail_elongation_fit,hydropathy_rim_match,elongation_shape_match,flatness_shape_match

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit
