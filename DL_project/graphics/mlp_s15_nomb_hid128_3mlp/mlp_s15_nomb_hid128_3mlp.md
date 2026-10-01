# mlp_s15_nomb_hid128_3mlp

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_nomb_hid128_3mlp'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.9094      0.8589      0.9337      0.8645      0.9220      0.8674
ALL                 5      0.9094      0.8589      0.9337      0.8645      0.9220      0.8674

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8801      0.8906     0.0388  5
max valid BA                0.8947      0.9010     0.0384  5
best valid F1               0.8462      0.8440     0.0550  5
test BA                     0.8841      0.9010     0.0447  5
test AUC                    0.9371      0.9495     0.0304  5
test AUC in-protein         0.9425      0.9455     0.0224  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9422      0.9464     0.0316  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8324      0.8491     0.0581  5
test sensitivity            0.9094      0.9167     0.0335  5
test specificity            0.8589      0.8646     0.0584  5
test precision              0.7688      0.7759     0.0760  5
test loss                   0.3040      0.2659     0.0752  5
FPR (FP/(FP+TN))            0.1411      0.1354     0.0584  5
FNR (FN/(FN+TP))            0.0906      0.0833     0.0335  5

=== abs(sensitivity-specificity) gap: mean=0.0504 median=0.0423 n=5 ===
sensitivity std across seeds (by group): mean=0.0335 median=0.0335 n=1
specificity std across seeds (by group): mean=0.0584 median=0.0584 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8801      0.8906     0.0388  5
  max valid BA                0.8947      0.9010     0.0384  5
  best valid F1               0.8462      0.8440     0.0550  5
  test BA                     0.8841      0.9010     0.0447  5
  test AUC                    0.9371      0.9495     0.0304  5
  test AUC in-protein         0.9425      0.9455     0.0224  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9422      0.9464     0.0316  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8324      0.8491     0.0581  5
  test sensitivity            0.9094      0.9167     0.0335  5
  test specificity            0.8589      0.8646     0.0584  5
  test precision              0.7688      0.7759     0.0760  5
  test loss                   0.3040      0.2659     0.0752  5
  FPR (FP/(FP+TN))            0.1411      0.1354     0.0584  5
  FNR (FN/(FN+TP))            0.0906      0.0833     0.0335  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_nomb_hid128_3mlp --seeds=0,1,2,3,4`
