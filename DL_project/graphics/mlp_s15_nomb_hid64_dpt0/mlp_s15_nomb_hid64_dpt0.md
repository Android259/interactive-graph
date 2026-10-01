# mlp_s15_nomb_hid64_dpt0

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid64_dpt0'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8474      0.8670      0.9579      0.8876      0.9098      0.8694
ALL                 5      0.8474      0.8670      0.9579      0.8876      0.9098      0.8694

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8771      0.8739     0.0339  5
max valid BA                0.8896      0.8802     0.0450  5
best valid F1               0.8409      0.8367     0.0598  5
test BA                     0.8572      0.8721     0.0433  5
test AUC                    0.9376      0.9447     0.0368  5
test AUC in-protein         0.9399      0.9517     0.0385  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9370      0.9513     0.0477  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8050      0.8224     0.0575  5
test sensitivity            0.8474      0.8163     0.0467  5
test specificity            0.8670      0.8958     0.0720  5
test precision              0.7715      0.7959     0.0918  5
test loss                   0.3143      0.2878     0.0974  5
FPR (FP/(FP+TN))            0.1330      0.1042     0.0720  5
FNR (FN/(FN+TP))            0.1526      0.1837     0.0467  5

=== abs(sensitivity-specificity) gap: mean=0.0750 median=0.0746 n=5 ===
sensitivity std across seeds (by group): mean=0.0467 median=0.0467 n=1
specificity std across seeds (by group): mean=0.0720 median=0.0720 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8771      0.8739     0.0339  5
  max valid BA                0.8896      0.8802     0.0450  5
  best valid F1               0.8409      0.8367     0.0598  5
  test BA                     0.8572      0.8721     0.0433  5
  test AUC                    0.9376      0.9447     0.0368  5
  test AUC in-protein         0.9399      0.9517     0.0385  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9370      0.9513     0.0477  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8050      0.8224     0.0575  5
  test sensitivity            0.8474      0.8163     0.0467  5
  test specificity            0.8670      0.8958     0.0720  5
  test precision              0.7715      0.7959     0.0918  5
  test loss                   0.3143      0.2878     0.0974  5
  FPR (FP/(FP+TN))            0.1330      0.1042     0.0720  5
  FNR (FN/(FN+TP))            0.1526      0.1837     0.0467  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid64_dpt0 --seeds=0,1,2,3,4`
