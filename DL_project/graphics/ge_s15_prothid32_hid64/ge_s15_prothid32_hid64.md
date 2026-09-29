# ge_s15_prothid32_hid64

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32_hid64'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.9009      0.8775      0.9561      0.8721      0.9257      0.8942
ALL                 5      0.9009      0.8775      0.9561      0.8721      0.9257      0.8942

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8872      0.8854     0.0284  5
max valid BA                0.9099      0.9115     0.0279  5
best valid F1               0.8670      0.8687     0.0388  5
test BA                     0.8892      0.8906     0.0333  5
test AUC                    0.9401      0.9514     0.0272  5
test AUC in-protein         0.9268      0.9369     0.0300  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9324      0.9450     0.0249  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8412      0.8381     0.0453  5
test sensitivity            0.9009      0.9167     0.0262  5
test specificity            0.8775      0.8750     0.0425  5
test precision              0.7898      0.7818     0.0615  5
test loss                   0.2976      0.2668     0.0733  5
FPR (FP/(FP+TN))            0.1225      0.1250     0.0425  5
FNR (FN/(FN+TP))            0.0991      0.0833     0.0262  5

=== abs(sensitivity-specificity) gap: mean=0.0235 median=0.0208 n=5 ===
sensitivity std across seeds (by group): mean=0.0262 median=0.0262 n=1
specificity std across seeds (by group): mean=0.0425 median=0.0425 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8872      0.8854     0.0284  5
  max valid BA                0.9099      0.9115     0.0279  5
  best valid F1               0.8670      0.8687     0.0388  5
  test BA                     0.8892      0.8906     0.0333  5
  test AUC                    0.9401      0.9514     0.0272  5
  test AUC in-protein         0.9268      0.9369     0.0300  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9324      0.9450     0.0249  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8412      0.8381     0.0453  5
  test sensitivity            0.9009      0.9167     0.0262  5
  test specificity            0.8775      0.8750     0.0425  5
  test precision              0.7898      0.7818     0.0615  5
  test loss                   0.2976      0.2668     0.0733  5
  FPR (FP/(FP+TN))            0.1225      0.1250     0.0425  5
  FNR (FN/(FN+TP))            0.0991      0.0833     0.0262  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64 --seeds=0,1,2,3,4`
