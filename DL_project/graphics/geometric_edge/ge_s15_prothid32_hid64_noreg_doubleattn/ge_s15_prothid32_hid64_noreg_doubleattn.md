# ge_s15_prothid32_hid64_noreg_doubleattn

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32_hid64_noreg_doubleattn'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8681      0.9025      0.9553      0.8864      0.9425      0.8797
ALL                 5      0.8681      0.9025      0.9553      0.8864      0.9425      0.8797

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8989      0.9062     0.0253  5
max valid BA                0.9111      0.9167     0.0281  5
best valid F1               0.8662      0.8776     0.0390  5
test BA                     0.8853      0.8802     0.0433  5
test AUC                    0.9552      0.9670     0.0269  5
test AUC in-protein         0.9493      0.9486     0.0157  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9483      0.9513     0.0188  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8433      0.8421     0.0576  5
test sensitivity            0.8681      0.8571     0.0586  5
test specificity            0.9025      0.9271     0.0569  5
test precision              0.8235      0.8478     0.0798  5
test loss                   0.2973      0.2340     0.1162  5
FPR (FP/(FP+TN))            0.0975      0.0729     0.0569  5
FNR (FN/(FN+TP))            0.1319      0.1429     0.0586  5

=== abs(sensitivity-specificity) gap: mean=0.0598 median=0.0530 n=5 ===
sensitivity std across seeds (by group): mean=0.0586 median=0.0586 n=1
specificity std across seeds (by group): mean=0.0569 median=0.0569 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8989      0.9062     0.0253  5
  max valid BA                0.9111      0.9167     0.0281  5
  best valid F1               0.8662      0.8776     0.0390  5
  test BA                     0.8853      0.8802     0.0433  5
  test AUC                    0.9552      0.9670     0.0269  5
  test AUC in-protein         0.9493      0.9486     0.0157  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9483      0.9513     0.0188  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8433      0.8421     0.0576  5
  test sensitivity            0.8681      0.8571     0.0586  5
  test specificity            0.9025      0.9271     0.0569  5
  test precision              0.8235      0.8478     0.0798  5
  test loss                   0.2973      0.2340     0.1162  5
  FPR (FP/(FP+TN))            0.0975      0.0729     0.0569  5
  FNR (FN/(FN+TP))            0.1319      0.1429     0.0586  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_doubleattn --seeds=0,1,2,3,4`
