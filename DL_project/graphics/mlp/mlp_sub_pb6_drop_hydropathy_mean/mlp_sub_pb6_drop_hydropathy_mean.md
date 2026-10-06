# mlp_sub_pb6_drop_hydropathy_mean

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_drop_hydropathy_mean'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.5636      0.4683      0.5268      0.5919      0.5576      0.5400
groups_FA                                    5      0.2833      0.8432      0.5655      0.7899      0.2083      0.8944
groups_LPC+LPE+LPG                           5      0.6125      0.6645      0.7508      0.7210      0.6375      0.6867
groups_PA                                    5      0.5692      0.8308      0.6214      0.6668      0.6308      0.8692
groups_PC                                    5      0.5780      0.4162      0.5245      0.5325      0.4624      0.5685
groups_PE                                    5      0.8000      0.8100      0.6581      0.7697      0.8200      0.8200
groups_PG                                    5      0.6211      0.7628      0.7282      0.7235      0.6607      0.7345
groups_PI                                    5      0.2250      0.6875      0.4126      0.6290      0.4000      0.6750
ALL                                         40      0.5316      0.6854      0.5985      0.6780      0.5472      0.7235

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6229      0.5760     0.1132  40
max valid BA                0.6354      0.6125     0.1145  40
best valid F1               0.5466      0.5801     0.1694  40
test BA                     0.6085      0.5721     0.1260  40
test AUC                    0.5983      0.5753     0.1935  40
test AUC in-protein         0.5492      0.5272     0.2239  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.5284      0.5069     0.1876  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.4699      0.5253     0.2225  40
test sensitivity            0.5316      0.5044     0.3045  40
test specificity            0.6854      0.7746     0.3008  40
test precision              0.5109      0.5172     0.2018  37
test loss                   0.6518      0.6733     0.1024  40
FPR (FP/(FP+TN))            0.3146      0.2254     0.3008  40
FNR (FN/(FN+TP))            0.4684      0.4956     0.3045  40

