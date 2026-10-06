# ge_s15_prothid32_hid64_noreg_burybias

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32_hid64_noreg_burybias'
rows: 4

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    4      0.8654      0.9271      0.9651      0.8890      0.9435      0.9039
ALL                 4      0.8654      0.9271      0.9651      0.8890      0.9435      0.9039

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.9046      0.8958     0.0222  4
max valid BA                0.9237      0.9229     0.0112  4
best valid F1               0.8867      0.8865     0.0071  4
test BA                     0.8962      0.9021     0.0344  4
test AUC                    0.9615      0.9635     0.0079  4
test AUC in-protein         0.9389      0.9386     0.0022  4
  (proteins averaged)      10.0000      9.5000     2.4495  4
test AUC in-protein (pairs)      0.9421      0.9419     0.0163  4
  (proteins contributing)     18.7500     18.5000     1.7078  4
test F1                     0.8602      0.8682     0.0413  4
test sensitivity            0.8654      0.8663     0.0642  4
test specificity            0.9271      0.9223     0.0150  4
test precision              0.8563      0.8516     0.0291  4
test loss                   0.2779      0.2623     0.0473  4
FPR (FP/(FP+TN))            0.0729      0.0777     0.0150  4
FNR (FN/(FN+TP))            0.1346      0.1337     0.0642  4

=== abs(sensitivity-specificity) gap: mean=0.0725 median=0.0716 n=4 ===
sensitivity std across seeds (by group): mean=0.0642 median=0.0642 n=1
specificity std across seeds (by group): mean=0.0150 median=0.0150 n=1

=== By group ===
groups_species15 (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9046      0.8958     0.0222  4
  max valid BA                0.9237      0.9229     0.0112  4
  best valid F1               0.8867      0.8865     0.0071  4
  test BA                     0.8962      0.9021     0.0344  4
  test AUC                    0.9615      0.9635     0.0079  4
  test AUC in-protein         0.9389      0.9386     0.0022  4
    (proteins averaged)      10.0000      9.5000     2.4495  4
  test AUC in-protein (pairs)      0.9421      0.9419     0.0163  4
    (proteins contributing)     18.7500     18.5000     1.7078  4
  test F1                     0.8602      0.8682     0.0413  4
  test sensitivity            0.8654      0.8663     0.0642  4
  test specificity            0.9271      0.9223     0.0150  4
  test precision              0.8563      0.8516     0.0291  4
  test loss                   0.2779      0.2623     0.0473  4
  FPR (FP/(FP+TN))            0.0729      0.0777     0.0150  4
  FNR (FN/(FN+TP))            0.1346      0.1337     0.0642  4
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_burybias --seeds=0,1,2,3,4`
