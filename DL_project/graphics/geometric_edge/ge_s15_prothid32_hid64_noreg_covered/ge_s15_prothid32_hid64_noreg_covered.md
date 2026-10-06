# ge_s15_prothid32_hid64_noreg_covered

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32_hid64_noreg_covered'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group                       n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15_covered    5      0.8978      0.8971      0.9546      0.8786      0.9319      0.9141
ALL                         5      0.8978      0.8971      0.9546      0.8786      0.9319      0.9141

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.9007      0.9008     0.0396  5
max valid BA                0.9230      0.9309     0.0405  5
best valid F1               0.8950      0.9167     0.0562  5
test BA                     0.8974      0.9045     0.0237  5
test AUC                    0.9500      0.9573     0.0227  5
test AUC in-protein         0.9272      0.9378     0.0361  5
  (proteins averaged)       9.8000     10.0000     0.8367  5
test AUC in-protein (pairs)      0.9328      0.9404     0.0359  5
  (proteins contributing)     17.2000     17.0000     0.8367  5
test F1                     0.8620      0.8817     0.0426  5
test sensitivity            0.8978      0.8980     0.0181  5
test specificity            0.8971      0.9211     0.0461  5
test precision              0.8319      0.8776     0.0759  5
test loss                   0.3213      0.3752     0.0808  5
FPR (FP/(FP+TN))            0.1029      0.0789     0.0461  5
FNR (FN/(FN+TP))            0.1022      0.1020     0.0181  5

=== abs(sensitivity-specificity) gap: mean=0.0408 median=0.0428 n=5 ===
sensitivity std across seeds (by group): mean=0.0181 median=0.0181 n=1
specificity std across seeds (by group): mean=0.0461 median=0.0461 n=1

=== By group ===
groups_species15_covered (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9007      0.9008     0.0396  5
  max valid BA                0.9230      0.9309     0.0405  5
  best valid F1               0.8950      0.9167     0.0562  5
  test BA                     0.8974      0.9045     0.0237  5
  test AUC                    0.9500      0.9573     0.0227  5
  test AUC in-protein         0.9272      0.9378     0.0361  5
    (proteins averaged)       9.8000     10.0000     0.8367  5
  test AUC in-protein (pairs)      0.9328      0.9404     0.0359  5
    (proteins contributing)     17.2000     17.0000     0.8367  5
  test F1                     0.8620      0.8817     0.0426  5
  test sensitivity            0.8978      0.8980     0.0181  5
  test specificity            0.8971      0.9211     0.0461  5
  test precision              0.8319      0.8776     0.0759  5
  test loss                   0.3213      0.3752     0.0808  5
  FPR (FP/(FP+TN))            0.1029      0.0789     0.0461  5
  FNR (FN/(FN+TP))            0.1022      0.1020     0.0181  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_covered --seeds=0,1,2,3,4`
