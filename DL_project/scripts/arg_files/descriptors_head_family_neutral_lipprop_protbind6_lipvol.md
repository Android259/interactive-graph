# descriptors_head_family_neutral_lipprop_protbind6.md (dcs) plus ONE name added to
# --descriptor_names: experimental_lipid_volume. Exact dcs counterpart of
# descriptors_head_family_neutral_lipprop_lcs_protbind6_lipvol.md -- same single
# name added, same reasoning for isolating it (see that file's header for why: the
# bundled _pocketchem4_lipcron4.md siblings move eight names at once and cannot say
# whether volume itself helps, hurts, or is neutral).
#
# Inherits its base file's leak-risk caveat unchanged: depth_q10/hydropathy_core/
# hydropathy_mean carry protein-family eta^2 0.55-0.77, and --double_coldsplit is
# the split where that axis is actually held out. experimental_lipid_volume itself
# is a LIPID-side name with no protein-family eta^2 exposure -- it is the six
# PROTEIN names inherited from the base file that carry the risk, not the one name
# this file adds. Still an opt-in leak probe overall, for the reason its base file
# states in full.
#
# Note for a LOCAL smoke run: experimental_lipid_volume is a data/Lipid_Volumes.xlsx
# lookup and openpyxl is not installed on this machine, so it only resolves from an
# existing data/pair_descriptor_cache_deterministic_*.json.
#
# Not yet run.

--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptors_head
--descriptor_names=chain,unsaturation,hbond,heavy,experimental_lipid_volume,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit
