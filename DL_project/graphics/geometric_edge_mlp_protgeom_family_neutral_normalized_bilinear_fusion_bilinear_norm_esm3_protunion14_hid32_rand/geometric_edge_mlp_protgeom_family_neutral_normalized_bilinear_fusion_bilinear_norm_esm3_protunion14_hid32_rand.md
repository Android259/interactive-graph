# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_esm3_protunion14_hid32_rand

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_esm3_protunion14_hid32_rand'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
random    5      0.9121      0.8478      0.9400      0.8716      0.9602      0.8435
ALL       5      0.9121      0.8478      0.9400      0.8716      0.9602      0.8435

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8945      0.8906     0.0286  5
max valid BA                0.9019      0.8906     0.0297  5
best valid F1               0.8384      0.8269     0.0455  5
test BA                     0.8800      0.8790     0.0238  5
test AUC                    0.9324      0.9314     0.0192  5
test AUC in-protein         0.8948      0.9273     0.0595  5
  (proteins averaged)       9.2000      9.0000     1.7889  5
test AUC in-protein (pairs)      0.9251      0.9267     0.0253  5
  (proteins contributing)     16.2000     16.0000     1.3038  5
test F1                     0.8145      0.8119     0.0203  5
test sensitivity            0.9121      0.9111     0.0597  5
test specificity            0.8478      0.8454     0.0200  5
test precision              0.7373      0.7321     0.0114  5
test loss                   0.3399      0.3359     0.0550  5
FPR (FP/(FP+TN))            0.1522      0.1546     0.0200  5
FNR (FN/(FN+TP))            0.0879      0.0889     0.0597  5

=== abs(sensitivity-specificity) gap: mean=0.0721 median=0.0642 n=5 ===
sensitivity std across seeds (by group): mean=0.0597 median=0.0597 n=1
specificity std across seeds (by group): mean=0.0200 median=0.0200 n=1

=== By group ===
random (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8945      0.8906     0.0286  5
  max valid BA                0.9019      0.8906     0.0297  5
  best valid F1               0.8384      0.8269     0.0455  5
  test BA                     0.8800      0.8790     0.0238  5
  test AUC                    0.9324      0.9314     0.0192  5
  test AUC in-protein         0.8948      0.9273     0.0595  5
    (proteins averaged)       9.2000      9.0000     1.7889  5
  test AUC in-protein (pairs)      0.9251      0.9267     0.0253  5
    (proteins contributing)     16.2000     16.0000     1.3038  5
  test F1                     0.8145      0.8119     0.0203  5
  test sensitivity            0.9121      0.9111     0.0597  5
  test specificity            0.8478      0.8454     0.0200  5
  test precision              0.7373      0.7321     0.0114  5
  test loss                   0.3399      0.3359     0.0550  5
  FPR (FP/(FP+TN))            0.1522      0.1546     0.0200  5
  FNR (FN/(FN+TP))            0.0879      0.0889     0.0597  5
```

## AUC vs chemistry null model, in-sample increment

Failed: ValueError: Unknown parameter: --random_split -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_esm3_protunion14_hid32_rand --seeds=0,1,2,3,4`
