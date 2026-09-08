# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.4473      0.5801      0.7451      0.6328      0.4344      0.6781
groups_choline            5      0.3369      0.8000      0.6720      0.6433      0.3911      0.8440
groups_phosphorus_free    5      0.4710      0.5053      0.7002      0.4962      0.4133      0.5607
groups_sphingolipids      5      0.5576      0.5309      0.6609      0.6157      0.3758      0.7000
ALL                      20      0.4532      0.6041      0.6945      0.5970      0.4036      0.6957

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5327      0.5286     0.0590  20
max valid BA                0.5497      0.5497     0.0636  20
best valid F1               0.4875      0.5285     0.1100  20
test BA                     0.5286      0.5111     0.0795  20
test F1                     0.3906      0.4405     0.1707  20
test sensitivity            0.4532      0.4410     0.2897  20
test specificity            0.6041      0.7182     0.2749  20
test precision              0.4041      0.3893     0.1410  20
test loss                   0.7687      0.6947     0.2959  20
FPR (FP/(FP+TN))            0.3959      0.2818     0.2749  20
FNR (FN/(FN+TP))            0.5468      0.5590     0.2897  20

=== abs(sensitivity-specificity) gap: mean=0.4650 median=0.4890 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5308      0.5337     0.0208  5
  max valid BA                0.5563      0.5631     0.0268  5
  best valid F1               0.5206      0.5399     0.0514  5
  test BA                     0.5137      0.5221     0.0376  5
  test F1                     0.4031      0.4444     0.1066  5
  test sensitivity            0.4473      0.4946     0.1984  5
  test specificity            0.5801      0.5497     0.1868  5
  test precision              0.3967      0.4035     0.0647  5
  test loss                   0.7621      0.7244     0.1134  5
  FPR (FP/(FP+TN))            0.4199      0.4503     0.1868  5
  FNR (FN/(FN+TP))            0.5527      0.5054     0.1984  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5961      0.5997     0.0491  5
  max valid BA                0.6176      0.6443     0.0572  5
  best valid F1               0.5506      0.5729     0.0552  5
  test BA                     0.5685      0.5650     0.0592  5
  test F1                     0.3674      0.3889     0.2097  5
  test sensitivity            0.3369      0.3153     0.2512  5
  test specificity            0.8000      0.7964     0.1473  5
  test precision              0.4848      0.5072     0.1757  5
  test loss                   0.9285      0.6600     0.5950  5
  FPR (FP/(FP+TN))            0.2000      0.2036     0.1473  5
  FNR (FN/(FN+TP))            0.6631      0.6847     0.2512  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4807      0.4774     0.0683  5
  max valid BA                0.4870      0.4899     0.0629  5
  best valid F1               0.3633      0.4091     0.1522  5
  test BA                     0.4881      0.4791     0.0993  5
  test F1                     0.3424      0.4516     0.2176  5
  test sensitivity            0.4710      0.5161     0.3968  5
  test specificity            0.5053      0.6491     0.3542  5
  test precision              0.3130      0.3387     0.1613  5
  test loss                   0.7022      0.7149     0.0319  5
  FPR (FP/(FP+TN))            0.4947      0.3509     0.3542  5
  FNR (FN/(FN+TP))            0.5290      0.4839     0.3968  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5232      0.5236     0.0229  5
  max valid BA                0.5379      0.5497     0.0196  5
  best valid F1               0.5155      0.5263     0.0446  5
  test BA                     0.5442      0.5000     0.1031  5
  test F1                     0.4496      0.4524     0.1661  5
  test sensitivity            0.5576      0.5758     0.3282  5
  test specificity            0.5309      0.7091     0.3306  5
  test precision              0.4219      0.3750     0.1203  5
  test loss                   0.6819      0.6918     0.0338  5
  FPR (FP/(FP+TN))            0.4691      0.2909     0.3306  5
  FNR (FN/(FN+TP))            0.4424      0.4242     0.3282  5
```

## AUC vs chemistry null model, in-sample increment

