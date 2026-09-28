# deepclip_gltp_protein_gate_ep120

## Summary (analysis/summarize_label.py)

```
Summary: 'deepclip_gltp_protein_gate_ep120'
rows: 10

=== Sensitivity / specificity by group (test / train / valid) ===
group          n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_gltp   10      0.8067      0.8025      0.7448      0.6727      0.8633      0.7528
ALL           10      0.8067      0.8025      0.7448      0.6727      0.8633      0.7528

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.7884      0.8646     0.1583  10
max valid BA                0.8081      0.8646     0.1444  10
best valid F1               0.7043      0.8000     0.2267  10
test BA                     0.8046      0.7903     0.0894  10
test AUC                    0.8467      0.8944     0.1359  10
test AUC in-protein         0.8919      0.9012     0.1094  10
  (proteins averaged)       1.3000      1.0000     0.4830  10
test AUC in-protein (pairs)      0.8883      0.9125     0.1055  10
  (proteins contributing)      1.8000      2.0000     0.4216  10
test F1                     0.7187      0.7386     0.1230  10
test sensitivity            0.8067      0.7750     0.1495  10
test specificity            0.8025      0.8535     0.1620  10
test precision              0.6781      0.6905     0.1786  10
test loss                   0.5550      0.6128     0.1546  10
FPR (FP/(FP+TN))            0.1975      0.1465     0.1620  10
FNR (FN/(FN+TP))            0.1933      0.2250     0.1495  10

=== abs(sensitivity-specificity) gap: mean=0.1905 median=0.1659 n=10 ===
sensitivity std across seeds (by group): mean=0.1495 median=0.1495 n=1
specificity std across seeds (by group): mean=0.1620 median=0.1620 n=1

=== By group ===
groups_gltp (n=10):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7884      0.8646     0.1583  10
  max valid BA                0.8081      0.8646     0.1444  10
  best valid F1               0.7043      0.8000     0.2267  10
  test BA                     0.8046      0.7903     0.0894  10
  test AUC                    0.8467      0.8944     0.1359  10
  test AUC in-protein         0.8919      0.9012     0.1094  10
    (proteins averaged)       1.3000      1.0000     0.4830  10
  test AUC in-protein (pairs)      0.8883      0.9125     0.1055  10
    (proteins contributing)      1.8000      2.0000     0.4216  10
  test F1                     0.7187      0.7386     0.1230  10
  test sensitivity            0.8067      0.7750     0.1495  10
  test specificity            0.8025      0.8535     0.1620  10
  test precision              0.6781      0.6905     0.1786  10
  test loss                   0.5550      0.6128     0.1546  10
  FPR (FP/(FP+TN))            0.1975      0.1465     0.1620  10
  FNR (FN/(FN+TP))            0.1933      0.2250     0.1495  10
```

## AUC vs chemistry null model, in-sample increment

Failed: gltp/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label deepclip_gltp_protein_gate_ep120 --seeds=0,1,2,3,4,5,6,7,8,9`
