# ge_s15_prothid32_hid64_noreg_edgeattn

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32_hid64_noreg_edgeattn'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8722      0.9003      0.9605      0.8952      0.9302      0.8963
ALL                 5      0.8722      0.9003      0.9605      0.8952      0.9302      0.8963

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8946      0.9042     0.0419  5
max valid BA                0.9132      0.9167     0.0299  5
best valid F1               0.8711      0.8866     0.0397  5
test BA                     0.8863      0.9078     0.0480  5
test AUC                    0.9467      0.9619     0.0373  5
test AUC in-protein         0.9394      0.9400     0.0411  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9403      0.9513     0.0384  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8433      0.8713     0.0625  5
test sensitivity            0.8722      0.8776     0.0583  5
test specificity            0.9003      0.9062     0.0444  5
test precision              0.8172      0.8302     0.0720  5
test loss                   0.3591      0.2372     0.2202  5
FPR (FP/(FP+TN))            0.0997      0.0938     0.0444  5
FNR (FN/(FN+TP))            0.1278      0.1224     0.0583  5

=== abs(sensitivity-specificity) gap: mean=0.0368 median=0.0288 n=5 ===
sensitivity std across seeds (by group): mean=0.0583 median=0.0583 n=1
specificity std across seeds (by group): mean=0.0444 median=0.0444 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8946      0.9042     0.0419  5
  max valid BA                0.9132      0.9167     0.0299  5
  best valid F1               0.8711      0.8866     0.0397  5
  test BA                     0.8863      0.9078     0.0480  5
  test AUC                    0.9467      0.9619     0.0373  5
  test AUC in-protein         0.9394      0.9400     0.0411  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9403      0.9513     0.0384  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8433      0.8713     0.0625  5
  test sensitivity            0.8722      0.8776     0.0583  5
  test specificity            0.9003      0.9062     0.0444  5
  test precision              0.8172      0.8302     0.0720  5
  test loss                   0.3591      0.2372     0.2202  5
  FPR (FP/(FP+TN))            0.0997      0.0938     0.0444  5
  FNR (FN/(FN+TP))            0.1278      0.1224     0.0583  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_edgeattn --seeds=0,1,2,3,4`
