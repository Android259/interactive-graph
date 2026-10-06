# mlp_sub_pb6_drop_ev14_q10

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_drop_ev14_q10'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.6727      0.3171      0.6856      0.4909      0.6970      0.4250
groups_FA                                    5      0.2583      0.8811      0.5058      0.7746      0.2000      0.8944
groups_LPC+LPE+LPG                           5      0.7625      0.6000      0.6010      0.7010      0.8375      0.5800
groups_PA                                    5      0.5692      0.8538      0.6109      0.6593      0.6308      0.8615
groups_PC                                    5      0.5945      0.4030      0.5798      0.5048      0.5046      0.5340
groups_PE                                    5      0.8750      0.6275      0.7881      0.6051      0.8950      0.6200
groups_PG                                    5      0.5825      0.8088      0.5904      0.6996      0.5500      0.7717
groups_PI                                    5      0.2250      0.7625      0.4744      0.5601      0.4000      0.6750
ALL                                         40      0.5675      0.6567      0.6045      0.6244      0.5894      0.6702

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6167      0.5784     0.1111  40
max valid BA                0.6298      0.5916     0.1110  40
best valid F1               0.5401      0.5714     0.1679  40
test BA                     0.6121      0.5636     0.1213  40
test AUC                    0.5812      0.5671     0.1935  40
test AUC in-protein         0.5403      0.5000     0.2392  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.5304      0.4834     0.2191  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.4898      0.5253     0.2056  40
test sensitivity            0.5675      0.5889     0.3022  40
test specificity            0.6567      0.7894     0.3154  40
test precision              0.5201      0.5096     0.1825  38
test loss                   0.6602      0.6827     0.0947  40
FPR (FP/(FP+TN))            0.3433      0.2106     0.3154  40
FNR (FN/(FN+TP))            0.4325      0.4111     0.3022  40

