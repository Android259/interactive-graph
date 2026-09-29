# ge_s15_prothid32_hid64_noreg_hid128

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'ge_s15_prothid32_hid64_noreg_hid128'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8969      0.8839      0.9583      0.8881      0.9300      0.8922
ALL                 5      0.8969      0.8839      0.9583      0.8881      0.9300      0.8922

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8811      0.8906     0.0460  5
max valid BA                0.9111      0.9219     0.0332  5
best valid F1               0.8694      0.8776     0.0508  5
test BA                     0.8904      0.8802     0.0431  5
test AUC                    0.9516      0.9670     0.0305  5
test AUC in-protein         0.9430      0.9477     0.0228  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9482      0.9570     0.0272  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8458      0.8421     0.0583  5
test sensitivity            0.8969      0.9184     0.0596  5
test specificity            0.8839      0.9062     0.0813  5
test precision              0.8072      0.8214     0.0961  5
test loss                   0.3285      0.2979     0.1564  5
FPR (FP/(FP+TN))            0.1161      0.0938     0.0813  5
FNR (FN/(FN+TP))            0.1031      0.0816     0.0596  5

=== abs(sensitivity-specificity) gap: mean=0.0826 median=0.0625 n=5 ===
sensitivity std across seeds (by group): mean=0.0596 median=0.0596 n=1
specificity std across seeds (by group): mean=0.0813 median=0.0813 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8811      0.8906     0.0460  5
  max valid BA                0.9111      0.9219     0.0332  5
  best valid F1               0.8694      0.8776     0.0508  5
  test BA                     0.8904      0.8802     0.0431  5
  test AUC                    0.9516      0.9670     0.0305  5
  test AUC in-protein         0.9430      0.9477     0.0228  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9482      0.9570     0.0272  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8458      0.8421     0.0583  5
  test sensitivity            0.8969      0.9184     0.0596  5
  test specificity            0.8839      0.9062     0.0813  5
  test precision              0.8072      0.8214     0.0961  5
  test loss                   0.3285      0.2979     0.1564  5
  FPR (FP/(FP+TN))            0.1161      0.0938     0.0813  5
  FNR (FN/(FN+TP))            0.1031      0.0816     0.0596  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_hid128 --seeds=0,1,2,3,4`
