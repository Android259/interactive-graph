# mlp_sub_pb6_drop_hydropathy_core

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_drop_hydropathy_core'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.5273      0.4683      0.5130      0.5232      0.5455      0.4950
groups_FA                                    5      0.4250      0.7514      0.5147      0.6846      0.3833      0.7333
groups_LPC+LPE+LPG                           5      0.5375      0.6516      0.5282      0.7621      0.6125      0.6933
groups_PA                                    5      0.5692      0.8308      0.5622      0.6832      0.6308      0.8692
groups_PC                                    5      0.2532      0.7157      0.4673      0.7029      0.2954      0.7574
groups_PE                                    5      0.8000      0.7975      0.7375      0.6740      0.8200      0.8200
groups_PG                                    5      0.6561      0.7575      0.7033      0.6847      0.6250      0.7540
groups_PI                                    5      0.3000      0.7375      0.5411      0.6712      0.3500      0.8125
ALL                                         40      0.5085      0.7138      0.5709      0.6733      0.5328      0.7418

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6281      0.5919     0.1140  40
max valid BA                0.6373      0.6052     0.1141  40
best valid F1               0.5570      0.5854     0.1576  40
test BA                     0.6112      0.6056     0.1180  40
test AUC                    0.5978      0.5509     0.2001  40
test AUC in-protein         0.5799      0.5449     0.2379  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.5723      0.5427     0.2144  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.4593      0.5394     0.2256  40
test sensitivity            0.5085      0.5401     0.3074  40
test specificity            0.7138      0.8018     0.2790  40
test precision              0.5372      0.5652     0.2036  37
test loss                   0.6429      0.6770     0.0846  40
FPR (FP/(FP+TN))            0.2862      0.1982     0.2790  40
FNR (FN/(FN+TP))            0.4915      0.4599     0.3074  40

