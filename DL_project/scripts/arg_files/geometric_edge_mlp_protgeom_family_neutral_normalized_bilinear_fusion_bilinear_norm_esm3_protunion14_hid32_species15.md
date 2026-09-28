# geometric_edge, both towers at width 32, on the CONCRETE-LIPID cold split.
#
# Sibling of geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_
# bilinear_norm_esm3_protunion14_hid32_rand.md: same architecture down to the line --
# --hiddim=32 on both encoder towers, the 14-descriptor protein union, --protein_edge_mlp,
# ESM3 embeddings, --bilinear_fusion/--bilinear_pooled_norm -- with the split swapped from
# --random_split to --lipid_species_coldsplit=0.15, plus the sampler set that split's own
# measurements call for (see below).
#
# What the split does. --lipid_species_coldsplit=<share> cuts the lipid axis at the
# CONCRETE STRUCTURE, not at a chemical class: dataloader/lipid_species_blocks.py builds
# connected components over canonicalised (SmileGlobal, SmileFragment) pairs and draws a
# seeded block of individual lipids carrying `share` of the table's positives. Every
# protein stays in training; the block is redrawn per seed on purpose, so two seeds hold
# out different lipids. It names its own pseudo-group, so the run lands under
# exclusion_set "groups_species15" (training/new_train.py's int(x*100 + 0.5) naming), one
# directory per seed rather than one per family. Mutually exclusive with every other
# holdout axis -- lipid_coldsplit/lipid_isolation/lipid_subclass/double_coldsplit/
# mixed_coldsplit/excluded_groups/excluded_subgroups (read_configuration.py validate()).
#
# Why THIS sampler set, and it is not the obvious one. files/lipid_species_coldsplit.md
# section 4 measured the four sampler modes on exactly these blocks (share 0.15, seeds
# 0-4) against the three free marginals -- protein, family, lipid class:
#   - --balanced_proteins is mandatory: the only mode that puts all three marginals on the
#     0.500 floor AND gives the largest pool (1612 train rows). It strictly dominates the
#     others rather than trading against them.
#   - --balanced_batches is mandatory and free: ClassBalancedBatchSampler reads only
#     train_labels, so it costs no pool volume at all.
#   - --balanced_lipid_classes is deliberately NOT set, even though the descriptors-side
#     siblings use it. On this axis it is strictly dominated: 89 fewer train rows AND the
#     protein marginal still alive at 0.607. It balances the wrong axis -- the cut is by
#     individual lipid, and the classes are represented on both sides of it.
#   - --negatives_per_positive=5 is the recommended volume point (2889 train rows, 0.186
#     positive share). Without one of the three balancing flags npp is silently ignored
#     (split_and_sample_interactions' hardcoded 0.056 branch), so it only means anything
#     alongside --balanced_proteins.
#
# What to measure against, and what NOT to read as a win. After --balanced_proteins the
# three simple marginals are already at the floor, so they are not the bar. The bar is the
# JOINT (protein x lipid class), which scores BA 0.828 on the block from the train-only
# label table alone -- no model, no protein structure, no chemistry -- and the chemical
# nearest neighbour at 0.739 (same file, section 5). A result under those is the label
# prior being replayed, not the architecture reading structure. The npp caveat from
# lipid_subclass_split_and_cron_features.md section 7.4 applies too: across npp values BA
# stays comparable but F1 does not, so only compare at a fixed npp.

--ep=120
--fast_attention

--hiddim=32

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim,ev28_q10,aromatic_share_rim,depth_q10,hydropathy_core,ev14_q10,hydropathy_mean,pocket_extent

--protein_edge_mlp

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--negatives_per_positive=5
--lipid_species_coldsplit=0.15
