# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6731      0.7596      0.8978      0.8444      0.7011      0.8044
groups_choline            5      0.5153      0.5337      0.8603      0.7492      0.5536      0.5535
groups_phosphorus_free    5      0.4903      0.5959      0.7250      0.8639      0.6133      0.7143
groups_sphingolipids      5      0.5758      0.7805      0.8919      0.8179      0.5515      0.8850
ALL                      20      0.5636      0.6674      0.8437      0.8188      0.6049      0.7393

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6433      0.6624     0.0934  20
max valid BA                0.6721      0.6973     0.0992  20
best valid F1               0.5989      0.6435     0.1320  20
test BA                     0.6155      0.6208     0.0991  20
test F1                     0.5082      0.5483     0.1930  20
test sensitivity            0.5636      0.6093     0.2181  20
test specificity            0.6674      0.7021     0.2232  20
test precision              0.5391      0.5448     0.1385  18
test loss                   0.8100      0.7721     0.1887  20
FPR (FP/(FP+TN))            0.3326      0.2979     0.2232  20
FNR (FN/(FN+TP))            0.4364      0.3907     0.2181  20

=== abs(sensitivity-specificity) gap: mean=0.2799 median=0.1387 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7433      0.7400     0.0201  5
  max valid BA                0.7527      0.7555     0.0156  5
  best valid F1               0.6736      0.6763     0.0200  5
  test BA                     0.7163      0.7161     0.0313  5
  test F1                     0.6277      0.6243     0.0385  5
  test sensitivity            0.6731      0.6774     0.0472  5
  test specificity            0.7596      0.7268     0.0484  5
  test precision              0.5902      0.5798     0.0519  5
  test loss                   0.8699      0.8878     0.1887  5
  FPR (FP/(FP+TN))            0.2404      0.2732     0.0484  5
  FNR (FN/(FN+TP))            0.3269      0.3226     0.0472  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5412      0.5462     0.0346  5
  max valid BA                0.5535      0.5537     0.0427  5
  best valid F1               0.4663      0.5139     0.1161  5
  test BA                     0.5245      0.5000     0.0613  5
  test F1                     0.3811      0.4481     0.2178  5
  test sensitivity            0.5153      0.6126     0.3088  5
  test specificity            0.5337      0.5446     0.3131  5
  test precision              0.3863      0.3837     0.0580  4
  test loss                   0.7482      0.7187     0.0775  5
  FPR (FP/(FP+TN))            0.4663      0.4554     0.3131  5
  FNR (FN/(FN+TP))            0.4847      0.3874     0.3088  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6404      0.6680     0.0904  5
  max valid BA                0.6638      0.6680     0.1047  5
  best valid F1               0.5886      0.6341     0.1553  5
  test BA                     0.5431      0.5352     0.0529  5
  test F1                     0.4081      0.5000     0.2296  5
  test sensitivity            0.4903      0.5806     0.2797  5
  test specificity            0.5959      0.5306     0.2651  5
  test precision              0.4433      0.4288     0.0615  4
  test loss                   0.9590      0.9840     0.2362  5
  FPR (FP/(FP+TN))            0.4041      0.4694     0.2651  5
  FNR (FN/(FN+TP))            0.5097      0.4194     0.2797  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6481      0.6568     0.0781  5
  max valid BA                0.7183      0.7129     0.0724  5
  best valid F1               0.6670      0.6552     0.0991  5
  test BA                     0.6781      0.6445     0.0675  5
  test F1                     0.6158      0.6061     0.1011  5
  test sensitivity            0.5758      0.5758     0.1589  5
  test specificity            0.7805      0.7805     0.1035  5
  test precision              0.6869      0.6500     0.1018  5
  test loss                   0.6631      0.6604     0.0877  5
  FPR (FP/(FP+TN))            0.2195      0.2195     0.1035  5
  FNR (FN/(FN+TP))            0.4242      0.4242     0.1589  5
```

## AUC vs chemistry null model, in-sample increment

Failed: sphingolipids/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes --seeds=0,1,2,3,4`
