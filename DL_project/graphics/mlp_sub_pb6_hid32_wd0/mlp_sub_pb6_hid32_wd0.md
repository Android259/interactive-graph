# mlp_sub_pb6_hid32_wd0

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_hid32_wd0'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.3152      0.6878      0.6856      0.7281      0.4667      0.6050
groups_FA                                    5      0.3833      0.7081      0.7457      0.5511      0.4750      0.6667
groups_LPC+LPE+LPG                           5      0.7375      0.7935      0.8492      0.8107      0.6875      0.8600
groups_PA                                    5      0.5538      0.8462      0.6174      0.6914      0.5385      0.9154
groups_PC                                    5      0.1651      0.7868      0.8712      0.8053      0.2587      0.7604
groups_PE                                    5      0.8850      0.7725      0.7614      0.7785      0.9200      0.7675
groups_PG                                    5      0.7088      0.8000      0.7850      0.7863      0.7357      0.7876
groups_PI                                    5      0.2000      0.6625      0.8068      0.6023      0.3750      0.6875
groups_PS+PGP+DAG+TAG                        5      0.6444      0.5067      0.5504      0.5371      0.5250      0.5625
ALL                                         45      0.5104      0.7293      0.7414      0.6990      0.5536      0.7347

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6286      0.5938     0.1289  45
max valid BA                0.6441      0.6250     0.1304  45
best valid F1               0.5471      0.5714     0.1737  45
test BA                     0.6198      0.5962     0.1474  45
test AUC                    0.5977      0.5565     0.2095  45
test AUC in-protein         0.6256      0.6399     0.2208  32
  (proteins averaged)       3.0000      2.0000     3.5162  45
test AUC in-protein (pairs)      0.5728      0.6238     0.2422  45
  (proteins contributing)      5.4444      3.0000     4.0819  45
test F1                     0.4678      0.5556     0.2577  45
test sensitivity            0.5104      0.5625     0.3179  45
test specificity            0.7293      0.7699     0.2175  45
test precision              0.5105      0.5064     0.2370  42
test loss                   0.7490      0.6894     0.3588  45
FPR (FP/(FP+TN))            0.2707      0.2301     0.2175  45
FNR (FN/(FN+TP))            0.4896      0.4375     0.3179  45

