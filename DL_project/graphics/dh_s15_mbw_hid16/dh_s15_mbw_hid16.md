# dh_s15_mbw_hid16

## Summary (analysis/summarize_label.py)

```
Summary: 'dh_s15_mbw_hid16'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.2108      0.8068      0.4410      0.6176      0.5122      0.7067
ALL                 5      0.2108      0.8068      0.4410      0.6176      0.5122      0.7067

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5540      0.5521     0.0108  5
max valid BA                0.6094      0.6122     0.0385  5
best valid F1               0.3632      0.3636     0.0406  5
test BA                     0.5088      0.5078     0.0188  5
test AUC                    0.5138      0.5090     0.0509  5
test AUC in-protein         0.5852      0.6004     0.0516  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.5472      0.5238     0.0654  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.1903      0.2238     0.0640  5
test sensitivity            0.2108      0.2292     0.1242  5
test specificity            0.8068      0.8366     0.1384  5
test precision              0.2195      0.1975     0.0589  5
test loss                   0.6765      0.6792     0.0125  5
FPR (FP/(FP+TN))            0.1932      0.1634     0.1384  5
FNR (FN/(FN+TP))            0.7892      0.7708     0.1242  5

=== abs(sensitivity-specificity) gap: mean=0.5960 median=0.6075 n=5 ===
sensitivity std across seeds (by group): mean=0.1242 median=0.1242 n=1
specificity std across seeds (by group): mean=0.1384 median=0.1384 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5540      0.5521     0.0108  5
  max valid BA                0.6094      0.6122     0.0385  5
  best valid F1               0.3632      0.3636     0.0406  5
  test BA                     0.5088      0.5078     0.0188  5
  test AUC                    0.5138      0.5090     0.0509  5
  test AUC in-protein         0.5852      0.6004     0.0516  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.5472      0.5238     0.0654  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.1903      0.2238     0.0640  5
  test sensitivity            0.2108      0.2292     0.1242  5
  test specificity            0.8068      0.8366     0.1384  5
  test precision              0.2195      0.1975     0.0589  5
  test loss                   0.6765      0.6792     0.0125  5
  FPR (FP/(FP+TN))            0.1932      0.1634     0.1384  5
  FNR (FN/(FN+TP))            0.7892      0.7708     0.1242  5
```

## AUC vs chemistry null model, in-sample increment

Failed: ValueError: Unknown descriptor name(s): ['extent']. Known: lipid=('chain', 'unsaturation', 'hbond', 'heavy', 'tail_count', 'npr1', 'npr2', 'logp', 'tpsa', 'molar_refractivity', 'rotatable_bond_count', 'aromatic_ring_count', 'ring_count', 'tail_length_asymmetry', 'tail_length_mean', 'tail_double_bonds', 'tail_unsaturation_density', 'tail_double_bond_position', 'tail_logp', 'tail_molar_refractivity', 'tail_heavy_atoms', 'experimental_lipid_volume'), protein=('acidic_share_core', 'acidic_share_rim', 'apolar_sasa_share', 'aromatic_share', 'aromatic_share_coarse', 'aromatic_share_rim', 'basic_share_core', 'basic_share_rim', 'buriedness_q50', 'depth_q10', 'ev14_q10', 'ev14_q50', 'ev28_q10', 'hbond_acceptor_share_core', 'hbond_acceptor_share_rim', 'hbond_donor_share_core', 'hbond_donor_share_rim', 'hydropathy_core', 'hydropathy_mean', 'hydropathy_rim', 'pocket_elongation', 'pocket_elongation_lambda_sqrt', 'pocket_extent', 'pocket_extent_lambda_sqrt', 'pocket_flatness', 'pocket_flatness_lambda_sqrt', 'pocket_free_volume', 'pocket_packing_density', 'pocket_residue_share', 'pocket_sasa_share', 'pocket_volume_per_sasa', 'polar_share', 'polar_share_coarse', 'polar_share_core', 'polar_share_rim'), pair=('occupancy', 'chain_extent_gap', 'aromatic_contact', 'hbond_match', 'volume_fit', 'buriedness_match', 'depth_bulk_match', 'hydropathy_chain_match', 'aromatic_contact_min', 'hbond_match_min', 'tail_elongation_fit', 'hydropathy_rim_match', 'elongation_shape_match', 'flatness_shape_match') -- rerun for the full output: `python3 analysis/full_label_report.py --label dh_s15_mbw_hid16 --seeds=0,1,2,3,4`
