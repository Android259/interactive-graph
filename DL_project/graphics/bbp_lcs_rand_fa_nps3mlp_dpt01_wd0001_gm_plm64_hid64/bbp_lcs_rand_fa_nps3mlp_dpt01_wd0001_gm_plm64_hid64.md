# bbp_lcs_rand_fa_nps3mlp_dpt01_wd0001_gm_plm64_hid64

## Summary (analysis/summarize_label.py)

```
Summary: 'bbp_lcs_rand_fa_nps3mlp_dpt01_wd0001_gm_plm64_hid64'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.5312      0.5921      0.9554      0.8888      0.5161      0.6053
groups_choline            5      0.3477      0.8168      0.8594      0.7912      0.3786      0.7726
groups_phosphorus_free    5      0.6065      0.7368      0.9298      0.8206      0.6600      0.7071
groups_sphingolipids      5      0.2788      0.6873      0.6817      0.6581      0.3697      0.6963
ALL                      20      0.4410      0.7082      0.8566      0.7897      0.4811      0.6953

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5882      0.5743     0.0797  20
max valid BA                0.6203      0.6078     0.0814  20
best valid F1               0.5448      0.5437     0.0897  20
test BA                     0.5746      0.5509     0.0939  20
test F1                     0.4136      0.4728     0.2133  20
test sensitivity            0.4410      0.5337     0.2558  20
test specificity            0.7082      0.6967     0.1689  20
test precision              0.4447      0.4537     0.1488  19
test loss                   1.3835      1.0245     0.8702  20
FPR (FP/(FP+TN))            0.2918      0.3033     0.1689  20
FNR (FN/(FN+TP))            0.5590      0.4663     0.2558  20

=== abs(sensitivity-specificity) gap: mean=0.3231 median=0.1473 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5607      0.5714     0.0361  5
  max valid BA                0.5832      0.5813     0.0316  5
  best valid F1               0.5370      0.5439     0.0255  5
  test BA                     0.5616      0.5681     0.0356  5
  test F1                     0.4836      0.4821     0.0422  5
  test sensitivity            0.5312      0.5269     0.0630  5
  test specificity            0.5921      0.6093     0.0547  5
  test precision              0.4455      0.4537     0.0354  5
  test loss                   1.6013      1.7286     0.3617  5
  FPR (FP/(FP+TN))            0.4079      0.3907     0.0547  5
  FNR (FN/(FN+TP))            0.4688      0.4731     0.0630  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5756      0.5804     0.0457  5
  max valid BA                0.6098      0.6116     0.0388  5
  best valid F1               0.5268      0.5434     0.0824  5
  test BA                     0.5823      0.6324     0.0703  5
  test F1                     0.3766      0.5134     0.2484  5
  test sensitivity            0.3477      0.4324     0.2537  5
  test specificity            0.8168      0.8323     0.1262  5
  test precision              0.5451      0.5584     0.0837  4
  test loss                   1.2592      1.0836     0.7135  5
  FPR (FP/(FP+TN))            0.1832      0.1677     0.1262  5
  FNR (FN/(FN+TP))            0.6523      0.5676     0.2537  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6836      0.7137     0.0895  5
  max valid BA                0.7349      0.7137     0.0473  5
  best valid F1               0.6582      0.6400     0.0588  5
  test BA                     0.6716      0.6822     0.1119  5
  test F1                     0.5497      0.6027     0.2118  5
  test sensitivity            0.6065      0.7097     0.2760  5
  test specificity            0.7368      0.7193     0.0823  5
  test precision              0.5259      0.5500     0.1208  5
  test loss                   0.8938      0.8384     0.3468  5
  FPR (FP/(FP+TN))            0.2632      0.2807     0.0823  5
  FNR (FN/(FN+TP))            0.3935      0.2903     0.2760  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5330      0.5412     0.0494  5
  max valid BA                0.5534      0.5412     0.0533  5
  best valid F1               0.4574      0.4615     0.0351  5
  test BA                     0.4830      0.4818     0.0252  5
  test F1                     0.2446      0.2182     0.2025  5
  test sensitivity            0.2788      0.1818     0.2797  5
  test specificity            0.6873      0.7091     0.2768  5
  test precision              0.2826      0.3571     0.1654  5
  test loss                   1.7798      0.6953     1.5041  5
  FPR (FP/(FP+TN))            0.3127      0.2909     0.2768  5
  FNR (FN/(FN+TP))            0.7212      0.8182     0.2797  5
```

## AUC vs chemistry null model, in-sample increment

Failed: ValueError: Unknown parameter: --lipid_coldsplit -- rerun for the full output: `python3 analysis/full_label_report.py --label bbp_lcs_rand_fa_nps3mlp_dpt01_wd0001_gm_plm64_hid64 --seeds=0,1,2,3,4`
