# mlp_sub_pb6_drop_heavy

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_drop_heavy'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.6364      0.3317      0.6827      0.3767      0.6545      0.4050
groups_FA                                    5      0.6250      0.5730      0.5816      0.5993      0.5000      0.6611
groups_LPC+LPE+LPG                           5      0.8750      0.6129      0.6884      0.7210      0.8500      0.6333
groups_PA                                    5      0.5692      0.8615      0.4250      0.7692      0.6154      0.9385
groups_PC                                    5      0.5780      0.4051      0.6745      0.4080      0.6018      0.4203
groups_PE                                    5      0.9400      0.6100      0.8000      0.5742      0.9100      0.6175
groups_PG                                    5      0.7719      0.5947      0.7251      0.5174      0.7929      0.5770
groups_PI                                    5      0.2500      0.6875      0.4822      0.6315      0.4750      0.7125
ALL                                         40      0.6557      0.5845      0.6324      0.5747      0.6750      0.6207

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6353      0.6372     0.1247  40
max valid BA                0.6478      0.6562     0.1262  40
best valid F1               0.5886      0.6226     0.1383  40
test BA                     0.6201      0.6019     0.1376  40
test AUC                    0.6188      0.6323     0.2023  40
test AUC in-protein         0.5603      0.5326     0.2722  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.5514      0.5143     0.2379  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.5147      0.5925     0.2216  40
test sensitivity            0.6557      0.7138     0.3209  40
test specificity            0.5845      0.6991     0.3337  40
test precision              0.4963      0.5217     0.1669  37
test loss                   0.6636      0.6767     0.0902  40
FPR (FP/(FP+TN))            0.4155      0.3009     0.3337  40
FNR (FN/(FN+TP))            0.3443      0.2862     0.3209  40

