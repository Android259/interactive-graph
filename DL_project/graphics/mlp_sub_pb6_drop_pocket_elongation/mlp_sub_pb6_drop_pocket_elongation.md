# mlp_sub_pb6_drop_pocket_elongation

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_drop_pocket_elongation'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.5818      0.4049      0.6658      0.4188      0.6909      0.3700
groups_FA                                    5      0.2000      0.9730      0.5225      0.7535      0.1417      0.9778
groups_LPC+LPE+LPG                           5      0.5500      0.6968      0.5857      0.7586      0.5625      0.7533
groups_PA                                    5      0.4923      0.7615      0.5622      0.6907      0.5846      0.8154
groups_PC                                    5      0.6294      0.4091      0.6745      0.3851      0.6661      0.3949
groups_PE                                    5      0.9100      0.5850      0.8058      0.5640      0.9000      0.5975
groups_PG                                    5      0.6947      0.5752      0.7317      0.5771      0.6500      0.6195
groups_PI                                    5      0.2250      0.7500      0.4650      0.6250      0.4500      0.7750
ALL                                         40      0.5354      0.6444      0.6267      0.5966      0.5807      0.6629

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6098      0.5932     0.1000  40
max valid BA                0.6218      0.6150     0.1049  40
best valid F1               0.5468      0.5550     0.1299  40
test BA                     0.5899      0.5712     0.1084  40
test AUC                    0.5669      0.5744     0.1953  40
test AUC in-protein         0.5714      0.5878     0.2552  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.5752      0.6364     0.2363  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.4443      0.5011     0.2086  40
test sensitivity            0.5354      0.5796     0.3303  40
test specificity            0.6444      0.7341     0.3205  40
test precision              0.4877      0.4459     0.2057  38
test loss                   0.6635      0.6759     0.0915  40
FPR (FP/(FP+TN))            0.3556      0.2659     0.3205  40
FNR (FN/(FN+TP))            0.4646      0.4204     0.3303  40

