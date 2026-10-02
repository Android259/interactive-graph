# mlp_sub_pb6_hid32

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_hid32'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.5576      0.4585      0.6665      0.6920      0.5758      0.4700
groups_FA                                    5      0.4000      0.7081      0.6461      0.6934      0.3833      0.7778
groups_LPC+LPE+LPG                           5      0.5250      0.8645      0.8179      0.7873      0.5000      0.8867
groups_PA                                    5      0.5538      0.9154      0.5352      0.7293      0.5231      0.9385
groups_PC                                    5      0.1303      0.8102      0.5135      0.8632      0.1817      0.8254
groups_PE                                    5      0.8700      0.7875      0.7704      0.7760      0.8950      0.8000
groups_PG                                    5      0.7123      0.8142      0.8345      0.8002      0.7107      0.8000
groups_PI                                    5      0.2000      0.6375      0.6275      0.5739      0.4250      0.6625
groups_PS+PGP+DAG+TAG                        5      0.5333      0.5467      0.4833      0.6478      0.4250      0.7000
ALL                                         45      0.4980      0.7269      0.6550      0.7292      0.5133      0.7623

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6242      0.5938     0.1259  45
max valid BA                0.6378      0.5938     0.1221  45
best valid F1               0.5457      0.5545     0.1569  45
test BA                     0.6125      0.5889     0.1456  45
test AUC                    0.5859      0.5809     0.2139  45
test AUC in-protein         0.6402      0.6528     0.2259  32
  (proteins averaged)       3.0000      2.0000     3.5162  45
test AUC in-protein (pairs)      0.5912      0.6364     0.2422  45
  (proteins contributing)      5.4444      3.0000     4.0819  45
test F1                     0.4652      0.5352     0.2535  45
test sensitivity            0.4980      0.5625     0.3035  45
test specificity            0.7269      0.8053     0.2493  45
test precision              0.5319      0.6000     0.2371  41
test loss                   0.6762      0.6886     0.1940  45
FPR (FP/(FP+TN))            0.2731      0.1947     0.2493  45
FNR (FN/(FN+TP))            0.5020      0.4375     0.3035  45

