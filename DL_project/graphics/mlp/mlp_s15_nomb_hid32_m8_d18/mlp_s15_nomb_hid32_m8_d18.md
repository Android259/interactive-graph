# mlp_s15_nomb_hid32_m8_d18

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid32_m8_d18'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8225      0.8089      0.8697      0.7997      0.8680      0.8030
ALL                 5      0.8225      0.8089      0.8697      0.7997      0.8680      0.8030

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8303      0.8438     0.0395  5
max valid BA                0.8355      0.8542     0.0383  5
best valid F1               0.7684      0.7895     0.0444  5
test BA                     0.8157      0.8152     0.0401  5
test AUC                    0.8824      0.8908     0.0330  5
test AUC in-protein         0.8895      0.8848     0.0386  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.8899      0.8968     0.0226  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7473      0.7434     0.0494  5
test sensitivity            0.8225      0.8542     0.0525  5
test specificity            0.8089      0.8021     0.0379  5
test precision              0.6854      0.6724     0.0524  5
test loss                   0.4220      0.4176     0.0404  5
FPR (FP/(FP+TN))            0.1911      0.1979     0.0379  5
FNR (FN/(FN+TP))            0.1775      0.1458     0.0525  5

=== abs(sensitivity-specificity) gap: mean=0.0290 median=0.0121 n=5 ===
sensitivity std across seeds (by group): mean=0.0525 median=0.0525 n=1
specificity std across seeds (by group): mean=0.0379 median=0.0379 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8303      0.8438     0.0395  5
  max valid BA                0.8355      0.8542     0.0383  5
  best valid F1               0.7684      0.7895     0.0444  5
  test BA                     0.8157      0.8152     0.0401  5
  test AUC                    0.8824      0.8908     0.0330  5
  test AUC in-protein         0.8895      0.8848     0.0386  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.8899      0.8968     0.0226  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7473      0.7434     0.0494  5
  test sensitivity            0.8225      0.8542     0.0525  5
  test specificity            0.8089      0.8021     0.0379  5
  test precision              0.6854      0.6724     0.0524  5
  test loss                   0.4220      0.4176     0.0404  5
  FPR (FP/(FP+TN))            0.1911      0.1979     0.0379  5
  FNR (FN/(FN+TP))            0.1775      0.1458     0.0525  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid32_m8_d18 --seeds=0,1,2,3,4`
