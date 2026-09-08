# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_liphid32

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_liphid32'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.8258      0.2383      0.5879      0.5751      0.7226      0.4297
groups_choline            5      0.6793      0.4267      0.5119      0.5005      0.6339      0.5366
groups_phosphorus_free    5      0.1226      0.8612      0.5728      0.5501      0.5133      0.5837
groups_sphingolipids      5      0.4121      0.5171      0.5915      0.5293      0.4545      0.6950
ALL                      20      0.5099      0.5108      0.5660      0.5387      0.5811      0.5612

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5291      0.5265     0.0322  20
max valid BA                0.5712      0.5679     0.0428  20
best valid F1               0.5499      0.5424     0.0577  20
test BA                     0.5104      0.5087     0.0577  20
test AUC                    0.5206      0.5229     0.0599  20
test AUC in-protein         0.5358      0.5362     0.1677  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5231      0.5545     0.1335  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.3744      0.4455     0.1755  20
test sensitivity            0.5099      0.4521     0.3519  20
test specificity            0.5108      0.4350     0.3413  20
test precision              0.3965      0.3731     0.0763  18
test loss                   0.6979      0.6937     0.0248  20
FPR (FP/(FP+TN))            0.4892      0.5650     0.3413  20
FNR (FN/(FN+TP))            0.4901      0.5479     0.3519  20

=== abs(sensitivity-specificity) gap: mean=0.6110 median=0.6300 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5349      0.5309     0.0343  5
  max valid BA                0.5761      0.5485     0.0613  5
  best valid F1               0.5314      0.5187     0.0307  5
  test BA                     0.5320      0.5328     0.0561  5
  test AUC                    0.5085      0.4868     0.0645  5
  test AUC in-protein         0.4829      0.4540     0.0883  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.4934      0.4633     0.0780  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.4939      0.4824     0.0257  5
  test sensitivity            0.8258      0.8817     0.2325  5
  test specificity            0.2383      0.0984     0.3237  5
  test precision              0.3807      0.3523     0.0871  5
  test loss                   0.7187      0.7091     0.0420  5
  FPR (FP/(FP+TN))            0.7617      0.9016     0.3237  5
  FNR (FN/(FN+TP))            0.1742      0.1183     0.2325  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5417      0.5418     0.0280  5
  max valid BA                0.5853      0.5967     0.0368  5
  best valid F1               0.5466      0.5372     0.0191  5
  test BA                     0.5530      0.5600     0.0365  5
  test AUC                    0.5763      0.5846     0.0262  5
  test AUC in-protein         0.6066      0.6160     0.0329  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.5742      0.5751     0.0231  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.4310      0.5347     0.2410  5
  test sensitivity            0.6793      0.8378     0.3866  5
  test specificity            0.4267      0.2822     0.3399  5
  test precision              0.3968      0.3930     0.0221  4
  test loss                   0.6937      0.6934     0.0014  5
  FPR (FP/(FP+TN))            0.5733      0.7178     0.3399  5
  FNR (FN/(FN+TP))            0.3207      0.1622     0.3866  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5160      0.5173     0.0265  5
  max valid BA                0.5485      0.5554     0.0254  5
  best valid F1               0.5211      0.5476     0.0739  5
  test BA                     0.4919      0.4872     0.0182  5
  test AUC                    0.5070      0.5069     0.0455  5
  test AUC in-protein         0.5400      0.6000     0.3368  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.5711      0.5758     0.1694  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.1701      0.2174     0.1022  5
  test sensitivity            0.1226      0.1613     0.0770  5
  test specificity            0.8612      0.8776     0.0940  5
  test precision              0.3636      0.3333     0.0606  4
  test loss                   0.6814      0.6815     0.0113  5
  FPR (FP/(FP+TN))            0.1388      0.1224     0.0940  5
  FNR (FN/(FN+TP))            0.8774      0.8387     0.0770  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5239      0.5212     0.0421  5
  max valid BA                0.5748      0.5773     0.0449  5
  best valid F1               0.6005      0.6286     0.0660  5
  test BA                     0.4646      0.4250     0.0713  5
  test AUC                    0.4906      0.4930     0.0685  5
  test AUC in-protein         0.5136      0.5000     0.0306  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4537      0.3519     0.1900  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4028      0.3750     0.0462  5
  test sensitivity            0.4121      0.3939     0.1365  5
  test specificity            0.5171      0.4146     0.2624  5
  test precision              0.4384      0.3922     0.1020  5
  test loss                   0.6979      0.6940     0.0107  5
  FPR (FP/(FP+TN))            0.4829      0.5854     0.2624  5
  FNR (FN/(FN+TP))            0.5879      0.6061     0.1365  5
```

## AUC vs chemistry null model, in-sample increment

Failed: sphingolipids/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_liphid32 --seeds=0,1,2,3,4`
