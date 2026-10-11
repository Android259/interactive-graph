# thematical_paths_geom_chem_interaction_lr

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'thematical_paths_geom_chem_interaction_lr'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6328      0.4098      0.9680      0.4810      0.6597      0.3903
groups_GLTP            5      0.6000      0.4000      0.6434      0.3594      0.6000      0.4000
groups_IP_trans        5      0.3826      0.6298      0.5862      0.6697      0.4167      0.6596
groups_LBP_BPI_CETP    5      0.5217      0.5532      0.6144      0.5204      0.5333      0.5745
groups_START           5      0.4615      0.5955      0.5700      0.6358      0.4781      0.6112
groups_lipocalin       5      0.5500      0.5028      0.5957      0.4792      0.5278      0.5083
groups_scp2            5      0.4824      0.5588      0.6151      0.5185      0.4941      0.5882
ALL                   35      0.5187      0.5214      0.6561      0.5234      0.5300      0.5332

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5316      0.5000     0.0644  35
max valid BA                0.5413      0.5000     0.0769  35
best valid F1               0.4816      0.5053     0.2339  35
test BA                     0.5201      0.5000     0.0444  35
test F1                     0.3504      0.4844     0.2688  35
test sensitivity            0.5187      0.4769     0.4389  35
test specificity            0.5214      0.6404     0.4406  35
test precision              0.4413      0.4779     0.0979  23
test loss                   0.7458      0.7047     0.1499  35
FPR (FP/(FP+TN))            0.4786      0.3596     0.4406  35
FNR (FN/(FN+TP))            0.4813      0.5231     0.4389  35

=== abs(sensitivity-specificity) gap: mean=0.8002 median=1.0000 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5250      0.5148     0.0288  5
  max valid BA                0.5612      0.5519     0.0689  5
  best valid F1               0.6670      0.6837     0.0438  5
  test BA                     0.5213      0.5055     0.0300  5
  test F1                     0.5526      0.5000     0.1250  5
  test sensitivity            0.6328      0.4179     0.3358  5
  test specificity            0.4098      0.6230     0.3760  5
  test precision              0.5542      0.5306     0.0429  5
  test loss                   0.9859      1.0022     0.3059  5
  FPR (FP/(FP+TN))            0.5902      0.3770     0.3760  5
  FNR (FN/(FN+TP))            0.3672      0.5821     0.3358  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0000  5
  max valid BA                0.5000      0.5000     0.0000  5
  best valid F1               0.5333      0.6667     0.2981  5
  test BA                     0.5000      0.5000     0.0000  5
  test F1                     0.4000      0.6667     0.3651  5
  test sensitivity            0.6000      1.0000     0.5477  5
  test specificity            0.4000      0.0000     0.5477  5
  test precision              0.5000      0.5000     0.0000  3
  test loss                   0.7018      0.7004     0.0072  5
  FPR (FP/(FP+TN))            0.6000      1.0000     0.5477  5
  FNR (FN/(FN+TP))            0.4000      0.0000     0.5477  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5381      0.5000     0.0525  5
  max valid BA                0.5451      0.5000     0.0623  5
  best valid F1               0.4075      0.5053     0.2279  5
  test BA                     0.5062      0.5000     0.0186  5
  test F1                     0.2484      0.2857     0.2402  5
  test sensitivity            0.3826      0.2609     0.4363  5
  test specificity            0.6298      0.7234     0.4246  5
  test precision              0.3338      0.3286     0.0212  3
  test loss                   0.7281      0.7361     0.0627  5
  FPR (FP/(FP+TN))            0.3702      0.2766     0.4246  5
  FNR (FN/(FN+TP))            0.6174      0.7391     0.4363  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5539      0.5000     0.1205  5
  max valid BA                0.5622      0.5000     0.1392  5
  best valid F1               0.4532      0.5053     0.2746  5
  test BA                     0.5375      0.5000     0.0838  5
  test F1                     0.3145      0.4946     0.2894  5
  test sensitivity            0.5217      0.6087     0.5024  5
  test specificity            0.5532      0.7660     0.5140  5
  test precision              0.4057      0.3286     0.1336  3
  test loss                   0.6993      0.6894     0.0562  5
  FPR (FP/(FP+TN))            0.4468      0.2340     0.5140  5
  FNR (FN/(FN+TP))            0.4783      0.3913     0.5024  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5447      0.5000     0.0669  5
  max valid BA                0.5447      0.5000     0.0669  5
  best valid F1               0.4765      0.5899     0.2665  5
  test BA                     0.5285      0.5000     0.0401  5
  test F1                     0.3369      0.4844     0.3112  5
  test sensitivity            0.4615      0.4769     0.4617  5
  test specificity            0.5955      0.6404     0.4332  5
  test precision              0.4640      0.4779     0.0370  3
  test loss                   0.7015      0.7057     0.0152  5
  FPR (FP/(FP+TN))            0.4045      0.3596     0.4332  5
  FNR (FN/(FN+TP))            0.5385      0.5231     0.4617  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5181      0.5000     0.0404  5
  max valid BA                0.5347      0.5000     0.0776  5
  best valid F1               0.4150      0.5000     0.2343  5
  test BA                     0.5264      0.5000     0.0590  5
  test F1                     0.3102      0.5000     0.2839  5
  test sensitivity            0.5500      0.7500     0.5123  5
  test specificity            0.5028      0.5139     0.5000  5
  test precision              0.3674      0.3333     0.0590  3
  test loss                   0.7040      0.6885     0.0537  5
  FPR (FP/(FP+TN))            0.4972      0.4861     0.5000  5
  FNR (FN/(FN+TP))            0.4500      0.2500     0.5123  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5412      0.5000     0.0921  5
  max valid BA                0.5412      0.5000     0.0921  5
  best valid F1               0.4185      0.5000     0.2374  5
  test BA                     0.5206      0.5000     0.0460  5
  test F1                     0.2903      0.4516     0.2658  5
  test sensitivity            0.4824      0.4118     0.5016  5
  test specificity            0.5588      0.7941     0.5170  5
  test precision              0.3889      0.3333     0.0962  3
  test loss                   0.7003      0.6897     0.0478  5
  FPR (FP/(FP+TN))            0.4412      0.2059     0.5170  5
  FNR (FN/(FN+TP))            0.5176      0.5882     0.5016  5
```

## AUC vs chemistry null model, in-sample increment

