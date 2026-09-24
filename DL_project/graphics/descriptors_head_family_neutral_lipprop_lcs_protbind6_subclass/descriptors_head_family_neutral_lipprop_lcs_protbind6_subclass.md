# descriptors_head_family_neutral_lipprop_lcs_protbind6_subclass

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_head_family_neutral_lipprop_lcs_protbind6_subclass'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.5818      0.5317      0.4074      0.6864      0.5697      0.6400
groups_FA                                    5      0.4083      0.6865      0.3689      0.7750      0.4000      0.7389
groups_LPC+LPE+LPG                           5      0.8250      0.6194      0.5153      0.6940      0.8500      0.6467
groups_PA                                    5      0.5538      0.9385      0.4069      0.7090      0.6000      0.9154
groups_PC                                    5      0.4275      0.6782      0.6447      0.4739      0.5321      0.6558
groups_PE                                    5      0.6350      0.7875      0.4368      0.7006      0.7100      0.8000
groups_PG                                    5      0.7298      0.7097      0.5578      0.6688      0.7464      0.7292
groups_PI                                    5      0.5250      0.5500      0.5294      0.5083      0.5750      0.6500
groups_PS+PGP+DAG+TAG                        5      0.2000      0.7467      0.3974      0.6857      0.2250      0.8125
ALL                                         45      0.5429      0.6942      0.4739      0.6557      0.5787      0.7321

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6368      0.6806     0.1085  45
max valid BA                0.6554      0.6875     0.1101  45
best valid F1               0.5695      0.6016     0.1334  45
test BA                     0.6186      0.6242     0.1184  45
test AUC                    0.6138      0.6351     0.1491  45
test AUC in-protein         0.5661      0.5877     0.2436  32
  (proteins averaged)       3.0000      2.0000     3.5162  45
test AUC in-protein (pairs)      0.5305      0.5972     0.2243  45
  (proteins contributing)      5.4444      3.0000     4.0819  45
test F1                     0.4917      0.5303     0.1995  45
test sensitivity            0.5429      0.6154     0.2726  45
test specificity            0.6942      0.7333     0.2406  45
test precision              0.5469      0.5000     0.2101  43
test loss                   0.7193      0.6745     0.1829  45
FPR (FP/(FP+TN))            0.3058      0.2667     0.2406  45
FNR (FN/(FN+TP))            0.4571      0.3846     0.2726  45

