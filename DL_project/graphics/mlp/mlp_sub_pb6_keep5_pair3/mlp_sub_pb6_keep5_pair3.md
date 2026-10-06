# mlp_sub_pb6_keep5_pair3

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_keep5_pair3'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.6545      0.4244      0.5609      0.6453      0.6667      0.4750
groups_FA                                    5      0.5083      0.7081      0.6358      0.6661      0.3583      0.8833
groups_LPC+LPE+LPG                           5      0.6375      0.6774      0.6957      0.7049      0.6625      0.6933
groups_PA                                    5      0.5538      0.8769      0.6842      0.5775      0.5231      0.9308
groups_PC                                    5      0.3615      0.7695      0.5139      0.6805      0.3156      0.8325
groups_PE                                    5      0.8050      0.7500      0.6574      0.6780      0.8900      0.7425
groups_PG                                    5      0.7404      0.6460      0.5992      0.6558      0.7750      0.6319
groups_PI                                    5      0.6250      0.7000      0.6463      0.6599      0.8000      0.6000
ALL                                         40      0.6108      0.6941      0.6242      0.6585      0.6239      0.7237

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6677      0.6740     0.0945  40
max valid BA                0.6738      0.6781     0.0908  40
best valid F1               0.5932      0.6088     0.1129  40
test BA                     0.6524      0.6522     0.0963  40
test AUC                    0.6311      0.6283     0.1490  40
test AUC in-protein         0.5470      0.5039     0.1451  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.5365      0.5000     0.1366  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.5531      0.5746     0.1585  40
test sensitivity            0.6108      0.6202     0.2090  40
test specificity            0.6941      0.6965     0.2077  40
test precision              0.5621      0.5196     0.1341  38
test loss                   0.6663      0.6768     0.0801  40
FPR (FP/(FP+TN))            0.3059      0.3035     0.2077  40
FNR (FN/(FN+TP))            0.3892      0.3798     0.2090  40

