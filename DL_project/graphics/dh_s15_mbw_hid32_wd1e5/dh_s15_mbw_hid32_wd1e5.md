# dh_s15_mbw_hid32_wd1e5

## Summary (analysis/summarize_label.py)

```
Summary: 'dh_s15_mbw_hid32_wd1e5'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.4477      0.5991      0.4538      0.6234      0.7678      0.5082
ALL                 5      0.4477      0.5991      0.4538      0.6234      0.7678      0.5082

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6070      0.6184     0.0418  5
max valid BA                0.6380      0.6518     0.0334  5
best valid F1               0.3969      0.3938     0.0315  5
test BA                     0.5234      0.5412     0.0383  5
test AUC                    0.5846      0.6079     0.0740  5
test AUC in-protein         0.5845      0.5990     0.0887  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.5903      0.6280     0.0733  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.2658      0.2951     0.0686  5
test sensitivity            0.4477      0.3878     0.2310  5
test specificity            0.5991      0.6699     0.1859  5
test precision              0.1988      0.2066     0.0416  5
test loss                   0.6726      0.6765     0.0153  5
FPR (FP/(FP+TN))            0.4009      0.3301     0.1859  5
FNR (FN/(FN+TP))            0.5523      0.6122     0.2310  5

=== abs(sensitivity-specificity) gap: mean=0.3511 median=0.3478 n=5 ===
sensitivity std across seeds (by group): mean=0.2310 median=0.2310 n=1
specificity std across seeds (by group): mean=0.1859 median=0.1859 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6070      0.6184     0.0418  5
  max valid BA                0.6380      0.6518     0.0334  5
  best valid F1               0.3969      0.3938     0.0315  5
  test BA                     0.5234      0.5412     0.0383  5
  test AUC                    0.5846      0.6079     0.0740  5
  test AUC in-protein         0.5845      0.5990     0.0887  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.5903      0.6280     0.0733  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.2658      0.2951     0.0686  5
  test sensitivity            0.4477      0.3878     0.2310  5
  test specificity            0.5991      0.6699     0.1859  5
  test precision              0.1988      0.2066     0.0416  5
  test loss                   0.6726      0.6765     0.0153  5
  FPR (FP/(FP+TN))            0.4009      0.3301     0.1859  5
  FNR (FN/(FN+TP))            0.5523      0.6122     0.2310  5
```

## AUC vs chemistry null model, in-sample increment

Failed: ValueError: Unknown descriptor name(s): ['extent']. Known: lipid=('chain', 'unsaturation', 'hbond', 'heavy', 'tail_count', 'npr1', 'npr2', 'logp', 'tpsa', 'molar_refractivity', 'rotatable_bond_count', 'aromatic_ring_count', 'ring_count', 'tail_length_asymmetry', 'tail_length_mean', 'tail_double_bonds', 'tail_unsaturation_density', 'tail_double_bond_position', 'tail_logp', 'tail_molar_refractivity', 'tail_heavy_atoms', 'experimental_lipid_volume'), protein=('acidic_share_core', 'acidic_share_rim', 'apolar_sasa_share', 'aromatic_share', 'aromatic_share_coarse', 'aromatic_share_rim', 'basic_share_core', 'basic_share_rim', 'buriedness_q50', 'depth_q10', 'ev14_q10', 'ev14_q50', 'ev28_q10', 'hbond_acceptor_share_core', 'hbond_acceptor_share_rim', 'hbond_donor_share_core', 'hbond_donor_share_rim', 'hydropathy_core', 'hydropathy_mean', 'hydropathy_rim', 'pocket_elongation', 'pocket_elongation_lambda_sqrt', 'pocket_extent', 'pocket_extent_lambda_sqrt', 'pocket_flatness', 'pocket_flatness_lambda_sqrt', 'pocket_free_volume', 'pocket_packing_density', 'pocket_residue_share', 'pocket_sasa_share', 'pocket_volume_per_sasa', 'polar_share', 'polar_share_coarse', 'polar_share_core', 'polar_share_rim'), pair=('occupancy', 'chain_extent_gap', 'aromatic_contact', 'hbond_match', 'volume_fit', 'buriedness_match', 'depth_bulk_match', 'hydropathy_chain_match', 'aromatic_contact_min', 'hbond_match_min', 'tail_elongation_fit', 'hydropathy_rim_match', 'elongation_shape_match', 'flatness_shape_match') -- rerun for the full output: `python3 analysis/full_label_report.py --label dh_s15_mbw_hid32_wd1e5 --seeds=0,1,2,3,4`
