# mlp_s15_mbw_hid32_lr3e4

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_mbw_hid32_lr3e4'
rows: 2

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    2      0.8355      0.8266      0.8589      0.8402      0.9087      0.8594
ALL                 2      0.8355      0.8266      0.8589      0.8402      0.9087      0.8594

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8804      0.8804     0.0313  2
max valid BA                0.8841      0.8841     0.0326  2
best valid F1               0.7302      0.7302     0.0402  2
test BA                     0.8310      0.8310     0.0440  2
test AUC                    0.9179      0.9179     0.0109  2
test AUC in-protein         0.9228      0.9228     0.0065  2
  (proteins averaged)      16.5000     16.5000     3.5355  2
test AUC in-protein (pairs)      0.9166      0.9166     0.0169  2
  (proteins contributing)     20.0000     20.0000     4.2426  2
test F1                     0.6438      0.6438     0.0553  2
test sensitivity            0.8355      0.8355     0.0559  2
test specificity            0.8266      0.8266     0.0322  2
test precision              0.5238      0.5238     0.0513  2
test loss                   0.3319      0.3319     0.0157  2
FPR (FP/(FP+TN))            0.1734      0.1734     0.0322  2
FNR (FN/(FN+TP))            0.1645      0.1645     0.0559  2

=== abs(sensitivity-specificity) gap: mean=0.0168 median=0.0168 n=2 ===
sensitivity std across seeds (by group): mean=0.0559 median=0.0559 n=1
specificity std across seeds (by group): mean=0.0322 median=0.0322 n=1

=== By group ===
groups_species15 (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8804      0.8804     0.0313  2
  max valid BA                0.8841      0.8841     0.0326  2
  best valid F1               0.7302      0.7302     0.0402  2
  test BA                     0.8310      0.8310     0.0440  2
  test AUC                    0.9179      0.9179     0.0109  2
  test AUC in-protein         0.9228      0.9228     0.0065  2
    (proteins averaged)      16.5000     16.5000     3.5355  2
  test AUC in-protein (pairs)      0.9166      0.9166     0.0169  2
    (proteins contributing)     20.0000     20.0000     4.2426  2
  test F1                     0.6438      0.6438     0.0553  2
  test sensitivity            0.8355      0.8355     0.0559  2
  test specificity            0.8266      0.8266     0.0322  2
  test precision              0.5238      0.5238     0.0513  2
  test loss                   0.3319      0.3319     0.0157  2
  FPR (FP/(FP+TN))            0.1734      0.1734     0.0322  2
  FNR (FN/(FN+TP))            0.1645      0.1645     0.0559  2
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_mbw_hid32_lr3e4 --seeds=0,1,2,3,4`
