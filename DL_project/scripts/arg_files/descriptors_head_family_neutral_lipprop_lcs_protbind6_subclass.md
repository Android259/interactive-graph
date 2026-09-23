# Exact sibling of descriptors_head_family_neutral_lipprop_lcs_protbind6.md, ONE line
# changed: --lipid_coldsplit -> bare --lipid_subclass. Every --descriptor_names entry,
# every other flag, is copied verbatim -- see that file's own header for why those
# thirteen protein names and --lipid_propensity_weight are there.
#
# Same pairing as geometric_edge_mlp_..._protunion14_prothid32_subclass.md's own header
# explains in full -- read that file's header for the reasoning shared by both:
# --lipid_coldsplit's four sets are a hand-built partition of this project's own
# choosing; --lipid_subclass, bare, is the nine Titeca-et-al. subclass blocks
# (dataloader/lipid_subclass_blocks.py's FIG3_SUBCLASS_BLOCKS), the partition the task
# definition itself names ("classify binders and non-binders by lipid subclass"). This
# file is the descriptors_head half of that same pair, so the two answer the same
# question through the two fusion mechanisms the project already compares elsewhere
# (a token-level self-attention head here, --bilinear_fusion there).
#
# Block sizes, isolation, and the two already-unreadable blocks (PI, PS+PGP+DAG+TAG) --
# see the geometric_edge sibling's own header, identical table, not repeated here.
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
--save_model

--balanced_batches
--balanced_lipid_classes
--lipid_subclass
