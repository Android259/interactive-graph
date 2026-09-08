# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_liphid64

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_liphid64'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6946      0.7027      0.8897      0.8295      0.7204      0.7637
groups_choline            5      0.4847      0.6020      0.8715      0.8022      0.5375      0.6495
groups_phosphorus_free    5      0.5419      0.5061      0.8743      0.7434      0.7067      0.6286
groups_sphingolipids      5      0.7455      0.5463      0.8835      0.7691      0.7455      0.6850
ALL                      20      0.6167      0.5893      0.8798      0.7861      0.6775      0.6817

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6505      0.6706     0.0854  20
max valid BA                0.6796      0.7008     0.0967  20
best valid F1               0.6271      0.6466     0.1035  20
test BA                     0.6030      0.6127     0.1056  20
test AUC                    0.5720      0.5965     0.1441  18
test AUC in-protein         0.5484      0.5461     0.1244  10
  (proteins averaged)       6.5000      6.0000     4.9944  10
test F1                     0.5344      0.5840     0.1374  20
test sensitivity            0.6167      0.6613     0.1960  20
test specificity            0.5893      0.6584     0.2005  20
test precision              0.4867      0.4990     0.1255  20
test loss                   0.8821      0.8613     0.1907  20
FPR (FP/(FP+TN))            0.4107      0.3416     0.2005  20
FNR (FN/(FN+TP))            0.3833      0.3387     0.1960  20

=== abs(sensitivity-specificity) gap: mean=0.2277 median=0.1679 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7207      0.7202     0.0153  5
  max valid BA                0.7421      0.7372     0.0124  5
  best valid F1               0.6597      0.6526     0.0156  5
  test BA                     0.6987      0.6910     0.0234  5
  test AUC                    0.7252      0.7164     0.0241  3
  test AUC in-protein         0.4625      0.4625     0.0000  1
    (proteins averaged)      11.0000     11.0000     0.0000  1
  test F1                     0.6091      0.6019     0.0278  5
  test sensitivity            0.6946      0.6882     0.0434  5
  test specificity            0.7027      0.7049     0.0175  5
  test precision              0.5428      0.5289     0.0211  5
  test loss                   0.8790      0.8624     0.1032  5
  FPR (FP/(FP+TN))            0.2973      0.2951     0.0175  5
  FNR (FN/(FN+TP))            0.3054      0.3118     0.0434  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5733      0.5748     0.0572  5
  max valid BA                0.5935      0.5805     0.0621  5
  best valid F1               0.5264      0.5481     0.0584  5
  test BA                     0.5433      0.5400     0.0963  5
  test AUC                    0.5021      0.5041     0.1239  5
  test AUC in-protein         0.5040      0.5461     0.1312  4
    (proteins averaged)      11.2500     11.5000     0.9574  4
  test F1                     0.4344      0.4615     0.1222  5
  test sensitivity            0.4847      0.5315     0.1803  5
  test specificity            0.6020      0.6337     0.2034  5
  test precision              0.4119      0.4176     0.1222  5
  test loss                   0.8969      0.8603     0.1795  5
  FPR (FP/(FP+TN))            0.3980      0.3663     0.2034  5
  FNR (FN/(FN+TP))            0.5153      0.4685     0.1803  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6431      0.6439     0.0583  5
  max valid BA                0.6676      0.6847     0.0691  5
  best valid F1               0.6023      0.6377     0.1101  5
  test BA                     0.5240      0.5504     0.0741  5
  test AUC                    0.5095      0.5451     0.1129  5
  test AUC in-protein         0.5500      0.5500     0.0707  2
    (proteins averaged)       1.5000      1.5000     0.7071  2
  test F1                     0.4430      0.5000     0.1515  5
  test sensitivity            0.5419      0.5806     0.2654  5
  test specificity            0.5061      0.5306     0.1380  5
  test precision              0.3902      0.4211     0.0777  5
  test loss                   1.0063      0.9111     0.2581  5
  FPR (FP/(FP+TN))            0.4939      0.4694     0.1380  5
  FNR (FN/(FN+TP))            0.4581      0.4194     0.2654  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6647      0.7083     0.1174  5
  max valid BA                0.7152      0.7155     0.1406  5
  best valid F1               0.7200      0.6804     0.0979  5
  test BA                     0.6459      0.6593     0.1080  5
  test AUC                    0.6124      0.6009     0.1711  5
  test AUC in-protein         0.6352      0.6097     0.1496  3
    (proteins averaged)       2.0000      2.0000     0.0000  3
  test F1                     0.6509      0.6579     0.0646  5
  test sensitivity            0.7455      0.7576     0.1431  5
  test specificity            0.5463      0.6098     0.3211  5
  test precision              0.6021      0.5814     0.1191  5
  test loss                   0.7461      0.7474     0.1434  5
  FPR (FP/(FP+TN))            0.4537      0.3902     0.3211  5
  FNR (FN/(FN+TP))            0.2545      0.2424     0.1431  5
```

## AUC vs chemistry null model, in-sample increment

Failed: sphingolipids/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_liphid64 --seeds=0,1,2,3,4`
