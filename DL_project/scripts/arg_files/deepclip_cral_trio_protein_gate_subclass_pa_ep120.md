# CRAL-TRIO analogue of deepclip_gltp_protein_gate_subclass_sugar_phospho_ep120.md:
# same mechanism (--deepclip_protein_gate, same 11 descriptors, unchanged so the two
# families are directly comparable), same idea (hold out one subclass of a shared rule,
# keep sibling subclasses of the SAME rule in training), but on a family the GLTP test
# could not read cleanly -- that run's 10-seed result (files/deepclip_gate_and_subclass_
# plan.md's running log) came back at AUC_within_protein_pairs 0.458 +/- 0.261: no
# signal distinguishable from noise, because the held-out block was only 14 positives /
# 14 negatives on a 2-protein family. This file trades the clean mirror-pair framing for
# statistical power: 9 proteins, and the shared rule is carried by TWO of them at once.
#
# THE RULE: RLBP1 and TTPAL both bind anionic/zwitterionic phospholipids broadly across
# FOUR subclasses (counts, family-wide, from the raw table):
#
#           CL   PA   PE   PG
#   RLBP1   10    8   18   20
#   TTPAL    4    6   20   25
#
# The other seven CRAL-TRIO proteins are essentially silent on all four (ATCAY/BNIPL/
# SEC14L2/L4/L5/L6/TTPA hold at most a couple of PA/PG positives between them -- see
# deepclip_gltp_protein_gate_subclass_sugar_phospho_ep120.md's sibling breakdown script
# for the full table), so they supply the negative contrast the rule needs without
# carrying it themselves.
#
# --lipid_subclass=PA holds out the smallest of the four (RLBP1 8 + TTPAL 6 = 14 shared-
# rule positives) while CL+PE+PG stay in training (10+18+20 + 4+20+25 = 97 positives
# carrying the same rule, on the same two proteins). Family-wide: 149 positives left in
# training, 16 held out (RLBP1/TTPAL's 14 plus incidental others). Contrast the GLTP
# file's 50 left / 12-14 held -- both axes of the earlier run's weakness are fixed here.
#
# --negatives_per_positive=5, exactly deepclip_f1_normal_mean_cral_trio_subclass_pg_
# npp5_ep120.md's choice and for the same reason: the PA block carries 83 negatives
# family-wide, and 5x the block's 16 positives (80) is inside that without exhausting
# it. --lipid_subclass=PG was the file this project already validated at this family and
# this ratio; PA is the fourth-largest of the four shared subclasses and the one that
# leaves the most of the rule (149 of 165 family positives) in training.
#
# WHAT SUCCESS LOOKS LIKE
#
# Read per protein (RLBP1, TTPAL) rather than pooled -- the other seven proteins should
# stay negative on held-out PA the same way they were negative on CL/PE/PG in training,
# which is the easy part. The real question is whether RLBP1's and TTPAL's held-out PA
# rows score positive despite neither protein having seen that subclass during
# training. AUC_within_protein (not _pairs -- there is no mirror pair here, both
# proteins agree) is the metric that answers it.
#
# Not yet run.

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
--pocket_descriptors
--deepclip_protein_gate=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,basic_share_core,basic_share_rim,hbond_donor_share_core,pocket_free_volume

--balanced_proteins
--balanced_batches
--negatives_per_positive=5
--lipid_subclass=PA

--save_model_in_dynamics
--save_model
