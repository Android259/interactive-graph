# thematical_paths_geom_chem_ortweight05

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'thematical_paths_geom_chem_ortweight05'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4925      0.5639      0.8234      0.7052      0.5373      0.5903
groups_GLTP            5      0.8080      0.4800      0.7972      0.4030      0.7846      0.5154
groups_IP_trans        5      0.3478      0.7574      0.6860      0.7113      0.4167      0.7915
groups_LBP_BPI_CETP    5      0.3739      0.6426      0.8191      0.6116      0.4917      0.6340
groups_START           5      0.6338      0.5213      0.8055      0.5618      0.5938      0.5416
groups_lipocalin       5      0.6167      0.4389      0.9486      0.4755      0.5944      0.4639
groups_scp2            5      0.5882      0.5294      0.7256      0.4972      0.5765      0.5353
ALL                   35      0.5516      0.5619      0.8008      0.5665      0.5707      0.5817

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5762      0.5486     0.0905  35
max valid BA                0.5958      0.5735     0.1012  35
best valid F1               0.5792      0.5714     0.1181  35
test BA                     0.5568      0.5222     0.0858  35
test F1                     0.4475      0.4946     0.2043  35
test sensitivity            0.5516      0.5278     0.3443  35
test specificity            0.5619      0.6596     0.3738  35
test precision              0.4982      0.5000     0.1771  32
test loss                   0.7684      0.7141     0.1805  35
FPR (FP/(FP+TN))            0.4381      0.3404     0.3738  35
FNR (FN/(FN+TP))            0.4484      0.4722     0.3443  35

=== abs(sensitivity-specificity) gap: mean=0.6022 median=0.6000 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5638      0.5779     0.0359  5
  max valid BA                0.5833      0.5853     0.0418  5
  best valid F1               0.6751      0.6837     0.0299  5
  test BA                     0.5282      0.5104     0.0443  5
  test F1                     0.4934      0.4348     0.1257  5
  test sensitivity            0.4925      0.3731     0.2782  5
  test specificity            0.5639      0.6230     0.3088  5
  test precision              0.5825      0.5289     0.1115  5
  test loss                   1.0174      1.0933     0.3306  5
  FPR (FP/(FP+TN))            0.4361      0.3770     0.3088  5
  FNR (FN/(FN+TP))            0.5075      0.6269     0.2782  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6500      0.6538     0.1565  5
  max valid BA                0.6923      0.7308     0.1918  5
  best valid F1               0.7574      0.7541     0.1121  5
  test BA                     0.6440      0.6400     0.1584  5
  test F1                     0.6949      0.6667     0.1088  5
  test sensitivity            0.8080      0.8400     0.2456  5
  test specificity            0.4800      0.4400     0.4907  5
  test precision              0.7105      0.6000     0.2465  5
  test loss                   0.6594      0.6886     0.0839  5
  FPR (FP/(FP+TN))            0.5200      0.5600     0.4907  5
  FNR (FN/(FN+TP))            0.1920      0.1600     0.2456  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6041      0.5550     0.1210  5
  max valid BA                0.6200      0.5669     0.1142  5
  best valid F1               0.5527      0.5238     0.1104  5
  test BA                     0.5526      0.5509     0.0533  5
  test F1                     0.2864      0.4390     0.2625  5
  test sensitivity            0.3478      0.3913     0.3465  5
  test specificity            0.7574      0.8085     0.2837  5
  test precision              0.4361      0.4483     0.0708  3
  test loss                   0.7639      0.7012     0.1601  5
  FPR (FP/(FP+TN))            0.2426      0.1915     0.2837  5
  FNR (FN/(FN+TP))            0.6522      0.6087     0.3465  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5629      0.5394     0.0825  5
  max valid BA                0.5907      0.5514     0.0884  5
  best valid F1               0.5309      0.5053     0.0810  5
  test BA                     0.5082      0.5000     0.0708  5
  test F1                     0.3015      0.2857     0.1735  5
  test sensitivity            0.3739      0.3043     0.3748  5
  test specificity            0.6426      0.8085     0.3825  5
  test precision              0.3684      0.3286     0.1591  5
  test loss                   0.7012      0.7093     0.0898  5
  FPR (FP/(FP+TN))            0.3574      0.1915     0.3825  5
  FNR (FN/(FN+TP))            0.6261      0.6957     0.3748  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5677      0.5664     0.0642  5
  max valid BA                0.5737      0.5808     0.0612  5
  best valid F1               0.5723      0.5926     0.0706  5
  test BA                     0.5776      0.5498     0.0710  5
  test F1                     0.5321      0.5936     0.1181  5
  test sensitivity            0.6338      0.5846     0.3114  5
  test specificity            0.5213      0.7303     0.3548  5
  test precision              0.5178      0.5000     0.0902  5
  test loss                   0.7104      0.7141     0.0206  5
  FPR (FP/(FP+TN))            0.4787      0.2697     0.3548  5
  FNR (FN/(FN+TP))            0.3662      0.4154     0.3114  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5292      0.5347     0.0284  5
  max valid BA                0.5403      0.5486     0.0334  5
  best valid F1               0.4857      0.5000     0.0319  5
  test BA                     0.5278      0.5208     0.0307  5
  test F1                     0.4175      0.4578     0.1106  5
  test sensitivity            0.6167      0.5278     0.3729  5
  test specificity            0.4389      0.6111     0.4116  5
  test precision              0.3742      0.4000     0.0373  5
  test loss                   0.8314      0.8177     0.0835  5
  FPR (FP/(FP+TN))            0.5611      0.3889     0.4116  5
  FNR (FN/(FN+TP))            0.3833      0.4722     0.3729  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5559      0.5000     0.0767  5
  max valid BA                0.5706      0.5735     0.0701  5
  best valid F1               0.4800      0.5000     0.0447  5
  test BA                     0.5588      0.5000     0.0812  5
  test F1                     0.4066      0.5000     0.2274  5
  test sensitivity            0.5882      0.5294     0.4242  5
  test specificity            0.5294      0.7353     0.4926  5
  test precision              0.4667      0.4167     0.1743  4
  test loss                   0.6951      0.6502     0.0757  5
  FPR (FP/(FP+TN))            0.4706      0.2647     0.4926  5
  FNR (FN/(FN+TP))            0.4118      0.4706     0.4242  5
```

## AUC vs chemistry null model, in-sample increment

