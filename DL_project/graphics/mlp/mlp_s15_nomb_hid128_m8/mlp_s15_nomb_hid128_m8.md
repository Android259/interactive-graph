# mlp_s15_nomb_hid128_m8

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid128_m8'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8599      0.8796      0.9457      0.8788      0.9468      0.8549
ALL                 5      0.8599      0.8796      0.9457      0.8788      0.9468      0.8549

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8728      0.8854     0.0418  5
max valid BA                0.9009      0.9062     0.0352  5
best valid F1               0.8509      0.8544     0.0520  5
test BA                     0.8698      0.8566     0.0535  5
test AUC                    0.9382      0.9400     0.0352  5
test AUC in-protein         0.9425      0.9490     0.0264  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9416      0.9542     0.0283  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8203      0.8081     0.0685  5
test sensitivity            0.8599      0.8333     0.0631  5
test specificity            0.8796      0.8969     0.0509  5
test precision              0.7851      0.8000     0.0770  5
test loss                   0.2945      0.2962     0.0829  5
FPR (FP/(FP+TN))            0.1204      0.1031     0.0509  5
FNR (FN/(FN+TP))            0.1401      0.1667     0.0631  5

=== abs(sensitivity-specificity) gap: mean=0.0292 median=0.0217 n=5 ===
sensitivity std across seeds (by group): mean=0.0631 median=0.0631 n=1
specificity std across seeds (by group): mean=0.0509 median=0.0509 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8728      0.8854     0.0418  5
  max valid BA                0.9009      0.9062     0.0352  5
  best valid F1               0.8509      0.8544     0.0520  5
  test BA                     0.8698      0.8566     0.0535  5
  test AUC                    0.9382      0.9400     0.0352  5
  test AUC in-protein         0.9425      0.9490     0.0264  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9416      0.9542     0.0283  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8203      0.8081     0.0685  5
  test sensitivity            0.8599      0.8333     0.0631  5
  test specificity            0.8796      0.8969     0.0509  5
  test precision              0.7851      0.8000     0.0770  5
  test loss                   0.2945      0.2962     0.0829  5
  FPR (FP/(FP+TN))            0.1204      0.1031     0.0509  5
  FNR (FN/(FN+TP))            0.1401      0.1667     0.0631  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid128_m8 --seeds=0,1,2,3,4`
