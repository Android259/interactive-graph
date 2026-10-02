# mlp_sub_pb6_hid64

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_hid64'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.6606      0.3024      0.7201      0.7289      0.6788      0.3800
groups_FA                                    5      0.3500      0.7514      0.6338      0.7285      0.3250      0.7944
groups_LPC+LPE+LPG                           5      0.5750      0.8839      0.8233      0.7922      0.5875      0.9067
groups_PA                                    5      0.5538      0.8231      0.6158      0.7046      0.5231      0.9231
groups_PC                                    5      0.3817      0.5898      0.9149      0.8568      0.2661      0.7503
groups_PE                                    5      0.8850      0.8025      0.8159      0.7866      0.8950      0.8075
groups_PG                                    5      0.7263      0.8000      0.8756      0.8301      0.7500      0.7947
groups_PI                                    5      0.3500      0.5250      0.7485      0.4827      0.5000      0.5875
groups_PS+PGP+DAG+TAG                        5      0.6000      0.5200      0.7501      0.6803      0.4750      0.5500
ALL                                         45      0.5647      0.6665      0.7664      0.7323      0.5556      0.7216

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6264      0.5833     0.1305  45
max valid BA                0.6386      0.5833     0.1324  45
best valid F1               0.5465      0.5600     0.1756  45
test BA                     0.6156      0.6111     0.1437  45
test AUC                    0.5920      0.5765     0.2209  45
test AUC in-protein         0.6553      0.6764     0.2384  32
  (proteins averaged)       3.0000      2.0000     3.5162  45
test AUC in-protein (pairs)      0.6056      0.6000     0.2227  45
  (proteins contributing)      5.4444      3.0000     4.0819  45
test F1                     0.5154      0.5373     0.1861  45
test sensitivity            0.5647      0.5625     0.2561  45
test specificity            0.6665      0.7788     0.2878  45
test precision              0.5262      0.5000     0.1878  45
test loss                   0.7249      0.6942     0.2523  45
FPR (FP/(FP+TN))            0.3335      0.2212     0.2878  45
FNR (FN/(FN+TP))            0.4353      0.4375     0.2561  45

