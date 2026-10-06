--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--no_protein_embeddings

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim
--lipid_descriptors=chain,unsaturation,hbond,heavy,tail_count,npr1,npr2,logp,tpsa,molar_refractivity,rotatable_bond_count,aromatic_ring_count,ring_count

--protein_edge_mlp

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--double_coldsplit
