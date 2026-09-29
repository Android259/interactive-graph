# dh_s15_mbw_lipprop

## Summary (analysis/summarize_label.py)

```
Summary: 'dh_s15_mbw_lipprop'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.5567      0.4896      0.4352      0.6021      0.6773      0.5527
ALL                 5      0.5567      0.4896      0.4352      0.6021      0.6773      0.5527

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5982      0.5957     0.0717  5
max valid BA                0.6150      0.6016     0.0597  5
best valid F1               0.3751      0.3740     0.0511  5
test BA                     0.5232      0.5414     0.0553  5
test AUC                    0.5152      0.5306     0.0617  5
test AUC in-protein         0.5109      0.5528     0.1283  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.5146      0.5325     0.0584  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.2971      0.2881     0.0300  5
test sensitivity            0.5567      0.5208     0.1432  5
test specificity            0.4896      0.4505     0.2149  5
test precision              0.2098      0.2096     0.0346  5
test loss                   0.6823      0.6912     0.0259  5
FPR (FP/(FP+TN))            0.5104      0.5495     0.2149  5
FNR (FN/(FN+TP))            0.4433      0.4792     0.1432  5

=== abs(sensitivity-specificity) gap: mean=0.2797 median=0.3459 n=5 ===
sensitivity std across seeds (by group): mean=0.1432 median=0.1432 n=1
specificity std across seeds (by group): mean=0.2149 median=0.2149 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5982      0.5957     0.0717  5
  max valid BA                0.6150      0.6016     0.0597  5
  best valid F1               0.3751      0.3740     0.0511  5
  test BA                     0.5232      0.5414     0.0553  5
  test AUC                    0.5152      0.5306     0.0617  5
  test AUC in-protein         0.5109      0.5528     0.1283  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.5146      0.5325     0.0584  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.2971      0.2881     0.0300  5
  test sensitivity            0.5567      0.5208     0.1432  5
  test specificity            0.4896      0.4505     0.2149  5
  test precision              0.2098      0.2096     0.0346  5
  test loss                   0.6823      0.6912     0.0259  5
  FPR (FP/(FP+TN))            0.5104      0.5495     0.2149  5
  FNR (FN/(FN+TP))            0.4433      0.4792     0.1432  5
```

## AUC vs chemistry null model, in-sample increment

Failed: ValueError: Unknown descriptor name(s): ['extent']. Known: lipid=('chain', 'unsaturation', 'hbond', 'heavy', 'tail_count', 'npr1', 'npr2', 'logp', 'tpsa', 'molar_refractivity', 'rotatable_bond_count', 'aromatic_ring_count', 'ring_count', 'tail_length_asymmetry', 'tail_length_mean', 'tail_double_bonds', 'tail_unsaturation_density', 'tail_double_bond_position', 'tail_logp', 'tail_molar_refractivity', 'tail_heavy_atoms', 'experimental_lipid_volume'), protein=('acidic_share_core', 'acidic_share_rim', 'apolar_sasa_share', 'aromatic_share', 'aromatic_share_coarse', 'aromatic_share_rim', 'basic_share_core', 'basic_share_rim', 'buriedness_q50', 'depth_q10', 'ev14_q10', 'ev14_q50', 'ev28_q10', 'hbond_acceptor_share_core', 'hbond_acceptor_share_rim', 'hbond_donor_share_core', 'hbond_donor_share_rim', 'hydropathy_core', 'hydropathy_mean', 'hydropathy_rim', 'pocket_elongation', 'pocket_elongation_lambda_sqrt', 'pocket_extent', 'pocket_extent_lambda_sqrt', 'pocket_flatness', 'pocket_flatness_lambda_sqrt', 'pocket_free_volume', 'pocket_packing_density', 'pocket_residue_share', 'pocket_sasa_share', 'pocket_volume_per_sasa', 'polar_share', 'polar_share_coarse', 'polar_share_core', 'polar_share_rim'), pair=('occupancy', 'chain_extent_gap', 'aromatic_contact', 'hbond_match', 'volume_fit', 'buriedness_match', 'depth_bulk_match', 'hydropathy_chain_match', 'aromatic_contact_min', 'hbond_match_min', 'tail_elongation_fit', 'hydropathy_rim_match', 'elongation_shape_match', 'flatness_shape_match') -- rerun for the full output: `python3 analysis/full_label_report.py --label dh_s15_mbw_lipprop --seeds=0,1,2,3,4`
