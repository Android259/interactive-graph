# dh_s15_mbw_hid32_heads4

## Summary (analysis/summarize_label.py)

```
Summary: 'dh_s15_mbw_hid32_heads4'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.4946      0.5967      0.3310      0.7219      0.5903      0.6817
ALL                 5      0.4946      0.5967      0.3310      0.7219      0.5903      0.6817

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5851      0.5861     0.0232  5
max valid BA                0.6360      0.6373     0.0346  5
best valid F1               0.3988      0.3842     0.0415  5
test BA                     0.5456      0.5494     0.0317  5
test AUC                    0.5867      0.6027     0.0412  5
test AUC in-protein         0.5956      0.6089     0.0675  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.5773      0.5705     0.0458  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.2846      0.2992     0.0703  5
test sensitivity            0.4946      0.4694     0.2678  5
test specificity            0.5967      0.5355     0.2302  5
test precision              0.2295      0.2228     0.0302  5
test loss                   0.6785      0.6764     0.0133  5
FPR (FP/(FP+TN))            0.4033      0.4645     0.2302  5
FNR (FN/(FN+TP))            0.5054      0.5306     0.2678  5

=== abs(sensitivity-specificity) gap: mean=0.3679 median=0.3071 n=5 ===
sensitivity std across seeds (by group): mean=0.2678 median=0.2678 n=1
specificity std across seeds (by group): mean=0.2302 median=0.2302 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5851      0.5861     0.0232  5
  max valid BA                0.6360      0.6373     0.0346  5
  best valid F1               0.3988      0.3842     0.0415  5
  test BA                     0.5456      0.5494     0.0317  5
  test AUC                    0.5867      0.6027     0.0412  5
  test AUC in-protein         0.5956      0.6089     0.0675  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.5773      0.5705     0.0458  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.2846      0.2992     0.0703  5
  test sensitivity            0.4946      0.4694     0.2678  5
  test specificity            0.5967      0.5355     0.2302  5
  test precision              0.2295      0.2228     0.0302  5
  test loss                   0.6785      0.6764     0.0133  5
  FPR (FP/(FP+TN))            0.4033      0.4645     0.2302  5
  FNR (FN/(FN+TP))            0.5054      0.5306     0.2678  5
```

## AUC vs chemistry null model, in-sample increment

Failed: ValueError: Unknown descriptor name(s): ['extent']. Known: lipid=('chain', 'unsaturation', 'hbond', 'heavy', 'tail_count', 'npr1', 'npr2', 'logp', 'tpsa', 'molar_refractivity', 'rotatable_bond_count', 'aromatic_ring_count', 'ring_count', 'tail_length_asymmetry', 'tail_length_mean', 'tail_double_bonds', 'tail_unsaturation_density', 'tail_double_bond_position', 'tail_logp', 'tail_molar_refractivity', 'tail_heavy_atoms', 'experimental_lipid_volume'), protein=('acidic_share_core', 'acidic_share_rim', 'apolar_sasa_share', 'aromatic_share', 'aromatic_share_coarse', 'aromatic_share_rim', 'basic_share_core', 'basic_share_rim', 'buriedness_q50', 'depth_q10', 'ev14_q10', 'ev14_q50', 'ev28_q10', 'hbond_acceptor_share_core', 'hbond_acceptor_share_rim', 'hbond_donor_share_core', 'hbond_donor_share_rim', 'hydropathy_core', 'hydropathy_mean', 'hydropathy_rim', 'pocket_elongation', 'pocket_elongation_lambda_sqrt', 'pocket_extent', 'pocket_extent_lambda_sqrt', 'pocket_flatness', 'pocket_flatness_lambda_sqrt', 'pocket_free_volume', 'pocket_packing_density', 'pocket_residue_share', 'pocket_sasa_share', 'pocket_volume_per_sasa', 'polar_share', 'polar_share_coarse', 'polar_share_core', 'polar_share_rim'), pair=('occupancy', 'chain_extent_gap', 'aromatic_contact', 'hbond_match', 'volume_fit', 'buriedness_match', 'depth_bulk_match', 'hydropathy_chain_match', 'aromatic_contact_min', 'hbond_match_min', 'tail_elongation_fit', 'hydropathy_rim_match', 'elongation_shape_match', 'flatness_shape_match') -- rerun for the full output: `python3 analysis/full_label_report.py --label dh_s15_mbw_hid32_heads4 --seeds=0,1,2,3,4`
