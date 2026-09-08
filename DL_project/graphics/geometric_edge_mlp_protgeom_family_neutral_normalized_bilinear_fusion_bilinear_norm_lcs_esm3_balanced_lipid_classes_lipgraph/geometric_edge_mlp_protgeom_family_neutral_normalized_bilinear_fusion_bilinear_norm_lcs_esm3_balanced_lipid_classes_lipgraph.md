# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_lipgraph

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_lipgraph'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.7806      0.5956      0.8344      0.4919      0.7634      0.6703
groups_choline            5      0.2613      0.7188      0.4710      0.6935      0.3554      0.6673
groups_phosphorus_free    5      0.4968      0.4449      0.6778      0.5654      0.5333      0.4653
groups_sphingolipids      5      0.4242      0.4829      0.4585      0.6395      0.5152      0.5500
ALL                      20      0.4907      0.5606      0.6104      0.5976      0.5418      0.5882

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5591      0.5138     0.0869  20
max valid BA                0.5650      0.5138     0.0950  20
best valid F1               0.5028      0.5211     0.1275  20
test BA                     0.5256      0.5000     0.1076  20
test AUC                    0.5170      0.4813     0.1559  18
test AUC in-protein         0.4302      0.5060     0.1965  12
  (proteins averaged)       6.7500      6.5000     5.0295  12
test F1                     0.3696      0.4153     0.2361  20
test sensitivity            0.4907      0.5259     0.3692  20
test specificity            0.5606      0.6018     0.3364  20
test precision              0.3789      0.3857     0.1285  17
test loss                   0.7426      0.6981     0.1634  20
FPR (FP/(FP+TN))            0.4394      0.3981     0.3364  20
FNR (FN/(FN+TP))            0.5093      0.4741     0.3692  20

=== abs(sensitivity-specificity) gap: mean=0.5701 median=0.5581 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6962      0.6922     0.0144  5
  max valid BA                0.7169      0.7138     0.0165  5
  best valid F1               0.6352      0.6325     0.0169  5
  test BA                     0.6881      0.6802     0.0238  5
  test AUC                    0.7010      0.7144     0.0346  5
  test AUC in-protein         0.5725      0.5708     0.0365  4
    (proteins averaged)      11.7500     11.5000     0.9574  4
  test F1                     0.6060      0.5944     0.0244  5
  test sensitivity            0.7806      0.7957     0.0535  5
  test specificity            0.5956      0.5628     0.0563  5
  test precision              0.4968      0.4872     0.0279  5
  test loss                   0.6104      0.6211     0.0231  5
  FPR (FP/(FP+TN))            0.4044      0.4372     0.0563  5
  FNR (FN/(FN+TP))            0.2194      0.2043     0.0535  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5084      0.5000     0.0219  5
  max valid BA                0.5113      0.5053     0.0198  5
  best valid F1               0.4064      0.4185     0.0664  5
  test BA                     0.4900      0.5000     0.0424  5
  test AUC                    0.4836      0.4645     0.0488  3
  test AUC in-protein         0.2969      0.2969     0.0678  2
    (proteins averaged)      11.0000     11.0000     1.4142  2
  test F1                     0.2045      0.2384     0.2152  5
  test sensitivity            0.2613      0.1622     0.3574  5
  test specificity            0.7188      0.8911     0.3476  5
  test precision              0.2692      0.3135     0.1955  4
  test loss                   0.7223      0.6833     0.0817  5
  FPR (FP/(FP+TN))            0.2812      0.1089     0.3476  5
  FNR (FN/(FN+TP))            0.7387      0.8378     0.3574  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4993      0.5034     0.0181  5
  max valid BA                0.4993      0.5034     0.0181  5
  best valid F1               0.4346      0.4062     0.0964  5
  test BA                     0.4708      0.4677     0.0225  5
  test AUC                    0.4485      0.4098     0.1536  5
  test AUC in-protein         0.2556      0.1667     0.3097  3
    (proteins averaged)       2.0000      2.0000     1.0000  3
  test F1                     0.3726      0.2857     0.1483  5
  test sensitivity            0.4968      0.2581     0.3724  5
  test specificity            0.4449      0.6531     0.3548  5
  test precision              0.3463      0.3684     0.0420  5
  test loss                   0.9316      0.9354     0.2248  5
  FPR (FP/(FP+TN))            0.5551      0.3469     0.3548  5
  FNR (FN/(FN+TP))            0.5032      0.7419     0.3724  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5326      0.5125     0.0526  5
  max valid BA                0.5326      0.5125     0.0526  5
  best valid F1               0.5349      0.6226     0.1505  5
  test BA                     0.4536      0.5000     0.0852  5
  test AUC                    0.4216      0.4346     0.1298  5
  test AUC in-protein         0.5040      0.5023     0.0051  3
    (proteins averaged)       2.0000      2.0000     0.0000  3
  test F1                     0.2952      0.3158     0.2915  5
  test sensitivity            0.4242      0.3636     0.4490  5
  test specificity            0.4829      0.2439     0.4802  5
  test precision              0.3829      0.4237     0.0906  3
  test loss                   0.7060      0.7013     0.0192  5
  FPR (FP/(FP+TN))            0.5171      0.7561     0.4802  5
  FNR (FN/(FN+TP))            0.5758      0.6364     0.4490  5
```

## AUC vs chemistry null model, in-sample increment

Failed: sphingolipids/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_lipgraph --seeds=0,1,2,3,4`
