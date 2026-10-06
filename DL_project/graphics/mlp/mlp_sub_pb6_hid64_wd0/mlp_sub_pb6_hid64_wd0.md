# mlp_sub_pb6_hid64_wd0

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_hid64_wd0'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.4182      0.5122      0.8419      0.7893      0.4000      0.6350
groups_FA                                    5      0.2000      0.8324      0.8133      0.7005      0.2167      0.8944
groups_LPC+LPE+LPG                           5      0.6625      0.8581      0.8485      0.8033      0.6750      0.9267
groups_PA                                    5      0.5692      0.7846      0.6319      0.6593      0.5231      0.9231
groups_PC                                    5      0.2294      0.7147      0.9192      0.8619      0.2642      0.7645
groups_PE                                    5      0.8650      0.7900      0.8509      0.8045      0.8700      0.8225
groups_PG                                    5      0.7579      0.7894      0.8756      0.8285      0.7393      0.8000
groups_PI                                    5      0.2250      0.6125      0.7476      0.4845      0.4500      0.5625
groups_PS+PGP+DAG+TAG                        5      0.6000      0.4400      0.7173      0.6580      0.4500      0.5375
ALL                                         45      0.5030      0.7038      0.8051      0.7322      0.5098      0.7629

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6179      0.5625     0.1386  45
max valid BA                0.6364      0.5625     0.1431  45
best valid F1               0.5390      0.5455     0.1920  45
test BA                     0.6034      0.5444     0.1576  45
test AUC                    0.5993      0.5698     0.2166  45
test AUC in-protein         0.6101      0.6654     0.2618  32
  (proteins averaged)       3.0000      2.0000     3.5162  45
test AUC in-protein (pairs)      0.5887      0.6440     0.2463  45
  (proteins contributing)      5.4444      3.0000     4.0819  45
test F1                     0.4677      0.4762     0.2373  45
test sensitivity            0.5030      0.5385     0.2894  45
test specificity            0.7038      0.7750     0.2336  45
test precision              0.4806      0.5000     0.2277  45
test loss                   0.9083      0.6960     0.5690  45
FPR (FP/(FP+TN))            0.2962      0.2250     0.2336  45
FNR (FN/(FN+TP))            0.4970      0.4615     0.2894  45

