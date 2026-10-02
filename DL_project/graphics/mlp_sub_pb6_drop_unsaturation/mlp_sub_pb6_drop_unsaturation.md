# mlp_sub_pb6_drop_unsaturation

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_drop_unsaturation'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.5273      0.4683      0.4725      0.6301      0.4848      0.5500
groups_FA                                    5      0.4750      0.6378      0.6143      0.6825      0.3833      0.7833
groups_LPC+LPE+LPG                           5      0.6875      0.6710      0.6953      0.6704      0.7875      0.6533
groups_PA                                    5      0.6462      0.8538      0.5184      0.7139      0.5846      0.9538
groups_PC                                    5      0.6073      0.3614      0.6678      0.3973      0.6294      0.3827
groups_PE                                    5      0.8500      0.7625      0.6682      0.7224      0.8900      0.7625
groups_PG                                    5      0.6912      0.7593      0.6737      0.7124      0.6857      0.7504
groups_PI                                    5      0.5250      0.4375      0.5728      0.5153      0.7000      0.5250
ALL                                         40      0.6262      0.6190      0.6104      0.6305      0.6432      0.6701

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6474      0.6361     0.1220  40
max valid BA                0.6567      0.6547     0.1236  40
best valid F1               0.5926      0.6077     0.1399  40
test BA                     0.6226      0.5926     0.1365  40
test AUC                    0.6236      0.6689     0.2044  40
test AUC in-protein         0.6044      0.5972     0.2118  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.5564      0.5314     0.1839  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.5118      0.5735     0.2232  40
test sensitivity            0.6262      0.6859     0.3041  40
test specificity            0.6190      0.7562     0.3341  40
test precision              0.5276      0.5339     0.1629  36
test loss                   0.6448      0.6661     0.0868  40
FPR (FP/(FP+TN))            0.3810      0.2437     0.3341  40
FNR (FN/(FN+TP))            0.3738      0.3141     0.3041  40

