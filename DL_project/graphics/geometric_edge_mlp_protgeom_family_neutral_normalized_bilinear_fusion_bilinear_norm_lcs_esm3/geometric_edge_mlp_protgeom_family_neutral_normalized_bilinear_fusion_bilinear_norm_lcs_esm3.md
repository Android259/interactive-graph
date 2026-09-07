# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.5204      0.6079      0.9348      0.8667      0.5097      0.6225
groups_choline            5      0.3081      0.8635      0.9051      0.7136      0.2982      0.8762
groups_phosphorus_free    5      0.2968      0.8456      0.9012      0.7646      0.3000      0.8179
groups_sphingolipids      5      0.2000      0.7818      0.6081      0.7500      0.2182      0.8481
ALL                      20      0.3313      0.7747      0.8373      0.7737      0.3315      0.7912

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5613      0.5591     0.0396  20
max valid BA                0.6031      0.5979     0.0428  20
best valid F1               0.4922      0.4925     0.0828  20
test BA                     0.5530      0.5438     0.0733  20
test F1                     0.3561      0.4027     0.1811  20
test sensitivity            0.3313      0.3387     0.2075  20
test specificity            0.7747      0.7865     0.1375  20
test precision              0.4413      0.4584     0.1854  20
test loss                   1.0299      1.0385     0.3933  20
FPR (FP/(FP+TN))            0.2253      0.2135     0.1375  20
FNR (FN/(FN+TP))            0.6687      0.6613     0.2075  20

=== abs(sensitivity-specificity) gap: mean=0.4476 median=0.4864 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5661      0.5772     0.0257  5
  max valid BA                0.5816      0.5793     0.0258  5
  best valid F1               0.5257      0.5306     0.0368  5
  test BA                     0.5642      0.5722     0.0321  5
  test F1                     0.4829      0.4944     0.0275  5
  test sensitivity            0.5204      0.5484     0.0434  5
  test specificity            0.6079      0.5960     0.0779  5
  test precision              0.4537      0.4554     0.0447  5
  test loss                   1.2558      1.2901     0.1921  5
  FPR (FP/(FP+TN))            0.3921      0.4040     0.0779  5
  FNR (FN/(FN+TP))            0.4796      0.4516     0.0434  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5872      0.5878     0.0440  5
  max valid BA                0.6187      0.6131     0.0253  5
  best valid F1               0.4894      0.4706     0.0649  5
  test BA                     0.5858      0.5841     0.0850  5
  test F1                     0.3755      0.3188     0.2035  5
  test sensitivity            0.3081      0.2252     0.2237  5
  test specificity            0.8635      0.8743     0.0790  5
  test precision              0.5769      0.6283     0.2075  5
  test loss                   0.8364      0.7408     0.1975  5
  FPR (FP/(FP+TN))            0.1365      0.1257     0.0790  5
  FNR (FN/(FN+TP))            0.6919      0.7748     0.2237  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5589      0.5542     0.0435  5
  max valid BA                0.6361      0.6571     0.0627  5
  best valid F1               0.4936      0.5479     0.1243  5
  test BA                     0.5712      0.5897     0.0983  5
  test F1                     0.3356      0.4231     0.2293  5
  test sensitivity            0.2968      0.3226     0.2534  5
  test specificity            0.8456      0.8772     0.0673  5
  test precision              0.4409      0.5238     0.1906  5
  test loss                   0.8917      0.8015     0.3402  5
  FPR (FP/(FP+TN))            0.1544      0.1228     0.0673  5
  FNR (FN/(FN+TP))            0.7032      0.6774     0.2534  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5332      0.5522     0.0331  5
  max valid BA                0.5761      0.5774     0.0178  5
  best valid F1               0.4601      0.4719     0.0941  5
  test BA                     0.4909      0.4939     0.0293  5
  test F1                     0.2305      0.2609     0.1422  5
  test sensitivity            0.2000      0.1818     0.1415  5
  test specificity            0.7818      0.7455     0.1483  5
  test precision              0.2939      0.3636     0.1773  5
  test loss                   1.1358      0.6884     0.6283  5
  FPR (FP/(FP+TN))            0.2182      0.2545     0.1483  5
  FNR (FN/(FN+TP))            0.8000      0.8182     0.1415  5
```

## AUC vs chemistry null model, in-sample increment

Failed: ValueError: Unknown parameter: --lipid_coldsplit -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3 --seeds=0,1,2,3,4`
