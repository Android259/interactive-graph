# One variable against ..._lcs_esm3_balanced_lipid_classes (test BA 0.6155, the new
# lipid-cold-split baseline, files/lipid_coldsplit_architecture_direction.md section 7i):
# --lipid_hiddim, nothing else.
#
# The last untested capacity knob, and the only one that reaches the branch this split
# actually holds out. Everything a never-seen head-group class can express passes through
# ONE torch.nn.Linear(768, hiddim) over a MolFormer embedding
# (architecture/lipid_encoder.py); at hiddim=8 that is the whole of it.
#
# Why it is not "--hiddim again". Raising --hiddim 8 -> 64 raised BOTH branches and bought
# only memorisation: test BA 0.5530 -> 0.5511 while train sensitivity went 0.837 -> 0.897
# (section 3). The protein side is fully in-distribution here -- every protein is in
# training -- so width given to it can go straight into memorising, and did.
# --lipid_hiddim gives width to the cold branch alone; the protein tower is untouched and
# builds no adapter (section 7c).
#
# 32 and 64 are run as a pair so a flat result is a flat SLOPE, not one point that could
# have missed the useful width either side.

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
--lipid_hiddim=32
