# mlp_sub_pb6_keep5_tef

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_keep5_tef'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.5455      0.4390      0.4905      0.5486      0.5697      0.4900
groups_FA                                    5      0.6000      0.5730      0.7198      0.4934      0.6500      0.5889
groups_LPC+LPE+LPG                           5      0.7500      0.5161      0.4379      0.7658      0.7250      0.6533
groups_PA                                    5      0.5538      0.8538      0.5822      0.6476      0.5231      0.9538
groups_PC                                    5      0.2936      0.7665      0.3053      0.7557      0.2312      0.8284
groups_PE                                    5      0.8400      0.7325      0.5708      0.6841      0.8750      0.7225
groups_PG                                    5      0.7719      0.6832      0.5678      0.6558      0.7571      0.6619
groups_PI                                    5      0.1500      0.8000      0.4246      0.6036      0.3500      0.7625
ALL                                         40      0.5631      0.6705      0.5123      0.6443      0.5851      0.7077

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6329      0.6537     0.1146  40
max valid BA                0.6464      0.6691     0.1136  40
best valid F1               0.5530      0.6020     0.1750  40
test BA                     0.6168      0.6092     0.1222  40
test AUC                    0.5954      0.5807     0.1756  40
test AUC in-protein         0.5026      0.5000     0.0119  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.4998      0.5000     0.0148  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.4684      0.5532     0.2514  40
test sensitivity            0.5631      0.6154     0.3445  40
test specificity            0.6705      0.7102     0.2957  40
test precision              0.5164      0.5000     0.1645  34
test loss                   0.6663      0.6749     0.0383  40
FPR (FP/(FP+TN))            0.3295      0.2898     0.2957  40
FNR (FN/(FN+TP))            0.4369      0.3846     0.3445  40

