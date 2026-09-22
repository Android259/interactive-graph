# descriptors_head_family_neutral_lipprop_lcs_protbind6.md with EIGHT names added to
# --descriptor_names and nothing else touched -- four on the protein side, four on the
# lipid side. Single-variable sibling of that file in the same sense its own
# _hid16/_lambdasqrt siblings are; everything not mentioned here is copied verbatim
# (see that file's header for the thirteen protein names it already carries).
#
# Protein side, added: basic_share_core, basic_share_rim, hbond_donor_share_core,
# pocket_free_volume.
# Lipid side, added: experimental_lipid_volume, tail_double_bonds, logp,
# tail_unsaturation_density. (unsaturation, the fifth member of the winning lipid set,
# is already in the base file.)
#
# WHY THESE EIGHT
#
# Both halves come from the same two Kron-RLS searches on the Figure-3 lipid-subclass
# split, ranked by AUC_within_protein:
#
#   cron_test_metrics/exhaustive_descriptor_search.csv (16064 combinations, BOTH sides
#   free). The lipid side of its winner -- and of all three runners-up behind it -- is
#   the identical five names. Presence across the leading rows (chance ~50%):
#     experimental_lipid_volume 100% of the top 50, 100% of the top 200
#     logp                       98 / 98
#     tail_unsaturation_density  96 / 97
#     unsaturation               66 / 60
#     tail_double_bonds          60 / 51
#     tail_double_bond_position  12 / 17   <- dropped
#
#   cron_test_metrics/exhaustive_protein_side_search.csv (16369 subsets, lipid side
#   pinned to those five). Winner 0.6888 AUC_within_protein against the incumbent
#   seven-descriptor set's 0.6681, that incumbent ranking 1106th of 16369. Presence:
#     basic_share_core          96% of the top 50, 93% of the top 100, 90% of top 500
#     pocket_free_volume        88 / 74 / 68
#     basic_share_rim           74 / 73 / 67
#     hbond_donor_share_core    56 / 57 / 52
#     hbond_acceptor_share_core / _rim, polar_share_core  at or below chance, dropped
#
# The four protein names are new to the NETWORK's catalog
# (dataloader/pair_descriptors.py's POCKET_CHEMISTRY_DESCRIPTOR_NAMES, computed by
# dataloader/protein_graph_builder.py's pocket_chemistry_descriptor and verified
# bit-identical to the Kron-RLS side's own values over all 35 proteins), so a set found
# by that search now means exactly the same thing in an arg file here. The four lipid
# names were already in LIPID_DESCRIPTOR_NAMES.
#
# WHY ADDING THEM IS NOT JUST A WIDER PROTEIN MARGINAL
#
# Under --lipid_coldsplit every protein stays in training, so "which protein is this"
# is free and extra protein-side capacity gets spent on it rather than on the pair
# (files/lipid_coldsplit_architecture_direction.md section 7j -- which is why this run
# is read by AUC_within_protein and not by pooled AUC/BA). What makes these eight
# different is that they arrive as MATCHED HALVES, and --descriptors_head is the head
# that can pair them: NamedDescriptorHead puts one token per name into a
# self-attention, so a protein token and a lipid token can combine directly, with no
# protein/lipid tower in between to launder the protein identity through.
#   pocket_free_volume x experimental_lipid_volume -- both angstrom^3. The first
#       protein-side quantity on the same physical scale as the lipid's own volume, and
#       the one quantitative relation Titeca et al. actually measure (cavity volume
#       against lipid volume). pocket_volume_per_sasa, already in the base file, is a
#       ratio and has no counterpart to be compared with.
#   basic_share_core / basic_share_rim x the head group -- Lys/Arg against an anionic
#       head is the recognition mechanism the literature names first, and five of the
#       nine Figure-3 blocks (PG, PA, PS, PI, PGP) are anionic. The core/rim split is
#       the source paper's own two-channel specificity: the mouth reads the head group,
#       the depth packs the chain.
#   hbond_donor_share_core x hbond -- donors pair with ACCEPTORS. `hbond` (already in
#       the base file) is an undirected capacity count, so this is a partial match, not
#       a clean one; the clean version needs a lipid-side acceptor/donor split that
#       does not exist yet.
#   tail_double_bonds / tail_unsaturation_density x hydropathy_core, depth_q10 -- the
#       chain half of the same two-channel story, against the descriptors of the depth.
# Deliberately NOT included: any new PAIR descriptor spelling those products out by
# formula. PAIR_DESCRIPTOR_NAMES has no volume-against-volume fit (volume_fit is
# pocket_volume_per_sasa x heavy) and no charge match at all; adding them is a separate
# change with its own file. This run measures what the head finds when both halves are
# merely present -- and is the directly comparable partner of
# geometric_edge_mlp_..._protunion14_prothid32_pocketchem4.md, which asks the same
# question of --bilinear_fusion instead of a token head.
#
# The family-eta^2 caveat from the base file's header carries over unchanged and is
# not made worse: basic/hbond shares are pocket-residue composition, not fold, and
# under --lipid_coldsplit protein family is not the held-out axis anyway.
#
# Note for a LOCAL smoke run: experimental_lipid_volume is a data/Lipid_Volumes.xlsx
# lookup and openpyxl is not installed on this machine, so it only resolves from an
# existing data/pair_descriptor_cache_deterministic_*.json. On the cluster, or after
# openpyxl is installed, it is computed normally.
#
# Not yet run.

--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--pair_descriptors
--descriptors_head
--descriptor_names=chain,unsaturation,hbond,heavy,experimental_lipid_volume,tail_double_bonds,logp,tail_unsaturation_density,pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,basic_share_core,basic_share_rim,hbond_donor_share_core,pocket_free_volume

--save_model_in_dynamics

--balanced_batches
--balanced_lipid_classes
--lipid_coldsplit
