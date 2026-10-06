# mlp_s15_nomb_hid64_pu01

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid64_pu01'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8432      0.8504      0.9065      0.8595      0.9218      0.8508
ALL                 5      0.8432      0.8504      0.9065      0.8595      0.9218      0.8508

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8687      0.8836     0.0428  5
max valid BA                0.8863      0.8988     0.0344  5
best valid F1               0.8353      0.8627     0.0517  5
test BA                     0.8468      0.8516     0.0379  5
test AUC                    0.9295      0.9371     0.0362  5
test AUC in-protein         0.9253      0.9193     0.0395  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9307      0.9370     0.0343  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7888      0.8000     0.0466  5
test sensitivity            0.8432      0.8367     0.0738  5
test specificity            0.8504      0.8737     0.0669  5
test precision              0.7477      0.7857     0.0766  5
test loss                   0.2929      0.2772     0.0880  5
FPR (FP/(FP+TN))            0.1496      0.1263     0.0669  5
FNR (FN/(FN+TP))            0.1568      0.1633     0.0738  5

=== abs(sensitivity-specificity) gap: mean=0.0998 median=0.1042 n=5 ===
sensitivity std across seeds (by group): mean=0.0738 median=0.0738 n=1
specificity std across seeds (by group): mean=0.0669 median=0.0669 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8687      0.8836     0.0428  5
  max valid BA                0.8863      0.8988     0.0344  5
  best valid F1               0.8353      0.8627     0.0517  5
  test BA                     0.8468      0.8516     0.0379  5
  test AUC                    0.9295      0.9371     0.0362  5
  test AUC in-protein         0.9253      0.9193     0.0395  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9307      0.9370     0.0343  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7888      0.8000     0.0466  5
  test sensitivity            0.8432      0.8367     0.0738  5
  test specificity            0.8504      0.8737     0.0669  5
  test precision              0.7477      0.7857     0.0766  5
  test loss                   0.2929      0.2772     0.0880  5
  FPR (FP/(FP+TN))            0.1496      0.1263     0.0669  5
  FNR (FN/(FN+TP))            0.1568      0.1633     0.0738  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid64_pu01 --seeds=0,1,2,3,4`
