# ge_s15_prothid32

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8471      0.8213      0.9278      0.8308      0.9173      0.8319
ALL                 5      0.8471      0.8213      0.9278      0.8308      0.9173      0.8319

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8548      0.8396     0.0332  5
max valid BA                0.8746      0.8750     0.0288  5
best valid F1               0.8163      0.8108     0.0379  5
test BA                     0.8342      0.8281     0.0402  5
test AUC                    0.9171      0.9258     0.0253  5
test AUC in-protein         0.8983      0.8893     0.0372  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9009      0.8796     0.0404  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7710      0.7568     0.0538  5
test sensitivity            0.8471      0.8542     0.0312  5
test specificity            0.8213      0.7835     0.0592  5
test precision              0.7095      0.6667     0.0771  5
test loss                   0.3657      0.3629     0.0717  5
FPR (FP/(FP+TN))            0.1787      0.2165     0.0592  5
FNR (FN/(FN+TP))            0.1529      0.1458     0.0312  5

=== abs(sensitivity-specificity) gap: mean=0.0420 median=0.0406 n=5 ===
sensitivity std across seeds (by group): mean=0.0312 median=0.0312 n=1
specificity std across seeds (by group): mean=0.0592 median=0.0592 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8548      0.8396     0.0332  5
  max valid BA                0.8746      0.8750     0.0288  5
  best valid F1               0.8163      0.8108     0.0379  5
  test BA                     0.8342      0.8281     0.0402  5
  test AUC                    0.9171      0.9258     0.0253  5
  test AUC in-protein         0.8983      0.8893     0.0372  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9009      0.8796     0.0404  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7710      0.7568     0.0538  5
  test sensitivity            0.8471      0.8542     0.0312  5
  test specificity            0.8213      0.7835     0.0592  5
  test precision              0.7095      0.6667     0.0771  5
  test loss                   0.3657      0.3629     0.0717  5
  FPR (FP/(FP+TN))            0.1787      0.2165     0.0592  5
  FNR (FN/(FN+TP))            0.1529      0.1458     0.0312  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32 --seeds=0,1,2,3,4`
