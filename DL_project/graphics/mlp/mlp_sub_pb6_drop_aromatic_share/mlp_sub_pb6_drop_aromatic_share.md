# mlp_sub_pb6_drop_aromatic_share

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_drop_aromatic_share'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.6424      0.4098      0.6194      0.5157      0.5697      0.5450
groups_FA                                    5      0.3417      0.6973      0.6154      0.5978      0.3750      0.6944
groups_LPC+LPE+LPG                           5      0.6500      0.5226      0.6189      0.6103      0.7875      0.5733
groups_PA                                    5      0.5538      0.8385      0.5628      0.7084      0.5538      0.9154
groups_PC                                    5      0.4239      0.5898      0.6005      0.5456      0.4954      0.5817
groups_PE                                    5      0.9200      0.6125      0.7570      0.5612      0.9150      0.6400
groups_PG                                    5      0.7579      0.5894      0.7075      0.5331      0.7643      0.6000
groups_PI                                    5      0.4500      0.6125      0.5278      0.5295      0.5750      0.5375
ALL                                         40      0.5925      0.6090      0.6262      0.5752      0.6295      0.6359

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6216      0.5712     0.1227  40
max valid BA                0.6327      0.5785     0.1248  40
best valid F1               0.5631      0.5584     0.1420  40
test BA                     0.6008      0.5454     0.1273  40
test AUC                    0.5842      0.5336     0.2034  40
test AUC in-protein         0.5864      0.5646     0.2298  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.5540      0.5095     0.2139  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.4749      0.5090     0.2244  40
test sensitivity            0.5925      0.6458     0.3321  40
test specificity            0.6090      0.7010     0.3127  40
test precision              0.4713      0.4546     0.1749  38
test loss                   0.6719      0.6943     0.0948  40
FPR (FP/(FP+TN))            0.3910      0.2990     0.3127  40
FNR (FN/(FN+TP))            0.4075      0.3542     0.3321  40