=== abs(sensitivity-specificity) gap: mean=0.3693 median=0.3462 n=45 ===
sensitivity std across seeds (by group): mean=0.1713 median=0.2158 n=9
specificity std across seeds (by group): mean=0.2002 median=0.2081 n=9

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4957      0.4970     0.0120  5
  max valid BA                0.5294      0.5341     0.0213  5
  best valid F1               0.5836      0.5825     0.0313  5
  test BA                     0.4815      0.4738     0.0182  5
  test AUC                    0.4109      0.3954     0.1199  5
  test AUC in-protein         0.4906      0.4945     0.0858  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4447      0.4497     0.1419  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5128      0.5000     0.0683  5
  test sensitivity            0.6606      0.6061     0.2158  5
  test specificity            0.3024      0.3415     0.2081  5
  test precision              0.4313      0.4255     0.0144  5
  test loss                   0.8275      0.8366     0.0825  5
  FPR (FP/(FP+TN))            0.6976      0.6585     0.2081  5
  FNR (FN/(FN+TP))            0.3394      0.3939     0.2158  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5542      0.5556     0.0222  5
  max valid BA                0.5597      0.5556     0.0135  5
  best valid F1               0.4407      0.4211     0.0806  5
  test BA                     0.5507      0.5372     0.0396  5
  test AUC                    0.3989      0.3502     0.1217  5
  test AUC in-protein         0.6917      0.8000     0.3625  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.3961      0.4545     0.1439  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3801      0.3500     0.1030  5
  test sensitivity            0.3500      0.2917     0.2275  5
  test specificity            0.7514      0.8378     0.2487  5
  test precision              0.5288      0.4545     0.1489  5
  test loss                   0.8878      0.8960     0.1863  5
  FPR (FP/(FP+TN))            0.2486      0.1622     0.2487  5
  FNR (FN/(FN+TP))            0.6500      0.7083     0.2275  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7063      0.7292     0.0351  5
  max valid BA                0.7471      0.7312     0.0667  5
  best valid F1               0.6552      0.6429     0.0956  5
  test BA                     0.7294      0.7167     0.0328  5
  test AUC                    0.8002      0.7792     0.0886  5
  test AUC in-protein         0.9094      0.9115     0.0090  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.7768      0.7647     0.0504  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.6403      0.6207     0.0474  5
  test sensitivity            0.5750      0.5625     0.0523  5
  test specificity            0.8839      0.9032     0.0707  5
  test precision              0.7354      0.7273     0.1138  5
  test loss                   0.5126      0.5463     0.0996  5
  FPR (FP/(FP+TN))            0.1161      0.0968     0.0707  5
  FNR (FN/(FN+TP))            0.4250      0.4375     0.0523  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7154      0.7500     0.0567  5
  max valid BA                0.7231      0.7500     0.0554  5
  best valid F1               0.6259      0.6667     0.0856  5
  test BA                     0.6885      0.6923     0.0498  5
  test AUC                    0.6822      0.6746     0.0106  5
  test AUC in-protein         0.5435      0.6286     0.4296  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.6304      0.6000     0.2458  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.5859      0.5926     0.0583  5
  test sensitivity            0.5538      0.5385     0.0644  5
  test specificity            0.8231      0.8846     0.1349  5
  test precision              0.6515      0.6667     0.1595  5
  test loss                   0.6128      0.6002     0.0358  5
  FPR (FP/(FP+TN))            0.1769      0.1154     0.1349  5
  FNR (FN/(FN+TP))            0.4462      0.4615     0.0644  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4987      0.4929     0.0220  5
  max valid BA                0.5082      0.5107     0.0177  5
  best valid F1               0.3779      0.3490     0.1104  5
  test BA                     0.4857      0.4863     0.0164  5
  test AUC                    0.3995      0.4139     0.0424  5
  test AUC in-protein         0.6017      0.6581     0.1701  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.5735      0.5804     0.1175  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3301      0.3021     0.0983  5
  test sensitivity            0.3817      0.2661     0.2899  5
  test specificity            0.5898      0.7157     0.2932  5
  test precision              0.3364      0.3475     0.0284  5
  test loss                   1.1634      1.2572     0.2566  5
  FPR (FP/(FP+TN))            0.4102      0.2843     0.2932  5
  FNR (FN/(FN+TP))            0.6183      0.7339     0.2899  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8438      0.8438     0.0342  5
  max valid BA                0.8512      0.8438     0.0301  5
  best valid F1               0.7869      0.7857     0.0379  5
  test BA                     0.8438      0.8375     0.0276  5
  test AUC                    0.9106      0.9053     0.0360  5
  test AUC in-protein         0.7974      0.8212     0.1283  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7922      0.8060     0.0700  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7762      0.7765     0.0313  5
  test sensitivity            0.8850      0.8500     0.0627  5
  test specificity            0.8025      0.7875     0.0409  5
  test precision              0.6935      0.6667     0.0395  5
  test loss                   0.4094      0.3991     0.0348  5
  FPR (FP/(FP+TN))            0.1975      0.2125     0.0409  5
  FNR (FN/(FN+TP))            0.1150      0.1500     0.0627  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7679      0.7643     0.0159  5
  max valid BA                0.7723      0.7643     0.0198  5
  best valid F1               0.6933      0.6833     0.0248  5
  test BA                     0.7632      0.7666     0.0110  5
  test AUC                    0.8330      0.8355     0.0257  5
  test AUC in-protein         0.5885      0.5552     0.0624  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.5667      0.5691     0.0566  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6843      0.6880     0.0138  5
  test sensitivity            0.7263      0.7193     0.0200  5
  test specificity            0.8000      0.8053     0.0173  5
  test precision              0.6473      0.6508     0.0189  5
  test loss                   0.5313      0.5339     0.0491  5
  FPR (FP/(FP+TN))            0.2000      0.1947     0.0173  5
  FNR (FN/(FN+TP))            0.2737      0.2807     0.0200  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5437      0.5312     0.0568  5
  max valid BA                0.5437      0.5312     0.0568  5
  best valid F1               0.3691      0.4444     0.2286  5
  test BA                     0.4375      0.4375     0.0797  5
  test AUC                    0.3609      0.3672     0.1281  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.4400      0.5000     0.2862  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.2326      0.2000     0.1733  5
  test sensitivity            0.3500      0.1250     0.3791  5
  test specificity            0.5250      0.8125     0.4813  5
  test precision              0.2585      0.2500     0.1787  5
  test loss                   0.7325      0.7149     0.0655  5
  FPR (FP/(FP+TN))            0.4750      0.1875     0.4813  5
  FNR (FN/(FN+TP))            0.6500      0.8750     0.3791  5

groups_PS+PGP+DAG+TAG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5125      0.5000     0.0474  5
  max valid BA                0.5125      0.5000     0.0474  5
  best valid F1               0.3862      0.3636     0.0659  5
  test BA                     0.5600      0.5222     0.0815  5
  test AUC                    0.5319      0.5556     0.1023  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.8300      1.0000     0.2636  5
    (proteins contributing)      2.6000      3.0000     0.8944  5
  test F1                     0.4962      0.5263     0.0817  5
  test sensitivity            0.6000      0.5556     0.2304  5
  test specificity            0.5200      0.6000     0.3070  5
  test precision              0.4527      0.4000     0.1103  5
  test loss                   0.8469      0.8374     0.1588  5
  FPR (FP/(FP+TN))            0.4800      0.4000     0.3070  5
  FNR (FN/(FN+TP))            0.4000      0.4444     0.2304  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_hid64 --seeds=0,1,2,3,4`
