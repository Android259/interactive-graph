# mlp_s15_nomb_hid64_m8_dpt0

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid64_m8_dpt0'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8472      0.8734      0.9550      0.8863      0.9138      0.8756
ALL                 5      0.8472      0.8734      0.9550      0.8863      0.9138      0.8756

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8718      0.8646     0.0420  5
max valid BA                0.8947      0.9062     0.0380  5
best valid F1               0.8473      0.8485     0.0511  5
test BA                     0.8603      0.8923     0.0528  5
test AUC                    0.9359      0.9442     0.0379  5
test AUC in-protein         0.9387      0.9532     0.0405  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9385      0.9484     0.0481  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8081      0.8462     0.0667  5
test sensitivity            0.8472      0.8958     0.0676  5
test specificity            0.8734      0.8947     0.0507  5
test precision              0.7739      0.8000     0.0740  5
test loss                   0.3043      0.2853     0.0902  5
FPR (FP/(FP+TN))            0.1266      0.1053     0.0507  5
FNR (FN/(FN+TP))            0.1528      0.1042     0.0676  5

=== abs(sensitivity-specificity) gap: mean=0.0312 median=0.0104 n=5 ===
sensitivity std across seeds (by group): mean=0.0676 median=0.0676 n=1
specificity std across seeds (by group): mean=0.0507 median=0.0507 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8718      0.8646     0.0420  5
  max valid BA                0.8947      0.9062     0.0380  5
  best valid F1               0.8473      0.8485     0.0511  5
  test BA                     0.8603      0.8923     0.0528  5
  test AUC                    0.9359      0.9442     0.0379  5
  test AUC in-protein         0.9387      0.9532     0.0405  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9385      0.9484     0.0481  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8081      0.8462     0.0667  5
  test sensitivity            0.8472      0.8958     0.0676  5
  test specificity            0.8734      0.8947     0.0507  5
  test precision              0.7739      0.8000     0.0740  5
  test loss                   0.3043      0.2853     0.0902  5
  FPR (FP/(FP+TN))            0.1266      0.1053     0.0507  5
  FNR (FN/(FN+TP))            0.1528      0.1042     0.0676  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid64_m8_dpt0 --seeds=0,1,2,3,4`
