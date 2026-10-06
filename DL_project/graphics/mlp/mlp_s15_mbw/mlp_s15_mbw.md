# mlp_s15_mbw

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_mbw'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.7938      0.7850      0.7748      0.7742      0.8638      0.7879
ALL                 5      0.7938      0.7850      0.7748      0.7742      0.8638      0.7879

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8151      0.8107     0.0355  5
max valid BA                0.8259      0.8107     0.0396  5
best valid F1               0.6237      0.6142     0.0484  5
test BA                     0.7894      0.7928     0.0520  5
test AUC                    0.8543      0.8543     0.0405  5
test AUC in-protein         0.8474      0.8357     0.0366  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.8550      0.8480     0.0339  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.5838      0.5755     0.0731  5
test sensitivity            0.7938      0.7959     0.0773  5
test specificity            0.7850      0.7867     0.0600  5
test precision              0.4644      0.4396     0.0746  5
test loss                   0.4584      0.4847     0.0620  5
FPR (FP/(FP+TN))            0.2150      0.2133     0.0600  5
FNR (FN/(FN+TP))            0.2062      0.2041     0.0773  5

=== abs(sensitivity-specificity) gap: mean=0.0802 median=0.0856 n=5 ===
sensitivity std across seeds (by group): mean=0.0773 median=0.0773 n=1
specificity std across seeds (by group): mean=0.0600 median=0.0600 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8151      0.8107     0.0355  5
  max valid BA                0.8259      0.8107     0.0396  5
  best valid F1               0.6237      0.6142     0.0484  5
  test BA                     0.7894      0.7928     0.0520  5
  test AUC                    0.8543      0.8543     0.0405  5
  test AUC in-protein         0.8474      0.8357     0.0366  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.8550      0.8480     0.0339  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.5838      0.5755     0.0731  5
  test sensitivity            0.7938      0.7959     0.0773  5
  test specificity            0.7850      0.7867     0.0600  5
  test precision              0.4644      0.4396     0.0746  5
  test loss                   0.4584      0.4847     0.0620  5
  FPR (FP/(FP+TN))            0.2150      0.2133     0.0600  5
  FNR (FN/(FN+TP))            0.2062      0.2041     0.0773  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_mbw --seeds=0,1,2,3,4`
