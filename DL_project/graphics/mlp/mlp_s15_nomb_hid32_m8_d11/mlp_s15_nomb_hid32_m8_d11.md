# mlp_s15_nomb_hid32_m8_d11

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid32_m8_d11'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8306      0.7778      0.8485      0.7645      0.8718      0.7782
ALL                 5      0.8306      0.7778      0.8485      0.7645      0.8718      0.7782

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8156      0.8073     0.0482  5
max valid BA                0.8250      0.8177     0.0411  5
best valid F1               0.7537      0.7525     0.0459  5
test BA                     0.8042      0.7946     0.0295  5
test AUC                    0.8784      0.8728     0.0366  5
test AUC in-protein         0.8604      0.8718     0.0649  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.8673      0.8445     0.0526  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7320      0.7179     0.0371  5
test sensitivity            0.8306      0.8333     0.0264  5
test specificity            0.7778      0.7526     0.0473  5
test precision              0.6556      0.6190     0.0520  5
test loss                   0.4328      0.4537     0.0516  5
FPR (FP/(FP+TN))            0.2222      0.2474     0.0473  5
FNR (FN/(FN+TP))            0.1694      0.1667     0.0264  5

=== abs(sensitivity-specificity) gap: mean=0.0570 median=0.0436 n=5 ===
sensitivity std across seeds (by group): mean=0.0264 median=0.0264 n=1
specificity std across seeds (by group): mean=0.0473 median=0.0473 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8156      0.8073     0.0482  5
  max valid BA                0.8250      0.8177     0.0411  5
  best valid F1               0.7537      0.7525     0.0459  5
  test BA                     0.8042      0.7946     0.0295  5
  test AUC                    0.8784      0.8728     0.0366  5
  test AUC in-protein         0.8604      0.8718     0.0649  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.8673      0.8445     0.0526  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7320      0.7179     0.0371  5
  test sensitivity            0.8306      0.8333     0.0264  5
  test specificity            0.7778      0.7526     0.0473  5
  test precision              0.6556      0.6190     0.0520  5
  test loss                   0.4328      0.4537     0.0516  5
  FPR (FP/(FP+TN))            0.2222      0.2474     0.0473  5
  FNR (FN/(FN+TP))            0.1694      0.1667     0.0264  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid32_m8_d11 --seeds=0,1,2,3,4`
