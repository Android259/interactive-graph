# mlp_s15_mbw_hid64

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_mbw_hid64'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8186      0.8671      0.8577      0.8545      0.8928      0.8802
ALL                 5      0.8186      0.8671      0.8577      0.8545      0.8928      0.8802

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8708      0.8707     0.0326  5
max valid BA                0.8865      0.8752     0.0293  5
best valid F1               0.7534      0.7477     0.0378  5
test BA                     0.8429      0.8515     0.0541  5
test AUC                    0.9239      0.9304     0.0337  5
test AUC in-protein         0.9153      0.9202     0.0377  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.9159      0.9249     0.0383  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.6857      0.7027     0.0875  5
test sensitivity            0.8186      0.8163     0.0674  5
test specificity            0.8671      0.8767     0.0440  5
test precision              0.5916      0.6029     0.0974  5
test loss                   0.3052      0.2871     0.0681  5
FPR (FP/(FP+TN))            0.1329      0.1233     0.0440  5
FNR (FN/(FN+TP))            0.1814      0.1837     0.0674  5

=== abs(sensitivity-specificity) gap: mean=0.0485 median=0.0250 n=5 ===
sensitivity std across seeds (by group): mean=0.0674 median=0.0674 n=1
specificity std across seeds (by group): mean=0.0440 median=0.0440 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8708      0.8707     0.0326  5
  max valid BA                0.8865      0.8752     0.0293  5
  best valid F1               0.7534      0.7477     0.0378  5
  test BA                     0.8429      0.8515     0.0541  5
  test AUC                    0.9239      0.9304     0.0337  5
  test AUC in-protein         0.9153      0.9202     0.0377  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.9159      0.9249     0.0383  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.6857      0.7027     0.0875  5
  test sensitivity            0.8186      0.8163     0.0674  5
  test specificity            0.8671      0.8767     0.0440  5
  test precision              0.5916      0.6029     0.0974  5
  test loss                   0.3052      0.2871     0.0681  5
  FPR (FP/(FP+TN))            0.1329      0.1233     0.0440  5
  FNR (FN/(FN+TP))            0.1814      0.1837     0.0674  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_mbw_hid64 --seeds=0,1,2,3,4`
