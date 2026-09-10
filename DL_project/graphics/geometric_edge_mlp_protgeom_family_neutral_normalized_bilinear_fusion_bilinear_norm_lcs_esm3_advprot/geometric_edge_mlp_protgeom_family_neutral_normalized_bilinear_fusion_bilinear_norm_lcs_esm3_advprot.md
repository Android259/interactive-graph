# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_advprot

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_advprot'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.5505      0.4887      0.6732      0.5266      0.6839      0.4079
groups_choline            5      0.3802      0.8251      0.6423      0.6642      0.4500      0.8190
groups_phosphorus_free    5      0.4065      0.6491      0.5885      0.4138      0.4867      0.5893
groups_sphingolipids      5      0.2909      0.6982      0.5415      0.6528      0.4303      0.6407
ALL                      20      0.4070      0.6653      0.6114      0.5644      0.5127      0.6143

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5423      0.5373     0.0525  20
max valid BA                0.5635      0.5501     0.0552  20
best valid F1               0.5185      0.5510     0.1037  20
test BA                     0.5362      0.5278     0.0731  20
test AUC                    0.5317      0.5297     0.1196  20
test AUC in-protein         0.5209      0.5032     0.1157  20
  (proteins averaged)       7.9000      8.5000     3.5968  20
test AUC in-protein (pairs)      0.5388      0.5457     0.1394  20
  (proteins contributing)     11.7000     14.0000     5.3024  20
test F1                     0.3653      0.3912     0.1884  20
test sensitivity            0.4070      0.3788     0.2772  20
test specificity            0.6653      0.6534     0.2692  20
test precision              0.4606      0.4141     0.1433  17
test loss                   0.6837      0.6875     0.0352  20
FPR (FP/(FP+TN))            0.3347      0.3466     0.2692  20
FNR (FN/(FN+TP))            0.5930      0.6212     0.2772  20

=== abs(sensitivity-specificity) gap: mean=0.4864 median=0.3817 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5278      0.5258     0.0262  5
  max valid BA                0.5459      0.5514     0.0268  5
  best valid F1               0.5388      0.5519     0.0183  5
  test BA                     0.5196      0.5000     0.0389  5
  test AUC                    0.5294      0.5294     0.0467  5
  test AUC in-protein         0.5055      0.5031     0.1024  5
    (proteins averaged)      12.2000     12.0000     0.4472  5
  test AUC in-protein (pairs)      0.5482      0.5455     0.0648  5
    (proteins contributing)     16.4000     17.0000     1.5166  5
  test F1                     0.3975      0.4628     0.2286  5
  test sensitivity            0.5505      0.6022     0.3652  5
  test specificity            0.4887      0.4371     0.3618  5
  test precision              0.4030      0.3959     0.0328  4
  test loss                   0.7055      0.6933     0.0363  5
  FPR (FP/(FP+TN))            0.5113      0.5629     0.3618  5
  FNR (FN/(FN+TP))            0.4495      0.3978     0.3652  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6012      0.5938     0.0327  5
  max valid BA                0.6345      0.6399     0.0338  5
  best valid F1               0.5812      0.5714     0.0134  5
  test BA                     0.6027      0.5933     0.0330  5
  test AUC                    0.6556      0.6519     0.0444  5
  test AUC in-protein         0.6436      0.6478     0.0498  5
    (proteins averaged)       9.8000     10.0000     0.4472  5
  test AUC in-protein (pairs)      0.6716      0.6621     0.0570  5
    (proteins contributing)     14.8000     15.0000     0.4472  5
  test F1                     0.4459      0.4343     0.1093  5
  test sensitivity            0.3802      0.3423     0.1659  5
  test specificity            0.8251      0.8443     0.1325  5
  test precision              0.6350      0.5938     0.1256  5
  test loss                   0.6401      0.6468     0.0159  5
  FPR (FP/(FP+TN))            0.1749      0.1557     0.1325  5
  FNR (FN/(FN+TP))            0.6198      0.6577     0.1659  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5161      0.5000     0.0716  5
  max valid BA                0.5380      0.5000     0.0614  5
  best valid F1               0.4339      0.5172     0.1812  5
  test BA                     0.5278      0.5000     0.1124  5
  test AUC                    0.4456      0.3829     0.1704  5
  test AUC in-protein         0.4519      0.4189     0.1505  5
    (proteins averaged)       6.6000      7.0000     1.1402  5
  test AUC in-protein (pairs)      0.4370      0.3143     0.2066  5
    (proteins contributing)     12.2000     13.0000     2.1679  5
  test F1                     0.2965      0.3636     0.2884  5
  test sensitivity            0.4065      0.5161     0.3922  5
  test specificity            0.6491      0.5439     0.3336  5
  test precision              0.3892      0.3774     0.1148  3
  test loss                   0.6989      0.6930     0.0293  5
  FPR (FP/(FP+TN))            0.3509      0.4561     0.3336  5
  FNR (FN/(FN+TP))            0.5935      0.4839     0.3922  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5242      0.5168     0.0185  5
  max valid BA                0.5355      0.5354     0.0186  5
  best valid F1               0.5202      0.5500     0.0579  5
  test BA                     0.4945      0.5061     0.0445  5
  test AUC                    0.4963      0.5267     0.0689  5
  test AUC in-protein         0.4824      0.4690     0.0333  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4984      0.5206     0.0709  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.3212      0.3137     0.0596  5
  test sensitivity            0.2909      0.2424     0.0819  5
  test specificity            0.6982      0.6909     0.1095  5
  test precision              0.3750      0.3889     0.0679  5
  test loss                   0.6902      0.6910     0.0124  5
  FPR (FP/(FP+TN))            0.3018      0.3091     0.1095  5
  FNR (FN/(FN+TP))            0.7091      0.7576     0.0819  5
```

## AUC vs chemistry null model, in-sample increment

Failed: sphingolipids/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_advprot --seeds=0,1,2,3,4`
