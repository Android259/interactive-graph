# mlp_sub_pb6_drop_pocket_volume_per_sasa

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_drop_pocket_volume_per_sasa'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.7212      0.2976      0.6349      0.5131      0.6727      0.3900
groups_FA                                    5      0.2500      0.9297      0.5741      0.7787      0.1833      0.9444
groups_LPC+LPE+LPG                           5      0.6000      0.7226      0.7033      0.7101      0.6375      0.7400
groups_PA                                    5      0.6154      0.8538      0.5421      0.7115      0.6154      0.9000
groups_PC                                    5      0.5853      0.4193      0.6611      0.4051      0.6440      0.4071
groups_PE                                    5      0.9150      0.6175      0.7863      0.5764      0.9200      0.6025
groups_PG                                    5      0.7298      0.6283      0.7532      0.5414      0.7536      0.6018
groups_PI                                    5      0.2750      0.6375      0.5673      0.5897      0.5000      0.7500
ALL                                         40      0.5865      0.6383      0.6528      0.6033      0.6158      0.6670

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6349      0.6112     0.1141  40
max valid BA                0.6414      0.6250     0.1171  40
best valid F1               0.5799      0.5847     0.1221  40
test BA                     0.6124      0.5740     0.1299  40
test AUC                    0.6091      0.6149     0.2121  40
test AUC in-protein         0.5816      0.5669     0.2655  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.5248      0.5119     0.2636  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.4914      0.5427     0.2202  40
test sensitivity            0.5865      0.6250     0.3163  40
test specificity            0.6383      0.7662     0.3321  40
test precision              0.5152      0.5433     0.2036  38
test loss                   0.6603      0.6745     0.1012  40
FPR (FP/(FP+TN))            0.3617      0.2338     0.3321  40
FNR (FN/(FN+TP))            0.4135      0.3750     0.3163  40

