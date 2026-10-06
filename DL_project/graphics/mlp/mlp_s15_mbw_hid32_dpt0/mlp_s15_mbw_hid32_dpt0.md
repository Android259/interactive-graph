# mlp_s15_mbw_hid32_dpt0

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_mbw_hid32_dpt0'
rows: 3

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    3      0.8213      0.8824      0.8660      0.8680      0.9028      0.9000
ALL                 3      0.8213      0.8824      0.8660      0.8680      0.9028      0.9000

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8762      0.8811     0.0134  3
max valid BA                0.9014      0.8989     0.0125  3
best valid F1               0.7793      0.7706     0.0214  3
test BA                     0.8519      0.8332     0.0669  3
test AUC                    0.9323      0.9339     0.0456  3
test AUC in-protein         0.9007      0.8960     0.0677  3
  (proteins averaged)      15.0000     15.0000     2.0000  3
test AUC in-protein (pairs)      0.9186      0.9353     0.0529  3
  (proteins contributing)     19.3333     19.0000     1.5275  3
test F1                     0.7065      0.6555     0.1149  3
test sensitivity            0.8213      0.8125     0.0913  3
test specificity            0.8824      0.8578     0.0461  3
test precision              0.6222      0.5493     0.1297  3
test loss                   0.3014      0.3474     0.1112  3
FPR (FP/(FP+TN))            0.1176      0.1422     0.0461  3
FNR (FN/(FN+TP))            0.1787      0.1875     0.0913  3

=== abs(sensitivity-specificity) gap: mean=0.0612 median=0.0414 n=3 ===
sensitivity std across seeds (by group): mean=0.0913 median=0.0913 n=1
specificity std across seeds (by group): mean=0.0461 median=0.0461 n=1

=== By group ===
groups_species15 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8762      0.8811     0.0134  3
  max valid BA                0.9014      0.8989     0.0125  3
  best valid F1               0.7793      0.7706     0.0214  3
  test BA                     0.8519      0.8332     0.0669  3
  test AUC                    0.9323      0.9339     0.0456  3
  test AUC in-protein         0.9007      0.8960     0.0677  3
    (proteins averaged)      15.0000     15.0000     2.0000  3
  test AUC in-protein (pairs)      0.9186      0.9353     0.0529  3
    (proteins contributing)     19.3333     19.0000     1.5275  3
  test F1                     0.7065      0.6555     0.1149  3
  test sensitivity            0.8213      0.8125     0.0913  3
  test specificity            0.8824      0.8578     0.0461  3
  test precision              0.6222      0.5493     0.1297  3
  test loss                   0.3014      0.3474     0.1112  3
  FPR (FP/(FP+TN))            0.1176      0.1422     0.0461  3
  FNR (FN/(FN+TP))            0.1787      0.1875     0.0913  3
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_mbw_hid32_dpt0 --seeds=0,1,2,3,4`
