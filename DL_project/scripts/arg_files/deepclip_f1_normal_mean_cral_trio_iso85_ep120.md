# DeepCLIP, lipid-isolation point within CRAL-TRIO (cral-trio__0.85). Fills in the Tanimoto-similarity-vs-metric curve
# (files/split_similarity_vs_metric.md) at the family-only end, where the axis is
# currently only two points wide: CRAL-TRIO's own natural --family_only split sits at
# isolation ~0.996 (every test row's lipid is essentially in training, since the split
# is a random row cut, not a chemistry cut), and there is nothing between it and 0.5.
#
# Differs from deepclip_f1_normal_mean_ep120.md, this session's pick as the best of the
# five deepclip arms (files/deepclip_results_and_hard_negatives.md §0; picked on point
# estimates only -- BA 0.654 and AUC 0.667 are the highest of the five on the seven
# measurable families, it wins 4/7 paired family comparisons against the published-arm
# reference, and it does so at the SAME 1960 parameters as that reference rather than by
# adding capacity like the f4/f8 arms. None of these differences are individually
# significant against the 0.10-0.22 per-cell seed spread the same report measures --
# this is a best point estimate, not a proven winner).
#
# --family_only=cral-trio, VALUED rather than the base file's bare marker: fixes the run
# to CRAL-TRIO instead of expanding across all nine groups (which would silently rerun
# --lipid_isolation=cral-trio__0.85 -- a species set chosen for CRAL-TRIO's own panel -- against
# every other family in turn). scripts/launch/submit_grid.sh reads a valued
# --family_only=<x> as "run exactly this family", so this label needs no --groups
# override at launch: it already runs one job per seed, not nine. Cluster path only --
# scripts/run_local.sh has no --family_only handling at all.
#
# --lipid_isolation=cral-trio__0.85 holds 21 lipid species out of training for CRAL-TRIO
# alone (dataloader/lipid_isolation_blocks.py, chosen by analysis/lipid_block_search.py
# --family cral-trio so that training on CRAL-TRIO's OWN remaining rows reaches
# isolation 0.850 -- the GLOBAL blocks calibrated against the whole table do not
# transfer to one family's own panel, measured to land anywhere from 0.52 to 0.96 for
# the same nominal key depending on the family, so this ladder is calibrated on
# CRAL-TRIO specifically and the key is not meant to be reused under a different
# --family_only value).
#
# Composition: phosphatidylethanolamine, 100%. the largest and cleanest block of the five -- exactly the phosphatidylethanolamines, and the biggest positive count in the ladder. Reconstructed at seeds 0-4 with this file's own
# sampler (34 positives on the full table): test block 24 rows, 17 positives at every seed. Isolation is
# measured directly on each reconstructed split, not read off the nominal key -- see the
# CSV analysis/split_similarity_vs_metric.py writes alongside its figure.
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
--lipid_isolation=cral-trio__0.85
