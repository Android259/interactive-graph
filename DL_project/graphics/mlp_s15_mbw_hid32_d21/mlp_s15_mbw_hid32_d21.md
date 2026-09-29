# mlp_s15_mbw_hid32_d21

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_mbw_hid32_d21'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.7356      0.8012      0.7833      0.7647      0.7973      0.7701
ALL                 5      0.7356      0.8012      0.7833      0.7647      0.7973      0.7701

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.7721      0.7452     0.0475  5
max valid BA                0.7837      0.7712     0.0438  5
best valid F1               0.5790      0.5505     0.0504  5
test BA                     0.7684      0.7699     0.0495  5
test AUC                    0.8478      0.8652     0.0438  5
test AUC in-protein         0.8389      0.8631     0.0486  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.8516      0.8671     0.0452  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.5716      0.5649     0.0881  5
test sensitivity            0.7356      0.7500     0.0328  5
test specificity            0.8012      0.7847     0.0720  5
test precision              0.4729      0.4512     0.1095  5
test loss                   0.4336      0.4203     0.0600  5
FPR (FP/(FP+TN))            0.1988      0.2153     0.0720  5
FNR (FN/(FN+TP))            0.2644      0.2500     0.0328  5

=== abs(sensitivity-specificity) gap: mean=0.0676 median=0.0881 n=5 ===
sensitivity std across seeds (by group): mean=0.0328 median=0.0328 n=1
specificity std across seeds (by group): mean=0.0720 median=0.0720 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7721      0.7452     0.0475  5
  max valid BA                0.7837      0.7712     0.0438  5
  best valid F1               0.5790      0.5505     0.0504  5
  test BA                     0.7684      0.7699     0.0495  5
  test AUC                    0.8478      0.8652     0.0438  5
  test AUC in-protein         0.8389      0.8631     0.0486  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.8516      0.8671     0.0452  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.5716      0.5649     0.0881  5
  test sensitivity            0.7356      0.7500     0.0328  5
  test specificity            0.8012      0.7847     0.0720  5
  test precision              0.4729      0.4512     0.1095  5
  test loss                   0.4336      0.4203     0.0600  5
  FPR (FP/(FP+TN))            0.1988      0.2153     0.0720  5
  FNR (FN/(FN+TP))            0.2644      0.2500     0.0328  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_mbw_hid32_d21 --seeds=0,1,2,3,4`
