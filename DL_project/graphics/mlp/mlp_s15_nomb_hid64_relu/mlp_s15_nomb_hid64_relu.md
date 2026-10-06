# mlp_s15_nomb_hid64_relu

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid64_relu'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8929      0.8588      0.9293      0.8596      0.9260      0.8569
ALL                 5      0.8929      0.8588      0.9293      0.8596      0.9260      0.8569

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8831      0.8985     0.0463  5
max valid BA                0.8915      0.9039     0.0402  5
best valid F1               0.8433      0.8713     0.0594  5
test BA                     0.8759      0.8906     0.0529  5
test AUC                    0.9401      0.9541     0.0371  5
test AUC in-protein         0.9407      0.9594     0.0376  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9367      0.9536     0.0403  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8243      0.8431     0.0677  5
test sensitivity            0.8929      0.8958     0.0386  5
test specificity            0.8588      0.8854     0.0720  5
test precision              0.7677      0.7963     0.0889  5
test loss                   0.2974      0.2620     0.0906  5
FPR (FP/(FP+TN))            0.1412      0.1146     0.0720  5
FNR (FN/(FN+TP))            0.1071      0.1042     0.0386  5

=== abs(sensitivity-specificity) gap: mean=0.0418 median=0.0312 n=5 ===
sensitivity std across seeds (by group): mean=0.0386 median=0.0386 n=1
specificity std across seeds (by group): mean=0.0720 median=0.0720 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8831      0.8985     0.0463  5
  max valid BA                0.8915      0.9039     0.0402  5
  best valid F1               0.8433      0.8713     0.0594  5
  test BA                     0.8759      0.8906     0.0529  5
  test AUC                    0.9401      0.9541     0.0371  5
  test AUC in-protein         0.9407      0.9594     0.0376  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9367      0.9536     0.0403  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8243      0.8431     0.0677  5
  test sensitivity            0.8929      0.8958     0.0386  5
  test specificity            0.8588      0.8854     0.0720  5
  test precision              0.7677      0.7963     0.0889  5
  test loss                   0.2974      0.2620     0.0906  5
  FPR (FP/(FP+TN))            0.1412      0.1146     0.0720  5
  FNR (FN/(FN+TP))            0.1071      0.1042     0.0386  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid64_relu --seeds=0,1,2,3,4`
