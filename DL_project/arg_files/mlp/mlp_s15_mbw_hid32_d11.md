# mlp_s15_mbw_hid32, --descriptor_names: lcs-baseline set (11: 4 lipid + 7 protein) --
# the exact input files/results/descriptors_head_bottleneck.md §1 scored a plain MLP 64x64 on
# (test BA 0.853 there vs dh_s15_mbw_hid32_d11's NamedDescriptorHead at 0.535). Mirrors
# dh_s15_mbw_hid32_d11 with --descriptor_mlp -- the most direct re-check of that claim.
# План: files/history/descriptor_models.md

--ep=120
--fast_attention
--marginal_balance_weight

--hiddim=32

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--descriptors
--descriptor_mlp
--descriptor_names=chain,unsaturation,hbond,heavy,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim

--balanced_batches
--balanced_proteins
--lipid_species_coldsplit=0.15
