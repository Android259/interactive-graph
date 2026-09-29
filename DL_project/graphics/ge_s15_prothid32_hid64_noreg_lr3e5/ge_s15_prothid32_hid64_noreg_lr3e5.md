# ge_s15_prothid32_hid64_noreg_lr3e5

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'ge_s15_prothid32_hid64_noreg_lr3e5'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8311      0.9003      0.9635      0.9096      0.9138      0.9087
ALL                 5      0.8311      0.9003      0.9635      0.9096      0.9138      0.9087

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8947      0.9219     0.0509  5
max valid BA                0.9113      0.9271     0.0343  5
best valid F1               0.8726      0.8846     0.0456  5
test BA                     0.8657      0.8824     0.0616  5
test AUC                    0.9412      0.9546     0.0399  5
test AUC in-protein         0.9261      0.9421     0.0327  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9272      0.9412     0.0340  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8204      0.8511     0.0809  5
test sensitivity            0.8311      0.8542     0.0746  5
test specificity            0.9003      0.9158     0.0575  5
test precision              0.8119      0.8462     0.0970  5
test loss                   0.3066      0.2657     0.0894  5
FPR (FP/(FP+TN))            0.0997      0.0842     0.0575  5
FNR (FN/(FN+TP))            0.1689      0.1458     0.0746  5

=== abs(sensitivity-specificity) gap: mean=0.0696 median=0.0833 n=5 ===
sensitivity std across seeds (by group): mean=0.0746 median=0.0746 n=1
specificity std across seeds (by group): mean=0.0575 median=0.0575 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8947      0.9219     0.0509  5
  max valid BA                0.9113      0.9271     0.0343  5
  best valid F1               0.8726      0.8846     0.0456  5
  test BA                     0.8657      0.8824     0.0616  5
  test AUC                    0.9412      0.9546     0.0399  5
  test AUC in-protein         0.9261      0.9421     0.0327  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9272      0.9412     0.0340  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8204      0.8511     0.0809  5
  test sensitivity            0.8311      0.8542     0.0746  5
  test specificity            0.9003      0.9158     0.0575  5
  test precision              0.8119      0.8462     0.0970  5
  test loss                   0.3066      0.2657     0.0894  5
  FPR (FP/(FP+TN))            0.0997      0.0842     0.0575  5
  FNR (FN/(FN+TP))            0.1689      0.1458     0.0746  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_lr3e5 --seeds=0,1,2,3,4`
