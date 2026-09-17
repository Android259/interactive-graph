# DeepCLIP, CRAL-TRIO's own warm anchor for the lipid-isolation ladder.
#
# Differs from deepclip_f1_normal_mean_ep120.md the same way the five
# deepclip_f1_normal_mean_cral_trio_iso*_ep120.md siblings do -- --family_only=cral-trio
# (VALUED, fixes the run to this one family instead of expanding across all nine -- see
# any sibling's own header for why) and the sampler fix of
# files/deepclip_results_and_hard_negatives.md §4 -- but WITHOUT --lipid_isolation:
# CRAL-TRIO's own natural 85/7.5/7.5 random row split, the loader's default under
# --family_only alone.
#
# Why this needs its own file rather than reusing the existing CRAL-TRIO row of
# deepclip_f1_normal_mean_ep120.md's own 45-run grid: that run used the UNFIXED sampler
# (5.6% global negative subsample), so it is not on equal footing with the five
# lipid-isolation points above, which all use --balanced_proteins
# --negatives_per_positive=2 --balanced_batches. Comparing a fixed-sampler cold point
# against an unfixed-sampler warm one would confound the axis effect with the sampler
# effect -- exactly the trap files/split_similarity_vs_metric.md §4.2 documents for the
# named lipid sets. This file is the fixed-sampler counterpart at the warm end (no
# chemistry held out at all, isolation ~1.0 by construction), so the five points above
# and this one differ in exactly the axis, and nothing else.
#
# Cluster path only, same as its siblings; runs one job per seed, no --groups needed.
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

# Fix carried in from files/deepclip_results_and_hard_negatives.md §4: the base
# arm's dataloader sampler is untouched (5.6% global negative subsample), which on
# one family's own rows alone leaves 2-22 test rows and collapse_fraction
# 0.35-0.95 (measured on the same file's 45 completed runs). A --lipid_isolation
# block halves an already tiny excluded pool again, so without this fix the new
# points would be less readable than the ones already on the curve, not more.
--balanced_proteins
--balanced_batches
--negatives_per_positive=2
