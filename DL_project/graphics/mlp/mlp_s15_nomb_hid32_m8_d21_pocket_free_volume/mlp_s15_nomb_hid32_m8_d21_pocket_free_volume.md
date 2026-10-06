# mlp_s15_nomb_hid32_m8_d21_pocket_free_volume

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid32_m8_d21_pocket_free_volume'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8598      0.8546      0.8950      0.8194      0.8970      0.8156
ALL                 5      0.8598      0.8546      0.8950      0.8194      0.8970      0.8156

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8449      0.8490     0.0542  5
max valid BA                0.8563      0.8542     0.0449  5
best valid F1               0.7962      0.7857     0.0599  5
test BA                     0.8572      0.8690     0.0552  5
test AUC                    0.9225      0.9404     0.0415  5
test AUC in-protein         0.9148      0.9120     0.0371  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9138      0.9244     0.0462  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8013      0.8163     0.0692  5
test sensitivity            0.8598      0.8958     0.0664  5
test specificity            0.8546      0.8557     0.0528  5
test precision              0.7515      0.7586     0.0777  5
test loss                   0.3456      0.3262     0.0688  5
FPR (FP/(FP+TN))            0.1454      0.1443     0.0528  5
FNR (FN/(FN+TP))            0.1402      0.1042     0.0664  5

=== abs(sensitivity-specificity) gap: mean=0.0374 median=0.0423 n=5 ===
sensitivity std across seeds (by group): mean=0.0664 median=0.0664 n=1
specificity std across seeds (by group): mean=0.0528 median=0.0528 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8449      0.8490     0.0542  5
  max valid BA                0.8563      0.8542     0.0449  5
  best valid F1               0.7962      0.7857     0.0599  5
  test BA                     0.8572      0.8690     0.0552  5
  test AUC                    0.9225      0.9404     0.0415  5
  test AUC in-protein         0.9148      0.9120     0.0371  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9138      0.9244     0.0462  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8013      0.8163     0.0692  5
  test sensitivity            0.8598      0.8958     0.0664  5
  test specificity            0.8546      0.8557     0.0528  5
  test precision              0.7515      0.7586     0.0777  5
  test loss                   0.3456      0.3262     0.0688  5
  FPR (FP/(FP+TN))            0.1454      0.1443     0.0528  5
  FNR (FN/(FN+TP))            0.1402      0.1042     0.0664  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid32_m8_d21_pocket_free_volume --seeds=0,1,2,3,4`
