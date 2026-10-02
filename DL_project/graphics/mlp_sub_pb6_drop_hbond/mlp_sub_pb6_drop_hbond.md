# mlp_sub_pb6_drop_hbond

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_drop_hbond'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.5091      0.4878      0.5236      0.5765      0.5030      0.5550
groups_FA                                    5      0.3833      0.7784      0.6358      0.5989      0.4167      0.7611
groups_LPC+LPE+LPG                           5      0.7625      0.5226      0.7538      0.5378      0.8000      0.5333
groups_PA                                    5      0.6154      0.8846      0.5145      0.7291      0.6154      0.9231
groups_PC                                    5      0.5798      0.4152      0.6817      0.3904      0.6257      0.4244
groups_PE                                    5      0.7850      0.7250      0.6051      0.7201      0.7900      0.7825
groups_PG                                    5      0.8070      0.5310      0.6902      0.5325      0.8036      0.5345
groups_PI                                    5      0.2750      0.6500      0.5155      0.6083      0.5000      0.7875
ALL                                         40      0.5896      0.6243      0.6150      0.5867      0.6318      0.6627

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6407      0.6024     0.1184  40
max valid BA                0.6472      0.6438     0.1185  40
best valid F1               0.5833      0.5963     0.1298  40
test BA                     0.6070      0.5315     0.1321  40
test AUC                    0.6056      0.5766     0.1921  40
test AUC in-protein         0.6155      0.6169     0.2131  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.5516      0.5125     0.1873  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.4767      0.5364     0.2345  40
test sensitivity            0.5896      0.7138     0.3331  40
test specificity            0.6243      0.6875     0.3169  40
test precision              0.4792      0.5000     0.1998  37
test loss                   0.6657      0.6776     0.0881  40
FPR (FP/(FP+TN))            0.3757      0.3125     0.3169  40
FNR (FN/(FN+TP))            0.4104      0.2862     0.3331  40

