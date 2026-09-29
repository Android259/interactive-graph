# ge_s15_prothid32_hid64_noreg

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32_hid64_noreg'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.9008      0.9024      0.9508      0.8769      0.9338      0.8798
ALL                 5      0.9008      0.9024      0.9508      0.8769      0.9338      0.8798

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8914      0.8958     0.0289  5
max valid BA                0.9068      0.9115     0.0296  5
best valid F1               0.8623      0.8750     0.0419  5
test BA                     0.9016      0.9062     0.0253  5
test AUC                    0.9534      0.9592     0.0248  5
test AUC in-protein         0.9427      0.9543     0.0249  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9432      0.9412     0.0174  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8611      0.8687     0.0359  5
test sensitivity            0.9008      0.8980     0.0311  5
test specificity            0.9024      0.9167     0.0444  5
test precision              0.8270      0.8491     0.0601  5
test loss                   0.3152      0.2780     0.1192  5
FPR (FP/(FP+TN))            0.0976      0.0833     0.0444  5
FNR (FN/(FN+TP))            0.0992      0.1020     0.0311  5

=== abs(sensitivity-specificity) gap: mean=0.0400 median=0.0217 n=5 ===
sensitivity std across seeds (by group): mean=0.0311 median=0.0311 n=1
specificity std across seeds (by group): mean=0.0444 median=0.0444 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8914      0.8958     0.0289  5
  max valid BA                0.9068      0.9115     0.0296  5
  best valid F1               0.8623      0.8750     0.0419  5
  test BA                     0.9016      0.9062     0.0253  5
  test AUC                    0.9534      0.9592     0.0248  5
  test AUC in-protein         0.9427      0.9543     0.0249  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9432      0.9412     0.0174  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8611      0.8687     0.0359  5
  test sensitivity            0.9008      0.8980     0.0311  5
  test specificity            0.9024      0.9167     0.0444  5
  test precision              0.8270      0.8491     0.0601  5
  test loss                   0.3152      0.2780     0.1192  5
  FPR (FP/(FP+TN))            0.0976      0.0833     0.0444  5
  FNR (FN/(FN+TP))            0.0992      0.1020     0.0311  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg --seeds=0,1,2,3,4`
