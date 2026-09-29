# ge_s15_prothid32_mbw

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_prothid32_mbw'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8972      0.6962      0.9113      0.6674      0.9138      0.6839
ALL                 5      0.8972      0.6962      0.9113      0.6674      0.9138      0.6839

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.7824      0.8485     0.1594  5
max valid BA                0.7989      0.8685     0.1691  5
best valid F1               0.7543      0.8214     0.1456  5
test BA                     0.7967      0.8567     0.1677  5
test AUC                    0.8467      0.9236     0.1766  5
test AUC in-protein         0.8347      0.9228     0.1994  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.8395      0.8942     0.1733  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7550      0.8125     0.1457  5
test sensitivity            0.8972      0.8776     0.0764  5
test specificity            0.6962      0.8646     0.3909  5
test precision              0.6870      0.7636     0.2033  5
test loss                   0.4318      0.3267     0.2313  5
FPR (FP/(FP+TN))            0.3038      0.1354     0.3909  5
FNR (FN/(FN+TP))            0.1028      0.1224     0.0764  5

=== abs(sensitivity-specificity) gap: mean=0.2497 median=0.0631 n=5 ===
sensitivity std across seeds (by group): mean=0.0764 median=0.0764 n=1
specificity std across seeds (by group): mean=0.3909 median=0.3909 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7824      0.8485     0.1594  5
  max valid BA                0.7989      0.8685     0.1691  5
  best valid F1               0.7543      0.8214     0.1456  5
  test BA                     0.7967      0.8567     0.1677  5
  test AUC                    0.8467      0.9236     0.1766  5
  test AUC in-protein         0.8347      0.9228     0.1994  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.8395      0.8942     0.1733  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7550      0.8125     0.1457  5
  test sensitivity            0.8972      0.8776     0.0764  5
  test specificity            0.6962      0.8646     0.3909  5
  test precision              0.6870      0.7636     0.2033  5
  test loss                   0.4318      0.3267     0.2313  5
  FPR (FP/(FP+TN))            0.3038      0.1354     0.3909  5
  FNR (FN/(FN+TP))            0.1028      0.1224     0.0764  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_mbw --seeds=0,1,2,3,4`
