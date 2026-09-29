# mlp_s15_mbw_hid32_d14

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_mbw_hid32_d14'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.6192      0.7687      0.6527      0.7559      0.6810      0.7588
ALL                 5      0.6192      0.7687      0.6527      0.7559      0.6810      0.7588

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.7066      0.7191     0.0623  5
max valid BA                0.7199      0.7321     0.0697  5
best valid F1               0.4887      0.5034     0.0868  5
test BA                     0.6940      0.7009     0.0830  5
test AUC                    0.7680      0.7891     0.0973  5
test AUC in-protein         0.7848      0.7654     0.0709  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.7828      0.7840     0.0736  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.4499      0.4776     0.1252  5
test sensitivity            0.6192      0.7347     0.2579  5
test specificity            0.7687      0.7488     0.1193  5
test precision              0.3962      0.3800     0.0576  5
test loss                   0.5411      0.5116     0.0879  5
FPR (FP/(FP+TN))            0.2313      0.2512     0.1193  5
FNR (FN/(FN+TP))            0.3808      0.2653     0.2579  5

=== abs(sensitivity-specificity) gap: mean=0.2207 median=0.0958 n=5 ===
sensitivity std across seeds (by group): mean=0.2579 median=0.2579 n=1
specificity std across seeds (by group): mean=0.1193 median=0.1193 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7066      0.7191     0.0623  5
  max valid BA                0.7199      0.7321     0.0697  5
  best valid F1               0.4887      0.5034     0.0868  5
  test BA                     0.6940      0.7009     0.0830  5
  test AUC                    0.7680      0.7891     0.0973  5
  test AUC in-protein         0.7848      0.7654     0.0709  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.7828      0.7840     0.0736  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.4499      0.4776     0.1252  5
  test sensitivity            0.6192      0.7347     0.2579  5
  test specificity            0.7687      0.7488     0.1193  5
  test precision              0.3962      0.3800     0.0576  5
  test loss                   0.5411      0.5116     0.0879  5
  FPR (FP/(FP+TN))            0.2313      0.2512     0.1193  5
  FNR (FN/(FN+TP))            0.3808      0.2653     0.2579  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_mbw_hid32_d14 --seeds=0,1,2,3,4`
