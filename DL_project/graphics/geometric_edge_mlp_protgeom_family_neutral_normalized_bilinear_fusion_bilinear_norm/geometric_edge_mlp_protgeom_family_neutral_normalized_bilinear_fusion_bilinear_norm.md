# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4358      0.6820      0.7154      0.6450      0.4567      0.6710
groups_GLTP            5      0.2240      0.8480      0.7240      0.6531      0.3000      0.9000
groups_IP_trans        5      0.3391      0.8085      0.7388      0.6595      0.4167      0.8596
groups_LBP_BPI_CETP    5      0.2957      0.8638      0.7536      0.6196      0.4250      0.8170
groups_START           5      0.1723      0.8719      0.7031      0.5372      0.1688      0.8674
groups_lipocalin       5      0.1611      0.8972      0.6287      0.6969      0.1833      0.9000
groups_scp2            5      0.3765      0.7588      0.5845      0.6135      0.4000      0.7588
ALL                   35      0.2864      0.8186      0.6926      0.6321      0.3358      0.8248

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5803      0.5735     0.0600  35
max valid BA                0.6080      0.6029     0.0644  35
best valid F1               0.5197      0.5333     0.1399  35
test BA                     0.5525      0.5262     0.0768  35
test F1                     0.3209      0.3077     0.1995  35
test sensitivity            0.2864      0.2400     0.2311  35
test specificity            0.8186      0.8723     0.1648  35
test precision              0.4869      0.5000     0.1815  33
test loss                   0.7327      0.6833     0.1771  35
FPR (FP/(FP+TN))            0.1814      0.1277     0.1648  35
FNR (FN/(FN+TP))            0.7136      0.7600     0.2311  35

=== abs(sensitivity-specificity) gap: mean=0.5863 median=0.5929 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5638      0.5668     0.0495  5
  max valid BA                0.6001      0.5874     0.0413  5
  best valid F1               0.6545      0.6512     0.0561  5
  test BA                     0.5589      0.5323     0.0672  5
  test F1                     0.4714      0.4299     0.1781  5
  test sensitivity            0.4358      0.3433     0.2612  5
  test specificity            0.6820      0.7705     0.2720  5
  test precision              0.6202      0.6176     0.0777  5
  test loss                   0.6942      0.6954     0.0228  5
  FPR (FP/(FP+TN))            0.3180      0.2295     0.2720  5
  FNR (FN/(FN+TP))            0.5642      0.6567     0.2612  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6000      0.5769     0.0658  5
  max valid BA                0.6038      0.5962     0.0646  5
  best valid F1               0.5675      0.5946     0.1217  5
  test BA                     0.5360      0.5000     0.1187  5
  test F1                     0.3198      0.2703     0.1824  5
  test sensitivity            0.2240      0.2000     0.1345  5
  test specificity            0.8480      0.9200     0.1397  5
  test precision              0.6000      0.5000     0.2726  5
  test loss                   0.8140      0.8483     0.0618  5
  FPR (FP/(FP+TN))            0.1520      0.0800     0.1397  5
  FNR (FN/(FN+TP))            0.7760      0.8000     0.1345  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6381      0.6551     0.0429  5
  max valid BA                0.6744      0.6844     0.0447  5
  best valid F1               0.5823      0.5926     0.0489  5
  test BA                     0.5738      0.5458     0.0779  5
  test F1                     0.3717      0.3429     0.1427  5
  test sensitivity            0.3391      0.2609     0.2049  5
  test specificity            0.8085      0.7872     0.0638  5
  test precision              0.4477      0.4118     0.0748  5
  test loss                   0.6962      0.6397     0.1339  5
  FPR (FP/(FP+TN))            0.1915      0.2128     0.0638  5
  FNR (FN/(FN+TP))            0.6609      0.7391     0.2049  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6210      0.6445     0.0654  5
  max valid BA                0.6352      0.6857     0.0768  5
  best valid F1               0.5072      0.5965     0.1696  5
  test BA                     0.5797      0.5231     0.1013  5
  test F1                     0.3208      0.2424     0.2580  5
  test sensitivity            0.2957      0.1739     0.2739  5
  test specificity            0.8638      0.8723     0.1005  5
  test precision              0.3918      0.4000     0.2505  5
  test loss                   0.8119      0.6523     0.4143  5
  FPR (FP/(FP+TN))            0.1362      0.1277     0.1005  5
  FNR (FN/(FN+TP))            0.7043      0.8261     0.2739  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5181      0.5041     0.0325  5
  max valid BA                0.5523      0.5356     0.0780  5
  best valid F1               0.4427      0.3780     0.1908  5
  test BA                     0.5221      0.5000     0.0632  5
  test F1                     0.2086      0.1556     0.2156  5
  test sensitivity            0.1723      0.1077     0.2212  5
  test specificity            0.8719      0.9326     0.1280  5
  test precision              0.4606      0.4688     0.1606  4
  test loss                   0.7756      0.6915     0.1890  5
  FPR (FP/(FP+TN))            0.1281      0.0674     0.1280  5
  FNR (FN/(FN+TP))            0.8277      0.8923     0.2212  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5417      0.5347     0.0354  5
  max valid BA                0.5667      0.5625     0.0446  5
  best valid F1               0.3786      0.4409     0.1280  5
  test BA                     0.5292      0.5069     0.0528  5
  test F1                     0.1932      0.0976     0.2026  5
  test sensitivity            0.1611      0.0556     0.1836  5
  test specificity            0.8972      0.9444     0.1148  5
  test precision              0.3933      0.3912     0.1598  4
  test loss                   0.6751      0.6683     0.0640  5
  FPR (FP/(FP+TN))            0.1028      0.0556     0.1148  5
  FNR (FN/(FN+TP))            0.8389      0.9444     0.1836  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5794      0.5735     0.0397  5
  max valid BA                0.6235      0.6176     0.0246  5
  best valid F1               0.5052      0.5217     0.0362  5
  test BA                     0.5676      0.5294     0.0663  5
  test F1                     0.3611      0.4000     0.1711  5
  test sensitivity            0.3765      0.3529     0.2929  5
  test specificity            0.7588      0.9118     0.2253  5
  test precision              0.4704      0.4375     0.1229  5
  test loss                   0.6616      0.6573     0.0233  5
  FPR (FP/(FP+TN))            0.2412      0.0882     0.2253  5
  FNR (FN/(FN+TP))            0.6235      0.6471     0.2929  5
```

## AUC vs chemistry null model, in-sample increment

