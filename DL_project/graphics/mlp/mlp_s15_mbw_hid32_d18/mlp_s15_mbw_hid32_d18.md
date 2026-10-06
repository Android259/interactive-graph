# mlp_s15_mbw_hid32_d18

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_mbw_hid32_d18'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.7398      0.7688      0.7666      0.7385      0.8017      0.7452
ALL                 5      0.7398      0.7688      0.7666      0.7385      0.8017      0.7452

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.7622      0.7428     0.0438  5
max valid BA                0.7735      0.7612     0.0391  5
best valid F1               0.5579      0.5484     0.0490  5
test BA                     0.7543      0.7453     0.0354  5
test AUC                    0.8182      0.8304     0.0411  5
test AUC in-protein         0.8220      0.8302     0.0487  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.8244      0.8237     0.0423  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.5397      0.5294     0.0536  5
test sensitivity            0.7398      0.7292     0.0420  5
test specificity            0.7688      0.7560     0.0460  5
test precision              0.4271      0.4138     0.0625  5
test loss                   0.4756      0.4686     0.0479  5
FPR (FP/(FP+TN))            0.2312      0.2440     0.0460  5
FNR (FN/(FN+TP))            0.2602      0.2708     0.0420  5

=== abs(sensitivity-specificity) gap: mean=0.0417 median=0.0298 n=5 ===
sensitivity std across seeds (by group): mean=0.0420 median=0.0420 n=1
specificity std across seeds (by group): mean=0.0460 median=0.0460 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7622      0.7428     0.0438  5
  max valid BA                0.7735      0.7612     0.0391  5
  best valid F1               0.5579      0.5484     0.0490  5
  test BA                     0.7543      0.7453     0.0354  5
  test AUC                    0.8182      0.8304     0.0411  5
  test AUC in-protein         0.8220      0.8302     0.0487  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.8244      0.8237     0.0423  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.5397      0.5294     0.0536  5
  test sensitivity            0.7398      0.7292     0.0420  5
  test specificity            0.7688      0.7560     0.0460  5
  test precision              0.4271      0.4138     0.0625  5
  test loss                   0.4756      0.4686     0.0479  5
  FPR (FP/(FP+TN))            0.2312      0.2440     0.0460  5
  FNR (FN/(FN+TP))            0.2602      0.2708     0.0420  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_mbw_hid32_d18 --seeds=0,1,2,3,4`
