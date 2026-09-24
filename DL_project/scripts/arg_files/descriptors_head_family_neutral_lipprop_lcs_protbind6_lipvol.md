# descriptors_head_family_neutral_lipprop_lcs_protbind6.md plus ONE name added to
# --descriptor_names: experimental_lipid_volume. Everything else -- the base file's
# seventeen names, --lipid_propensity_weight, --balanced_lipid_classes, all of it --
# is copied verbatim. Same single-variable-sibling convention as that file's own
# _hid16/_lambdasqrt/_rotneg/_subclass siblings.
#
# WHY THIS FILE
#
# _pocketchem4_lipcron4.md (already run) adds EIGHT names at once -- four protein
# (basic_share_core, basic_share_rim, hbond_donor_share_core, pocket_free_volume) and
# four lipid (experimental_lipid_volume, tail_double_bonds, logp,
# tail_unsaturation_density) -- and came out WORSE than the plain protbind6 base on
# test BA/AUC/F1 (see files/lipid_subclass_split_and_cron_features.md and this
# session's own numbers: test BA 0.5539 -> 0.5258, test AUC 0.5705 -> 0.5216, test F1
# 0.4501 -> 0.4205). That result cannot say whether the volume descriptor itself hurt,
# helped and got outweighed by the other seven, or is neutral -- eight variables moved
# at once. This file isolates the one name the rest of this conversation has been
# about: experimental_lipid_volume alone, nothing else added.
#
# Nothing here needs pocket_free_volume as a partner to be meaningful on its own --
# unlike geometric_edge_mlp's --bilinear_fusion, which needs a commensurate protein
# channel for torch.nn.Bilinear to form a product, --descriptors_head puts one token
# per name into a shared self-attention, so a lone new lipid token can still attend to
# whatever protein tokens are already present (pocket_volume_per_sasa included) without
# a matched Angstrom^3 partner having to exist first.
#
# Note for a LOCAL smoke run: experimental_lipid_volume is a data/Lipid_Volumes.xlsx
# lookup and openpyxl is not installed on this machine, so it only resolves from an
# existing data/pair_descriptor_cache_deterministic_*.json -- same caveat as its
# _pocketchem4_lipcron4 sibling.
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
--balanced_lipid_classes
--lipid_coldsplit
