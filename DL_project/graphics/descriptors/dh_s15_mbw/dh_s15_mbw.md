# dh_s15_mbw

## Summary (analysis/summarize_label.py)

```
Summary: 'dh_s15_mbw'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.5150      0.4532      0.4312      0.5945      0.6105      0.5870
ALL                 5      0.5150      0.4532      0.4312      0.5945      0.6105      0.5870

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5522      0.5592     0.0423  5
max valid BA                0.5988      0.5877     0.0550  5
best valid F1               0.3645      0.3610     0.0567  5
test BA                     0.4841      0.4674     0.0305  5
test AUC                    0.4686      0.4214     0.0803  5
test AUC in-protein         0.5014      0.5638     0.1015  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.4594      0.4747     0.0924  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.2469      0.2768     0.0653  5
test sensitivity            0.5150      0.5918     0.2703  5
test specificity            0.4532      0.4498     0.3013  5
test precision              0.1869      0.1770     0.0284  5
test loss                   0.7058      0.7121     0.0209  5
FPR (FP/(FP+TN))            0.5468      0.5502     0.3013  5
FNR (FN/(FN+TP))            0.4850      0.4082     0.2703  5

=== abs(sensitivity-specificity) gap: mean=0.4197 median=0.3637 n=5 ===
sensitivity std across seeds (by group): mean=0.2703 median=0.2703 n=1
specificity std across seeds (by group): mean=0.3013 median=0.3013 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5522      0.5592     0.0423  5
  max valid BA                0.5988      0.5877     0.0550  5
  best valid F1               0.3645      0.3610     0.0567  5
  test BA                     0.4841      0.4674     0.0305  5
  test AUC                    0.4686      0.4214     0.0803  5
  test AUC in-protein         0.5014      0.5638     0.1015  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.4594      0.4747     0.0924  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.2469      0.2768     0.0653  5
  test sensitivity            0.5150      0.5918     0.2703  5
  test specificity            0.4532      0.4498     0.3013  5
  test precision              0.1869      0.1770     0.0284  5
  test loss                   0.7058      0.7121     0.0209  5
  FPR (FP/(FP+TN))            0.5468      0.5502     0.3013  5
  FNR (FN/(FN+TP))            0.4850      0.4082     0.2703  5
```

## AUC vs chemistry null model, in-sample increment

Failed: ValueError: Unknown descriptor name(s): ['extent']. Known: lipid=('chain', 'unsaturation', 'hbond', 'heavy', 'tail_count', 'npr1', 'npr2', 'logp', 'tpsa', 'molar_refractivity', 'rotatable_bond_count', 'aromatic_ring_count', 'ring_count', 'tail_length_asymmetry', 'tail_length_mean', 'tail_double_bonds', 'tail_unsaturation_density', 'tail_double_bond_position', 'tail_logp', 'tail_molar_refractivity', 'tail_heavy_atoms', 'experimental_lipid_volume'), protein=('acidic_share_core', 'acidic_share_rim', 'apolar_sasa_share', 'aromatic_share', 'aromatic_share_coarse', 'aromatic_share_rim', 'basic_share_core', 'basic_share_rim', 'buriedness_q50', 'depth_q10', 'ev14_q10', 'ev14_q50', 'ev28_q10', 'hbond_acceptor_share_core', 'hbond_acceptor_share_rim', 'hbond_donor_share_core', 'hbond_donor_share_rim', 'hydropathy_core', 'hydropathy_mean', 'hydropathy_rim', 'pocket_elongation', 'pocket_elongation_lambda_sqrt', 'pocket_extent', 'pocket_extent_lambda_sqrt', 'pocket_flatness', 'pocket_flatness_lambda_sqrt', 'pocket_free_volume', 'pocket_packing_density', 'pocket_residue_share', 'pocket_sasa_share', 'pocket_volume_per_sasa', 'polar_share', 'polar_share_coarse', 'polar_share_core', 'polar_share_rim'), pair=('occupancy', 'chain_extent_gap', 'aromatic_contact', 'hbond_match', 'volume_fit', 'buriedness_match', 'depth_bulk_match', 'hydropathy_chain_match', 'aromatic_contact_min', 'hbond_match_min', 'tail_elongation_fit', 'hydropathy_rim_match', 'elongation_shape_match', 'flatness_shape_match') -- rerun for the full output: `python3 analysis/full_label_report.py --label dh_s15_mbw --seeds=0,1,2,3,4`
