# mlp_sub_pb6

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.6667      0.3268      0.5366      0.6939      0.5697      0.5150
groups_FA                                    5      0.5167      0.6649      0.6747      0.5808      0.5083      0.6444
groups_LPC+LPE+LPG                           5      0.5375      0.8000      0.7379      0.7640      0.5125      0.7800
groups_PA                                    5      0.5692      0.7769      0.6105      0.6952      0.5385      0.8923
groups_PC                                    5      0.2899      0.6985      0.5611      0.5629      0.3064      0.7127
groups_PE                                    5      0.8950      0.7875      0.7639      0.7445      0.8850      0.7700
groups_PG                                    5      0.6842      0.7735      0.7029      0.7057      0.6857      0.7788
groups_PI                                    5      0.3500      0.6625      0.4738      0.6637      0.4750      0.6875
groups_PS+PGP+DAG+TAG                        5      0.5333      0.5600      0.4441      0.7438      0.3500      0.7625
ALL                                         45      0.5603      0.6723      0.6117      0.6838      0.5368      0.7270

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6186      0.5625     0.1273  45
max valid BA                0.6319      0.5962     0.1238  45
best valid F1               0.5247      0.5714     0.1857  45
test BA                     0.6163      0.6115     0.1268  45
test AUC                    0.6012      0.5968     0.1940  45
test AUC in-protein         0.6442      0.6250     0.2103  32
  (proteins averaged)       3.0000      2.0000     3.5162  45
test AUC in-protein (pairs)      0.5690      0.5950     0.2220  45
  (proteins contributing)      5.4444      3.0000     4.0819  45
test F1                     0.4945      0.5455     0.2081  45
test sensitivity            0.5603      0.5625     0.2917  45
test specificity            0.6723      0.7750     0.2917  45
test precision              0.5312      0.5311     0.1571  42
test loss                   0.6426      0.6825     0.0853  45
FPR (FP/(FP+TN))            0.3277      0.2250     0.2917  45
FNR (FN/(FN+TP))            0.4397      0.4375     0.2917  45

