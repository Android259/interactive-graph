# dh_s15_mbw_hid32_dpt0

## Summary (analysis/summarize_label.py)

```
Summary: 'dh_s15_mbw_hid32_dpt0'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.5623      0.5532      0.4935      0.5774      0.6730      0.5882
ALL                 5      0.5623      0.5532      0.4935      0.5774      0.6730      0.5882

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5910      0.5888     0.0516  5
max valid BA                0.6306      0.6447     0.0333  5
best valid F1               0.3837      0.3920     0.0319  5
test BA                     0.5578      0.5692     0.0417  5
test AUC                    0.5760      0.5955     0.0801  5
test AUC in-protein         0.5435      0.5796     0.0910  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.5815      0.5983     0.0872  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.2799      0.3427     0.1246  5
test sensitivity            0.5623      0.6458     0.4002  5
test specificity            0.5532      0.5446     0.3567  5
test precision              0.2233      0.2147     0.0646  5
test loss                   0.6958      0.6638     0.0906  5
FPR (FP/(FP+TN))            0.4468      0.4554     0.3567  5
FNR (FN/(FN+TP))            0.4377      0.3542     0.4002  5

=== abs(sensitivity-specificity) gap: mean=0.6068 median=0.5967 n=5 ===
sensitivity std across seeds (by group): mean=0.4002 median=0.4002 n=1
specificity std across seeds (by group): mean=0.3567 median=0.3567 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5910      0.5888     0.0516  5
  max valid BA                0.6306      0.6447     0.0333  5
  best valid F1               0.3837      0.3920     0.0319  5
  test BA                     0.5578      0.5692     0.0417  5
  test AUC                    0.5760      0.5955     0.0801  5
  test AUC in-protein         0.5435      0.5796     0.0910  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.5815      0.5983     0.0872  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.2799      0.3427     0.1246  5
  test sensitivity            0.5623      0.6458     0.4002  5
  test specificity            0.5532      0.5446     0.3567  5
  test precision              0.2233      0.2147     0.0646  5
  test loss                   0.6958      0.6638     0.0906  5
  FPR (FP/(FP+TN))            0.4468      0.4554     0.3567  5
  FNR (FN/(FN+TP))            0.4377      0.3542     0.4002  5
```

## AUC vs chemistry null model, in-sample increment

Failed: ValueError: Unknown descriptor name(s): ['extent']. Known: lipid=('chain', 'unsaturation', 'hbond', 'heavy', 'tail_count', 'npr1', 'npr2', 'logp', 'tpsa', 'molar_refractivity', 'rotatable_bond_count', 'aromatic_ring_count', 'ring_count', 'tail_length_asymmetry', 'tail_length_mean', 'tail_double_bonds', 'tail_unsaturation_density', 'tail_double_bond_position', 'tail_logp', 'tail_molar_refractivity', 'tail_heavy_atoms', 'experimental_lipid_volume'), protein=('acidic_share_core', 'acidic_share_rim', 'apolar_sasa_share', 'aromatic_share', 'aromatic_share_coarse', 'aromatic_share_rim', 'basic_share_core', 'basic_share_rim', 'buriedness_q50', 'depth_q10', 'ev14_q10', 'ev14_q50', 'ev28_q10', 'hbond_acceptor_share_core', 'hbond_acceptor_share_rim', 'hbond_donor_share_core', 'hbond_donor_share_rim', 'hydropathy_core', 'hydropathy_mean', 'hydropathy_rim', 'pocket_elongation', 'pocket_elongation_lambda_sqrt', 'pocket_extent', 'pocket_extent_lambda_sqrt', 'pocket_flatness', 'pocket_flatness_lambda_sqrt', 'pocket_free_volume', 'pocket_packing_density', 'pocket_residue_share', 'pocket_sasa_share', 'pocket_volume_per_sasa', 'polar_share', 'polar_share_coarse', 'polar_share_core', 'polar_share_rim'), pair=('occupancy', 'chain_extent_gap', 'aromatic_contact', 'hbond_match', 'volume_fit', 'buriedness_match', 'depth_bulk_match', 'hydropathy_chain_match', 'aromatic_contact_min', 'hbond_match_min', 'tail_elongation_fit', 'hydropathy_rim_match', 'elongation_shape_match', 'flatness_shape_match') -- rerun for the full output: `python3 analysis/full_label_report.py --label dh_s15_mbw_hid32_dpt0 --seeds=0,1,2,3,4`
