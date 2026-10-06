# mlp_s15_nomb_hid64_ep360

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid64_ep360'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.9048      0.8568      0.9542      0.8889      0.9343      0.8777
ALL                 5      0.9048      0.8568      0.9542      0.8889      0.9343      0.8777

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8904      0.8933     0.0497  5
max valid BA                0.9060      0.9039     0.0366  5
best valid F1               0.8604      0.8713     0.0540  5
test BA                     0.8808      0.8923     0.0294  5
test AUC                    0.9443      0.9541     0.0262  5
test AUC in-protein         0.9424      0.9524     0.0288  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9417      0.9558     0.0371  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8286      0.8462     0.0408  5
test sensitivity            0.9048      0.9167     0.0434  5
test specificity            0.8568      0.8854     0.0708  5
test precision              0.7689      0.8000     0.0735  5
test loss                   0.2967      0.2575     0.0831  5
FPR (FP/(FP+TN))            0.1432      0.1146     0.0708  5
FNR (FN/(FN+TP))            0.0952      0.0833     0.0434  5

=== abs(sensitivity-specificity) gap: mean=0.0772 median=0.0521 n=5 ===
sensitivity std across seeds (by group): mean=0.0434 median=0.0434 n=1
specificity std across seeds (by group): mean=0.0708 median=0.0708 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8904      0.8933     0.0497  5
  max valid BA                0.9060      0.9039     0.0366  5
  best valid F1               0.8604      0.8713     0.0540  5
  test BA                     0.8808      0.8923     0.0294  5
  test AUC                    0.9443      0.9541     0.0262  5
  test AUC in-protein         0.9424      0.9524     0.0288  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9417      0.9558     0.0371  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8286      0.8462     0.0408  5
  test sensitivity            0.9048      0.9167     0.0434  5
  test specificity            0.8568      0.8854     0.0708  5
  test precision              0.7689      0.8000     0.0735  5
  test loss                   0.2967      0.2575     0.0831  5
  FPR (FP/(FP+TN))            0.1432      0.1146     0.0708  5
  FNR (FN/(FN+TP))            0.0952      0.0833     0.0434  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid64_ep360 --seeds=0,1,2,3,4`