=== abs(sensitivity-specificity) gap: mean=0.4556 median=0.3586 n=40 ===
sensitivity std across seeds (by group): mean=0.2258 median=0.2009 n=8
specificity std across seeds (by group): mean=0.2330 median=0.1888 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5256      0.5318     0.0247  5
  max valid BA                0.5488      0.5318     0.0643  5
  best valid F1               0.5811      0.6226     0.0663  5
  test BA                     0.5160      0.5000     0.0329  5
  test AUC                    0.4600      0.5092     0.0919  5
  test AUC in-protein         0.4750      0.4960     0.1045  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3743      0.3353     0.1134  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4330      0.4839     0.2499  5
  test sensitivity            0.5636      0.4545     0.4035  5
  test specificity            0.4683      0.6341     0.4306  5
  test precision              0.4745      0.4730     0.0403  4
  test loss                   0.7077      0.6964     0.0283  5
  FPR (FP/(FP+TN))            0.5317      0.3659     0.4306  5
  FNR (FN/(FN+TP))            0.4364      0.5455     0.4035  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5458      0.5417     0.0248  5
  max valid BA                0.5514      0.5486     0.0233  5
  best valid F1               0.4508      0.4789     0.1331  5
  test BA                     0.5633      0.5659     0.0405  5
  test AUC                    0.4392      0.3806     0.1201  5
  test AUC in-protein         0.4417      0.4833     0.4193  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.4143      0.4545     0.1582  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3706      0.3889     0.0644  5
  test sensitivity            0.2833      0.2917     0.0618  5
  test specificity            0.8432      0.8378     0.0700  5
  test precision              0.5556      0.5000     0.1375  5
  test loss                   0.7460      0.6929     0.1229  5
  FPR (FP/(FP+TN))            0.1568      0.1622     0.0700  5
  FNR (FN/(FN+TP))            0.7167      0.7083     0.0618  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6496      0.6354     0.0757  5
  max valid BA                0.6621      0.6354     0.0720  5
  best valid F1               0.5740      0.5517     0.0967  5
  test BA                     0.6385      0.6371     0.1070  5
  test AUC                    0.6800      0.6694     0.0781  5
  test AUC in-protein         0.7533      0.8032     0.1639  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.6381      0.7000     0.1553  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5414      0.5161     0.1142  5
  test sensitivity            0.6125      0.5000     0.1896  5
  test specificity            0.6645      0.7097     0.2086  5
  test precision              0.5122      0.5333     0.1331  5
  test loss                   0.6388      0.6330     0.0729  5
  FPR (FP/(FP+TN))            0.3355      0.2903     0.2086  5
  FNR (FN/(FN+TP))            0.3875      0.5000     0.1896  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7346      0.7500     0.0417  5
  max valid BA                0.7500      0.7500     0.0236  5
  best valid F1               0.6658      0.6667     0.0400  5
  test BA                     0.7000      0.6923     0.0617  5
  test AUC                    0.7497      0.7633     0.1157  5
  test AUC in-protein         0.6077      0.5571     0.2537  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.6875      0.7143     0.1111  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6040      0.5833     0.0746  5
  test sensitivity            0.5692      0.5385     0.0877  5
  test specificity            0.8308      0.8846     0.1690  5
  test precision              0.6808      0.7000     0.1689  5
  test loss                   0.6215      0.6244     0.0477  5
  FPR (FP/(FP+TN))            0.1692      0.1154     0.1690  5
  FNR (FN/(FN+TP))            0.4308      0.4615     0.0877  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5134      0.5000     0.0292  5
  max valid BA                0.5155      0.5018     0.0302  5
  best valid F1               0.4245      0.5253     0.1523  5
  test BA                     0.4971      0.4983     0.0042  5
  test AUC                    0.4267      0.4547     0.0908  5
  test AUC in-protein         0.4146      0.4177     0.1354  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.3900      0.3977     0.1056  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3117      0.5079     0.2846  5
  test sensitivity            0.5780      0.8899     0.5295  5
  test specificity            0.4162      0.1066     0.5232  5
  test precision              0.2135      0.3553     0.1949  5
  test loss                   0.7235      0.6977     0.0637  5
  FPR (FP/(FP+TN))            0.5838      0.8934     0.5232  5
  FNR (FN/(FN+TP))            0.4220      0.1101     0.5295  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8100      0.8000     0.0389  5
  max valid BA                0.8200      0.8125     0.0427  5
  best valid F1               0.7505      0.7368     0.0450  5
  test BA                     0.8050      0.8187     0.0664  5
  test AUC                    0.8649      0.8991     0.1154  5
  test AUC in-protein         0.7296      0.7076     0.1232  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.6761      0.6716     0.1526  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7225      0.7447     0.0894  5
  test sensitivity            0.8000      0.8750     0.2121  5
  test specificity            0.8100      0.7750     0.0974  5
  test precision              0.7069      0.6727     0.1117  5
  test loss                   0.4968      0.4673     0.1162  5
  FPR (FP/(FP+TN))            0.1900      0.2250     0.0974  5
  FNR (FN/(FN+TP))            0.2000      0.1250     0.2121  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6851      0.6889     0.0118  5
  max valid BA                0.6976      0.6933     0.0134  5
  best valid F1               0.6008      0.6000     0.0191  5
  test BA                     0.6919      0.6833     0.0439  5
  test AUC                    0.7537      0.7690     0.0411  5
  test AUC in-protein         0.4537      0.4406     0.0744  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4605      0.4800     0.0623  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.5919      0.5789     0.0572  5
  test sensitivity            0.6211      0.5965     0.0982  5
  test specificity            0.7628      0.7876     0.0494  5
  test precision              0.5702      0.5789     0.0438  5
  test loss                   0.5922      0.5847     0.0356  5
  FPR (FP/(FP+TN))            0.2372      0.2124     0.0494  5
  FNR (FN/(FN+TP))            0.3789      0.4035     0.0982  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5188      0.5000     0.0280  5
  max valid BA                0.5375      0.5312     0.0407  5
  best valid F1               0.3251      0.4211     0.2319  5
  test BA                     0.4562      0.4688     0.0648  5
  test AUC                    0.4125      0.4219     0.0893  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.5867      0.6000     0.2765  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.1841      0.2667     0.1741  5
  test sensitivity            0.2250      0.2500     0.2236  5
  test specificity            0.6875      0.6875     0.3156  5
  test precision              0.2692      0.2857     0.0488  3
  test loss                   0.6878      0.6923     0.0318  5
  FPR (FP/(FP+TN))            0.3125      0.3125     0.3156  5
  FNR (FN/(FN+TP))            0.7750      0.7500     0.2236  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_drop_hydropathy_mean --seeds=0,1,2,3,4`
