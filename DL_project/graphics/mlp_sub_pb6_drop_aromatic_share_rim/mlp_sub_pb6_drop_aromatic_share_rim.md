# mlp_sub_pb6_drop_aromatic_share_rim

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_drop_aromatic_share_rim'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.6000      0.3610      0.5173      0.6109      0.6061      0.4600
groups_FA                                    5      0.3167      0.7784      0.7232      0.6581      0.2750      0.8278
groups_LPC+LPE+LPG                           5      0.6875      0.5742      0.5741      0.7078      0.8125      0.5800
groups_PA                                    5      0.5846      0.8538      0.5878      0.6771      0.5846      0.9000
groups_PC                                    5      0.5780      0.4376      0.6120      0.4859      0.5596      0.4914
groups_PE                                    5      0.8800      0.7700      0.6949      0.7445      0.9100      0.7725
groups_PG                                    5      0.6632      0.7717      0.6714      0.7161      0.6750      0.7540
groups_PI                                    5      0.2500      0.7250      0.5693      0.6299      0.4000      0.7500
ALL                                         40      0.5700      0.6590      0.6187      0.6538      0.6029      0.6920

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6343      0.6062     0.1179  40
max valid BA                0.6474      0.6427     0.1162  40
best valid F1               0.5712      0.5938     0.1445  40
test BA                     0.6145      0.5707     0.1294  40
test AUC                    0.5963      0.5718     0.2063  40
test AUC in-protein         0.6147      0.5814     0.2239  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.6018      0.5917     0.2097  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.4872      0.5397     0.2241  40
test sensitivity            0.5700      0.6202     0.3012  40
test specificity            0.6590      0.7397     0.2815  40
test precision              0.4985      0.5000     0.1864  38
test loss                   0.6486      0.6781     0.0915  40
FPR (FP/(FP+TN))            0.3410      0.2603     0.2815  40
FNR (FN/(FN+TP))            0.4300      0.3798     0.3012  40

