# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_lam025

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_lam025'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.7849      0.2470      0.6429      0.5263      0.8129      0.2791
groups_choline            5      0.7676      0.3752      0.5100      0.5759      0.6982      0.5079
groups_phosphorus_free    5      0.0903      0.8612      0.5647      0.5813      0.1733      0.8776
groups_sphingolipids      5      0.2727      0.6780      0.5426      0.5912      0.7212      0.4500
ALL                      20      0.4789      0.5404      0.5650      0.5687      0.6014      0.5286

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5349      0.5239     0.0375  20
max valid BA                0.5650      0.5527     0.0445  20
best valid F1               0.5246      0.5475     0.1221  20
test BA                     0.5096      0.5096     0.0527  20
test AUC                    0.5329      0.5076     0.0854  20
test AUC in-protein         0.5673      0.5537     0.1129  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5386      0.5645     0.1161  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.3341      0.4234     0.2130  20
test sensitivity            0.4789      0.4342     0.3907  20
test specificity            0.5404      0.5920     0.3627  20
test precision              0.3571      0.3636     0.1123  17
test loss                   0.6973      0.6924     0.0222  20
FPR (FP/(FP+TN))            0.4596      0.4080     0.3627  20
FNR (FN/(FN+TP))            0.5211      0.5658     0.3907  20

=== abs(sensitivity-specificity) gap: mean=0.6725 median=0.7594 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5140      0.5183     0.0114  5
  max valid BA                0.5460      0.5445     0.0202  5
  best valid F1               0.5152      0.5150     0.0056  5
  test BA                     0.5160      0.5165     0.0080  5
  test AUC                    0.5432      0.5060     0.0931  5
  test AUC in-protein         0.5014      0.5206     0.0500  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.4912      0.4972     0.0314  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.4320      0.5057     0.1717  5
  test sensitivity            0.7849      0.9462     0.3982  5
  test specificity            0.2470      0.0874     0.3853  5
  test precision              0.3504      0.3451     0.0103  5
  test loss                   0.7201      0.7191     0.0317  5
  FPR (FP/(FP+TN))            0.7530      0.9126     0.3853  5
  FNR (FN/(FN+TP))            0.2151      0.0538     0.3982  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5726      0.5523     0.0448  5
  max valid BA                0.6031      0.6059     0.0458  5
  best valid F1               0.5572      0.5445     0.0319  5
  test BA                     0.5714      0.5771     0.0211  5
  test AUC                    0.6169      0.6103     0.0233  5
  test AUC in-protein         0.6483      0.6269     0.0479  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.6198      0.6061     0.0525  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.5247      0.5367     0.0306  5
  test sensitivity            0.7676      0.8018     0.1766  5
  test specificity            0.3752      0.3812     0.2020  5
  test precision              0.4089      0.4076     0.0274  5
  test loss                   0.6942      0.6932     0.0031  5
  FPR (FP/(FP+TN))            0.6248      0.6188     0.2020  5
  FNR (FN/(FN+TP))            0.2324      0.1982     0.1766  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5141      0.5119     0.0136  5
  max valid BA                0.5254      0.5167     0.0189  5
  best valid F1               0.4097      0.5505     0.1982  5
  test BA                     0.4758      0.4796     0.0257  5
  test AUC                    0.4887      0.4723     0.0592  5
  test AUC in-protein         0.6000      0.6667     0.1933  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.5723      0.6061     0.0992  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.0956      0.0000     0.1486  5
  test sensitivity            0.0903      0.0000     0.1537  5
  test specificity            0.8612      0.9592     0.1996  5
  test precision              0.1912      0.2500     0.1696  3
  test loss                   0.6802      0.6815     0.0133  5
  FPR (FP/(FP+TN))            0.1388      0.0408     0.1996  5
  FNR (FN/(FN+TP))            0.9097      1.0000     0.1537  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5386      0.5390     0.0383  5
  max valid BA                0.5856      0.6091     0.0422  5
  best valid F1               0.6162      0.6275     0.0447  5
  test BA                     0.4754      0.4900     0.0655  5
  test AUC                    0.4827      0.4605     0.0863  5
  test AUC in-protein         0.5194      0.5204     0.0240  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4710      0.3783     0.1796  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.2840      0.3333     0.1773  5
  test sensitivity            0.2727      0.2727     0.2206  5
  test specificity            0.6780      0.7317     0.3187  5
  test precision              0.4252      0.3961     0.0931  4
  test loss                   0.6947      0.6960     0.0102  5
  FPR (FP/(FP+TN))            0.3220      0.2683     0.3187  5
  FNR (FN/(FN+TP))            0.7273      0.7273     0.2206  5
```

## AUC vs chemistry null model, in-sample increment

Failed: sphingolipids/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_lam025 --seeds=0,1,2,3,4`
