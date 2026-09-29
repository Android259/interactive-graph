# dh_s15_mbw_hid32_d13

## Summary (analysis/summarize_label.py)

```
Summary: 'dh_s15_mbw_hid32_d13'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.5563      0.5047      0.4159      0.6240      0.6108      0.5554
ALL                 5      0.5563      0.5047      0.4159      0.6240      0.6108      0.5554

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5660      0.5681     0.0358  5
max valid BA                0.5831      0.5918     0.0309  5
best valid F1               0.3459      0.3617     0.0303  5
test BA                     0.5305      0.5303     0.0406  5
test AUC                    0.5209      0.5202     0.0777  5
test AUC in-protein         0.5146      0.5120     0.0780  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.5381      0.5408     0.0677  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.2833      0.3059     0.0796  5
test sensitivity            0.5563      0.6250     0.2585  5
test specificity            0.5047      0.4785     0.2511  5
test precision              0.2038      0.2083     0.0247  5
test loss                   0.6906      0.6839     0.0406  5
FPR (FP/(FP+TN))            0.4953      0.5215     0.2511  5
FNR (FN/(FN+TP))            0.4437      0.3750     0.2585  5

=== abs(sensitivity-specificity) gap: mean=0.3585 median=0.2154 n=5 ===
sensitivity std across seeds (by group): mean=0.2585 median=0.2585 n=1
specificity std across seeds (by group): mean=0.2511 median=0.2511 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5660      0.5681     0.0358  5
  max valid BA                0.5831      0.5918     0.0309  5
  best valid F1               0.3459      0.3617     0.0303  5
  test BA                     0.5305      0.5303     0.0406  5
  test AUC                    0.5209      0.5202     0.0777  5
  test AUC in-protein         0.5146      0.5120     0.0780  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.5381      0.5408     0.0677  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.2833      0.3059     0.0796  5
  test sensitivity            0.5563      0.6250     0.2585  5
  test specificity            0.5047      0.4785     0.2511  5
  test precision              0.2038      0.2083     0.0247  5
  test loss                   0.6906      0.6839     0.0406  5
  FPR (FP/(FP+TN))            0.4953      0.5215     0.2511  5
  FNR (FN/(FN+TP))            0.4437      0.3750     0.2585  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label dh_s15_mbw_hid32_d13 --seeds=0,1,2,3,4`
