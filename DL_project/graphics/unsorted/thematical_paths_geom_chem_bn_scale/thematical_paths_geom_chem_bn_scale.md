# thematical_paths_geom_chem_bn_scale

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'thematical_paths_geom_chem_bn_scale'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.3612      0.6623      0.8160      0.6297      0.4119      0.6742
groups_GLTP            5      0.5120      0.5680      0.6053      0.6075      0.5385      0.6154
groups_IP_trans        5      0.3652      0.6553      0.5785      0.7848      0.4083      0.7149
groups_LBP_BPI_CETP    5      0.2174      0.9404      0.5392      0.8343      0.2667      0.9106
groups_START           5      0.5385      0.5596      0.7358      0.6102      0.5062      0.5663
groups_lipocalin       5      0.5889      0.4056      0.6538      0.4914      0.6222      0.4278
groups_scp2            5      0.4235      0.5353      0.6378      0.4927      0.4941      0.5588
ALL                   35      0.4295      0.6181      0.6523      0.6358      0.4640      0.6383

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5478      0.5299     0.0562  35
max valid BA                0.5741      0.5456     0.0762  35
best valid F1               0.4885      0.5306     0.2162  35
test BA                     0.5238      0.5000     0.0522  35
test F1                     0.3413      0.3824     0.2267  35
test sensitivity            0.4295      0.3478     0.3805  35
test specificity            0.6181      0.7941     0.3929  35
test precision              0.4442      0.4681     0.1900  29
test loss                   0.7420      0.6945     0.1460  35
FPR (FP/(FP+TN))            0.3819      0.2059     0.3929  35
FNR (FN/(FN+TP))            0.5705      0.6522     0.3805  35

=== abs(sensitivity-specificity) gap: mean=0.7158 median=0.8001 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5431      0.5486     0.0365  5
  max valid BA                0.5594      0.5767     0.0492  5
  best valid F1               0.6104      0.6837     0.1347  5
  test BA                     0.5117      0.5031     0.0389  5
  test F1                     0.3326      0.2250     0.2880  5
  test sensitivity            0.3612      0.1343     0.4178  5
  test specificity            0.6623      0.9016     0.4020  5
  test precision              0.4678      0.5385     0.2697  5
  test loss                   0.9385      0.9149     0.2899  5
  FPR (FP/(FP+TN))            0.3377      0.0984     0.4020  5
  FNR (FN/(FN+TP))            0.6388      0.8657     0.4178  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5538      0.5385     0.0712  5
  max valid BA                0.5885      0.5577     0.0986  5
  best valid F1               0.5386      0.6667     0.3012  5
  test BA                     0.5400      0.5200     0.0469  5
  test F1                     0.4340      0.4615     0.2743  5
  test sensitivity            0.5120      0.3600     0.4467  5
  test specificity            0.5680      0.8000     0.4886  5
  test precision              0.6277      0.5767     0.1662  4
  test loss                   0.7125      0.7044     0.0244  5
  FPR (FP/(FP+TN))            0.4320      0.2000     0.4886  5
  FNR (FN/(FN+TP))            0.4880      0.6400     0.4467  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5616      0.5913     0.0568  5
  max valid BA                0.6130      0.6423     0.0657  5
  best valid F1               0.4311      0.5306     0.2412  5
  test BA                     0.5103      0.5037     0.0148  5
  test F1                     0.2824      0.3404     0.1829  5
  test sensitivity            0.3652      0.3043     0.3798  5
  test specificity            0.6553      0.7660     0.3869  5
  test precision              0.3536      0.3485     0.0282  4
  test loss                   0.7001      0.6833     0.0809  5
  FPR (FP/(FP+TN))            0.3447      0.2340     0.3869  5
  FNR (FN/(FN+TP))            0.6348      0.6957     0.3798  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5887      0.6232     0.0824  5
  max valid BA                0.6096      0.6556     0.1038  5
  best valid F1               0.4405      0.5053     0.2520  5
  test BA                     0.5789      0.5879     0.0768  5
  test F1                     0.2753      0.3636     0.2580  5
  test sensitivity            0.2174      0.2609     0.2085  5
  test specificity            0.9404      0.9149     0.0571  5
  test precision              0.6391      0.6250     0.0477  3
  test loss                   0.6284      0.6188     0.0410  5
  FPR (FP/(FP+TN))            0.0596      0.0851     0.0571  5
  FNR (FN/(FN+TP))            0.7826      0.7391     0.2085  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5363      0.5299     0.0437  5
  max valid BA                0.5702      0.5373     0.0872  5
  best valid F1               0.5885      0.5899     0.0709  5
  test BA                     0.5490      0.5296     0.0476  5
  test F1                     0.4799      0.5278     0.1080  5
  test sensitivity            0.5385      0.5077     0.2884  5
  test specificity            0.5596      0.7191     0.3274  5
  test precision              0.4892      0.4810     0.0613  5
  test loss                   0.7059      0.7184     0.0216  5
  FPR (FP/(FP+TN))            0.4404      0.2809     0.3274  5
  FNR (FN/(FN+TP))            0.4615      0.4923     0.2884  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5250      0.5000     0.0356  5
  max valid BA                0.5458      0.5000     0.0639  5
  best valid F1               0.4102      0.5000     0.2304  5
  test BA                     0.4972      0.5000     0.0395  5
  test F1                     0.3542      0.3889     0.2061  5
  test sensitivity            0.5889      0.5833     0.4292  5
  test specificity            0.4056      0.2917     0.4485  5
  test precision              0.3411      0.3333     0.0476  4
  test loss                   0.7445      0.7392     0.0746  5
  FPR (FP/(FP+TN))            0.5944      0.7083     0.4485  5
  FNR (FN/(FN+TP))            0.4111      0.4167     0.4292  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5265      0.5000     0.0592  5
  max valid BA                0.5324      0.5147     0.0564  5
  best valid F1               0.4000      0.5000     0.2236  5
  test BA                     0.4794      0.5000     0.0287  5
  test F1                     0.2308      0.1538     0.2537  5
  test sensitivity            0.4235      0.1176     0.5284  5
  test specificity            0.5353      0.7941     0.4941  5
  test precision              0.2222      0.2778     0.1571  4
  test loss                   0.7638      0.7364     0.1110  5
  FPR (FP/(FP+TN))            0.4647      0.2059     0.4941  5
  FNR (FN/(FN+TP))            0.5765      0.8824     0.5284  5
```

## AUC vs chemistry null model, in-sample increment

