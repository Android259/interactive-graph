# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_attnbypocket

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_attnbypocket'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4836      0.6656      0.6926      0.6934      0.5134      0.6452
groups_GLTP            5      0.2480      0.7120      0.6466      0.6529      0.3615      0.8000
groups_IP_trans        5      0.4522      0.8043      0.6347      0.6433      0.4833      0.7872
groups_LBP_BPI_CETP    5      0.2783      0.9149      0.5912      0.6353      0.3167      0.8894
groups_START           5      0.2308      0.7146      0.6096      0.6041      0.3219      0.7236
groups_lipocalin       5      0.1444      0.8667      0.6067      0.7104      0.1722      0.8833
groups_scp2            5      0.2941      0.8588      0.6791      0.5998      0.3412      0.8824
ALL                   35      0.3045      0.7910      0.6372      0.6484      0.3586      0.8016

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5795      0.5735     0.0555  35
max valid BA                0.6072      0.6012     0.0652  35
best valid F1               0.5082      0.5397     0.1444  35
test BA                     0.5477      0.5584     0.0762  35
test F1                     0.3436      0.3667     0.1844  35
test sensitivity            0.3045      0.3056     0.2028  35
test specificity            0.7910      0.8033     0.1702  35
test precision              0.5162      0.5000     0.1379  33
test loss                   0.6942      0.6796     0.1059  35
FPR (FP/(FP+TN))            0.2090      0.1967     0.1702  35
FNR (FN/(FN+TP))            0.6955      0.6944     0.2028  35

=== abs(sensitivity-specificity) gap: mean=0.5243 median=0.4800 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5793      0.5668     0.0360  5
  max valid BA                0.6045      0.5909     0.0289  5
  best valid F1               0.6507      0.6786     0.0701  5
  test BA                     0.5746      0.5696     0.0181  5
  test F1                     0.5241      0.5000     0.1092  5
  test sensitivity            0.4836      0.4179     0.1993  5
  test specificity            0.6656      0.7213     0.1678  5
  test precision              0.6198      0.6230     0.0182  5
  test loss                   0.6867      0.6829     0.0110  5
  FPR (FP/(FP+TN))            0.3344      0.2787     0.1678  5
  FNR (FN/(FN+TP))            0.5164      0.5821     0.1993  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5769      0.5577     0.0544  5
  max valid BA                0.5885      0.5769     0.0443  5
  best valid F1               0.5389      0.5306     0.1137  5
  test BA                     0.4800      0.4800     0.0894  5
  test F1                     0.3110      0.3000     0.1371  5
  test sensitivity            0.2480      0.2400     0.1277  5
  test specificity            0.7120      0.7200     0.1753  5
  test precision              0.4982      0.4615     0.1539  5
  test loss                   0.7861      0.7467     0.0923  5
  FPR (FP/(FP+TN))            0.2880      0.2800     0.1753  5
  FNR (FN/(FN+TP))            0.7520      0.7600     0.1277  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6353      0.6441     0.0241  5
  max valid BA                0.6645      0.6746     0.0303  5
  best valid F1               0.5640      0.5714     0.0355  5
  test BA                     0.6282      0.6207     0.0541  5
  test F1                     0.4751      0.4444     0.1007  5
  test sensitivity            0.4522      0.4348     0.1808  5
  test specificity            0.8043      0.8511     0.0991  5
  test precision              0.5392      0.5152     0.0712  5
  test loss                   0.7546      0.6607     0.2377  5
  FPR (FP/(FP+TN))            0.1957      0.1489     0.0991  5
  FNR (FN/(FN+TP))            0.5478      0.5652     0.1808  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6030      0.6139     0.0622  5
  max valid BA                0.6605      0.6649     0.0595  5
  best valid F1               0.5265      0.5763     0.1468  5
  test BA                     0.5966      0.5893     0.0830  5
  test F1                     0.3438      0.4286     0.2221  5
  test sensitivity            0.2783      0.3043     0.2165  5
  test specificity            0.9149      0.9574     0.0838  5
  test precision              0.6205      0.6667     0.1294  5
  test loss                   0.6322      0.6351     0.0457  5
  FPR (FP/(FP+TN))            0.0851      0.0426     0.0838  5
  FNR (FN/(FN+TP))            0.7217      0.6957     0.2165  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5227      0.5135     0.0324  5
  max valid BA                0.5419      0.5298     0.0427  5
  best valid F1               0.4086      0.3387     0.1790  5
  test BA                     0.4727      0.4638     0.0301  5
  test F1                     0.2192      0.1319     0.2070  5
  test sensitivity            0.2308      0.0923     0.2551  5
  test specificity            0.7146      0.7753     0.2861  5
  test precision              0.3768      0.3882     0.1107  4
  test loss                   0.7070      0.7083     0.0177  5
  FPR (FP/(FP+TN))            0.2854      0.2247     0.2861  5
  FNR (FN/(FN+TP))            0.7692      0.9077     0.2551  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5278      0.5278     0.0314  5
  max valid BA                0.5403      0.5347     0.0355  5
  best valid F1               0.3384      0.3492     0.1347  5
  test BA                     0.5056      0.5000     0.0397  5
  test F1                     0.1734      0.1000     0.1600  5
  test sensitivity            0.1444      0.0556     0.1488  5
  test specificity            0.8667      0.8472     0.1237  5
  test precision              0.3614      0.3958     0.1554  4
  test loss                   0.6464      0.6359     0.0317  5
  FPR (FP/(FP+TN))            0.1333      0.1528     0.1237  5
  FNR (FN/(FN+TP))            0.8556      0.9444     0.1488  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6118      0.6176     0.0472  5
  max valid BA                0.6500      0.6176     0.0669  5
  best valid F1               0.5303      0.5000     0.0802  5
  test BA                     0.5765      0.5735     0.0263  5
  test F1                     0.3587      0.3571     0.1038  5
  test sensitivity            0.2941      0.2941     0.1248  5
  test specificity            0.8588      0.8235     0.0789  5
  test precision              0.5385      0.5000     0.0830  5
  test loss                   0.6463      0.6514     0.0284  5
  FPR (FP/(FP+TN))            0.1412      0.1765     0.0789  5
  FNR (FN/(FN+TP))            0.7059      0.7059     0.1248  5
```

## AUC vs chemistry null model, in-sample increment

(skipped: SKIP_AUC=1 -- rerun without it to fill this in: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_attnbypocket --seeds=0,1,2,3,4`)
