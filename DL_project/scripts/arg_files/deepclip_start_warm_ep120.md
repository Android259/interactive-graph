# DeepCLIP on the START family's own rows -- the no-gate control for
# deepclip_start_protein_gate_ep120.md. Same role deepclip_gltp_warm_ep120.md plays
# for the GLTP pair; every flag is copied from it, only --family_only changes.
#
# WHY THIS FAMILY
#
# The GLTP capacity test has a hole it names itself: two proteins, so the gate sees
# two input vectors and can memorise them. START is the next step up
# (files/deepclip_gate_and_subclass_plan.md section 8, item 3): three proteins,
# 65 / 21 / 64 positives (STARD10 / STARD11 / STARD2), and mirror structure on three
# different axes (same file, section 3):
#
#   STARD2   PC 64/76   PE  0/24   PG  0/41   -- choline only
#   STARD10  PC 24/76   PE 20/24   PG 21/41   -- broad
#   STARD11  bare Cer 14/14, nothing else
#
# One START fold, three incompatible specificities. A protein-blind model has to emit
# one number per lipid and is wrong on at least one protein for every PE, PG and Cer.
#
# HOW TO READ THE RESULT
#
# Not by the pooled test number. Per protein and per mirror triple, with
# analysis/deepclip_mirror_pairs.py -- for this label the mirror accuracy is 0.500 by
# construction (the lipid alone decides the score), so what this run supplies is the
# per-protein AUC the gated sibling has to exceed on the same lipids.
#
# Still a capacity test: three gate inputs can be memorised as easily as two.
# Memorisation is only excluded by a protein the gate never trained on.

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

--balanced_proteins
--balanced_batches
--negatives_per_positive=2

--save_model_in_dynamics
--save_model
