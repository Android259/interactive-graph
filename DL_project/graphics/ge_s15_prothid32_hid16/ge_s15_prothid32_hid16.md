# ge_s15_prothid32_hid16

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32_hid16'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8845      0.8693      0.9412      0.8639      0.9468      0.8486
ALL                 5      0.8845      0.8693      0.9412      0.8639      0.9468      0.8486

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8758      0.8781     0.0265  5
max valid BA                0.8977      0.8988     0.0296  5
best valid F1               0.8451      0.8468     0.0368  5
test BA                     0.8769      0.8820     0.0374  5
test AUC                    0.9415      0.9466     0.0215  5
test AUC in-protein         0.9276      0.9319     0.0275  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9343      0.9370     0.0204  5
  (proteins contributing)     19.0000     19.0000     1.5811  5
test F1                     0.8256      0.8302     0.0481  5
test sensitivity            0.8845      0.8980     0.0490  5
test specificity            0.8693      0.8660     0.0437  5
test precision              0.7759      0.7719     0.0638  5
test loss                   0.3079      0.3021     0.0689  5
FPR (FP/(FP+TN))            0.1307      0.1340     0.0437  5
FNR (FN/(FN+TP))            0.1155      0.1020     0.0490  5

=== abs(sensitivity-specificity) gap: mean=0.0441 median=0.0417 n=5 ===
sensitivity std across seeds (by group): mean=0.0490 median=0.0490 n=1
specificity std across seeds (by group): mean=0.0437 median=0.0437 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8758      0.8781     0.0265  5
  max valid BA                0.8977      0.8988     0.0296  5
  best valid F1               0.8451      0.8468     0.0368  5
  test BA                     0.8769      0.8820     0.0374  5
  test AUC                    0.9415      0.9466     0.0215  5
  test AUC in-protein         0.9276      0.9319     0.0275  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9343      0.9370     0.0204  5
    (proteins contributing)     19.0000     19.0000     1.5811  5
  test F1                     0.8256      0.8302     0.0481  5
  test sensitivity            0.8845      0.8980     0.0490  5
  test specificity            0.8693      0.8660     0.0437  5
  test precision              0.7759      0.7719     0.0638  5
  test loss                   0.3079      0.3021     0.0689  5
  FPR (FP/(FP+TN))            0.1307      0.1340     0.0437  5
  FNR (FN/(FN+TP))            0.1155      0.1020     0.0490  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid16 --seeds=0,1,2,3,4`
