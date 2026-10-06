# mlp_s15_mbw_hid32_m8

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_mbw_hid32_m8'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8144      0.8662      0.8570      0.8493      0.9053      0.8747
ALL                 5      0.8144      0.8662      0.8570      0.8493      0.9053      0.8747

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8671      0.8657     0.0216  5
max valid BA                0.8900      0.8910     0.0231  5
best valid F1               0.7470      0.7568     0.0298  5
test BA                     0.8403      0.8329     0.0460  5
test AUC                    0.9218      0.9264     0.0327  5
test AUC in-protein         0.9113      0.9038     0.0388  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.9174      0.9231     0.0319  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.6820      0.6852     0.0777  5
test sensitivity            0.8144      0.8367     0.0703  5
test specificity            0.8662      0.8630     0.0480  5
test precision              0.5906      0.5833     0.0950  5
test loss                   0.3083      0.3215     0.0679  5
FPR (FP/(FP+TN))            0.1338      0.1370     0.0480  5
FNR (FN/(FN+TP))            0.1856      0.1633     0.0703  5

=== abs(sensitivity-specificity) gap: mean=0.0717 median=0.0507 n=5 ===
sensitivity std across seeds (by group): mean=0.0703 median=0.0703 n=1
specificity std across seeds (by group): mean=0.0480 median=0.0480 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8671      0.8657     0.0216  5
  max valid BA                0.8900      0.8910     0.0231  5
  best valid F1               0.7470      0.7568     0.0298  5
  test BA                     0.8403      0.8329     0.0460  5
  test AUC                    0.9218      0.9264     0.0327  5
  test AUC in-protein         0.9113      0.9038     0.0388  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.9174      0.9231     0.0319  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.6820      0.6852     0.0777  5
  test sensitivity            0.8144      0.8367     0.0703  5
  test specificity            0.8662      0.8630     0.0480  5
  test precision              0.5906      0.5833     0.0950  5
  test loss                   0.3083      0.3215     0.0679  5
  FPR (FP/(FP+TN))            0.1338      0.1370     0.0480  5
  FNR (FN/(FN+TP))            0.1856      0.1633     0.0703  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_mbw_hid32_m8 --seeds=0,1,2,3,4`