=== abs(sensitivity-specificity) gap: mean=0.3463 median=0.3029 n=45 ===
sensitivity std across seeds (by group): mean=0.1516 median=0.0877 n=9
specificity std across seeds (by group): mean=0.1596 median=0.1403 n=9

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4891      0.4822     0.0326  5
  max valid BA                0.5175      0.5011     0.0278  5
  best valid F1               0.5620      0.5747     0.0487  5
  test BA                     0.4652      0.4590     0.0650  5
  test AUC                    0.4402      0.4309     0.0820  5
  test AUC in-protein         0.3813      0.3518     0.1439  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3719      0.3382     0.1676  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3620      0.4286     0.2144  5
  test sensitivity            0.4182      0.3939     0.3491  5
  test specificity            0.5122      0.5610     0.2870  5
  test precision              0.3568      0.4054     0.1629  5
  test loss                   0.9055      0.9278     0.1350  5
  FPR (FP/(FP+TN))            0.4878      0.4390     0.2870  5
  FNR (FN/(FN+TP))            0.5818      0.6061     0.3491  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5458      0.5417     0.0135  5
  max valid BA                0.5556      0.5556     0.0098  5
  best valid F1               0.3853      0.4091     0.0950  5
  test BA                     0.5162      0.5158     0.0561  5
  test AUC                    0.3863      0.4077     0.0613  5
  test AUC in-protein         0.4500      0.4833     0.4290  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.4006      0.4286     0.2485  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.2680      0.2703     0.0834  5
  test sensitivity            0.2000      0.2083     0.0801  5
  test specificity            0.8324      0.8649     0.1522  5
  test precision              0.5128      0.4444     0.1864  5
  test loss                   1.6769      1.1958     1.0852  5
  FPR (FP/(FP+TN))            0.1676      0.1351     0.1522  5
  FNR (FN/(FN+TP))            0.8000      0.7917     0.0801  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7654      0.7479     0.0433  5
  max valid BA                0.8008      0.7958     0.0454  5
  best valid F1               0.7435      0.7407     0.0614  5
  test BA                     0.7603      0.7137     0.0826  5
  test AUC                    0.8369      0.7994     0.0830  5
  test AUC in-protein         0.8698      0.8646     0.0356  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.7282      0.7647     0.0714  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.6848      0.6316     0.1161  5
  test sensitivity            0.6625      0.6875     0.1296  5
  test specificity            0.8581      0.9032     0.1108  5
  test precision              0.7260      0.7273     0.1450  5
  test loss                   0.4996      0.5415     0.1186  5
  FPR (FP/(FP+TN))            0.1419      0.0968     0.1108  5
  FNR (FN/(FN+TP))            0.3375      0.3125     0.1296  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6731      0.6731     0.0638  5
  max valid BA                0.7231      0.7500     0.0554  5
  best valid F1               0.6259      0.6667     0.0856  5
  test BA                     0.6769      0.6923     0.0809  5
  test AUC                    0.6822      0.6982     0.0344  5
  test AUC in-protein         0.5435      0.6286     0.4296  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.5971      0.5556     0.2373  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.5763      0.6000     0.0955  5
  test sensitivity            0.5692      0.5385     0.0877  5
  test specificity            0.7846      0.7692     0.1403  5
  test precision              0.6102      0.5714     0.1881  5
  test loss                   0.6192      0.6115     0.0347  5
  FPR (FP/(FP+TN))            0.2154      0.2308     0.1403  5
  FNR (FN/(FN+TP))            0.4308      0.4615     0.0877  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5067      0.5031     0.0173  5
  max valid BA                0.5143      0.5142     0.0119  5
  best valid F1               0.3704      0.3571     0.0770  5
  test BA                     0.4720      0.4833     0.0216  5
  test AUC                    0.4027      0.4192     0.0427  5
  test AUC in-protein         0.6859      0.6716     0.0480  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.6553      0.6672     0.0645  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.2608      0.2857     0.0533  5
  test sensitivity            0.2294      0.2477     0.0577  5
  test specificity            0.7147      0.7208     0.0244  5
  test precision              0.3043      0.3295     0.0446  5
  test loss                   1.6367      1.6572     0.1421  5
  FPR (FP/(FP+TN))            0.2853      0.2792     0.0244  5
  FNR (FN/(FN+TP))            0.7706      0.7523     0.0577  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8300      0.8500     0.0357  5
  max valid BA                0.8463      0.8688     0.0355  5
  best valid F1               0.7822      0.7959     0.0435  5
  test BA                     0.8275      0.8125     0.0445  5
  test AUC                    0.8971      0.8919     0.0481  5
  test AUC in-protein         0.7765      0.8295     0.1212  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7786      0.8000     0.0746  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7566      0.7391     0.0508  5
  test sensitivity            0.8650      0.8500     0.0698  5
  test specificity            0.7900      0.7750     0.0224  5
  test precision              0.6726      0.6538     0.0395  5
  test loss                   0.4151      0.4223     0.0821  5
  FPR (FP/(FP+TN))            0.2100      0.2250     0.0224  5
  FNR (FN/(FN+TP))            0.1350      0.1500     0.0698  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7635      0.7512     0.0207  5
  max valid BA                0.7696      0.7645     0.0214  5
  best valid F1               0.6900      0.6825     0.0273  5
  test BA                     0.7736      0.7666     0.0193  5
  test AUC                    0.8414      0.8367     0.0181  5
  test AUC in-protein         0.5704      0.5706     0.0965  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.5630      0.5782     0.0740  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6964      0.6880     0.0221  5
  test sensitivity            0.7579      0.7368     0.0487  5
  test specificity            0.7894      0.7788     0.0246  5
  test precision              0.6455      0.6364     0.0226  5
  test loss                   0.6015      0.6134     0.0799  5
  FPR (FP/(FP+TN))            0.2106      0.2212     0.0246  5
  FNR (FN/(FN+TP))            0.2421      0.2632     0.0487  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5062      0.5000     0.0513  5
  max valid BA                0.5062      0.5000     0.0513  5
  best valid F1               0.3247      0.3333     0.2067  5
  test BA                     0.4188      0.4375     0.0568  5
  test AUC                    0.3703      0.3516     0.1106  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.3733      0.5000     0.3491  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.1381      0.0000     0.1899  5
  test sensitivity            0.2250      0.0000     0.3112  5
  test specificity            0.6125      0.8750     0.4179  5
  test precision              0.0997      0.0000     0.1369  5
  test loss                   0.9335      0.7265     0.3689  5
  FPR (FP/(FP+TN))            0.3875      0.1250     0.4179  5
  FNR (FN/(FN+TP))            0.7750      1.0000     0.3112  5

groups_PS+PGP+DAG+TAG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4813      0.4688     0.0648  5
  max valid BA                0.4938      0.5000     0.0559  5
  best valid F1               0.3668      0.3333     0.0849  5
  test BA                     0.5200      0.5000     0.0600  5
  test AUC                    0.5363      0.5407     0.1021  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.8300      1.0000     0.2636  5
    (proteins contributing)      2.6000      3.0000     0.8944  5
  test F1                     0.4658      0.4762     0.0736  5
  test sensitivity            0.6000      0.5556     0.2304  5
  test specificity            0.4400      0.5333     0.2565  5
  test precision              0.3977      0.3750     0.0645  5
  test loss                   0.8866      0.8583     0.2059  5
  FPR (FP/(FP+TN))            0.5600      0.4667     0.2565  5
  FNR (FN/(FN+TP))            0.4000      0.4444     0.2304  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_hid64_wd0 --seeds=0,1,2,3,4`