=== abs(sensitivity-specificity) gap: mean=0.4830 median=0.5141 n=40 ===
sensitivity std across seeds (by group): mean=0.2519 median=0.2601 n=8
specificity std across seeds (by group): mean=0.2557 median=0.2676 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5202      0.5000     0.0403  5
  max valid BA                0.5202      0.5000     0.0403  5
  best valid F1               0.5867      0.6226     0.0651  5
  test BA                     0.4978      0.5000     0.0237  5
  test AUC                    0.3528      0.3311     0.0643  5
  test AUC in-protein         0.4206      0.4395     0.1036  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3259      0.3451     0.0963  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3525      0.5333     0.3235  5
  test sensitivity            0.5273      0.7273     0.4912  5
  test specificity            0.4683      0.1951     0.4907  5
  test precision              0.4428      0.4459     0.0204  3
  test loss                   0.7039      0.7002     0.0110  5
  FPR (FP/(FP+TN))            0.5317      0.8049     0.4907  5
  FNR (FN/(FN+TP))            0.4727      0.2727     0.4912  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5417     0.0257  5
  max valid BA                0.5583      0.5556     0.0188  5
  best valid F1               0.4834      0.4789     0.1040  5
  test BA                     0.5882      0.5907     0.0443  5
  test AUC                    0.5255      0.4977     0.1807  5
  test AUC in-protein         0.6500      0.8000     0.4435  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.6206      0.5455     0.2199  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.4290      0.3529     0.1477  5
  test sensitivity            0.4250      0.2500     0.3082  5
  test specificity            0.7514      0.8378     0.2545  5
  test precision              0.5842      0.5652     0.1525  5
  test loss                   0.6909      0.6776     0.0301  5
  FPR (FP/(FP+TN))            0.2486      0.1622     0.2545  5
  FNR (FN/(FN+TP))            0.5750      0.7500     0.3082  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6283      0.5917     0.0877  5
  max valid BA                0.6529      0.6083     0.0959  5
  best valid F1               0.5605      0.5161     0.1298  5
  test BA                     0.5946      0.6230     0.1016  5
  test AUC                    0.6014      0.5706     0.1183  5
  test AUC in-protein         0.7320      0.7731     0.1610  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.6139      0.6667     0.1973  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.4915      0.4615     0.0831  5
  test sensitivity            0.5375      0.5625     0.1569  5
  test specificity            0.6516      0.7419     0.2807  5
  test precision              0.5188      0.5789     0.1825  5
  test loss                   0.6672      0.6723     0.0429  5
  FPR (FP/(FP+TN))            0.3484      0.2581     0.2807  5
  FNR (FN/(FN+TP))            0.4625      0.4375     0.1569  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7423      0.7308     0.0258  5
  max valid BA                0.7500      0.7500     0.0236  5
  best valid F1               0.6658      0.6667     0.0400  5
  test BA                     0.7000      0.6923     0.0570  5
  test AUC                    0.7675      0.7870     0.1231  5
  test AUC in-protein         0.6077      0.6571     0.3017  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.6530      0.7143     0.2167  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6020      0.5833     0.0750  5
  test sensitivity            0.5692      0.5385     0.0877  5
  test specificity            0.8308      0.8846     0.1480  5
  test precision              0.6684      0.6667     0.1568  5
  test loss                   0.6249      0.6236     0.0431  5
  FPR (FP/(FP+TN))            0.1692      0.1154     0.1480  5
  FNR (FN/(FN+TP))            0.4308      0.4615     0.0877  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5149      0.5065     0.0297  5
  max valid BA                0.5264      0.5165     0.0282  5
  best valid F1               0.4235      0.5253     0.1590  5
  test BA                     0.4845      0.4801     0.0144  5
  test AUC                    0.4097      0.4351     0.0697  5
  test AUC in-protein         0.4997      0.4034     0.2118  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4631      0.3916     0.1588  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.2132      0.1739     0.1832  5
  test sensitivity            0.2532      0.1284     0.3369  5
  test specificity            0.7157      0.8071     0.3199  5
  test precision              0.2438      0.2791     0.1406  5
  test loss                   0.6922      0.6918     0.0161  5
  FPR (FP/(FP+TN))            0.2843      0.1929     0.3199  5
  FNR (FN/(FN+TP))            0.7468      0.8716     0.3369  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8175      0.8063     0.0357  5
  max valid BA                0.8200      0.8125     0.0379  5
  best valid F1               0.7501      0.7391     0.0399  5
  test BA                     0.7987      0.8063     0.0605  5
  test AUC                    0.8695      0.8978     0.1129  5
  test AUC in-protein         0.7383      0.7681     0.1563  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7207      0.7761     0.1596  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7144      0.7312     0.0822  5
  test sensitivity            0.8000      0.8750     0.2121  5
  test specificity            0.7975      0.7625     0.1029  5
  test precision              0.6948      0.6491     0.1155  5
  test loss                   0.4932      0.4609     0.1149  5
  FPR (FP/(FP+TN))            0.2025      0.2375     0.1029  5
  FNR (FN/(FN+TP))            0.2000      0.1250     0.2121  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6824      0.6928     0.0364  5
  max valid BA                0.6895      0.6972     0.0422  5
  best valid F1               0.5957      0.5950     0.0342  5
  test BA                     0.7068      0.7006     0.0321  5
  test AUC                    0.7656      0.7677     0.0494  5
  test AUC in-protein         0.4609      0.4887     0.0760  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4814      0.5034     0.0542  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6131      0.6080     0.0429  5
  test sensitivity            0.6561      0.6667     0.1086  5
  test specificity            0.7575      0.7965     0.1056  5
  test precision              0.5894      0.6170     0.0654  5
  test loss                   0.5869      0.5667     0.0706  5
  FPR (FP/(FP+TN))            0.2425      0.2035     0.1056  5
  FNR (FN/(FN+TP))            0.3439      0.3333     0.1086  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5687      0.5625     0.0713  5
  max valid BA                0.5813      0.5625     0.0753  5
  best valid F1               0.3900      0.4615     0.2284  5
  test BA                     0.5188      0.5000     0.0419  5
  test AUC                    0.4906      0.5000     0.0256  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.7000      0.6667     0.2981  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.2586      0.2222     0.1892  5
  test sensitivity            0.3000      0.1250     0.3137  5
  test specificity            0.7375      0.8750     0.3435  5
  test precision              0.5123      0.3667     0.3272  4
  test loss                   0.6840      0.6940     0.0285  5
  FPR (FP/(FP+TN))            0.2625      0.1250     0.3435  5
  FNR (FN/(FN+TP))            0.7000      0.8750     0.3137  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_drop_hydropathy_core --seeds=0,1,2,3,4`
