# mlp_sub_pb6_keep5_all6

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_keep5_all6'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.8424      0.3171      0.5595      0.6531      0.6545      0.5950
groups_FA                                    5      0.3583      0.8865      0.7068      0.6011      0.4833      0.7444
groups_LPC+LPE+LPG                           5      0.8750      0.6516      0.6299      0.7235      0.8875      0.6067
groups_PA                                    5      0.6308      0.8538      0.6382      0.5295      0.6923      0.8615
groups_PC                                    5      0.3174      0.7228      0.5649      0.6117      0.4294      0.6203
groups_PE                                    5      0.9000      0.7650      0.6466      0.6917      0.9000      0.7875
groups_PG                                    5      0.7719      0.6956      0.6472      0.6277      0.7786      0.6655
groups_PI                                    5      0.6000      0.4375      0.6757      0.5678      0.6750      0.6000
ALL                                         40      0.6620      0.6662      0.6336      0.6258      0.6876      0.6851

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6750      0.6705     0.1144  40
max valid BA                0.6863      0.7074     0.1108  40
best valid F1               0.6090      0.6330     0.1345  40
test BA                     0.6641      0.6518     0.1444  40
test AUC                    0.6441      0.6457     0.2005  40
test AUC in-protein         0.5952      0.5039     0.1556  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.5795      0.5138     0.1416  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.5644      0.5963     0.2148  40
test sensitivity            0.6620      0.7538     0.2870  40
test specificity            0.6662      0.7342     0.2582  40
test precision              0.5474      0.5477     0.1809  40
test loss                   0.6705      0.6766     0.0819  40
FPR (FP/(FP+TN))            0.3338      0.2658     0.2582  40
FNR (FN/(FN+TP))            0.3380      0.2462     0.2870  40

