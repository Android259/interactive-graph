# ge_s15_prothid32_hid64_noreg_nodebilinear

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32_hid64_noreg_nodebilinear'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8348      0.9003      0.9054      0.8576      0.9385      0.8756
ALL                 5      0.8348      0.9003      0.9054      0.8576      0.9385      0.8756

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8903      0.8958     0.0412  5
max valid BA                0.9070      0.9091     0.0334  5
best valid F1               0.8598      0.8738     0.0446  5
test BA                     0.8675      0.8954     0.0493  5
test AUC                    0.9385      0.9594     0.0364  5
test AUC in-protein         0.9288      0.9431     0.0333  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9212      0.9401     0.0513  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8219      0.8571     0.0654  5
test sensitivity            0.8348      0.8542     0.0596  5
test specificity            0.9003      0.9158     0.0414  5
test precision              0.8097      0.8400     0.0729  5
test loss                   0.3687      0.3832     0.1315  5
FPR (FP/(FP+TN))            0.0997      0.0842     0.0414  5
FNR (FN/(FN+TP))            0.1652      0.1458     0.0596  5

=== abs(sensitivity-specificity) gap: mean=0.0655 median=0.0799 n=5 ===
sensitivity std across seeds (by group): mean=0.0596 median=0.0596 n=1
specificity std across seeds (by group): mean=0.0414 median=0.0414 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8903      0.8958     0.0412  5
  max valid BA                0.9070      0.9091     0.0334  5
  best valid F1               0.8598      0.8738     0.0446  5
  test BA                     0.8675      0.8954     0.0493  5
  test AUC                    0.9385      0.9594     0.0364  5
  test AUC in-protein         0.9288      0.9431     0.0333  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9212      0.9401     0.0513  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8219      0.8571     0.0654  5
  test sensitivity            0.8348      0.8542     0.0596  5
  test specificity            0.9003      0.9158     0.0414  5
  test precision              0.8097      0.8400     0.0729  5
  test loss                   0.3687      0.3832     0.1315  5
  FPR (FP/(FP+TN))            0.0997      0.0842     0.0414  5
  FNR (FN/(FN+TP))            0.1652      0.1458     0.0596  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_nodebilinear --seeds=0,1,2,3,4`
