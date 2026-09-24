# DeepCLIP on the GLTP family's own rows -- the no-gate control for
# deepclip_gltp_protein_gate_ep120.md, and nothing else.
#
# WHY THIS FAMILY
#
# GLTP and GLTPD1 are the cleanest mirror pair in the whole table. Measured over
# data/lipid_article_classification.json's own subclasses:
#
#   subclass   GLTP     GLTPD1
#   HexCer     20/20     0/20
#   Hex2Cer     2/2      0/2
#   SHexCer     2/2      0/2
#   SM          0/17    17/17
#   CerP        0/10    10/10
#
# Same sphingoid backbone throughout, so the ONLY thing separating "binds" from
# "does not bind" is the head group -- a sugar for one protein, a phosphate or
# phosphocholine for the other -- and the two proteins want the opposite answer on
# the same chemistry. Published DeepCLIP has no protein input
# (architecture/deepclip.py's forward takes the lipid alone), so it must emit ONE
# number per lipid and is wrong on one of the two by construction. This file
# measures how wrong, and is what the gated sibling has to beat.
#
# The lipid side is not the bottleneck here, which is worth knowing before reading
# a bad number as a representation failure: analysis/deepclip_headgroup_probe.py
# separates HexCer from SM at 0.986 leave-one-out accuracy on these same 37 species
# with these exact published widths. The head group reaches the end of the branch
# intact; what is missing is anything to condition it on.
#
# HOW TO READ THE RESULT
#
# Per protein, not pooled. The pooled number over the family mixes the two halves of
# a mirror and can look reasonable while one protein is answered perfectly and the
# other inverted -- which is exactly what the sphingolipid block already showed on
# the two pocket-reading architectures.
#
# Sampler fix and --family_only convention carried from
# deepclip_f1_normal_mean_cral_trio_warm_ep120.md; see that file's header.
#
# Not yet run.

--ep=120
--family_only=gltp
--deepclip
--lipid_smiles_tokens
--deepclip_filters=1
--deepclip_widths=4,5,6,7,8
--deepclip_lstm=10
--deepclip_lstm_dropout=0.1
--deepclip_conv_init=normal
--deepclip_readout=mean

--balanced_proteins
--balanced_batches
--negatives_per_positive=2

--save_model_in_dynamics
--save_model
