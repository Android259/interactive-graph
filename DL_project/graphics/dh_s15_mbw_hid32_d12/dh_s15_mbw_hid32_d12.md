# dh_s15_mbw_hid32_d12

## Summary (analysis/summarize_label.py)

```
Summary: 'dh_s15_mbw_hid32_d12'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.4961      0.5898      0.5351      0.5014      0.5948      0.5734
ALL                 5      0.4961      0.5898      0.5351      0.5014      0.5948      0.5734

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5650      0.5759     0.0431  5
max valid BA                0.5841      0.5990     0.0306  5
best valid F1               0.3390      0.3519     0.0415  5
test BA                     0.5430      0.5441     0.0099  5
test AUC                    0.5502      0.5516     0.0255  5
test AUC in-protein         0.5849      0.5511     0.0576  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.5912      0.5629     0.0690  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.2977      0.2903     0.0254  5
test sensitivity            0.4961      0.5625     0.1548  5
test specificity            0.5898      0.4932     0.1554  5
test precision              0.2211      0.2214     0.0182  5
test loss                   0.6717      0.6794     0.0177  5
FPR (FP/(FP+TN))            0.4102      0.5068     0.1554  5
FNR (FN/(FN+TP))            0.5039      0.4375     0.1548  5

=== abs(sensitivity-specificity) gap: mean=0.2490 median=0.1646 n=5 ===
sensitivity std across seeds (by group): mean=0.1548 median=0.1548 n=1
specificity std across seeds (by group): mean=0.1554 median=0.1554 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5650      0.5759     0.0431  5
  max valid BA                0.5841      0.5990     0.0306  5
  best valid F1               0.3390      0.3519     0.0415  5
  test BA                     0.5430      0.5441     0.0099  5
  test AUC                    0.5502      0.5516     0.0255  5
  test AUC in-protein         0.5849      0.5511     0.0576  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.5912      0.5629     0.0690  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.2977      0.2903     0.0254  5
  test sensitivity            0.4961      0.5625     0.1548  5
  test specificity            0.5898      0.4932     0.1554  5
  test precision              0.2211      0.2214     0.0182  5
  test loss                   0.6717      0.6794     0.0177  5
  FPR (FP/(FP+TN))            0.4102      0.5068     0.1554  5
  FNR (FN/(FN+TP))            0.5039      0.4375     0.1548  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label dh_s15_mbw_hid32_d12 --seeds=0,1,2,3,4`
