# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_rankprot

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_rankprot'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.8215      0.4536      0.8951      0.6680      0.8323      0.5407
groups_choline            5      0.6180      0.6030      0.6900      0.6384      0.7357      0.5475
groups_phosphorus_free    5      0.3290      0.7469      0.8506      0.5698      0.5467      0.7551
groups_sphingolipids      5      0.6364      0.4341      0.7468      0.5281      0.8182      0.4700
ALL                      20      0.6012      0.5594      0.7956      0.6011      0.7332      0.5783

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6164      0.6356     0.0708  20
max valid BA                0.6558      0.6705     0.0543  20
best valid F1               0.5963      0.6266     0.1050  20
test BA                     0.5803      0.6072     0.0929  20
test AUC                    0.6002      0.6228     0.1094  20
test AUC in-protein         0.5562      0.5157     0.1737  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.6364      0.6364     0.0000  1
  (proteins contributing)     10.0000     10.0000     0.0000  1
test F1                     0.4912      0.5525     0.1431  20
test sensitivity            0.6012      0.6649     0.2577  20
test specificity            0.5594      0.4716     0.2363  20
test precision              0.4762      0.4413     0.1123  20
test loss                   0.7383      0.7166     0.1910  20
FPR (FP/(FP+TN))            0.4406      0.5284     0.2363  20
FNR (FN/(FN+TP))            0.3988      0.3351     0.2577  20

=== abs(sensitivity-specificity) gap: mean=0.3881 median=0.4132 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6629      0.6770     0.0451  5
  max valid BA                0.6865      0.6770     0.0435  5
  best valid F1               0.6124      0.6058     0.0408  5
  test BA                     0.6375      0.6405     0.0333  5
  test AUC                    0.7034      0.6932     0.0271  5
  test AUC in-protein         0.4916      0.5278     0.1023  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test F1                     0.5681      0.5735     0.0213  5
  test sensitivity            0.8215      0.8602     0.1005  5
  test specificity            0.4536      0.4208     0.1446  5
  test precision              0.4408      0.4301     0.0496  5
  test loss                   0.8782      0.7555     0.3177  5
  FPR (FP/(FP+TN))            0.5464      0.5792     0.1446  5
  FNR (FN/(FN+TP))            0.1785      0.1398     0.1005  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6098      0.6567     0.0816  5
  max valid BA                0.6416      0.6766     0.0610  5
  best valid F1               0.5634      0.6209     0.0937  5
  test BA                     0.6105      0.6102     0.0745  5
  test AUC                    0.6239      0.6307     0.0598  5
  test AUC in-protein         0.6020      0.6451     0.0775  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test F1                     0.4994      0.5566     0.1688  5
  test sensitivity            0.6180      0.6937     0.2692  5
  test specificity            0.6030      0.5941     0.1609  5
  test precision              0.4485      0.4343     0.0639  5
  test loss                   0.7021      0.7176     0.0391  5
  FPR (FP/(FP+TN))            0.3970      0.4059     0.1609  5
  FNR (FN/(FN+TP))            0.3820      0.3063     0.2692  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5955      0.5796     0.0627  5
  max valid BA                0.6509      0.6776     0.0646  5
  best valid F1               0.5274      0.6000     0.1553  5
  test BA                     0.5380      0.5211     0.0785  5
  test AUC                    0.5571      0.5648     0.1270  5
  test AUC in-protein         0.5967      0.5000     0.3296  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.6364      0.6364     0.0000  1
    (proteins contributing)     10.0000     10.0000     0.0000  1
  test F1                     0.3546      0.3500     0.1427  5
  test sensitivity            0.3290      0.2258     0.2071  5
  test specificity            0.7469      0.8163     0.2655  5
  test precision              0.5194      0.5000     0.1653  5
  test loss                   0.6458      0.6579     0.1064  5
  FPR (FP/(FP+TN))            0.2531      0.1837     0.2655  5
  FNR (FN/(FN+TP))            0.6710      0.7742     0.2071  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5976      0.5591     0.0865  5
  max valid BA                0.6441      0.6155     0.0507  5
  best valid F1               0.6819      0.6804     0.0320  5
  test BA                     0.5353      0.6042     0.1347  5
  test AUC                    0.5165      0.5233     0.1063  5
  test AUC in-protein         0.5347      0.5000     0.0877  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test F1                     0.5426      0.5965     0.1179  5
  test sensitivity            0.6364      0.6364     0.1868  5
  test specificity            0.4341      0.4146     0.2606  5
  test precision              0.4960      0.5192     0.1439  5
  test loss                   0.7273      0.8076     0.1504  5
  FPR (FP/(FP+TN))            0.5659      0.5854     0.2606  5
  FNR (FN/(FN+TP))            0.3636      0.3636     0.1868  5
```

## AUC vs chemistry null model, in-sample increment

Failed: sphingolipids/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_rankprot --seeds=0,1,2,3,4`
