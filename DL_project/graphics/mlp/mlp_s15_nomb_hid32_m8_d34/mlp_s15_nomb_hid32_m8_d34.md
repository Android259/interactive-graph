# mlp_s15_nomb_hid32_m8_d34

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid32_m8_d34'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8516      0.8379      0.9062      0.8218      0.8972      0.8383
ALL                 5      0.8516      0.8379      0.9062      0.8218      0.8972      0.8383

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8479      0.8438     0.0437  5
max valid BA                0.8678      0.8542     0.0444  5
best valid F1               0.8104      0.7857     0.0593  5
test BA                     0.8448      0.8564     0.0526  5
test AUC                    0.9137      0.9327     0.0430  5
test AUC in-protein         0.9060      0.8982     0.0363  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9026      0.9227     0.0358  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7844      0.8000     0.0649  5
test sensitivity            0.8516      0.8571     0.0594  5
test specificity            0.8379      0.8542     0.0461  5
test precision              0.7272      0.7500     0.0682  5
test loss                   0.3498      0.3204     0.0726  5
FPR (FP/(FP+TN))            0.1621      0.1458     0.0461  5
FNR (FN/(FN+TP))            0.1484      0.1429     0.0594  5

=== abs(sensitivity-specificity) gap: mean=0.0168 median=0.0208 n=5 ===
sensitivity std across seeds (by group): mean=0.0594 median=0.0594 n=1
specificity std across seeds (by group): mean=0.0461 median=0.0461 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8479      0.8438     0.0437  5
  max valid BA                0.8678      0.8542     0.0444  5
  best valid F1               0.8104      0.7857     0.0593  5
  test BA                     0.8448      0.8564     0.0526  5
  test AUC                    0.9137      0.9327     0.0430  5
  test AUC in-protein         0.9060      0.8982     0.0363  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9026      0.9227     0.0358  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7844      0.8000     0.0649  5
  test sensitivity            0.8516      0.8571     0.0594  5
  test specificity            0.8379      0.8542     0.0461  5
  test precision              0.7272      0.7500     0.0682  5
  test loss                   0.3498      0.3204     0.0726  5
  FPR (FP/(FP+TN))            0.1621      0.1458     0.0461  5
  FNR (FN/(FN+TP))            0.1484      0.1429     0.0594  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid32_m8_d34 --seeds=0,1,2,3,4`
