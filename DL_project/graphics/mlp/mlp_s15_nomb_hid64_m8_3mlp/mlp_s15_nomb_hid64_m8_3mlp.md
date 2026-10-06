# mlp_s15_nomb_hid64_m8_3mlp

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid64_m8_3mlp'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8799      0.8672      0.9438      0.8695      0.9305      0.8632
ALL                 5      0.8799      0.8672      0.9438      0.8695      0.9305      0.8632

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8904      0.8906     0.0273  5
max valid BA                0.8968      0.8906     0.0330  5
best valid F1               0.8489      0.8400     0.0496  5
test BA                     0.8736      0.8958     0.0495  5
test AUC                    0.9423      0.9558     0.0326  5
test AUC in-protein         0.9529      0.9496     0.0278  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9495      0.9656     0.0373  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8230      0.8571     0.0631  5
test sensitivity            0.8799      0.8776     0.0684  5
test specificity            0.8672      0.8947     0.0765  5
test precision              0.7785      0.8070     0.0880  5
test loss                   0.2975      0.2573     0.0843  5
FPR (FP/(FP+TN))            0.1328      0.1053     0.0765  5
FNR (FN/(FN+TP))            0.1201      0.1224     0.0684  5

=== abs(sensitivity-specificity) gap: mean=0.0835 median=0.0522 n=5 ===
sensitivity std across seeds (by group): mean=0.0684 median=0.0684 n=1
specificity std across seeds (by group): mean=0.0765 median=0.0765 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8904      0.8906     0.0273  5
  max valid BA                0.8968      0.8906     0.0330  5
  best valid F1               0.8489      0.8400     0.0496  5
  test BA                     0.8736      0.8958     0.0495  5
  test AUC                    0.9423      0.9558     0.0326  5
  test AUC in-protein         0.9529      0.9496     0.0278  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9495      0.9656     0.0373  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8230      0.8571     0.0631  5
  test sensitivity            0.8799      0.8776     0.0684  5
  test specificity            0.8672      0.8947     0.0765  5
  test precision              0.7785      0.8070     0.0880  5
  test loss                   0.2975      0.2573     0.0843  5
  FPR (FP/(FP+TN))            0.1328      0.1053     0.0765  5
  FNR (FN/(FN+TP))            0.1201      0.1224     0.0684  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid64_m8_3mlp --seeds=0,1,2,3,4`
