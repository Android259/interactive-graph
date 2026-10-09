# descriptors_head reading the WHOLE descriptor catalog, on the CONCRETE-LIPID cold split.
#
# Two changes from dh_family_neutral_pb6_lipprop_rand.md:
#   1. --descriptor_names goes from the 17 hand-picked names (the family-neutral 11 plus
#      the six protein-binding ones) to all 70 entries of dataloader/descriptors.py's
#      DESCRIPTOR_CATALOG.
#   2. the split goes from --random_split to --lipid_species_coldsplit=0.15, which brings
#      the sampler set that split's own measurements call for (see below).
# --descriptors/--descriptors_head, --lipid_propensity_weight, --hiddim=8, dropout,
# weight decay, pool type and epochs are copied over untouched.
#
# The 70 names are the catalog in its own order, which is also the three groups the ask
# names: 22 LIPID_DESCRIPTOR_NAMES, then "extent" (DescriptorHead's own train-fit-
# coarsened pocket_extent), then 20 PROTEIN_DESCRIPTOR_NAMES, then "polar_share", then 12
# POCKET_CHEMISTRY_DESCRIPTOR_NAMES, then 14 PAIR_DESCRIPTOR_NAMES. --descriptor_names
# accepts all of them: it names an arbitrary subset of DESCRIPTOR_CATALOG and builds one
# NamedDescriptorHead over exactly those tokens (read_configuration.py's descriptor_names
# docstring), so pair-side names -- which resolve_lipid_or_protein_side rejects -- are fine
# here, unlike on the protein-only --protein_descriptors path.
#
# What the split does. --lipid_species_coldsplit=<share> cuts the lipid axis at the
# CONCRETE STRUCTURE, not at a chemical class: dataloader/lipid_species_blocks.py builds
# connected components over canonicalised (SmileGlobal, SmileFragment) pairs and draws a
# seeded block of individual lipids carrying `share` of the table's positives. Every
# protein stays in training; the block is redrawn per seed on purpose. The run lands under
# exclusion_set "groups_species15", one directory per seed. Mutually exclusive with every
# other holdout axis (read_configuration.py validate()).
#
# NAME, not "family_neutral". The parent is called family_neutral because its 17 names were
# chosen to exclude the descriptors that fingerprint a protein family. This file
# deliberately drops that restriction, so carrying the word over would be a false label.
# Three things it now contains that the parent excluded on purpose:
#   - "extent" and "pocket_extent"/"pocket_residue_share"/"pocket_sasa_share": cavity-size
#     quantities. The descriptors path's family-fingerprint leak was measured on exactly
#     this family of columns (files/results/descriptors_baseline_leak_confirmed.md), so a good
#     number here is a leak candidate first and a result second.
#   - redundant re-parameterisations of the same quantity: pocket_extent /
#     pocket_elongation / pocket_flatness sit alongside their _lambda_sqrt twins, and
#     aromatic_contact / hbond_match alongside their _min twins. Four of the 70 tokens are
#     therefore near-duplicates of four others, which is what "all available" means but not
#     what an information-maximal set would look like.
#   - the 12 pocket-chemistry columns and experimental_lipid_volume, which elsewhere are
#     opt-in (the _pocketchem4 and _lipvol variants) rather than baseline.
#
# Why the sampler changed with the split, and why --balanced_lipid_classes is GONE.
# files/reference/lipid_species_coldsplit.md section 4 measured the four sampler modes on exactly
# these blocks (share 0.15, seeds 0-4) against the free marginals:
#   - --balanced_proteins is mandatory: the only mode that puts protein, family and lipid
#     class all on the 0.500 floor AND gives the largest pool. It strictly dominates.
#   - --balanced_batches is mandatory and free (reads only train_labels).
#   - --balanced_lipid_classes, which the parent DID set, is strictly dominated here: 89
#     fewer train rows AND the protein marginal still alive at 0.607. It balances the wrong
#     axis, because the cut is by individual lipid and the classes sit on both sides of it.
#     This is the one place this file knowingly breaks the "differ by one line" rule -- a
#     sampler that is measured to be dominated on the new axis is not worth preserving for
#     the sake of a cleaner diff.
#   - --negatives_per_positive=5 is the recommended volume point; without one of the
#     balancing flags npp is silently ignored (the hardcoded 0.056 branch).
#
# What to measure against. After --balanced_proteins the simple marginals are at the floor,
# so they are not the bar. The bar is the JOINT (protein x lipid class) at BA 0.828 from
# the train-only label table alone, and the chemical nearest neighbour at 0.739 (same file,
# section 5). Anything under those is the label prior replaying, not descriptors reading
# chemistry -- which is the specific risk for a 70-token set built to maximise coverage.

--ep=120
--fast_attention
--lipid_propensity_weight

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"

--descriptors
--descriptors_head
--descriptor_names=chain,unsaturation,hbond,heavy,tail_count,npr1,npr2,logp,tpsa,molar_refractivity,rotatable_bond_count,aromatic_ring_count,ring_count,tail_length_asymmetry,tail_length_mean,tail_double_bonds,tail_unsaturation_density,tail_double_bond_position,tail_logp,tail_molar_refractivity,tail_heavy_atoms,experimental_lipid_volume,extent,pocket_residue_share,pocket_sasa_share,pocket_volume_per_sasa,pocket_extent,pocket_elongation,pocket_flatness,ev14_q50,buriedness_q50,depth_q10,apolar_sasa_share,aromatic_share,hydropathy_core,hydropathy_rim,ev28_q10,aromatic_share_rim,hydropathy_mean,ev14_q10,pocket_extent_lambda_sqrt,pocket_elongation_lambda_sqrt,pocket_flatness_lambda_sqrt,polar_share,basic_share_core,basic_share_rim,acidic_share_core,acidic_share_rim,polar_share_core,polar_share_rim,hbond_donor_share_core,hbond_donor_share_rim,hbond_acceptor_share_core,hbond_acceptor_share_rim,pocket_free_volume,pocket_packing_density,occupancy,chain_extent_gap,aromatic_contact,hbond_match,volume_fit,buriedness_match,depth_bulk_match,hydropathy_chain_match,aromatic_contact_min,hbond_match_min,tail_elongation_fit,hydropathy_rim_match,elongation_shape_match,flatness_shape_match

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--negatives_per_positive=5
--lipid_species_coldsplit=0.15
