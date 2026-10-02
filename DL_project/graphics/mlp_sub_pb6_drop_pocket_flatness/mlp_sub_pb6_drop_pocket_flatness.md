# mlp_sub_pb6_drop_pocket_flatness

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_drop_pocket_flatness'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.3515      0.6439      0.4912      0.7027      0.4970      0.6150
groups_FA                                    5      0.2583      0.8865      0.5962      0.6409      0.2417      0.8944
groups_LPC+LPE+LPG                           5      0.5125      0.7613      0.6794      0.7115      0.6500      0.6733
groups_PA                                    5      0.4769      0.8923      0.5852      0.6711      0.5846      0.8462
groups_PC                                    5      0.4037      0.6030      0.6433      0.4179      0.6385      0.4558
groups_PE                                    5      0.9200      0.6225      0.7982      0.5837      0.9100      0.6175
groups_PG                                    5      0.7509      0.6159      0.7754      0.5553      0.7429      0.6124
groups_PI                                    5      0.2500      0.7375      0.5796      0.6158      0.4750      0.6500
ALL                                         40      0.4905      0.7204      0.6436      0.6124      0.5925      0.6706

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6184      0.5816     0.1116  40
max valid BA                0.6315      0.6104     0.1081  40
best valid F1               0.5572      0.5714     0.1291  40
test BA                     0.6054      0.5503     0.1290  40
test AUC                    0.5890      0.5591     0.2073  40
test AUC in-protein         0.6377      0.6475     0.2231  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.5978      0.6201     0.2206  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.4423      0.4915     0.2367  40
test sensitivity            0.4905      0.5076     0.3239  40
test specificity            0.7204      0.7885     0.2968  40
test precision              0.5324      0.5000     0.2046  36
test loss                   0.6486      0.6746     0.1028  40
FPR (FP/(FP+TN))            0.2796      0.2115     0.2968  40
FNR (FN/(FN+TP))            0.5095      0.4924     0.3239  40

