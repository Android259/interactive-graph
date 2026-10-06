# One variable against geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_
# fusion_bilinear_norm_lcs_esm3 (test BA 0.5530, 4 lipid sets x 5 seeds):
# --balanced_lipid_classes added. First run of this flag in the project -- it appears in
# metrics_summary.csv exactly once, as a header.
#
# What it does (training/read_configuration.py:805-810, dataloader/sampler.py's
# split_and_sample_lipid_class_balanced_interactions): matches negatives to positives
# inside every (family, lipid class) cell, which removes the per-lipid-class positive
# rate prior from training -- measured there as 0.25-0.68 -> 0.50-0.51.
#
# Why under this split and not the others. --balanced_proteins, which every lcs run so
# far used, corrects the PROTEIN axis; under --lipid_coldsplit that axis is not held out
# and every protein is in train. The axis that IS held out is the lipid class, and a
# model that has learned "class X is mostly positive" has nothing to fall back on when a
# class it has never seen arrives -- it has to discriminate within the class instead,
# which is the thing being measured. This is the mirror of --balanced_proteins, aimed at
# the cold axis rather than the warm one.
#
# --balanced_proteins is deliberately left in place below: Dataloader.py:1416 tests
# balanced_lipid_classes FIRST in the if/elif chain, so the lipid-class sampler wins and
# the line is inert. Kept so this file stays a one-line diff from the baseline, and so
# the override is visible rather than implied by an absent flag. The trade is real and
# documented in the flag's own docstring: this sampler does NOT also balance per
# protein, and that is unavoidable on this data.

--ep=120
--fast_attention

--hiddim=8

--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm

--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim

--protein_edge_mlp

--save_model_in_dynamics

--balanced_batches
--balanced_proteins
--balanced_lipid_classes
--lipid_coldsplit
