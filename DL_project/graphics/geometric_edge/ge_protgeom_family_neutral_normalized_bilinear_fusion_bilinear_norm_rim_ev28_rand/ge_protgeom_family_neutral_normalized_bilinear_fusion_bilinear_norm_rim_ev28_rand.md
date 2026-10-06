# ge_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28_rand

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28_rand'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
random    5      0.6345      0.6568      0.6435      0.6681      0.6356      0.7146
ALL       5      0.6345      0.6568      0.6435      0.6681      0.6356      0.7146

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6528      0.6342     0.0892  5
max valid BA                0.6751      0.6508     0.0950  5
best valid F1               0.5671      0.5455     0.1063  5
test BA                     0.6456      0.6232     0.0401  5
test AUC                    0.6812      0.6653     0.0469  5
test AUC in-protein         0.6325      0.6472     0.0440  5
  (proteins averaged)       9.2000      9.0000     1.7889  5
test AUC in-protein (pairs)      0.7124      0.7331     0.0530  5
  (proteins contributing)     16.2000     16.0000     1.3038  5
test F1                     0.5354      0.5185     0.0428  5
test sensitivity            0.6345      0.6279     0.0650  5
test specificity            0.6568      0.6495     0.0564  5
test precision              0.4647      0.4667     0.0412  5
test loss                   0.6409      0.6529     0.0262  5
FPR (FP/(FP+TN))            0.3432      0.3505     0.0564  5
FNR (FN/(FN+TP))            0.3655      0.3721     0.0650  5

=== abs(sensitivity-specificity) gap: mean=0.0832 median=0.0798 n=5 ===
sensitivity std across seeds (by group): mean=0.0650 median=0.0650 n=1
specificity std across seeds (by group): mean=0.0564 median=0.0564 n=1

=== By group ===
random (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6528      0.6342     0.0892  5
  max valid BA                0.6751      0.6508     0.0950  5
  best valid F1               0.5671      0.5455     0.1063  5
  test BA                     0.6456      0.6232     0.0401  5
  test AUC                    0.6812      0.6653     0.0469  5
  test AUC in-protein         0.6325      0.6472     0.0440  5
    (proteins averaged)       9.2000      9.0000     1.7889  5
  test AUC in-protein (pairs)      0.7124      0.7331     0.0530  5
    (proteins contributing)     16.2000     16.0000     1.3038  5
  test F1                     0.5354      0.5185     0.0428  5
  test sensitivity            0.6345      0.6279     0.0650  5
  test specificity            0.6568      0.6495     0.0564  5
  test precision              0.4647      0.4667     0.0412  5
  test loss                   0.6409      0.6529     0.0262  5
  FPR (FP/(FP+TN))            0.3432      0.3505     0.0564  5
  FNR (FN/(FN+TP))            0.3655      0.3721     0.0650  5
```

## AUC vs chemistry null model, in-sample increment

(skipped: SKIP_AUC=1 -- rerun without it to fill this in: `python3 analysis/full_label_report.py --label ge_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28_rand --seeds=0,1,2,3,4`)
