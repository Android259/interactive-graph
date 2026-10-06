# mlp_sub_pb6_drop_ev28_q10

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_drop_ev28_q10'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.5394      0.4634      0.4792      0.5530      0.5333      0.5000
groups_FA                                    5      0.1583      0.8973      0.5778      0.6850      0.2917      0.8167
groups_LPC+LPE+LPG                           5      0.5625      0.7419      0.7658      0.6630      0.5875      0.7000
groups_PA                                    5      0.5538      0.9154      0.5523      0.7258      0.4923      0.9615
groups_PC                                    5      0.5339      0.5076      0.5904      0.4880      0.5468      0.5147
groups_PE                                    5      0.8650      0.7500      0.7357      0.7545      0.8900      0.7650
groups_PG                                    5      0.7228      0.7646      0.7317      0.7412      0.6857      0.7858
groups_PI                                    5      0.2000      0.7125      0.4207      0.6806      0.3750      0.8125
ALL                                         40      0.5170      0.7191      0.6067      0.6614      0.5503      0.7320

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6326      0.6105     0.1175  40
max valid BA                0.6412      0.6240     0.1152  40
best valid F1               0.5644      0.5774     0.1367  40
test BA                     0.6180      0.5653     0.1339  40
test AUC                    0.6047      0.6136     0.2068  40
test AUC in-protein         0.5834      0.5828     0.2521  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.5549      0.5414     0.2214  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.4546      0.5594     0.2646  40
test sensitivity            0.5170      0.6154     0.3373  40
test specificity            0.7191      0.8027     0.2932  40
test precision              0.5264      0.5965     0.2126  35
test loss                   0.6420      0.6715     0.0971  40
FPR (FP/(FP+TN))            0.2809      0.1973     0.2932  40
FNR (FN/(FN+TP))            0.4830      0.3846     0.3373  40

