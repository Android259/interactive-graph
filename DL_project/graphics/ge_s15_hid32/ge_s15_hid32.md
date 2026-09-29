# ge_s15_hid32

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_s15_hid32'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8845      0.8567      0.9330      0.8472      0.9302      0.8797
ALL                 5      0.8845      0.8567      0.9330      0.8472      0.9302      0.8797

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8966      0.8988     0.0274  5
max valid BA                0.9049      0.9062     0.0321  5
best valid F1               0.8604      0.8660     0.0446  5
test BA                     0.8706      0.8750     0.0439  5
test AUC                    0.9375      0.9503     0.0310  5
test AUC in-protein         0.9387      0.9358     0.0223  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9366      0.9364     0.0233  5
  (proteins contributing)     19.0000     19.0000     1.5811  5
test F1                     0.8177      0.8190     0.0595  5
test sensitivity            0.8845      0.8958     0.0301  5
test specificity            0.8567      0.8542     0.0648  5
test precision              0.7628      0.7544     0.0868  5
test loss                   0.3097      0.2813     0.0788  5
FPR (FP/(FP+TN))            0.1433      0.1458     0.0648  5
FNR (FN/(FN+TP))            0.1155      0.1042     0.0301  5

=== abs(sensitivity-specificity) gap: mean=0.0479 median=0.0503 n=5 ===
sensitivity std across seeds (by group): mean=0.0301 median=0.0301 n=1
specificity std across seeds (by group): mean=0.0648 median=0.0648 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8966      0.8988     0.0274  5
  max valid BA                0.9049      0.9062     0.0321  5
  best valid F1               0.8604      0.8660     0.0446  5
  test BA                     0.8706      0.8750     0.0439  5
  test AUC                    0.9375      0.9503     0.0310  5
  test AUC in-protein         0.9387      0.9358     0.0223  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9366      0.9364     0.0233  5
    (proteins contributing)     19.0000     19.0000     1.5811  5
  test F1                     0.8177      0.8190     0.0595  5
  test sensitivity            0.8845      0.8958     0.0301  5
  test specificity            0.8567      0.8542     0.0648  5
  test precision              0.7628      0.7544     0.0868  5
  test loss                   0.3097      0.2813     0.0788  5
  FPR (FP/(FP+TN))            0.1433      0.1458     0.0648  5
  FNR (FN/(FN+TP))            0.1155      0.1042     0.0301  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_hid32 --seeds=0,1,2,3,4`
