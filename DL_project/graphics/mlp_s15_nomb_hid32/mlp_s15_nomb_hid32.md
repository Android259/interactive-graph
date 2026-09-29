# mlp_s15_nomb_hid32

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid32'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8601      0.8486      0.9211      0.8343      0.9178      0.8632
ALL                 5      0.8601      0.8486      0.9211      0.8343      0.9178      0.8632

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8812      0.8698     0.0333  5
max valid BA                0.8905      0.8802     0.0377  5
best valid F1               0.8420      0.8148     0.0572  5
test BA                     0.8544      0.8958     0.0716  5
test AUC                    0.9310      0.9460     0.0435  5
test AUC in-protein         0.9297      0.9469     0.0379  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9324      0.9286     0.0417  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7985      0.8544     0.0894  5
test sensitivity            0.8601      0.8750     0.0748  5
test specificity            0.8486      0.8842     0.0732  5
test precision              0.7465      0.8000     0.1027  5
test loss                   0.3149      0.2819     0.0926  5
FPR (FP/(FP+TN))            0.1514      0.1158     0.0732  5
FNR (FN/(FN+TP))            0.1399      0.1250     0.0748  5

=== abs(sensitivity-specificity) gap: mean=0.0316 median=0.0325 n=5 ===
sensitivity std across seeds (by group): mean=0.0748 median=0.0748 n=1
specificity std across seeds (by group): mean=0.0732 median=0.0732 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8812      0.8698     0.0333  5
  max valid BA                0.8905      0.8802     0.0377  5
  best valid F1               0.8420      0.8148     0.0572  5
  test BA                     0.8544      0.8958     0.0716  5
  test AUC                    0.9310      0.9460     0.0435  5
  test AUC in-protein         0.9297      0.9469     0.0379  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9324      0.9286     0.0417  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7985      0.8544     0.0894  5
  test sensitivity            0.8601      0.8750     0.0748  5
  test specificity            0.8486      0.8842     0.0732  5
  test precision              0.7465      0.8000     0.1027  5
  test loss                   0.3149      0.2819     0.0926  5
  FPR (FP/(FP+TN))            0.1514      0.1158     0.0732  5
  FNR (FN/(FN+TP))            0.1399      0.1250     0.0748  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid32 --seeds=0,1,2,3,4`
