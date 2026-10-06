# mlp_s15_nomb_hid64_gelu

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid64_gelu'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.7852      0.7592      0.8730      0.6871      0.8887      0.7513
ALL                 5      0.7852      0.7592      0.8730      0.6871      0.8887      0.7513

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8056      0.7969     0.0529  5
max valid BA                0.8200      0.8021     0.0551  5
best valid F1               0.7493      0.7288     0.0672  5
test BA                     0.7722      0.7552     0.0642  5
test AUC                    0.8636      0.8647     0.0672  5
test AUC in-protein         0.8500      0.8561     0.0873  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.8681      0.8608     0.0523  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.6944      0.6731     0.0736  5
test sensitivity            0.7852      0.7755     0.0900  5
test specificity            0.7592      0.7812     0.0703  5
test precision              0.6248      0.6250     0.0726  5
test loss                   0.4397      0.4429     0.0848  5
FPR (FP/(FP+TN))            0.2408      0.2188     0.0703  5
FNR (FN/(FN+TP))            0.2148      0.2245     0.0900  5

=== abs(sensitivity-specificity) gap: mean=0.0802 median=0.0833 n=5 ===
sensitivity std across seeds (by group): mean=0.0900 median=0.0900 n=1
specificity std across seeds (by group): mean=0.0703 median=0.0703 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8056      0.7969     0.0529  5
  max valid BA                0.8200      0.8021     0.0551  5
  best valid F1               0.7493      0.7288     0.0672  5
  test BA                     0.7722      0.7552     0.0642  5
  test AUC                    0.8636      0.8647     0.0672  5
  test AUC in-protein         0.8500      0.8561     0.0873  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.8681      0.8608     0.0523  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.6944      0.6731     0.0736  5
  test sensitivity            0.7852      0.7755     0.0900  5
  test specificity            0.7592      0.7812     0.0703  5
  test precision              0.6248      0.6250     0.0726  5
  test loss                   0.4397      0.4429     0.0848  5
  FPR (FP/(FP+TN))            0.2408      0.2188     0.0703  5
  FNR (FN/(FN+TP))            0.2148      0.2245     0.0900  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid64_gelu --seeds=0,1,2,3,4`
