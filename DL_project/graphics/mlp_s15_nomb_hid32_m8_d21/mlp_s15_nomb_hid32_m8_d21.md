# mlp_s15_nomb_hid32_m8_d21

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid32_m8_d21'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8432      0.8588      0.8943      0.8157      0.8927      0.8136
ALL                 5      0.8432      0.8588      0.8943      0.8157      0.8927      0.8136

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8448      0.8490     0.0568  5
max valid BA                0.8531      0.8490     0.0524  5
best valid F1               0.7917      0.7788     0.0687  5
test BA                     0.8510      0.8639     0.0370  5
test AUC                    0.9158      0.9289     0.0303  5
test AUC in-protein         0.9059      0.9045     0.0246  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9090      0.9118     0.0327  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7948      0.8119     0.0478  5
test sensitivity            0.8432      0.8542     0.0388  5
test specificity            0.8588      0.8737     0.0383  5
test precision              0.7521      0.7736     0.0569  5
test loss                   0.3598      0.3464     0.0499  5
FPR (FP/(FP+TN))            0.1412      0.1263     0.0383  5
FNR (FN/(FN+TP))            0.1568      0.1458     0.0388  5

=== abs(sensitivity-specificity) gap: mean=0.0245 median=0.0221 n=5 ===
sensitivity std across seeds (by group): mean=0.0388 median=0.0388 n=1
specificity std across seeds (by group): mean=0.0383 median=0.0383 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8448      0.8490     0.0568  5
  max valid BA                0.8531      0.8490     0.0524  5
  best valid F1               0.7917      0.7788     0.0687  5
  test BA                     0.8510      0.8639     0.0370  5
  test AUC                    0.9158      0.9289     0.0303  5
  test AUC in-protein         0.9059      0.9045     0.0246  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9090      0.9118     0.0327  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7948      0.8119     0.0478  5
  test sensitivity            0.8432      0.8542     0.0388  5
  test specificity            0.8588      0.8737     0.0383  5
  test precision              0.7521      0.7736     0.0569  5
  test loss                   0.3598      0.3464     0.0499  5
  FPR (FP/(FP+TN))            0.1412      0.1263     0.0383  5
  FNR (FN/(FN+TP))            0.1568      0.1458     0.0388  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid32_m8_d21 --seeds=0,1,2,3,4`
