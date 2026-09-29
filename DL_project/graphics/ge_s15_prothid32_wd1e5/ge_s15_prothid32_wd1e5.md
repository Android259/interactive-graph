# ge_s15_prothid32_wd1e5

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32_wd1e5'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8844      0.8422      0.9241      0.8315      0.9258      0.8590
ALL                 5      0.8844      0.8422      0.9241      0.8315      0.9258      0.8590

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8757      0.8698     0.0223  5
max valid BA                0.8924      0.8906     0.0188  5
best valid F1               0.8422      0.8454     0.0311  5
test BA                     0.8633      0.8698     0.0362  5
test AUC                    0.9319      0.9388     0.0354  5
test AUC in-protein         0.9268      0.9251     0.0173  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9305      0.9210     0.0189  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8062      0.8113     0.0482  5
test sensitivity            0.8844      0.8776     0.0226  5
test specificity            0.8422      0.8438     0.0534  5
test precision              0.7421      0.7414     0.0677  5
test loss                   0.3364      0.3099     0.1183  5
FPR (FP/(FP+TN))            0.1578      0.1562     0.0534  5
FNR (FN/(FN+TP))            0.1156      0.1224     0.0226  5

=== abs(sensitivity-specificity) gap: mean=0.0459 median=0.0521 n=5 ===
sensitivity std across seeds (by group): mean=0.0226 median=0.0226 n=1
specificity std across seeds (by group): mean=0.0534 median=0.0534 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8757      0.8698     0.0223  5
  max valid BA                0.8924      0.8906     0.0188  5
  best valid F1               0.8422      0.8454     0.0311  5
  test BA                     0.8633      0.8698     0.0362  5
  test AUC                    0.9319      0.9388     0.0354  5
  test AUC in-protein         0.9268      0.9251     0.0173  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9305      0.9210     0.0189  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8062      0.8113     0.0482  5
  test sensitivity            0.8844      0.8776     0.0226  5
  test specificity            0.8422      0.8438     0.0534  5
  test precision              0.7421      0.7414     0.0677  5
  test loss                   0.3364      0.3099     0.1183  5
  FPR (FP/(FP+TN))            0.1578      0.1562     0.0534  5
  FNR (FN/(FN+TP))            0.1156      0.1224     0.0226  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_wd1e5 --seeds=0,1,2,3,4`
