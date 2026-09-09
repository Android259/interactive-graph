# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_rankprot_advprot

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_rankprot_advprot'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.5290      0.4590      0.4790      0.6429      0.4602      0.5835
groups_choline            5      0.4847      0.6713      0.5912      0.4551      0.5250      0.6624
groups_phosphorus_free    5      0.2129      0.7673      0.6545      0.4610      0.4933      0.5714
groups_sphingolipids      5      0.5758      0.4000      0.7271      0.3889      0.7030      0.5000
ALL                      20      0.4506      0.5744      0.6130      0.4870      0.5454      0.5793

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5407      0.5193     0.0415  20
max valid BA                0.5624      0.5446     0.0530  20
best valid F1               0.5149      0.5448     0.1405  20
test BA                     0.5125      0.5000     0.0499  20
test AUC                    0.5413      0.5278     0.0707  20
test AUC in-protein         0.5199      0.5000     0.1307  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5468      0.5268     0.1200  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.3432      0.4122     0.2206  20
test sensitivity            0.4506      0.4312     0.3537  20
test specificity            0.5744      0.6369     0.3382  20
test precision              0.3896      0.3957     0.0933  16
test loss                   0.6953      0.6853     0.0775  20
FPR (FP/(FP+TN))            0.4256      0.3631     0.3382  20
FNR (FN/(FN+TP))            0.5494      0.5688     0.3537  20

=== abs(sensitivity-specificity) gap: mean=0.6162 median=0.6133 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5084      0.5112     0.0094  5
  max valid BA                0.5219      0.5148     0.0164  5
  best valid F1               0.5033      0.5054     0.0102  5
  test BA                     0.4940      0.4955     0.0090  5
  test AUC                    0.5197      0.5112     0.0176  5
  test AUC in-protein         0.4914      0.4772     0.0479  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.5271      0.5203     0.0512  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.3393      0.4118     0.2021  5
  test sensitivity            0.5290      0.5269     0.3942  5
  test specificity            0.4590      0.4754     0.4059  5
  test precision              0.3323      0.3321     0.0049  4
  test loss                   0.6780      0.6835     0.0326  5
  FPR (FP/(FP+TN))            0.5410      0.5246     0.4059  5
  FNR (FN/(FN+TP))            0.4710      0.4731     0.3942  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5706      0.5781     0.0427  5
  max valid BA                0.5937      0.6120     0.0615  5
  best valid F1               0.4392      0.5413     0.2458  5
  test BA                     0.5780      0.5892     0.0501  5
  test AUC                    0.6021      0.6450     0.1128  5
  test AUC in-protein         0.6072      0.6652     0.1699  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.6411      0.6656     0.1212  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.3999      0.5073     0.2342  5
  test sensitivity            0.4847      0.4685     0.3495  5
  test specificity            0.6713      0.7921     0.2797  5
  test precision              0.4667      0.4471     0.0630  4
  test loss                   0.6570      0.6481     0.0252  5
  FPR (FP/(FP+TN))            0.3287      0.2079     0.2797  5
  FNR (FN/(FN+TP))            0.5153      0.5315     0.3495  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5148      0.5167     0.0089  5
  max valid BA                0.5324      0.5221     0.0239  5
  best valid F1               0.4954      0.5505     0.0972  5
  test BA                     0.4901      0.5000     0.0256  5
  test AUC                    0.5304      0.5280     0.0345  5
  test AUC in-protein         0.4667      0.5000     0.1683  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.5746      0.5455     0.0854  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.1637      0.0513     0.2302  5
  test sensitivity            0.2129      0.0323     0.3738  5
  test specificity            0.7673      0.8571     0.3575  5
  test precision              0.3003      0.3846     0.1519  3
  test loss                   0.6670      0.6893     0.0678  5
  FPR (FP/(FP+TN))            0.2327      0.1429     0.3575  5
  FNR (FN/(FN+TP))            0.7871      0.9677     0.3738  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5692      0.5746     0.0437  5
  max valid BA                0.6015      0.5958     0.0492  5
  best valid F1               0.6217      0.6292     0.0422  5
  test BA                     0.4879      0.4897     0.0378  5
  test AUC                    0.5131      0.5203     0.0565  5
  test AUC in-protein         0.5142      0.4933     0.0870  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4444      0.3722     0.1348  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4699      0.4819     0.1343  5
  test sensitivity            0.5758      0.6061     0.2786  5
  test specificity            0.4000      0.2683     0.2443  5
  test precision              0.4275      0.4333     0.0329  5
  test loss                   0.7793      0.7482     0.1012  5
  FPR (FP/(FP+TN))            0.6000      0.7317     0.2443  5
  FNR (FN/(FN+TP))            0.4242      0.3939     0.2786  5
```

## AUC vs chemistry null model, in-sample increment

