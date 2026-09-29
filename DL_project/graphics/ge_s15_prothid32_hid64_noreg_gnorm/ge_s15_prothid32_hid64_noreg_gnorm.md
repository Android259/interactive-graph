# ge_s15_prothid32_hid64_noreg_gnorm

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'ge_s15_prothid32_hid64_noreg_gnorm'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8764      0.8961      0.9564      0.8925      0.9505      0.8839
ALL                 5      0.8764      0.8961      0.9564      0.8925      0.9505      0.8839

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.9007      0.9115     0.0241  5
max valid BA                0.9172      0.9219     0.0320  5
best valid F1               0.8775      0.8958     0.0437  5
test BA                     0.8863      0.9010     0.0400  5
test AUC                    0.9464      0.9601     0.0366  5
test AUC in-protein         0.9524      0.9608     0.0276  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9465      0.9553     0.0315  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8421      0.8600     0.0509  5
test sensitivity            0.8764      0.8750     0.0554  5
test specificity            0.8961      0.9062     0.0423  5
test precision              0.8123      0.8269     0.0638  5
test loss                   0.4111      0.3209     0.3101  5
FPR (FP/(FP+TN))            0.1039      0.0938     0.0423  5
FNR (FN/(FN+TP))            0.1236      0.1250     0.0554  5

=== abs(sensitivity-specificity) gap: mean=0.0451 median=0.0521 n=5 ===
sensitivity std across seeds (by group): mean=0.0554 median=0.0554 n=1
specificity std across seeds (by group): mean=0.0423 median=0.0423 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9007      0.9115     0.0241  5
  max valid BA                0.9172      0.9219     0.0320  5
  best valid F1               0.8775      0.8958     0.0437  5
  test BA                     0.8863      0.9010     0.0400  5
  test AUC                    0.9464      0.9601     0.0366  5
  test AUC in-protein         0.9524      0.9608     0.0276  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9465      0.9553     0.0315  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8421      0.8600     0.0509  5
  test sensitivity            0.8764      0.8750     0.0554  5
  test specificity            0.8961      0.9062     0.0423  5
  test precision              0.8123      0.8269     0.0638  5
  test loss                   0.4111      0.3209     0.3101  5
  FPR (FP/(FP+TN))            0.1039      0.0938     0.0423  5
  FNR (FN/(FN+TP))            0.1236      0.1250     0.0554  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_gnorm --seeds=0,1,2,3,4`
