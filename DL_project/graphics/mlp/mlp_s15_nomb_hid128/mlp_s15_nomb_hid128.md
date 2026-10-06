# mlp_s15_nomb_hid128

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid128'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8844      0.8526      0.9322      0.8619      0.9385      0.8487
ALL                 5      0.8844      0.8526      0.9322      0.8619      0.9385      0.8487

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8771      0.8854     0.0499  5
max valid BA                0.8936      0.8958     0.0400  5
best valid F1               0.8438      0.8462     0.0586  5
test BA                     0.8685      0.8771     0.0438  5
test AUC                    0.9365      0.9506     0.0403  5
test AUC in-protein         0.9441      0.9475     0.0272  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9460      0.9536     0.0257  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8157      0.8367     0.0576  5
test sensitivity            0.8844      0.8750     0.0472  5
test specificity            0.8526      0.8737     0.0875  5
test precision              0.7631      0.7931     0.0945  5
test loss                   0.3075      0.2681     0.1022  5
FPR (FP/(FP+TN))            0.1474      0.1263     0.0875  5
FNR (FN/(FN+TP))            0.1156      0.1250     0.0472  5

=== abs(sensitivity-specificity) gap: mean=0.0808 median=0.0808 n=5 ===
sensitivity std across seeds (by group): mean=0.0472 median=0.0472 n=1
specificity std across seeds (by group): mean=0.0875 median=0.0875 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8771      0.8854     0.0499  5
  max valid BA                0.8936      0.8958     0.0400  5
  best valid F1               0.8438      0.8462     0.0586  5
  test BA                     0.8685      0.8771     0.0438  5
  test AUC                    0.9365      0.9506     0.0403  5
  test AUC in-protein         0.9441      0.9475     0.0272  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9460      0.9536     0.0257  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8157      0.8367     0.0576  5
  test sensitivity            0.8844      0.8750     0.0472  5
  test specificity            0.8526      0.8737     0.0875  5
  test precision              0.7631      0.7931     0.0945  5
  test loss                   0.3075      0.2681     0.1022  5
  FPR (FP/(FP+TN))            0.1474      0.1263     0.0875  5
  FNR (FN/(FN+TP))            0.1156      0.1250     0.0472  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid128 --seeds=0,1,2,3,4`
