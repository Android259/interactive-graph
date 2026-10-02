# mlp_sub_pb6_drop_apolar_sasa_share

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_drop_apolar_sasa_share'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.7030      0.3073      0.7092      0.4135      0.7879      0.3100
groups_FA                                    5      0.2417      0.8486      0.5195      0.7653      0.2083      0.8833
groups_LPC+LPE+LPG                           5      0.5125      0.6774      0.5870      0.8009      0.6375      0.7267
groups_PA                                    5      0.5538      0.8923      0.6592      0.6844      0.5231      0.9538
groups_PC                                    5      0.5046      0.5482      0.6183      0.4347      0.5945      0.4883
groups_PE                                    5      0.8550      0.7750      0.7310      0.7390      0.8900      0.7700
groups_PG                                    5      0.6456      0.7522      0.7063      0.6778      0.6536      0.7239
groups_PI                                    5      0.2000      0.7750      0.4049      0.6802      0.3750      0.7500
ALL                                         40      0.5270      0.6970      0.6169      0.6495      0.5837      0.7008

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6306      0.5938     0.1149  40
max valid BA                0.6422      0.6256     0.1112  40
best valid F1               0.5594      0.5714     0.1506  40
test BA                     0.6120      0.5876     0.1247  40
test AUC                    0.6307      0.5936     0.1813  40
test AUC in-protein         0.6091      0.5954     0.2217  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.5974      0.6004     0.2034  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.4712      0.5401     0.2296  40
test sensitivity            0.5270      0.5499     0.3078  40
test specificity            0.6970      0.7545     0.2865  40
test precision              0.5210      0.5000     0.2050  37
test loss                   0.6354      0.6677     0.0980  40
FPR (FP/(FP+TN))            0.3030      0.2455     0.2865  40
FNR (FN/(FN+TP))            0.4730      0.4501     0.3078  40

