# mlp_sub_pb6_drop_depth_q10

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_drop_depth_q10'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.5333      0.4488      0.4732      0.5488      0.5273      0.5050
groups_FA                                    5      0.2333      0.8486      0.6259      0.6588      0.3250      0.7722
groups_LPC+LPE+LPG                           5      0.5875      0.6710      0.6854      0.7372      0.7000      0.7133
groups_PA                                    5      0.6308      0.7538      0.6780      0.5903      0.7077      0.7923
groups_PC                                    5      0.3835      0.6406      0.5404      0.6075      0.4055      0.6426
groups_PE                                    5      0.8150      0.8100      0.6444      0.7614      0.8450      0.7825
groups_PG                                    5      0.6982      0.7345      0.6944      0.6782      0.7071      0.7204
groups_PI                                    5      0.3000      0.7000      0.3974      0.7074      0.3000      0.8250
ALL                                         40      0.5227      0.7009      0.5924      0.6612      0.5647      0.7192

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6318      0.6250     0.1148  40
max valid BA                0.6419      0.6406     0.1184  40
best valid F1               0.5582      0.6000     0.1620  40
test BA                     0.6118      0.5734     0.1241  40
test AUC                    0.6056      0.6013     0.1975  40
test AUC in-protein         0.5503      0.5621     0.2383  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.5603      0.5306     0.2082  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.4466      0.5275     0.2526  40
test sensitivity            0.5227      0.5987     0.3417  40
test specificity            0.7009      0.7831     0.2903  40
test precision              0.5117      0.5211     0.1754  35
test loss                   0.6561      0.6766     0.1074  40
FPR (FP/(FP+TN))            0.2991      0.2169     0.2903  40
FNR (FN/(FN+TP))            0.4773      0.4013     0.3417  40

