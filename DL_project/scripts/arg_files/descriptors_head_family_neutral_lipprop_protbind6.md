# descriptors_head_family_neutral_lipprop.md (dcs) plus the same six extra
# --descriptor_names names its _lcs_protbind6.md sibling adds: ev28_q10,
# aromatic_share_rim, depth_q10, hydropathy_core, ev14_q10, hydropathy_mean. No dcs
# variant of protbind6 existed before this file, in either architecture -- every
# existing protbind6 file (this one's own _lcs sibling, and every geometric_edge_mlp/
# geometric_edge_attention protbind6 file) is a _lcs_ file. This is the first one on
# --double_coldsplit.
#
# LEAK-RISK CAVEAT, READ BEFORE RUNNING
#
# The _lcs_protbind6.md header flags depth_q10/hydropathy_core/hydropathy_mean's
# eta^2 against PROTEIN FAMILY as 0.55-0.77 -- above the family-neutral floor the
# base seven descriptors were chosen to sit under -- and explicitly says the risk
# does not apply under --lipid_coldsplit because that split never holds protein
# family out (all 35 proteins stay in train either way). --double_coldsplit is the
# opposite case: protein family IS the held-out axis. So on THIS split, these three
# names (and ev28_q10/aromatic_share_rim/ev14_q10, whose family eta^2 has not been
# re-checked here) are exactly the kind of protein-side signal
# files/lipid_coldsplit_architecture_direction.md section 7j warns can let the model
# spend capacity on "which family is this" instead of the pair. This file is
# therefore an explicit, opt-in leak probe, not a vetted-safe default the way the
# base family-neutral-7 set is -- read its result against AUC_within_protein, and
# treat any BA/AUC gain over the plain dcs base with suspicion until checked against
# a family-blind control.
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
--balanced_proteins
--double_coldsplit
