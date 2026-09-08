# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protgeom8

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protgeom8'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.4946      0.6291      0.9210      0.8556      0.5871      0.6185
groups_choline            5      0.3640      0.8084      0.9163      0.7170      0.4250      0.8012
groups_phosphorus_free    5      0.3290      0.8386      0.8300      0.6625      0.3800      0.8929
groups_sphingolipids      5      0.3273      0.6291      0.5461      0.6188      0.5333      0.5815
ALL                      20      0.3787      0.7263      0.8034      0.7135      0.4814      0.7235

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5789      0.5780     0.0475  20
max valid BA                0.6024      0.5921     0.0583  20
best valid F1               0.5196      0.5607     0.1142  20
test BA                     0.5525      0.5588     0.0749  20
test F1                     0.3808      0.4034     0.1684  20
test sensitivity            0.3787      0.3817     0.2109  20
test specificity            0.7263      0.7292     0.2076  20
test precision              0.4893      0.4701     0.1088  18
test loss                   0.8914      0.8054     0.2658  20
FPR (FP/(FP+TN))            0.2737      0.2708     0.2076  20
FNR (FN/(FN+TP))            0.6213      0.6183     0.2109  20

=== abs(sensitivity-specificity) gap: mean=0.4057 median=0.3713 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5738      0.5801     0.0155  5
  max valid BA                0.6028      0.6040     0.0167  5
  best valid F1               0.5600      0.5620     0.0135  5
  test BA                     0.5619      0.5631     0.0115  5
  test F1                     0.4696      0.4583     0.0333  5
  test sensitivity            0.4946      0.4731     0.0772  5
  test specificity            0.6291      0.6358     0.0661  5
  test precision              0.4519      0.4444     0.0146  5
  test loss                   1.2197      1.1789     0.2452  5
  FPR (FP/(FP+TN))            0.3709      0.3642     0.0661  5
  FNR (FN/(FN+TP))            0.5054      0.5269     0.0772  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5911      0.5967     0.0415  5
  max valid BA                0.6131      0.5967     0.0453  5
  best valid F1               0.5705      0.5714     0.0468  5
  test BA                     0.5862      0.5872     0.0390  5
  test F1                     0.4302      0.4022     0.0835  5
  test sensitivity            0.3640      0.3243     0.1417  5
  test specificity            0.8084      0.8084     0.1111  5
  test precision              0.5815      0.5484     0.1046  5
  test loss                   0.8452      0.7986     0.1932  5
  FPR (FP/(FP+TN))            0.1916      0.1916     0.1111  5
  FNR (FN/(FN+TP))            0.6360      0.6757     0.1417  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6079      0.5810     0.0653  5
  max valid BA                0.6364      0.5988     0.0887  5
  best valid F1               0.4450      0.3590     0.1916  5
  test BA                     0.5838      0.5382     0.0923  5
  test F1                     0.3665      0.2800     0.1878  5
  test sensitivity            0.3290      0.2258     0.2635  5
  test specificity            0.8386      0.8421     0.0980  5
  test precision              0.5150      0.5500     0.0881  5
  test loss                   0.7858      0.6912     0.2112  5
  FPR (FP/(FP+TN))            0.1614      0.1579     0.0980  5
  FNR (FN/(FN+TP))            0.6710      0.7742     0.2635  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5429      0.5589     0.0400  5
  max valid BA                0.5574      0.5589     0.0430  5
  best valid F1               0.5031      0.5500     0.1012  5
  test BA                     0.4782      0.5000     0.0824  5
  test F1                     0.2567      0.3529     0.2427  5
  test sensitivity            0.3273      0.4545     0.3041  5
  test specificity            0.6291      0.5818     0.3615  5
  test precision              0.3550      0.3115     0.0960  3
  test loss                   0.7148      0.7026     0.0562  5
  FPR (FP/(FP+TN))            0.3709      0.4182     0.3615  5
  FNR (FN/(FN+TP))            0.6727      0.5455     0.3041  5
```

## AUC vs chemistry null model, in-sample increment

Failed: sphingolipids/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protgeom8 --seeds=0,1,2,3,4`
