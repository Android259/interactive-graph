# mlp_s15_nomb_hid32_m8_d21_experimental_lipid_volume

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid32_m8_d21_experimental_lipid_volume'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8268      0.8462      0.8865      0.8196      0.8842      0.8260
ALL                 5      0.8268      0.8462      0.8865      0.8196      0.8842      0.8260

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8377      0.8438     0.0541  5
max valid BA                0.8551      0.8594     0.0521  5
best valid F1               0.7947      0.7928     0.0678  5
test BA                     0.8365      0.8438     0.0394  5
test AUC                    0.9057      0.9219     0.0402  5
test AUC in-protein         0.8989      0.8880     0.0288  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.8952      0.9021     0.0218  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7766      0.7879     0.0499  5
test sensitivity            0.8268      0.8333     0.0409  5
test specificity            0.8462      0.8542     0.0505  5
test precision              0.7338      0.7407     0.0661  5
test loss                   0.3748      0.3463     0.0657  5
FPR (FP/(FP+TN))            0.1538      0.1458     0.0505  5
FNR (FN/(FN+TP))            0.1732      0.1667     0.0409  5

=== abs(sensitivity-specificity) gap: mean=0.0377 median=0.0312 n=5 ===
sensitivity std across seeds (by group): mean=0.0409 median=0.0409 n=1
specificity std across seeds (by group): mean=0.0505 median=0.0505 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8377      0.8438     0.0541  5
  max valid BA                0.8551      0.8594     0.0521  5
  best valid F1               0.7947      0.7928     0.0678  5
  test BA                     0.8365      0.8438     0.0394  5
  test AUC                    0.9057      0.9219     0.0402  5
  test AUC in-protein         0.8989      0.8880     0.0288  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.8952      0.9021     0.0218  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7766      0.7879     0.0499  5
  test sensitivity            0.8268      0.8333     0.0409  5
  test specificity            0.8462      0.8542     0.0505  5
  test precision              0.7338      0.7407     0.0661  5
  test loss                   0.3748      0.3463     0.0657  5
  FPR (FP/(FP+TN))            0.1538      0.1458     0.0505  5
  FNR (FN/(FN+TP))            0.1732      0.1667     0.0409  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid32_m8_d21_experimental_lipid_volume --seeds=0,1,2,3,4`
