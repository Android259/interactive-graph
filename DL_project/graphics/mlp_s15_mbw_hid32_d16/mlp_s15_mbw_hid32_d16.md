# mlp_s15_mbw_hid32_d16

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_mbw_hid32_d16'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.7647      0.7465      0.7616      0.7344      0.8013      0.7331
ALL                 5      0.7647      0.7465      0.7616      0.7344      0.8013      0.7331

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.7547      0.7392     0.0324  5
max valid BA                0.7672      0.7549     0.0259  5
best valid F1               0.5459      0.5470     0.0313  5
test BA                     0.7556      0.7576     0.0417  5
test AUC                    0.8224      0.8227     0.0386  5
test AUC in-protein         0.8198      0.8120     0.0554  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.8337      0.8407     0.0360  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.5349      0.5248     0.0582  5
test sensitivity            0.7647      0.7708     0.0353  5
test specificity            0.7465      0.7443     0.0493  5
test precision              0.4124      0.3978     0.0602  5
test loss                   0.4884      0.5030     0.0485  5
FPR (FP/(FP+TN))            0.2535      0.2557     0.0493  5
FNR (FN/(FN+TP))            0.2353      0.2292     0.0353  5

=== abs(sensitivity-specificity) gap: mean=0.0204 median=0.0253 n=5 ===
sensitivity std across seeds (by group): mean=0.0353 median=0.0353 n=1
specificity std across seeds (by group): mean=0.0493 median=0.0493 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7547      0.7392     0.0324  5
  max valid BA                0.7672      0.7549     0.0259  5
  best valid F1               0.5459      0.5470     0.0313  5
  test BA                     0.7556      0.7576     0.0417  5
  test AUC                    0.8224      0.8227     0.0386  5
  test AUC in-protein         0.8198      0.8120     0.0554  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.8337      0.8407     0.0360  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.5349      0.5248     0.0582  5
  test sensitivity            0.7647      0.7708     0.0353  5
  test specificity            0.7465      0.7443     0.0493  5
  test precision              0.4124      0.3978     0.0602  5
  test loss                   0.4884      0.5030     0.0485  5
  FPR (FP/(FP+TN))            0.2535      0.2557     0.0493  5
  FNR (FN/(FN+TP))            0.2353      0.2292     0.0353  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_mbw_hid32_d16 --seeds=0,1,2,3,4`
