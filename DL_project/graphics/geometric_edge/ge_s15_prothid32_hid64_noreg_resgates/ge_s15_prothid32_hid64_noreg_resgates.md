# ge_s15_prothid32_hid64_noreg_resgates

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32_hid64_noreg_resgates'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8639      0.9106      0.9564      0.8915      0.9178      0.9025
ALL                 5      0.8639      0.9106      0.9564      0.8915      0.9178      0.9025

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8896      0.8854     0.0317  5
max valid BA                0.9102      0.9115     0.0260  5
best valid F1               0.8725      0.8723     0.0320  5
test BA                     0.8873      0.8977     0.0368  5
test AUC                    0.9496      0.9592     0.0340  5
test AUC in-protein         0.9399      0.9544     0.0342  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9482      0.9467     0.0230  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8474      0.8723     0.0498  5
test sensitivity            0.8639      0.8542     0.0465  5
test specificity            0.9106      0.9167     0.0469  5
test precision              0.8341      0.8367     0.0741  5
test loss                   0.3743      0.3039     0.2313  5
FPR (FP/(FP+TN))            0.0894      0.0833     0.0469  5
FNR (FN/(FN+TP))            0.1361      0.1458     0.0465  5

=== abs(sensitivity-specificity) gap: mean=0.0596 median=0.0625 n=5 ===
sensitivity std across seeds (by group): mean=0.0465 median=0.0465 n=1
specificity std across seeds (by group): mean=0.0469 median=0.0469 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8896      0.8854     0.0317  5
  max valid BA                0.9102      0.9115     0.0260  5
  best valid F1               0.8725      0.8723     0.0320  5
  test BA                     0.8873      0.8977     0.0368  5
  test AUC                    0.9496      0.9592     0.0340  5
  test AUC in-protein         0.9399      0.9544     0.0342  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9482      0.9467     0.0230  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8474      0.8723     0.0498  5
  test sensitivity            0.8639      0.8542     0.0465  5
  test specificity            0.9106      0.9167     0.0469  5
  test precision              0.8341      0.8367     0.0741  5
  test loss                   0.3743      0.3039     0.2313  5
  FPR (FP/(FP+TN))            0.0894      0.0833     0.0469  5
  FNR (FN/(FN+TP))            0.1361      0.1458     0.0465  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_resgates --seeds=0,1,2,3,4`