=== abs(sensitivity-specificity) gap: mean=0.3872 median=0.3250 n=45 ===
sensitivity std across seeds (by group): mean=0.2077 median=0.2044 n=9
specificity std across seeds (by group): mean=0.1947 median=0.1726 n=9

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5798      0.5939     0.1088  5
  max valid BA                0.6048      0.5939     0.0953  5
  best valid F1               0.5808      0.6222     0.0805  5
  test BA                     0.5568      0.5632     0.0663  5
  test AUC                    0.5967      0.5935     0.0672  5
  test AUC in-protein         0.6355      0.5036     0.2061  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.7274      0.7110     0.1166  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5078      0.4878     0.1196  5
  test sensitivity            0.5818      0.6061     0.3101  5
  test specificity            0.5317      0.3171     0.3540  5
  test precision              0.5779      0.5000     0.1926  5
  test loss                   0.7183      0.6828     0.0730  5
  FPR (FP/(FP+TN))            0.4683      0.6829     0.3540  5
  FNR (FN/(FN+TP))            0.4182      0.3939     0.3101  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5569      0.5556     0.0780  5
  max valid BA                0.5694      0.5625     0.0725  5
  best valid F1               0.4644      0.4667     0.1191  5
  test BA                     0.5474      0.5417     0.0303  5
  test AUC                    0.5358      0.5462     0.0735  5
  test AUC in-protein         0.3333      0.1833     0.3115  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.4156      0.5000     0.1818  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3969      0.4324     0.1443  5
  test sensitivity            0.4083      0.3333     0.2401  5
  test specificity            0.6865      0.7568     0.2713  5
  test precision              0.5826      0.4706     0.2475  5
  test loss                   0.6857      0.6909     0.0277  5
  FPR (FP/(FP+TN))            0.3135      0.2432     0.2713  5
  FNR (FN/(FN+TP))            0.5917      0.6667     0.2401  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7150      0.7500     0.0641  5
  max valid BA                0.7483      0.7667     0.0579  5
  best valid F1               0.6686      0.6957     0.0775  5
  test BA                     0.7222      0.7419     0.0784  5
  test AUC                    0.7498      0.7702     0.0544  5
  test AUC in-protein         0.7291      0.7222     0.0984  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.6264      0.6364     0.0645  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.6379      0.6667     0.0964  5
  test sensitivity            0.8250      0.9375     0.2044  5
  test specificity            0.6194      0.6452     0.1194  5
  test precision              0.5306      0.5000     0.0735  5
  test loss                   0.6614      0.6759     0.0345  5
  FPR (FP/(FP+TN))            0.3806      0.3548     0.1194  5
  FNR (FN/(FN+TP))            0.1750      0.0625     0.2044  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7385      0.7500     0.0349  5
  max valid BA                0.7577      0.7500     0.0349  5
  best valid F1               0.6784      0.6667     0.0518  5
  test BA                     0.7462      0.7500     0.0672  5
  test AUC                    0.6574      0.6627     0.0347  5
  test AUC in-protein         0.4417      0.3833     0.4500  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.4539      0.6364     0.3083  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6570      0.6667     0.1093  5
  test sensitivity            0.5538      0.5385     0.1141  5
  test specificity            0.9385      0.9615     0.0344  5
  test precision              0.8156      0.8750     0.0996  5
  test loss                   0.6309      0.6242     0.0263  5
  FPR (FP/(FP+TN))            0.0615      0.0385     0.0344  5
  FNR (FN/(FN+TP))            0.4462      0.4615     0.1141  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5733      0.5365     0.0799  5
  max valid BA                0.5940      0.6108     0.0720  5
  best valid F1               0.4949      0.5224     0.0984  5
  test BA                     0.5528      0.5125     0.0653  5
  test AUC                    0.5547      0.5414     0.0362  5
  test AUC in-protein         0.4769      0.4723     0.0816  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4910      0.5214     0.0561  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3728      0.3863     0.2251  5
  test sensitivity            0.4275      0.4128     0.2755  5
  test specificity            0.6782      0.5990     0.1818  5
  test precision              0.4168      0.4116     0.0585  4
  test loss                   0.7730      0.7336     0.1231  5
  FPR (FP/(FP+TN))            0.3218      0.4010     0.1818  5
  FNR (FN/(FN+TP))            0.5725      0.5872     0.2755  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7300      0.7375     0.0615  5
  max valid BA                0.7550      0.7688     0.0758  5
  best valid F1               0.6873      0.6944     0.0845  5
  test BA                     0.7112      0.6937     0.0547  5
  test AUC                    0.7814      0.7803     0.0184  5
  test AUC in-protein         0.7351      0.6974     0.1378  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7022      0.7313     0.1203  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.6144      0.5952     0.0695  5
  test sensitivity            0.6350      0.6250     0.1294  5
  test specificity            0.7875      0.7625     0.0980  5
  test precision              0.6138      0.6333     0.0928  5
  test loss                   0.6227      0.6166     0.0236  5
  FPR (FP/(FP+TN))            0.2125      0.2375     0.0980  5
  FNR (FN/(FN+TP))            0.3650      0.3750     0.1294  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7254      0.7111     0.0351  5
  max valid BA                0.7378      0.7469     0.0338  5
  best valid F1               0.6532      0.6618     0.0398  5
  test BA                     0.7198      0.7226     0.0450  5
  test AUC                    0.7287      0.7323     0.0345  5
  test AUC in-protein         0.5720      0.6243     0.1087  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.5682      0.6076     0.0866  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6353      0.6349     0.0502  5
  test sensitivity            0.7298      0.7368     0.0520  5
  test specificity            0.7097      0.7257     0.0886  5
  test precision              0.5668      0.5542     0.0739  5
  test loss                   0.6455      0.6522     0.0261  5
  FPR (FP/(FP+TN))            0.2903      0.2743     0.0886  5
  FNR (FN/(FN+TP))            0.2702      0.2632     0.0520  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6062      0.5625     0.1050  5
  max valid BA                0.6125      0.5625     0.1003  5
  best valid F1               0.5151      0.4800     0.1254  5
  test BA                     0.5375      0.4688     0.1277  5
  test AUC                    0.4266      0.4375     0.1957  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.3600      0.3000     0.2994  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.3854      0.4286     0.2334  5
  test sensitivity            0.5250      0.7500     0.3791  5
  test specificity            0.5500      0.6875     0.4317  5
  test precision              0.4327      0.3182     0.3717  5
  test loss                   1.0433      1.1039     0.4152  5
  FPR (FP/(FP+TN))            0.4500      0.3125     0.4317  5
  FNR (FN/(FN+TP))            0.4750      0.2500     0.3791  5

groups_PS+PGP+DAG+TAG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5062      0.4688     0.0559  5
  max valid BA                0.5188      0.4688     0.0685  5
  best valid F1               0.3824      0.3636     0.1031  5
  test BA                     0.4733      0.4778     0.0651  5
  test AUC                    0.4933      0.4444     0.1945  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.4300      0.4000     0.3457  5
    (proteins contributing)      2.6000      3.0000     0.8944  5
  test F1                     0.2174      0.2222     0.1623  5
  test sensitivity            0.2000      0.2222     0.1648  5
  test specificity            0.7467      0.7333     0.1726  5
  test precision              0.3125      0.2917     0.0998  4
  test loss                   0.6934      0.6967     0.0433  5
  FPR (FP/(FP+TN))            0.2533      0.2667     0.1726  5
  FNR (FN/(FN+TP))            0.8000      0.7778     0.1648  5
```

## AUC vs chemistry null model, in-sample increment

