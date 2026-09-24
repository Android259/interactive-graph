# Generalisation test for the protein gate, not a capacity test like the sibling
# deepclip_gltp_protein_gate_ep120.md. That file never holds any chemistry out, so a
# perfect score there is consistent with the gate simply memorising two input vectors
# (its own header says so). This file holds out one subclass of EACH protein's rule
# while keeping at least one sibling subclass of the SAME rule in training, so success
# requires the rule to transfer to an unseen subclass, not just a memorised lipid list.
#
# THE RULE, PER PROTEIN, FROM THE RAW TABLE (families/gltp only, all 62 positives):
#
#   GLTP    sugar-headed sphingolipids: HexCer 20/20, Hex2Cer 2/2, SHexCer 2/2 -- every
#           row of all three subclasses is a positive, none of anything else.
#   GLTPD1  phospho-headed sphingolipids: CerP 10/10, SM 17/17 (+PG 2/39) -- same shape,
#           the other headgroup.
#
# Both rules are 100% precision/recall on their subclasses and 0% elsewhere within the
# family -- as clean a mirror as the table has (see files/deepclip_gate_and_subclass_
# plan.md section 3.1).
#
# WHAT IS HELD OUT AND WHY THIS SPLIT AND NOT THE FULL SPHINGOLIPID BLOCK
#
# --lipid_subclass=CerP+Hex2Cer+SHexCer removes exactly the SMALLER subclass of each
# rule (GLTPD1 keeps SM=17 in training for phospho, GLTP keeps HexCer=20 in training for
# sugar, plus Hex2Cer's sibling SHexCer also moves to test so GLTP is tested on 2
# distinct unseen sugar subclasses, not 1). The full 6-way sphingolipid block
# (deepclip_gltp_protein_gate_ep120's sibling analysis, files/deepclip_gate_and_
# subclass_plan.md section 5) takes 51 of GLTP's 62 positives and leaves 11 to train on
# -- too little of the rule survives to learn from. This spec leaves 50 of 62 in
# training (GLTP: HexCer 20 + FA 3 + LPE 4 + LPG 1 + FAL 1 = 29; GLTPD1: SM 17 + PG 2 =
# 19 -- wait, PG 2/39 is nearly all-negative, not part of the rule, but stays with
# whichever split it lands in) and holds out 12 (GLTP: Hex2Cer 2 + SHexCer 2; GLTPD1:
# CerP 10).
#
# Every held-out row is one of the family's own mirror pairs (files/deepclip_gate_and_
# subclass_plan.md section 3): the SAME lipid species scored against both proteins,
# opposite label each time -- GLTP negative / GLTPD1 positive on CerP rows, GLTP
# positive / GLTPD1 negative on Hex2Cer+SHexCer rows. 24 within-family rows total
# (Hex2Cer 4 + SHexCer 4 + CerP 20 pre-split; wait -- per-protein breakdown below is the
# real count).
#
# --family_only=gltp combined with --lipid_subclass is not a new mechanism: the same
# combination is already used by deepclip_f1_normal_mean_cral_trio_subclass_pg_npp5_
# ep120.md (that file's header has the general argument for why block choice trades
# coldness against size). training/read_configuration.py's family_only guard only
# rejects excluded_groups/double_coldsplit/mixed_coldsplit/lipid_coldsplit/cold_split --
# lipid_subclass is deliberately not in that list.
#
# WHAT SUCCESS LOOKS LIKE
#
# Read per protein, not pooled (both proteins' rows share one balanced_accuracy
# otherwise). GLTP should score positive on held-out Hex2Cer/SHexCer, GLTPD1 positive on
# held-out CerP, each against the family's negatives -- despite neither having appeared
# under that protein during training. Chance-level or reversed sign on the held-out
# subclass, with the sibling capacity-test run still scoring near 1.0, would mean the
# gate memorises input vectors rather than reading pocket chemistry.
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
--negatives_per_positive=2
--lipid_subclass=CerP+Hex2Cer+SHexCer

--save_model_in_dynamics
--save_model
