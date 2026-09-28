# descriptors_head_family_neutral_lipprop_rand

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_head_family_neutral_lipprop_rand'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
random    5      0.6599      0.4379      0.7129      0.3953      0.7397      0.4489
ALL       5      0.6599      0.4379      0.7129      0.3953      0.7397      0.4489

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5774      0.5902     0.0404  5
max valid BA                0.5943      0.6067     0.0400  5
best valid F1               0.5109      0.5036     0.0246  5
test BA                     0.5489      0.5795     0.0671  5
test AUC                    0.5389      0.5509     0.0935  5
test AUC in-protein         0.5661      0.5718     0.0457  5
  (proteins averaged)       9.2000      9.0000     1.7889  5
test AUC in-protein (pairs)      0.5919      0.6254     0.0710  5
  (proteins contributing)     16.2000     16.0000     1.3038  5
test F1                     0.4581      0.4737     0.0824  5
test sensitivity            0.6599      0.6739     0.1734  5
test specificity            0.4379      0.5300     0.1490  5
test precision              0.3549      0.3805     0.0587  5
test loss                   0.6811      0.6874     0.0263  5
FPR (FP/(FP+TN))            0.5621      0.4700     0.1490  5
FNR (FN/(FN+TP))            0.3401      0.3261     0.1734  5

=== abs(sensitivity-specificity) gap: mean=0.2666 median=0.1750 n=5 ===
sensitivity std across seeds (by group): mean=0.1734 median=0.1734 n=1
specificity std across seeds (by group): mean=0.1490 median=0.1490 n=1

=== By group ===
random (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5774      0.5902     0.0404  5
  max valid BA                0.5943      0.6067     0.0400  5
  best valid F1               0.5109      0.5036     0.0246  5
  test BA                     0.5489      0.5795     0.0671  5
  test AUC                    0.5389      0.5509     0.0935  5
  test AUC in-protein         0.5661      0.5718     0.0457  5
    (proteins averaged)       9.2000      9.0000     1.7889  5
  test AUC in-protein (pairs)      0.5919      0.6254     0.0710  5
    (proteins contributing)     16.2000     16.0000     1.3038  5
  test F1                     0.4581      0.4737     0.0824  5
  test sensitivity            0.6599      0.6739     0.1734  5
  test specificity            0.4379      0.5300     0.1490  5
  test precision              0.3549      0.3805     0.0587  5
  test loss                   0.6811      0.6874     0.0263  5
  FPR (FP/(FP+TN))            0.5621      0.4700     0.1490  5
  FNR (FN/(FN+TP))            0.3401      0.3261     0.1734  5
```

## AUC vs chemistry null model, in-sample increment

(skipped: SKIP_AUC=1 -- rerun without it to fill this in: `python3 analysis/full_label_report.py --label descriptors_head_family_neutral_lipprop_rand --seeds=0,1,2,3,4`)
