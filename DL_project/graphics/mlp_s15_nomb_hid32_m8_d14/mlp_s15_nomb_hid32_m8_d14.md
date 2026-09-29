# mlp_s15_nomb_hid32_m8_d14

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid32_m8_d14'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8305      0.8048      0.8626      0.7742      0.8883      0.7886
ALL                 5      0.8305      0.8048      0.8626      0.7742      0.8883      0.7886

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8218      0.8160     0.0417  5
max valid BA                0.8384      0.8263     0.0429  5
best valid F1               0.7710      0.7563     0.0552  5
test BA                     0.8177      0.8177     0.0266  5
test AUC                    0.8902      0.8944     0.0329  5
test AUC in-protein         0.8706      0.8991     0.0652  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.8658      0.8825     0.0548  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7492      0.7500     0.0333  5
test sensitivity            0.8305      0.8125     0.0340  5
test specificity            0.8048      0.8125     0.0368  5
test precision              0.6833      0.6842     0.0432  5
test loss                   0.4093      0.4162     0.0481  5
FPR (FP/(FP+TN))            0.1952      0.1875     0.0368  5
FNR (FN/(FN+TP))            0.1695      0.1875     0.0340  5

=== abs(sensitivity-specificity) gap: mean=0.0299 median=0.0104 n=5 ===
sensitivity std across seeds (by group): mean=0.0340 median=0.0340 n=1
specificity std across seeds (by group): mean=0.0368 median=0.0368 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8218      0.8160     0.0417  5
  max valid BA                0.8384      0.8263     0.0429  5
  best valid F1               0.7710      0.7563     0.0552  5
  test BA                     0.8177      0.8177     0.0266  5
  test AUC                    0.8902      0.8944     0.0329  5
  test AUC in-protein         0.8706      0.8991     0.0652  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.8658      0.8825     0.0548  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7492      0.7500     0.0333  5
  test sensitivity            0.8305      0.8125     0.0340  5
  test specificity            0.8048      0.8125     0.0368  5
  test precision              0.6833      0.6842     0.0432  5
  test loss                   0.4093      0.4162     0.0481  5
  FPR (FP/(FP+TN))            0.1952      0.1875     0.0368  5
  FNR (FN/(FN+TP))            0.1695      0.1875     0.0340  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid32_m8_d14 --seeds=0,1,2,3,4`
