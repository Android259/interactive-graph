# geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_edge_rbf6

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_edge_rbf6'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4507      0.7115      0.6960      0.5960      0.4448      0.6968
groups_GLTP            5      0.3440      0.5840      0.6557      0.5977      0.4769      0.6462
groups_IP_trans        5      0.4348      0.7830      0.7207      0.6391      0.5250      0.7915
groups_LBP_BPI_CETP    5      0.2696      0.8809      0.7268      0.5925      0.3250      0.8638
groups_START           5      0.1538      0.8157      0.5290      0.7270      0.1844      0.8225
groups_lipocalin       5      0.2722      0.7556      0.7034      0.6468      0.3278      0.7694
groups_scp2            5      0.3529      0.7471      0.6697      0.6660      0.4235      0.7706
ALL                   35      0.3254      0.7540      0.6716      0.6379      0.3868      0.7658

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5763      0.5764     0.0656  35
max valid BA                0.6150      0.6176     0.0749  35
best valid F1               0.5341      0.5667     0.1138  35
test BA                     0.5397      0.5441     0.0716  35
test F1                     0.3498      0.3462     0.1767  35
test sensitivity            0.3254      0.3043     0.2223  35
test specificity            0.7540      0.8056     0.2140  35
test precision              0.4654      0.4733     0.1775  34
test loss                   0.7153      0.6885     0.1302  35
FPR (FP/(FP+TN))            0.2461      0.1944     0.2140  35
FNR (FN/(FN+TP))            0.6746      0.6957     0.2223  35

=== abs(sensitivity-specificity) gap: mean=0.5345 median=0.5241 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5708      0.5519     0.0591  5
  max valid BA                0.5987      0.5844     0.0695  5
  best valid F1               0.6311      0.6259     0.0610  5
  test BA                     0.5811      0.5756     0.0265  5
  test F1                     0.5058      0.5299     0.1226  5
  test sensitivity            0.4507      0.4627     0.1984  5
  test specificity            0.7115      0.7213     0.2092  5
  test precision              0.6606      0.6731     0.0698  5
  test loss                   0.6971      0.6885     0.0239  5
  FPR (FP/(FP+TN))            0.2885      0.2787     0.2092  5
  FNR (FN/(FN+TP))            0.5493      0.5373     0.1984  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5615      0.5385     0.0459  5
  max valid BA                0.5962      0.5577     0.0871  5
  best valid F1               0.5249      0.4889     0.1303  5
  test BA                     0.4640      0.4600     0.0297  5
  test F1                     0.3277      0.3077     0.2043  5
  test sensitivity            0.3440      0.2400     0.3727  5
  test specificity            0.5840      0.6800     0.3306  5
  test precision              0.4103      0.4286     0.0943  5
  test loss                   0.7616      0.7563     0.0598  5
  FPR (FP/(FP+TN))            0.4160      0.3200     0.3306  5
  FNR (FN/(FN+TP))            0.6560      0.7600     0.3727  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6582      0.6649     0.0319  5
  max valid BA                0.6951      0.7061     0.0424  5
  best valid F1               0.6046      0.6154     0.0518  5
  test BA                     0.6089      0.6226     0.0569  5
  test F1                     0.4544      0.5000     0.1053  5
  test sensitivity            0.4348      0.5217     0.1409  5
  test specificity            0.7830      0.8085     0.0571  5
  test precision              0.4902      0.4800     0.0682  5
  test loss                   0.6355      0.6287     0.0140  5
  FPR (FP/(FP+TN))            0.2170      0.1915     0.0571  5
  FNR (FN/(FN+TP))            0.5652      0.4783     0.1409  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5944      0.6024     0.0299  5
  max valid BA                0.6653      0.6857     0.0619  5
  best valid F1               0.5590      0.5714     0.0654  5
  test BA                     0.5752      0.5550     0.0963  5
  test F1                     0.3329      0.3265     0.2236  5
  test sensitivity            0.2696      0.3478     0.1803  5
  test specificity            0.8809      0.9362     0.1494  5
  test precision              0.4810      0.5714     0.3310  5
  test loss                   0.6321      0.6046     0.0695  5
  FPR (FP/(FP+TN))            0.1191      0.0638     0.1494  5
  FNR (FN/(FN+TP))            0.7304      0.6522     0.1803  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5034      0.5122     0.0468  5
  max valid BA                0.5341      0.5298     0.0249  5
  best valid F1               0.4711      0.4974     0.1374  5
  test BA                     0.4848      0.4965     0.0301  5
  test F1                     0.1781      0.1364     0.1761  5
  test sensitivity            0.1538      0.0923     0.1696  5
  test specificity            0.8157      0.8090     0.1908  5
  test precision              0.3572      0.3532     0.0836  4
  test loss                   0.8370      0.7169     0.1961  5
  FPR (FP/(FP+TN))            0.1843      0.1910     0.1908  5
  FNR (FN/(FN+TP))            0.8462      0.9077     0.1696  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5486      0.5694     0.0829  5
  max valid BA                0.5806      0.5764     0.0754  5
  best valid F1               0.4202      0.4474     0.1445  5
  test BA                     0.5139      0.4861     0.0627  5
  test F1                     0.2879      0.3099     0.1559  5
  test sensitivity            0.2722      0.3056     0.1836  5
  test specificity            0.7556      0.8056     0.1173  5
  test precision              0.3345      0.3143     0.1470  5
  test loss                   0.7665      0.6886     0.2251  5
  FPR (FP/(FP+TN))            0.2444      0.1944     0.1173  5
  FNR (FN/(FN+TP))            0.7278      0.6944     0.1836  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5971      0.6176     0.0526  5
  max valid BA                0.6353      0.6176     0.0351  5
  best valid F1               0.5278      0.5333     0.0510  5
  test BA                     0.5500      0.5735     0.0556  5
  test F1                     0.3616      0.3478     0.0731  5
  test sensitivity            0.3529      0.2353     0.2161  5
  test specificity            0.7471      0.9118     0.3103  5
  test precision              0.5025      0.5000     0.1332  5
  test loss                   0.6775      0.6534     0.0509  5
  FPR (FP/(FP+TN))            0.2529      0.0882     0.3103  5
  FNR (FN/(FN+TP))            0.6471      0.7647     0.2161  5
```

## AUC vs chemistry null model, in-sample increment