=== abs(sensitivity-specificity) gap: mean=0.4928 median=0.4293 n=40 ===
sensitivity std across seeds (by group): mean=0.2266 median=0.1980 n=8
specificity std across seeds (by group): mean=0.2812 median=0.3353 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5179      0.5000     0.0349  5
  max valid BA                0.5560      0.5235     0.0617  5
  best valid F1               0.5667      0.6226     0.1122  5
  test BA                     0.4977      0.5000     0.0125  5
  test AUC                    0.3626      0.3843     0.0774  5
  test AUC in-protein         0.4380      0.5021     0.1397  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3194      0.3611     0.1217  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.2805      0.3200     0.2767  5
  test sensitivity            0.3515      0.2424     0.4202  5
  test specificity            0.6439      0.7805     0.4269  5
  test precision              0.4472      0.4459     0.0228  3
  test loss                   0.7044      0.7049     0.0116  5
  FPR (FP/(FP+TN))            0.3561      0.2195     0.4269  5
  FNR (FN/(FN+TP))            0.6485      0.7576     0.4202  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5556      0.5694     0.0329  5
  max valid BA                0.5681      0.5833     0.0345  5
  best valid F1               0.5052      0.5714     0.0961  5
  test BA                     0.5724      0.5907     0.0748  5
  test AUC                    0.4667      0.3818     0.1514  5
  test AUC in-protein         0.7750      0.8000     0.0739  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.6284      0.5833     0.1665  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3601      0.3333     0.0947  5
  test sensitivity            0.2583      0.2500     0.0801  5
  test specificity            0.8865      0.9459     0.1485  5
  test precision              0.6803      0.7500     0.2049  5
  test loss                   0.7042      0.6970     0.0454  5
  FPR (FP/(FP+TN))            0.1135      0.0541     0.1485  5
  FNR (FN/(FN+TP))            0.7417      0.7500     0.0801  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6396      0.6521     0.0667  5
  max valid BA                0.6617      0.6521     0.0672  5
  best valid F1               0.5766      0.5333     0.0760  5
  test BA                     0.6369      0.6804     0.1031  5
  test AUC                    0.6623      0.7238     0.1810  5
  test AUC in-protein         0.8281      0.8646     0.1107  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.7182      0.7647     0.1125  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5144      0.6047     0.1487  5
  test sensitivity            0.5125      0.5000     0.2044  5
  test specificity            0.7613      0.8387     0.1833  5
  test precision              0.5652      0.4815     0.1982  5
  test loss                   0.6305      0.6661     0.1208  5
  FPR (FP/(FP+TN))            0.2387      0.1613     0.1833  5
  FNR (FN/(FN+TP))            0.4875      0.5000     0.2044  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7115      0.7115     0.0527  5
  max valid BA                0.7154      0.7115     0.0583  5
  best valid F1               0.6124      0.6000     0.0779  5
  test BA                     0.6846      0.6731     0.1067  5
  test AUC                    0.7044      0.7692     0.2409  5
  test AUC in-protein         0.8292      0.8583     0.1734  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.7806      0.8000     0.1438  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.5508      0.5455     0.2018  5
  test sensitivity            0.4769      0.5385     0.1915  5
  test specificity            0.8923      0.9231     0.0958  5
  test precision              0.6889      0.6667     0.1948  5
  test loss                   0.6034      0.6247     0.0674  5
  FPR (FP/(FP+TN))            0.1077      0.0769     0.0958  5
  FNR (FN/(FN+TP))            0.5231      0.4615     0.1915  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5281      0.5121     0.0327  5
  max valid BA                0.5472      0.5182     0.0587  5
  best valid F1               0.4710      0.5253     0.1204  5
  test BA                     0.5034      0.4949     0.0343  5
  test AUC                    0.4588      0.4765     0.0972  5
  test AUC in-protein         0.5055      0.5052     0.2210  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4857      0.5283     0.1852  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3044      0.2667     0.2110  5
  test sensitivity            0.4037      0.2385     0.3950  5
  test specificity            0.6030      0.6954     0.3756  5
  test precision              0.2826      0.3443     0.1626  5
  test loss                   0.7104      0.6880     0.0633  5
  FPR (FP/(FP+TN))            0.3970      0.3046     0.3756  5
  FNR (FN/(FN+TP))            0.5963      0.7615     0.3950  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7638      0.8000     0.1527  5
  max valid BA                0.7638      0.8000     0.1527  5
  best valid F1               0.7053      0.7216     0.1229  5
  test BA                     0.7712      0.8125     0.1556  5
  test AUC                    0.8221      0.8997     0.1959  5
  test AUC in-protein         0.7379      0.7908     0.2115  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7353      0.7910     0.1679  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7143      0.7368     0.1263  5
  test sensitivity            0.9200      0.9500     0.0694  5
  test specificity            0.6225      0.7625     0.3492  5
  test precision              0.6028      0.6471     0.1550  5
  test loss                   0.5301      0.4901     0.1643  5
  FPR (FP/(FP+TN))            0.3775      0.2375     0.3492  5
  FNR (FN/(FN+TP))            0.0800      0.0500     0.0694  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6749      0.7199     0.1001  5
  max valid BA                0.6776      0.7289     0.1018  5
  best valid F1               0.6034      0.6406     0.0662  5
  test BA                     0.6834      0.6963     0.1118  5
  test AUC                    0.7350      0.7451     0.0986  5
  test AUC in-protein         0.4544      0.5320     0.1373  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4545      0.4558     0.1175  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6131      0.6000     0.0836  5
  test sensitivity            0.7509      0.7544     0.1586  5
  test specificity            0.6159      0.7611     0.3447  5
  test precision              0.5470      0.5714     0.1255  5
  test loss                   0.6204      0.5925     0.1177  5
  FPR (FP/(FP+TN))            0.3841      0.2389     0.3447  5
  FNR (FN/(FN+TP))            0.2491      0.2456     0.1586  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5563      0.5625     0.0559  5
  max valid BA                0.5625      0.5625     0.0494  5
  best valid F1               0.4172      0.5000     0.1522  5
  test BA                     0.4938      0.5000     0.0342  5
  test AUC                    0.5000      0.4844     0.0993  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.6600      0.6667     0.3077  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.2006      0.1818     0.2057  5
  test sensitivity            0.2500      0.1250     0.2932  5
  test specificity            0.7375      0.8750     0.3260  5
  test precision              0.3304      0.3333     0.0349  3
  test loss                   0.6854      0.6949     0.0322  5
  FPR (FP/(FP+TN))            0.2625      0.1250     0.3260  5
  FNR (FN/(FN+TP))            0.7500      0.8750     0.2932  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_drop_pocket_flatness --seeds=0,1,2,3,4`
