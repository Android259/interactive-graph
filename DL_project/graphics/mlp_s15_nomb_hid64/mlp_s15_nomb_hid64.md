# mlp_s15_nomb_hid64

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid64'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8805      0.8713      0.9434      0.8645      0.9260      0.8632
ALL                 5      0.8805      0.8713      0.9434      0.8645      0.9260      0.8632

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8812      0.8698     0.0422  5
max valid BA                0.8946      0.8958     0.0350  5
best valid F1               0.8469      0.8367     0.0495  5
test BA                     0.8759      0.8823     0.0553  5
test AUC                    0.9405      0.9468     0.0412  5
test AUC in-protein         0.9434      0.9537     0.0312  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9405      0.9599     0.0432  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8271      0.8454     0.0700  5
test sensitivity            0.8805      0.8367     0.0620  5
test specificity            0.8713      0.8947     0.0797  5
test precision              0.7849      0.8214     0.0984  5
test loss                   0.2946      0.2713     0.0988  5
FPR (FP/(FP+TN))            0.1287      0.1053     0.0797  5
FNR (FN/(FN+TP))            0.1195      0.1633     0.0620  5

=== abs(sensitivity-specificity) gap: mean=0.0790 median=0.0833 n=5 ===
sensitivity std across seeds (by group): mean=0.0620 median=0.0620 n=1
specificity std across seeds (by group): mean=0.0797 median=0.0797 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8812      0.8698     0.0422  5
  max valid BA                0.8946      0.8958     0.0350  5
  best valid F1               0.8469      0.8367     0.0495  5
  test BA                     0.8759      0.8823     0.0553  5
  test AUC                    0.9405      0.9468     0.0412  5
  test AUC in-protein         0.9434      0.9537     0.0312  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9405      0.9599     0.0432  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8271      0.8454     0.0700  5
  test sensitivity            0.8805      0.8367     0.0620  5
  test specificity            0.8713      0.8947     0.0797  5
  test precision              0.7849      0.8214     0.0984  5
  test loss                   0.2946      0.2713     0.0988  5
  FPR (FP/(FP+TN))            0.1287      0.1053     0.0797  5
  FNR (FN/(FN+TP))            0.1195      0.1633     0.0620  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid64 --seeds=0,1,2,3,4`
