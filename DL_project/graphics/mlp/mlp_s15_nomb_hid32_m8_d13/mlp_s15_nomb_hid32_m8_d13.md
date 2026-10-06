# mlp_s15_nomb_hid32_m8_d13

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid32_m8_d13'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8265      0.7884      0.8440      0.7298      0.8965      0.7450
ALL                 5      0.8265      0.7884      0.8440      0.7298      0.8965      0.7450

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8115      0.8005     0.0567  5
max valid BA                0.8207      0.8105     0.0518  5
best valid F1               0.7483      0.7360     0.0632  5
test BA                     0.8074      0.8021     0.0417  5
test AUC                    0.8897      0.8828     0.0454  5
test AUC in-protein         0.8646      0.8798     0.0808  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.8758      0.8655     0.0595  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.7372      0.7290     0.0525  5
test sensitivity            0.8265      0.8125     0.0396  5
test specificity            0.7884      0.7917     0.0626  5
test precision              0.6674      0.6610     0.0702  5
test loss                   0.4112      0.4300     0.0648  5
FPR (FP/(FP+TN))            0.2116      0.2083     0.0626  5
FNR (FN/(FN+TP))            0.1735      0.1875     0.0396  5

=== abs(sensitivity-specificity) gap: mean=0.0465 median=0.0208 n=5 ===
sensitivity std across seeds (by group): mean=0.0396 median=0.0396 n=1
specificity std across seeds (by group): mean=0.0626 median=0.0626 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8115      0.8005     0.0567  5
  max valid BA                0.8207      0.8105     0.0518  5
  best valid F1               0.7483      0.7360     0.0632  5
  test BA                     0.8074      0.8021     0.0417  5
  test AUC                    0.8897      0.8828     0.0454  5
  test AUC in-protein         0.8646      0.8798     0.0808  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.8758      0.8655     0.0595  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.7372      0.7290     0.0525  5
  test sensitivity            0.8265      0.8125     0.0396  5
  test specificity            0.7884      0.7917     0.0626  5
  test precision              0.6674      0.6610     0.0702  5
  test loss                   0.4112      0.4300     0.0648  5
  FPR (FP/(FP+TN))            0.2116      0.2083     0.0626  5
  FNR (FN/(FN+TP))            0.1735      0.1875     0.0396  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid32_m8_d13 --seeds=0,1,2,3,4`
