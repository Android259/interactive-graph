# ge_s15_prothid32_hid64_noreg_swe

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32_hid64_noreg_swe'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8679      0.9047      0.9635      0.9039      0.9427      0.8941
ALL                 5      0.8679      0.9047      0.9635      0.9039      0.9427      0.8941

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8965      0.9191     0.0400  5
max valid BA                0.9184      0.9271     0.0272  5
best valid F1               0.8758      0.8889     0.0373  5
test BA                     0.8863      0.9062     0.0527  5
test AUC                    0.9489      0.9638     0.0348  5
test AUC in-protein         0.9515      0.9508     0.0094  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9429      0.9450     0.0168  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8462      0.8750     0.0722  5
test sensitivity            0.8679      0.8750     0.0417  5
test specificity            0.9047      0.9278     0.0647  5
test precision              0.8274      0.8627     0.0986  5
test loss                   0.3216      0.2734     0.1488  5
FPR (FP/(FP+TN))            0.0953      0.0722     0.0647  5
FNR (FN/(FN+TP))            0.1321      0.1250     0.0417  5

=== abs(sensitivity-specificity) gap: mean=0.0376 median=0.0312 n=5 ===
sensitivity std across seeds (by group): mean=0.0417 median=0.0417 n=1
specificity std across seeds (by group): mean=0.0647 median=0.0647 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8965      0.9191     0.0400  5
  max valid BA                0.9184      0.9271     0.0272  5
  best valid F1               0.8758      0.8889     0.0373  5
  test BA                     0.8863      0.9062     0.0527  5
  test AUC                    0.9489      0.9638     0.0348  5
  test AUC in-protein         0.9515      0.9508     0.0094  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9429      0.9450     0.0168  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8462      0.8750     0.0722  5
  test sensitivity            0.8679      0.8750     0.0417  5
  test specificity            0.9047      0.9278     0.0647  5
  test precision              0.8274      0.8627     0.0986  5
  test loss                   0.3216      0.2734     0.1488  5
  FPR (FP/(FP+TN))            0.0953      0.0722     0.0647  5
  FNR (FN/(FN+TP))            0.1321      0.1250     0.0417  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_swe --seeds=0,1,2,3,4`
