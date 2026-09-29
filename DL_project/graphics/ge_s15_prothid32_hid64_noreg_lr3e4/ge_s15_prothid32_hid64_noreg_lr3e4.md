# ge_s15_prothid32_hid64_noreg_lr3e4

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'ge_s15_prothid32_hid64_noreg_lr3e4'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8762      0.9129      0.9572      0.8734      0.9343      0.8796
ALL                 5      0.8762      0.9129      0.9572      0.8734      0.9343      0.8796

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8955      0.8906     0.0208  5
max valid BA                0.9070      0.9115     0.0252  5
best valid F1               0.8647      0.8776     0.0370  5
test BA                     0.8945      0.8906     0.0348  5
test AUC                    0.9504      0.9618     0.0317  5
test AUC in-protein         0.9310      0.9398     0.0313  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9402      0.9432     0.0296  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8567      0.8602     0.0489  5
test sensitivity            0.8762      0.8776     0.0434  5
test specificity            0.9129      0.9381     0.0565  5
test precision              0.8419      0.8723     0.0795  5
test loss                   0.3466      0.2914     0.1808  5
FPR (FP/(FP+TN))            0.0871      0.0619     0.0565  5
FNR (FN/(FN+TP))            0.1238      0.1224     0.0434  5

=== abs(sensitivity-specificity) gap: mean=0.0620 median=0.0631 n=5 ===
sensitivity std across seeds (by group): mean=0.0434 median=0.0434 n=1
specificity std across seeds (by group): mean=0.0565 median=0.0565 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8955      0.8906     0.0208  5
  max valid BA                0.9070      0.9115     0.0252  5
  best valid F1               0.8647      0.8776     0.0370  5
  test BA                     0.8945      0.8906     0.0348  5
  test AUC                    0.9504      0.9618     0.0317  5
  test AUC in-protein         0.9310      0.9398     0.0313  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9402      0.9432     0.0296  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8567      0.8602     0.0489  5
  test sensitivity            0.8762      0.8776     0.0434  5
  test specificity            0.9129      0.9381     0.0565  5
  test precision              0.8419      0.8723     0.0795  5
  test loss                   0.3466      0.2914     0.1808  5
  FPR (FP/(FP+TN))            0.0871      0.0619     0.0565  5
  FNR (FN/(FN+TP))            0.1238      0.1224     0.0434  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_lr3e4 --seeds=0,1,2,3,4`
