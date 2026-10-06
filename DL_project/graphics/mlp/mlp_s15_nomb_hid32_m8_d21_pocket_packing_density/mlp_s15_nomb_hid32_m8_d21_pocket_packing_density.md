# mlp_s15_nomb_hid32_m8_d21_pocket_packing_density

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid32_m8_d21_pocket_packing_density'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8390      0.8401      0.9032      0.8254      0.8848      0.8342
ALL                 5      0.8390      0.8401      0.9032      0.8254      0.8848      0.8342

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8478      0.8646     0.0559  5
max valid BA                0.8595      0.8750     0.0507  5
best valid F1               0.7998      0.8070     0.0635  5
test BA                     0.8396      0.8563     0.0496  5
test AUC                    0.9195      0.9303     0.0384  5
test AUC in-protein         0.9164      0.9172     0.0334  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9129      0.9202     0.0438  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7790      0.7963     0.0617  5
test sensitivity            0.8390      0.8542     0.0563  5
test specificity            0.8401      0.8421     0.0492  5
test precision              0.7279      0.7288     0.0703  5
test loss                   0.3451      0.3318     0.0638  5
FPR (FP/(FP+TN))            0.1599      0.1579     0.0492  5
FNR (FN/(FN+TP))            0.1610      0.1458     0.0563  5

=== abs(sensitivity-specificity) gap: mean=0.0306 median=0.0312 n=5 ===
sensitivity std across seeds (by group): mean=0.0563 median=0.0563 n=1
specificity std across seeds (by group): mean=0.0492 median=0.0492 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8478      0.8646     0.0559  5
  max valid BA                0.8595      0.8750     0.0507  5
  best valid F1               0.7998      0.8070     0.0635  5
  test BA                     0.8396      0.8563     0.0496  5
  test AUC                    0.9195      0.9303     0.0384  5
  test AUC in-protein         0.9164      0.9172     0.0334  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9129      0.9202     0.0438  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7790      0.7963     0.0617  5
  test sensitivity            0.8390      0.8542     0.0563  5
  test specificity            0.8401      0.8421     0.0492  5
  test precision              0.7279      0.7288     0.0703  5
  test loss                   0.3451      0.3318     0.0638  5
  FPR (FP/(FP+TN))            0.1599      0.1579     0.0492  5
  FNR (FN/(FN+TP))            0.1610      0.1458     0.0563  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid32_m8_d21_pocket_packing_density --seeds=0,1,2,3,4`
