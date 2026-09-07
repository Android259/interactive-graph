# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_pair_broadcast

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_pair_broadcast'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4507      0.6852      0.6920      0.6804      0.4657      0.6806
groups_GLTP            5      0.2480      0.6800      0.5345      0.6886      0.3769      0.7385
groups_IP_trans        5      0.3304      0.8170      0.6793      0.6551      0.4083      0.8383
groups_LBP_BPI_CETP    5      0.4261      0.8511      0.7216      0.6322      0.4417      0.8255
groups_START           5      0.0708      0.8539      0.6471      0.6474      0.1250      0.8719
groups_lipocalin       5      0.2333      0.8000      0.5896      0.6474      0.2667      0.8083
groups_scp2            5      0.4000      0.7000      0.6314      0.5591      0.4824      0.6882
ALL                   35      0.3085      0.7696      0.6422      0.6443      0.3667      0.7788

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5722      0.5577     0.0607  35
max valid BA                0.6028      0.5769     0.0715  35
best valid F1               0.5236      0.5306     0.1302  35
test BA                     0.5390      0.5147     0.0845  35
test F1                     0.3206      0.3200     0.2059  35
test sensitivity            0.3085      0.2353     0.2561  35
test specificity            0.7696      0.8085     0.1870  35
test precision              0.4392      0.4556     0.1978  34
test loss                   0.7157      0.6844     0.1759  35
FPR (FP/(FP+TN))            0.2304      0.1915     0.1870  35
FNR (FN/(FN+TP))            0.6915      0.7647     0.2561  35

=== abs(sensitivity-specificity) gap: mean=0.5481 median=0.5838 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5732      0.5662     0.0270  5
  max valid BA                0.6000      0.5986     0.0342  5
  best valid F1               0.6533      0.6835     0.0730  5
  test BA                     0.5680      0.5774     0.0233  5
  test F1                     0.4844      0.4808     0.1518  5
  test sensitivity            0.4507      0.3731     0.2844  5
  test specificity            0.6852      0.8033     0.2634  5
  test precision              0.6295      0.6275     0.0437  5
  test loss                   0.7513      0.6943     0.1348  5
  FPR (FP/(FP+TN))            0.3148      0.1967     0.2634  5
  FNR (FN/(FN+TP))            0.5493      0.6269     0.2844  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5538      0.5577     0.0161  5
  max valid BA                0.5615      0.5577     0.0161  5
  best valid F1               0.5367      0.5306     0.1159  5
  test BA                     0.4640      0.4400     0.0477  5
  test F1                     0.2846      0.2162     0.1549  5
  test sensitivity            0.2480      0.1600     0.1968  5
  test specificity            0.6800      0.6800     0.2245  5
  test precision              0.5141      0.4211     0.2789  5
  test loss                   0.7425      0.7254     0.0534  5
  FPR (FP/(FP+TN))            0.3200      0.3200     0.2245  5
  FNR (FN/(FN+TP))            0.7520      0.8400     0.1968  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6233      0.6232     0.0360  5
  max valid BA                0.6774      0.6857     0.0357  5
  best valid F1               0.5734      0.5778     0.0400  5
  test BA                     0.5737      0.5782     0.0780  5
  test F1                     0.3514      0.4000     0.1875  5
  test sensitivity            0.3304      0.3478     0.2432  5
  test specificity            0.8170      0.8085     0.0885  5
  test precision              0.4307      0.4706     0.0903  5
  test loss                   0.6316      0.6332     0.0259  5
  FPR (FP/(FP+TN))            0.1830      0.1915     0.0885  5
  FNR (FN/(FN+TP))            0.6696      0.6522     0.2432  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6336      0.6316     0.0830  5
  max valid BA                0.6568      0.6955     0.0882  5
  best valid F1               0.5223      0.6000     0.1816  5
  test BA                     0.6386      0.6661     0.1152  5
  test F1                     0.4323      0.5600     0.2820  5
  test sensitivity            0.4261      0.5652     0.3065  5
  test specificity            0.8511      0.8511     0.0952  5
  test precision              0.4645      0.5185     0.2694  5
  test loss                   0.6719      0.6477     0.0981  5
  FPR (FP/(FP+TN))            0.1489      0.1489     0.0952  5
  FNR (FN/(FN+TP))            0.5739      0.4348     0.3065  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4985      0.4988     0.0159  5
  max valid BA                0.5160      0.5200     0.0153  5
  best valid F1               0.4677      0.4645     0.0937  5
  test BA                     0.4624      0.4506     0.0325  5
  test F1                     0.1019      0.1333     0.0722  5
  test sensitivity            0.0708      0.0923     0.0550  5
  test specificity            0.8539      0.8090     0.1176  5
  test precision              0.2531      0.2609     0.1770  5
  test loss                   0.8949      0.7223     0.4091  5
  FPR (FP/(FP+TN))            0.1461      0.1910     0.1176  5
  FNR (FN/(FN+TP))            0.9292      0.9077     0.0550  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5375      0.5278     0.0433  5
  max valid BA                0.5931      0.5556     0.0858  5
  best valid F1               0.4139      0.3529     0.1876  5
  test BA                     0.5167      0.5000     0.0665  5
  test F1                     0.2100      0.0976     0.2226  5
  test sensitivity            0.2333      0.0556     0.3028  5
  test specificity            0.8000      0.8750     0.2050  5
  test precision              0.3325      0.3538     0.1149  4
  test loss                   0.6450      0.6448     0.0387  5
  FPR (FP/(FP+TN))            0.2000      0.1250     0.2050  5
  FNR (FN/(FN+TP))            0.7667      0.9444     0.3028  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5853      0.5882     0.0554  5
  max valid BA                0.6147      0.6029     0.0544  5
  best valid F1               0.4977      0.5000     0.0510  5
  test BA                     0.5500      0.5294     0.0536  5
  test F1                     0.3797      0.3529     0.1117  5
  test sensitivity            0.4000      0.3529     0.2331  5
  test specificity            0.7000      0.7941     0.2420  5
  test precision              0.4285      0.3529     0.1142  5
  test loss                   0.6725      0.6818     0.0202  5
  FPR (FP/(FP+TN))            0.3000      0.2059     0.2420  5
  FNR (FN/(FN+TP))            0.6000      0.6471     0.2331  5
```

## AUC vs chemistry null model, in-sample increment

