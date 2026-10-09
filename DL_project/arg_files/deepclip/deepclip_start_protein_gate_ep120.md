# Exact sibling of deepclip_start_warm_ep120.md, ONE mechanism added:
# --deepclip_protein_gate, with the same eleven descriptors and the same two
# prerequisite flags as deepclip_gltp_protein_gate_ep120.md (see that file's header
# for what the gate does and why these names). Every other flag is copied verbatim,
# so this and the GLTP gate differ only in --family_only.
#
# WHAT THIS ADDS OVER THE GLTP RUN
#
# Three proteins instead of two, and three kinds of disagreement instead of one:
# choline vs not (STARD2 vs STARD10 on PE/PG), breadth (STARD10 vs STARD2 on PC), and
# a bare ceramide only STARD11 takes. If the gate separates GLTP from GLTPD1 but not
# these, two-vector memorisation is the likelier reading of the GLTP result.
#
# HOW TO READ THE RESULT
#
# analysis/probes/deepclip_mirror_pairs.py, against deepclip_start_warm_ep120: mirror
# accuracy above 0.500 on train_pair is the capacity itself; the gate columns per
# protein show whether the gate moved at all.
#
# Chemistry is not held out, for the same reason as the GLTP run: this asks whether
# the gate CAN condition on the protein, not whether it generalises.

--ep=120
--family_only=start
--deepclip
--lipid_smiles_tokens
--deepclip_filters=1
--deepclip_widths=4,5,6,7,8
--deepclip_lstm=10
--deepclip_lstm_dropout=0.1
--deepclip_conv_init=normal
--deepclip_readout=mean

--descriptors
--deepclip_protein_gate=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,basic_share_core,basic_share_rim,hbond_donor_share_core,pocket_free_volume

--balanced_proteins
--balanced_batches
--negatives_per_positive=2

--save_model_in_dynamics
--save_model
