# mlp_s15_nomb_hid64_dpt0_3mlp

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid64_dpt0_3mlp'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8268      0.8734      0.9483      0.8844      0.9098      0.8653
ALL                 5      0.8268      0.8734      0.9483      0.8844      0.9098      0.8653

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8700      0.8802     0.0365  5
max valid BA                0.8876      0.8854     0.0378  5
best valid F1               0.8382      0.8257     0.0533  5
test BA                     0.8501      0.8567     0.0626  5
test AUC                    0.9261      0.9398     0.0447  5
test AUC in-protein         0.9387      0.9513     0.0335  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9324      0.9495     0.0391  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7985      0.8125     0.0796  5
test sensitivity            0.8268      0.7959     0.0654  5
test specificity            0.8734      0.9053     0.0796  5
test precision              0.7761      0.8163     0.1041  5
test loss                   0.3239      0.3016     0.0978  5
FPR (FP/(FP+TN))            0.1266      0.0947     0.0796  5
FNR (FN/(FN+TP))            0.1732      0.2041     0.0654  5

=== abs(sensitivity-specificity) gap: mean=0.0724 median=0.0719 n=5 ===
sensitivity std across seeds (by group): mean=0.0654 median=0.0654 n=1
specificity std across seeds (by group): mean=0.0796 median=0.0796 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8700      0.8802     0.0365  5
  max valid BA                0.8876      0.8854     0.0378  5
  best valid F1               0.8382      0.8257     0.0533  5
  test BA                     0.8501      0.8567     0.0626  5
  test AUC                    0.9261      0.9398     0.0447  5
  test AUC in-protein         0.9387      0.9513     0.0335  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9324      0.9495     0.0391  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7985      0.8125     0.0796  5
  test sensitivity            0.8268      0.7959     0.0654  5
  test specificity            0.8734      0.9053     0.0796  5
  test precision              0.7761      0.8163     0.1041  5
  test loss                   0.3239      0.3016     0.0978  5
  FPR (FP/(FP+TN))            0.1266      0.0947     0.0796  5
  FNR (FN/(FN+TP))            0.1732      0.2041     0.0654  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid64_dpt0_3mlp --seeds=0,1,2,3,4`
