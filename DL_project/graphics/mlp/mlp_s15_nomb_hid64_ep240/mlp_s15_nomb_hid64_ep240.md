# mlp_s15_nomb_hid64_ep240

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid64_ep240'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8515      0.8733      0.9427      0.8766      0.9218      0.8798
ALL                 5      0.8515      0.8733      0.9427      0.8766      0.9218      0.8798

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8894      0.8833     0.0393  5
max valid BA                0.9008      0.9010     0.0414  5
best valid F1               0.8555      0.8627     0.0577  5
test BA                     0.8624      0.8771     0.0514  5
test AUC                    0.9400      0.9491     0.0315  5
test AUC in-protein         0.9379      0.9429     0.0272  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9340      0.9558     0.0345  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8123      0.8367     0.0672  5
test sensitivity            0.8515      0.8367     0.0459  5
test specificity            0.8733      0.8958     0.0706  5
test precision              0.7797      0.8000     0.0942  5
test loss                   0.2958      0.2591     0.0843  5
FPR (FP/(FP+TN))            0.1267      0.1042     0.0706  5
FNR (FN/(FN+TP))            0.1485      0.1633     0.0459  5

=== abs(sensitivity-specificity) gap: mean=0.0563 median=0.0521 n=5 ===
sensitivity std across seeds (by group): mean=0.0459 median=0.0459 n=1
specificity std across seeds (by group): mean=0.0706 median=0.0706 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8894      0.8833     0.0393  5
  max valid BA                0.9008      0.9010     0.0414  5
  best valid F1               0.8555      0.8627     0.0577  5
  test BA                     0.8624      0.8771     0.0514  5
  test AUC                    0.9400      0.9491     0.0315  5
  test AUC in-protein         0.9379      0.9429     0.0272  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9340      0.9558     0.0345  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8123      0.8367     0.0672  5
  test sensitivity            0.8515      0.8367     0.0459  5
  test specificity            0.8733      0.8958     0.0706  5
  test precision              0.7797      0.8000     0.0942  5
  test loss                   0.2958      0.2591     0.0843  5
  FPR (FP/(FP+TN))            0.1267      0.1042     0.0706  5
  FNR (FN/(FN+TP))            0.1485      0.1633     0.0459  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid64_ep240 --seeds=0,1,2,3,4`
