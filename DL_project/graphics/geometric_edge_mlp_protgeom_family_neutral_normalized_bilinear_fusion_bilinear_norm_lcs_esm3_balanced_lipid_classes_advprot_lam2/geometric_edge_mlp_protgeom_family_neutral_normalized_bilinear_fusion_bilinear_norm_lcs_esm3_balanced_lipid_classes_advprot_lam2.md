# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_lam2

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_lam2'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.7957      0.1902      0.5661      0.5394      0.5871      0.4978
groups_choline            5      0.6865      0.4663      0.4243      0.6232      0.7571      0.4772
groups_phosphorus_free    5      0.0323      0.9265      0.5752      0.4989      0.3133      0.7551
groups_sphingolipids      5      0.3636      0.6049      0.5887      0.5637      0.4545      0.7550
ALL                      20      0.4695      0.5470      0.5386      0.5563      0.5280      0.6213

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5517      0.5315     0.0553  20
max valid BA                0.5747      0.5604     0.0516  20
best valid F1               0.5203      0.5458     0.1457  20
test BA                     0.5082      0.5011     0.0552  20
test AUC                    0.5267      0.5143     0.0719  20
test AUC in-protein         0.5775      0.5186     0.1166  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5551      0.6033     0.1166  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.3541      0.4657     0.1919  20
test sensitivity            0.4695      0.4812     0.3330  20
test specificity            0.5470      0.5976     0.3063  20
test precision              0.3662      0.3622     0.0948  18
test loss                   0.6965      0.6935     0.0189  20
FPR (FP/(FP+TN))            0.4530      0.4024     0.3063  20
FNR (FN/(FN+TP))            0.5305      0.5188     0.3330  20

=== abs(sensitivity-specificity) gap: mean=0.5331 median=0.5887 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5189      0.5232     0.0077  5
  max valid BA                0.5424      0.5426     0.0125  5
  best valid F1               0.5131      0.5111     0.0046  5
  test BA                     0.4929      0.5022     0.0367  5
  test AUC                    0.4961      0.4936     0.0330  5
  test AUC in-protein         0.4766      0.4869     0.0346  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.4850      0.4807     0.0368  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.4658      0.4836     0.0504  5
  test sensitivity            0.7957      0.8495     0.1567  5
  test specificity            0.1902      0.1858     0.0977  5
  test precision              0.3309      0.3383     0.0240  5
  test loss                   0.7171      0.7123     0.0230  5
  FPR (FP/(FP+TN))            0.8098      0.8142     0.0977  5
  FNR (FN/(FN+TP))            0.2043      0.1505     0.1567  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5840      0.5435     0.0592  5
  max valid BA                0.6172      0.6027     0.0371  5
  best valid F1               0.5653      0.5623     0.0317  5
  test BA                     0.5764      0.5844     0.0226  5
  test AUC                    0.6135      0.6249     0.0273  5
  test AUC in-protein         0.6654      0.6794     0.0347  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.6209      0.6280     0.0171  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.5105      0.5126     0.0319  5
  test sensitivity            0.6865      0.6396     0.2138  5
  test specificity            0.4663      0.5297     0.2533  5
  test precision              0.4285      0.4277     0.0460  5
  test loss                   0.6950      0.6929     0.0057  5
  FPR (FP/(FP+TN))            0.5337      0.4703     0.2533  5
  FNR (FN/(FN+TP))            0.3135      0.3604     0.2138  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5214      0.5221     0.0108  5
  max valid BA                0.5342      0.5333     0.0233  5
  best valid F1               0.3753      0.5238     0.2334  5
  test BA                     0.4794      0.4812     0.0212  5
  test AUC                    0.5158      0.5049     0.0517  5
  test AUC in-protein         0.6600      0.6667     0.1584  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.6471      0.6364     0.0515  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.0516      0.0526     0.0514  5
  test sensitivity            0.0323      0.0323     0.0323  5
  test specificity            0.9265      0.8980     0.0686  5
  test precision              0.2169      0.2222     0.0716  3
  test loss                   0.6779      0.6828     0.0098  5
  FPR (FP/(FP+TN))            0.0735      0.1020     0.0686  5
  FNR (FN/(FN+TP))            0.9677      0.9677     0.0323  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5823      0.5542     0.0766  5
  max valid BA                0.6048      0.5943     0.0620  5
  best valid F1               0.6276      0.6279     0.0450  5
  test BA                     0.4843      0.4993     0.0657  5
  test AUC                    0.4814      0.4715     0.0820  5
  test AUC in-protein         0.5080      0.5041     0.0102  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4672      0.3812     0.1689  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3883      0.3509     0.0821  5
  test sensitivity            0.3636      0.3333     0.1028  5
  test specificity            0.6049      0.6098     0.1248  5
  test precision              0.4288      0.4444     0.0701  5
  test loss                   0.6960      0.7008     0.0086  5
  FPR (FP/(FP+TN))            0.3951      0.3902     0.1248  5
  FNR (FN/(FN+TP))            0.6364      0.6667     0.1028  5
```

## AUC vs chemistry null model, in-sample increment

Failed: sphingolipids/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_lam2 --seeds=0,1,2,3,4`