=== abs(sensitivity-specificity) gap: mean=0.4987 median=0.4788 n=40 ===
sensitivity std across seeds (by group): mean=0.2809 median=0.2240 n=8
specificity std across seeds (by group): mean=0.2516 median=0.2130 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5161      0.5000     0.0243  5
  max valid BA                0.5161      0.5000     0.0243  5
  best valid F1               0.5686      0.6226     0.0781  5
  test BA                     0.4911      0.5000     0.0169  5
  test AUC                    0.4339      0.3865     0.0939  5
  test AUC in-protein         0.3849      0.3710     0.0745  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3544      0.3696     0.0646  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3504      0.5333     0.3214  5
  test sensitivity            0.5333      0.7273     0.4973  5
  test specificity            0.4488      0.1951     0.5083  5
  test precision              0.4366      0.4429     0.0136  3
  test loss                   0.7104      0.7012     0.0261  5
  FPR (FP/(FP+TN))            0.5512      0.8049     0.5083  5
  FNR (FN/(FN+TP))            0.4667      0.2727     0.4973  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5306      0.5347     0.0244  5
  max valid BA                0.5486      0.5417     0.0278  5
  best valid F1               0.4737      0.4638     0.1126  5
  test BA                     0.5410      0.5619     0.0307  5
  test AUC                    0.4649      0.3727     0.1840  5
  test AUC in-protein         0.6500      0.8000     0.4435  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.6115      0.5455     0.2247  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.2753      0.3125     0.1832  5
  test sensitivity            0.2333      0.2083     0.2137  5
  test specificity            0.8486      0.9189     0.1789  5
  test precision              0.5365      0.5383     0.1022  4
  test loss                   0.7728      0.6863     0.1815  5
  FPR (FP/(FP+TN))            0.1514      0.0811     0.1789  5
  FNR (FN/(FN+TP))            0.7667      0.7917     0.2137  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6937      0.6833     0.0574  5
  max valid BA                0.7067      0.6833     0.0711  5
  best valid F1               0.6178      0.6275     0.1006  5
  test BA                     0.6292      0.6079     0.0474  5
  test AUC                    0.6946      0.7016     0.0729  5
  test AUC in-protein         0.6652      0.6637     0.0681  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.5947      0.6471     0.1361  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5227      0.5333     0.0665  5
  test sensitivity            0.5875      0.5625     0.2006  5
  test specificity            0.6710      0.8065     0.2471  5
  test precision              0.5291      0.5714     0.1180  5
  test loss                   0.6241      0.6256     0.0968  5
  FPR (FP/(FP+TN))            0.3290      0.1935     0.2471  5
  FNR (FN/(FN+TP))            0.4125      0.4375     0.2006  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7346      0.7115     0.0316  5
  max valid BA                0.7500      0.7500     0.0408  5
  best valid F1               0.6574      0.6667     0.0533  5
  test BA                     0.6923      0.7115     0.1036  5
  test AUC                    0.7438      0.8225     0.1679  5
  test AUC in-protein         0.4649      0.4000     0.3634  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.5569      0.7000     0.2903  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.5934      0.6087     0.1284  5
  test sensitivity            0.6308      0.5385     0.2135  5
  test specificity            0.7538      0.6923     0.1623  5
  test precision              0.5994      0.5417     0.1966  5
  test loss                   0.6343      0.6346     0.0442  5
  FPR (FP/(FP+TN))            0.2462      0.3077     0.1623  5
  FNR (FN/(FN+TP))            0.3692      0.4615     0.2135  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5227      0.5082     0.0325  5
  max valid BA                0.5241      0.5099     0.0315  5
  best valid F1               0.4277      0.5253     0.1535  5
  test BA                     0.5120      0.5006     0.0443  5
  test AUC                    0.4581      0.4701     0.0817  5
  test AUC in-protein         0.5242      0.4502     0.1759  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4863      0.4831     0.1442  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.2580      0.1529     0.2597  5
  test sensitivity            0.3835      0.1101     0.4631  5
  test specificity            0.6406      0.8173     0.3935  5
  test precision              0.2762      0.3636     0.1646  5
  test loss                   0.6969      0.6975     0.0241  5
  FPR (FP/(FP+TN))            0.3594      0.1827     0.3935  5
  FNR (FN/(FN+TP))            0.6165      0.8899     0.4631  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8037      0.7937     0.0428  5
  max valid BA                0.8137      0.8000     0.0329  5
  best valid F1               0.7410      0.7423     0.0343  5
  test BA                     0.8125      0.8438     0.0749  5
  test AUC                    0.8711      0.8956     0.0996  5
  test AUC in-protein         0.7382      0.7173     0.1542  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7047      0.7015     0.1490  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7278      0.7742     0.1031  5
  test sensitivity            0.8150      0.9000     0.2343  5
  test specificity            0.8100      0.7875     0.0958  5
  test precision              0.7103      0.6792     0.1043  5
  test loss                   0.5114      0.4794     0.1032  5
  FPR (FP/(FP+TN))            0.1900      0.2125     0.0958  5
  FNR (FN/(FN+TP))            0.1850      0.1000     0.2343  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7031      0.7110     0.0371  5
  max valid BA                0.7137      0.7110     0.0442  5
  best valid F1               0.6228      0.6179     0.0543  5
  test BA                     0.7164      0.7047     0.0367  5
  test AUC                    0.7565      0.7452     0.0394  5
  test AUC in-protein         0.4504      0.4497     0.0868  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4670      0.4791     0.0731  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6275      0.6176     0.0442  5
  test sensitivity            0.6982      0.7193     0.0649  5
  test specificity            0.7345      0.7611     0.0460  5
  test precision              0.5718      0.5833     0.0435  5
  test loss                   0.6094      0.6076     0.0190  5
  FPR (FP/(FP+TN))            0.2655      0.2389     0.0460  5
  FNR (FN/(FN+TP))            0.3018      0.2807     0.0649  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5000     0.0685  5
  max valid BA                0.5625      0.5312     0.0733  5
  best valid F1               0.3568      0.4615     0.2272  5
  test BA                     0.5000      0.5000     0.0442  5
  test AUC                    0.4219      0.4141     0.0683  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.7067      0.7000     0.2976  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.2173      0.1818     0.2277  5
  test sensitivity            0.3000      0.1250     0.3601  5
  test specificity            0.7000      0.8750     0.3812  5
  test precision              0.3393      0.3333     0.0426  3
  test loss                   0.6896      0.6954     0.0296  5
  FPR (FP/(FP+TN))            0.3000      0.1250     0.3812  5
  FNR (FN/(FN+TP))            0.7000      0.8750     0.3601  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_drop_depth_q10 --seeds=0,1,2,3,4`