=== abs(sensitivity-specificity) gap: mean=0.4916 median=0.3711 n=40 ===
sensitivity std across seeds (by group): mean=0.2197 median=0.1870 n=8
specificity std across seeds (by group): mean=0.2627 median=0.3407 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5314      0.5163     0.0409  5
  max valid BA                0.5314      0.5163     0.0409  5
  best valid F1               0.6033      0.6226     0.0500  5
  test BA                     0.5094      0.5033     0.0157  5
  test AUC                    0.3595      0.2668     0.1536  5
  test AUC in-protein         0.3603      0.3529     0.2137  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3227      0.3757     0.2068  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4816      0.6000     0.2696  5
  test sensitivity            0.7212      0.8788     0.4085  5
  test specificity            0.2976      0.1951     0.4009  5
  test precision              0.4529      0.4489     0.0101  4
  test loss                   0.7260      0.7045     0.0382  5
  FPR (FP/(FP+TN))            0.7024      0.8049     0.4009  5
  FNR (FN/(FN+TP))            0.2788      0.1212     0.4085  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5639      0.5625     0.0271  5
  max valid BA                0.5639      0.5625     0.0271  5
  best valid F1               0.4869      0.5714     0.1262  5
  test BA                     0.5899      0.5771     0.0466  5
  test AUC                    0.4950      0.4876     0.1175  5
  test AUC in-protein         0.5667      0.6500     0.3018  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.4407      0.5000     0.2079  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3617      0.3529     0.1133  5
  test sensitivity            0.2500      0.2500     0.0932  5
  test specificity            0.9297      0.9459     0.0242  5
  test precision              0.6865      0.7000     0.0912  5
  test loss                   0.7283      0.7044     0.0936  5
  FPR (FP/(FP+TN))            0.0703      0.0541     0.0242  5
  FNR (FN/(FN+TP))            0.7500      0.7500     0.0932  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6796      0.6875     0.0752  5
  max valid BA                0.6887      0.6979     0.0723  5
  best valid F1               0.6118      0.6207     0.0657  5
  test BA                     0.6613      0.6804     0.0759  5
  test AUC                    0.7486      0.7500     0.1104  5
  test AUC in-protein         0.8012      0.8108     0.1061  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.6680      0.7500     0.1647  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5547      0.6047     0.1032  5
  test sensitivity            0.6000      0.5625     0.2054  5
  test specificity            0.7226      0.6452     0.1685  5
  test precision              0.5614      0.5200     0.1454  5
  test loss                   0.6317      0.6386     0.0822  5
  FPR (FP/(FP+TN))            0.2774      0.3548     0.1685  5
  FNR (FN/(FN+TP))            0.4000      0.4375     0.2054  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7423      0.7500     0.0740  5
  max valid BA                0.7577      0.7500     0.0908  5
  best valid F1               0.6724      0.6667     0.1198  5
  test BA                     0.7346      0.7115     0.0629  5
  test AUC                    0.7959      0.7811     0.0906  5
  test AUC in-protein         0.7292      0.8583     0.3622  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.6149      0.8000     0.3653  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6474      0.6087     0.0825  5
  test sensitivity            0.6154      0.6154     0.0942  5
  test specificity            0.8538      0.8846     0.0996  5
  test precision              0.7006      0.7000     0.1377  5
  test loss                   0.6024      0.5828     0.0346  5
  FPR (FP/(FP+TN))            0.1462      0.1154     0.0996  5
  FNR (FN/(FN+TP))            0.3846      0.3846     0.0942  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5149      0.5031     0.0191  5
  max valid BA                0.5256      0.5161     0.0276  5
  best valid F1               0.4681      0.5238     0.0937  5
  test BA                     0.5023      0.5000     0.0350  5
  test AUC                    0.4481      0.4200     0.0833  5
  test AUC in-protein         0.4745      0.3867     0.2113  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4675      0.4178     0.1716  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3735      0.4795     0.2244  5
  test sensitivity            0.5853      0.6972     0.4064  5
  test specificity            0.4193      0.3299     0.3750  5
  test precision              0.2822      0.3562     0.1605  5
  test loss                   0.7176      0.6992     0.0586  5
  FPR (FP/(FP+TN))            0.5807      0.6701     0.3750  5
  FNR (FN/(FN+TP))            0.4147      0.3028     0.4064  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7600      0.8187     0.1465  5
  max valid BA                0.7612      0.8187     0.1475  5
  best valid F1               0.7014      0.7473     0.1145  5
  test BA                     0.7662      0.8187     0.1498  5
  test AUC                    0.8454      0.8953     0.1571  5
  test AUC in-protein         0.7689      0.8720     0.2297  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7506      0.8442     0.2003  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7087      0.7447     0.1185  5
  test sensitivity            0.9150      0.8750     0.0576  5
  test specificity            0.6175      0.7500     0.3466  5
  test precision              0.5975      0.6481     0.1507  5
  test loss                   0.5335      0.4629     0.1599  5
  FPR (FP/(FP+TN))            0.3825      0.2500     0.3466  5
  FNR (FN/(FN+TP))            0.0850      0.1250     0.0576  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6687      0.7020     0.0974  5
  max valid BA                0.6777      0.7159     0.1015  5
  best valid F1               0.6038      0.6294     0.0657  5
  test BA                     0.6791      0.7140     0.1054  5
  test AUC                    0.7475      0.7635     0.0601  5
  test AUC in-protein         0.4412      0.4642     0.1181  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4408      0.4744     0.1126  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6067      0.6207     0.0719  5
  test sensitivity            0.7298      0.6316     0.1685  5
  test specificity            0.6283      0.7699     0.3519  5
  test precision              0.5537      0.6102     0.1247  5
  test loss                   0.6483      0.6041     0.0979  5
  FPR (FP/(FP+TN))            0.3717      0.2301     0.3519  5
  FNR (FN/(FN+TP))            0.2702      0.3684     0.1685  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6188      0.6250     0.0778  5
  max valid BA                0.6250      0.6250     0.0765  5
  best valid F1               0.4918      0.5455     0.1188  5
  test BA                     0.4562      0.4688     0.0356  5
  test AUC                    0.4328      0.3750     0.1364  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.4933      0.5000     0.4186  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.1967      0.1667     0.2049  5
  test sensitivity            0.2750      0.1250     0.3236  5
  test specificity            0.6375      0.8125     0.3348  5
  test precision              0.2142      0.2721     0.1452  4
  test loss                   0.6943      0.7001     0.0311  5
  FPR (FP/(FP+TN))            0.3625      0.1875     0.3348  5
  FNR (FN/(FN+TP))            0.7250      0.8750     0.3236  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_drop_pocket_volume_per_sasa --seeds=0,1,2,3,4`
