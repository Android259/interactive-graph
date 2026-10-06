# mlp_sub_pb6_drop_hydropathy_rim

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_drop_hydropathy_rim'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.6788      0.3659      0.6335      0.5449      0.7212      0.4150
groups_FA                                    5      0.2833      0.8649      0.4761      0.7266      0.2000      0.9222
groups_LPC+LPE+LPG                           5      0.4875      0.6516      0.5661      0.7633      0.5625      0.7400
groups_PA                                    5      0.5692      0.8538      0.4622      0.7225      0.5692      0.9231
groups_PC                                    5      0.5101      0.5025      0.6654      0.4357      0.5890      0.4589
groups_PE                                    5      0.8150      0.7725      0.6527      0.7740      0.8200      0.7925
groups_PG                                    5      0.6596      0.7398      0.6495      0.6841      0.6714      0.7345
groups_PI                                    5      0.3500      0.5875      0.6252      0.5617      0.6000      0.6250
ALL                                         40      0.5442      0.6673      0.5913      0.6516      0.5917      0.7014

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6264      0.6000     0.1019  40
max valid BA                0.6465      0.6292     0.1013  40
best valid F1               0.5701      0.5760     0.1259  40
test BA                     0.6058      0.5718     0.1162  40
test AUC                    0.5835      0.5214     0.1794  40
test AUC in-protein         0.6132      0.5532     0.2208  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.5686      0.5475     0.2067  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.4807      0.5359     0.1974  40
test sensitivity            0.5442      0.5385     0.2820  40
test specificity            0.6673      0.7365     0.2688  40
test precision              0.4937      0.5000     0.1951  39
test loss                   0.6565      0.6836     0.0805  40
FPR (FP/(FP+TN))            0.3327      0.2635     0.2688  40
FNR (FN/(FN+TP))            0.4558      0.4615     0.2820  40

