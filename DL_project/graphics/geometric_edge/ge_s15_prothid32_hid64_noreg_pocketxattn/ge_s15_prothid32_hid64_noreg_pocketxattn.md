# ge_s15_prothid32_hid64_noreg_pocketxattn

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32_hid64_noreg_pocketxattn'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8682      0.9044      0.9594      0.8881      0.9385      0.8921
ALL                 5      0.8682      0.9044      0.9594      0.8881      0.9385      0.8921

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8967      0.9042     0.0372  5
max valid BA                0.9153      0.9219     0.0302  5
best valid F1               0.8740      0.8889     0.0441  5
test BA                     0.8863      0.8958     0.0395  5
test AUC                    0.9481      0.9643     0.0327  5
test AUC in-protein         0.9295      0.9408     0.0331  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9406      0.9433     0.0265  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8452      0.8515     0.0556  5
test sensitivity            0.8682      0.8750     0.0524  5
test specificity            0.9044      0.8958     0.0581  5
test precision              0.8289      0.8113     0.0986  5
test loss                   0.3313      0.2920     0.1372  5
FPR (FP/(FP+TN))            0.0956      0.1042     0.0581  5
FNR (FN/(FN+TP))            0.1318      0.1250     0.0524  5

=== abs(sensitivity-specificity) gap: mean=0.0407 median=0.0112 n=5 ===
sensitivity std across seeds (by group): mean=0.0524 median=0.0524 n=1
specificity std across seeds (by group): mean=0.0581 median=0.0581 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8967      0.9042     0.0372  5
  max valid BA                0.9153      0.9219     0.0302  5
  best valid F1               0.8740      0.8889     0.0441  5
  test BA                     0.8863      0.8958     0.0395  5
  test AUC                    0.9481      0.9643     0.0327  5
  test AUC in-protein         0.9295      0.9408     0.0331  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9406      0.9433     0.0265  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8452      0.8515     0.0556  5
  test sensitivity            0.8682      0.8750     0.0524  5
  test specificity            0.9044      0.8958     0.0581  5
  test precision              0.8289      0.8113     0.0986  5
  test loss                   0.3313      0.2920     0.1372  5
  FPR (FP/(FP+TN))            0.0956      0.1042     0.0581  5
  FNR (FN/(FN+TP))            0.1318      0.1250     0.0524  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_pocketxattn --seeds=0,1,2,3,4`
