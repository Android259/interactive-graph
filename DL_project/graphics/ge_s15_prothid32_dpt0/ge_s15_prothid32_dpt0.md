# ge_s15_prothid32_dpt0

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'ge_s15_prothid32_dpt0'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8639      0.8338      0.9200      0.8431      0.9297      0.8257
ALL                 5      0.8639      0.8338      0.9200      0.8431      0.9297      0.8257

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8707      0.8594     0.0226  5
max valid BA                0.8777      0.8698     0.0260  5
best valid F1               0.8182      0.8113     0.0352  5
test BA                     0.8489      0.8385     0.0298  5
test AUC                    0.9199      0.9299     0.0336  5
test AUC in-protein         0.9063      0.9155     0.0372  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9014      0.9076     0.0376  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7888      0.7736     0.0417  5
test sensitivity            0.8639      0.8542     0.0415  5
test specificity            0.8338      0.8229     0.0608  5
test precision              0.7294      0.7069     0.0720  5
test loss                   0.3569      0.3447     0.0717  5
FPR (FP/(FP+TN))            0.1662      0.1771     0.0608  5
FNR (FN/(FN+TP))            0.1361      0.1458     0.0415  5

=== abs(sensitivity-specificity) gap: mean=0.0624 median=0.0429 n=5 ===
sensitivity std across seeds (by group): mean=0.0415 median=0.0415 n=1
specificity std across seeds (by group): mean=0.0608 median=0.0608 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8707      0.8594     0.0226  5
  max valid BA                0.8777      0.8698     0.0260  5
  best valid F1               0.8182      0.8113     0.0352  5
  test BA                     0.8489      0.8385     0.0298  5
  test AUC                    0.9199      0.9299     0.0336  5
  test AUC in-protein         0.9063      0.9155     0.0372  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9014      0.9076     0.0376  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7888      0.7736     0.0417  5
  test sensitivity            0.8639      0.8542     0.0415  5
  test specificity            0.8338      0.8229     0.0608  5
  test precision              0.7294      0.7069     0.0720  5
  test loss                   0.3569      0.3447     0.0717  5
  FPR (FP/(FP+TN))            0.1662      0.1771     0.0608  5
  FNR (FN/(FN+TP))            0.1361      0.1458     0.0415  5
```

## AUC vs chemistry null model, in-sample increment

Failed: FileNotFoundError: [Errno 2] No usable temporary directory found in ['/tmp', '/var/tmp', '/usr/tmp', '/home/andrei/DL_project_5/DL_project'] -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_dpt0 --seeds=0,1,2,3,4`
