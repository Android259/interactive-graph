# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_bilinear_wd01

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_bilinear_wd01'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4507      0.7246      0.7166      0.6818      0.4597      0.7161
groups_GLTP            5      0.2720      0.6240      0.5247      0.6475      0.3923      0.7000
groups_IP_trans        5      0.4435      0.7872      0.6512      0.6821      0.5167      0.7872
groups_LBP_BPI_CETP    5      0.3565      0.8426      0.7330      0.6018      0.4583      0.8043
groups_START           5      0.0708      0.9281      0.5809      0.7014      0.0844      0.9438
groups_lipocalin       5      0.0722      0.9306      0.6006      0.7251      0.1111      0.9306
groups_scp2            5      0.2706      0.8588      0.6370      0.6413      0.3412      0.8588
ALL                   35      0.2766      0.8137      0.6349      0.6687      0.3377      0.8201

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5789      0.5694     0.0652  35
max valid BA                0.6064      0.5962     0.0702  35
best valid F1               0.5210      0.5574     0.1475  35
test BA                     0.5452      0.5333     0.0749  35
test F1                     0.3109      0.3175     0.2027  35
test sensitivity            0.2766      0.2400     0.2259  35
test specificity            0.8137      0.8511     0.1582  35
test precision              0.4647      0.4725     0.1857  32
test loss                   0.6890      0.6764     0.0629  35
FPR (FP/(FP+TN))            0.1863      0.1489     0.1582  35
FNR (FN/(FN+TP))            0.7234      0.7600     0.2259  35

=== abs(sensitivity-specificity) gap: mean=0.5879 median=0.5902 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5879      0.5892     0.0315  5
  max valid BA                0.6033      0.6056     0.0323  5
  best valid F1               0.6792      0.6901     0.0258  5
  test BA                     0.5877      0.5964     0.0538  5
  test F1                     0.5262      0.4854     0.0814  5
  test sensitivity            0.4507      0.4030     0.0987  5
  test specificity            0.7246      0.7213     0.0618  5
  test precision              0.6416      0.6415     0.0642  5
  test loss                   0.6899      0.6923     0.0162  5
  FPR (FP/(FP+TN))            0.2754      0.2787     0.0618  5
  FNR (FN/(FN+TP))            0.5493      0.5970     0.0987  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5462      0.5385     0.0219  5
  max valid BA                0.5654      0.5577     0.0322  5
  best valid F1               0.5477      0.5574     0.1299  5
  test BA                     0.4480      0.4600     0.0179  5
  test F1                     0.3083      0.2703     0.1264  5
  test sensitivity            0.2720      0.2000     0.1863  5
  test specificity            0.6240      0.6800     0.1757  5
  test precision              0.4037      0.4000     0.0484  5
  test loss                   0.7213      0.7224     0.0250  5
  FPR (FP/(FP+TN))            0.3760      0.3200     0.1757  5
  FNR (FN/(FN+TP))            0.7280      0.8000     0.1863  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6520      0.6551     0.0622  5
  max valid BA                0.6895      0.6955     0.0544  5
  best valid F1               0.5902      0.6000     0.0692  5
  test BA                     0.6154      0.6004     0.0575  5
  test F1                     0.4470      0.4545     0.1226  5
  test sensitivity            0.4435      0.4348     0.2409  5
  test specificity            0.7872      0.8085     0.1346  5
  test precision              0.5200      0.4872     0.0677  5
  test loss                   0.6979      0.6456     0.1118  5
  FPR (FP/(FP+TN))            0.2128      0.1915     0.1346  5
  FNR (FN/(FN+TP))            0.5565      0.5652     0.2409  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6313      0.6609     0.0692  5
  max valid BA                0.6363      0.6853     0.0727  5
  best valid F1               0.4969      0.5854     0.1621  5
  test BA                     0.5995      0.6203     0.0879  5
  test F1                     0.3597      0.4242     0.2538  5
  test sensitivity            0.3565      0.3043     0.3274  5
  test specificity            0.8426      0.9362     0.2115  5
  test precision              0.4675      0.5000     0.2880  5
  test loss                   0.6490      0.6430     0.0594  5
  FPR (FP/(FP+TN))            0.1574      0.0638     0.2115  5
  FNR (FN/(FN+TP))            0.6435      0.6957     0.3274  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5141      0.5126     0.0178  5
  max valid BA                0.5508      0.5332     0.0695  5
  best valid F1               0.4571      0.4737     0.1574  5
  test BA                     0.4994      0.5000     0.0350  5
  test F1                     0.1083      0.0800     0.1175  5
  test sensitivity            0.0708      0.0462     0.0781  5
  test specificity            0.9281      0.9551     0.0975  5
  test precision              0.4456      0.3226     0.2329  3
  test loss                   0.7398      0.7000     0.0828  5
  FPR (FP/(FP+TN))            0.0719      0.0449     0.0975  5
  FNR (FN/(FN+TP))            0.9292      0.9538     0.0781  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5208      0.5069     0.0295  5
  max valid BA                0.5583      0.5486     0.0590  5
  best valid F1               0.3486      0.3548     0.1663  5
  test BA                     0.5014      0.5000     0.0166  5
  test F1                     0.0930      0.0476     0.1321  5
  test sensitivity            0.0722      0.0278     0.1172  5
  test specificity            0.9306      0.9722     0.0967  5
  test precision              0.2593      0.2685     0.2207  4
  test loss                   0.6753      0.6736     0.0291  5
  FPR (FP/(FP+TN))            0.0694      0.0278     0.0967  5
  FNR (FN/(FN+TP))            0.9278      0.9722     0.1172  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6000      0.5735     0.0573  5
  max valid BA                0.6412      0.6618     0.0556  5
  best valid F1               0.5273      0.5455     0.0537  5
  test BA                     0.5647      0.5882     0.0505  5
  test F1                     0.3338      0.4000     0.1429  5
  test sensitivity            0.2706      0.2941     0.1354  5
  test specificity            0.8588      0.8529     0.0603  5
  test precision              0.4663      0.4667     0.1403  5
  test loss                   0.6498      0.6405     0.0149  5
  FPR (FP/(FP+TN))            0.1412      0.1471     0.0603  5
  FNR (FN/(FN+TP))            0.7294      0.7059     0.1354  5
```

## AUC vs chemistry null model, in-sample increment