=== abs(sensitivity-specificity) gap: mean=0.3993 median=0.3101 n=40 ===
sensitivity std across seeds (by group): mean=0.1948 median=0.1683 n=8
specificity std across seeds (by group): mean=0.1860 median=0.1119 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5519      0.5545     0.0557  5
  max valid BA                0.5681      0.5545     0.0659  5
  best valid F1               0.6033      0.6316     0.0748  5
  test BA                     0.5223      0.5037     0.0300  5
  test AUC                    0.4599      0.4619     0.0417  5
  test AUC in-protein         0.4450      0.4565     0.0383  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3823      0.3548     0.1259  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4772      0.5714     0.2680  5
  test sensitivity            0.6788      0.7879     0.4012  5
  test specificity            0.3659      0.2195     0.3921  5
  test precision              0.4660      0.4590     0.0251  4
  test loss                   0.7128      0.6987     0.0267  5
  FPR (FP/(FP+TN))            0.6341      0.7805     0.3921  5
  FNR (FN/(FN+TP))            0.3212      0.2121     0.4012  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5444      0.5486     0.0248  5
  max valid BA                0.5611      0.5625     0.0180  5
  best valid F1               0.4599      0.4675     0.1317  5
  test BA                     0.5741      0.5709     0.0332  5
  test AUC                    0.4359      0.3908     0.0790  5
  test AUC in-protein         0.8167      0.8167     0.0192  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.6039      0.5714     0.1576  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3802      0.3810     0.0334  5
  test sensitivity            0.2833      0.2917     0.0349  5
  test specificity            0.8649      0.8919     0.0811  5
  test precision              0.6008      0.6000     0.1226  5
  test loss                   0.6913      0.6850     0.0202  5
  FPR (FP/(FP+TN))            0.1351      0.1081     0.0811  5
  FNR (FN/(FN+TP))            0.7167      0.7083     0.0349  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6146      0.6062     0.0595  5
  max valid BA                0.6512      0.6333     0.0532  5
  best valid F1               0.5590      0.5333     0.0631  5
  test BA                     0.5696      0.5726     0.0656  5
  test AUC                    0.6276      0.6935     0.1805  5
  test AUC in-protein         0.7230      0.8056     0.2089  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.6011      0.6667     0.1858  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.4496      0.4571     0.0868  5
  test sensitivity            0.4875      0.5000     0.1118  5
  test specificity            0.6516      0.6452     0.0924  5
  test precision              0.4241      0.4211     0.0951  5
  test loss                   0.6459      0.6805     0.0900  5
  FPR (FP/(FP+TN))            0.3484      0.3548     0.0924  5
  FNR (FN/(FN+TP))            0.5125      0.5000     0.1118  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7231      0.7115     0.0483  5
  max valid BA                0.7462      0.7500     0.0459  5
  best valid F1               0.6581      0.6667     0.0664  5
  test BA                     0.7115      0.7115     0.0490  5
  test AUC                    0.7053      0.6864     0.0407  5
  test AUC in-protein         0.6792      0.7583     0.3630  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.5990      0.7000     0.3390  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6146      0.6087     0.0698  5
  test sensitivity            0.5692      0.5385     0.0421  5
  test specificity            0.8538      0.8462     0.0740  5
  test precision              0.6758      0.6364     0.1323  5
  test loss                   0.6410      0.6753     0.0575  5
  FPR (FP/(FP+TN))            0.1462      0.1538     0.0740  5
  FNR (FN/(FN+TP))            0.4308      0.4615     0.0421  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5161      0.5161     0.0218  5
  max valid BA                0.5239      0.5227     0.0290  5
  best valid F1               0.4240      0.5253     0.1567  5
  test BA                     0.5063      0.5000     0.0257  5
  test AUC                    0.4407      0.4519     0.1032  5
  test AUC in-protein         0.4739      0.4721     0.2273  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4449      0.4621     0.1831  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3253      0.4154     0.2438  5
  test sensitivity            0.5101      0.4954     0.4693  5
  test specificity            0.5025      0.5076     0.4376  5
  test precision              0.2763      0.3562     0.1586  5
  test loss                   0.7154      0.6939     0.0611  5
  FPR (FP/(FP+TN))            0.4975      0.4924     0.4376  5
  FNR (FN/(FN+TP))            0.4899      0.5046     0.4693  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8000      0.8000     0.0207  5
  max valid BA                0.8063      0.8125     0.0182  5
  best valid F1               0.7342      0.7391     0.0189  5
  test BA                     0.7938      0.7875     0.0623  5
  test AUC                    0.8430      0.8616     0.1057  5
  test AUC in-protein         0.7471      0.7514     0.1753  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.6965      0.7164     0.1633  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7078      0.7083     0.0799  5
  test sensitivity            0.8150      0.9000     0.2247  5
  test specificity            0.7725      0.7250     0.1315  5
  test precision              0.6860      0.6452     0.1518  5
  test loss                   0.5459      0.5521     0.1029  5
  FPR (FP/(FP+TN))            0.2275      0.2750     0.1315  5
  FNR (FN/(FN+TP))            0.1850      0.1000     0.2247  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6860      0.6843     0.0352  5
  max valid BA                0.7030      0.7022     0.0261  5
  best valid F1               0.6060      0.6094     0.0372  5
  test BA                     0.6997      0.7005     0.0299  5
  test AUC                    0.7383      0.7359     0.0676  5
  test AUC in-protein         0.4837      0.4730     0.0363  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4882      0.4762     0.0331  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6073      0.6094     0.0340  5
  test sensitivity            0.6596      0.6491     0.0342  5
  test specificity            0.7398      0.7434     0.0555  5
  test precision              0.5650      0.5645     0.0522  5
  test loss                   0.5991      0.6075     0.0636  5
  FPR (FP/(FP+TN))            0.2602      0.2566     0.0555  5
  FNR (FN/(FN+TP))            0.3404      0.3509     0.0342  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5750      0.5938     0.0419  5
  max valid BA                0.6125      0.6250     0.0568  5
  best valid F1               0.5164      0.5000     0.0712  5
  test BA                     0.4688      0.4688     0.0312  5
  test AUC                    0.4172      0.4141     0.0597  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.7333      0.6667     0.1900  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.2836      0.3158     0.1679  5
  test sensitivity            0.3500      0.3750     0.2404  5
  test specificity            0.5875      0.5000     0.2236  5
  test precision              0.2504      0.3125     0.1421  5
  test loss                   0.7010      0.6976     0.0110  5
  FPR (FP/(FP+TN))            0.4125      0.5000     0.2236  5
  FNR (FN/(FN+TP))            0.6500      0.6250     0.2404  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_drop_hydropathy_rim --seeds=0,1,2,3,4`
