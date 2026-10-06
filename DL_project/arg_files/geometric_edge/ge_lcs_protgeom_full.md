--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion

--no_protein_embeddings

--protein_descriptors=pocket_residue_share,pocket_sasa_share,pocket_volume_per_sasa,pocket_extent,pocket_elongation,pocket_flatness,ev14_q50,buriedness_q50,depth_q10,apolar_sasa_share,aromatic_share,hydropathy_core,hydropathy_rim,ev28_q10,aromatic_share_rim

--protein_edge_mlp

--adversarial_grl
--no_adv_lipid

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--lipid_coldsplit
