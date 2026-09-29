# mlp_s15_mbw_hid32

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_mbw_hid32'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8022      0.8615      0.8532      0.8381      0.8928      0.8802
ALL                 5      0.8022      0.8615      0.8532      0.8381      0.8928      0.8802

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8725      0.8814     0.0231  5
max valid BA                0.8865      0.8908     0.0199  5
best valid F1               0.7428      0.7500     0.0316  5
test BA                     0.8319      0.8271     0.0495  5
test AUC                    0.9151      0.9130     0.0409  5
test AUC in-protein         0.8997      0.8990     0.0531  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.9059      0.9029     0.0472  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.6673      0.6667     0.0705  5
test sensitivity            0.8022      0.7755     0.0904  5
test specificity            0.8615      0.8531     0.0392  5
test precision              0.5749      0.5309     0.0776  5
test loss                   0.3219      0.3466     0.0670  5
FPR (FP/(FP+TN))            0.1385      0.1469     0.0392  5
FNR (FN/(FN+TP))            0.1978      0.2245     0.0904  5

=== abs(sensitivity-specificity) gap: mean=0.0871 median=0.0693 n=5 ===
sensitivity std across seeds (by group): mean=0.0904 median=0.0904 n=1
specificity std across seeds (by group): mean=0.0392 median=0.0392 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8725      0.8814     0.0231  5
  max valid BA                0.8865      0.8908     0.0199  5
  best valid F1               0.7428      0.7500     0.0316  5
  test BA                     0.8319      0.8271     0.0495  5
  test AUC                    0.9151      0.9130     0.0409  5
  test AUC in-protein         0.8997      0.8990     0.0531  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.9059      0.9029     0.0472  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.6673      0.6667     0.0705  5
  test sensitivity            0.8022      0.7755     0.0904  5
  test specificity            0.8615      0.8531     0.0392  5
  test precision              0.5749      0.5309     0.0776  5
  test loss                   0.3219      0.3466     0.0670  5
  FPR (FP/(FP+TN))            0.1385      0.1469     0.0392  5
  FNR (FN/(FN+TP))            0.1978      0.2245     0.0904  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_mbw_hid32 --seeds=0,1,2,3,4`
