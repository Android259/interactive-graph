# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_heads2

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_heads2'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.8237      0.1803      0.6071      0.5669      0.7935      0.2868
groups_choline            5      0.7874      0.3149      0.4019      0.6235      0.6161      0.5941
groups_phosphorus_free    5      0.0839      0.8571      0.4293      0.6621      0.1867      0.8735
groups_sphingolipids      5      0.2242      0.7171      0.5796      0.5770      0.5152      0.6500
ALL                      20      0.4798      0.5173      0.5045      0.6074      0.5279      0.6011

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5421      0.5240     0.0429  20
max valid BA                0.5645      0.5514     0.0420  20
best valid F1               0.5083      0.5369     0.1516  20
test BA                     0.4986      0.5000     0.0493  20
test AUC                    0.5160      0.4998     0.0678  20
test AUC in-protein         0.5311      0.5342     0.1779  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5306      0.5693     0.1158  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.3396      0.3895     0.1934  20
test sensitivity            0.4798      0.4595     0.3642  20
test specificity            0.5173      0.5495     0.3307  20
test precision              0.3542      0.3491     0.0674  17
test loss                   0.7005      0.6938     0.0245  20
FPR (FP/(FP+TN))            0.4827      0.4505     0.3307  20
FNR (FN/(FN+TP))            0.5202      0.5405     0.3642  20

=== abs(sensitivity-specificity) gap: mean=0.5968 median=0.5778 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5290      0.5253     0.0143  5
  max valid BA                0.5402      0.5383     0.0116  5
  best valid F1               0.5176      0.5217     0.0066  5
  test BA                     0.5020      0.5193     0.0292  5
  test AUC                    0.4920      0.4787     0.0414  5
  test AUC in-protein         0.4968      0.4891     0.0331  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.4893      0.4774     0.0364  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.4755      0.4985     0.0452  5
  test sensitivity            0.8237      0.8710     0.1656  5
  test specificity            0.1803      0.1749     0.1162  5
  test precision              0.3362      0.3460     0.0177  5
  test loss                   0.7285      0.7504     0.0313  5
  FPR (FP/(FP+TN))            0.8197      0.8251     0.1162  5
  FNR (FN/(FN+TP))            0.1763      0.1290     0.1656  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5643      0.5227     0.0700  5
  max valid BA                0.6051      0.6079     0.0484  5
  best valid F1               0.5529      0.5388     0.0329  5
  test BA                     0.5511      0.5576     0.0412  5
  test AUC                    0.5966      0.5999     0.0531  5
  test AUC in-protein         0.6377      0.6522     0.0456  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.5913      0.5902     0.0358  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.5175      0.5226     0.0211  5
  test sensitivity            0.7874      0.7387     0.1755  5
  test specificity            0.3149      0.2970     0.2414  5
  test precision              0.3954      0.3852     0.0389  5
  test loss                   0.6936      0.6939     0.0080  5
  FPR (FP/(FP+TN))            0.6851      0.7030     0.2414  5
  FNR (FN/(FN+TP))            0.2126      0.2613     0.1755  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5244      0.5221     0.0250  5
  max valid BA                0.5301      0.5313     0.0222  5
  best valid F1               0.3565      0.5208     0.2529  5
  test BA                     0.4705      0.4608     0.0293  5
  test AUC                    0.4843      0.4957     0.0219  5
  test AUC in-protein         0.4722      0.6111     0.3559  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.5701      0.5938     0.1340  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.1062      0.1000     0.1131  5
  test sensitivity            0.0839      0.0645     0.0957  5
  test specificity            0.8571      0.8571     0.1436  5
  test precision              0.2586      0.2353     0.0520  3
  test loss                   0.6798      0.6850     0.0107  5
  FPR (FP/(FP+TN))            0.1429      0.1429     0.1436  5
  FNR (FN/(FN+TP))            0.9161      0.9355     0.0957  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5510      0.5515     0.0412  5
  max valid BA                0.5826      0.5852     0.0269  5
  best valid F1               0.6063      0.6226     0.0260  5
  test BA                     0.4707      0.4930     0.0521  5
  test AUC                    0.4909      0.4856     0.0768  5
  test AUC in-protein         0.5177      0.5117     0.0184  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4715      0.3842     0.1733  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.2592      0.3284     0.1535  5
  test sensitivity            0.2242      0.3030     0.1382  5
  test specificity            0.7171      0.7317     0.1993  5
  test precision              0.3969      0.3939     0.0708  4
  test loss                   0.7000      0.7017     0.0110  5
  FPR (FP/(FP+TN))            0.2829      0.2683     0.1993  5
  FNR (FN/(FN+TP))            0.7758      0.6970     0.1382  5
```

## AUC vs chemistry null model, in-sample increment

Failed: sphingolipids/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_heads2 --seeds=0,1,2,3,4`