=== abs(sensitivity-specificity) gap: mean=0.4776 median=0.3786 n=40 ===
sensitivity std across seeds (by group): mean=0.2133 median=0.1272 n=8
specificity std across seeds (by group): mean=0.2119 median=0.1278 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5136      0.5000     0.0195  5
  max valid BA                0.5167      0.5000     0.0228  5
  best valid F1               0.5556      0.6226     0.0934  5
  test BA                     0.5014      0.5000     0.0108  5
  test AUC                    0.4284      0.4457     0.0600  5
  test AUC in-protein         0.3877      0.4261     0.0916  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3392      0.3079     0.1357  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3572      0.5556     0.3270  5
  test sensitivity            0.5394      0.7576     0.5004  5
  test specificity            0.4634      0.2195     0.4960  5
  test precision              0.4468      0.4459     0.0087  3
  test loss                   0.7092      0.6977     0.0270  5
  FPR (FP/(FP+TN))            0.5366      0.7805     0.4960  5
  FNR (FN/(FN+TP))            0.4606      0.2424     0.5004  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5444      0.5625     0.0324  5
  max valid BA                0.5542      0.5625     0.0284  5
  best valid F1               0.4700      0.5067     0.1308  5
  test BA                     0.5278      0.5084     0.0358  5
  test AUC                    0.4457      0.3356     0.1816  5
  test AUC in-protein         0.6083      0.8000     0.4059  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.5587      0.5455     0.1779  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.2230      0.2759     0.1356  5
  test sensitivity            0.1583      0.1667     0.1079  5
  test specificity            0.8973      0.9189     0.1169  5
  test precision              0.5606      0.5268     0.1901  4
  test loss                   0.7298      0.6955     0.0803  5
  FPR (FP/(FP+TN))            0.1027      0.0811     0.1169  5
  FNR (FN/(FN+TP))            0.8417      0.8333     0.1079  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6388      0.6146     0.0657  5
  max valid BA                0.6438      0.6229     0.0638  5
  best valid F1               0.5591      0.5333     0.0699  5
  test BA                     0.6522      0.6865     0.1046  5
  test AUC                    0.6804      0.7137     0.1570  5
  test AUC in-protein         0.7728      0.7986     0.0767  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.6969      0.7273     0.1077  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5475      0.5600     0.1227  5
  test sensitivity            0.5625      0.5000     0.1466  5
  test specificity            0.7419      0.7419     0.1387  5
  test precision              0.5589      0.6000     0.1717  5
  test loss                   0.6332      0.6385     0.0873  5
  FPR (FP/(FP+TN))            0.2581      0.2581     0.1387  5
  FNR (FN/(FN+TP))            0.4375      0.5000     0.1466  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7269      0.7115     0.0394  5
  max valid BA                0.7269      0.7115     0.0394  5
  best valid F1               0.6301      0.6000     0.0627  5
  test BA                     0.7346      0.7115     0.0498  5
  test AUC                    0.7598      0.7308     0.0940  5
  test AUC in-protein         0.7292      0.8583     0.3622  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.7038      0.8000     0.2469  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6436      0.6087     0.0776  5
  test sensitivity            0.5538      0.5385     0.0644  5
  test specificity            0.9154      0.9231     0.0501  5
  test precision              0.7728      0.7500     0.1133  5
  test loss                   0.6031      0.6174     0.0547  5
  FPR (FP/(FP+TN))            0.0846      0.0769     0.0501  5
  FNR (FN/(FN+TP))            0.4462      0.4615     0.0644  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5215      0.5017     0.0487  5
  max valid BA                0.5308      0.5118     0.0466  5
  best valid F1               0.4268      0.5253     0.1567  5
  test BA                     0.5208      0.5000     0.0397  5
  test AUC                    0.4375      0.4090     0.0815  5
  test AUC in-protein         0.4320      0.3915     0.2180  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4321      0.4500     0.1565  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3338      0.4946     0.2664  5
  test sensitivity            0.5339      0.6330     0.4853  5
  test specificity            0.5076      0.4873     0.4409  5
  test precision              0.2805      0.3562     0.1682  5
  test loss                   0.7153      0.6934     0.0600  5
  FPR (FP/(FP+TN))            0.4924      0.5127     0.4409  5
  FNR (FN/(FN+TP))            0.4661      0.3670     0.4853  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8263      0.8375     0.0156  5
  max valid BA                0.8275      0.8375     0.0169  5
  best valid F1               0.7542      0.7600     0.0189  5
  test BA                     0.8075      0.7812     0.0399  5
  test AUC                    0.8940      0.8850     0.0436  5
  test AUC in-protein         0.7437      0.7358     0.1514  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7364      0.7000     0.1129  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7323      0.7010     0.0468  5
  test sensitivity            0.8650      0.8500     0.0379  5
  test specificity            0.7500      0.7250     0.0459  5
  test precision              0.6355      0.6000     0.0520  5
  test loss                   0.4819      0.4819     0.0562  5
  FPR (FP/(FP+TN))            0.2500      0.2750     0.0459  5
  FNR (FN/(FN+TP))            0.1350      0.1500     0.0379  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7332      0.7330     0.0273  5
  max valid BA                0.7358      0.7330     0.0241  5
  best valid F1               0.6490      0.6435     0.0297  5
  test BA                     0.7437      0.7401     0.0189  5
  test AUC                    0.7811      0.7750     0.0296  5
  test AUC in-protein         0.4821      0.4701     0.0914  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.5054      0.5286     0.0585  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6592      0.6562     0.0241  5
  test sensitivity            0.7228      0.7368     0.0759  5
  test specificity            0.7646      0.7788     0.0487  5
  test precision              0.6102      0.6207     0.0267  5
  test loss                   0.5751      0.5687     0.0471  5
  FPR (FP/(FP+TN))            0.2354      0.2212     0.0487  5
  FNR (FN/(FN+TP))            0.2772      0.2632     0.0759  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5563      0.5625     0.0559  5
  max valid BA                0.5938      0.6250     0.0938  5
  best valid F1               0.4705      0.5000     0.1278  5
  test BA                     0.4562      0.4375     0.0419  5
  test AUC                    0.4109      0.4297     0.0678  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.4667      0.5000     0.3613  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.1401      0.0000     0.1934  5
  test sensitivity            0.2000      0.0000     0.2878  5
  test specificity            0.7125      0.8750     0.3579  5
  test precision              0.1835      0.2727     0.1589  3
  test loss                   0.6885      0.6924     0.0270  5
  FPR (FP/(FP+TN))            0.2875      0.1250     0.3579  5
  FNR (FN/(FN+TP))            0.8000      1.0000     0.2878  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_drop_ev28_q10 --seeds=0,1,2,3,4`
