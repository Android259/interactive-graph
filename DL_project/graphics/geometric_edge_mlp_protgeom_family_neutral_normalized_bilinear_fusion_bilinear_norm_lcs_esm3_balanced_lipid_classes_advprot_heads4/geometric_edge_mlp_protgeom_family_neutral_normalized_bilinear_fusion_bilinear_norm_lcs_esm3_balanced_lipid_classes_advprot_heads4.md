# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_heads4

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_heads4'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.8065      0.2153      0.6612      0.5345      0.6946      0.3791
groups_choline            5      0.7495      0.3733      0.4895      0.5984      0.5661      0.6386
groups_phosphorus_free    5      0.2129      0.7633      0.4031      0.7098      0.4600      0.6367
groups_sphingolipids      5      0.3394      0.6049      0.4880      0.6783      0.4909      0.7350
ALL                      20      0.5271      0.4892      0.5105      0.6302      0.5529      0.5974

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5499      0.5415     0.0427  20
max valid BA                0.5751      0.5672     0.0434  20
best valid F1               0.5631      0.5505     0.0469  20
test BA                     0.5081      0.5079     0.0494  20
test AUC                    0.5127      0.5017     0.0780  20
test AUC in-protein         0.5751      0.5102     0.1484  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5112      0.5181     0.1152  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.3836      0.4500     0.1808  20
test sensitivity            0.5271      0.5013     0.3289  20
test specificity            0.4892      0.5484     0.3005  20
test precision              0.3506      0.3564     0.1094  19
test loss                   0.7035      0.6969     0.0196  20
FPR (FP/(FP+TN))            0.5108      0.4516     0.3005  20
FNR (FN/(FN+TP))            0.4729      0.4987     0.3289  20

=== abs(sensitivity-specificity) gap: mean=0.5144 median=0.5512 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5257      0.5227     0.0255  5
  max valid BA                0.5369      0.5302     0.0140  5
  best valid F1               0.5149      0.5145     0.0044  5
  test BA                     0.5109      0.5123     0.0280  5
  test AUC                    0.5176      0.5041     0.0337  5
  test AUC in-protein         0.4621      0.4411     0.0338  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.4705      0.4492     0.0465  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.4783      0.4818     0.0227  5
  test sensitivity            0.8065      0.8387     0.1807  5
  test specificity            0.2153      0.1858     0.2296  5
  test precision              0.3479      0.3436     0.0236  5
  test loss                   0.7200      0.7334     0.0277  5
  FPR (FP/(FP+TN))            0.7847      0.8142     0.2296  5
  FNR (FN/(FN+TP))            0.1935      0.1613     0.1807  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5668      0.5682     0.0534  5
  max valid BA                0.6023      0.5967     0.0469  5
  best valid F1               0.5585      0.5483     0.0311  5
  test BA                     0.5614      0.5675     0.0413  5
  test AUC                    0.6051      0.5965     0.0284  5
  test AUC in-protein         0.6554      0.6472     0.0438  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.6176      0.6115     0.0315  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.5157      0.5266     0.0341  5
  test sensitivity            0.7495      0.8468     0.1843  5
  test specificity            0.3733      0.2871     0.2443  5
  test precision              0.4069      0.3975     0.0432  5
  test loss                   0.6927      0.6935     0.0059  5
  FPR (FP/(FP+TN))            0.6267      0.7129     0.2443  5
  FNR (FN/(FN+TP))            0.2505      0.1532     0.1843  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5248      0.5238     0.0192  5
  max valid BA                0.5484      0.5514     0.0200  5
  best valid F1               0.5539      0.5505     0.0154  5
  test BA                     0.4881      0.4845     0.0193  5
  test AUC                    0.4595      0.4602     0.0410  5
  test AUC in-protein         0.6667      0.6667     0.2483  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.5428      0.5758     0.0753  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.2200      0.2500     0.1877  5
  test sensitivity            0.2129      0.1935     0.2073  5
  test specificity            0.7633      0.7755     0.2054  5
  test precision              0.3232      0.3594     0.1069  4
  test loss                   0.6909      0.6901     0.0039  5
  FPR (FP/(FP+TN))            0.2367      0.2245     0.2054  5
  FNR (FN/(FN+TP))            0.7871      0.8065     0.2073  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5823      0.5773     0.0401  5
  max valid BA                0.6130      0.6227     0.0267  5
  best valid F1               0.6252      0.6286     0.0372  5
  test BA                     0.4721      0.4756     0.0552  5
  test AUC                    0.4686      0.4405     0.0930  5
  test AUC in-protein         0.5163      0.5000     0.0328  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4139      0.3519     0.1577  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3203      0.3438     0.2165  5
  test sensitivity            0.3394      0.3333     0.2781  5
  test specificity            0.6049      0.6098     0.2304  5
  test precision              0.3190      0.3548     0.1921  5
  test loss                   0.7105      0.7058     0.0159  5
  FPR (FP/(FP+TN))            0.3951      0.3902     0.2304  5
  FNR (FN/(FN+TP))            0.6606      0.6667     0.2781  5
```

## AUC vs chemistry null model, in-sample increment

Failed: sphingolipids/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_heads4 --seeds=0,1,2,3,4`