=== abs(sensitivity-specificity) gap: mean=0.4733 median=0.3595 n=40 ===
sensitivity std across seeds (by group): mean=0.2245 median=0.2175 n=8
specificity std across seeds (by group): mean=0.3002 median=0.3388 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5273      0.5000     0.0531  5
  max valid BA                0.5298      0.5000     0.0527  5
  best valid F1               0.5816      0.6226     0.0700  5
  test BA                     0.4840      0.5000     0.0271  5
  test AUC                    0.3203      0.3052     0.1172  5
  test AUC in-protein         0.3799      0.3168     0.1502  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3140      0.3382     0.1353  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4402      0.5349     0.2575  5
  test sensitivity            0.6364      0.6970     0.4171  5
  test specificity            0.3317      0.2683     0.4105  5
  test precision              0.4290      0.4400     0.0265  4
  test loss                   0.7224      0.7191     0.0275  5
  FPR (FP/(FP+TN))            0.6683      0.7317     0.4105  5
  FNR (FN/(FN+TP))            0.3636      0.3030     0.4171  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5611      0.5347     0.0532  5
  max valid BA                0.5806      0.5625     0.0502  5
  best valid F1               0.5294      0.5854     0.1647  5
  test BA                     0.5990      0.5929     0.0506  5
  test AUC                    0.5563      0.5484     0.1379  5
  test AUC in-protein         0.4083      0.4000     0.4717  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.5777      0.5455     0.1795  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.5220      0.5750     0.1131  5
  test sensitivity            0.6250      0.7083     0.3019  5
  test specificity            0.5730      0.5135     0.3160  5
  test precision              0.5304      0.5263     0.0948  5
  test loss                   0.6826      0.6803     0.0137  5
  FPR (FP/(FP+TN))            0.4270      0.4865     0.3160  5
  FNR (FN/(FN+TP))            0.3750      0.2917     0.3019  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7312      0.7208     0.0497  5
  max valid BA                0.7417      0.7375     0.0403  5
  best valid F1               0.6708      0.6667     0.0425  5
  test BA                     0.7440      0.7107     0.0599  5
  test AUC                    0.7462      0.7399     0.0719  5
  test AUC in-protein         0.8009      0.8229     0.0535  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.7394      0.7625     0.1706  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.6694      0.6383     0.0628  5
  test sensitivity            0.8750      0.8750     0.0765  5
  test specificity            0.6129      0.6452     0.1163  5
  test precision              0.5464      0.5217     0.0774  5
  test loss                   0.6636      0.6690     0.0591  5
  FPR (FP/(FP+TN))            0.3871      0.3548     0.1163  5
  FNR (FN/(FN+TP))            0.1250      0.1250     0.0765  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7462      0.7500     0.1108  5
  max valid BA                0.7769      0.7500     0.0845  5
  best valid F1               0.6991      0.6667     0.1122  5
  test BA                     0.7154      0.7308     0.0370  5
  test AUC                    0.7814      0.7663     0.1032  5
  test AUC in-protein         0.6726      0.8167     0.3159  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.7130      0.7778     0.1984  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6180      0.6364     0.0490  5
  test sensitivity            0.5692      0.5385     0.0421  5
  test specificity            0.8615      0.8846     0.0583  5
  test precision              0.6820      0.7000     0.0900  5
  test loss                   0.6388      0.6361     0.0308  5
  FPR (FP/(FP+TN))            0.1385      0.1154     0.0583  5
  FNR (FN/(FN+TP))            0.4308      0.4615     0.0421  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5092      0.5096     0.0088  5
  max valid BA                0.5111      0.5096     0.0124  5
  best valid F1               0.4473      0.4945     0.0985  5
  test BA                     0.4915      0.4949     0.0211  5
  test AUC                    0.4324      0.4012     0.0699  5
  test AUC in-protein         0.4520      0.3807     0.1974  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4448      0.3934     0.1278  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3532      0.4591     0.2285  5
  test sensitivity            0.5780      0.6697     0.4546  5
  test specificity            0.4051      0.3096     0.4301  5
  test precision              0.2709      0.3493     0.1546  5
  test loss                   0.7187      0.6963     0.0582  5
  FPR (FP/(FP+TN))            0.5949      0.6904     0.4301  5
  FNR (FN/(FN+TP))            0.4220      0.3303     0.4546  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7600      0.8063     0.1474  5
  max valid BA                0.7638      0.8063     0.1501  5
  best valid F1               0.7052      0.7356     0.1183  5
  test BA                     0.7750      0.8125     0.1569  5
  test AUC                    0.8468      0.9009     0.1644  5
  test AUC in-protein         0.7818      0.8438     0.2029  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7372      0.7800     0.1912  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7168      0.7368     0.1263  5
  test sensitivity            0.9400      0.9500     0.0518  5
  test specificity            0.6100      0.7500     0.3421  5
  test precision              0.5957      0.6364     0.1505  5
  test loss                   0.5317      0.4562     0.1606  5
  FPR (FP/(FP+TN))            0.3900      0.2500     0.3421  5
  FNR (FN/(FN+TP))            0.0600      0.0500     0.0518  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6724      0.7067     0.0972  5
  max valid BA                0.6849      0.7287     0.1035  5
  best valid F1               0.6143      0.6393     0.0654  5
  test BA                     0.6833      0.7092     0.1065  5
  test AUC                    0.7442      0.7630     0.0730  5
  test AUC in-protein         0.4668      0.4877     0.0789  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4586      0.4629     0.0570  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6153      0.6212     0.0717  5
  test sensitivity            0.7719      0.7193     0.1330  5
  test specificity            0.5947      0.6991     0.3354  5
  test precision              0.5366      0.5467     0.1207  5
  test loss                   0.6539      0.6173     0.0964  5
  FPR (FP/(FP+TN))            0.4053      0.3009     0.3354  5
  FNR (FN/(FN+TP))            0.2281      0.2807     0.1330  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5750      0.5625     0.0784  5
  max valid BA                0.5938      0.6562     0.0856  5
  best valid F1               0.4608      0.5000     0.1442  5
  test BA                     0.4688      0.4688     0.0383  5
  test AUC                    0.5227      0.5078     0.0640  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.4267      0.3333     0.3752  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.1828      0.1667     0.1891  5
  test sensitivity            0.2500      0.1250     0.3187  5
  test specificity            0.6875      0.8125     0.3928  5
  test precision              0.2786      0.2857     0.0258  3
  test loss                   0.6973      0.6971     0.0528  5
  FPR (FP/(FP+TN))            0.3125      0.1875     0.3928  5
  FNR (FN/(FN+TP))            0.7500      0.8750     0.3187  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_drop_heavy --seeds=0,1,2,3,4`
