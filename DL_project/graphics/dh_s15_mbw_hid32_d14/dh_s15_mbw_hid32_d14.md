# dh_s15_mbw_hid32_d14

## Summary (analysis/summarize_label.py)

```
Summary: 'dh_s15_mbw_hid32_d14'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.4119      0.5874      0.4163      0.6088      0.5567      0.6186
ALL                 5      0.4119      0.5874      0.4163      0.6088      0.5567      0.6186

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5750      0.5665     0.0380  5
max valid BA                0.5876      0.5824     0.0308  5
best valid F1               0.3532      0.3558     0.0351  5
test BA                     0.4996      0.5134     0.0704  5
test AUC                    0.5058      0.5365     0.1032  5
test AUC in-protein         0.5470      0.6313     0.1422  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.5090      0.5439     0.1217  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.2433      0.2308     0.0760  5
test sensitivity            0.4119      0.4082     0.2396  5
test specificity            0.5874      0.4851     0.2416  5
test precision              0.1935      0.2000     0.0380  5
test loss                   0.6865      0.6831     0.0203  5
FPR (FP/(FP+TN))            0.4126      0.5149     0.2416  5
FNR (FN/(FN+TP))            0.5881      0.5918     0.2396  5

=== abs(sensitivity-specificity) gap: mean=0.3503 median=0.3280 n=5 ===
sensitivity std across seeds (by group): mean=0.2396 median=0.2396 n=1
specificity std across seeds (by group): mean=0.2416 median=0.2416 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5750      0.5665     0.0380  5
  max valid BA                0.5876      0.5824     0.0308  5
  best valid F1               0.3532      0.3558     0.0351  5
  test BA                     0.4996      0.5134     0.0704  5
  test AUC                    0.5058      0.5365     0.1032  5
  test AUC in-protein         0.5470      0.6313     0.1422  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.5090      0.5439     0.1217  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.2433      0.2308     0.0760  5
  test sensitivity            0.4119      0.4082     0.2396  5
  test specificity            0.5874      0.4851     0.2416  5
  test precision              0.1935      0.2000     0.0380  5
  test loss                   0.6865      0.6831     0.0203  5
  FPR (FP/(FP+TN))            0.4126      0.5149     0.2416  5
  FNR (FN/(FN+TP))            0.5881      0.5918     0.2396  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label dh_s15_mbw_hid32_d14 --seeds=0,1,2,3,4`
