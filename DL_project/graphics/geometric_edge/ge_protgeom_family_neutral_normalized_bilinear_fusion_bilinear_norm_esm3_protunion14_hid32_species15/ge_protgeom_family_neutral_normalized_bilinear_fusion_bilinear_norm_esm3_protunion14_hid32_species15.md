# ge_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_esm3_protunion14_hid32_species15

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_esm3_protunion14_hid32_species15'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8842      0.8696      0.9418      0.8482      0.9427      0.8737
ALL                 5      0.8842      0.8696      0.9418      0.8482      0.9427      0.8737

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.9011      0.8970     0.0192  5
max valid BA                0.9082      0.8989     0.0257  5
best valid F1               0.7685      0.7664     0.0209  5
test BA                     0.8769      0.8796     0.0361  5
test AUC                    0.9396      0.9357     0.0265  5
test AUC in-protein         0.9335      0.9286     0.0259  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.9377      0.9348     0.0153  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.7207      0.7213     0.0487  5
test sensitivity            0.8842      0.8980     0.0687  5
test specificity            0.8696      0.8721     0.0221  5
test precision              0.6091      0.6027     0.0445  5
test loss                   0.2826      0.2927     0.0564  5
FPR (FP/(FP+TN))            0.1304      0.1279     0.0221  5
FNR (FN/(FN+TP))            0.1158      0.1020     0.0687  5

=== abs(sensitivity-specificity) gap: mean=0.0566 median=0.0591 n=5 ===
sensitivity std across seeds (by group): mean=0.0687 median=0.0687 n=1
specificity std across seeds (by group): mean=0.0221 median=0.0221 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9011      0.8970     0.0192  5
  max valid BA                0.9082      0.8989     0.0257  5
  best valid F1               0.7685      0.7664     0.0209  5
  test BA                     0.8769      0.8796     0.0361  5
  test AUC                    0.9396      0.9357     0.0265  5
  test AUC in-protein         0.9335      0.9286     0.0259  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.9377      0.9348     0.0153  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.7207      0.7213     0.0487  5
  test sensitivity            0.8842      0.8980     0.0687  5
  test specificity            0.8696      0.8721     0.0221  5
  test precision              0.6091      0.6027     0.0445  5
  test loss                   0.2826      0.2927     0.0564  5
  FPR (FP/(FP+TN))            0.1304      0.1279     0.0221  5
  FNR (FN/(FN+TP))            0.1158      0.1020     0.0687  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_esm3_protunion14_hid32_species15 --seeds=0,1,2,3,4`
