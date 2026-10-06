# dh_lcs_family_neutral_pb6_lipprop_subclass

## Summary (analysis/summarize_label.py)

```
Summary: 'dh_lcs_family_neutral_pb6_lipprop_subclass'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.5939      0.5268      0.4944      0.5966      0.5939      0.5900
groups_FA                                    5      0.4000      0.6757      0.3724      0.7739      0.3917      0.7444
groups_LPC+LPE+LPG                           5      0.8000      0.6516      0.4887      0.7352      0.7750      0.7200
groups_PA                                    5      0.5077      0.9231      0.4095      0.7366      0.5846      0.9462
groups_PC                                    5      0.4881      0.6325      0.6856      0.4325      0.5541      0.6447
groups_PE                                    5      0.6650      0.7950      0.4769      0.7191      0.7250      0.8575
groups_PG                                    5      0.7404      0.7080      0.5286      0.6841      0.7571      0.7257
groups_PI                                    5      0.5250      0.5625      0.5178      0.5658      0.5250      0.7125
groups_PS+PGP+DAG+TAG                        5      0.1556      0.7333      0.3507      0.7373      0.2250      0.8250
ALL                                         45      0.5417      0.6898      0.4805      0.6646      0.5702      0.7518

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6435      0.6528     0.1145  45
max valid BA                0.6610      0.6875     0.1113  45
best valid F1               0.5754      0.6066     0.1359  45
test BA                     0.6158      0.6199     0.1233  45
test AUC                    0.6195      0.6391     0.1643  45
test AUC in-protein         0.5744      0.6351     0.2546  32
  (proteins averaged)       3.0000      2.0000     3.5162  45
test AUC in-protein (pairs)      0.5424      0.6000     0.2443  45
  (proteins contributing)      5.4444      3.0000     4.0819  45
test F1                     0.4918      0.5022     0.1958  45
test sensitivity            0.5417      0.5614     0.2722  45
test specificity            0.6898      0.7333     0.2347  45
test precision              0.5370      0.5407     0.2126  44
test loss                   0.7208      0.6707     0.1801  45
FPR (FP/(FP+TN))            0.3102      0.2667     0.2347  45
FNR (FN/(FN+TP))            0.4583      0.4386     0.2722  45

=== abs(sensitivity-specificity) gap: mean=0.3878 median=0.3462 n=45 ===
sensitivity std across seeds (by group): mean=0.2023 median=0.1710 n=9
specificity std across seeds (by group): mean=0.1826 median=0.1293 n=9

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5595      0.5568     0.0840  5
  max valid BA                0.5920      0.6068     0.0885  5
  best valid F1               0.5835      0.6042     0.0836  5
  test BA                     0.5604      0.5661     0.0688  5
  test AUC                    0.5831      0.5928     0.0651  5
  test AUC in-protein         0.6460      0.5091     0.2393  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.7392      0.7139     0.1556  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5155      0.4878     0.1175  5
  test sensitivity            0.5939      0.6061     0.3124  5
  test specificity            0.5268      0.3171     0.3486  5
  test precision              0.5771      0.5077     0.1916  5
  test loss                   0.7171      0.6913     0.0793  5
  FPR (FP/(FP+TN))            0.4732      0.6829     0.3486  5
  FNR (FN/(FN+TP))            0.4061      0.3939     0.3124  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5417     0.0679  5
  max valid BA                0.5681      0.5625     0.0744  5
  best valid F1               0.4707      0.4483     0.1224  5
  test BA                     0.5378      0.5208     0.0492  5
  test AUC                    0.5268      0.5146     0.0895  5
  test AUC in-protein         0.3333      0.1833     0.3115  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.3656      0.3182     0.1870  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3823      0.4737     0.1735  5
  test sensitivity            0.4000      0.3750     0.2422  5
  test specificity            0.6757      0.7568     0.2847  5
  test precision              0.5806      0.4706     0.2554  5
  test loss                   0.6935      0.6905     0.0322  5
  FPR (FP/(FP+TN))            0.3243      0.2432     0.2847  5
  FNR (FN/(FN+TP))            0.6000      0.6250     0.2422  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7333      0.7458     0.0698  5
  max valid BA                0.7475      0.7562     0.0609  5
  best valid F1               0.6676      0.6842     0.0741  5
  test BA                     0.7258      0.7319     0.0864  5
  test AUC                    0.7929      0.7893     0.0469  5
  test AUC in-protein         0.7476      0.7639     0.0789  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.6452      0.6364     0.0628  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.6391      0.6452     0.1023  5
  test sensitivity            0.8000      0.9375     0.2227  5
  test specificity            0.6516      0.6452     0.1278  5
  test precision              0.5487      0.5714     0.0870  5
  test loss                   0.6565      0.6527     0.0222  5
  FPR (FP/(FP+TN))            0.3484      0.3548     0.1278  5
  FNR (FN/(FN+TP))            0.2000      0.0625     0.2227  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7500      0.7500     0.0430  5
  max valid BA                0.7654      0.7692     0.0439  5
  best valid F1               0.6883      0.7000     0.0685  5
  test BA                     0.7154      0.7115     0.0551  5
  test AUC                    0.6799      0.6538     0.0627  5
  test AUC in-protein         0.3917      0.2833     0.4375  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.3451      0.2667     0.2693  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6096      0.6087     0.0911  5
  test sensitivity            0.5077      0.5385     0.0877  5
  test specificity            0.9231      0.9231     0.0385  5
  test precision              0.7690      0.7143     0.1047  5
  test loss                   0.6401      0.6542     0.0283  5
  FPR (FP/(FP+TN))            0.0769      0.0769     0.0385  5
  FNR (FN/(FN+TP))            0.4923      0.4615     0.0877  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5734      0.5473     0.0574  5
  max valid BA                0.5994      0.6027     0.0677  5
  best valid F1               0.4956      0.5179     0.1005  5
  test BA                     0.5603      0.5722     0.0493  5
  test AUC                    0.5303      0.5415     0.0727  5
  test AUC in-protein         0.5041      0.4667     0.1300  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.5080      0.5302     0.0835  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.4484      0.4819     0.0801  5
  test sensitivity            0.4881      0.5229     0.1264  5
  test specificity            0.6325      0.6041     0.0614  5
  test precision              0.4200      0.4286     0.0512  5
  test loss                   0.7864      0.7305     0.1092  5
  FPR (FP/(FP+TN))            0.3675      0.3959     0.0614  5
  FNR (FN/(FN+TP))            0.5119      0.4771     0.1264  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7775      0.7875     0.0452  5
  max valid BA                0.7913      0.8000     0.0404  5
  best valid F1               0.7202      0.7234     0.0542  5
  test BA                     0.7300      0.7125     0.0643  5
  test AUC                    0.7893      0.7794     0.0305  5
  test AUC in-protein         0.7760      0.7384     0.0807  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7516      0.7612     0.0513  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.6326      0.6154     0.0869  5
  test sensitivity            0.6650      0.6000     0.1710  5
  test specificity            0.7950      0.7875     0.0520  5
  test precision              0.6182      0.6207     0.0300  5
  test loss                   0.6135      0.6212     0.0260  5
  FPR (FP/(FP+TN))            0.2050      0.2125     0.0520  5
  FNR (FN/(FN+TP))            0.3350      0.4000     0.1710  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7289      0.7336     0.0372  5
  max valid BA                0.7414      0.7336     0.0285  5
  best valid F1               0.6553      0.6475     0.0346  5
  test BA                     0.7242      0.7310     0.0466  5
  test AUC                    0.7377      0.7441     0.0436  5
  test AUC in-protein         0.5721      0.6318     0.1250  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.5666      0.6215     0.0979  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6398      0.6475     0.0504  5
  test sensitivity            0.7404      0.7544     0.1105  5
  test specificity            0.7080      0.6726     0.1293  5
  test precision              0.5800      0.5488     0.0965  5
  test loss                   0.6488      0.6350     0.0246  5
  FPR (FP/(FP+TN))            0.2920      0.3274     0.1293  5
  FNR (FN/(FN+TP))            0.2596      0.2456     0.1105  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6062      0.5625     0.1073  5
  max valid BA                0.6188      0.5625     0.0948  5
  best valid F1               0.5183      0.5000     0.1241  5
  test BA                     0.5437      0.4688     0.1391  5
  test AUC                    0.4203      0.4297     0.1865  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.3600      0.3000     0.2994  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.3924      0.4286     0.2429  5
  test sensitivity            0.5250      0.7500     0.3791  5
  test specificity            0.5625      0.7500     0.4375  5
  test precision              0.4436      0.3182     0.3766  5
  test loss                   1.0344      1.0497     0.4111  5
  FPR (FP/(FP+TN))            0.4375      0.2500     0.4375  5
  FNR (FN/(FN+TP))            0.4750      0.2500     0.3791  5

groups_PS+PGP+DAG+TAG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5125      0.5000     0.0523  5
  max valid BA                0.5250      0.5312     0.0464  5
  best valid F1               0.3792      0.3636     0.0810  5
  test BA                     0.4444      0.4222     0.0671  5
  test AUC                    0.5156      0.4148     0.2332  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.6000      0.8000     0.4000  5
    (proteins contributing)      2.6000      3.0000     0.8944  5
  test F1                     0.1664      0.1429     0.1544  5
  test sensitivity            0.1556      0.1111     0.1685  5
  test specificity            0.7333      0.7333     0.1633  5
  test precision              0.2357      0.2000     0.1128  4
  test loss                   0.6967      0.7014     0.0429  5
  FPR (FP/(FP+TN))            0.2667      0.2667     0.1633  5
  FNR (FN/(FN+TP))            0.8444      0.8889     0.1685  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label dh_lcs_family_neutral_pb6_lipprop_subclass --seeds=0,1,2,3,4`
