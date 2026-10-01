# ge_s15_prothid32_hid64_noreg_liphandicap

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'ge_s15_prothid32_hid64_noreg_liphandicap'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8764      0.8919      0.9572      0.8931      0.9262      0.8921
ALL                 5      0.8764      0.8919      0.9572      0.8931      0.9262      0.8921

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8903      0.8958     0.0342  5
max valid BA                0.9092      0.9167     0.0265  5
best valid F1               0.8667      0.8800     0.0365  5
test BA                     0.8842      0.9062     0.0463  5
test AUC                    0.9492      0.9590     0.0355  5
test AUC in-protein         0.9422      0.9460     0.0141  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9410      0.9412     0.0239  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8387      0.8687     0.0608  5
test sensitivity            0.8764      0.8958     0.0571  5
test specificity            0.8919      0.9053     0.0416  5
test precision              0.8050      0.8302     0.0696  5
test loss                   0.3513      0.2829     0.1928  5
FPR (FP/(FP+TN))            0.1081      0.0947     0.0416  5
FNR (FN/(FN+TP))            0.1236      0.1042     0.0571  5

=== abs(sensitivity-specificity) gap: mean=0.0326 median=0.0312 n=5 ===
sensitivity std across seeds (by group): mean=0.0571 median=0.0571 n=1
specificity std across seeds (by group): mean=0.0416 median=0.0416 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8903      0.8958     0.0342  5
  max valid BA                0.9092      0.9167     0.0265  5
  best valid F1               0.8667      0.8800     0.0365  5
  test BA                     0.8842      0.9062     0.0463  5
  test AUC                    0.9492      0.9590     0.0355  5
  test AUC in-protein         0.9422      0.9460     0.0141  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9410      0.9412     0.0239  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8387      0.8687     0.0608  5
  test sensitivity            0.8764      0.8958     0.0571  5
  test specificity            0.8919      0.9053     0.0416  5
  test precision              0.8050      0.8302     0.0696  5
  test loss                   0.3513      0.2829     0.1928  5
  FPR (FP/(FP+TN))            0.1081      0.0947     0.0416  5
  FNR (FN/(FN+TP))            0.1236      0.1042     0.0571  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_liphandicap --seeds=0,1,2,3,4`
