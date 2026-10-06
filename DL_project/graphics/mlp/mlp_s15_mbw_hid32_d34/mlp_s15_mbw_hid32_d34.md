# mlp_s15_mbw_hid32_d34

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_mbw_hid32_d34'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.7935      0.7974      0.7883      0.7798      0.8308      0.8064
ALL                 5      0.7935      0.7974      0.7883      0.7798      0.8308      0.8064

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8071      0.7929     0.0364  5
max valid BA                0.8186      0.7968     0.0396  5
best valid F1               0.6245      0.6032     0.0471  5
test BA                     0.7955      0.7862     0.0359  5
test AUC                    0.8746      0.8649     0.0401  5
test AUC in-protein         0.8720      0.8710     0.0310  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.8750      0.8714     0.0409  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.5963      0.5714     0.0631  5
test sensitivity            0.7935      0.7917     0.0452  5
test specificity            0.7974      0.8057     0.0598  5
test precision              0.4814      0.4675     0.0765  5
test loss                   0.4071      0.4273     0.0581  5
FPR (FP/(FP+TN))            0.2026      0.1943     0.0598  5
FNR (FN/(FN+TP))            0.2065      0.2083     0.0452  5

=== abs(sensitivity-specificity) gap: mean=0.0651 median=0.0702 n=5 ===
sensitivity std across seeds (by group): mean=0.0452 median=0.0452 n=1
specificity std across seeds (by group): mean=0.0598 median=0.0598 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8071      0.7929     0.0364  5
  max valid BA                0.8186      0.7968     0.0396  5
  best valid F1               0.6245      0.6032     0.0471  5
  test BA                     0.7955      0.7862     0.0359  5
  test AUC                    0.8746      0.8649     0.0401  5
  test AUC in-protein         0.8720      0.8710     0.0310  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.8750      0.8714     0.0409  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.5963      0.5714     0.0631  5
  test sensitivity            0.7935      0.7917     0.0452  5
  test specificity            0.7974      0.8057     0.0598  5
  test precision              0.4814      0.4675     0.0765  5
  test loss                   0.4071      0.4273     0.0581  5
  FPR (FP/(FP+TN))            0.2026      0.1943     0.0598  5
  FNR (FN/(FN+TP))            0.2065      0.2083     0.0452  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_mbw_hid32_d34 --seeds=0,1,2,3,4`
