# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_balanced_lipid_classes_advprot

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_balanced_lipid_classes_advprot'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.5914      0.4175      0.6330      0.5340      0.6151      0.4527
groups_choline            5      0.5856      0.5644      0.4691      0.6032      0.6857      0.5168
groups_phosphorus_free    5      0.2710      0.6694      0.4939      0.5788      0.3800      0.7306
groups_sphingolipids      5      0.3879      0.5171      0.5680      0.5163      0.5455      0.6650
ALL                      20      0.4590      0.5421      0.5410      0.5581      0.5566      0.5913

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5521      0.5425     0.0394  20
max valid BA                0.5739      0.5578     0.0434  20
best valid F1               0.5437      0.5382     0.0572  20
test BA                     0.5005      0.4946     0.0563  20
test AUC                    0.5072      0.4998     0.0727  20
test AUC in-protein         0.6160      0.5709     0.1623  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5575      0.5483     0.1389  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.3593      0.3861     0.1694  20
test sensitivity            0.4590      0.4042     0.3369  20
test specificity            0.5421      0.6485     0.2978  20
test precision              0.3517      0.3563     0.0763  20
test loss                   0.6990      0.6938     0.0231  20
FPR (FP/(FP+TN))            0.4579      0.3515     0.2978  20
FNR (FN/(FN+TP))            0.5410      0.5958     0.3369  20

=== abs(sensitivity-specificity) gap: mean=0.5322 median=0.5200 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5242      0.5254     0.0143  5
  max valid BA                0.5339      0.5353     0.0119  5
  best valid F1               0.5121      0.5111     0.0039  5
  test BA                     0.5044      0.5082     0.0224  5
  test AUC                    0.4959      0.4846     0.0321  5
  test AUC in-protein         0.5294      0.5228     0.0435  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.5146      0.5028     0.0481  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.3977      0.4310     0.1205  5
  test sensitivity            0.5914      0.5376     0.3650  5
  test specificity            0.4175      0.5137     0.3366  5
  test precision              0.3330      0.3407     0.0277  5
  test loss                   0.7162      0.6936     0.0427  5
  FPR (FP/(FP+TN))            0.5825      0.4863     0.3366  5
  FNR (FN/(FN+TP))            0.4086      0.4624     0.3650  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5768      0.5641     0.0316  5
  max valid BA                0.6013      0.5877     0.0375  5
  best valid F1               0.5483      0.5387     0.0221  5
  test BA                     0.5750      0.5818     0.0388  5
  test AUC                    0.6018      0.5983     0.0464  5
  test AUC in-protein         0.6273      0.6352     0.0881  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.6008      0.5790     0.1057  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.4855      0.5128     0.0661  5
  test sensitivity            0.5856      0.5405     0.1715  5
  test specificity            0.5644      0.6089     0.1446  5
  test precision              0.4277      0.4203     0.0445  5
  test loss                   0.6917      0.6928     0.0051  5
  FPR (FP/(FP+TN))            0.4356      0.3911     0.1446  5
  FNR (FN/(FN+TP))            0.4144      0.4595     0.1715  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5422      0.5296     0.0360  5
  max valid BA                0.5553      0.5480     0.0310  5
  best valid F1               0.4992      0.5070     0.0607  5
  test BA                     0.4702      0.4651     0.0144  5
  test AUC                    0.4807      0.4832     0.0413  5
  test AUC in-protein         0.8322      0.8333     0.1460  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.6887      0.7273     0.1214  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.2189      0.1818     0.1954  5
  test sensitivity            0.2710      0.1290     0.3928  5
  test specificity            0.6694      0.8163     0.3666  5
  test precision              0.2751      0.2941     0.0836  5
  test loss                   0.6903      0.6894     0.0094  5
  FPR (FP/(FP+TN))            0.3306      0.1837     0.3666  5
  FNR (FN/(FN+TP))            0.7290      0.8710     0.3928  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5651      0.5614     0.0528  5
  max valid BA                0.6052      0.6163     0.0430  5
  best valid F1               0.6151      0.6286     0.0351  5
  test BA                     0.4525      0.4568     0.0432  5
  test AUC                    0.4503      0.4324     0.0629  5
  test AUC in-protein         0.4751      0.5000     0.0380  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4261      0.4487     0.1254  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3352      0.2903     0.1791  5
  test sensitivity            0.3879      0.2727     0.3601  5
  test specificity            0.5171      0.5122     0.3342  5
  test precision              0.3711      0.3714     0.0491  5
  test loss                   0.6979      0.6951     0.0073  5
  FPR (FP/(FP+TN))            0.4829      0.4878     0.3342  5
  FNR (FN/(FN+TP))            0.6121      0.7273     0.3601  5
```

## AUC vs chemistry null model, in-sample increment

Failed: sphingolipids/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_balanced_lipid_classes_advprot --seeds=0,1,2,3,4`
