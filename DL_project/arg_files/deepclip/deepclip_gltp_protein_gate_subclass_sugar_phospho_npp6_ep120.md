# Exact sibling of deepclip_gltp_protein_gate_subclass_sugar_phospho_ep120.md, one line
# changed: --negatives_per_positive=2 -> 6. That run's 10-seed result collapsed toward
# "always positive" at several seeds (seed0: sensitivity 1.0, specificity 0.0) --
# consistent with training not seeing enough negative contrast for the held-out rule to
# calibrate a threshold against, since --balanced_proteins draws negatives to match each
# protein's OWN positive count and GLTP/GLTPD1 only have ~25-31 positives each.
#
# WHAT THIS CAN AND CANNOT FIX
#
# --negatives_per_positive only widens the TRAINING draw. It cannot widen the held-out
# block itself: --lipid_subclass=CerP+Hex2Cer+SHexCer's block is 14 positives against 14
# negatives family-wide (every candidate already in the source table, nothing left to
# draw further -- GLTP's 10 CerP rows are all negative already, GLTPD1's 4 Hex2Cer+
# SHexCer rows are all negative already). Raising npp cannot enlarge that pool; the
# sibling file's AUC_within_protein_pairs noise floor (14 pos/14 neg spread over 10
# seeds) is a data-size ceiling this flag does not touch. What it CAN do is give
# training itself a less positive-skewed diet, which is the plausible fix for the
# degenerate specificity=0 seeds specifically, as opposed to the underlying small-N
# noise in the metric itself.
#
# Family-wide train pool easily supports 6 (566 family rows total, ~50 train positives
# left after the block, several hundred negatives available -- nowhere near the PA/PG
# CRAL-TRIO blocks' tighter margins).
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

--pair_descriptors
--pocket_descriptors
--deepclip_protein_gate=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,basic_share_core,basic_share_rim,hbond_donor_share_core,pocket_free_volume

--balanced_proteins
--balanced_batches
--negatives_per_positive=6
--lipid_subclass=CerP+Hex2Cer+SHexCer

--save_model_in_dynamics
--save_model
