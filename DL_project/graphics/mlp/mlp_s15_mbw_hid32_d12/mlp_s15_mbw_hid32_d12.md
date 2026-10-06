# mlp_s15_mbw_hid32_d12

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_mbw_hid32_d12'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.6903      0.7421      0.6952      0.7103      0.7683      0.7130
ALL                 5      0.6903      0.7421      0.6952      0.7103      0.7683      0.7130

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.7222      0.7373     0.0623  5
max valid BA                0.7407      0.7517     0.0530  5
best valid F1               0.5083      0.5270     0.0517  5
test BA                     0.7162      0.7048     0.0427  5
test AUC                    0.7898      0.7790     0.0278  5
test AUC in-protein         0.7917      0.7819     0.0449  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.8014      0.8137     0.0318  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.4871      0.4717     0.0338  5
test sensitivity            0.6903      0.6735     0.1285  5
test specificity            0.7421      0.7177     0.0628  5
test precision              0.3831      0.3925     0.0379  5
test loss                   0.5578      0.5250     0.0742  5
FPR (FP/(FP+TN))            0.2579      0.2823     0.0628  5
FNR (FN/(FN+TP))            0.3097      0.3265     0.1285  5

=== abs(sensitivity-specificity) gap: mean=0.1400 median=0.1195 n=5 ===
sensitivity std across seeds (by group): mean=0.1285 median=0.1285 n=1
specificity std across seeds (by group): mean=0.0628 median=0.0628 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7222      0.7373     0.0623  5
  max valid BA                0.7407      0.7517     0.0530  5
  best valid F1               0.5083      0.5270     0.0517  5
  test BA                     0.7162      0.7048     0.0427  5
  test AUC                    0.7898      0.7790     0.0278  5
  test AUC in-protein         0.7917      0.7819     0.0449  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.8014      0.8137     0.0318  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.4871      0.4717     0.0338  5
  test sensitivity            0.6903      0.6735     0.1285  5
  test specificity            0.7421      0.7177     0.0628  5
  test precision              0.3831      0.3925     0.0379  5
  test loss                   0.5578      0.5250     0.0742  5
  FPR (FP/(FP+TN))            0.2579      0.2823     0.0628  5
  FNR (FN/(FN+TP))            0.3097      0.3265     0.1285  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_mbw_hid32_d12 --seeds=0,1,2,3,4`
