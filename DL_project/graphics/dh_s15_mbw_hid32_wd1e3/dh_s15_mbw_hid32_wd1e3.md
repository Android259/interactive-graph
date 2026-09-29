# dh_s15_mbw_hid32_wd1e3

## Summary (analysis/summarize_label.py)

```
Summary: 'dh_s15_mbw_hid32_wd1e3'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.4188      0.6778      0.4415      0.6474      0.7350      0.5480
ALL                 5      0.4188      0.6778      0.4415      0.6474      0.7350      0.5480

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6018      0.6054     0.0269  5
max valid BA                0.6415      0.6513     0.0195  5
best valid F1               0.3980      0.4000     0.0156  5
test BA                     0.5483      0.5728     0.0783  5
test AUC                    0.5955      0.6236     0.0924  5
test AUC in-protein         0.5780      0.6083     0.1251  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.5907      0.6329     0.0877  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.2905      0.3279     0.0961  5
test sensitivity            0.4188      0.4792     0.1779  5
test specificity            0.6778      0.6895     0.1477  5
test precision              0.2361      0.2222     0.0746  5
test loss                   0.6817      0.6728     0.0277  5
FPR (FP/(FP+TN))            0.3222      0.3105     0.1477  5
FNR (FN/(FN+TP))            0.5812      0.5208     0.1779  5

=== abs(sensitivity-specificity) gap: mean=0.3007 median=0.2138 n=5 ===
sensitivity std across seeds (by group): mean=0.1779 median=0.1779 n=1
specificity std across seeds (by group): mean=0.1477 median=0.1477 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6018      0.6054     0.0269  5
  max valid BA                0.6415      0.6513     0.0195  5
  best valid F1               0.3980      0.4000     0.0156  5
  test BA                     0.5483      0.5728     0.0783  5
  test AUC                    0.5955      0.6236     0.0924  5
  test AUC in-protein         0.5780      0.6083     0.1251  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.5907      0.6329     0.0877  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.2905      0.3279     0.0961  5
  test sensitivity            0.4188      0.4792     0.1779  5
  test specificity            0.6778      0.6895     0.1477  5
  test precision              0.2361      0.2222     0.0746  5
  test loss                   0.6817      0.6728     0.0277  5
  FPR (FP/(FP+TN))            0.3222      0.3105     0.1477  5
  FNR (FN/(FN+TP))            0.5812      0.5208     0.1779  5
```

## AUC vs chemistry null model, in-sample increment

Failed: ValueError: Unknown descriptor name(s): ['extent']. Known: lipid=('chain', 'unsaturation', 'hbond', 'heavy', 'tail_count', 'npr1', 'npr2', 'logp', 'tpsa', 'molar_refractivity', 'rotatable_bond_count', 'aromatic_ring_count', 'ring_count', 'tail_length_asymmetry', 'tail_length_mean', 'tail_double_bonds', 'tail_unsaturation_density', 'tail_double_bond_position', 'tail_logp', 'tail_molar_refractivity', 'tail_heavy_atoms', 'experimental_lipid_volume'), protein=('acidic_share_core', 'acidic_share_rim', 'apolar_sasa_share', 'aromatic_share', 'aromatic_share_coarse', 'aromatic_share_rim', 'basic_share_core', 'basic_share_rim', 'buriedness_q50', 'depth_q10', 'ev14_q10', 'ev14_q50', 'ev28_q10', 'hbond_acceptor_share_core', 'hbond_acceptor_share_rim', 'hbond_donor_share_core', 'hbond_donor_share_rim', 'hydropathy_core', 'hydropathy_mean', 'hydropathy_rim', 'pocket_elongation', 'pocket_elongation_lambda_sqrt', 'pocket_extent', 'pocket_extent_lambda_sqrt', 'pocket_flatness', 'pocket_flatness_lambda_sqrt', 'pocket_free_volume', 'pocket_packing_density', 'pocket_residue_share', 'pocket_sasa_share', 'pocket_volume_per_sasa', 'polar_share', 'polar_share_coarse', 'polar_share_core', 'polar_share_rim'), pair=('occupancy', 'chain_extent_gap', 'aromatic_contact', 'hbond_match', 'volume_fit', 'buriedness_match', 'depth_bulk_match', 'hydropathy_chain_match', 'aromatic_contact_min', 'hbond_match_min', 'tail_elongation_fit', 'hydropathy_rim_match', 'elongation_shape_match', 'flatness_shape_match') -- rerun for the full output: `python3 analysis/full_label_report.py --label dh_s15_mbw_hid32_wd1e3 --seeds=0,1,2,3,4`
