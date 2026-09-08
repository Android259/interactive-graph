# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_lipdesc

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_lipdesc'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6387      0.6809      0.8710      0.7872      0.7097      0.7154
groups_choline            5      0.4054      0.6099      0.9129      0.8130      0.3268      0.7970
groups_phosphorus_free    5      0.4645      0.6653      0.8949      0.8130      0.5667      0.7184
groups_sphingolipids      5      0.7212      0.5122      0.7863      0.6613      0.7818      0.5800
ALL                      20      0.5575      0.6171      0.8663      0.7686      0.5962      0.7027

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6179      0.5939     0.0972  20
max valid BA                0.6495      0.6525     0.1022  20
best valid F1               0.5893      0.5856     0.1213  20
test BA                     0.5873      0.5905     0.1011  20
test AUC                    0.5915      0.6200     0.1604  18
test AUC in-protein         0.5298      0.4989     0.1193  12
  (proteins averaged)       6.5000      6.0000     4.7386  12
test F1                     0.4846      0.5433     0.1810  20
test sensitivity            0.5575      0.5860     0.2833  20
test specificity            0.6171      0.6857     0.2844  20
test precision              0.4780      0.4676     0.1502  20
test loss                   0.8592      0.8226     0.2178  20
FPR (FP/(FP+TN))            0.3829      0.3143     0.2844  20
FNR (FN/(FN+TP))            0.4425      0.4140     0.2833  20

=== abs(sensitivity-specificity) gap: mean=0.3940 median=0.2599 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6896      0.6760     0.0484  5
  max valid BA                0.7125      0.7144     0.0421  5
  best valid F1               0.6267      0.6301     0.0477  5
  test BA                     0.6598      0.6523     0.0406  5
  test AUC                    0.7093      0.6975     0.0372  4
  test AUC in-protein         0.4971      0.4971     0.0219  2
    (proteins averaged)      11.5000     11.5000     0.7071  2
  test F1                     0.5624      0.5455     0.0493  5
  test sensitivity            0.6387      0.6344     0.1036  5
  test specificity            0.6809      0.6776     0.0948  5
  test precision              0.5109      0.4758     0.0587  5
  test loss                   0.7948      0.8356     0.0831  5
  FPR (FP/(FP+TN))            0.3191      0.3224     0.0948  5
  FNR (FN/(FN+TP))            0.3613      0.3656     0.1036  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5400      0.5487     0.0370  5
  max valid BA                0.5619      0.5541     0.0520  5
  best valid F1               0.4857      0.5098     0.0695  5
  test BA                     0.5077      0.5000     0.0541  5
  test AUC                    0.4073      0.4116     0.0171  4
  test AUC in-protein         0.4716      0.4667     0.1264  4
    (proteins averaged)      10.7500     10.5000     0.9574  4
  test F1                     0.3250      0.2723     0.1788  5
  test sensitivity            0.4054      0.2613     0.3771  5
  test specificity            0.6099      0.6386     0.3637  5
  test precision              0.3558      0.3546     0.1075  5
  test loss                   1.0867      1.0907     0.2767  5
  FPR (FP/(FP+TN))            0.3901      0.3614     0.3637  5
  FNR (FN/(FN+TP))            0.5946      0.7387     0.3771  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5852      0.5663     0.0636  5
  max valid BA                0.6425      0.6554     0.0386  5
  best valid F1               0.5445      0.5915     0.1077  5
  test BA                     0.5649      0.5938     0.0888  5
  test AUC                    0.5740      0.6024     0.1670  5
  test AUC in-protein         0.5000      0.5000     0.0000  1
    (proteins averaged)       2.0000      2.0000     0.0000  1
  test F1                     0.4432      0.5429     0.1859  5
  test sensitivity            0.4645      0.5484     0.2322  5
  test specificity            0.6653      0.6939     0.1123  5
  test precision              0.4411      0.4667     0.1487  5
  test loss                   0.8653      0.8694     0.1719  5
  FPR (FP/(FP+TN))            0.3347      0.3061     0.1123  5
  FNR (FN/(FN+TP))            0.5355      0.4516     0.2322  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6567      0.6015     0.1409  5
  max valid BA                0.6809      0.6167     0.1667  5
  best valid F1               0.7003      0.6531     0.1348  5
  test BA                     0.6167      0.5480     0.1408  5
  test AUC                    0.6622      0.7347     0.1607  5
  test AUC in-protein         0.5954      0.6077     0.1323  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test F1                     0.6076      0.6168     0.1618  5
  test sensitivity            0.7212      0.7273     0.3048  5
  test specificity            0.5122      0.8293     0.4566  5
  test precision              0.6043      0.5714     0.1684  5
  test loss                   0.6898      0.6967     0.0808  5
  FPR (FP/(FP+TN))            0.4878      0.1707     0.4566  5
  FNR (FN/(FN+TP))            0.2788      0.2727     0.3048  5
```

## AUC vs chemistry null model, in-sample increment

Failed: sphingolipids/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_lipdesc --seeds=0,1,2,3,4`