=== abs(sensitivity-specificity) gap: mean=0.4084 median=0.3407 n=45 ===
sensitivity std across seeds (by group): mean=0.2226 median=0.2710 n=9
specificity std across seeds (by group): mean=0.2439 median=0.2863 n=9

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4933      0.5000     0.0594  5
  max valid BA                0.5423      0.5318     0.0757  5
  best valid F1               0.5877      0.6154     0.0515  5
  test BA                     0.4967      0.4945     0.0228  5
  test AUC                    0.4341      0.4183     0.0720  5
  test AUC in-protein         0.4766      0.5188     0.0937  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4626      0.4135     0.1637  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5143      0.5455     0.0929  5
  test sensitivity            0.6667      0.7273     0.2710  5
  test specificity            0.3268      0.2439     0.2863  5
  test precision              0.4483      0.4426     0.0310  5
  test loss                   0.7004      0.7009     0.0043  5
  FPR (FP/(FP+TN))            0.6732      0.7561     0.2863  5
  FNR (FN/(FN+TP))            0.3333      0.2727     0.2710  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5708      0.5417     0.0948  5
  max valid BA                0.5764      0.5556     0.0927  5
  best valid F1               0.4437      0.3429     0.1881  5
  test BA                     0.5908      0.6115     0.0805  5
  test AUC                    0.5101      0.4842     0.1923  5
  test AUC in-protein         0.7750      0.7500     0.1792  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.5801      0.5714     0.0815  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.4641      0.4706     0.1597  5
  test sensitivity            0.5167      0.3333     0.3745  5
  test specificity            0.6649      0.8649     0.4097  5
  test precision              0.6071      0.5405     0.2099  5
  test loss                   0.6951      0.7048     0.0267  5
  FPR (FP/(FP+TN))            0.3351      0.1351     0.4097  5
  FNR (FN/(FN+TP))            0.4833      0.6667     0.3745  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6358      0.6354     0.1371  5
  max valid BA                0.6462      0.6354     0.1230  5
  best valid F1               0.5527      0.5333     0.1284  5
  test BA                     0.6688      0.6825     0.0492  5
  test AUC                    0.7381      0.7460     0.0965  5
  test AUC in-protein         0.8160      0.8542     0.1023  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.6058      0.7000     0.2390  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5578      0.5714     0.0674  5
  test sensitivity            0.5375      0.5625     0.1135  5
  test specificity            0.8000      0.8710     0.1278  5
  test precision              0.6114      0.6667     0.1215  5
  test loss                   0.5940      0.6081     0.1000  5
  FPR (FP/(FP+TN))            0.2000      0.1290     0.1278  5
  FNR (FN/(FN+TP))            0.4625      0.4375     0.1135  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7077      0.7500     0.0786  5
  max valid BA                0.7154      0.7500     0.0737  5
  best valid F1               0.6291      0.6667     0.0861  5
  test BA                     0.6731      0.6923     0.0608  5
  test AUC                    0.6568      0.6391     0.1124  5
  test AUC in-protein         0.7000      0.8000     0.3830  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.6812      0.6667     0.2782  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.5717      0.5714     0.0554  5
  test sensitivity            0.5692      0.5385     0.0877  5
  test specificity            0.7769      0.8462     0.1853  5
  test precision              0.6093      0.6667     0.1448  5
  test loss                   0.6564      0.6497     0.0360  5
  FPR (FP/(FP+TN))            0.2231      0.1538     0.1853  5
  FNR (FN/(FN+TP))            0.4308      0.4615     0.0877  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5017      0.5000     0.0199  5
  max valid BA                0.5096      0.5042     0.0256  5
  best valid F1               0.3095      0.2301     0.1402  5
  test BA                     0.4942      0.4969     0.0086  5
  test AUC                    0.5329      0.5375     0.1043  5
  test AUC in-protein         0.6104      0.6501     0.0874  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.5880      0.5950     0.0135  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.2235      0.2471     0.2004  5
  test sensitivity            0.2899      0.1927     0.4064  5
  test specificity            0.6985      0.7970     0.3998  5
  test precision              0.3224      0.3467     0.0552  4
  test loss                   0.6869      0.6880     0.0219  5
  FPR (FP/(FP+TN))            0.3015      0.2030     0.3998  5
  FNR (FN/(FN+TP))            0.7101      0.8073     0.4064  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8213      0.8187     0.0338  5
  max valid BA                0.8275      0.8187     0.0341  5
  best valid F1               0.7542      0.7423     0.0368  5
  test BA                     0.8413      0.8250     0.0432  5
  test AUC                    0.9023      0.8916     0.0415  5
  test AUC in-protein         0.7722      0.8295     0.1217  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7653      0.7800     0.0797  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7714      0.7527     0.0495  5
  test sensitivity            0.8950      0.8750     0.0647  5
  test specificity            0.7875      0.7750     0.0331  5
  test precision              0.6784      0.6735     0.0443  5
  test loss                   0.4672      0.4604     0.0356  5
  FPR (FP/(FP+TN))            0.2125      0.2250     0.0331  5
  FNR (FN/(FN+TP))            0.1050      0.1250     0.0647  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7242      0.7464     0.0420  5
  max valid BA                0.7322      0.7464     0.0373  5
  best valid F1               0.6416      0.6609     0.0484  5
  test BA                     0.7288      0.7229     0.0391  5
  test AUC                    0.7675      0.7538     0.0563  5
  test AUC in-protein         0.4309      0.4313     0.0768  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4382      0.4057     0.0711  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6423      0.6316     0.0483  5
  test sensitivity            0.6842      0.6667     0.0511  5
  test specificity            0.7735      0.7965     0.0592  5
  test precision              0.6080      0.6230     0.0631  5
  test loss                   0.5858      0.5842     0.0396  5
  FPR (FP/(FP+TN))            0.2265      0.2035     0.0592  5
  FNR (FN/(FN+TP))            0.3158      0.3333     0.0511  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5750      0.5625     0.0844  5
  max valid BA                0.5813      0.5625     0.0978  5
  best valid F1               0.3833      0.5000     0.2609  5
  test BA                     0.5062      0.5000     0.0778  5
  test AUC                    0.3812      0.3203     0.1369  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.4000      0.5000     0.2528  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.2933      0.3846     0.2006  5
  test sensitivity            0.3500      0.5000     0.2710  5
  test specificity            0.6625      0.7500     0.3236  5
  test precision              0.3611      0.3333     0.0962  4
  test loss                   0.6933      0.7001     0.0175  5
  FPR (FP/(FP+TN))            0.3375      0.2500     0.3236  5
  FNR (FN/(FN+TP))            0.6500      0.5000     0.2710  5

groups_PS+PGP+DAG+TAG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5375      0.5000     0.0677  5
  max valid BA                0.5563      0.5312     0.0922  5
  best valid F1               0.4208      0.3750     0.1382  5
  test BA                     0.5467      0.5000     0.0964  5
  test AUC                    0.4874      0.4519     0.1115  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.6000      0.6000     0.4000  5
    (proteins contributing)      2.6000      3.0000     0.8944  5
  test F1                     0.4116      0.5000     0.2472  5
  test sensitivity            0.5333      0.5556     0.3635  5
  test specificity            0.5600      0.6000     0.3700  5
  test precision              0.4407      0.4148     0.1175  4
  test loss                   0.7045      0.6960     0.0256  5
  FPR (FP/(FP+TN))            0.4400      0.4000     0.3700  5
  FNR (FN/(FN+TP))            0.4667      0.4444     0.3635  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6 --seeds=0,1,2,3,4`
