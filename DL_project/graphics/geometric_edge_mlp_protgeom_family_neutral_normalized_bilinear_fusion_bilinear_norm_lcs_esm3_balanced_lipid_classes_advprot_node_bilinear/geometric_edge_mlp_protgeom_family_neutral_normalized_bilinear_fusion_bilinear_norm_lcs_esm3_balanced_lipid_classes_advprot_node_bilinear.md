# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_node_bilinear

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_node_bilinear'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.5806      0.5694      0.5603      0.5546      0.6882      0.5176
groups_choline            5      0.7243      0.3455      0.4915      0.5630      0.6000      0.5604
groups_phosphorus_free    5      0.5613      0.4122      0.4415      0.5761      0.6667      0.5388
groups_sphingolipids      5      0.4364      0.4927      0.5387      0.5040      0.7212      0.5250
ALL                      20      0.5757      0.4550      0.5080      0.5494      0.6690      0.5354

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5717      0.5585     0.0503  20
max valid BA                0.6022      0.5937     0.0505  20
best valid F1               0.5801      0.5683     0.0531  20
test BA                     0.5153      0.5096     0.0790  20
test AUC                    0.5127      0.5162     0.0955  20
test AUC in-protein         0.5626      0.5369     0.2004  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5271      0.5129     0.1346  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.4506      0.4629     0.0992  20
test sensitivity            0.5757      0.6129     0.2144  20
test specificity            0.4550      0.4269     0.2434  20
test precision              0.4147      0.3868     0.0997  20
test loss                   0.7872      0.6969     0.3831  20
FPR (FP/(FP+TN))            0.5450      0.5731     0.2434  20
FNR (FN/(FN+TP))            0.4243      0.3871     0.2144  20

=== abs(sensitivity-specificity) gap: mean=0.3633 median=0.2890 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5944      0.5978     0.0797  5
  max valid BA                0.6029      0.5978     0.0734  5
  best valid F1               0.5493      0.5333     0.0462  5
  test BA                     0.5750      0.5637     0.0980  5
  test AUC                    0.5561      0.5518     0.1187  5
  test AUC in-protein         0.5331      0.5183     0.0387  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.5366      0.5381     0.0489  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.4510      0.4643     0.1763  5
  test sensitivity            0.5806      0.6452     0.2900  5
  test specificity            0.5694      0.5683     0.3339  5
  test precision              0.4554      0.4011     0.1243  5
  test loss                   0.6926      0.6941     0.0489  5
  FPR (FP/(FP+TN))            0.4306      0.4317     0.3339  5
  FNR (FN/(FN+TP))            0.4194      0.3548     0.2900  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5502      0.5500     0.0221  5
  max valid BA                0.5802      0.5784     0.0133  5
  best valid F1               0.5443      0.5450     0.0092  5
  test BA                     0.5349      0.5529     0.0352  5
  test AUC                    0.5418      0.5091     0.1185  5
  test AUC in-protein         0.5535      0.5959     0.1436  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.5370      0.4755     0.1034  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.4910      0.5084     0.0520  5
  test sensitivity            0.7243      0.7477     0.1901  5
  test specificity            0.3455      0.3515     0.1887  5
  test precision              0.3799      0.3817     0.0234  5
  test loss                   0.7121      0.6943     0.0393  5
  FPR (FP/(FP+TN))            0.6545      0.6485     0.1887  5
  FNR (FN/(FN+TP))            0.2757      0.2523     0.1901  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5629      0.5660     0.0347  5
  max valid BA                0.6027      0.6078     0.0311  5
  best valid F1               0.5715      0.5714     0.0096  5
  test BA                     0.4868      0.4750     0.0477  5
  test AUC                    0.4966      0.5234     0.0703  5
  test AUC in-protein         0.6600      0.8000     0.3876  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.6106      0.5758     0.1825  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.4482      0.4615     0.0590  5
  test sensitivity            0.5613      0.5806     0.1084  5
  test specificity            0.4122      0.4082     0.0894  5
  test precision              0.3757      0.3636     0.0388  5
  test loss                   1.0511      0.7098     0.7593  5
  FPR (FP/(FP+TN))            0.5878      0.5918     0.0894  5
  FNR (FN/(FN+TP))            0.4387      0.4194     0.1084  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5793      0.5595     0.0508  5
  max valid BA                0.6231      0.6235     0.0665  5
  best valid F1               0.6554      0.6486     0.0334  5
  test BA                     0.4645      0.4490     0.0855  5
  test AUC                    0.4563      0.4568     0.0507  5
  test AUC in-protein         0.5039      0.4917     0.0340  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4241      0.3911     0.1321  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4123      0.4146     0.0747  5
  test sensitivity            0.4364      0.3333     0.1851  5
  test specificity            0.4927      0.5854     0.3014  5
  test precision              0.4476      0.3929     0.1511  5
  test loss                   0.6928      0.6969     0.0087  5
  FPR (FP/(FP+TN))            0.5073      0.4146     0.3014  5
  FNR (FN/(FN+TP))            0.5636      0.6667     0.1851  5
```

## AUC vs chemistry null model, in-sample increment

Failed: sphingolipids/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_node_bilinear --seeds=0,1,2,3,4`