=== abs(sensitivity-specificity) gap: mean=0.4710 median=0.4231 n=40 ===
sensitivity std across seeds (by group): mean=0.1902 median=0.1230 n=8
specificity std across seeds (by group): mean=0.2332 median=0.2460 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5524      0.5742     0.0368  5
  max valid BA                0.5610      0.5818     0.0452  5
  best valid F1               0.5703      0.6226     0.0892  5
  test BA                     0.4949      0.4978     0.0157  5
  test AUC                    0.4341      0.4494     0.0643  5
  test AUC in-protein         0.4623      0.4708     0.0796  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3631      0.3519     0.0996  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5175      0.5517     0.0885  5
  test sensitivity            0.6727      0.7273     0.2601  5
  test specificity            0.3171      0.2683     0.2633  5
  test precision              0.4424      0.4444     0.0172  5
  test loss                   0.7108      0.6983     0.0275  5
  FPR (FP/(FP+TN))            0.6829      0.7317     0.2633  5
  FNR (FN/(FN+TP))            0.3273      0.2727     0.2601  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5403      0.5417     0.0151  5
  max valid BA                0.5472      0.5556     0.0186  5
  best valid F1               0.4496      0.4571     0.1257  5
  test BA                     0.5697      0.5636     0.0285  5
  test AUC                    0.4248      0.3581     0.1298  5
  test AUC in-protein         0.4417      0.4833     0.4193  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.4158      0.4286     0.1645  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3565      0.3429     0.0495  5
  test sensitivity            0.2583      0.2500     0.0543  5
  test specificity            0.8811      0.9189     0.0755  5
  test precision              0.6088      0.6250     0.1142  5
  test loss                   0.7139      0.6933     0.0451  5
  FPR (FP/(FP+TN))            0.1189      0.0811     0.0755  5
  FNR (FN/(FN+TP))            0.7417      0.7500     0.0543  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6817      0.6625     0.0438  5
  max valid BA                0.7087      0.7021     0.0478  5
  best valid F1               0.6343      0.6383     0.0554  5
  test BA                     0.6813      0.6633     0.1035  5
  test AUC                    0.7034      0.6492     0.1243  5
  test AUC in-protein         0.7678      0.8495     0.2131  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.6439      0.6667     0.2001  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.6095      0.5957     0.1012  5
  test sensitivity            0.7625      0.8125     0.1355  5
  test specificity            0.6000      0.6774     0.2288  5
  test precision              0.5278      0.4737     0.1432  5
  test loss                   0.6281      0.6761     0.1175  5
  FPR (FP/(FP+TN))            0.4000      0.3226     0.2288  5
  FNR (FN/(FN+TP))            0.2375      0.1875     0.1355  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7385      0.7500     0.0349  5
  max valid BA                0.7462      0.7500     0.0251  5
  best valid F1               0.6625      0.6667     0.0406  5
  test BA                     0.7115      0.7115     0.0608  5
  test AUC                    0.7302      0.7870     0.1315  5
  test AUC in-protein         0.5577      0.5571     0.3195  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.6445      0.7143     0.2072  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6187      0.6087     0.0789  5
  test sensitivity            0.5692      0.5385     0.0877  5
  test specificity            0.8538      0.8846     0.1595  5
  test precision              0.7161      0.7000     0.1793  5
  test loss                   0.6297      0.6285     0.0443  5
  FPR (FP/(FP+TN))            0.1462      0.1154     0.1595  5
  FNR (FN/(FN+TP))            0.4308      0.4615     0.0877  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5175      0.5000     0.0343  5
  max valid BA                0.5193      0.5065     0.0335  5
  best valid F1               0.4225      0.5253     0.1587  5
  test BA                     0.4988      0.5000     0.0116  5
  test AUC                    0.3887      0.3597     0.0688  5
  test AUC in-protein         0.3916      0.3809     0.1259  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.3815      0.3821     0.0900  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3428      0.5135     0.2503  5
  test sensitivity            0.5945      0.8716     0.5007  5
  test specificity            0.4030      0.1574     0.4866  5
  test precision              0.2732      0.3562     0.1557  5
  test loss                   0.7263      0.6984     0.0609  5
  FPR (FP/(FP+TN))            0.5970      0.8426     0.4866  5
  FNR (FN/(FN+TP))            0.4055      0.1284     0.5007  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7475      0.7875     0.1459  5
  max valid BA                0.7575      0.7937     0.1477  5
  best valid F1               0.6999      0.7191     0.1185  5
  test BA                     0.7512      0.7937     0.1457  5
  test AUC                    0.8377      0.9050     0.1582  5
  test AUC in-protein         0.7223      0.7131     0.1598  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.6982      0.7200     0.1686  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.6926      0.7158     0.1164  5
  test sensitivity            0.8750      0.8750     0.1016  5
  test specificity            0.6275      0.8000     0.3518  5
  test precision              0.5961      0.6444     0.1503  5
  test loss                   0.5335      0.4619     0.1608  5
  FPR (FP/(FP+TN))            0.3725      0.2000     0.3518  5
  FNR (FN/(FN+TP))            0.1250      0.1250     0.1016  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6367      0.6703     0.0993  5
  max valid BA                0.6608      0.6791     0.0591  5
  best valid F1               0.5598      0.5636     0.0538  5
  test BA                     0.6957      0.7052     0.0469  5
  test AUC                    0.6964      0.7057     0.0561  5
  test AUC in-protein         0.4680      0.4692     0.0905  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4758      0.4830     0.0825  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.5902      0.6095     0.0691  5
  test sensitivity            0.5825      0.5614     0.1105  5
  test specificity            0.8088      0.8053     0.0335  5
  test precision              0.6048      0.5902     0.0429  5
  test loss                   0.6463      0.6358     0.0384  5
  FPR (FP/(FP+TN))            0.1912      0.1947     0.0335  5
  FNR (FN/(FN+TP))            0.4175      0.4386     0.1105  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5188      0.5000     0.0280  5
  max valid BA                0.5375      0.5312     0.0407  5
  best valid F1               0.3221      0.4348     0.2325  5
  test BA                     0.4938      0.5000     0.0140  5
  test AUC                    0.4344      0.4297     0.0490  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.6200      0.6000     0.3798  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.1909      0.1667     0.1995  5
  test sensitivity            0.2250      0.1250     0.2710  5
  test specificity            0.7625      0.8125     0.2666  5
  test precision              0.3056      0.3333     0.0481  3
  test loss                   0.6925      0.6930     0.0384  5
  FPR (FP/(FP+TN))            0.2375      0.1875     0.2666  5
  FNR (FN/(FN+TP))            0.7750      0.8750     0.2710  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_drop_ev14_q10 --seeds=0,1,2,3,4`
