# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_attnpool_pocketbias

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_attnpool_pocketbias'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5224      0.6197      0.7029      0.6798      0.5313      0.6484
groups_GLTP            5      0.1280      0.7920      0.6378      0.5084      0.2538      0.8538
groups_IP_trans        5      0.4435      0.8000      0.6953      0.6595      0.5250      0.8213
groups_LBP_BPI_CETP    5      0.2522      0.9106      0.7634      0.5802      0.3417      0.8979
groups_START           5      0.3323      0.6494      0.6915      0.5096      0.3312      0.6562
groups_lipocalin       5      0.1556      0.8833      0.4569      0.7829      0.1500      0.8944
groups_scp2            5      0.2941      0.8353      0.7037      0.6230      0.3412      0.8882
ALL                   35      0.3040      0.7843      0.6645      0.6205      0.3535      0.8086

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5799      0.5577     0.0767  35
max valid BA                0.6068      0.5981     0.0743  35
best valid F1               0.5214      0.5517     0.1388  35
test BA                     0.5442      0.5347     0.0717  35
test F1                     0.3217      0.3158     0.2071  35
test sensitivity            0.3040      0.2609     0.2558  35
test specificity            0.7843      0.8085     0.2124  35
test precision              0.4834      0.5000     0.1907  33
test loss                   0.6890      0.6767     0.0940  35
FPR (FP/(FP+TN))            0.2157      0.1915     0.2124  35
FNR (FN/(FN+TP))            0.6960      0.7391     0.2558  35

=== abs(sensitivity-specificity) gap: mean=0.5723 median=0.5458 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5899      0.5798     0.0319  5
  max valid BA                0.6117      0.6109     0.0350  5
  best valid F1               0.6830      0.6812     0.0108  5
  test BA                     0.5710      0.5839     0.0317  5
  test F1                     0.5427      0.5357     0.1115  5
  test sensitivity            0.5224      0.4478     0.2065  5
  test specificity            0.6197      0.7377     0.1945  5
  test precision              0.6074      0.6000     0.0473  5
  test loss                   0.6930      0.6906     0.0230  5
  FPR (FP/(FP+TN))            0.3803      0.2623     0.1945  5
  FNR (FN/(FN+TP))            0.4776      0.5522     0.2065  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5462      0.5385     0.0219  5
  max valid BA                0.5731      0.5577     0.0316  5
  best valid F1               0.5265      0.4889     0.0979  5
  test BA                     0.4600      0.4400     0.0374  5
  test F1                     0.1773      0.2162     0.0999  5
  test sensitivity            0.1280      0.1600     0.0867  5
  test specificity            0.7920      0.7200     0.1559  5
  test precision              0.4194      0.4000     0.0773  5
  test loss                   0.7051      0.7023     0.0132  5
  FPR (FP/(FP+TN))            0.2080      0.2800     0.1559  5
  FNR (FN/(FN+TP))            0.8720      0.8400     0.0867  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6731      0.6547     0.0484  5
  max valid BA                0.6872      0.6755     0.0348  5
  best valid F1               0.5888      0.5667     0.0432  5
  test BA                     0.6217      0.6216     0.0683  5
  test F1                     0.4517      0.4762     0.1461  5
  test sensitivity            0.4435      0.4348     0.2309  5
  test specificity            0.8000      0.8085     0.1132  5
  test precision              0.5554      0.5263     0.1473  5
  test loss                   0.6389      0.6332     0.0175  5
  FPR (FP/(FP+TN))            0.2000      0.1915     0.1132  5
  FNR (FN/(FN+TP))            0.5565      0.5652     0.2309  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6198      0.6551     0.0795  5
  max valid BA                0.6506      0.6653     0.0618  5
  best valid F1               0.4962      0.5455     0.1635  5
  test BA                     0.5814      0.5458     0.1017  5
  test F1                     0.3049      0.3500     0.2665  5
  test sensitivity            0.2522      0.3043     0.2329  5
  test specificity            0.9106      0.9149     0.0788  5
  test precision              0.4584      0.5000     0.2883  5
  test loss                   0.7278      0.6321     0.2326  5
  FPR (FP/(FP+TN))            0.0894      0.0851     0.0788  5
  FNR (FN/(FN+TP))            0.7478      0.6957     0.2329  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4937      0.5000     0.0402  5
  max valid BA                0.5381      0.5432     0.0406  5
  best valid F1               0.4385      0.3538     0.1314  5
  test BA                     0.4909      0.5000     0.0250  5
  test F1                     0.2790      0.2826     0.2276  5
  test sensitivity            0.3323      0.2000     0.3977  5
  test specificity            0.6494      0.8202     0.3922  5
  test precision              0.3924      0.4078     0.0878  4
  test loss                   0.7388      0.7005     0.0876  5
  FPR (FP/(FP+TN))            0.3506      0.1798     0.3922  5
  FNR (FN/(FN+TP))            0.6677      0.8000     0.3977  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5222      0.5000     0.0446  5
  max valid BA                0.5431      0.5486     0.0412  5
  best valid F1               0.3660      0.4250     0.1322  5
  test BA                     0.5194      0.5139     0.0247  5
  test F1                     0.1599      0.1000     0.1915  5
  test sensitivity            0.1556      0.0556     0.2337  5
  test specificity            0.8833      0.9722     0.1936  5
  test precision              0.3443      0.4387     0.2367  4
  test loss                   0.6712      0.6791     0.0338  5
  FPR (FP/(FP+TN))            0.1167      0.0278     0.1936  5
  FNR (FN/(FN+TP))            0.8444      0.9444     0.2337  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6147      0.6029     0.0828  5
  max valid BA                0.6441      0.6324     0.1078  5
  best valid F1               0.5508      0.5263     0.1087  5
  test BA                     0.5647      0.5588     0.0339  5
  test F1                     0.3363      0.3871     0.1320  5
  test sensitivity            0.2941      0.3529     0.1765  5
  test specificity            0.8353      0.8529     0.1357  5
  test precision              0.5605      0.4286     0.2520  5
  test loss                   0.6483      0.6436     0.0163  5
  FPR (FP/(FP+TN))            0.1647      0.1471     0.1357  5
  FNR (FN/(FN+TP))            0.7059      0.6471     0.1765  5
```

## AUC vs chemistry null model, in-sample increment

(skipped: SKIP_AUC=1 -- rerun without it to fill this in: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_attnpool_pocketbias --seeds=0,1,2,3,4`)
