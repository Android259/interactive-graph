# mlp_s15_mbw_hid32_d13

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_mbw_hid32_d13'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.7315      0.7465      0.7747      0.7231      0.7973      0.7534
ALL                 5      0.7315      0.7465      0.7747      0.7231      0.7973      0.7534

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.7579      0.7669     0.0314  5
max valid BA                0.7754      0.7856     0.0320  5
best valid F1               0.5582      0.5734     0.0412  5
test BA                     0.7390      0.7436     0.0360  5
test AUC                    0.8269      0.8275     0.0486  5
test AUC in-protein         0.8268      0.8370     0.0627  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.8387      0.8352     0.0558  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.5183      0.5147     0.0525  5
test sensitivity            0.7315      0.7292     0.0370  5
test specificity            0.7465      0.7580     0.0615  5
test precision              0.4039      0.3977     0.0619  5
test loss                   0.4804      0.4822     0.0572  5
FPR (FP/(FP+TN))            0.2535      0.2420     0.0615  5
FNR (FN/(FN+TP))            0.2685      0.2708     0.0370  5

=== abs(sensitivity-specificity) gap: mean=0.0544 median=0.0469 n=5 ===
sensitivity std across seeds (by group): mean=0.0370 median=0.0370 n=1
specificity std across seeds (by group): mean=0.0615 median=0.0615 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7579      0.7669     0.0314  5
  max valid BA                0.7754      0.7856     0.0320  5
  best valid F1               0.5582      0.5734     0.0412  5
  test BA                     0.7390      0.7436     0.0360  5
  test AUC                    0.8269      0.8275     0.0486  5
  test AUC in-protein         0.8268      0.8370     0.0627  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.8387      0.8352     0.0558  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.5183      0.5147     0.0525  5
  test sensitivity            0.7315      0.7292     0.0370  5
  test specificity            0.7465      0.7580     0.0615  5
  test precision              0.4039      0.3977     0.0619  5
  test loss                   0.4804      0.4822     0.0572  5
  FPR (FP/(FP+TN))            0.2535      0.2420     0.0615  5
  FNR (FN/(FN+TP))            0.2685      0.2708     0.0370  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_mbw_hid32_d13 --seeds=0,1,2,3,4`
