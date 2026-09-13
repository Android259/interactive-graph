# descriptors_head_family_neutral_lipprop_lcs.md + item E (files/reference_baselines_
# metrics_proposal.md section 3): replace hbond,heavy with the four tail tokens,
# keep chain,unsaturation. hbond/heavy are near-pure head-class fingerprints
# (eta^2=0.99/0.92 against head-group class, analysis/lipid_descriptor_class_identity.py,
# 283 species/34 classes) -- inert under double_coldsplit (lipid classes aren't held
# out there) but directly the kind of shortcut --lipid_coldsplit is built to deny,
# since it holds out named lipid sets. tail_length_mean/tail_double_bonds/
# tail_unsaturation_density/tail_length_asymmetry are the least class-specific tokens
# in the whole catalog (eta^2=0.31-0.34, dataloader/pair_descriptors.py:56-61).
# Operational support from geometric_edge_mlp under lcs: within-protein signal
# appeared exactly on the two held-out sets that differ mainly by acyl chain
# (choline, phosphorus_free), not on the two that differ mainly by head group
# (anionic, sphingolipids) -- lipid_coldsplit_architecture_direction.md section 7p.

--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptors_head
--descriptor_names=chain,unsaturation,tail_length_mean,tail_double_bonds,tail_unsaturation_density,tail_length_asymmetry,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim

--save_model_in_dynamics

--balanced_batches
--balanced_lipid_classes
--lipid_coldsplit