=== abs(sensitivity-specificity) gap: mean=0.2806 median=0.2356 n=40 ===
sensitivity std across seeds (by group): mean=0.1463 median=0.1002 n=8
specificity std across seeds (by group): mean=0.1589 median=0.1556 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5483      0.5386     0.0501  5
  max valid BA                0.5708      0.5500     0.0595  5
  best valid F1               0.6001      0.6471     0.0812  5
  test BA                     0.5395      0.5092     0.0911  5
  test AUC                    0.4500      0.4656     0.0394  5
  test AUC in-protein         0.4058      0.5000     0.2095  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4673      0.6173     0.2602  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4846      0.6024     0.2769  5
  test sensitivity            0.6545      0.7576     0.3776  5
  test specificity            0.4244      0.3902     0.3753  5
  test precision              0.4861      0.4754     0.0773  4
  test loss                   0.7991      0.8353     0.0950  5
  FPR (FP/(FP+TN))            0.5756      0.6098     0.3753  5
  FNR (FN/(FN+TP))            0.3455      0.2424     0.3776  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6167      0.5972     0.0676  5
  max valid BA                0.6208      0.5972     0.0680  5
  best valid F1               0.5055      0.4762     0.1482  5
  test BA                     0.6082      0.6222     0.0583  5
  test AUC                    0.5747      0.5698     0.0293  5
  test AUC in-protein         0.5208      0.5000     0.0417  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.4766      0.5000     0.0788  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.5223      0.5366     0.0256  5
  test sensitivity            0.5083      0.5417     0.0685  5
  test specificity            0.7081      0.7027     0.1807  5
  test precision              0.5702      0.5417     0.1408  5
  test loss                   0.6719      0.6905     0.0372  5
  FPR (FP/(FP+TN))            0.2919      0.2973     0.1807  5
  FNR (FN/(FN+TP))            0.4917      0.4583     0.0685  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6713      0.6479     0.0615  5
  max valid BA                0.6779      0.6646     0.0565  5
  best valid F1               0.5906      0.5625     0.0694  5
  test BA                     0.6575      0.6482     0.0684  5
  test AUC                    0.6796      0.6552     0.1085  5
  test AUC in-protein         0.7508      0.8175     0.1842  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.6799      0.7500     0.1844  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5587      0.5778     0.0950  5
  test sensitivity            0.6375      0.6875     0.1896  5
  test specificity            0.6774      0.7097     0.1707  5
  test precision              0.5242      0.4643     0.1084  5
  test loss                   0.6282      0.6364     0.0592  5
  FPR (FP/(FP+TN))            0.3226      0.2903     0.1707  5
  FNR (FN/(FN+TP))            0.3625      0.3125     0.1896  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7269      0.7115     0.0394  5
  max valid BA                0.7269      0.7115     0.0394  5
  best valid F1               0.6301      0.6000     0.0627  5
  test BA                     0.7154      0.7115     0.0798  5
  test AUC                    0.7089      0.6864     0.1653  5
  test AUC in-protein         0.5000      0.5000     0.0000  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.5000      0.5000     0.0000  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6235      0.6087     0.1052  5
  test sensitivity            0.5538      0.5385     0.0644  5
  test specificity            0.8769      0.9231     0.1287  5
  test precision              0.7331      0.7500     0.1853  5
  test loss                   0.6244      0.6476     0.0577  5
  FPR (FP/(FP+TN))            0.1231      0.0769     0.1287  5
  FNR (FN/(FN+TP))            0.4462      0.4615     0.0644  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5670      0.5783     0.0390  5
  max valid BA                0.5740      0.5944     0.0429  5
  best valid F1               0.4451      0.5060     0.1191  5
  test BA                     0.5655      0.5837     0.0382  5
  test AUC                    0.4696      0.4596     0.0427  5
  test AUC in-protein         0.5187      0.5234     0.0375  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4939      0.5020     0.0325  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3632      0.4667     0.2055  5
  test sensitivity            0.3615      0.4495     0.2220  5
  test specificity            0.7695      0.7360     0.1687  5
  test precision              0.4797      0.4727     0.0591  4
  test loss                   0.6924      0.6913     0.0171  5
  FPR (FP/(FP+TN))            0.2305      0.2640     0.1687  5
  FNR (FN/(FN+TP))            0.6385      0.5505     0.2220  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8163      0.8313     0.0244  5
  max valid BA                0.8163      0.8313     0.0244  5
  best valid F1               0.7403      0.7579     0.0275  5
  test BA                     0.7775      0.8000     0.0473  5
  test AUC                    0.8320      0.8455     0.0350  5
  test AUC in-protein         0.6501      0.6267     0.0696  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.6626      0.6667     0.0976  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.6995      0.7253     0.0539  5
  test sensitivity            0.8050      0.8250     0.0481  5
  test specificity            0.7500      0.7625     0.0523  5
  test precision              0.6191      0.6415     0.0588  5
  test loss                   0.5701      0.5622     0.0421  5
  FPR (FP/(FP+TN))            0.2500      0.2375     0.0523  5
  FNR (FN/(FN+TP))            0.1950      0.1750     0.0481  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6954      0.7156     0.0364  5
  max valid BA                0.7034      0.7201     0.0426  5
  best valid F1               0.6177      0.6316     0.0398  5
  test BA                     0.6932      0.6913     0.0383  5
  test AUC                    0.7612      0.7765     0.0353  5
  test AUC in-protein         0.5091      0.5078     0.0276  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.5121      0.5136     0.0313  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6037      0.6069     0.0485  5
  test sensitivity            0.7404      0.7719     0.1119  5
  test specificity            0.6460      0.6195     0.0524  5
  test precision              0.5132      0.5079     0.0233  5
  test loss                   0.6444      0.6656     0.0450  5
  FPR (FP/(FP+TN))            0.3540      0.3805     0.0524  5
  FNR (FN/(FN+TP))            0.2596      0.2281     0.1119  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7000      0.7188     0.0568  5
  max valid BA                0.7000      0.7188     0.0568  5
  best valid F1               0.6164      0.6316     0.0555  5
  test BA                     0.6625      0.6562     0.0895  5
  test AUC                    0.5727      0.5391     0.0815  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.5000      0.5000     0.0000  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.5692      0.5556     0.1066  5
  test sensitivity            0.6250      0.6250     0.0884  5
  test specificity            0.7000      0.6875     0.1425  5
  test precision              0.5391      0.5000     0.1750  5
  test loss                   0.6997      0.6944     0.0268  5
  FPR (FP/(FP+TN))            0.3000      0.3125     0.1425  5
  FNR (FN/(FN+TP))            0.3750      0.3750     0.0884  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_keep5_pair3 --seeds=0,1,2,3,4`