=== abs(sensitivity-specificity) gap: mean=0.4762 median=0.3888 n=40 ===
sensitivity std across seeds (by group): mean=0.2339 median=0.2492 n=8
specificity std across seeds (by group): mean=0.2417 median=0.2029 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5048      0.5000     0.0070  5
  max valid BA                0.5298      0.5000     0.0586  5
  best valid F1               0.5825      0.6226     0.0785  5
  test BA                     0.4922      0.5000     0.0174  5
  test AUC                    0.5290      0.5503     0.1458  5
  test AUC in-protein         0.5050      0.5000     0.0112  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.5035      0.5000     0.0079  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3534      0.5333     0.3244  5
  test sensitivity            0.5455      0.7273     0.5102  5
  test specificity            0.4390      0.1951     0.5183  5
  test precision              0.4376      0.4459     0.0144  3
  test loss                   0.6974      0.6979     0.0063  5
  FPR (FP/(FP+TN))            0.5610      0.8049     0.5183  5
  FNR (FN/(FN+TP))            0.4545      0.2727     0.5102  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5972      0.5972     0.0722  5
  max valid BA                0.6194      0.6667     0.0876  5
  best valid F1               0.5631      0.5714     0.0869  5
  test BA                     0.5865      0.5805     0.0670  5
  test AUC                    0.4991      0.5518     0.1180  5
  test AUC in-protein         0.5000      0.5000     0.0000  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.5000      0.5000     0.0000  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.5268      0.5417     0.0566  5
  test sensitivity            0.6000      0.5417     0.2275  5
  test specificity            0.5730      0.7027     0.3257  5
  test precision              0.5087      0.5000     0.0961  5
  test loss                   0.6990      0.6931     0.0270  5
  FPR (FP/(FP+TN))            0.4270      0.2973     0.3257  5
  FNR (FN/(FN+TP))            0.4000      0.4583     0.2275  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6442      0.6833     0.0919  5
  max valid BA                0.6892      0.7000     0.0795  5
  best valid F1               0.6023      0.6400     0.1100  5
  test BA                     0.6331      0.6462     0.0540  5
  test AUC                    0.6315      0.5746     0.1714  5
  test AUC in-protein         0.5000      0.5000     0.0000  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.5000      0.5000     0.0000  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5404      0.5882     0.0921  5
  test sensitivity            0.7500      0.9375     0.2898  5
  test specificity            0.5161      0.4194     0.2015  5
  test precision              0.4498      0.4286     0.0342  5
  test loss                   0.6813      0.6750     0.0106  5
  FPR (FP/(FP+TN))            0.4839      0.5806     0.2015  5
  FNR (FN/(FN+TP))            0.2500      0.0625     0.2898  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7385      0.7500     0.0349  5
  max valid BA                0.7385      0.7500     0.0349  5
  best valid F1               0.6467      0.6667     0.0581  5
  test BA                     0.7038      0.6923     0.0845  5
  test AUC                    0.6142      0.6642     0.1003  5
  test AUC in-protein         0.5000      0.5000     0.0000  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.5000      0.5000     0.0000  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6094      0.5714     0.1121  5
  test sensitivity            0.5538      0.5385     0.0644  5
  test specificity            0.8538      0.9231     0.1371  5
  test precision              0.7007      0.7500     0.2055  5
  test loss                   0.6345      0.6365     0.0452  5
  FPR (FP/(FP+TN))            0.1462      0.0769     0.1371  5
  FNR (FN/(FN+TP))            0.4462      0.4615     0.0644  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5230      0.5053     0.0417  5
  max valid BA                0.5298      0.5053     0.0541  5
  best valid F1               0.3656      0.3273     0.1725  5
  test BA                     0.5300      0.5051     0.0587  5
  test AUC                    0.4525      0.4386     0.1301  5
  test AUC in-protein         0.5013      0.4939     0.0260  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4898      0.4913     0.0428  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.2316      0.1504     0.2565  5
  test sensitivity            0.2936      0.0917     0.4240  5
  test specificity            0.7665      0.9289     0.4253  5
  test precision              0.4788      0.4167     0.1607  3
  test loss                   0.6842      0.6824     0.0188  5
  FPR (FP/(FP+TN))            0.2335      0.0711     0.4253  5
  FNR (FN/(FN+TP))            0.7064      0.9083     0.4240  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7987      0.8000     0.0458  5
  max valid BA                0.7987      0.8000     0.0458  5
  best valid F1               0.7204      0.7170     0.0510  5
  test BA                     0.7863      0.7812     0.0143  5
  test AUC                    0.8386      0.8414     0.0135  5
  test AUC in-protein         0.5101      0.5000     0.0139  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.5058      0.5000     0.0079  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7079      0.7021     0.0182  5
  test sensitivity            0.8400      0.8250     0.0335  5
  test specificity            0.7325      0.7125     0.0481  5
  test precision              0.6136      0.6034     0.0392  5
  test loss                   0.6122      0.6106     0.0089  5
  FPR (FP/(FP+TN))            0.2675      0.2875     0.0481  5
  FNR (FN/(FN+TP))            0.1600      0.1750     0.0335  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7006      0.7021     0.0400  5
  max valid BA                0.7095      0.7021     0.0342  5
  best valid F1               0.6221      0.6080     0.0357  5
  test BA                     0.7276      0.7270     0.0239  5
  test AUC                    0.7682      0.7678     0.0271  5
  test AUC in-protein         0.5000      0.5000     0.0000  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4995      0.5000     0.0010  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6440      0.6400     0.0239  5
  test sensitivity            0.7719      0.7895     0.0511  5
  test specificity            0.6832      0.6991     0.0736  5
  test precision              0.5555      0.5696     0.0409  5
  test loss                   0.6378      0.6371     0.0305  5
  FPR (FP/(FP+TN))            0.3168      0.3009     0.0736  5
  FNR (FN/(FN+TP))            0.2281      0.2105     0.0511  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5563      0.5000     0.0948  5
  max valid BA                0.5563      0.5000     0.0948  5
  best valid F1               0.3209      0.2857     0.2616  5
  test BA                     0.4750      0.5000     0.1022  5
  test AUC                    0.4305      0.3750     0.1344  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.5000      0.5000     0.0000  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.1333      0.0000     0.2173  5
  test sensitivity            0.1500      0.0000     0.2710  5
  test specificity            0.8000      0.8125     0.2044  5
  test precision              0.2222      0.2500     0.2097  3
  test loss                   0.6844      0.6943     0.0205  5
  FPR (FP/(FP+TN))            0.2000      0.1875     0.2044  5
  FNR (FN/(FN+TP))            0.8500      1.0000     0.2710  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_keep5_tef --seeds=0,1,2,3,4`
