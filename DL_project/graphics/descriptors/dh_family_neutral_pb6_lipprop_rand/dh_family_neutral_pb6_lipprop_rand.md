# dh_family_neutral_pb6_lipprop_rand

## Summary (analysis/summarize_label.py)

```
Summary: 'dh_family_neutral_pb6_lipprop_rand'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
random    5      0.6109      0.6741      0.5646      0.7006      0.6551      0.6905
ALL       5      0.6109      0.6741      0.5646      0.7006      0.6551      0.6905

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6623      0.6425     0.0476  5
max valid BA                0.6728      0.6425     0.0470  5
best valid F1               0.5855      0.5672     0.0460  5
test BA                     0.6425      0.6311     0.0577  5
test AUC                    0.6950      0.6694     0.0564  5
test AUC in-protein         0.6486      0.6387     0.0805  5
  (proteins averaged)       7.0000      7.0000     1.5811  5
test AUC in-protein (pairs)      0.6372      0.6458     0.0712  5
  (proteins contributing)     17.0000     16.0000     3.0000  5
test F1                     0.5356      0.5357     0.0649  5
test sensitivity            0.6109      0.6250     0.1522  5
test specificity            0.6741      0.6522     0.0821  5
test precision              0.4881      0.4688     0.0366  5
test loss                   0.6445      0.6465     0.0137  5
FPR (FP/(FP+TN))            0.3259      0.3478     0.0821  5
FNR (FN/(FN+TP))            0.3891      0.3750     0.1522  5

=== abs(sensitivity-specificity) gap: mean=0.1680 median=0.1771 n=5 ===
sensitivity std across seeds (by group): mean=0.1522 median=0.1522 n=1
specificity std across seeds (by group): mean=0.0821 median=0.0821 n=1

=== By group ===
random (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6623      0.6425     0.0476  5
  max valid BA                0.6728      0.6425     0.0470  5
  best valid F1               0.5855      0.5672     0.0460  5
  test BA                     0.6425      0.6311     0.0577  5
  test AUC                    0.6950      0.6694     0.0564  5
  test AUC in-protein         0.6486      0.6387     0.0805  5
    (proteins averaged)       7.0000      7.0000     1.5811  5
  test AUC in-protein (pairs)      0.6372      0.6458     0.0712  5
    (proteins contributing)     17.0000     16.0000     3.0000  5
  test F1                     0.5356      0.5357     0.0649  5
  test sensitivity            0.6109      0.6250     0.1522  5
  test specificity            0.6741      0.6522     0.0821  5
  test precision              0.4881      0.4688     0.0366  5
  test loss                   0.6445      0.6465     0.0137  5
  FPR (FP/(FP+TN))            0.3259      0.3478     0.0821  5
  FNR (FN/(FN+TP))            0.3891      0.3750     0.1522  5
```

## AUC vs chemistry null model, in-sample increment

(skipped: SKIP_AUC=1 -- rerun without it to fill this in: `python3 analysis/full_label_report.py --label dh_family_neutral_pb6_lipprop_rand --seeds=0,1,2,3,4`)
