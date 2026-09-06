# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_edge_rbf6

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_edge_rbf6'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5343      0.6590      0.6771      0.7294      0.5224      0.6355
groups_GLTP            5      0.2080      0.6960      0.5534      0.6238      0.3308      0.7692
groups_IP_trans        5      0.3739      0.8128      0.6865      0.6529      0.4750      0.8170
groups_LBP_BPI_CETP    5      0.1913      0.9404      0.6881      0.6454      0.2667      0.8766
groups_START           5      0.1200      0.8112      0.6669      0.5969      0.1844      0.8067
groups_lipocalin       5      0.2611      0.8250      0.5927      0.6511      0.2500      0.8417
groups_scp2            5      0.4000      0.7471      0.6667      0.6905      0.4706      0.7706
ALL                   35      0.2984      0.7845      0.6473      0.6557      0.3571      0.7882

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5736      0.5632     0.0645  35
max valid BA                0.6093      0.6029     0.0711  35
best valid F1               0.5104      0.5417     0.1323  35
test BA                     0.5414      0.5284     0.0872  35
test F1                     0.3268      0.3000     0.2041  35
test sensitivity            0.2984      0.2400     0.2355  35
test specificity            0.7845      0.8085     0.1544  35
test precision              0.4446      0.4792     0.1901  34
test loss                   0.7029      0.6833     0.1164  35
FPR (FP/(FP+TN))            0.2155      0.1915     0.1544  35
FNR (FN/(FN+TP))            0.7016      0.7600     0.2355  35

=== abs(sensitivity-specificity) gap: mean=0.5347 median=0.5226 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5789      0.5632     0.0271  5
  max valid BA                0.6116      0.5898     0.0399  5
  best valid F1               0.6425      0.6628     0.0768  5
  test BA                     0.5967      0.5747     0.0538  5
  test F1                     0.5547      0.5088     0.1405  5
  test sensitivity            0.5343      0.4328     0.2567  5
  test specificity            0.6590      0.7049     0.1677  5
  test precision              0.6361      0.6389     0.0319  5
  test loss                   0.6905      0.6851     0.0206  5
  FPR (FP/(FP+TN))            0.3410      0.2951     0.1677  5
  FNR (FN/(FN+TP))            0.4657      0.5672     0.2567  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5385     0.0172  5
  max valid BA                0.5577      0.5577     0.0236  5
  best valid F1               0.4940      0.5000     0.0901  5
  test BA                     0.4520      0.4400     0.0268  5
  test F1                     0.2398      0.3000     0.1731  5
  test sensitivity            0.2080      0.2400     0.1730  5
  test specificity            0.6960      0.6400     0.2184  5
  test precision              0.3258      0.4000     0.1832  5
  test loss                   0.7441      0.7073     0.0891  5
  FPR (FP/(FP+TN))            0.3040      0.3600     0.2184  5
  FNR (FN/(FN+TP))            0.7920      0.7600     0.1730  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6460      0.6241     0.0408  5
  max valid BA                0.6950      0.6946     0.0406  5
  best valid F1               0.6031      0.6000     0.0522  5
  test BA                     0.5933      0.6216     0.0830  5
  test F1                     0.4058      0.4762     0.1639  5
  test sensitivity            0.3739      0.4348     0.2030  5
  test specificity            0.8128      0.8085     0.0571  5
  test precision              0.4716      0.5263     0.1148  5
  test loss                   0.6327      0.6375     0.0222  5
  FPR (FP/(FP+TN))            0.1872      0.1915     0.0571  5
  FNR (FN/(FN+TP))            0.6261      0.5652     0.2030  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5716      0.5519     0.0646  5
  max valid BA                0.6252      0.6144     0.0595  5
  best valid F1               0.4719      0.4255     0.1102  5
  test BA                     0.5659      0.5328     0.0811  5
  test F1                     0.2461      0.1538     0.2411  5
  test sensitivity            0.1913      0.0870     0.2099  5
  test specificity            0.9404      0.9787     0.0530  5
  test precision              0.4851      0.5714     0.2815  5
  test loss                   0.6212      0.6011     0.0328  5
  FPR (FP/(FP+TN))            0.0596      0.0213     0.0530  5
  FNR (FN/(FN+TP))            0.8087      0.9130     0.2099  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4956      0.5000     0.0157  5
  max valid BA                0.5446      0.5141     0.0653  5
  best valid F1               0.4261      0.4148     0.1538  5
  test BA                     0.4656      0.4681     0.0510  5
  test F1                     0.1624      0.1957     0.1022  5
  test sensitivity            0.1200      0.1385     0.0780  5
  test specificity            0.8112      0.7978     0.1464  5
  test precision              0.3375      0.3021     0.1322  4
  test loss                   0.8354      0.7152     0.2382  5
  FPR (FP/(FP+TN))            0.1888      0.2022     0.1464  5
  FNR (FN/(FN+TP))            0.8800      0.8615     0.0780  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5528      0.5139     0.0973  5
  max valid BA                0.5778      0.5417     0.0918  5
  best valid F1               0.3923      0.3551     0.1755  5
  test BA                     0.5431      0.5069     0.1168  5
  test F1                     0.2892      0.2000     0.2273  5
  test sensitivity            0.2611      0.1389     0.2595  5
  test specificity            0.8250      0.8194     0.0375  5
  test precision              0.3603      0.3571     0.1827  5
  test loss                   0.7193      0.6818     0.0898  5
  FPR (FP/(FP+TN))            0.1750      0.1806     0.0375  5
  FNR (FN/(FN+TP))            0.7389      0.8611     0.2595  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6206      0.6176     0.0242  5
  max valid BA                0.6529      0.6618     0.0354  5
  best valid F1               0.5433      0.5600     0.0552  5
  test BA                     0.5735      0.5882     0.0698  5
  test F1                     0.3899      0.4848     0.1625  5
  test sensitivity            0.4000      0.4706     0.2475  5
  test specificity            0.7471      0.7647     0.1796  5
  test precision              0.4744      0.5000     0.1913  5
  test loss                   0.6774      0.6642     0.0237  5
  FPR (FP/(FP+TN))            0.2529      0.2353     0.1796  5
  FNR (FN/(FN+TP))            0.6000      0.5294     0.2475  5
```

## AUC vs chemistry null model, in-sample increment