=== abs(sensitivity-specificity) gap: mean=0.4738 median=0.3811 n=40 ===
sensitivity std across seeds (by group): mean=0.2874 median=0.3081 n=8
specificity std across seeds (by group): mean=0.3106 median=0.3261 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5414      0.5326     0.0293  5
  max valid BA                0.5573      0.5769     0.0387  5
  best valid F1               0.5334      0.6374     0.1672  5
  test BA                     0.5261      0.5406     0.0310  5
  test AUC                    0.4170      0.4309     0.0554  5
  test AUC in-protein         0.4465      0.4327     0.0984  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3836      0.3889     0.1096  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4816      0.5745     0.2398  5
  test sensitivity            0.6424      0.7576     0.3562  5
  test specificity            0.4098      0.3415     0.3210  5
  test precision              0.4424      0.4769     0.0629  5
  test loss                   0.7014      0.6963     0.0095  5
  FPR (FP/(FP+TN))            0.5902      0.6585     0.3210  5
  FNR (FN/(FN+TP))            0.3576      0.2424     0.3562  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5250      0.5278     0.0206  5
  max valid BA                0.5347      0.5278     0.0311  5
  best valid F1               0.4461      0.4675     0.1391  5
  test BA                     0.5195      0.5096     0.0326  5
  test AUC                    0.4092      0.3750     0.0748  5
  test AUC in-protein         0.7750      0.8000     0.0739  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.6292      0.7273     0.2125  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3013      0.3226     0.2017  5
  test sensitivity            0.3417      0.2083     0.3835  5
  test specificity            0.6973      0.8108     0.4042  5
  test precision              0.4840      0.4142     0.1538  4
  test loss                   0.7277      0.7484     0.0427  5
  FPR (FP/(FP+TN))            0.3027      0.1892     0.4042  5
  FNR (FN/(FN+TP))            0.6583      0.7917     0.3835  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6567      0.6146     0.1358  5
  max valid BA                0.6804      0.6979     0.1291  5
  best valid F1               0.6169      0.6000     0.1097  5
  test BA                     0.5863      0.5413     0.1151  5
  test AUC                    0.7183      0.6875     0.1272  5
  test AUC in-protein         0.6119      0.6682     0.3380  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.5321      0.4545     0.2548  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5001      0.5079     0.1279  5
  test sensitivity            0.6500      0.6250     0.2600  5
  test specificity            0.5226      0.6452     0.2960  5
  test precision              0.4273      0.3889     0.1121  5
  test loss                   0.6785      0.6980     0.1298  5
  FPR (FP/(FP+TN))            0.4774      0.3548     0.2960  5
  FNR (FN/(FN+TP))            0.3500      0.3750     0.2600  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7231      0.7115     0.0752  5
  max valid BA                0.7346      0.7115     0.0916  5
  best valid F1               0.6249      0.6000     0.1219  5
  test BA                     0.6962      0.7500     0.1133  5
  test AUC                    0.7071      0.7929     0.2138  5
  test AUC in-protein         0.7458      0.7000     0.1960  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.6943      0.7000     0.2036  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.5713      0.6667     0.2096  5
  test sensitivity            0.5538      0.6154     0.2516  5
  test specificity            0.8385      0.9231     0.1524  5
  test precision              0.6589      0.5500     0.2120  5
  test loss                   0.6318      0.6281     0.0597  5
  FPR (FP/(FP+TN))            0.1615      0.0769     0.1524  5
  FNR (FN/(FN+TP))            0.4462      0.3846     0.2516  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5289      0.5007     0.0406  5
  max valid BA                0.5386      0.5384     0.0399  5
  best valid F1               0.4568      0.5253     0.1090  5
  test BA                     0.5069      0.4975     0.0318  5
  test AUC                    0.4213      0.4436     0.0906  5
  test AUC in-protein         0.4636      0.4530     0.2149  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4527      0.4648     0.1848  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3081      0.3077     0.2209  5
  test sensitivity            0.4239      0.2752     0.4139  5
  test specificity            0.5898      0.7157     0.3886  5
  test precision              0.2818      0.3488     0.1615  5
  test loss                   0.7132      0.6940     0.0626  5
  FPR (FP/(FP+TN))            0.4102      0.2843     0.3886  5
  FNR (FN/(FN+TP))            0.5761      0.7248     0.4139  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7700      0.8187     0.1556  5
  max valid BA                0.7775      0.8375     0.1592  5
  best valid F1               0.7248      0.7692     0.1339  5
  test BA                     0.7662      0.8375     0.1520  5
  test AUC                    0.8416      0.9100     0.1647  5
  test AUC in-protein         0.7110      0.8250     0.2635  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.6763      0.7532     0.2417  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7082      0.7692     0.1215  5
  test sensitivity            0.9200      0.9250     0.0597  5
  test specificity            0.6125      0.7625     0.3440  5
  test precision              0.5936      0.6667     0.1501  5
  test loss                   0.5614      0.5068     0.1559  5
  FPR (FP/(FP+TN))            0.3875      0.2375     0.3440  5
  FNR (FN/(FN+TP))            0.0800      0.0750     0.0597  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6777      0.7243     0.1033  5
  max valid BA                0.6821      0.7422     0.1056  5
  best valid F1               0.6090      0.6560     0.0721  5
  test BA                     0.6736      0.7530     0.1169  5
  test AUC                    0.7076      0.7611     0.1241  5
  test AUC in-protein         0.4257      0.3828     0.0933  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4638      0.4149     0.1137  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.5971      0.6714     0.1055  5
  test sensitivity            0.7579      0.7719     0.2032  5
  test specificity            0.5894      0.7434     0.3312  5
  test precision              0.5200      0.5663     0.1133  5
  test loss                   0.6579      0.6095     0.0989  5
  FPR (FP/(FP+TN))            0.4106      0.2566     0.3312  5
  FNR (FN/(FN+TP))            0.2421      0.2281     0.2032  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5312     0.0474  5
  max valid BA                0.5563      0.5312     0.0601  5
  best valid F1               0.4929      0.5000     0.0722  5
  test BA                     0.5312      0.5312     0.0856  5
  test AUC                    0.4516      0.4141     0.1021  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.6000      0.5000     0.2528  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.3315      0.4545     0.2456  5
  test sensitivity            0.4500      0.6250     0.3708  5
  test specificity            0.6125      0.5625     0.2476  5
  test precision              0.3381      0.3845     0.1174  4
  test loss                   0.7029      0.7015     0.0369  5
  FPR (FP/(FP+TN))            0.3875      0.4375     0.2476  5
  FNR (FN/(FN+TP))            0.5500      0.3750     0.3708  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_drop_aromatic_share --seeds=0,1,2,3,4`
