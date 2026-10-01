# ge_s15_prothid32_hid64_noreg_attnpool

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'ge_s15_prothid32_hid64_noreg_attnpool'
rows: 4

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    4      0.8551      0.9039      0.9586      0.8905      0.9479      0.8781
ALL                 4      0.8551      0.9039      0.9586      0.8905      0.9479      0.8781

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8974      0.9010     0.0317  4
max valid BA                0.9130      0.9245     0.0323  4
best valid F1               0.8698      0.8868     0.0447  4
test BA                     0.8795      0.8906     0.0509  4
test AUC                    0.9476      0.9680     0.0502  4
test AUC in-protein         0.9386      0.9554     0.0429  4
  (proteins averaged)       9.2500      9.0000     1.5000  4
test AUC in-protein (pairs)      0.9512      0.9622     0.0369  4
  (proteins contributing)     19.7500     20.0000     1.5000  4
test F1                     0.8378      0.8597     0.0675  4
test sensitivity            0.8551      0.8457     0.0651  4
test specificity            0.9039      0.9266     0.0688  4
test precision              0.8267      0.8620     0.1017  4
test loss                   0.3563      0.2625     0.2274  4
FPR (FP/(FP+TN))            0.0961      0.0734     0.0688  4
FNR (FN/(FN+TP))            0.1449      0.1543     0.0651  4

=== abs(sensitivity-specificity) gap: mean=0.0658 median=0.0421 n=4 ===
sensitivity std across seeds (by group): mean=0.0651 median=0.0651 n=1
specificity std across seeds (by group): mean=0.0688 median=0.0688 n=1

=== By group ===
groups_species15 (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8974      0.9010     0.0317  4
  max valid BA                0.9130      0.9245     0.0323  4
  best valid F1               0.8698      0.8868     0.0447  4
  test BA                     0.8795      0.8906     0.0509  4
  test AUC                    0.9476      0.9680     0.0502  4
  test AUC in-protein         0.9386      0.9554     0.0429  4
    (proteins averaged)       9.2500      9.0000     1.5000  4
  test AUC in-protein (pairs)      0.9512      0.9622     0.0369  4
    (proteins contributing)     19.7500     20.0000     1.5000  4
  test F1                     0.8378      0.8597     0.0675  4
  test sensitivity            0.8551      0.8457     0.0651  4
  test specificity            0.9039      0.9266     0.0688  4
  test precision              0.8267      0.8620     0.1017  4
  test loss                   0.3563      0.2625     0.2274  4
  FPR (FP/(FP+TN))            0.0961      0.0734     0.0688  4
  FNR (FN/(FN+TP))            0.1449      0.1543     0.0651  4
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_attnpool --seeds=0,1,2,3,4`
