# ge_s15_prothid32_hid64_noreg_nodebilin

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32_hid64_noreg_nodebilin'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8598      0.8836      0.9282      0.8753      0.9303      0.8859
ALL                 5      0.8598      0.8836      0.9282      0.8753      0.9303      0.8859

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8842      0.8885     0.0375  5
max valid BA                0.9081      0.9094     0.0356  5
best valid F1               0.8653      0.8866     0.0479  5
test BA                     0.8717      0.8854     0.0538  5
test AUC                    0.9335      0.9509     0.0347  5
test AUC in-protein         0.9297      0.9424     0.0378  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9262      0.9401     0.0435  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8234      0.8454     0.0699  5
test sensitivity            0.8598      0.8542     0.0668  5
test specificity            0.8836      0.8842     0.0547  5
test precision              0.7922      0.8070     0.0868  5
test loss                   0.3722      0.3627     0.1187  5
FPR (FP/(FP+TN))            0.1164      0.1158     0.0547  5
FNR (FN/(FN+TP))            0.1402      0.1458     0.0668  5

=== abs(sensitivity-specificity) gap: mean=0.0535 median=0.0625 n=5 ===
sensitivity std across seeds (by group): mean=0.0668 median=0.0668 n=1
specificity std across seeds (by group): mean=0.0547 median=0.0547 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8842      0.8885     0.0375  5
  max valid BA                0.9081      0.9094     0.0356  5
  best valid F1               0.8653      0.8866     0.0479  5
  test BA                     0.8717      0.8854     0.0538  5
  test AUC                    0.9335      0.9509     0.0347  5
  test AUC in-protein         0.9297      0.9424     0.0378  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9262      0.9401     0.0435  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8234      0.8454     0.0699  5
  test sensitivity            0.8598      0.8542     0.0668  5
  test specificity            0.8836      0.8842     0.0547  5
  test precision              0.7922      0.8070     0.0868  5
  test loss                   0.3722      0.3627     0.1187  5
  FPR (FP/(FP+TN))            0.1164      0.1158     0.0547  5
  FNR (FN/(FN+TP))            0.1402      0.1458     0.0668  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_nodebilin --seeds=0,1,2,3,4`
