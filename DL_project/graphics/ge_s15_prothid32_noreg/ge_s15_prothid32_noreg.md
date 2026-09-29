# ge_s15_prothid32_noreg

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32_noreg'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8762      0.8629      0.9293      0.8611      0.9382      0.8610
ALL                 5      0.8762      0.8629      0.9293      0.8611      0.9382      0.8610

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8861      0.8906     0.0256  5
max valid BA                0.8996      0.9062     0.0261  5
best valid F1               0.8487      0.8519     0.0384  5
test BA                     0.8695      0.8854     0.0415  5
test AUC                    0.9351      0.9514     0.0325  5
test AUC in-protein         0.9169      0.9154     0.0409  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9303      0.9328     0.0291  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8176      0.8400     0.0559  5
test sensitivity            0.8762      0.8750     0.0283  5
test specificity            0.8629      0.8737     0.0622  5
test precision              0.7688      0.7857     0.0820  5
test loss                   0.3364      0.2844     0.1150  5
FPR (FP/(FP+TN))            0.1371      0.1263     0.0622  5
FNR (FN/(FN+TP))            0.1238      0.1250     0.0283  5

=== abs(sensitivity-specificity) gap: mean=0.0418 median=0.0430 n=5 ===
sensitivity std across seeds (by group): mean=0.0283 median=0.0283 n=1
specificity std across seeds (by group): mean=0.0622 median=0.0622 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8861      0.8906     0.0256  5
  max valid BA                0.8996      0.9062     0.0261  5
  best valid F1               0.8487      0.8519     0.0384  5
  test BA                     0.8695      0.8854     0.0415  5
  test AUC                    0.9351      0.9514     0.0325  5
  test AUC in-protein         0.9169      0.9154     0.0409  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9303      0.9328     0.0291  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8176      0.8400     0.0559  5
  test sensitivity            0.8762      0.8750     0.0283  5
  test specificity            0.8629      0.8737     0.0622  5
  test precision              0.7688      0.7857     0.0820  5
  test loss                   0.3364      0.2844     0.1150  5
  FPR (FP/(FP+TN))            0.1371      0.1263     0.0622  5
  FNR (FN/(FN+TP))            0.1238      0.1250     0.0283  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_noreg --seeds=0,1,2,3,4`
