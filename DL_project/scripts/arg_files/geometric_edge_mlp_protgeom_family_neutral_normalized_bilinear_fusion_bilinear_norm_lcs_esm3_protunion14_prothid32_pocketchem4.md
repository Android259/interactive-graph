# geometric_edge_mlp_..._lcs_esm3_protunion14_prothid32.md with FOUR names added to
# --protein_descriptors and nothing else touched. Single-variable sibling of that file;
# everything it does not mention is copied from it verbatim (see its own header, and
# the base protunion14.md's, for the rest of the reasoning).
#
# The four: basic_share_core, basic_share_rim, hbond_donor_share_core,
# pocket_free_volume. They are new to the NETWORK's descriptor catalog
# (dataloader/pair_descriptors.py's POCKET_CHEMISTRY_DESCRIPTOR_NAMES; values computed
# by dataloader/protein_graph_builder.py's pocket_chemistry_descriptor, bit-identical
# to training/pair_baseline_common.py's own POCKET_CHEMISTRY_NAMES/POCKET_CAVITY_NAMES
# -- verified over all 35 proteins) but not to the project: the Kron-RLS side got them
# first and searched them exhaustively.
#
# WHY THESE FOUR AND NOT THE OTHER EIGHT
#
# cron_test_metrics/exhaustive_protein_side_search.csv, 16369 subsets, ranked by
# AUC_within_protein on the Figure-3 lipid-subclass split with the lipid side fixed.
# The incumbent seven-descriptor set the search was asked to defend scores 0.6681 and
# ranks 1106th of 16369; the winner scores 0.6888 with
#   ev14_q50, apolar_sasa_share, pocket_elongation_lambda_sqrt, hydropathy_mean,
#   pocket_free_volume, basic_share_core
# Presence in the leading rows (a subset drawn at random contains any given name ~50%
# of the time, so 50% is the chance line):
#   basic_share_core         96% of the top 50, 93% of the top 100, 90% of the top 500
#   pocket_free_volume       88 / 74 / 68
#   basic_share_rim          74 / 73 / 67
#   hbond_donor_share_core   56 / 57 / 52
#   hbond_acceptor_share_core 46 / 45 / 52   <- chance
#   hbond_acceptor_share_rim  34 / 37 / 49   <- chance
#   polar_share_core          28 / 37 / 39   <- below chance
# Only the first four are enriched at every depth, so only those four are added here.
# (pocket_packing_density was the single best ADDITION to the incumbent seven in the
# pre-screen -- 0.6754 against the incumbent's own 0.6681 -- but ranked last of twelve
# standalone and was cut before the exhaustive stage, so it has never been measured in
# a real combination. It is nameable now; it is deliberately not in this file.)
#
# WHY THESE FOUR AND NOT SIMPLY MORE POCKET DESCRIPTORS
#
# Under --lipid_coldsplit every protein stays in training, so protein identity is free
# and the model will happily spend new protein-side capacity on the protein marginal
# rather than on the pair (files/lipid_coldsplit_architecture_direction.md section 7j,
# and the reason AUC_within_protein and not pooled AUC is what this run is read by).
# Adding descriptors to a CONCATENATION cannot fix that by itself. What separates these
# four from the fourteen already here is that each one has a commensurate partner on
# the lipid side, so there is an actual product for --bilinear_fusion's
# torch.nn.Bilinear -- which multiplies every pooled lipid channel against every pooled
# protein channel -- to find:
#   basic_share_core/_rim x head-group charge      Lys/Arg against an anionic head is
#       the mechanism the head-group-recognition literature names first, and five of
#       the nine Figure-3 blocks (PG, PA, PS, PI, PGP) are anionic. core/rim is the
#       source paper's own two-channel specificity: the mouth reads the head group,
#       the depth packs the chain.
#   hbond_donor_share_core x lipid H-bond capacity  donors pair with ACCEPTORS; the
#       existing hbond_match token multiplies undirected counts and cannot express it.
#   pocket_free_volume x experimental_lipid_volume  both in angstrom^3 -- the first
#       protein-side quantity on the same physical scale as the lipid's own volume, and
#       the one quantitative relation Titeca et al. actually measure. The older
#       pocket_volume_per_sasa is a ratio and has no such partner.
# This file gives the network the PROTEIN HALF of each of those pairs and deliberately
# stops there: the lipid half is not added, and no explicit pair descriptor is either
# (there is none in PAIR_DESCRIPTOR_NAMES yet -- volume_fit is pocket_volume_per_sasa x
# heavy, not a volume-against-volume fit -- and writing one is a separate change with
# its own file). So the one thing this run measures is what the four new protein
# descriptors buy on their own, with the lipid branch exactly as the baseline left it.
#
# It is the FIRST of three, and only the three together separate the two effects:
#   this file                    protein half only          new protein chemistry alone
#   ..._pocketchem4_lipcron4.md  + --lipid_descriptors      both halves, bilinear fusion
#   descriptors_head_..._pocketchem4_lipcron4.md            both halves, token head
# This file against the second isolates whether supplying the commensurate lipid half
# (experimental_lipid_volume against pocket_free_volume, in the same angstrom^3) is what
# lets torch.nn.Bilinear form the product at all, or whether the protein descriptors
# carry their gain without it. The second against the third holds the eight names fixed
# and swaps only the fusion mechanism.
#
# Note for a LOCAL smoke run: the lipid side here is untouched, so nothing in this file
# needs data/Lipid_Volumes.xlsx. Its descriptors_head sibling does (it adds
# experimental_lipid_volume), and openpyxl is not installed on this machine -- that one
# only resolves from data/pair_descriptor_cache_deterministic_*.json.
#
# Not yet run.

--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent,basic_share_core,basic_share_rim,hbond_donor_share_core,pocket_free_volume

--protein_edge_mlp
--protein_hiddim=32

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--lipid_coldsplit
