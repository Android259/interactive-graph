# thematical_paths_geom_chem

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'thematical_paths_geom_chem'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.2239      0.7639      0.8000      0.7764      0.2806      0.8000
groups_GLTP            5      0.4880      0.5520      0.5804      0.6110      0.5385      0.5692
groups_IP_trans        5      0.4522      0.6766      0.5747      0.7964      0.4417      0.6809
groups_LBP_BPI_CETP    5      0.0522      0.9660      0.5191      0.8541      0.1583      0.9617
groups_START           5      0.4492      0.6697      0.7256      0.7481      0.4281      0.6831
groups_lipocalin       5      0.5722      0.4222      0.6385      0.5804      0.6000      0.4556
groups_scp2            5      0.3059      0.6353      0.6245      0.6628      0.4000      0.6647
ALL                   35      0.3634      0.6694      0.6375      0.7185      0.4067      0.6879

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5473      0.5400     0.0481  35
max valid BA                0.5726      0.5650     0.0715  35
best valid F1               0.4863      0.5075     0.2203  35
test BA                     0.5164      0.5000     0.0481  35
test F1                     0.3031      0.3333     0.2202  35
test sensitivity            0.3634      0.2615     0.3481  35
test specificity            0.6694      0.7528     0.3329  35
test precision              0.4342      0.4595     0.1788  29
test loss                   0.7931      0.7053     0.1786  35
FPR (FP/(FP+TN))            0.3306      0.2472     0.3329  35
FNR (FN/(FN+TP))            0.6366      0.7385     0.3481  35

=== abs(sensitivity-specificity) gap: mean=0.6543 median=0.7941 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5403      0.5402     0.0168  5
  max valid BA                0.5518      0.5563     0.0265  5
  best valid F1               0.5767      0.6837     0.1625  5
  test BA                     0.4939      0.4831     0.0280  5
  test F1                     0.2906      0.3000     0.1589  5
  test sensitivity            0.2239      0.2239     0.1352  5
  test specificity            0.7639      0.7049     0.1262  5
  test precision              0.4613      0.5000     0.1554  5
  test loss                   0.9992      1.0297     0.2545  5
  FPR (FP/(FP+TN))            0.2361      0.2951     0.1262  5
  FNR (FN/(FN+TP))            0.7761      0.7761     0.1352  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5538      0.5385     0.0599  5
  max valid BA                0.6192      0.5962     0.1286  5
  best valid F1               0.5751      0.6842     0.3245  5
  test BA                     0.5200      0.5000     0.0346  5
  test F1                     0.3884      0.4615     0.3078  5
  test sensitivity            0.4880      0.3600     0.4861  5
  test specificity            0.5520      0.8000     0.4910  5
  test precision              0.5383      0.5051     0.0699  4
  test loss                   0.6995      0.6992     0.0053  5
  FPR (FP/(FP+TN))            0.4480      0.2000     0.4910  5
  FNR (FN/(FN+TP))            0.5120      0.6400     0.4861  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5613      0.5465     0.0507  5
  max valid BA                0.5978      0.5891     0.0689  5
  best valid F1               0.4273      0.5053     0.2406  5
  test BA                     0.5644      0.5518     0.0527  5
  test F1                     0.3676      0.4483     0.2166  5
  test sensitivity            0.4522      0.5652     0.3320  5
  test specificity            0.6766      0.7234     0.3044  5
  test precision              0.4435      0.4357     0.0935  4
  test loss                   0.7377      0.6932     0.1227  5
  FPR (FP/(FP+TN))            0.3234      0.2766     0.3044  5
  FNR (FN/(FN+TP))            0.5478      0.4348     0.3320  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5600      0.5417     0.0814  5
  max valid BA                0.5759      0.5603     0.0972  5
  best valid F1               0.4339      0.5053     0.2510  5
  test BA                     0.5091      0.5000     0.0178  5
  test F1                     0.0847      0.0833     0.0889  5
  test sensitivity            0.0522      0.0435     0.0567  5
  test specificity            0.9660      1.0000     0.0490  5
  test precision              0.5952      0.5000     0.3665  3
  test loss                   0.7890      0.6897     0.1570  5
  FPR (FP/(FP+TN))            0.0340      0.0000     0.0490  5
  FNR (FN/(FN+TP))            0.9478      0.9565     0.0567  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5556      0.5348     0.0572  5
  max valid BA                0.5890      0.6022     0.0407  5
  best valid F1               0.5883      0.5899     0.0147  5
  test BA                     0.5594      0.5714     0.0660  5
  test F1                     0.4509      0.4793     0.1504  5
  test sensitivity            0.4492      0.4462     0.2236  5
  test specificity            0.6697      0.6966     0.1347  5
  test precision              0.4843      0.4845     0.0795  5
  test loss                   0.7335      0.7153     0.0615  5
  FPR (FP/(FP+TN))            0.3303      0.3034     0.1347  5
  FNR (FN/(FN+TP))            0.5508      0.5538     0.2236  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5278      0.5278     0.0282  5
  max valid BA                0.5306      0.5278     0.0328  5
  best valid F1               0.4015      0.5000     0.2245  5
  test BA                     0.4972      0.5000     0.0174  5
  test F1                     0.3475      0.4151     0.2055  5
  test sensitivity            0.5722      0.6111     0.4247  5
  test specificity            0.4222      0.3333     0.4368  5
  test precision              0.3361      0.3317     0.0220  4
  test loss                   0.7622      0.7077     0.1462  5
  FPR (FP/(FP+TN))            0.5778      0.6667     0.4368  5
  FNR (FN/(FN+TP))            0.4278      0.3889     0.4247  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5324      0.5294     0.0335  5
  max valid BA                0.5441      0.5735     0.0403  5
  best valid F1               0.4015      0.5000     0.2245  5
  test BA                     0.4706      0.4706     0.0312  5
  test F1                     0.1918      0.0870     0.2302  5
  test sensitivity            0.3059      0.0588     0.4351  5
  test specificity            0.6353      0.8529     0.4057  5
  test precision              0.2019      0.2372     0.1533  4
  test loss                   0.8310      0.7364     0.2569  5
  FPR (FP/(FP+TN))            0.3647      0.1471     0.4057  5
  FNR (FN/(FN+TP))            0.6941      0.9412     0.4351  5
```

## AUC vs chemistry null model, in-sample increment

