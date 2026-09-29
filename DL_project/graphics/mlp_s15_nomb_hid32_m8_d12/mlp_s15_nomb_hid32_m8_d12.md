# mlp_s15_nomb_hid32_m8_d12

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid32_m8_d12'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8143      0.8027      0.8544      0.7619      0.8763      0.7844
ALL                 5      0.8143      0.8027      0.8544      0.7619      0.8763      0.7844

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8272      0.8125     0.0495  5
max valid BA                0.8303      0.8177     0.0482  5
best valid F1               0.7617      0.7525     0.0576  5
test BA                     0.8085      0.8050     0.0320  5
test AUC                    0.8897      0.8893     0.0317  5
test AUC in-protein         0.8838      0.8764     0.0693  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.8821      0.8655     0.0608  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7388      0.7321     0.0411  5
test sensitivity            0.8143      0.8333     0.0469  5
test specificity            0.8027      0.7938     0.0508  5
test precision              0.6784      0.6508     0.0571  5
test loss                   0.4155      0.4223     0.0441  5
FPR (FP/(FP+TN))            0.1973      0.2062     0.0508  5
FNR (FN/(FN+TP))            0.1857      0.1667     0.0469  5

=== abs(sensitivity-specificity) gap: mean=0.0596 median=0.0591 n=5 ===
sensitivity std across seeds (by group): mean=0.0469 median=0.0469 n=1
specificity std across seeds (by group): mean=0.0508 median=0.0508 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8272      0.8125     0.0495  5
  max valid BA                0.8303      0.8177     0.0482  5
  best valid F1               0.7617      0.7525     0.0576  5
  test BA                     0.8085      0.8050     0.0320  5
  test AUC                    0.8897      0.8893     0.0317  5
  test AUC in-protein         0.8838      0.8764     0.0693  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.8821      0.8655     0.0608  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7388      0.7321     0.0411  5
  test sensitivity            0.8143      0.8333     0.0469  5
  test specificity            0.8027      0.7938     0.0508  5
  test precision              0.6784      0.6508     0.0571  5
  test loss                   0.4155      0.4223     0.0441  5
  FPR (FP/(FP+TN))            0.1973      0.2062     0.0508  5
  FNR (FN/(FN+TP))            0.1857      0.1667     0.0469  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid32_m8_d12 --seeds=0,1,2,3,4`
