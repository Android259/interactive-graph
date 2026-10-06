# ge_s15_prothid32_hid64_noreg_forcedint

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32_hid64_noreg_forcedint'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8886      0.8962      0.9434      0.8665      0.9300      0.8963
ALL                 5      0.8886      0.8962      0.9434      0.8665      0.9300      0.8963

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8925      0.8958     0.0361  5
max valid BA                0.9132      0.9271     0.0332  5
best valid F1               0.8729      0.8866     0.0479  5
test BA                     0.8924      0.8771     0.0333  5
test AUC                    0.9504      0.9599     0.0289  5
test AUC in-protein         0.9372      0.9484     0.0276  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9416      0.9427     0.0216  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8494      0.8367     0.0456  5
test sensitivity            0.8886      0.8980     0.0423  5
test specificity            0.8962      0.9158     0.0480  5
test precision              0.8158      0.8367     0.0656  5
test loss                   0.3079      0.2930     0.0940  5
FPR (FP/(FP+TN))            0.1038      0.0842     0.0480  5
FNR (FN/(FN+TP))            0.1114      0.1020     0.0423  5

=== abs(sensitivity-specificity) gap: mean=0.0414 median=0.0417 n=5 ===
sensitivity std across seeds (by group): mean=0.0423 median=0.0423 n=1
specificity std across seeds (by group): mean=0.0480 median=0.0480 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8925      0.8958     0.0361  5
  max valid BA                0.9132      0.9271     0.0332  5
  best valid F1               0.8729      0.8866     0.0479  5
  test BA                     0.8924      0.8771     0.0333  5
  test AUC                    0.9504      0.9599     0.0289  5
  test AUC in-protein         0.9372      0.9484     0.0276  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9416      0.9427     0.0216  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8494      0.8367     0.0456  5
  test sensitivity            0.8886      0.8980     0.0423  5
  test specificity            0.8962      0.9158     0.0480  5
  test precision              0.8158      0.8367     0.0656  5
  test loss                   0.3079      0.2930     0.0940  5
  FPR (FP/(FP+TN))            0.1038      0.0842     0.0480  5
  FNR (FN/(FN+TP))            0.1114      0.1020     0.0423  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_forcedint --seeds=0,1,2,3,4`
