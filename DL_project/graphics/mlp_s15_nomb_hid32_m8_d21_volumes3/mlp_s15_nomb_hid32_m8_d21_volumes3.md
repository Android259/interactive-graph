# mlp_s15_nomb_hid32_m8_d21_volumes3

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid32_m8_d21_volumes3'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8014      0.8316      0.8995      0.8137      0.8888      0.8322
ALL                 5      0.8014      0.8316      0.8995      0.8137      0.8888      0.8322

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8511      0.8594     0.0484  5
max valid BA                0.8605      0.8646     0.0487  5
best valid F1               0.8022      0.7965     0.0655  5
test BA                     0.8165      0.8021     0.0391  5
test AUC                    0.9058      0.9198     0.0290  5
test AUC in-protein         0.8996      0.8914     0.0417  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.8934      0.9158     0.0425  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7515      0.7416     0.0488  5
test sensitivity            0.8014      0.8125     0.0690  5
test specificity            0.8316      0.8557     0.0692  5
test precision              0.7145      0.7500     0.0809  5
test loss                   0.3745      0.3427     0.0568  5
FPR (FP/(FP+TN))            0.1684      0.1443     0.0692  5
FNR (FN/(FN+TP))            0.1986      0.1875     0.0690  5

=== abs(sensitivity-specificity) gap: mean=0.0657 median=0.0433 n=5 ===
sensitivity std across seeds (by group): mean=0.0690 median=0.0690 n=1
specificity std across seeds (by group): mean=0.0692 median=0.0692 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8511      0.8594     0.0484  5
  max valid BA                0.8605      0.8646     0.0487  5
  best valid F1               0.8022      0.7965     0.0655  5
  test BA                     0.8165      0.8021     0.0391  5
  test AUC                    0.9058      0.9198     0.0290  5
  test AUC in-protein         0.8996      0.8914     0.0417  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.8934      0.9158     0.0425  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7515      0.7416     0.0488  5
  test sensitivity            0.8014      0.8125     0.0690  5
  test specificity            0.8316      0.8557     0.0692  5
  test precision              0.7145      0.7500     0.0809  5
  test loss                   0.3745      0.3427     0.0568  5
  FPR (FP/(FP+TN))            0.1684      0.1443     0.0692  5
  FNR (FN/(FN+TP))            0.1986      0.1875     0.0690  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid32_m8_d21_volumes3 --seeds=0,1,2,3,4`