=== abs(sensitivity-specificity) gap: mean=0.5060 median=0.4795 n=40 ===
sensitivity std across seeds (by group): mean=0.2270 median=0.1846 n=8
specificity std across seeds (by group): mean=0.2451 median=0.2991 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5130      0.5000     0.0197  5
  max valid BA                0.5305      0.5000     0.0572  5
  best valid F1               0.5426      0.6226     0.1640  5
  test BA                     0.4933      0.5000     0.0137  5
  test AUC                    0.3036      0.2749     0.1387  5
  test AUC in-protein         0.4068      0.4544     0.3111  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3336      0.2688     0.3318  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4061      0.5517     0.2743  5
  test sensitivity            0.5818      0.7273     0.4662  5
  test specificity            0.4049      0.2683     0.4539  5
  test precision              0.4278      0.4452     0.0352  4
  test loss                   0.7380      0.7219     0.0521  5
  FPR (FP/(FP+TN))            0.5951      0.7317     0.4539  5
  FNR (FN/(FN+TP))            0.4182      0.2727     0.4662  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5583      0.5625     0.0297  5
  max valid BA                0.5597      0.5625     0.0280  5
  best valid F1               0.4926      0.5455     0.1040  5
  test BA                     0.5865      0.5833     0.0288  5
  test AUC                    0.4554      0.4392     0.1555  5
  test AUC in-protein         0.6917      0.8000     0.2394  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.6340      0.6364     0.1668  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3198      0.2857     0.0706  5
  test sensitivity            0.2000      0.1667     0.0543  5
  test specificity            0.9730      0.9730     0.0191  5
  test precision              0.8350      0.8333     0.1208  5
  test loss                   0.6961      0.6918     0.0317  5
  FPR (FP/(FP+TN))            0.0270      0.0270     0.0191  5
  FNR (FN/(FN+TP))            0.8000      0.8333     0.0543  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6475      0.6146     0.0884  5
  max valid BA                0.6579      0.6396     0.0904  5
  best valid F1               0.5805      0.5366     0.0890  5
  test BA                     0.6234      0.5907     0.0677  5
  test AUC                    0.6659      0.6381     0.1307  5
  test AUC in-protein         0.7638      0.7775     0.1506  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.7430      0.7059     0.0668  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5094      0.4571     0.0915  5
  test sensitivity            0.5500      0.5000     0.1425  5
  test specificity            0.6968      0.6774     0.0669  5
  test precision              0.4827      0.5000     0.0634  5
  test loss                   0.6454      0.6569     0.0527  5
  FPR (FP/(FP+TN))            0.3032      0.3226     0.0669  5
  FNR (FN/(FN+TP))            0.4500      0.5000     0.1425  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6769      0.6923     0.0534  5
  max valid BA                0.7000      0.7308     0.0617  5
  best valid F1               0.5990      0.6400     0.0816  5
  test BA                     0.6269      0.6346     0.1076  5
  test AUC                    0.6089      0.6331     0.0908  5
  test AUC in-protein         0.5542      0.7000     0.3823  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.5451      0.6364     0.3186  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.4894      0.5185     0.1794  5
  test sensitivity            0.4923      0.5385     0.1931  5
  test specificity            0.7615      0.7692     0.0740  5
  test precision              0.4939      0.5000     0.1638  5
  test loss                   0.6552      0.6654     0.0433  5
  FPR (FP/(FP+TN))            0.2385      0.2308     0.0740  5
  FNR (FN/(FN+TP))            0.5077      0.4615     0.1931  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5227      0.5227     0.0227  5
  max valid BA                0.5305      0.5227     0.0324  5
  best valid F1               0.4508      0.5253     0.1419  5
  test BA                     0.5192      0.5078     0.0256  5
  test AUC                    0.4648      0.4822     0.0847  5
  test AUC in-protein         0.4797      0.4316     0.2057  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4725      0.4500     0.1813  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3893      0.5253     0.2320  5
  test sensitivity            0.6294      0.8257     0.4450  5
  test specificity            0.4091      0.2741     0.4174  5
  test precision              0.2975      0.3673     0.1667  5
  test loss                   0.7171      0.6956     0.0596  5
  FPR (FP/(FP+TN))            0.5909      0.7259     0.4174  5
  FNR (FN/(FN+TP))            0.3706      0.1743     0.4450  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7438      0.7812     0.1395  5
  max valid BA                0.7488      0.7875     0.1423  5
  best valid F1               0.6886      0.7083     0.1110  5
  test BA                     0.7475      0.7875     0.1474  5
  test AUC                    0.8243      0.8666     0.1453  5
  test AUC in-protein         0.6615      0.5696     0.2413  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.6807      0.6866     0.1922  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.6858      0.7083     0.1182  5
  test sensitivity            0.9100      0.9500     0.0822  5
  test specificity            0.5850      0.7250     0.3295  5
  test precision              0.5654      0.6071     0.1394  5
  test loss                   0.5429      0.4921     0.1548  5
  FPR (FP/(FP+TN))            0.4150      0.2750     0.3295  5
  FNR (FN/(FN+TP))            0.0900      0.0500     0.0822  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6224      0.6487     0.0732  5
  max valid BA                0.6347      0.6662     0.0769  5
  best valid F1               0.5534      0.5741     0.0379  5
  test BA                     0.6350      0.6569     0.0839  5
  test AUC                    0.7265      0.7480     0.0710  5
  test AUC in-protein         0.5016      0.4918     0.1597  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4992      0.5543     0.1422  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.5566      0.5439     0.0501  5
  test sensitivity            0.6947      0.6491     0.1761  5
  test specificity            0.5752      0.7168     0.3309  5
  test precision              0.4942      0.5294     0.1076  5
  test loss                   0.6260      0.6036     0.1112  5
  FPR (FP/(FP+TN))            0.4248      0.2832     0.3309  5
  FNR (FN/(FN+TP))            0.3053      0.3509     0.1761  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5938      0.6250     0.0733  5
  max valid BA                0.6125      0.6562     0.0927  5
  best valid F1               0.4670      0.5333     0.1590  5
  test BA                     0.4875      0.5000     0.0171  5
  test AUC                    0.4859      0.4766     0.1319  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.6933      0.6667     0.2127  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.1976      0.2857     0.1882  5
  test sensitivity            0.2250      0.2500     0.2562  5
  test specificity            0.7500      0.7500     0.2688  5
  test precision              0.2448      0.3229     0.1635  4
  test loss                   0.6870      0.6927     0.0197  5
  FPR (FP/(FP+TN))            0.2500      0.2500     0.2688  5
  FNR (FN/(FN+TP))            0.7750      0.7500     0.2562  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_drop_pocket_elongation --seeds=0,1,2,3,4`
