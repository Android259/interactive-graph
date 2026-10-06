# mlp_s15_nomb_hid128_dpt0

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid128_dpt0'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8352      0.8714      0.9572      0.8889      0.9220      0.8715
ALL                 5      0.8352      0.8714      0.9572      0.8889      0.9220      0.8715

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8739      0.8698     0.0492  5
max valid BA                0.8967      0.9062     0.0401  5
best valid F1               0.8489      0.8468     0.0541  5
test BA                     0.8533      0.8617     0.0781  5
test AUC                    0.9309      0.9417     0.0492  5
test AUC in-protein         0.9379      0.9407     0.0453  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9365      0.9484     0.0475  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8004      0.8119     0.0984  5
test sensitivity            0.8352      0.8367     0.0947  5
test specificity            0.8714      0.8866     0.0685  5
test precision              0.7697      0.7885     0.1051  5
test loss                   0.3121      0.2875     0.1198  5
FPR (FP/(FP+TN))            0.1286      0.1134     0.0685  5
FNR (FN/(FN+TP))            0.1648      0.1633     0.0947  5

=== abs(sensitivity-specificity) gap: mean=0.0491 median=0.0383 n=5 ===
sensitivity std across seeds (by group): mean=0.0947 median=0.0947 n=1
specificity std across seeds (by group): mean=0.0685 median=0.0685 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8739      0.8698     0.0492  5
  max valid BA                0.8967      0.9062     0.0401  5
  best valid F1               0.8489      0.8468     0.0541  5
  test BA                     0.8533      0.8617     0.0781  5
  test AUC                    0.9309      0.9417     0.0492  5
  test AUC in-protein         0.9379      0.9407     0.0453  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9365      0.9484     0.0475  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8004      0.8119     0.0984  5
  test sensitivity            0.8352      0.8367     0.0947  5
  test specificity            0.8714      0.8866     0.0685  5
  test precision              0.7697      0.7885     0.1051  5
  test loss                   0.3121      0.2875     0.1198  5
  FPR (FP/(FP+TN))            0.1286      0.1134     0.0685  5
  FNR (FN/(FN+TP))            0.1648      0.1633     0.0947  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid128_dpt0 --seeds=0,1,2,3,4`
