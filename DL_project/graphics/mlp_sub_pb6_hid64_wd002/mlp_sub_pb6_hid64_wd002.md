# mlp_sub_pb6_hid64_wd002

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_hid64_wd002'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.7091      0.2049      0.7366      0.5793      0.7394      0.3150
groups_FA                                    5      0.4833      0.6216      0.7754      0.5432      0.4917      0.6278
groups_LPC+LPE+LPG                           5      0.4875      0.8839      0.8183      0.7902      0.5750      0.8400
groups_PA                                    5      0.5846      0.7462      0.7368      0.6797      0.5231      0.9385
groups_PC                                    5      0.3596      0.6051      0.7606      0.7109      0.3468      0.6396
groups_PE                                    5      0.8900      0.7825      0.8101      0.7939      0.9200      0.7925
groups_PG                                    5      0.7228      0.8212      0.8583      0.8227      0.7286      0.8000
groups_PI                                    5      0.3000      0.5500      0.7563      0.4478      0.5250      0.6125
groups_PS+PGP+DAG+TAG                        5      0.5333      0.5600      0.6606      0.6561      0.4250      0.5750
ALL                                         45      0.5634      0.6417      0.7681      0.6693      0.5861      0.6823

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6194      0.5938     0.1351  45
max valid BA                0.6342      0.5938     0.1326  45
best valid F1               0.5441      0.5714     0.1741  45
test BA                     0.6025      0.5769     0.1427  45
test AUC                    0.5824      0.5728     0.2193  45
test AUC in-protein         0.6275      0.6422     0.2316  32
  (proteins averaged)       3.0000      2.0000     3.5162  45
test AUC in-protein (pairs)      0.5665      0.5782     0.2385  45
  (proteins contributing)      5.4444      3.0000     4.0819  45
test F1                     0.4952      0.5263     0.2008  45
test sensitivity            0.5634      0.6154     0.2846  45
test specificity            0.6417      0.7742     0.2965  45
test precision              0.4984      0.4615     0.1873  45
test loss                   0.6920      0.6889     0.1984  45
FPR (FP/(FP+TN))            0.3583      0.2258     0.2965  45
FNR (FN/(FN+TP))            0.4366      0.3846     0.2846  45

