# geometric_edge_attention_nwd

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention_nwd'
rows: 14

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       2      0.8134      0.2459      0.7157      0.5735      0.8806      0.2903
groups_GLTP            2      0.7600      0.2200      0.6953      0.5390      0.8462      0.3654
groups_IP_trans        2      0.8478      0.4468      0.8939      0.6791      0.8125      0.5638
groups_LBP_BPI_CETP    2      0.6739      0.5745      0.8776      0.5928      0.6875      0.6170
groups_START           2      0.9462      0.1011      0.7167      0.5085      0.9453      0.1067
groups_lipocalin       2      0.0000      1.0000      0.4878      0.4618      0.0000      1.0000
groups_scp2            2      0.5000      0.5735      0.5516      0.5435      0.6471      0.6471
ALL                   14      0.6488      0.4517      0.7055      0.5569      0.6884      0.5129

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6007      0.6050     0.0699  14
max valid BA                0.6362      0.6482     0.0732  14
best valid F1               0.6244      0.6231     0.0739  14
test BA                     0.5502      0.5297     0.0641  14
test F1                     0.4795      0.5514     0.2163  14
test sensitivity            0.6488      0.7644     0.3266  14
test specificity            0.4517      0.3320     0.3199  14
test precision              0.4605      0.4651     0.0644  12
test loss                   0.7057      0.6936     0.0581  14
FPR (FP/(FP+TN))            0.5483      0.6680     0.3199  14
FNR (FN/(FN+TP))            0.3512      0.2356     0.3266  14

=== abs(sensitivity-specificity) gap: mean=0.5819 median=0.5216 n=14 ===

=== By group ===
groups_CRAL-TRIO (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5855      0.5855     0.0097  2
  max valid BA                0.6321      0.6321     0.0757  2
  best valid F1               0.7040      0.7040     0.0171  2
  test BA                     0.5297      0.5297     0.0127  2
  test F1                     0.6496      0.6496     0.0349  2
  test sensitivity            0.8134      0.8134     0.0950  2
  test specificity            0.2459      0.2459     0.0696  2
  test precision              0.5420      0.5420     0.0061  2
  test loss                   0.6934      0.6934     0.0006  2
  FPR (FP/(FP+TN))            0.7541      0.7541     0.0696  2
  FNR (FN/(FN+TP))            0.1866      0.1866     0.0950  2

groups_GLTP (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6058      0.6058     0.0408  2
  max valid BA                0.6250      0.6250     0.0680  2
  best valid F1               0.7101      0.7101     0.0615  2
  test BA                     0.4900      0.4900     0.0424  2
  test F1                     0.5917      0.5917     0.0925  2
  test sensitivity            0.7600      0.7600     0.2263  2
  test specificity            0.2200      0.2200     0.1414  2
  test precision              0.4899      0.4899     0.0300  2
  test loss                   0.7187      0.7187     0.0248  2
  FPR (FP/(FP+TN))            0.7800      0.7800     0.1414  2
  FNR (FN/(FN+TP))            0.2400      0.2400     0.2263  2

groups_IP_trans (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6882      0.6882     0.0235  2
  max valid BA                0.7256      0.7256     0.0013  2
  best valid F1               0.6466      0.6466     0.0006  2
  test BA                     0.6473      0.6473     0.0291  2
  test F1                     0.5703      0.5703     0.0146  2
  test sensitivity            0.8478      0.8478     0.0922  2
  test specificity            0.4468      0.4468     0.1504  2
  test precision              0.4327      0.4327     0.0408  2
  test loss                   0.7387      0.7387     0.0955  2
  FPR (FP/(FP+TN))            0.5532      0.5532     0.1504  2
  FNR (FN/(FN+TP))            0.1522      0.1522     0.0922  2

groups_LBP_BPI_CETP (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6523      0.6523     0.0461  2
  max valid BA                0.6981      0.6981     0.0690  2
  best valid F1               0.6282      0.6282     0.0544  2
  test BA                     0.6242      0.6242     0.0128  2
  test F1                     0.5267      0.5267     0.0228  2
  test sensitivity            0.6739      0.6739     0.2152  2
  test specificity            0.5745      0.5745     0.2407  2
  test precision              0.4521      0.4521     0.0677  2
  test loss                   0.7068      0.7068     0.1702  2
  FPR (FP/(FP+TN))            0.4255      0.4255     0.2407  2
  FNR (FN/(FN+TP))            0.3261      0.3261     0.2152  2

groups_START (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5260      0.5260     0.0240  2
  max valid BA                0.5761      0.5761     0.0147  2
  best valid F1               0.5990      0.5990     0.0015  2
  test BA                     0.5236      0.5236     0.0222  2
  test F1                     0.5952      0.5952     0.0255  2
  test sensitivity            0.9462      0.9462     0.0761  2
  test specificity            0.1011      0.1011     0.0318  2
  test precision              0.4343      0.4343     0.0111  2
  test loss                   0.7133      0.7133     0.0148  2
  FPR (FP/(FP+TN))            0.8989      0.8989     0.0318  2
  FNR (FN/(FN+TP))            0.0538      0.0538     0.0761  2

groups_lipocalin (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0000  2
  max valid BA                0.5347      0.5347     0.0295  2
  best valid F1               0.5035      0.5035     0.0050  2
  test BA                     0.5000      0.5000     0.0000  2
  test F1                     0.0000      0.0000     0.0000  2
  test sensitivity            0.0000      0.0000     0.0000  2
  test specificity            1.0000      1.0000     0.0000  2
  test loss                   0.6867      0.6867     0.0011  2
  FPR (FP/(FP+TN))            0.0000      0.0000     0.0000  2
  FNR (FN/(FN+TP))            1.0000      1.0000     0.0000  2

groups_scp2 (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6471      0.6471     0.0416  2
  max valid BA                0.6618      0.6618     0.0208  2
  best valid F1               0.5791      0.5791     0.0296  2
  test BA                     0.5368      0.5368     0.0728  2
  test F1                     0.4226      0.4226     0.0124  2
  test sensitivity            0.5000      0.5000     0.2080  2
  test specificity            0.5735      0.5735     0.3536  2
  test precision              0.4118      0.4118     0.1248  2
  test loss                   0.6824      0.6824     0.0156  2
  FPR (FP/(FP+TN))            0.4265      0.4265     0.3536  2
  FNR (FN/(FN+TP))            0.5000      0.5000     0.2080  2
```

## AUC vs chemistry null model, in-sample increment