=== abs(sensitivity-specificity) gap: mean=0.3991 median=0.3778 n=45 ===
sensitivity std across seeds (by group): mean=0.1882 median=0.1355 n=9
specificity std across seeds (by group): mean=0.1819 median=0.1606 n=9

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5230      0.5246     0.0548  5
  max valid BA                0.5358      0.5246     0.0568  5
  best valid F1               0.5571      0.5957     0.0868  5
  test BA                     0.5015      0.5000     0.0568  5
  test AUC                    0.4670      0.4353     0.0876  5
  test AUC in-protein         0.4565      0.4498     0.1551  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4168      0.3460     0.2089  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3183      0.3214     0.2291  5
  test sensitivity            0.3152      0.2727     0.2577  5
  test specificity            0.6878      0.6585     0.1900  5
  test precision              0.4212      0.4389     0.0995  4
  test loss                   0.8217      0.8522     0.1244  5
  FPR (FP/(FP+TN))            0.3122      0.3415     0.1900  5
  FNR (FN/(FN+TP))            0.6848      0.7273     0.2577  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5556      0.5556     0.0170  5
  max valid BA                0.5708      0.5556     0.0211  5
  best valid F1               0.4332      0.4324     0.1374  5
  test BA                     0.5457      0.5833     0.0670  5
  test AUC                    0.3881      0.4054     0.1089  5
  test AUC in-protein         0.5500      0.6000     0.3226  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.4998      0.5455     0.2169  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3823      0.3256     0.1335  5
  test sensitivity            0.3833      0.2917     0.3025  5
  test specificity            0.7081      0.6757     0.2844  5
  test precision              0.5701      0.4490     0.2798  5
  test loss                   0.7849      0.7255     0.1086  5
  FPR (FP/(FP+TN))            0.2919      0.3243     0.2844  5
  FNR (FN/(FN+TP))            0.6167      0.7083     0.3025  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7450      0.7438     0.0171  5
  max valid BA                0.7737      0.7771     0.0337  5
  best valid F1               0.7004      0.7097     0.0460  5
  test BA                     0.7655      0.7641     0.1022  5
  test AUC                    0.8135      0.7812     0.1003  5
  test AUC in-protein         0.8278      0.8252     0.1387  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.7341      0.7143     0.0910  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.6965      0.6897     0.1321  5
  test sensitivity            0.7375      0.8125     0.1355  5
  test specificity            0.7935      0.7742     0.1606  5
  test precision              0.6793      0.6500     0.1777  5
  test loss                   0.5466      0.5560     0.1524  5
  FPR (FP/(FP+TN))            0.2065      0.2258     0.1606  5
  FNR (FN/(FN+TP))            0.2625      0.1875     0.1355  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7077      0.6923     0.0498  5
  max valid BA                0.7269      0.7500     0.0417  5
  best valid F1               0.6300      0.6667     0.0674  5
  test BA                     0.7000      0.6923     0.0740  5
  test AUC                    0.6367      0.6391     0.0838  5
  test AUC in-protein         0.6542      0.7083     0.3441  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.7061      0.7000     0.2313  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6045      0.5833     0.0919  5
  test sensitivity            0.5538      0.5385     0.0644  5
  test specificity            0.8462      0.8846     0.1586  5
  test precision              0.6976      0.6667     0.1932  5
  test loss                   0.6041      0.5918     0.0529  5
  FPR (FP/(FP+TN))            0.1538      0.1154     0.1586  5
  FNR (FN/(FN+TP))            0.4462      0.4615     0.0644  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4943      0.5000     0.0187  5
  max valid BA                0.5096      0.5046     0.0375  5
  best valid F1               0.3591      0.3191     0.0952  5
  test BA                     0.4760      0.4751     0.0169  5
  test AUC                    0.4009      0.3886     0.0480  5
  test AUC in-protein         0.5951      0.6491     0.0976  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.5898      0.5787     0.0621  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.1946      0.2283     0.1137  5
  test sensitivity            0.1651      0.1927     0.0988  5
  test specificity            0.7868      0.7259     0.1207  5
  test precision              0.2979      0.2963     0.0277  4
  test loss                   1.1600      1.3877     0.4284  5
  FPR (FP/(FP+TN))            0.2132      0.2741     0.1207  5
  FNR (FN/(FN+TP))            0.8349      0.8073     0.0988  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8300      0.8125     0.0475  5
  max valid BA                0.8438      0.8375     0.0372  5
  best valid F1               0.7743      0.7660     0.0437  5
  test BA                     0.8287      0.8375     0.0411  5
  test AUC                    0.8996      0.8962     0.0487  5
  test AUC in-protein         0.7705      0.8659     0.1788  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7765      0.8507     0.1300  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7556      0.7692     0.0448  5
  test sensitivity            0.8850      0.8750     0.0762  5
  test specificity            0.7725      0.7625     0.0205  5
  test precision              0.6600      0.6552     0.0306  5
  test loss                   0.4563      0.4632     0.0424  5
  FPR (FP/(FP+TN))            0.2275      0.2375     0.0205  5
  FNR (FN/(FN+TP))            0.1150      0.1250     0.0762  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7518      0.7467     0.0234  5
  max valid BA                0.7617      0.7512     0.0281  5
  best valid F1               0.6798      0.6667     0.0346  5
  test BA                     0.7544      0.7622     0.0193  5
  test AUC                    0.8237      0.8116     0.0261  5
  test AUC in-protein         0.5561      0.5619     0.1200  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.5388      0.5714     0.1016  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6732      0.6829     0.0245  5
  test sensitivity            0.7088      0.7193     0.0364  5
  test specificity            0.8000      0.8053     0.0213  5
  test precision              0.6417      0.6379     0.0248  5
  test loss                   0.5587      0.5626     0.0585  5
  FPR (FP/(FP+TN))            0.2000      0.1947     0.0213  5
  FNR (FN/(FN+TP))            0.2912      0.2807     0.0364  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5125      0.5000     0.0648  5
  max valid BA                0.5312      0.5000     0.0625  5
  best valid F1               0.3791      0.3636     0.1475  5
  test BA                     0.4313      0.4375     0.0261  5
  test AUC                    0.3766      0.3203     0.0972  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.4733      0.6667     0.3040  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.1328      0.0000     0.1942  5
  test sensitivity            0.2000      0.0000     0.3260  5
  test specificity            0.6625      0.8125     0.3325  5
  test precision              0.1044      0.0000     0.1456  5
  test loss                   1.1114      0.7192     0.7466  5
  FPR (FP/(FP+TN))            0.3375      0.1875     0.3325  5
  FNR (FN/(FN+TP))            0.8000      1.0000     0.3260  5

groups_PS+PGP+DAG+TAG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5375      0.5000     0.0677  5
  max valid BA                0.5437      0.5000     0.0609  5
  best valid F1               0.4107      0.5000     0.1460  5
  test BA                     0.5756      0.5889     0.0585  5
  test AUC                    0.5733      0.5407     0.0829  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.4200      0.5000     0.4266  5
    (proteins contributing)      2.6000      3.0000     0.8944  5
  test F1                     0.4528      0.5600     0.2551  5
  test sensitivity            0.6444      0.7778     0.3960  5
  test specificity            0.5067      0.4000     0.3483  5
  test precision              0.4498      0.4540     0.0466  4
  test loss                   0.6971      0.6932     0.0140  5
  FPR (FP/(FP+TN))            0.4933      0.6000     0.3483  5
  FNR (FN/(FN+TP))            0.3556      0.2222     0.3960  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_hid32_wd0 --seeds=0,1,2,3,4`