=== abs(sensitivity-specificity) gap: mean=0.4486 median=0.3737 n=40 ===
sensitivity std across seeds (by group): mean=0.1946 median=0.1381 n=8
specificity std across seeds (by group): mean=0.1985 median=0.1584 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5199      0.5064     0.0251  5
  max valid BA                0.5489      0.5367     0.0474  5
  best valid F1               0.6006      0.6226     0.0595  5
  test BA                     0.5052      0.5000     0.0089  5
  test AUC                    0.4662      0.4745     0.0387  5
  test AUC in-protein         0.3968      0.4229     0.1123  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3587      0.3519     0.1610  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4744      0.5833     0.2663  5
  test sensitivity            0.7030      0.8485     0.4062  5
  test specificity            0.3073      0.1463     0.4014  5
  test precision              0.4498      0.4494     0.0055  4
  test loss                   0.7110      0.6994     0.0264  5
  FPR (FP/(FP+TN))            0.6927      0.8537     0.4014  5
  FNR (FN/(FN+TP))            0.2970      0.1515     0.4062  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5347      0.5278     0.0163  5
  max valid BA                0.5458      0.5556     0.0167  5
  best valid F1               0.4583      0.4675     0.1191  5
  test BA                     0.5452      0.5709     0.0519  5
  test AUC                    0.4592      0.4752     0.1013  5
  test AUC in-protein         0.7750      0.8000     0.0739  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.6766      0.7273     0.1414  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3301      0.3333     0.0298  5
  test sensitivity            0.2417      0.2500     0.0186  5
  test specificity            0.8486      0.8919     0.1140  5
  test precision              0.5706      0.6000     0.1972  5
  test loss                   0.6859      0.6758     0.0221  5
  FPR (FP/(FP+TN))            0.1514      0.1081     0.1140  5
  FNR (FN/(FN+TP))            0.7583      0.7500     0.0186  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6496      0.6583     0.0716  5
  max valid BA                0.6821      0.6750     0.0715  5
  best valid F1               0.5950      0.6000     0.0736  5
  test BA                     0.5950      0.6381     0.1136  5
  test AUC                    0.7026      0.6915     0.1338  5
  test AUC in-protein         0.7279      0.7500     0.1091  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.6348      0.6364     0.1018  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.4785      0.5333     0.1384  5
  test sensitivity            0.5125      0.4375     0.2044  5
  test specificity            0.6774      0.6129     0.2027  5
  test precision              0.4951      0.4783     0.2056  5
  test loss                   0.6451      0.6671     0.1235  5
  FPR (FP/(FP+TN))            0.3226      0.3871     0.2027  5
  FNR (FN/(FN+TP))            0.4875      0.5625     0.2044  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7385      0.7500     0.0349  5
  max valid BA                0.7385      0.7500     0.0349  5
  best valid F1               0.6467      0.6667     0.0581  5
  test BA                     0.7231      0.7115     0.0661  5
  test AUC                    0.7793      0.7840     0.0892  5
  test AUC in-protein         0.6792      0.7583     0.3630  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.7061      0.7000     0.2313  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6306      0.6087     0.0939  5
  test sensitivity            0.5538      0.5385     0.0644  5
  test specificity            0.8923      0.9231     0.0958  5
  test precision              0.7456      0.7500     0.1608  5
  test loss                   0.5966      0.6177     0.0505  5
  FPR (FP/(FP+TN))            0.1077      0.0769     0.0958  5
  FNR (FN/(FN+TP))            0.4462      0.4615     0.0644  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5272      0.5114     0.0378  5
  max valid BA                0.5414      0.5213     0.0477  5
  best valid F1               0.4500      0.5253     0.1354  5
  test BA                     0.5264      0.5380     0.0263  5
  test AUC                    0.4836      0.5389     0.0971  5
  test AUC in-protein         0.5046      0.5386     0.2069  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4931      0.5500     0.1895  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3497      0.4019     0.2238  5
  test sensitivity            0.5046      0.3945     0.4459  5
  test specificity            0.5482      0.6853     0.4383  5
  test precision              0.3259      0.3864     0.1875  5
  test loss                   0.7136      0.6923     0.0619  5
  FPR (FP/(FP+TN))            0.4518      0.3147     0.4383  5
  FNR (FN/(FN+TP))            0.4954      0.6055     0.4459  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8300      0.8313     0.0223  5
  max valid BA                0.8300      0.8313     0.0223  5
  best valid F1               0.7581      0.7609     0.0258  5
  test BA                     0.8150      0.8000     0.0487  5
  test AUC                    0.8955      0.8878     0.0520  5
  test AUC in-protein         0.7797      0.8087     0.1558  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7808      0.8000     0.1010  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7416      0.7234     0.0562  5
  test sensitivity            0.8550      0.8500     0.0716  5
  test specificity            0.7750      0.7750     0.0306  5
  test precision              0.6550      0.6400     0.0474  5
  test loss                   0.4667      0.4423     0.0733  5
  FPR (FP/(FP+TN))            0.2250      0.2250     0.0306  5
  FNR (FN/(FN+TP))            0.1450      0.1500     0.0716  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6824      0.6707     0.0465  5
  max valid BA                0.6887      0.6707     0.0458  5
  best valid F1               0.5909      0.5620     0.0553  5
  test BA                     0.6989      0.7185     0.0463  5
  test AUC                    0.7621      0.7565     0.0427  5
  test AUC in-protein         0.4715      0.4222     0.1132  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4690      0.4574     0.0630  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6041      0.6250     0.0569  5
  test sensitivity            0.6456      0.6140     0.0717  5
  test specificity            0.7522      0.7522     0.0451  5
  test precision              0.5696      0.5882     0.0589  5
  test loss                   0.5803      0.5893     0.0483  5
  FPR (FP/(FP+TN))            0.2478      0.2478     0.0451  5
  FNR (FN/(FN+TP))            0.3544      0.3860     0.0717  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5625      0.5938     0.0585  5
  max valid BA                0.5625      0.5938     0.0585  5
  best valid F1               0.3751      0.5000     0.1966  5
  test BA                     0.4875      0.5000     0.0356  5
  test AUC                    0.4969      0.4766     0.0759  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.6600      0.6667     0.2586  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.1604      0.0000     0.2201  5
  test sensitivity            0.2000      0.0000     0.2739  5
  test specificity            0.7750      0.8750     0.2600  5
  test precision              0.2238      0.3077     0.1958  3
  test loss                   0.6837      0.6933     0.0284  5
  FPR (FP/(FP+TN))            0.2250      0.1250     0.2600  5
  FNR (FN/(FN+TP))            0.8000      1.0000     0.2739  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_drop_apolar_sasa_share --seeds=0,1,2,3,4`
