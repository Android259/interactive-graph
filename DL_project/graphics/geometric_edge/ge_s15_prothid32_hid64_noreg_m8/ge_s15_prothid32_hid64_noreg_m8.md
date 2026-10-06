# ge_s15_prothid32_hid64_noreg_m8

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'ge_s15_prothid32_hid64_noreg_m8'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8636      0.9067      0.9579      0.8819      0.9423      0.8963
ALL                 5      0.8636      0.9067      0.9579      0.8819      0.9423      0.8963

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.9080      0.9167     0.0267  5
max valid BA                0.9193      0.9219     0.0242  5
best valid F1               0.8785      0.8846     0.0337  5
test BA                     0.8852      0.9010     0.0482  5
test AUC                    0.9478      0.9538     0.0269  5
test AUC in-protein         0.9293      0.9375     0.0322  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9391      0.9432     0.0154  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8431      0.8571     0.0614  5
test sensitivity            0.8636      0.8542     0.0757  5
test specificity            0.9067      0.9271     0.0463  5
test precision              0.8269      0.8409     0.0723  5
test loss                   0.3432      0.3329     0.1380  5
FPR (FP/(FP+TN))            0.0933      0.0729     0.0463  5
FNR (FN/(FN+TP))            0.1364      0.1458     0.0757  5

=== abs(sensitivity-specificity) gap: mean=0.0644 median=0.0318 n=5 ===
sensitivity std across seeds (by group): mean=0.0757 median=0.0757 n=1
specificity std across seeds (by group): mean=0.0463 median=0.0463 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9080      0.9167     0.0267  5
  max valid BA                0.9193      0.9219     0.0242  5
  best valid F1               0.8785      0.8846     0.0337  5
  test BA                     0.8852      0.9010     0.0482  5
  test AUC                    0.9478      0.9538     0.0269  5
  test AUC in-protein         0.9293      0.9375     0.0322  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9391      0.9432     0.0154  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8431      0.8571     0.0614  5
  test sensitivity            0.8636      0.8542     0.0757  5
  test specificity            0.9067      0.9271     0.0463  5
  test precision              0.8269      0.8409     0.0723  5
  test loss                   0.3432      0.3329     0.1380  5
  FPR (FP/(FP+TN))            0.0933      0.0729     0.0463  5
  FNR (FN/(FN+TP))            0.1364      0.1458     0.0757  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_m8 --seeds=0,1,2,3,4`
