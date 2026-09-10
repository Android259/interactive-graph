# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_cross_forced

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_cross_forced'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.8817      0.1301      0.6871      0.5279      0.6946      0.3692
groups_choline            5      0.7622      0.3733      0.4993      0.5543      0.7411      0.4673
groups_phosphorus_free    5      0.2194      0.6898      0.6771      0.4449      0.4333      0.7184
groups_sphingolipids      5      0.3939      0.5512      0.5595      0.5407      0.6182      0.5500
ALL                      20      0.5643      0.4361      0.6057      0.5170      0.6218      0.5262

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5474      0.5477     0.0291  20
max valid BA                0.5740      0.5753     0.0368  20
best valid F1               0.5633      0.5544     0.0434  20
test BA                     0.5002      0.4923     0.0541  20
test AUC                    0.5102      0.4978     0.0800  20
test AUC in-protein         0.5831      0.5302     0.1367  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5387      0.5140     0.1325  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.4029      0.4484     0.1471  20
test sensitivity            0.5643      0.6306     0.3308  20
test specificity            0.4361      0.4225     0.2894  20
test precision              0.3611      0.3466     0.0681  20
test loss                   0.6996      0.6955     0.0128  20
FPR (FP/(FP+TN))            0.5639      0.5775     0.2894  20
FNR (FN/(FN+TP))            0.4357      0.3694     0.3308  20

=== abs(sensitivity-specificity) gap: mean=0.5351 median=0.5264 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5178      0.5110     0.0196  5
  max valid BA                0.5319      0.5354     0.0125  5
  best valid F1               0.5129      0.5138     0.0037  5
  test BA                     0.5059      0.5000     0.0204  5
  test AUC                    0.4862      0.4943     0.0249  5
  test AUC in-protein         0.4814      0.4701     0.0581  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.4747      0.4724     0.0378  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.4889      0.4983     0.0253  5
  test sensitivity            0.8817      0.9355     0.1377  5
  test specificity            0.1301      0.0437     0.1470  5
  test precision              0.3404      0.3370     0.0119  5
  test loss                   0.7143      0.7170     0.0152  5
  FPR (FP/(FP+TN))            0.8699      0.9563     0.1470  5
  FNR (FN/(FN+TP))            0.1183      0.0645     0.1377  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5678      0.5480     0.0362  5
  max valid BA                0.6042      0.6048     0.0195  5
  best valid F1               0.5550      0.5583     0.0117  5
  test BA                     0.5677      0.5580     0.0524  5
  test AUC                    0.6051      0.6252     0.0681  5
  test AUC in-protein         0.6291      0.6660     0.1006  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.6007      0.6221     0.1156  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.5251      0.5450     0.0422  5
  test sensitivity            0.7622      0.7928     0.1299  5
  test specificity            0.3733      0.3614     0.1712  5
  test precision              0.4072      0.3866     0.0535  5
  test loss                   0.6937      0.6942     0.0020  5
  FPR (FP/(FP+TN))            0.6267      0.6386     0.1712  5
  FNR (FN/(FN+TP))            0.2378      0.2072     0.1299  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5586      0.5551     0.0193  5
  max valid BA                0.5759      0.5776     0.0365  5
  best valid F1               0.5576      0.5505     0.0165  5
  test BA                     0.4546      0.4503     0.0189  5
  test AUC                    0.4672      0.4865     0.0497  5
  test AUC in-protein         0.6733      0.7500     0.1988  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.6049      0.5758     0.0881  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.2293      0.1739     0.1272  5
  test sensitivity            0.2194      0.1290     0.1728  5
  test specificity            0.6898      0.7755     0.1884  5
  test precision              0.2894      0.3235     0.0669  5
  test loss                   0.6924      0.6922     0.0113  5
  FPR (FP/(FP+TN))            0.3102      0.2245     0.1884  5
  FNR (FN/(FN+TP))            0.7806      0.8710     0.1728  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5453      0.5489     0.0135  5
  max valid BA                0.5841      0.5826     0.0326  5
  best valid F1               0.6277      0.6250     0.0071  5
  test BA                     0.4726      0.4819     0.0329  5
  test AUC                    0.4822      0.4760     0.0859  5
  test AUC in-protein         0.5484      0.5045     0.0920  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4744      0.3806     0.2006  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3683      0.3137     0.1308  5
  test sensitivity            0.3939      0.2727     0.3068  5
  test specificity            0.5512      0.6829     0.3039  5
  test precision              0.4076      0.4348     0.0469  5
  test loss                   0.6982      0.6960     0.0055  5
  FPR (FP/(FP+TN))            0.4488      0.3171     0.3039  5
  FNR (FN/(FN+TP))            0.6061      0.7273     0.3068  5
```

## AUC vs chemistry null model, in-sample increment

Failed: sphingolipids/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_cross_forced --seeds=0,1,2,3,4`
