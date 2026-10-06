# mlp_s15_nomb_hid64_pu01_subclass

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid64_pu01_subclass'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.4168      0.9441      0.4839      0.9412      0.6322      0.9171
ALL                 5      0.4168      0.9441      0.4839      0.9412      0.6322      0.9171

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.7540      0.7794     0.0421  5
max valid BA                0.7746      0.7812     0.0533  5
best valid F1               0.7054      0.7160     0.0775  5
test BA                     0.6804      0.6875     0.0365  5
test AUC                    0.8900      0.8987     0.0395  5
test AUC in-protein         0.8927      0.9053     0.0258  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.8898      0.8814     0.0359  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.5417      0.5652     0.0779  5
test sensitivity            0.4168      0.4375     0.0951  5
test specificity            0.9441      0.9691     0.0669  5
test precision              0.8230      0.8800     0.1283  5
test loss                   0.3776      0.3714     0.0191  5
FPR (FP/(FP+TN))            0.0559      0.0309     0.0669  5
FNR (FN/(FN+TP))            0.5832      0.5625     0.0951  5

=== abs(sensitivity-specificity) gap: mean=0.5274 median=0.5414 n=5 ===
sensitivity std across seeds (by group): mean=0.0951 median=0.0951 n=1
specificity std across seeds (by group): mean=0.0669 median=0.0669 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7540      0.7794     0.0421  5
  max valid BA                0.7746      0.7812     0.0533  5
  best valid F1               0.7054      0.7160     0.0775  5
  test BA                     0.6804      0.6875     0.0365  5
  test AUC                    0.8900      0.8987     0.0395  5
  test AUC in-protein         0.8927      0.9053     0.0258  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.8898      0.8814     0.0359  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.5417      0.5652     0.0779  5
  test sensitivity            0.4168      0.4375     0.0951  5
  test specificity            0.9441      0.9691     0.0669  5
  test precision              0.8230      0.8800     0.1283  5
  test loss                   0.3776      0.3714     0.0191  5
  FPR (FP/(FP+TN))            0.0559      0.0309     0.0669  5
  FNR (FN/(FN+TP))            0.5832      0.5625     0.0951  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid64_pu01_subclass --seeds=0,1,2,3,4`
