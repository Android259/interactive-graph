# ge_s15_prothid32_hid64_noreg_rbf32

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'ge_s15_prothid32_hid64_noreg_rbf32'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8804      0.8921      0.9698      0.9052      0.9340      0.8901
ALL                 5      0.8804      0.8921      0.9698      0.9052      0.9340      0.8901

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.9018      0.9167     0.0349  5
max valid BA                0.9120      0.9188     0.0343  5
best valid F1               0.8688      0.8866     0.0445  5
test BA                     0.8863      0.9027     0.0524  5
test AUC                    0.9523      0.9644     0.0345  5
test AUC in-protein         0.9471      0.9496     0.0174  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9389      0.9484     0.0322  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8426      0.8687     0.0694  5
test sensitivity            0.8804      0.8776     0.0484  5
test specificity            0.8921      0.9062     0.0623  5
test precision              0.8097      0.8302     0.0895  5
test loss                   0.3483      0.2419     0.2376  5
FPR (FP/(FP+TN))            0.1079      0.0938     0.0623  5
FNR (FN/(FN+TP))            0.1196      0.1224     0.0484  5

=== abs(sensitivity-specificity) gap: mean=0.0293 median=0.0328 n=5 ===
sensitivity std across seeds (by group): mean=0.0484 median=0.0484 n=1
specificity std across seeds (by group): mean=0.0623 median=0.0623 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9018      0.9167     0.0349  5
  max valid BA                0.9120      0.9188     0.0343  5
  best valid F1               0.8688      0.8866     0.0445  5
  test BA                     0.8863      0.9027     0.0524  5
  test AUC                    0.9523      0.9644     0.0345  5
  test AUC in-protein         0.9471      0.9496     0.0174  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9389      0.9484     0.0322  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8426      0.8687     0.0694  5
  test sensitivity            0.8804      0.8776     0.0484  5
  test specificity            0.8921      0.9062     0.0623  5
  test precision              0.8097      0.8302     0.0895  5
  test loss                   0.3483      0.2419     0.2376  5
  FPR (FP/(FP+TN))            0.1079      0.0938     0.0623  5
  FNR (FN/(FN+TP))            0.1196      0.1224     0.0484  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_rbf32 --seeds=0,1,2,3,4`