=== abs(sensitivity-specificity) gap: mean=0.3553 median=0.2500 n=40 ===
sensitivity std across seeds (by group): mean=0.1644 median=0.0948 n=8
specificity std across seeds (by group): mean=0.1616 median=0.1512 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5770      0.5886     0.0450  5
  max valid BA                0.6248      0.6314     0.0904  5
  best valid F1               0.6288      0.6286     0.0156  5
  test BA                     0.5797      0.5798     0.0628  5
  test AUC                    0.5598      0.5137     0.2135  5
  test AUC in-protein         0.7145      0.6143     0.2668  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.7414      0.7179     0.2808  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.6265      0.6207     0.0362  5
  test sensitivity            0.8424      0.8182     0.1122  5
  test specificity            0.3171      0.3415     0.1966  5
  test precision              0.5042      0.5000     0.0476  5
  test loss                   0.7745      0.7845     0.0792  5
  FPR (FP/(FP+TN))            0.6829      0.6585     0.1966  5
  FNR (FN/(FN+TP))            0.1576      0.1818     0.1122  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5917      0.5903     0.0134  5
  max valid BA                0.6139      0.5972     0.0395  5
  best valid F1               0.4852      0.4324     0.1354  5
  test BA                     0.6224      0.6273     0.0486  5
  test AUC                    0.5035      0.5231     0.0776  5
  test AUC in-protein         0.5000      0.5000     0.0000  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.5188      0.5000     0.0310  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.4671      0.5000     0.0755  5
  test sensitivity            0.3583      0.3750     0.0632  5
  test specificity            0.8865      0.9189     0.0586  5
  test precision              0.6817      0.7000     0.1267  5
  test loss                   0.6765      0.6860     0.0379  5
  FPR (FP/(FP+TN))            0.1135      0.0811     0.0586  5
  FNR (FN/(FN+TP))            0.6417      0.6250     0.0632  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7404      0.7396     0.0757  5
  max valid BA                0.7471      0.7396     0.0629  5
  best valid F1               0.6803      0.6667     0.0594  5
  test BA                     0.7633      0.8256     0.1149  5
  test AUC                    0.7431      0.8024     0.1354  5
  test AUC in-protein         0.8017      0.8181     0.0868  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.7017      0.6818     0.1005  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.6989      0.7647     0.1137  5
  test sensitivity            0.8750      0.8750     0.0625  5
  test specificity            0.6516      0.7742     0.2071  5
  test precision              0.5924      0.6818     0.1431  5
  test loss                   0.6305      0.5919     0.0771  5
  FPR (FP/(FP+TN))            0.3484      0.2258     0.2071  5
  FNR (FN/(FN+TP))            0.1250      0.1250     0.0625  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7731      0.7692     0.0567  5
  max valid BA                0.7769      0.7692     0.0520  5
  best valid F1               0.7052      0.6957     0.0648  5
  test BA                     0.7423      0.6923     0.1506  5
  test AUC                    0.8402      0.8254     0.0942  5
  test AUC in-protein         0.5000      0.5000     0.0000  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.5000      0.5000     0.0000  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6566      0.5714     0.1938  5
  test sensitivity            0.6308      0.5385     0.2135  5
  test specificity            0.8538      0.9231     0.1371  5
  test precision              0.7087      0.7500     0.2151  5
  test loss                   0.6475      0.6436     0.0129  5
  FPR (FP/(FP+TN))            0.1462      0.0769     0.1371  5
  FNR (FN/(FN+TP))            0.3692      0.4615     0.2135  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5178      0.5061     0.0302  5
  max valid BA                0.5248      0.5079     0.0413  5
  best valid F1               0.4079      0.3710     0.1216  5
  test BA                     0.5201      0.4995     0.0454  5
  test AUC                    0.4512      0.4208     0.0752  5
  test AUC in-protein         0.4979      0.4831     0.0325  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4973      0.5122     0.0346  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.2211      0.0345     0.2712  5
  test sensitivity            0.3174      0.0183     0.4471  5
  test specificity            0.7228      0.9746     0.4153  5
  test precision              0.3226      0.3333     0.1092  5
  test loss                   0.6873      0.6827     0.0083  5
  FPR (FP/(FP+TN))            0.2772      0.0254     0.4153  5
  FNR (FN/(FN+TP))            0.6826      0.9817     0.4471  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8425      0.8438     0.0357  5
  max valid BA                0.8438      0.8438     0.0362  5
  best valid F1               0.7736      0.7778     0.0399  5
  test BA                     0.8325      0.8187     0.0346  5
  test AUC                    0.8690      0.8614     0.0299  5
  test AUC in-protein         0.6501      0.6267     0.0696  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.6665      0.6667     0.0901  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7597      0.7447     0.0394  5
  test sensitivity            0.9000      0.9000     0.0685  5
  test specificity            0.7650      0.7625     0.0541  5
  test precision              0.6599      0.6481     0.0476  5
  test loss                   0.5570      0.5676     0.0266  5
  FPR (FP/(FP+TN))            0.2350      0.2375     0.0541  5
  FNR (FN/(FN+TP))            0.1000      0.1000     0.0685  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7202      0.7201     0.0289  5
  max valid BA                0.7220      0.7201     0.0281  5
  best valid F1               0.6357      0.6308     0.0290  5
  test BA                     0.7338      0.7267     0.0444  5
  test AUC                    0.7646      0.7529     0.0431  5
  test AUC in-protein         0.5051      0.5078     0.0257  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.5098      0.5102     0.0222  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6497      0.6423     0.0497  5
  test sensitivity            0.7719      0.7719     0.0775  5
  test specificity            0.6956      0.7080     0.0586  5
  test precision              0.5632      0.5606     0.0464  5
  test loss                   0.6403      0.6354     0.0281  5
  FPR (FP/(FP+TN))            0.3044      0.2920     0.0586  5
  FNR (FN/(FN+TP))            0.2281      0.2281     0.0775  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6375      0.6250     0.0719  5
  max valid BA                0.6375      0.6250     0.0719  5
  best valid F1               0.5552      0.5600     0.0798  5
  test BA                     0.5188      0.5000     0.1762  5
  test AUC                    0.4211      0.4453     0.1443  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.5000      0.5000     0.0000  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.4357      0.4615     0.2002  5
  test sensitivity            0.6000      0.7500     0.2710  5
  test specificity            0.4375      0.3750     0.1654  5
  test precision              0.3463      0.3333     0.1673  5
  test loss                   0.7508      0.6998     0.0902  5
  FPR (FP/(FP+TN))            0.5625      0.6250     0.1654  5
  FNR (FN/(FN+TP))            0.4000      0.2500     0.2710  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_keep5_all6 --seeds=0,1,2,3,4`
