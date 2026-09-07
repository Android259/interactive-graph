# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_hid64

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_hid64'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6172      0.5682      0.9612      0.8984      0.6215      0.5828
groups_choline            5      0.2000      0.8731      0.8920      0.7606      0.2196      0.8667
groups_phosphorus_free    5      0.2258      0.8070      0.9037      0.7972      0.3200      0.8429
groups_sphingolipids      5      0.2667      0.8509      0.8292      0.7437      0.2970      0.9037
ALL                      20      0.3274      0.7748      0.8965      0.8000      0.3645      0.7990

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5818      0.5816     0.0686  20
max valid BA                0.6320      0.6229     0.0550  20
best valid F1               0.5477      0.5678     0.0806  20
test BA                     0.5511      0.5477     0.0717  20
test F1                     0.3431      0.3790     0.1929  20
test sensitivity            0.3274      0.3189     0.2355  20
test specificity            0.7748      0.7994     0.1833  20
test precision              0.4910      0.4878     0.2355  20
test loss                   1.1883      1.1604     0.5188  20
FPR (FP/(FP+TN))            0.2252      0.2006     0.1833  20
FNR (FN/(FN+TP))            0.6726      0.6811     0.2355  20

=== abs(sensitivity-specificity) gap: mean=0.5048 median=0.5346 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6021      0.6024     0.0163  5
  max valid BA                0.6171      0.6227     0.0200  5
  best valid F1               0.5674      0.5679     0.0092  5
  test BA                     0.5927      0.5838     0.0274  5
  test F1                     0.5284      0.5408     0.0493  5
  test sensitivity            0.6172      0.6774     0.1201  5
  test specificity            0.5682      0.5364     0.1027  5
  test precision              0.4712      0.4773     0.0296  5
  test loss                   1.3160      1.3501     0.1329  5
  FPR (FP/(FP+TN))            0.4318      0.4636     0.1027  5
  FNR (FN/(FN+TP))            0.3828      0.3226     0.1201  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5432      0.5506     0.0400  5
  max valid BA                0.6083      0.5982     0.0286  5
  best valid F1               0.5213      0.5208     0.0716  5
  test BA                     0.5365      0.5256     0.0562  5
  test F1                     0.2629      0.1926     0.1700  5
  test sensitivity            0.2000      0.1171     0.1605  5
  test specificity            0.8731      0.8443     0.0853  5
  test precision              0.5344      0.5417     0.1888  5
  test loss                   1.3165      0.8650     0.8153  5
  FPR (FP/(FP+TN))            0.1269      0.1557     0.0853  5
  FNR (FN/(FN+TP))            0.8000      0.8829     0.1605  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5814      0.5708     0.1001  5
  max valid BA                0.6771      0.6893     0.0753  5
  best valid F1               0.5761      0.6087     0.1248  5
  test BA                     0.5164      0.4859     0.0697  5
  test F1                     0.2420      0.2500     0.2050  5
  test sensitivity            0.2258      0.1613     0.2326  5
  test specificity            0.8070      0.8947     0.1370  5
  test precision              0.3251      0.3333     0.2183  5
  test loss                   0.8390      0.7916     0.3247  5
  FPR (FP/(FP+TN))            0.1930      0.1053     0.1370  5
  FNR (FN/(FN+TP))            0.7742      0.8387     0.2326  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6003      0.6061     0.0874  5
  max valid BA                0.6254      0.6120     0.0625  5
  best valid F1               0.5260      0.5546     0.0842  5
  test BA                     0.5588      0.5061     0.1080  5
  test F1                     0.3392      0.3733     0.1990  5
  test sensitivity            0.2667      0.3030     0.1623  5
  test specificity            0.8509      0.9818     0.2213  5
  test precision              0.6333      0.5000     0.3416  5
  test loss                   1.2818      1.2091     0.5353  5
  FPR (FP/(FP+TN))            0.1491      0.0182     0.2213  5
  FNR (FN/(FN+TP))            0.7333      0.6970     0.1623  5
```

## AUC vs chemistry null model, in-sample increment

Failed: ValueError: Unknown parameter: --lipid_coldsplit -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_hid64 --seeds=0,1,2,3,4`
