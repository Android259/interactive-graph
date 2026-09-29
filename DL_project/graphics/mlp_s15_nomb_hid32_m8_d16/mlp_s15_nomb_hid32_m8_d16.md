# mlp_s15_nomb_hid32_m8_d16

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid32_m8_d16'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8266      0.8131      0.8686      0.7908      0.8595      0.8114
ALL                 5      0.8266      0.8131      0.8686      0.7908      0.8595      0.8114

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8343      0.8333     0.0385  5
max valid BA                0.8355      0.8333     0.0369  5
best valid F1               0.7701      0.7789     0.0441  5
test BA                     0.8198      0.8281     0.0250  5
test AUC                    0.8903      0.9086     0.0326  5
test AUC in-protein         0.8802      0.9071     0.0611  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.8814      0.8896     0.0491  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7523      0.7647     0.0308  5
test sensitivity            0.8266      0.8542     0.0441  5
test specificity            0.8131      0.8144     0.0369  5
test precision              0.6917      0.6949     0.0387  5
test loss                   0.4056      0.3831     0.0440  5
FPR (FP/(FP+TN))            0.1869      0.1856     0.0369  5
FNR (FN/(FN+TP))            0.1734      0.1458     0.0441  5

=== abs(sensitivity-specificity) gap: mean=0.0498 median=0.0417 n=5 ===
sensitivity std across seeds (by group): mean=0.0441 median=0.0441 n=1
specificity std across seeds (by group): mean=0.0369 median=0.0369 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8343      0.8333     0.0385  5
  max valid BA                0.8355      0.8333     0.0369  5
  best valid F1               0.7701      0.7789     0.0441  5
  test BA                     0.8198      0.8281     0.0250  5
  test AUC                    0.8903      0.9086     0.0326  5
  test AUC in-protein         0.8802      0.9071     0.0611  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.8814      0.8896     0.0491  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7523      0.7647     0.0308  5
  test sensitivity            0.8266      0.8542     0.0441  5
  test specificity            0.8131      0.8144     0.0369  5
  test precision              0.6917      0.6949     0.0387  5
  test loss                   0.4056      0.3831     0.0440  5
  FPR (FP/(FP+TN))            0.1869      0.1856     0.0369  5
  FNR (FN/(FN+TP))            0.1734      0.1458     0.0441  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid32_m8_d16 --seeds=0,1,2,3,4`