=== abs(sensitivity-specificity) gap: mean=0.4786 median=0.3664 n=40 ===
sensitivity std across seeds (by group): mean=0.2738 median=0.2610 n=8
specificity std across seeds (by group): mean=0.2672 median=0.2992 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5286      0.5152     0.0381  5
  max valid BA                0.5290      0.5152     0.0382  5
  best valid F1               0.5855      0.6226     0.0734  5
  test BA                     0.4984      0.5000     0.0121  5
  test AUC                    0.4223      0.4109     0.1081  5
  test AUC in-protein         0.5310      0.5292     0.1647  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4807      0.4417     0.1726  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3488      0.5591     0.3192  5
  test sensitivity            0.5091      0.7576     0.4740  5
  test specificity            0.4878      0.2683     0.4773  5
  test precision              0.4446      0.4459     0.0107  3
  test loss                   0.7038      0.6961     0.0112  5
  FPR (FP/(FP+TN))            0.5122      0.7317     0.4773  5
  FNR (FN/(FN+TP))            0.4909      0.2424     0.4740  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5708      0.5833     0.0345  5
  max valid BA                0.5889      0.5903     0.0541  5
  best valid F1               0.5155      0.5763     0.1525  5
  test BA                     0.5809      0.5501     0.0599  5
  test AUC                    0.4856      0.4234     0.1340  5
  test AUC in-protein         0.6500      0.8000     0.3226  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.4829      0.5000     0.1156  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.4287      0.4000     0.1149  5
  test sensitivity            0.3833      0.3333     0.1918  5
  test specificity            0.7784      0.7838     0.1626  5
  test precision              0.5710      0.5152     0.1841  5
  test loss                   0.7432      0.7709     0.0669  5
  FPR (FP/(FP+TN))            0.2216      0.2162     0.1626  5
  FNR (FN/(FN+TP))            0.6167      0.6667     0.1918  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6604      0.6937     0.1175  5
  max valid BA                0.6667      0.6937     0.1128  5
  best valid F1               0.6111      0.6111     0.0825  5
  test BA                     0.6425      0.6966     0.1212  5
  test AUC                    0.6913      0.7520     0.1440  5
  test AUC in-protein         0.7309      0.7291     0.0478  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.6149      0.7059     0.2175  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5725      0.6190     0.1172  5
  test sensitivity            0.7625      0.8125     0.2044  5
  test specificity            0.5226      0.6129     0.3012  5
  test precision              0.4764      0.5000     0.1215  5
  test loss                   0.6597      0.6731     0.1027  5
  FPR (FP/(FP+TN))            0.4774      0.3871     0.3012  5
  FNR (FN/(FN+TP))            0.2375      0.1875     0.2044  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7692      0.7500     0.0912  5
  max valid BA                0.7692      0.7500     0.0912  5
  best valid F1               0.6896      0.6667     0.1202  5
  test BA                     0.7500      0.7500     0.0732  5
  test AUC                    0.7627      0.7396     0.0849  5
  test AUC in-protein         0.7792      0.8583     0.2658  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.7376      0.7000     0.2074  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6682      0.6667     0.1015  5
  test sensitivity            0.6154      0.6154     0.0942  5
  test specificity            0.8846      0.8846     0.0720  5
  test precision              0.7376      0.7273     0.1353  5
  test loss                   0.6092      0.6302     0.0422  5
  FPR (FP/(FP+TN))            0.1154      0.1154     0.0720  5
  FNR (FN/(FN+TP))            0.3846      0.3846     0.0942  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5219      0.5254     0.0204  5
  max valid BA                0.5250      0.5254     0.0253  5
  best valid F1               0.4372      0.5253     0.1355  5
  test BA                     0.4975      0.5000     0.0220  5
  test AUC                    0.4254      0.3820     0.0795  5
  test AUC in-protein         0.4643      0.3681     0.2169  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4397      0.4021     0.1334  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3541      0.4813     0.2339  5
  test sensitivity            0.5798      0.7064     0.4624  5
  test specificity            0.4152      0.3198     0.4346  5
  test precision              0.2739      0.3562     0.1568  5
  test loss                   0.7184      0.6975     0.0573  5
  FPR (FP/(FP+TN))            0.5848      0.6802     0.4346  5
  FNR (FN/(FN+TP))            0.4202      0.2936     0.4624  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7850      0.8063     0.0730  5
  max valid BA                0.7863      0.8125     0.0735  5
  best valid F1               0.6920      0.7347     0.1103  5
  test BA                     0.7550      0.7937     0.1401  5
  test AUC                    0.8141      0.8831     0.1956  5
  test AUC in-protein         0.7247      0.7384     0.1667  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7213      0.8060     0.1629  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.6442      0.7129     0.2087  5
  test sensitivity            0.7850      0.9000     0.3175  5
  test specificity            0.7250      0.7250     0.0459  5
  test precision              0.5610      0.5902     0.1159  5
  test loss                   0.5434      0.5129     0.0882  5
  FPR (FP/(FP+TN))            0.2750      0.2750     0.0459  5
  FNR (FN/(FN+TP))            0.2150      0.1000     0.3175  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6584      0.7113     0.0930  5
  max valid BA                0.6690      0.7203     0.0980  5
  best valid F1               0.5968      0.6331     0.0632  5
  test BA                     0.6690      0.7090     0.0954  5
  test AUC                    0.7370      0.7536     0.0706  5
  test AUC in-protein         0.4911      0.4584     0.0657  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4960      0.5034     0.0286  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6009      0.6241     0.0571  5
  test sensitivity            0.8070      0.7719     0.1103  5
  test specificity            0.5310      0.6637     0.2971  5
  test precision              0.4929      0.5238     0.0889  5
  test loss                   0.6498      0.6318     0.0971  5
  FPR (FP/(FP+TN))            0.4690      0.3363     0.2971  5
  FNR (FN/(FN+TP))            0.1930      0.2281     0.1103  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6312      0.5938     0.1022  5
  max valid BA                0.6438      0.6250     0.1073  5
  best valid F1               0.5390      0.5000     0.1219  5
  test BA                     0.4625      0.4375     0.0342  5
  test AUC                    0.5063      0.4688     0.1536  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.4400      0.5000     0.1786  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.1965      0.1538     0.2088  5
  test sensitivity            0.2750      0.1250     0.3354  5
  test specificity            0.6500      0.7500     0.3469  5
  test precision              0.2083      0.2500     0.1500  4
  test loss                   0.6980      0.7003     0.0340  5
  FPR (FP/(FP+TN))            0.3500      0.2500     0.3469  5
  FNR (FN/(FN+TP))            0.7250      0.8750     0.3354  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_drop_hbond --seeds=0,1,2,3,4`