=== abs(sensitivity-specificity) gap: mean=0.4143 median=0.4032 n=45 ===
sensitivity std across seeds (by group): mean=0.2111 median=0.2040 n=9
specificity std across seeds (by group): mean=0.2065 median=0.1838 n=9

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4785      0.4648     0.0265  5
  max valid BA                0.5272      0.5174     0.0275  5
  best valid F1               0.5914      0.5825     0.0291  5
  test BA                     0.4570      0.4497     0.0501  5
  test AUC                    0.4096      0.4050     0.1108  5
  test AUC in-protein         0.4748      0.4855     0.1020  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4069      0.3771     0.1261  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5179      0.5102     0.0751  5
  test sensitivity            0.7091      0.7576     0.2040  5
  test specificity            0.2049      0.2683     0.1838  5
  test precision              0.4153      0.4000     0.0325  5
  test loss                   0.7932      0.8314     0.0669  5
  FPR (FP/(FP+TN))            0.7951      0.7317     0.1838  5
  FNR (FN/(FN+TP))            0.2909      0.2424     0.2040  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5569      0.5556     0.0199  5
  max valid BA                0.5597      0.5556     0.0181  5
  best valid F1               0.4556      0.4211     0.1072  5
  test BA                     0.5525      0.5602     0.0282  5
  test AUC                    0.4063      0.3525     0.1273  5
  test AUC in-protein         0.6500      0.8000     0.3226  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.3870      0.4286     0.1407  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.4163      0.3243     0.1531  5
  test sensitivity            0.4833      0.2500     0.3640  5
  test specificity            0.6216      0.7838     0.3376  5
  test precision              0.5137      0.4524     0.1608  5
  test loss                   0.8232      0.7400     0.1572  5
  FPR (FP/(FP+TN))            0.3784      0.2162     0.3376  5
  FNR (FN/(FN+TP))            0.5167      0.7500     0.3640  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6754      0.6854     0.0301  5
  max valid BA                0.7075      0.7104     0.0542  5
  best valid F1               0.5999      0.6383     0.1011  5
  test BA                     0.6857      0.6996     0.0467  5
  test AUC                    0.7583      0.7349     0.0725  5
  test AUC in-protein         0.7987      0.8046     0.0356  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.6480      0.6667     0.1722  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5636      0.5926     0.0874  5
  test sensitivity            0.4875      0.5000     0.1202  5
  test specificity            0.8839      0.9032     0.0629  5
  test precision              0.6937      0.7273     0.0825  5
  test loss                   0.5592      0.5908     0.0855  5
  FPR (FP/(FP+TN))            0.1161      0.0968     0.0629  5
  FNR (FN/(FN+TP))            0.5125      0.5000     0.1202  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7154      0.7308     0.0439  5
  max valid BA                0.7308      0.7500     0.0451  5
  best valid F1               0.6358      0.6667     0.0724  5
  test BA                     0.6654      0.6731     0.0554  5
  test AUC                    0.6911      0.7012     0.0184  5
  test AUC in-protein         0.5792      0.6583     0.4685  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.6434      0.7778     0.3356  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.5634      0.5714     0.0514  5
  test sensitivity            0.5846      0.6154     0.0877  5
  test specificity            0.7462      0.8077     0.1690  5
  test precision              0.5680      0.6000     0.1152  5
  test loss                   0.6329      0.6198     0.0482  5
  FPR (FP/(FP+TN))            0.2538      0.1923     0.1690  5
  FNR (FN/(FN+TP))            0.4154      0.3846     0.0877  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4869      0.4911     0.0218  5
  max valid BA                0.4932      0.4911     0.0212  5
  best valid F1               0.3712      0.3689     0.1173  5
  test BA                     0.4824      0.4898     0.0126  5
  test AUC                    0.3807      0.3874     0.0283  5
  test AUC in-protein         0.5398      0.6043     0.1733  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.5033      0.5448     0.1169  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3039      0.2714     0.1236  5
  test sensitivity            0.3596      0.2385     0.3309  5
  test specificity            0.6051      0.7107     0.3222  5
  test precision              0.3258      0.3256     0.0206  5
  test loss                   0.9699      1.1462     0.2492  5
  FPR (FP/(FP+TN))            0.3949      0.2893     0.3222  5
  FNR (FN/(FN+TP))            0.6404      0.7615     0.3309  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8450      0.8375     0.0352  5
  max valid BA                0.8562      0.8438     0.0269  5
  best valid F1               0.7898      0.7816     0.0334  5
  test BA                     0.8363      0.8313     0.0162  5
  test AUC                    0.9108      0.9016     0.0284  5
  test AUC in-protein         0.7822      0.8306     0.1557  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7782      0.8060     0.1032  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7659      0.7660     0.0194  5
  test sensitivity            0.8900      0.9000     0.0379  5
  test specificity            0.7825      0.7750     0.0381  5
  test precision              0.6737      0.6667     0.0343  5
  test loss                   0.4297      0.4297     0.0431  5
  FPR (FP/(FP+TN))            0.2175      0.2250     0.0381  5
  FNR (FN/(FN+TP))            0.1100      0.1000     0.0379  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7598      0.7553     0.0104  5
  max valid BA                0.7643      0.7642     0.0083  5
  best valid F1               0.6836      0.6825     0.0111  5
  test BA                     0.7720      0.7580     0.0394  5
  test AUC                    0.8261      0.8263     0.0317  5
  test AUC in-protein         0.5971      0.5926     0.0741  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.5683      0.5660     0.0555  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6946      0.6783     0.0485  5
  test sensitivity            0.7228      0.6842     0.0769  5
  test specificity            0.8212      0.8230     0.0115  5
  test precision              0.6699      0.6724     0.0280  5
  test loss                   0.5020      0.4991     0.0432  5
  FPR (FP/(FP+TN))            0.1788      0.1770     0.0115  5
  FNR (FN/(FN+TP))            0.2772      0.3158     0.0769  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5687      0.5625     0.0809  5
  max valid BA                0.5687      0.5625     0.0809  5
  best valid F1               0.3876      0.5333     0.2396  5
  test BA                     0.4250      0.4375     0.0523  5
  test AUC                    0.3547      0.3516     0.1301  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.3733      0.5000     0.3491  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.1962      0.1818     0.2010  5
  test sensitivity            0.3000      0.1250     0.3601  5
  test specificity            0.5500      0.7500     0.3913  5
  test precision              0.1793      0.2632     0.1655  5
  test loss                   0.7229      0.7171     0.0329  5
  FPR (FP/(FP+TN))            0.4500      0.2500     0.3913  5
  FNR (FN/(FN+TP))            0.7000      0.8750     0.3601  5

groups_PS+PGP+DAG+TAG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4875      0.5000     0.0900  5
  max valid BA                0.5000      0.5000     0.0663  5
  best valid F1               0.3816      0.3636     0.0730  5
  test BA                     0.5467      0.5222     0.0461  5
  test AUC                    0.5037      0.5407     0.1155  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.7900      0.7500     0.2012  5
    (proteins contributing)      2.6000      3.0000     0.8944  5
  test F1                     0.4349      0.5000     0.1492  5
  test sensitivity            0.5333      0.5556     0.3182  5
  test specificity            0.5600      0.6000     0.3419  5
  test precision              0.4459      0.4545     0.0571  5
  test loss                   0.7950      0.7030     0.1557  5
  FPR (FP/(FP+TN))            0.4400      0.4000     0.3419  5
  FNR (FN/(FN+TP))            0.4667      0.4444     0.3182  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_hid64_wd002 --seeds=0,1,2,3,4`
