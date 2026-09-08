# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_liphid32

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_liphid32'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6473      0.7913      0.8955      0.8567      0.7032      0.7879
groups_choline            5      0.6414      0.4327      0.8375      0.7341      0.7125      0.4416
groups_phosphorus_free    5      0.4194      0.6735      0.8792      0.8199      0.6067      0.6939
groups_sphingolipids      5      0.5212      0.8439      0.8521      0.8021      0.6970      0.8500
ALL                      20      0.5573      0.6853      0.8661      0.8032      0.6798      0.6933

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6390      0.6456     0.1119  20
max valid BA                0.6866      0.6770     0.1156  20
best valid F1               0.6268      0.6202     0.1350  20
test BA                     0.6213      0.5824     0.1185  20
test AUC                    0.6201      0.6176     0.1530  16
test AUC in-protein         0.5893      0.5325     0.2054  9
  (proteins averaged)       6.2222      3.0000     5.3098  9
test F1                     0.5139      0.5191     0.1971  20
test sensitivity            0.5573      0.6173     0.2382  20
test specificity            0.6853      0.7272     0.2247  20
test precision              0.5329      0.4688     0.1669  19
test loss                   0.8043      0.8232     0.1896  20
FPR (FP/(FP+TN))            0.3147      0.2728     0.2247  20
FNR (FN/(FN+TP))            0.4427      0.3827     0.2382  20

=== abs(sensitivity-specificity) gap: mean=0.2831 median=0.1632 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7393      0.7421     0.0200  5
  max valid BA                0.7456      0.7512     0.0211  5
  best valid F1               0.6637      0.6704     0.0271  5
  test BA                     0.7193      0.7131     0.0484  5
  test AUC                    0.7108      0.7056     0.0219  3
  test AUC in-protein         0.4640      0.4692     0.0713  3
    (proteins averaged)      11.6667     11.0000     1.1547  3
  test F1                     0.6312      0.6231     0.0615  5
  test sensitivity            0.6473      0.6452     0.0446  5
  test specificity            0.7913      0.7596     0.0692  5
  test precision              0.6199      0.5849     0.0950  5
  test loss                   0.7652      0.8298     0.1316  5
  FPR (FP/(FP+TN))            0.2087      0.2404     0.0692  5
  FNR (FN/(FN+TP))            0.3527      0.3548     0.0446  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5320      0.5512     0.0336  5
  max valid BA                0.5770      0.5883     0.0536  5
  best valid F1               0.5248      0.5288     0.0230  5
  test BA                     0.5371      0.5456     0.0424  5
  test AUC                    0.5373      0.5756     0.1221  4
  test AUC in-protein         0.3524      0.3524     0.0000  1
    (proteins averaged)      12.0000     12.0000     0.0000  1
  test F1                     0.4632      0.5047     0.0987  5
  test sensitivity            0.6414      0.6216     0.2691  5
  test specificity            0.4327      0.4802     0.2747  5
  test precision              0.3844      0.3857     0.0420  5
  test loss                   0.8601      0.8187     0.1833  5
  FPR (FP/(FP+TN))            0.5673      0.5198     0.2747  5
  FNR (FN/(FN+TP))            0.3586      0.3784     0.2691  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6082      0.6201     0.0830  5
  max valid BA                0.6503      0.6711     0.0992  5
  best valid F1               0.5666      0.6000     0.1549  5
  test BA                     0.5464      0.5395     0.0454  5
  test AUC                    0.5813      0.5599     0.0747  4
  test AUC in-protein         0.6917      0.6333     0.2167  4
    (proteins averaged)       1.7500      1.5000     0.9574  4
  test F1                     0.4143      0.4762     0.1286  5
  test sensitivity            0.4194      0.4839     0.1881  5
  test specificity            0.6735      0.6531     0.1224  5
  test precision              0.4403      0.4250     0.0435  5
  test loss                   0.9548      0.8942     0.1531  5
  FPR (FP/(FP+TN))            0.3265      0.3469     0.1224  5
  FNR (FN/(FN+TP))            0.5806      0.5161     0.1881  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6764      0.7076     0.1459  5
  max valid BA                0.7735      0.8689     0.1410  5
  best valid F1               0.7523      0.8525     0.1495  5
  test BA                     0.6826      0.7967     0.1672  5
  test AUC                    0.6630      0.7650     0.2353  5
  test AUC in-protein         0.7928      0.7928     0.0000  1
    (proteins averaged)       2.0000      2.0000     0.0000  1
  test F1                     0.5468      0.7586     0.3470  5
  test sensitivity            0.5212      0.6667     0.3397  5
  test specificity            0.8439      0.8537     0.1386  5
  test precision              0.7256      0.7889     0.1928  4
  test loss                   0.6373      0.6137     0.1656  5
  FPR (FP/(FP+TN))            0.1561      0.1463     0.1386  5
  FNR (FN/(FN+TP))            0.4788      0.3333     0.3397  5
```

## AUC vs chemistry null model, in-sample increment