=== abs(sensitivity-specificity) gap: mean=0.4667 median=0.3740 n=40 ===
sensitivity std across seeds (by group): mean=0.2657 median=0.2475 n=8
specificity std across seeds (by group): mean=0.2688 median=0.2961 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5167      0.5000     0.0373  5
  max valid BA                0.5174      0.5000     0.0369  5
  best valid F1               0.5584      0.5909     0.0772  5
  test BA                     0.4978      0.5000     0.0050  5
  test AUC                    0.4476      0.4368     0.1832  5
  test AUC in-protein         0.4688      0.4271     0.1662  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4388      0.4528     0.1624  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3504      0.5185     0.3224  5
  test sensitivity            0.5273      0.6364     0.5037  5
  test specificity            0.4683      0.3415     0.5050  5
  test precision              0.4431      0.4459     0.0049  3
  test loss                   0.7105      0.6975     0.0284  5
  FPR (FP/(FP+TN))            0.5317      0.6585     0.5050  5
  FNR (FN/(FN+TP))            0.4727      0.3636     0.5037  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5833      0.5625     0.0506  5
  max valid BA                0.5833      0.5625     0.0506  5
  best valid F1               0.5344      0.5823     0.1688  5
  test BA                     0.5564      0.5918     0.0531  5
  test AUC                    0.4847      0.4527     0.1482  5
  test AUC in-protein         0.5792      0.7000     0.2760  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.4346      0.3636     0.1511  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.4149      0.4000     0.1829  5
  test sensitivity            0.4750      0.2917     0.3592  5
  test specificity            0.6378      0.8649     0.3357  5
  test precision              0.4841      0.4490     0.1517  5
  test loss                   0.6975      0.6898     0.0241  5
  FPR (FP/(FP+TN))            0.3622      0.1351     0.3357  5
  FNR (FN/(FN+TP))            0.5250      0.7083     0.3592  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6767      0.6625     0.0976  5
  max valid BA                0.7204      0.7000     0.0678  5
  best valid F1               0.6417      0.6400     0.0843  5
  test BA                     0.6792      0.7117     0.0987  5
  test AUC                    0.7421      0.7510     0.0830  5
  test AUC in-protein         0.8704      0.9144     0.1540  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.7417      0.8235     0.1620  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.6032      0.6364     0.0877  5
  test sensitivity            0.6875      0.6875     0.1326  5
  test specificity            0.6710      0.7419     0.2564  5
  test precision              0.5776      0.5294     0.1794  5
  test loss                   0.6260      0.6240     0.0790  5
  FPR (FP/(FP+TN))            0.3290      0.2581     0.2564  5
  FNR (FN/(FN+TP))            0.3125      0.3125     0.1326  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7615      0.7500     0.0986  5
  max valid BA                0.7692      0.7500     0.0912  5
  best valid F1               0.6854      0.6667     0.1248  5
  test BA                     0.7500      0.7115     0.0892  5
  test AUC                    0.7944      0.7544     0.0857  5
  test AUC in-protein         0.6583      0.6667     0.3167  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.6636      0.6667     0.2457  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6635      0.6154     0.1140  5
  test sensitivity            0.6462      0.6154     0.1595  5
  test specificity            0.8538      0.8462     0.0740  5
  test precision              0.6985      0.7000     0.1336  5
  test loss                   0.6101      0.6325     0.0545  5
  FPR (FP/(FP+TN))            0.1462      0.1538     0.0740  5
  FNR (FN/(FN+TP))            0.3538      0.3846     0.1595  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5050      0.5005     0.0073  5
  max valid BA                0.5060      0.5005     0.0081  5
  best valid F1               0.4289      0.5084     0.1301  5
  test BA                     0.4844      0.5000     0.0363  5
  test AUC                    0.4623      0.4635     0.0423  5
  test AUC in-protein         0.5031      0.5086     0.1271  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.5139      0.5601     0.1128  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3539      0.5082     0.2366  5
  test sensitivity            0.6073      0.8532     0.4712  5
  test specificity            0.3614      0.1675     0.4427  5
  test precision              0.3267      0.3541     0.0602  4
  test loss                   0.7149      0.6978     0.0561  5
  FPR (FP/(FP+TN))            0.6386      0.8325     0.4427  5
  FNR (FN/(FN+TP))            0.3927      0.1468     0.4712  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8200      0.8063     0.0320  5
  max valid BA                0.8263      0.8313     0.0304  5
  best valid F1               0.7536      0.7579     0.0350  5
  test BA                     0.8063      0.8187     0.0500  5
  test AUC                    0.8754      0.9034     0.0647  5
  test AUC in-protein         0.6726      0.6796     0.1594  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.6741      0.7612     0.1810  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7300      0.7447     0.0581  5
  test sensitivity            0.8500      0.8750     0.1000  5
  test specificity            0.7625      0.7750     0.0515  5
  test precision              0.6429      0.6481     0.0465  5
  test loss                   0.5110      0.5322     0.0773  5
  FPR (FP/(FP+TN))            0.2375      0.2250     0.0515  5
  FNR (FN/(FN+TP))            0.1500      0.1250     0.1000  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7100      0.7197     0.0521  5
  max valid BA                0.7181      0.7197     0.0404  5
  best valid F1               0.6257      0.6271     0.0518  5
  test BA                     0.7253      0.7362     0.0255  5
  test AUC                    0.7753      0.7572     0.0469  5
  test AUC in-protein         0.5371      0.5432     0.0823  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.5179      0.5186     0.0294  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6380      0.6481     0.0295  5
  test sensitivity            0.6912      0.6842     0.0640  5
  test specificity            0.7593      0.7434     0.0728  5
  test precision              0.5991      0.5946     0.0622  5
  test loss                   0.5820      0.6002     0.0612  5
  FPR (FP/(FP+TN))            0.2407      0.2566     0.0728  5
  FNR (FN/(FN+TP))            0.3088      0.3158     0.0640  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6062      0.6250     0.0685  5
  max valid BA                0.6125      0.6250     0.0784  5
  best valid F1               0.5129      0.5455     0.1345  5
  test BA                     0.4813      0.4688     0.0568  5
  test AUC                    0.4070      0.4062     0.1149  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.4667      0.5000     0.1514  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.3405      0.4138     0.1914  5
  test sensitivity            0.5250      0.7500     0.3354  5
  test specificity            0.4375      0.1875     0.4122  5
  test precision              0.3365      0.3158     0.0630  4
  test loss                   0.7067      0.6998     0.0309  5
  FPR (FP/(FP+TN))            0.5625      0.8125     0.4122  5
  FNR (FN/(FN+TP))            0.4750      0.2500     0.3354  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_drop_unsaturation --seeds=0,1,2,3,4`
