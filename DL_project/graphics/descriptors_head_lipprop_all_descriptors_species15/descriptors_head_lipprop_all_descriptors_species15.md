# descriptors_head_lipprop_all_descriptors_species15

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_head_lipprop_all_descriptors_species15'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.4594      0.5582      0.6031      0.4870      0.7442      0.5068
ALL                 5      0.4594      0.5582      0.6031      0.4870      0.7442      0.5068

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6017      0.5830     0.0670  5
max valid BA                0.6255      0.6214     0.0577  5
best valid F1               0.3887      0.3724     0.0458  5
test BA                     0.5088      0.5069     0.0984  5
test AUC                    0.5031      0.5178     0.1090  5
test AUC in-protein         0.5190      0.5495     0.1374  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.5188      0.5579     0.1094  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.2688      0.2842     0.0918  5
test sensitivity            0.4594      0.5208     0.1762  5
test specificity            0.5582      0.5434     0.0692  5
test precision              0.1910      0.1940     0.0638  5
test loss                   0.7246      0.6866     0.1052  5
FPR (FP/(FP+TN))            0.4418      0.4566     0.0692  5
FNR (FN/(FN+TP))            0.5406      0.4792     0.1762  5

=== abs(sensitivity-specificity) gap: mean=0.1670 median=0.1276 n=5 ===
sensitivity std across seeds (by group): mean=0.1762 median=0.1762 n=1
specificity std across seeds (by group): mean=0.0692 median=0.0692 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6017      0.5830     0.0670  5
  max valid BA                0.6255      0.6214     0.0577  5
  best valid F1               0.3887      0.3724     0.0458  5
  test BA                     0.5088      0.5069     0.0984  5
  test AUC                    0.5031      0.5178     0.1090  5
  test AUC in-protein         0.5190      0.5495     0.1374  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.5188      0.5579     0.1094  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.2688      0.2842     0.0918  5
  test sensitivity            0.4594      0.5208     0.1762  5
  test specificity            0.5582      0.5434     0.0692  5
  test precision              0.1910      0.1940     0.0638  5
  test loss                   0.7246      0.6866     0.1052  5
  FPR (FP/(FP+TN))            0.4418      0.4566     0.0692  5
  FNR (FN/(FN+TP))            0.5406      0.4792     0.1762  5
```

## AUC vs chemistry null model, in-sample increment

