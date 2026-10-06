# mlp_s15_mbw_hid16

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_mbw_hid16'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.7649      0.8420      0.8129      0.8067      0.8803      0.8407
ALL                 5      0.7649      0.8420      0.8129      0.8067      0.8803      0.8407

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8519      0.8449     0.0246  5
max valid BA                0.8605      0.8540     0.0252  5
best valid F1               0.6947      0.6972     0.0321  5
test BA                     0.8034      0.7879     0.0618  5
test AUC                    0.8856      0.8873     0.0420  5
test AUC in-protein         0.8754      0.8729     0.0519  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.8802      0.8828     0.0516  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.6265      0.5821     0.0987  5
test sensitivity            0.7649      0.7708     0.0961  5
test specificity            0.8420      0.8389     0.0565  5
test precision              0.5350      0.4769     0.1089  5
test loss                   0.3783      0.4116     0.0683  5
FPR (FP/(FP+TN))            0.1580      0.1611     0.0565  5
FNR (FN/(FN+TP))            0.2351      0.2292     0.0961  5

=== abs(sensitivity-specificity) gap: mean=0.0835 median=0.0237 n=5 ===
sensitivity std across seeds (by group): mean=0.0961 median=0.0961 n=1
specificity std across seeds (by group): mean=0.0565 median=0.0565 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8519      0.8449     0.0246  5
  max valid BA                0.8605      0.8540     0.0252  5
  best valid F1               0.6947      0.6972     0.0321  5
  test BA                     0.8034      0.7879     0.0618  5
  test AUC                    0.8856      0.8873     0.0420  5
  test AUC in-protein         0.8754      0.8729     0.0519  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.8802      0.8828     0.0516  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.6265      0.5821     0.0987  5
  test sensitivity            0.7649      0.7708     0.0961  5
  test specificity            0.8420      0.8389     0.0565  5
  test precision              0.5350      0.4769     0.1089  5
  test loss                   0.3783      0.4116     0.0683  5
  FPR (FP/(FP+TN))            0.1580      0.1611     0.0565  5
  FNR (FN/(FN+TP))            0.2351      0.2292     0.0961  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_mbw_hid16 --seeds=0,1,2,3,4`
