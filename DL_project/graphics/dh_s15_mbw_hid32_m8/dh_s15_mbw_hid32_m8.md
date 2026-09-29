# dh_s15_mbw_hid32_m8

## Summary (analysis/summarize_label.py)

```
Summary: 'dh_s15_mbw_hid32_m8'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.6339      0.3929      0.5233      0.5276      0.6813      0.5671
ALL                 5      0.6339      0.3929      0.5233      0.5276      0.6813      0.5671

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5785      0.5560     0.0450  5
max valid BA                0.6242      0.6260     0.0284  5
best valid F1               0.3786      0.3905     0.0264  5
test BA                     0.5134      0.5409     0.0801  5
test AUC                    0.5286      0.5973     0.1071  5
test AUC in-protein         0.5380      0.5580     0.1341  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.5364      0.5631     0.1024  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.2811      0.3347     0.1016  5
test sensitivity            0.6339      0.7143     0.2818  5
test specificity            0.3929      0.4354     0.1791  5
test precision              0.1830      0.2081     0.0600  5
test loss                   0.7096      0.7102     0.0269  5
FPR (FP/(FP+TN))            0.6071      0.5646     0.1791  5
FNR (FN/(FN+TP))            0.3661      0.2857     0.2818  5

=== abs(sensitivity-specificity) gap: mean=0.4360 median=0.4875 n=5 ===
sensitivity std across seeds (by group): mean=0.2818 median=0.2818 n=1
specificity std across seeds (by group): mean=0.1791 median=0.1791 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5785      0.5560     0.0450  5
  max valid BA                0.6242      0.6260     0.0284  5
  best valid F1               0.3786      0.3905     0.0264  5
  test BA                     0.5134      0.5409     0.0801  5
  test AUC                    0.5286      0.5973     0.1071  5
  test AUC in-protein         0.5380      0.5580     0.1341  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.5364      0.5631     0.1024  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.2811      0.3347     0.1016  5
  test sensitivity            0.6339      0.7143     0.2818  5
  test specificity            0.3929      0.4354     0.1791  5
  test precision              0.1830      0.2081     0.0600  5
  test loss                   0.7096      0.7102     0.0269  5
  FPR (FP/(FP+TN))            0.6071      0.5646     0.1791  5
  FNR (FN/(FN+TP))            0.3661      0.2857     0.2818  5
```

## AUC vs chemistry null model, in-sample increment

Failed: ValueError: Unknown descriptor name(s): ['extent']. Known: lipid=('chain', 'unsaturation', 'hbond', 'heavy', 'tail_count', 'npr1', 'npr2', 'logp', 'tpsa', 'molar_refractivity', 'rotatable_bond_count', 'aromatic_ring_count', 'ring_count', 'tail_length_asymmetry', 'tail_length_mean', 'tail_double_bonds', 'tail_unsaturation_density', 'tail_double_bond_position', 'tail_logp', 'tail_molar_refractivity', 'tail_heavy_atoms', 'experimental_lipid_volume'), protein=('acidic_share_core', 'acidic_share_rim', 'apolar_sasa_share', 'aromatic_share', 'aromatic_share_coarse', 'aromatic_share_rim', 'basic_share_core', 'basic_share_rim', 'buriedness_q50', 'depth_q10', 'ev14_q10', 'ev14_q50', 'ev28_q10', 'hbond_acceptor_share_core', 'hbond_acceptor_share_rim', 'hbond_donor_share_core', 'hbond_donor_share_rim', 'hydropathy_core', 'hydropathy_mean', 'hydropathy_rim', 'pocket_elongation', 'pocket_elongation_lambda_sqrt', 'pocket_extent', 'pocket_extent_lambda_sqrt', 'pocket_flatness', 'pocket_flatness_lambda_sqrt', 'pocket_free_volume', 'pocket_packing_density', 'pocket_residue_share', 'pocket_sasa_share', 'pocket_volume_per_sasa', 'polar_share', 'polar_share_coarse', 'polar_share_core', 'polar_share_rim'), pair=('occupancy', 'chain_extent_gap', 'aromatic_contact', 'hbond_match', 'volume_fit', 'buriedness_match', 'depth_bulk_match', 'hydropathy_chain_match', 'aromatic_contact_min', 'hbond_match_min', 'tail_elongation_fit', 'hydropathy_rim_match', 'elongation_shape_match', 'flatness_shape_match') -- rerun for the full output: `python3 analysis/full_label_report.py --label dh_s15_mbw_hid32_m8 --seeds=0,1,2,3,4`