=== abs(sensitivity-specificity) gap: mean=0.4211 median=0.3730 n=45 ===
sensitivity std across seeds (by group): mean=0.1922 median=0.1147 n=9
specificity std across seeds (by group): mean=0.1765 median=0.1271 n=9

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5040      0.5000     0.0438  5
  max valid BA                0.5229      0.5167     0.0256  5
  best valid F1               0.5866      0.6022     0.0362  5
  test BA                     0.5081      0.5000     0.0375  5
  test AUC                    0.4479      0.4390     0.1151  5
  test AUC in-protein         0.4781      0.4200     0.1225  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4437      0.5073     0.2056  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4361      0.5227     0.2460  5
  test sensitivity            0.5576      0.5758     0.3452  5
  test specificity            0.4585      0.4878     0.3623  5
  test precision              0.4590      0.4589     0.0359  4
  test loss                   0.7637      0.7003     0.0976  5
  FPR (FP/(FP+TN))            0.5415      0.5122     0.3623  5
  FNR (FN/(FN+TP))            0.4424      0.4242     0.3452  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5653      0.5694     0.0181  5
  max valid BA                0.5806      0.5903     0.0244  5
  best valid F1               0.4481      0.4444     0.1490  5
  test BA                     0.5541      0.5738     0.0674  5
  test AUC                    0.3840      0.3863     0.1061  5
  test AUC in-protein         0.7000      0.8167     0.3662  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.5156      0.5714     0.2245  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3959      0.3182     0.1343  5
  test sensitivity            0.4000      0.2917     0.3181  5
  test specificity            0.7081      0.7568     0.3229  5
  test precision              0.5968      0.4340     0.2872  5
  test loss                   0.7708      0.7450     0.0815  5
  FPR (FP/(FP+TN))            0.2919      0.2432     0.3229  5
  FNR (FN/(FN+TP))            0.6000      0.7083     0.3181  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6804      0.6813     0.0374  5
  max valid BA                0.6933      0.7125     0.0462  5
  best valid F1               0.5793      0.6250     0.0831  5
  test BA                     0.6948      0.6855     0.0410  5
  test AUC                    0.7623      0.7329     0.0678  5
  test AUC in-protein         0.7954      0.8021     0.1131  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.7133      0.7059     0.0660  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5854      0.5882     0.0692  5
  test sensitivity            0.5250      0.5625     0.0948  5
  test specificity            0.8645      0.8710     0.0736  5
  test precision              0.6799      0.6667     0.0937  5
  test loss                   0.5583      0.5776     0.0775  5
  FPR (FP/(FP+TN))            0.1355      0.1290     0.0736  5
  FNR (FN/(FN+TP))            0.4750      0.4375     0.0948  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7154      0.7308     0.0498  5
  max valid BA                0.7308      0.7500     0.0451  5
  best valid F1               0.6358      0.6667     0.0724  5
  test BA                     0.7346      0.7500     0.0534  5
  test AUC                    0.6604      0.6509     0.0477  5
  test AUC in-protein         0.6292      0.6583     0.3902  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.7398      0.7778     0.2157  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6440      0.6667     0.0811  5
  test sensitivity            0.5538      0.5385     0.0644  5
  test specificity            0.9154      0.9231     0.0501  5
  test precision              0.7728      0.8000     0.1223  5
  test loss                   0.5873      0.5753     0.0352  5
  FPR (FP/(FP+TN))            0.0846      0.0769     0.0501  5
  FNR (FN/(FN+TP))            0.4462      0.4615     0.0644  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4877      0.4924     0.0212  5
  max valid BA                0.5035      0.5000     0.0411  5
  best valid F1               0.3664      0.3218     0.0991  5
  test BA                     0.4702      0.4756     0.0223  5
  test AUC                    0.4025      0.3750     0.0513  5
  test AUC in-protein         0.5575      0.6109     0.1342  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.5683      0.5821     0.1117  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.1533      0.1989     0.1302  5
  test sensitivity            0.1303      0.1651     0.1147  5
  test specificity            0.8102      0.7310     0.1271  5
  test precision              0.2408      0.2808     0.1118  4
  test loss                   0.9187      0.7179     0.3091  5
  FPR (FP/(FP+TN))            0.1898      0.2690     0.1271  5
  FNR (FN/(FN+TP))            0.8697      0.8349     0.1147  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8413      0.8313     0.0228  5
  max valid BA                0.8475      0.8375     0.0196  5
  best valid F1               0.7818      0.7674     0.0229  5
  test BA                     0.8287      0.8125     0.0425  5
  test AUC                    0.9113      0.8959     0.0414  5
  test AUC in-protein         0.8064      0.8249     0.1281  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.8062      0.8000     0.0935  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7579      0.7416     0.0487  5
  test sensitivity            0.8700      0.8500     0.0647  5
  test specificity            0.7875      0.7875     0.0265  5
  test precision              0.6717      0.6735     0.0404  5
  test loss                   0.4221      0.4347     0.0431  5
  FPR (FP/(FP+TN))            0.2125      0.2125     0.0265  5
  FNR (FN/(FN+TP))            0.1300      0.1500     0.0647  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7491      0.7463     0.0193  5
  max valid BA                0.7554      0.7508     0.0181  5
  best valid F1               0.6726      0.6667     0.0239  5
  test BA                     0.7632      0.7711     0.0331  5
  test AUC                    0.8166      0.8126     0.0262  5
  test AUC in-protein         0.5560      0.5649     0.0960  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.5438      0.5374     0.0916  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6841      0.6942     0.0419  5
  test sensitivity            0.7123      0.7193     0.0563  5
  test specificity            0.8142      0.8142     0.0140  5
  test precision              0.6585      0.6562     0.0311  5
  test loss                   0.5238      0.5174     0.0357  5
  FPR (FP/(FP+TN))            0.1858      0.1858     0.0140  5
  FNR (FN/(FN+TP))            0.2877      0.2807     0.0563  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5437      0.5625     0.0784  5
  max valid BA                0.5437      0.5625     0.0784  5
  best valid F1               0.4200      0.4444     0.1218  5
  test BA                     0.4188      0.4062     0.0568  5
  test AUC                    0.3375      0.3125     0.0907  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.4800      0.4000     0.3754  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.1278      0.0000     0.1912  5
  test sensitivity            0.2000      0.0000     0.3260  5
  test specificity            0.6375      0.8125     0.3519  5
  test precision              0.1205      0.0909     0.1472  4
  test loss                   0.7726      0.7166     0.1032  5
  FPR (FP/(FP+TN))            0.3625      0.1875     0.3519  5
  FNR (FN/(FN+TP))            0.8000      1.0000     0.3260  5

groups_PS+PGP+DAG+TAG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5312      0.5000     0.0585  5
  max valid BA                0.5625      0.5938     0.0442  5
  best valid F1               0.4204      0.5000     0.1198  5
  test BA                     0.5400      0.5000     0.0731  5
  test AUC                    0.5511      0.5185     0.1362  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.5100      0.6000     0.4068  5
    (proteins contributing)      2.6000      3.0000     0.8944  5
  test F1                     0.4020      0.4348     0.2414  5
  test sensitivity            0.5333      0.5556     0.3461  5
  test specificity            0.5467      0.4000     0.2599  5
  test precision              0.4072      0.4006     0.0558  4
  test loss                   0.7687      0.6936     0.1665  5
  FPR (FP/(FP+TN))            0.4533      0.6000     0.2599  5
  FNR (FN/(FN+TP))            0.4667      0.4444     0.3461  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_hid32 --seeds=0,1,2,3,4`
