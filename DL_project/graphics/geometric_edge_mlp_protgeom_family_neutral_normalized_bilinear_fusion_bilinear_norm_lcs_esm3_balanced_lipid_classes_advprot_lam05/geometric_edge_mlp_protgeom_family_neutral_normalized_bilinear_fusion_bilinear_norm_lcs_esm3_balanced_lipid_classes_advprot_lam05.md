# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_lam05

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_lam05'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6710      0.3650      0.5210      0.6080      0.6043      0.4956
groups_choline            5      0.7892      0.3307      0.4263      0.6157      0.6536      0.5396
groups_phosphorus_free    5      0.0129      0.9592      0.4750      0.6400      0.0867      0.9673
groups_sphingolipids      5      0.2606      0.8293      0.6454      0.5842      0.5818      0.7000
ALL                      20      0.4334      0.6210      0.5169      0.6119      0.4816      0.6756

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5611      0.5332     0.0749  20
max valid BA                0.5786      0.5514     0.0714  20
best valid F1               0.5247      0.5403     0.1528  20
test BA                     0.5272      0.5037     0.0683  20
test AUC                    0.5624      0.5447     0.0841  20
test AUC in-protein         0.5975      0.6354     0.1580  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5820      0.5687     0.1283  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.3224      0.3630     0.2340  20
test sensitivity            0.4334      0.3675     0.3847  20
test specificity            0.6210      0.6951     0.3436  20
test precision              0.3659      0.3581     0.1747  17
test loss                   0.6860      0.6900     0.0358  20
FPR (FP/(FP+TN))            0.3790      0.3049     0.3436  20
FNR (FN/(FN+TP))            0.5666      0.6325     0.3847  20

=== abs(sensitivity-specificity) gap: mean=0.6578 median=0.6957 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5316      0.5311     0.0304  5
  max valid BA                0.5500      0.5493     0.0154  5
  best valid F1               0.5202      0.5145     0.0116  5
  test BA                     0.5180      0.5169     0.0374  5
  test AUC                    0.5401      0.5135     0.0720  5
  test AUC in-protein         0.4926      0.4878     0.0302  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.4823      0.4807     0.0320  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.4265      0.4969     0.1356  5
  test sensitivity            0.6710      0.8602     0.3461  5
  test specificity            0.3650      0.2186     0.2905  5
  test precision              0.3384      0.3452     0.0328  5
  test loss                   0.7083      0.7068     0.0176  5
  FPR (FP/(FP+TN))            0.6350      0.7814     0.2905  5
  FNR (FN/(FN+TP))            0.3290      0.1398     0.3461  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5697      0.5696     0.0545  5
  max valid BA                0.5966      0.5711     0.0522  5
  best valid F1               0.5584      0.5407     0.0266  5
  test BA                     0.5599      0.5679     0.0347  5
  test AUC                    0.6227      0.6072     0.0408  5
  test AUC in-protein         0.6852      0.6556     0.0659  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.6280      0.6230     0.0504  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.5199      0.5305     0.0371  5
  test sensitivity            0.7892      0.8378     0.2177  5
  test specificity            0.3307      0.3119     0.2683  5
  test precision              0.4027      0.4009     0.0353  5
  test loss                   0.6903      0.6952     0.0079  5
  FPR (FP/(FP+TN))            0.6693      0.6881     0.2683  5
  FNR (FN/(FN+TP))            0.2108      0.1622     0.2177  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5170      0.5092     0.0133  5
  max valid BA                0.5270      0.5194     0.0229  5
  best valid F1               0.3618      0.4615     0.2239  5
  test BA                     0.4860      0.4898     0.0155  5
  test AUC                    0.5180      0.5082     0.0489  5
  test AUC in-protein         0.5833      0.6667     0.2186  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.5922      0.5652     0.0548  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.0219      0.0000     0.0300  5
  test sensitivity            0.0129      0.0000     0.0177  5
  test specificity            0.9592      0.9796     0.0479  5
  test precision              0.1222      0.1667     0.1072  3
  test loss                   0.6766      0.6773     0.0032  5
  FPR (FP/(FP+TN))            0.0408      0.0204     0.0479  5
  FNR (FN/(FN+TP))            0.9871      1.0000     0.0177  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6263      0.6148     0.1169  5
  max valid BA                0.6409      0.6299     0.1053  5
  best valid F1               0.6582      0.6400     0.0550  5
  test BA                     0.5449      0.5000     0.1240  5
  test AUC                    0.5688      0.5477     0.1290  5
  test AUC in-protein         0.6288      0.5250     0.2018  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.6254      0.6386     0.2326  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3213      0.3333     0.2533  5
  test sensitivity            0.2606      0.2424     0.2202  5
  test specificity            0.8293      0.8537     0.1336  5
  test precision              0.5373      0.5000     0.2234  4
  test loss                   0.6689      0.6902     0.0676  5
  FPR (FP/(FP+TN))            0.1707      0.1463     0.1336  5
  FNR (FN/(FN+TP))            0.7394      0.7576     0.2202  5
```

## AUC vs chemistry null model, in-sample increment

Failed: sphingolipids/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_lam05 --seeds=0,1,2,3,4`