=== abs(sensitivity-specificity) gap: mean=0.4133 median=0.3293 n=40 ===
sensitivity std across seeds (by group): mean=0.2111 median=0.1954 n=8
specificity std across seeds (by group): mean=0.2068 median=0.1742 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5211      0.5091     0.0276  5
  max valid BA                0.5330      0.5261     0.0307  5
  best valid F1               0.5843      0.6226     0.0650  5
  test BA                     0.4805      0.4885     0.0411  5
  test AUC                    0.3860      0.3991     0.0507  5
  test AUC in-protein         0.4015      0.4180     0.0825  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3632      0.3389     0.0968  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4345      0.5333     0.2492  5
  test sensitivity            0.6000      0.7273     0.3594  5
  test specificity            0.3610      0.2195     0.3611  5
  test precision              0.4275      0.4298     0.0315  4
  test loss                   0.7095      0.7024     0.0151  5
  FPR (FP/(FP+TN))            0.6390      0.7805     0.3611  5
  FNR (FN/(FN+TP))            0.4000      0.2727     0.3594  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5472      0.5486     0.0124  5
  max valid BA                0.5514      0.5556     0.0105  5
  best valid F1               0.4733      0.4789     0.1000  5
  test BA                     0.5475      0.5428     0.0249  5
  test AUC                    0.3881      0.3457     0.1146  5
  test AUC in-protein         0.8583      0.8167     0.0957  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.7089      0.6429     0.1665  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3518      0.3415     0.1187  5
  test sensitivity            0.3167      0.2500     0.2255  5
  test specificity            0.7784      0.8919     0.2088  5
  test precision              0.5204      0.5714     0.0847  5
  test loss                   0.7579      0.7437     0.0876  5
  FPR (FP/(FP+TN))            0.2216      0.1081     0.2088  5
  FNR (FN/(FN+TP))            0.6833      0.7500     0.2255  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6613      0.6687     0.0537  5
  max valid BA                0.6963      0.7000     0.0497  5
  best valid F1               0.6197      0.6400     0.0610  5
  test BA                     0.6308      0.6210     0.0681  5
  test AUC                    0.7034      0.6915     0.1039  5
  test AUC in-protein         0.7176      0.7396     0.1298  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.5892      0.6000     0.1549  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5444      0.5128     0.0732  5
  test sensitivity            0.6875      0.6250     0.1654  5
  test specificity            0.5742      0.5806     0.1395  5
  test precision              0.4610      0.4545     0.0663  5
  test loss                   0.6424      0.6438     0.0626  5
  FPR (FP/(FP+TN))            0.4258      0.4194     0.1395  5
  FNR (FN/(FN+TP))            0.3125      0.3750     0.1654  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7385      0.7500     0.0463  5
  max valid BA                0.7423      0.7500     0.0399  5
  best valid F1               0.6547      0.6667     0.0561  5
  test BA                     0.7192      0.7115     0.0674  5
  test AUC                    0.7692      0.7485     0.1062  5
  test AUC in-protein         0.6792      0.7583     0.3630  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.7283      0.7778     0.2319  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6307      0.6087     0.0920  5
  test sensitivity            0.5846      0.6154     0.0421  5
  test specificity            0.8538      0.8846     0.1198  5
  test precision              0.7032      0.7000     0.1853  5
  test loss                   0.6132      0.6113     0.0523  5
  FPR (FP/(FP+TN))            0.1462      0.1154     0.1198  5
  FNR (FN/(FN+TP))            0.4154      0.3846     0.0421  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5199      0.5025     0.0338  5
  max valid BA                0.5255      0.5120     0.0350  5
  best valid F1               0.4260      0.5266     0.1569  5
  test BA                     0.5078      0.5000     0.0317  5
  test AUC                    0.4558      0.4326     0.0714  5
  test AUC in-protein         0.4950      0.4449     0.1721  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4574      0.4321     0.1362  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3534      0.4956     0.2447  5
  test sensitivity            0.5780      0.7706     0.4719  5
  test specificity            0.4376      0.2589     0.4315  5
  test precision              0.2785      0.3562     0.1602  5
  test loss                   0.6959      0.6960     0.0182  5
  FPR (FP/(FP+TN))            0.5624      0.7411     0.4315  5
  FNR (FN/(FN+TP))            0.4220      0.2294     0.4719  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8375      0.8187     0.0337  5
  max valid BA                0.8413      0.8313     0.0311  5
  best valid F1               0.7699      0.7579     0.0373  5
  test BA                     0.8250      0.8375     0.0385  5
  test AUC                    0.8909      0.9038     0.0570  5
  test AUC in-protein         0.7744      0.7750     0.1170  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7705      0.7792     0.1106  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7523      0.7600     0.0447  5
  test sensitivity            0.8800      0.8750     0.0597  5
  test specificity            0.7700      0.7625     0.0411  5
  test precision              0.6580      0.6415     0.0460  5
  test loss                   0.4869      0.4778     0.0466  5
  FPR (FP/(FP+TN))            0.2300      0.2375     0.0411  5
  FNR (FN/(FN+TP))            0.1200      0.1250     0.0597  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7056      0.7024     0.0235  5
  max valid BA                0.7145      0.7151     0.0175  5
  best valid F1               0.6220      0.6182     0.0208  5
  test BA                     0.7174      0.7272     0.0530  5
  test AUC                    0.7540      0.7621     0.0492  5
  test AUC in-protein         0.4591      0.4629     0.0962  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4632      0.4651     0.0783  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6273      0.6379     0.0669  5
  test sensitivity            0.6632      0.6491     0.0717  5
  test specificity            0.7717      0.7611     0.0510  5
  test precision              0.5965      0.5833     0.0720  5
  test loss                   0.5975      0.5890     0.0411  5
  FPR (FP/(FP+TN))            0.2283      0.2389     0.0510  5
  FNR (FN/(FN+TP))            0.3368      0.3509     0.0717  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5437      0.5312     0.0474  5
  max valid BA                0.5750      0.5625     0.0648  5
  best valid F1               0.4194      0.5000     0.1560  5
  test BA                     0.4875      0.5000     0.0356  5
  test AUC                    0.4234      0.4141     0.0614  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.7333      0.6667     0.2528  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.2033      0.2000     0.2043  5
  test sensitivity            0.2500      0.1250     0.2932  5
  test specificity            0.7250      0.8750     0.3017  5
  test precision              0.2865      0.3229     0.2086  4
  test loss                   0.6857      0.6940     0.0362  5
  FPR (FP/(FP+TN))            0.2750      0.1250     0.3017  5
  FNR (FN/(FN+TP))            0.7500      0.8750     0.2932  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_drop_aromatic_share_rim --seeds=0,1,2,3,4`
