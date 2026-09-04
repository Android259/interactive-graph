--ep=120

--hiddim=8

--dropout=0.1
--weight_decay=0.01

--thematical_paths
--geometric_descriptors=chain,tail_count,npr1,npr2,heavy,molar_refractivity,rotatable_bond_count,ring_count,pocket_extent,pocket_elongation,pocket_volume_per_sasa,pocket_flatness,buriedness_q50,depth_q10,pocket_sasa_share,pocket_residue_share,ev14_q50
--chemical_descriptors=unsaturation,aromatic_ring_count,hbond,tpsa,logp,aromatic_share,aromatic_share_rim,apolar_sasa_share,hydropathy_core,hydropathy_rim,ev28_q10
--thematical_orth_weight=0.05

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit
