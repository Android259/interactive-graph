# mlp_s15_nomb_hid64_pu005

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid64_pu005'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.7896      0.8879      0.8641      0.8915      0.8763      0.8881
ALL                 5      0.7896      0.8879      0.8641      0.8915      0.8763      0.8881

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8686      0.8785     0.0504  5
max valid BA                0.8822      0.8958     0.0408  5
best valid F1               0.8373      0.8462     0.0584  5
test BA                     0.8387      0.8490     0.0471  5
test AUC                    0.9357      0.9489     0.0411  5
test AUC in-protein         0.9406      0.9573     0.0398  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9430      0.9628     0.0434  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7856      0.8041     0.0614  5
test sensitivity            0.7896      0.7755     0.0592  5
test specificity            0.8879      0.8958     0.0488  5
test precision              0.7838      0.8077     0.0777  5
test loss                   0.3051      0.2866     0.0919  5
FPR (FP/(FP+TN))            0.1121      0.1042     0.0488  5
FNR (FN/(FN+TP))            0.2104      0.2245     0.0592  5

=== abs(sensitivity-specificity) gap: mean=0.0982 median=0.0898 n=5 ===
sensitivity std across seeds (by group): mean=0.0592 median=0.0592 n=1
specificity std across seeds (by group): mean=0.0488 median=0.0488 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8686      0.8785     0.0504  5
  max valid BA                0.8822      0.8958     0.0408  5
  best valid F1               0.8373      0.8462     0.0584  5
  test BA                     0.8387      0.8490     0.0471  5
  test AUC                    0.9357      0.9489     0.0411  5
  test AUC in-protein         0.9406      0.9573     0.0398  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9430      0.9628     0.0434  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7856      0.8041     0.0614  5
  test sensitivity            0.7896      0.7755     0.0592  5
  test specificity            0.8879      0.8958     0.0488  5
  test precision              0.7838      0.8077     0.0777  5
  test loss                   0.3051      0.2866     0.0919  5
  FPR (FP/(FP+TN))            0.1121      0.1042     0.0488  5
  FNR (FN/(FN+TP))            0.2104      0.2245     0.0592  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid64_pu005 --seeds=0,1,2,3,4`
