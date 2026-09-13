# Adds six extra names to descriptors_head_family_neutral_lipprop_lcs.md's protein-
# side --descriptor_names -- the descriptors_head equivalent of the geometric_edge_
# ..._lcs_protbind6.md siblings this session added (same six names, same
# reasoning, see either of those files' own header for the full writeup):
#   - ev28_q10, aromatic_share_rim: already tested under dcs (geometric_edge, as
#     rim_ev28), not previously tried on this architecture.
#   - depth_q10, hydropathy_core: already in PROTEIN_DESCRIPTOR_NAMES, excluded from
#     family-neutral-7 by eta^2 (0.55/0.77) but the two best "real site signal"
#     candidates per files/pocket_shape_descriptors.md section 4's within-family check.
#   - ev14_q10, hydropathy_mean: new this session (dataloader/pair_descriptors.py).
# Single-variable sibling of the base file, same convention as its existing
# _rankprot/_tailtokens/_protgeom8 siblings -- base file's descriptor_names and every
# other flag left untouched.
#
# depth_q10/hydropathy_core/hydropathy_mean's eta^2 against protein family (0.55-0.77)
# is above the family-neutral floor -- descriptors_head has no --double_coldsplit
# variant of this file to begin with (--adversarial_grl, the mechanism that would need
# family-blind protein input most, is unsupported by --descriptors_head entirely, see
# the base file's own header), and --lipid_coldsplit does not hold out protein family
# at all (all 35 proteins stay in train), so that leak risk does not apply here either
# way.
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
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean

--save_model_in_dynamics

--balanced_batches
--balanced_lipid_classes
--lipid_coldsplit
