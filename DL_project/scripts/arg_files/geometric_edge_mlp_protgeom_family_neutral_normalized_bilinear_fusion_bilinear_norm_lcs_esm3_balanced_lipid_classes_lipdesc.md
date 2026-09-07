# One variable against ..._lcs_esm3_balanced_lipid_classes: --lipid_descriptors added.
#
# The lipid side has never been given named descriptors on the main architecture -- a grep
# of metrics_summary.csv for molar_refractivity matches only thematical_paths_* labels,
# which is a separate sufficiency head with no protein/lipid tower at all. The protein
# side gets 7 descriptors in every one of these runs. That asymmetry is the wrong way
# round for a split that holds the LIPID axis out.
#
# WHICH five, and why not all 13. The eta^2 audit
# (files/lipid_coldsplit_architecture_direction.md section 7f/7h,
# analysis/lipid_descriptor_class_identity.py) found no descriptor neutral on every axis,
# but the axis that decides an actual run is the binary one -- a run holds out ONE set --
# and by max eta^2 over those four axes these five are the flattest available:
#
#   logp                  0.029   ring_count            0.043   tail_count            0.072
#   molar_refractivity    0.100   rotatable_bond_count  0.102
#
# against tpsa 0.325 and hbond 0.256, the two the audit flagged as essentially the class
# label (they retain 1.7% and 0.95% of their variance WITHIN a class). Note logp: eta^2
# 0.86 against the 34 fine head-group classes yet 0.029 against every set the split
# actually holds out -- selecting on the fine axis alone would have thrown it away.
#
# What this cannot do, stated so the result is not over-read: the audit's per-set table
# gives a DIFFERENT best set for each held-out set, and scripts/launch/submit_grid.sh runs
# a --lipid_coldsplit label over all four sets at once (--groups/--no_groups are rejected
# for exactly this axis). So this is one compromise set for all four, not the per-set
# choice section 7i asked for; that needs a --lipid_sets override in the launcher first.

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
--lipid_descriptors=logp,ring_count,tail_count,molar_refractivity,rotatable_bond_count
