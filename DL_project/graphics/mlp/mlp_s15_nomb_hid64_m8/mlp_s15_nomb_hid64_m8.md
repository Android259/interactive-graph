# mlp_s15_nomb_hid64_m8

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid64_m8'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8679      0.8590      0.9397      0.8641      0.9178      0.8653
ALL                 5      0.8679      0.8590      0.9397      0.8641      0.9178      0.8653

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8864      0.8888     0.0418  5
max valid BA                0.8916      0.8888     0.0391  5
best valid F1               0.8435      0.8515     0.0582  5
test BA                     0.8634      0.8566     0.0540  5
test AUC                    0.9311      0.9414     0.0454  5
test AUC in-protein         0.9289      0.9458     0.0479  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9273      0.9495     0.0480  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8120      0.8081     0.0699  5
test sensitivity            0.8679      0.8750     0.0663  5
test specificity            0.8590      0.8969     0.1002  5
test precision              0.7709      0.8000     0.1052  5
test loss                   0.3156      0.2888     0.1180  5
FPR (FP/(FP+TN))            0.1410      0.1031     0.1002  5
FNR (FN/(FN+TP))            0.1321      0.1250     0.0663  5

=== abs(sensitivity-specificity) gap: mean=0.0994 median=0.0806 n=5 ===
sensitivity std across seeds (by group): mean=0.0663 median=0.0663 n=1
specificity std across seeds (by group): mean=0.1002 median=0.1002 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8864      0.8888     0.0418  5
  max valid BA                0.8916      0.8888     0.0391  5
  best valid F1               0.8435      0.8515     0.0582  5
  test BA                     0.8634      0.8566     0.0540  5
  test AUC                    0.9311      0.9414     0.0454  5
  test AUC in-protein         0.9289      0.9458     0.0479  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9273      0.9495     0.0480  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8120      0.8081     0.0699  5
  test sensitivity            0.8679      0.8750     0.0663  5
  test specificity            0.8590      0.8969     0.1002  5
  test precision              0.7709      0.8000     0.1052  5
  test loss                   0.3156      0.2888     0.1180  5
  FPR (FP/(FP+TN))            0.1410      0.1031     0.1002  5
  FNR (FN/(FN+TP))            0.1321      0.1250     0.0663  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid64_m8 --seeds=0,1,2,3,4`
