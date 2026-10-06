# deepclip_start_warm_ep120

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'deepclip_start_warm_ep120'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group           n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_start    5      0.6923      0.7615      0.6545      0.5980      0.7001      0.6769
ALL             5      0.6923      0.7615      0.6545      0.5980      0.7001      0.6769

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6747      0.6833     0.0820  5
max valid BA                0.6885      0.6833     0.0615  5
best valid F1               0.5985      0.5714     0.0926  5
test BA                     0.7269      0.7549     0.0632  5
test AUC                    0.8095      0.8095     0.0874  5
test AUC in-protein         0.8346      0.8273     0.0767  5
  (proteins averaged)       2.0000      2.0000     0.0000  5
test AUC in-protein (pairs)      0.8061      0.8037     0.0807  5
  (proteins contributing)      3.0000      3.0000     0.0000  5
test F1                     0.6529      0.6667     0.0635  5
test sensitivity            0.6923      0.6364     0.0963  5
test specificity            0.7615      0.7826     0.1192  5
test precision              0.6281      0.6154     0.0992  5
test loss                   0.6148      0.6749     0.1258  5
FPR (FP/(FP+TN))            0.2385      0.2174     0.1192  5
FNR (FN/(FN+TP))            0.3077      0.3636     0.0963  5

=== abs(sensitivity-specificity) gap: mean=0.1410 median=0.1795 n=5 ===
sensitivity std across seeds (by group): mean=0.0963 median=0.0963 n=1
specificity std across seeds (by group): mean=0.1192 median=0.1192 n=1

=== By group ===
groups_start (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6747      0.6833     0.0820  5
  max valid BA                0.6885      0.6833     0.0615  5
  best valid F1               0.5985      0.5714     0.0926  5
  test BA                     0.7269      0.7549     0.0632  5
  test AUC                    0.8095      0.8095     0.0874  5
  test AUC in-protein         0.8346      0.8273     0.0767  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.8061      0.8037     0.0807  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.6529      0.6667     0.0635  5
  test sensitivity            0.6923      0.6364     0.0963  5
  test specificity            0.7615      0.7826     0.1192  5
  test precision              0.6281      0.6154     0.0992  5
  test loss                   0.6148      0.6749     0.1258  5
  FPR (FP/(FP+TN))            0.2385      0.2174     0.1192  5
  FNR (FN/(FN+TP))            0.3077      0.3636     0.0963  5
```

## AUC vs chemistry null model, in-sample increment

Failed: start/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label deepclip_start_warm_ep120 --seeds=0,1,2,3,4`
