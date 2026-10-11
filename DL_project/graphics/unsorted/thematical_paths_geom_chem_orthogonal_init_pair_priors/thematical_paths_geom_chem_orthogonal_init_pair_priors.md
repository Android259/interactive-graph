# thematical_paths_geom_chem_orthogonal_init_pair_priors

## Summary (analysis/summarize_label.py)

```
Summary: 'thematical_paths_geom_chem_orthogonal_init_pair_priors'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4239      0.6066      0.8931      0.6337      0.4776      0.6097
groups_GLTP            5      0.5920      0.6880      0.8473      0.6869      0.5846      0.7385
groups_IP_trans        5      0.3043      0.7617      0.7168      0.7697      0.3500      0.7787
groups_LBP_BPI_CETP    5      0.4261      0.8170      0.8454      0.6928      0.4667      0.8426
groups_START           5      0.6031      0.4337      0.8014      0.6386      0.6719      0.4809
groups_lipocalin       5      0.6333      0.4944      0.9144      0.6150      0.6222      0.4583
groups_scp2            5      0.5294      0.7882      0.7991      0.7688      0.5059      0.7706
ALL                   35      0.5017      0.6557      0.8311      0.6865      0.5256      0.6685

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5966      0.5820     0.0858  35
max valid BA                0.6246      0.6042     0.0862  35
best valid F1               0.5784      0.5714     0.1082  35
test BA                     0.5787      0.5600     0.0940  35
test F1                     0.4609      0.5000     0.1752  35
test sensitivity            0.5017      0.5075     0.2799  35
test specificity            0.6557      0.7660     0.2943  35
test precision              0.5426      0.5430     0.1553  34
test loss                   0.7683      0.7034     0.2012  35
FPR (FP/(FP+TN))            0.3443      0.2340     0.2943  35
FNR (FN/(FN+TP))            0.4983      0.4925     0.2799  35

=== abs(sensitivity-specificity) gap: mean=0.4650 median=0.4306 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5436      0.5277     0.0468  5
  max valid BA                0.5626      0.5835     0.0468  5
  best valid F1               0.6137      0.6667     0.0964  5
  test BA                     0.5152      0.5078     0.0152  5
  test F1                     0.4201      0.3711     0.1850  5
  test sensitivity            0.4239      0.2687     0.3511  5
  test specificity            0.6066      0.8033     0.3715  5
  test precision              0.5672      0.5385     0.0520  5
  test loss                   1.0030      1.0149     0.3509  5
  FPR (FP/(FP+TN))            0.3934      0.1967     0.3715  5
  FNR (FN/(FN+TP))            0.5761      0.7313     0.3511  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6615      0.6154     0.1174  5
  max valid BA                0.6885      0.6538     0.1133  5
  best valid F1               0.7047      0.6909     0.1191  5
  test BA                     0.6400      0.6200     0.1503  5
  test F1                     0.6090      0.6122     0.2037  5
  test sensitivity            0.5920      0.6000     0.2339  5
  test specificity            0.6880      0.6400     0.1947  5
  test precision              0.6539      0.6176     0.2042  5
  test loss                   0.7242      0.6937     0.2796  5
  FPR (FP/(FP+TN))            0.3120      0.3600     0.1947  5
  FNR (FN/(FN+TP))            0.4080      0.4000     0.2339  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5644      0.5625     0.0549  5
  max valid BA                0.5809      0.5922     0.0619  5
  best valid F1               0.4611      0.5053     0.0802  5
  test BA                     0.5330      0.5435     0.0312  5
  test F1                     0.2528      0.2759     0.1858  5
  test sensitivity            0.3043      0.1739     0.4008  5
  test specificity            0.7617      0.9574     0.4301  5
  test precision              0.6142      0.5641     0.2924  4
  test loss                   0.7631      0.7215     0.0986  5
  FPR (FP/(FP+TN))            0.2383      0.0426     0.4301  5
  FNR (FN/(FN+TP))            0.6957      0.8261     0.4008  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6546      0.6556     0.1047  5
  max valid BA                0.6771      0.6644     0.0894  5
  best valid F1               0.5732      0.5667     0.1129  5
  test BA                     0.6216      0.5786     0.0942  5
  test F1                     0.4508      0.4186     0.1545  5
  test sensitivity            0.4261      0.3913     0.2409  5
  test specificity            0.8170      0.7872     0.0959  5
  test precision              0.5385      0.5758     0.1223  5
  test loss                   0.7355      0.6915     0.1404  5
  FPR (FP/(FP+TN))            0.1830      0.2128     0.0959  5
  FNR (FN/(FN+TP))            0.5739      0.6087     0.2409  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5764      0.5710     0.0243  5
  max valid BA                0.5801      0.5864     0.0253  5
  best valid F1               0.5871      0.5899     0.0351  5
  test BA                     0.5184      0.5298     0.0809  5
  test F1                     0.4706      0.5444     0.1691  5
  test sensitivity            0.6031      0.7077     0.3248  5
  test specificity            0.4337      0.3483     0.2745  5
  test precision              0.4492      0.4423     0.0879  5
  test loss                   0.7454      0.7014     0.1015  5
  FPR (FP/(FP+TN))            0.5663      0.6517     0.2745  5
  FNR (FN/(FN+TP))            0.3969      0.2923     0.3248  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5403      0.5139     0.0753  5
  max valid BA                0.5917      0.5625     0.0661  5
  best valid F1               0.5152      0.5124     0.0499  5
  test BA                     0.5639      0.5625     0.0876  5
  test F1                     0.4794      0.4444     0.0685  5
  test sensitivity            0.6333      0.6389     0.2302  5
  test specificity            0.4944      0.6250     0.3416  5
  test precision              0.4221      0.4000     0.1070  5
  test loss                   0.7720      0.7952     0.0720  5
  FPR (FP/(FP+TN))            0.5056      0.3750     0.3416  5
  FNR (FN/(FN+TP))            0.3667      0.3611     0.2302  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6353      0.6471     0.0753  5
  max valid BA                0.6912      0.7206     0.0785  5
  best valid F1               0.5942      0.6250     0.0953  5
  test BA                     0.6588      0.6618     0.0263  5
  test F1                     0.5435      0.5455     0.0247  5
  test sensitivity            0.5294      0.5294     0.0416  5
  test specificity            0.7882      0.7941     0.0842  5
  test precision              0.5676      0.5625     0.0721  5
  test loss                   0.6350      0.6292     0.0484  5
  FPR (FP/(FP+TN))            0.2118      0.2059     0.0842  5
  FNR (FN/(FN+TP))            0.4706      0.4706     0.0416  5
```

## AUC vs chemistry null model, in-sample increment

