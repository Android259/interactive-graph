# mlp_s15_nomb_hid32_m8

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid32_m8'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8679      0.8485      0.9311      0.8513      0.9137      0.8695
ALL                 5      0.8679      0.8485      0.9311      0.8513      0.9137      0.8695

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8842      0.8854     0.0380  5
max valid BA                0.8916      0.8854     0.0403  5
best valid F1               0.8429      0.8350     0.0569  5
test BA                     0.8582      0.8665     0.0511  5
test AUC                    0.9313      0.9405     0.0426  5
test AUC in-protein         0.9391      0.9449     0.0396  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9345      0.9570     0.0443  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8028      0.8073     0.0654  5
test sensitivity            0.8679      0.8958     0.0495  5
test specificity            0.8485      0.8632     0.0722  5
test precision              0.7501      0.7719     0.0898  5
test loss                   0.3147      0.2987     0.0907  5
FPR (FP/(FP+TN))            0.1515      0.1368     0.0722  5
FNR (FN/(FN+TP))            0.1321      0.1042     0.0495  5

=== abs(sensitivity-specificity) gap: mean=0.0610 median=0.0629 n=5 ===
sensitivity std across seeds (by group): mean=0.0495 median=0.0495 n=1
specificity std across seeds (by group): mean=0.0722 median=0.0722 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8842      0.8854     0.0380  5
  max valid BA                0.8916      0.8854     0.0403  5
  best valid F1               0.8429      0.8350     0.0569  5
  test BA                     0.8582      0.8665     0.0511  5
  test AUC                    0.9313      0.9405     0.0426  5
  test AUC in-protein         0.9391      0.9449     0.0396  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9345      0.9570     0.0443  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8028      0.8073     0.0654  5
  test sensitivity            0.8679      0.8958     0.0495  5
  test specificity            0.8485      0.8632     0.0722  5
  test precision              0.7501      0.7719     0.0898  5
  test loss                   0.3147      0.2987     0.0907  5
  FPR (FP/(FP+TN))            0.1515      0.1368     0.0722  5
  FNR (FN/(FN+TP))            0.1321      0.1042     0.0495  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid32_m8 --seeds=0,1,2,3,4`
