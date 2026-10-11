# thematical_paths_geom_chem_orthogonal_init_batch64

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'thematical_paths_geom_chem_orthogonal_init_batch64'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.2448      0.8066      0.8669      0.7464      0.3672      0.7774
groups_GLTP            5      0.4720      0.9360      0.8168      0.7259      0.4615      0.9231
groups_IP_trans        5      0.4348      0.5787      0.6231      0.6664      0.5083      0.6128
groups_LBP_BPI_CETP    5      0.2609      0.8723      0.7706      0.7358      0.3083      0.8979
groups_START           5      0.4123      0.6921      0.4799      0.8338      0.3875      0.6854
groups_lipocalin       5      0.4944      0.5583      0.8061      0.5538      0.5111      0.5417
groups_scp2            5      0.5529      0.5765      0.8890      0.6434      0.6588      0.5294
ALL                   35      0.4103      0.7172      0.7503      0.7008      0.4575      0.7097

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5836      0.5638     0.0848  35
max valid BA                0.5991      0.5780     0.0863  35
best valid F1               0.5011      0.5106     0.1429  35
test BA                     0.5638      0.5502     0.0869  35
test F1                     0.3853      0.4118     0.2026  35
test sensitivity            0.4103      0.3529     0.2994  35
test specificity            0.7172      0.8197     0.2980  35
test precision              0.5167      0.5000     0.1863  32
test loss                   0.7393      0.6928     0.1382  35
FPR (FP/(FP+TN))            0.2828      0.1803     0.2980  35
FNR (FN/(FN+TP))            0.5897      0.6471     0.2994  35

=== abs(sensitivity-specificity) gap: mean=0.5769 median=0.5600 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5723      0.5638     0.0480  5
  max valid BA                0.5834      0.5719     0.0517  5
  best valid F1               0.5258      0.6167     0.2046  5
  test BA                     0.5257      0.5143     0.0251  5
  test F1                     0.3213      0.3846     0.1744  5
  test sensitivity            0.2448      0.2985     0.1434  5
  test specificity            0.8066      0.7869     0.1077  5
  test precision              0.5646      0.5600     0.0479  5
  test loss                   0.8773      0.8418     0.2054  5
  FPR (FP/(FP+TN))            0.1934      0.2131     0.1077  5
  FNR (FN/(FN+TP))            0.7552      0.7015     0.1434  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6923      0.6923     0.1400  5
  max valid BA                0.7077      0.6923     0.1342  5
  best valid F1               0.6164      0.6667     0.2108  5
  test BA                     0.7040      0.6800     0.1276  5
  test F1                     0.5894      0.5789     0.2307  5
  test sensitivity            0.4720      0.4400     0.2322  5
  test specificity            0.9360      0.9200     0.0358  5
  test precision              0.8451      0.8462     0.1215  5
  test loss                   0.7077      0.6823     0.2083  5
  FPR (FP/(FP+TN))            0.0640      0.0800     0.0358  5
  FNR (FN/(FN+TP))            0.5280      0.5600     0.2322  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5605      0.5106     0.0783  5
  max valid BA                0.5777      0.5780     0.0745  5
  best valid F1               0.4717      0.5000     0.1069  5
  test BA                     0.5068      0.5000     0.0499  5
  test F1                     0.3106      0.3492     0.1941  5
  test sensitivity            0.4348      0.4783     0.3702  5
  test specificity            0.5787      0.5319     0.3979  5
  test precision              0.3866      0.3499     0.1294  4
  test loss                   0.7389      0.6914     0.1522  5
  FPR (FP/(FP+TN))            0.4213      0.4681     0.3979  5
  FNR (FN/(FN+TP))            0.5652      0.5217     0.3702  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6031      0.5829     0.0624  5
  max valid BA                0.6359      0.6627     0.0611  5
  best valid F1               0.4990      0.5500     0.1022  5
  test BA                     0.5666      0.5888     0.0594  5
  test F1                     0.3239      0.4103     0.1640  5
  test sensitivity            0.2609      0.3043     0.1537  5
  test specificity            0.8723      0.8936     0.0499  5
  test precision              0.4614      0.5000     0.1620  5
  test loss                   0.7197      0.6892     0.0779  5
  FPR (FP/(FP+TN))            0.1277      0.1064     0.0499  5
  FNR (FN/(FN+TP))            0.7391      0.6957     0.1537  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5364      0.5392     0.0415  5
  max valid BA                0.5448      0.5476     0.0482  5
  best valid F1               0.4447      0.3306     0.1648  5
  test BA                     0.5522      0.5521     0.0526  5
  test F1                     0.3234      0.3542     0.3162  5
  test sensitivity            0.4123      0.2615     0.4633  5
  test specificity            0.6921      0.8427     0.3653  5
  test precision              0.5092      0.5049     0.0372  3
  test loss                   0.6795      0.6849     0.0176  5
  FPR (FP/(FP+TN))            0.3079      0.1573     0.3653  5
  FNR (FN/(FN+TP))            0.5877      0.7385     0.4633  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5264      0.5278     0.0232  5
  max valid BA                0.5417      0.5347     0.0357  5
  best valid F1               0.4307      0.4138     0.0908  5
  test BA                     0.5264      0.5208     0.0280  5
  test F1                     0.3719      0.3077     0.1199  5
  test sensitivity            0.4944      0.2222     0.3790  5
  test specificity            0.5583      0.7778     0.3877  5
  test precision              0.3829      0.3671     0.0687  5
  test loss                   0.7167      0.6981     0.0431  5
  FPR (FP/(FP+TN))            0.4417      0.2222     0.3877  5
  FNR (FN/(FN+TP))            0.5056      0.7778     0.3790  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5941      0.6029     0.0620  5
  max valid BA                0.6029      0.6176     0.0682  5
  best valid F1               0.5193      0.5333     0.0301  5
  test BA                     0.5647      0.5588     0.0732  5
  test F1                     0.4564      0.4500     0.0779  5
  test sensitivity            0.5529      0.4706     0.2584  5
  test specificity            0.5765      0.6471     0.3415  5
  test precision              0.4383      0.3913     0.1389  5
  test loss                   0.7355      0.7615     0.1210  5
  FPR (FP/(FP+TN))            0.4235      0.3529     0.3415  5
  FNR (FN/(FN+TP))            0.4471      0.5294     0.2584  5
```

## AUC vs chemistry null model, in-sample increment

