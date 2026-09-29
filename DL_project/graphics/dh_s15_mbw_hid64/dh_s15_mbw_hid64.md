# dh_s15_mbw_hid64

## Summary (analysis/summarize_label.py)

```
Summary: 'dh_s15_mbw_hid64'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.4273      0.6022      0.3962      0.6424      0.7227      0.5262
ALL                 5      0.4273      0.6022      0.3962      0.6424      0.7227      0.5262

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5539      0.5622     0.0520  5
max valid BA                0.6244      0.6103     0.0346  5
best valid F1               0.3816      0.3628     0.0283  5
test BA                     0.5148      0.5000     0.0499  5
test AUC                    0.5181      0.5015     0.0880  5
test AUC in-protein         0.5394      0.5708     0.0784  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.5118      0.5054     0.0945  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.1830      0.2396     0.1718  5
test sensitivity            0.4273      0.4694     0.4300  5
test specificity            0.6022      0.4795     0.3913  5
test precision              0.1962      0.2034     0.0324  3
test loss                   0.6922      0.6907     0.0284  5
FPR (FP/(FP+TN))            0.3978      0.5205     0.3913  5
FNR (FN/(FN+TP))            0.5727      0.5306     0.4300  5

=== abs(sensitivity-specificity) gap: mean=0.6251 median=0.8791 n=5 ===
sensitivity std across seeds (by group): mean=0.4300 median=0.4300 n=1
specificity std across seeds (by group): mean=0.3913 median=0.3913 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5539      0.5622     0.0520  5
  max valid BA                0.6244      0.6103     0.0346  5
  best valid F1               0.3816      0.3628     0.0283  5
  test BA                     0.5148      0.5000     0.0499  5
  test AUC                    0.5181      0.5015     0.0880  5
  test AUC in-protein         0.5394      0.5708     0.0784  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.5118      0.5054     0.0945  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.1830      0.2396     0.1718  5
  test sensitivity            0.4273      0.4694     0.4300  5
  test specificity            0.6022      0.4795     0.3913  5
  test precision              0.1962      0.2034     0.0324  3
  test loss                   0.6922      0.6907     0.0284  5
  FPR (FP/(FP+TN))            0.3978      0.5205     0.3913  5
  FNR (FN/(FN+TP))            0.5727      0.5306     0.4300  5
```

## AUC vs chemistry null model, in-sample increment

Failed: ValueError: Unknown descriptor name(s): ['extent']. Known: lipid=('chain', 'unsaturation', 'hbond', 'heavy', 'tail_count', 'npr1', 'npr2', 'logp', 'tpsa', 'molar_refractivity', 'rotatable_bond_count', 'aromatic_ring_count', 'ring_count', 'tail_length_asymmetry', 'tail_length_mean', 'tail_double_bonds', 'tail_unsaturation_density', 'tail_double_bond_position', 'tail_logp', 'tail_molar_refractivity', 'tail_heavy_atoms', 'experimental_lipid_volume'), protein=('acidic_share_core', 'acidic_share_rim', 'apolar_sasa_share', 'aromatic_share', 'aromatic_share_coarse', 'aromatic_share_rim', 'basic_share_core', 'basic_share_rim', 'buriedness_q50', 'depth_q10', 'ev14_q10', 'ev14_q50', 'ev28_q10', 'hbond_acceptor_share_core', 'hbond_acceptor_share_rim', 'hbond_donor_share_core', 'hbond_donor_share_rim', 'hydropathy_core', 'hydropathy_mean', 'hydropathy_rim', 'pocket_elongation', 'pocket_elongation_lambda_sqrt', 'pocket_extent', 'pocket_extent_lambda_sqrt', 'pocket_flatness', 'pocket_flatness_lambda_sqrt', 'pocket_free_volume', 'pocket_packing_density', 'pocket_residue_share', 'pocket_sasa_share', 'pocket_volume_per_sasa', 'polar_share', 'polar_share_coarse', 'polar_share_core', 'polar_share_rim'), pair=('occupancy', 'chain_extent_gap', 'aromatic_contact', 'hbond_match', 'volume_fit', 'buriedness_match', 'depth_bulk_match', 'hydropathy_chain_match', 'aromatic_contact_min', 'hbond_match_min', 'tail_elongation_fit', 'hydropathy_rim_match', 'elongation_shape_match', 'flatness_shape_match') -- rerun for the full output: `python3 analysis/full_label_report.py --label dh_s15_mbw_hid64 --seeds=0,1,2,3,4`
