# mlp_s15_mbw_hid32_d11

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_mbw_hid32_d11'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.7566      0.7129      0.7407      0.6720      0.7890      0.6913
ALL                 5      0.7566      0.7129      0.7407      0.6720      0.7890      0.6913

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.7262      0.7278     0.0173  5
max valid BA                0.7401      0.7364     0.0214  5
best valid F1               0.5061      0.5000     0.0211  5
test BA                     0.7348      0.7289     0.0522  5
test AUC                    0.7922      0.7838     0.0506  5
test AUC in-protein         0.7766      0.7500     0.0754  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.7993      0.8105     0.0608  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.5080      0.4819     0.0810  5
test sensitivity            0.7566      0.7500     0.0568  5
test specificity            0.7129      0.7078     0.0825  5
test precision              0.3873      0.3600     0.0931  5
test loss                   0.5238      0.5484     0.0526  5
FPR (FP/(FP+TN))            0.2871      0.2922     0.0825  5
FNR (FN/(FN+TP))            0.2434      0.2500     0.0568  5

=== abs(sensitivity-specificity) gap: mean=0.0763 median=0.0549 n=5 ===
sensitivity std across seeds (by group): mean=0.0568 median=0.0568 n=1
specificity std across seeds (by group): mean=0.0825 median=0.0825 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7262      0.7278     0.0173  5
  max valid BA                0.7401      0.7364     0.0214  5
  best valid F1               0.5061      0.5000     0.0211  5
  test BA                     0.7348      0.7289     0.0522  5
  test AUC                    0.7922      0.7838     0.0506  5
  test AUC in-protein         0.7766      0.7500     0.0754  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.7993      0.8105     0.0608  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.5080      0.4819     0.0810  5
  test sensitivity            0.7566      0.7500     0.0568  5
  test specificity            0.7129      0.7078     0.0825  5
  test precision              0.3873      0.3600     0.0931  5
  test loss                   0.5238      0.5484     0.0526  5
  FPR (FP/(FP+TN))            0.2871      0.2922     0.0825  5
  FNR (FN/(FN+TP))            0.2434      0.2500     0.0568  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_mbw_hid32_d11 --seeds=0,1,2,3,4`
