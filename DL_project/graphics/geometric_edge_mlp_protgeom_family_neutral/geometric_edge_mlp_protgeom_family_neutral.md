# geometric_edge_mlp_protgeom_family_neutral

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.7433      0.3705      0.6903      0.5896      0.7851      0.4032
groups_GLTP            5      0.5760      0.4640      0.7786      0.5583      0.6385      0.5692
groups_IP_trans        5      0.4087      0.7404      0.6623      0.6785      0.5583      0.7745
groups_LBP_BPI_CETP    5      0.1130      0.8851      0.6639      0.6085      0.2250      0.8809
groups_START           5      0.6738      0.4067      0.8567      0.5939      0.7531      0.3933
groups_lipocalin       5      0.6389      0.4694      0.7009      0.5294      0.6667      0.4944
groups_scp2            5      0.6353      0.5412      0.7716      0.5755      0.7294      0.6412
ALL                   35      0.5413      0.5539      0.7320      0.5905      0.6223      0.5938

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6081      0.6029     0.0746  35
max valid BA                0.6467      0.6346     0.0722  35
best valid F1               0.6196      0.6310     0.0973  35
test BA                     0.5476      0.5417     0.0623  35
test F1                     0.4419      0.4965     0.1958  35
test sensitivity            0.5413      0.5294     0.3211  35
test specificity            0.5539      0.5833     0.2975  35
test precision              0.4519      0.4634     0.1356  35
test loss                   0.7699      0.7173     0.1969  35
FPR (FP/(FP+TN))            0.4461      0.4167     0.2975  35
FNR (FN/(FN+TP))            0.4587      0.4706     0.3211  35

=== abs(sensitivity-specificity) gap: mean=0.5061 median=0.4000 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5942      0.6017     0.0435  5
  max valid BA                0.6110      0.6223     0.0469  5
  best valid F1               0.7161      0.7159     0.0145  5
  test BA                     0.5569      0.5542     0.0178  5
  test F1                     0.6272      0.6364     0.0996  5
  test sensitivity            0.7433      0.7313     0.2394  5
  test specificity            0.3705      0.3770     0.2053  5
  test precision              0.5653      0.5652     0.0058  5
  test loss                   0.6886      0.6878     0.0106  5
  FPR (FP/(FP+TN))            0.6295      0.6230     0.2053  5
  FNR (FN/(FN+TP))            0.2567      0.2687     0.2394  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6038      0.6154     0.0674  5
  max valid BA                0.6269      0.6154     0.0752  5
  best valid F1               0.6846      0.6761     0.0217  5
  test BA                     0.5200      0.4800     0.1030  5
  test F1                     0.5228      0.5128     0.1540  5
  test sensitivity            0.5760      0.5200     0.2780  5
  test specificity            0.4640      0.4400     0.2920  5
  test precision              0.5273      0.4889     0.1292  5
  test loss                   0.7617      0.7520     0.0445  5
  FPR (FP/(FP+TN))            0.5360      0.5600     0.2920  5
  FNR (FN/(FN+TP))            0.4240      0.4800     0.2780  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6664      0.6640     0.0703  5
  max valid BA                0.6971      0.6941     0.0503  5
  best valid F1               0.6108      0.6129     0.0562  5
  test BA                     0.5746      0.5657     0.0597  5
  test F1                     0.3818      0.3636     0.1584  5
  test sensitivity            0.4087      0.3478     0.2811  5
  test specificity            0.7404      0.7234     0.1833  5
  test precision              0.4552      0.4286     0.1284  5
  test loss                   0.7037      0.7171     0.0641  5
  FPR (FP/(FP+TN))            0.2596      0.2766     0.1833  5
  FNR (FN/(FN+TP))            0.5913      0.6522     0.2811  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5529      0.5408     0.0396  5
  max valid BA                0.6453      0.6609     0.0704  5
  best valid F1               0.5152      0.5818     0.1737  5
  test BA                     0.4991      0.5046     0.0142  5
  test F1                     0.1218      0.0800     0.1468  5
  test sensitivity            0.1130      0.0435     0.1808  5
  test specificity            0.8851      0.9787     0.1758  5
  test precision              0.3067      0.3333     0.2127  5
  test loss                   1.1012      1.0293     0.3833  5
  FPR (FP/(FP+TN))            0.1149      0.0213     0.1758  5
  FNR (FN/(FN+TP))            0.8870      0.9565     0.1808  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5732      0.5741     0.0395  5
  max valid BA                0.6028      0.5936     0.0248  5
  best valid F1               0.6128      0.6263     0.0267  5
  test BA                     0.5403      0.5402     0.0530  5
  test F1                     0.5257      0.5882     0.1119  5
  test sensitivity            0.6738      0.6923     0.2598  5
  test specificity            0.4067      0.5169     0.2004  5
  test precision              0.4477      0.4444     0.0478  5
  test loss                   0.7558      0.7578     0.0506  5
  FPR (FP/(FP+TN))            0.5933      0.4831     0.2004  5
  FNR (FN/(FN+TP))            0.3262      0.3077     0.2598  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5806      0.5347     0.0987  5
  max valid BA                0.6292      0.6181     0.1069  5
  best valid F1               0.5628      0.5147     0.0846  5
  test BA                     0.5542      0.5417     0.0614  5
  test F1                     0.4398      0.4935     0.1406  5
  test sensitivity            0.6389      0.6667     0.3464  5
  test specificity            0.4694      0.5833     0.4097  5
  test precision              0.4476      0.4444     0.1371  5
  test loss                   0.6900      0.6734     0.0366  5
  FPR (FP/(FP+TN))            0.5306      0.4167     0.4097  5
  FNR (FN/(FN+TP))            0.3611      0.3333     0.3464  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6853      0.6618     0.0694  5
  max valid BA                0.7147      0.6912     0.0556  5
  best valid F1               0.6346      0.6154     0.0594  5
  test BA                     0.5882      0.6029     0.0682  5
  test F1                     0.4740      0.5231     0.1395  5
  test sensitivity            0.6353      0.7059     0.3068  5
  test specificity            0.5412      0.6471     0.2886  5
  test precision              0.4135      0.4062     0.0726  5
  test loss                   0.6882      0.6569     0.0698  5
  FPR (FP/(FP+TN))            0.4588      0.3529     0.2886  5
  FNR (FN/(FN+TP))            0.3647      0.2941     0.3068  5
```

## AUC vs chemistry null model, in-sample increment

