# ge_s15_prothid32_hid64_noreg_adv

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32_hid64_noreg_adv'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8762      0.8567      0.9118      0.7945      0.9097      0.8340
ALL                 5      0.8762      0.8567      0.9118      0.7945      0.9097      0.8340

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8541      0.8698     0.0459  5
max valid BA                0.8718      0.8891     0.0320  5
best valid F1               0.8136      0.8381     0.0454  5
test BA                     0.8664      0.8802     0.0413  5
test AUC                    0.9359      0.9352     0.0239  5
test AUC in-protein         0.9330      0.9211     0.0288  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9348      0.9433     0.0255  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8124      0.8269     0.0546  5
test sensitivity            0.8762      0.8571     0.0409  5
test specificity            0.8567      0.8646     0.0564  5
test precision              0.7593      0.7679     0.0753  5
test loss                   0.3142      0.3194     0.0694  5
FPR (FP/(FP+TN))            0.1433      0.1354     0.0564  5
FNR (FN/(FN+TP))            0.1238      0.1429     0.0409  5

=== abs(sensitivity-specificity) gap: mean=0.0437 median=0.0428 n=5 ===
sensitivity std across seeds (by group): mean=0.0409 median=0.0409 n=1
specificity std across seeds (by group): mean=0.0564 median=0.0564 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8541      0.8698     0.0459  5
  max valid BA                0.8718      0.8891     0.0320  5
  best valid F1               0.8136      0.8381     0.0454  5
  test BA                     0.8664      0.8802     0.0413  5
  test AUC                    0.9359      0.9352     0.0239  5
  test AUC in-protein         0.9330      0.9211     0.0288  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9348      0.9433     0.0255  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8124      0.8269     0.0546  5
  test sensitivity            0.8762      0.8571     0.0409  5
  test specificity            0.8567      0.8646     0.0564  5
  test precision              0.7593      0.7679     0.0753  5
  test loss                   0.3142      0.3194     0.0694  5
  FPR (FP/(FP+TN))            0.1433      0.1354     0.0564  5
  FNR (FN/(FN+TP))            0.1238      0.1429     0.0409  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_adv --seeds=0,1,2,3,4`
