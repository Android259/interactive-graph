# dh_s15_mbw_hid32_d11

## Summary (analysis/summarize_label.py)

```
Summary: 'dh_s15_mbw_hid32_d11'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.4633      0.6069      0.4075      0.6050      0.4493      0.7212
ALL                 5      0.4633      0.6069      0.4075      0.6050      0.4493      0.7212

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5707      0.5658     0.0364  5
max valid BA                0.5852      0.5793     0.0278  5
best valid F1               0.3417      0.3314     0.0367  5
test BA                     0.5351      0.5300     0.0381  5
test AUC                    0.5308      0.5207     0.0445  5
test AUC in-protein         0.5733      0.5898     0.0680  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.5535      0.5578     0.0471  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.2852      0.2762     0.0489  5
test sensitivity            0.4633      0.5208     0.1616  5
test specificity            0.6069      0.6029     0.1550  5
test precision              0.2158      0.2069     0.0287  5
test loss                   0.6831      0.6820     0.0100  5
FPR (FP/(FP+TN))            0.3931      0.3971     0.1550  5
FNR (FN/(FN+TP))            0.5367      0.4792     0.1616  5

=== abs(sensitivity-specificity) gap: mean=0.2248 median=0.1475 n=5 ===
sensitivity std across seeds (by group): mean=0.1616 median=0.1616 n=1
specificity std across seeds (by group): mean=0.1550 median=0.1550 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5707      0.5658     0.0364  5
  max valid BA                0.5852      0.5793     0.0278  5
  best valid F1               0.3417      0.3314     0.0367  5
  test BA                     0.5351      0.5300     0.0381  5
  test AUC                    0.5308      0.5207     0.0445  5
  test AUC in-protein         0.5733      0.5898     0.0680  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.5535      0.5578     0.0471  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.2852      0.2762     0.0489  5
  test sensitivity            0.4633      0.5208     0.1616  5
  test specificity            0.6069      0.6029     0.1550  5
  test precision              0.2158      0.2069     0.0287  5
  test loss                   0.6831      0.6820     0.0100  5
  FPR (FP/(FP+TN))            0.3931      0.3971     0.1550  5
  FNR (FN/(FN+TP))            0.5367      0.4792     0.1616  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label dh_s15_mbw_hid32_d11 --seeds=0,1,2,3,4`
