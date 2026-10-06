# ge_s15_prothid32_hid64_noreg_prot64

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'ge_s15_prothid32_hid64_noreg_prot64'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8762      0.8922      0.9587      0.8900      0.9302      0.8901
ALL                 5      0.8762      0.8922      0.9587      0.8900      0.9302      0.8901

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8904      0.8906     0.0287  5
max valid BA                0.9101      0.9142     0.0332  5
best valid F1               0.8667      0.8679     0.0439  5
test BA                     0.8842      0.8974     0.0505  5
test AUC                    0.9451      0.9533     0.0353  5
test AUC in-protein         0.9284      0.9331     0.0275  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9359      0.9398     0.0301  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8399      0.8544     0.0668  5
test sensitivity            0.8762      0.8958     0.0501  5
test specificity            0.8922      0.9062     0.0572  5
test precision              0.8080      0.8163     0.0841  5
test loss                   0.3242      0.2946     0.1229  5
FPR (FP/(FP+TN))            0.1078      0.0938     0.0572  5
FNR (FN/(FN+TP))            0.1238      0.1042     0.0501  5

=== abs(sensitivity-specificity) gap: mean=0.0257 median=0.0225 n=5 ===
sensitivity std across seeds (by group): mean=0.0501 median=0.0501 n=1
specificity std across seeds (by group): mean=0.0572 median=0.0572 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8904      0.8906     0.0287  5
  max valid BA                0.9101      0.9142     0.0332  5
  best valid F1               0.8667      0.8679     0.0439  5
  test BA                     0.8842      0.8974     0.0505  5
  test AUC                    0.9451      0.9533     0.0353  5
  test AUC in-protein         0.9284      0.9331     0.0275  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9359      0.9398     0.0301  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8399      0.8544     0.0668  5
  test sensitivity            0.8762      0.8958     0.0501  5
  test specificity            0.8922      0.9062     0.0572  5
  test precision              0.8080      0.8163     0.0841  5
  test loss                   0.3242      0.2946     0.1229  5
  FPR (FP/(FP+TN))            0.1078      0.0938     0.0572  5
  FNR (FN/(FN+TP))            0.1238      0.1042     0.0501  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_prot64 --seeds=0,1,2,3,4`
