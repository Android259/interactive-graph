# Gated sibling of deepclip_f1_normal_mean_cral_trio_warm_ep120.md (already run, 5
# seeds): every flag copied from it, --deepclip_protein_gate added with the same
# eleven descriptors and prerequisites as deepclip_gltp_protein_gate_ep120.md, plus
# --save_model. Same warm split (CRAL-TRIO's own 85/7.5/7.5), same sampler, same
# --negatives_per_positive=2 -- NOT the 5 the gate's subclass/species runs use, so
# that the one existing control is matched flag for flag.
#
# WHY THIS FAMILY
#
# Nine proteins, the most in any family, so memorising nine gate inputs is a larger
# ask than two. But the positives are lopsided: RLBP1 62, TTPAL 62, SEC14L6 14,
# TTPA 10, SEC14L2 9, SEC14L4 3, ATCAY 2, SEC14L5 2, BNIPL 1. The mirror triples will
# be dominated by the two big proteins; the per-protein AUC of the small ones rests
# on a handful of positives and should be read as such.
#
# HOW TO READ THE RESULT
#
# analysis/probes/deepclip_mirror_pairs.py. The no-gate control's mirror accuracy is 0.500 by
# construction, so its missing weights (that file has no --save_model) do not block
# the mirror comparison; they do block a per-protein AUC comparison on the same
# lipids, which would need that control rerun with --save_model.

--ep=120
--family_only=cral-trio
--deepclip
--lipid_smiles_tokens
--deepclip_filters=1
--deepclip_widths=4,5,6,7,8
--deepclip_lstm=10
--deepclip_lstm_dropout=0.1
--deepclip_conv_init=normal
--deepclip_readout=mean

--pair_descriptors
--deepclip_protein_gate=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,basic_share_core,basic_share_rim,hbond_donor_share_core,pocket_free_volume

--balanced_proteins
--balanced_batches
--negatives_per_positive=2

--save_model_in_dynamics
--save_model
