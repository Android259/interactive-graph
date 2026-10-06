# ge_s15_prothid32_hid64_noreg_liptail

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'ge_s15_prothid32_hid64_noreg_liptail'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8594      0.8984      0.9568      0.8932      0.9467      0.8901
ALL                 5      0.8594      0.8984      0.9568      0.8932      0.9467      0.8901

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.9080      0.9115     0.0252  5
max valid BA                0.9184      0.9242     0.0251  5
best valid F1               0.8764      0.8911     0.0382  5
test BA                     0.8789      0.8698     0.0414  5
test AUC                    0.9466      0.9607     0.0304  5
test AUC in-protein         0.9326      0.9350     0.0201  5
  (proteins averaged)      10.0000     10.0000     2.1213  5
test AUC in-protein (pairs)      0.9398      0.9454     0.0268  5
  (proteins contributing)     19.2000     19.0000     1.7889  5
test F1                     0.8345      0.8247     0.0535  5
test sensitivity            0.8594      0.8571     0.0683  5
test specificity            0.8984      0.9072     0.0548  5
test precision              0.8157      0.8235     0.0737  5
test loss                   0.3315      0.2910     0.1305  5
FPR (FP/(FP+TN))            0.1016      0.0928     0.0548  5
FNR (FN/(FN+TP))            0.1406      0.1429     0.0683  5

=== abs(sensitivity-specificity) gap: mean=0.0769 median=0.0729 n=5 ===
sensitivity std across seeds (by group): mean=0.0683 median=0.0683 n=1
specificity std across seeds (by group): mean=0.0548 median=0.0548 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9080      0.9115     0.0252  5
  max valid BA                0.9184      0.9242     0.0251  5
  best valid F1               0.8764      0.8911     0.0382  5
  test BA                     0.8789      0.8698     0.0414  5
  test AUC                    0.9466      0.9607     0.0304  5
  test AUC in-protein         0.9326      0.9350     0.0201  5
    (proteins averaged)      10.0000     10.0000     2.1213  5
  test AUC in-protein (pairs)      0.9398      0.9454     0.0268  5
    (proteins contributing)     19.2000     19.0000     1.7889  5
  test F1                     0.8345      0.8247     0.0535  5
  test sensitivity            0.8594      0.8571     0.0683  5
  test specificity            0.8984      0.9072     0.0548  5
  test precision              0.8157      0.8235     0.0737  5
  test loss                   0.3315      0.2910     0.1305  5
  FPR (FP/(FP+TN))            0.1016      0.0928     0.0548  5
  FNR (FN/(FN+TP))            0.1406      0.1429     0.0683  5
```

## AUC vs chemistry null model, in-sample increment

Failed: species15/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_s15_prothid32_hid64_noreg_liptail --seeds=0,1,2,3,4`
