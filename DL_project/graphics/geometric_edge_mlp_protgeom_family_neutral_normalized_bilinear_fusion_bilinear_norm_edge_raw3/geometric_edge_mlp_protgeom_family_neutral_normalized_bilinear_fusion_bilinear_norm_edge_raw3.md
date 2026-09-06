# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_edge_raw3

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_edge_raw3'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.3373      0.7607      0.5960      0.7061      0.3642      0.7903
groups_GLTP            5      0.2880      0.6000      0.6305      0.5371      0.3769      0.7231
groups_IP_trans        5      0.6000      0.7277      0.6981      0.5915      0.6333      0.7149
groups_LBP_BPI_CETP    5      0.4087      0.8255      0.7237      0.5781      0.4417      0.8000
groups_START           5      0.3569      0.6697      0.4867      0.5863      0.3500      0.6719
groups_lipocalin       5      0.1944      0.8444      0.5309      0.7382      0.1722      0.8500
groups_scp2            5      0.5059      0.7118      0.6469      0.6204      0.4471      0.7882
ALL                   35      0.3845      0.7342      0.6161      0.6225      0.3979      0.7626

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5803      0.5769     0.0729  35
max valid BA                0.6060      0.6029     0.0752  35
best valid F1               0.5252      0.5385     0.1103  35
test BA                     0.5594      0.5588     0.0878  35
test F1                     0.3696      0.4242     0.2250  35
test sensitivity            0.3845      0.4118     0.2790  35
test specificity            0.7342      0.7872     0.2228  35
test precision              0.4565      0.4495     0.1687  32
test loss                   0.6805      0.6818     0.0475  35
FPR (FP/(FP+TN))            0.2658      0.2128     0.2228  35
FNR (FN/(FN+TP))            0.6155      0.5882     0.2790  35

=== abs(sensitivity-specificity) gap: mean=0.4799 median=0.3719 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5773      0.5791     0.0560  5
  max valid BA                0.6196      0.6193     0.0540  5
  best valid F1               0.6120      0.6579     0.1229  5
  test BA                     0.5490      0.5606     0.0581  5
  test F1                     0.3664      0.3830     0.2773  5
  test sensitivity            0.3373      0.2687     0.3058  5
  test specificity            0.7607      0.8361     0.2046  5
  test precision              0.5873      0.6191     0.0986  4
  test loss                   0.7061      0.6993     0.0380  5
  FPR (FP/(FP+TN))            0.2393      0.1639     0.2046  5
  FNR (FN/(FN+TP))            0.6627      0.7313     0.3058  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5577     0.0219  5
  max valid BA                0.5538      0.5577     0.0251  5
  best valid F1               0.5054      0.4889     0.0523  5
  test BA                     0.4440      0.4400     0.0167  5
  test F1                     0.3225      0.3415     0.1315  5
  test sensitivity            0.2880      0.2800     0.1585  5
  test specificity            0.6000      0.6400     0.1497  5
  test precision              0.3975      0.4000     0.0681  5
  test loss                   0.7316      0.7179     0.0367  5
  FPR (FP/(FP+TN))            0.4000      0.3600     0.1497  5
  FNR (FN/(FN+TP))            0.7120      0.7200     0.1585  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6741      0.6547     0.0712  5
  max valid BA                0.6970      0.6955     0.0518  5
  best valid F1               0.6092      0.6071     0.0596  5
  test BA                     0.6638      0.6758     0.0468  5
  test F1                     0.5573      0.5581     0.0478  5
  test sensitivity            0.6000      0.5652     0.0943  5
  test specificity            0.7277      0.7872     0.1188  5
  test precision              0.5329      0.5484     0.0745  5
  test loss                   0.6404      0.6374     0.0370  5
  FPR (FP/(FP+TN))            0.2723      0.2128     0.1188  5
  FNR (FN/(FN+TP))            0.4000      0.4348     0.0943  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6208      0.6135     0.0613  5
  max valid BA                0.6521      0.6436     0.0649  5
  best valid F1               0.5260      0.5385     0.1134  5
  test BA                     0.6171      0.5994     0.1064  5
  test F1                     0.4166      0.4211     0.2567  5
  test sensitivity            0.4087      0.4348     0.2708  5
  test specificity            0.8255      0.8511     0.1253  5
  test precision              0.4420      0.5333     0.2727  5
  test loss                   0.6527      0.6438     0.0699  5
  FPR (FP/(FP+TN))            0.1745      0.1489     0.1253  5
  FNR (FN/(FN+TP))            0.5913      0.5652     0.2708  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5110      0.5078     0.0119  5
  max valid BA                0.5449      0.5276     0.0518  5
  best valid F1               0.5115      0.5250     0.1204  5
  test BA                     0.5133      0.5000     0.0562  5
  test F1                     0.2549      0.0769     0.3155  5
  test sensitivity            0.3569      0.0462     0.4771  5
  test specificity            0.6697      0.8876     0.4286  5
  test precision              0.2909      0.3264     0.2264  4
  test loss                   0.6963      0.6862     0.0197  5
  FPR (FP/(FP+TN))            0.3303      0.1124     0.4286  5
  FNR (FN/(FN+TP))            0.6431      0.9538     0.4771  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5111      0.5069     0.0546  5
  max valid BA                0.5306      0.5208     0.0473  5
  best valid F1               0.3878      0.4000     0.0933  5
  test BA                     0.5194      0.5069     0.0284  5
  test F1                     0.1832      0.0976     0.2003  5
  test sensitivity            0.1944      0.0556     0.2778  5
  test specificity            0.8444      0.9583     0.2221  5
  test precision              0.4127      0.3935     0.0601  4
  test loss                   0.6740      0.6781     0.0364  5
  FPR (FP/(FP+TN))            0.1556      0.0417     0.2221  5
  FNR (FN/(FN+TP))            0.8056      0.9444     0.2778  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6176      0.6176     0.0403  5
  max valid BA                0.6441      0.6176     0.0503  5
  best valid F1               0.5244      0.5238     0.0586  5
  test BA                     0.6088      0.6176     0.0460  5
  test F1                     0.4864      0.4898     0.0438  5
  test sensitivity            0.5059      0.4118     0.1354  5
  test specificity            0.7118      0.7353     0.1999  5
  test precision              0.5167      0.4545     0.1572  5
  test loss                   0.6625      0.6618     0.0242  5
  FPR (FP/(FP+TN))            0.2882      0.2647     0.1999  5
  FNR (FN/(FN+TP))            0.4941      0.5882     0.1354  5
```

## AUC vs chemistry null model, in-sample increment

