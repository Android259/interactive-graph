# mlp_s15_nomb_hid64_3mlp

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid64_3mlp'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8845      0.8610      0.9337      0.8619      0.9137      0.8674
ALL                 5      0.8845      0.8610      0.9337      0.8619      0.9137      0.8674

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8738      0.8594     0.0425  5
max valid BA                0.8905      0.8906     0.0377  5
best valid F1               0.8418      0.8350     0.0560  5
test BA                     0.8728      0.8953     0.0692  5
test AUC                    0.9303      0.9428     0.0433  5
test AUC in-protein         0.9287      0.9509     0.0488  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9236      0.9495     0.0543  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8220      0.8515     0.0886  5
test sensitivity            0.8845      0.8958     0.0635  5
test specificity            0.8610      0.8660     0.0797  5
test precision              0.7701      0.7797     0.1110  5
test loss                   0.3086      0.2840     0.0901  5
FPR (FP/(FP+TN))            0.1390      0.1340     0.0797  5
FNR (FN/(FN+TP))            0.1155      0.1042     0.0635  5

=== abs(sensitivity-specificity) gap: mean=0.0360 median=0.0312 n=5 ===
sensitivity std across seeds (by group): mean=0.0635 median=0.0635 n=1
specificity std across seeds (by group): mean=0.0797 median=0.0797 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8738      0.8594     0.0425  5
  max valid BA                0.8905      0.8906     0.0377  5
  best valid F1               0.8418      0.8350     0.0560  5
  test BA                     0.8728      0.8953     0.0692  5
  test AUC                    0.9303      0.9428     0.0433  5
  test AUC in-protein         0.9287      0.9509     0.0488  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9236      0.9495     0.0543  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8220      0.8515     0.0886  5
  test sensitivity            0.8845      0.8958     0.0635  5
  test specificity            0.8610      0.8660     0.0797  5
  test precision              0.7701      0.7797     0.1110  5
  test loss                   0.3086      0.2840     0.0901  5
  FPR (FP/(FP+TN))            0.1390      0.1340     0.0797  5
  FNR (FN/(FN+TP))            0.1155      0.1042     0.0635  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid64_3mlp --seeds=0,1,2,3,4`
