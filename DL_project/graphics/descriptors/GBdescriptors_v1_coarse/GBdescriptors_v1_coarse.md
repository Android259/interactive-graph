# GBdescriptors_v1_coarse

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'GBdescriptors_v1_coarse'
rows: 19

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       1      0.2388      0.8033      0.6143      0.3761      0.1642      0.8065
groups_GLTP            3      0.5733      0.6400      0.5517      0.4845      0.5513      0.6154
groups_IP_trans        1      0.2609      0.7660      0.8788      0.4959      0.2917      0.9362
groups_LBP_BPI_CETP    3      0.4203      0.8085      0.5017      0.6817      0.5833      0.8227
groups_ML              3      0.5333      0.3667      0.6683      0.4243      0.6000      0.5667
groups_OSBP            3      0.2222      0.3889      0.6035      0.4803      0.7778      0.7222
groups_START           2      0.2769      0.7022      0.4915      0.6195      0.3047      0.7528
groups_lipocalin       1      0.0000      1.0000      0.0153      0.9832      0.0000      1.0000
groups_scp2            2      0.7059      0.2794      0.6097      0.4435      0.8235      0.3676
ALL                   19      0.4059      0.5866      0.5624      0.5365      0.5394      0.6929

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6162      0.6139     0.1031  19
max valid BA                0.6426      0.6500     0.1156  19
best valid F1               0.5893      0.6000     0.1422  19
test BA                     0.4963      0.5000     0.1214  19
test F1                     0.3505      0.4173     0.1968  19
test sensitivity            0.4059      0.4000     0.3095  19
test specificity            0.5866      0.6000     0.3001  19
test precision              0.4061      0.3724     0.2222  18
test loss                   0.7040      0.6956     0.0463  19
FPR (FP/(FP+TN))            0.4134      0.4000     0.3001  19
FNR (FN/(FN+TP))            0.5941      0.6000     0.3095  19

=== abs(sensitivity-specificity) gap: mean=0.4894 median=0.5000 n=19 ===

=== By group ===
groups_CRAL-TRIO (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4853      0.4853     0.0000  1
  max valid BA                0.4853      0.4853     0.0000  1
  best valid F1               0.2444      0.2444     0.0000  1
  test BA                     0.5210      0.5210     0.0000  1
  test F1                     0.3368      0.3368     0.0000  1
  test sensitivity            0.2388      0.2388     0.0000  1
  test specificity            0.8033      0.8033     0.0000  1
  test precision              0.5714      0.5714     0.0000  1
  test loss                   0.7781      0.7781     0.0000  1
  FPR (FP/(FP+TN))            0.1967      0.1967     0.0000  1
  FNR (FN/(FN+TP))            0.7612      0.7612     0.0000  1

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5833      0.5577     0.0618  3
  max valid BA                0.6090      0.6154     0.0484  3
  best valid F1               0.6543      0.6667     0.0671  3
  test BA                     0.6067      0.6200     0.0231  3
  test F1                     0.5656      0.5957     0.1290  3
  test sensitivity            0.5733      0.5600     0.3002  3
  test specificity            0.6400      0.6800     0.3418  3
  test precision              0.6871      0.6364     0.1683  3
  test loss                   0.6863      0.6831     0.0059  3
  FPR (FP/(FP+TN))            0.3600      0.3200     0.3418  3
  FNR (FN/(FN+TP))            0.4267      0.4400     0.3002  3

groups_IP_trans (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6139      0.6139     0.0000  1
  max valid BA                0.6246      0.6246     0.0000  1
  best valid F1               0.5647      0.5647     0.0000  1
  test BA                     0.5134      0.5134     0.0000  1
  test F1                     0.3000      0.3000     0.0000  1
  test sensitivity            0.2609      0.2609     0.0000  1
  test specificity            0.7660      0.7660     0.0000  1
  test precision              0.3529      0.3529     0.0000  1
  test loss                   0.7181      0.7181     0.0000  1
  FPR (FP/(FP+TN))            0.2340      0.2340     0.0000  1
  FNR (FN/(FN+TP))            0.7391      0.7391     0.0000  1

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7030      0.7066     0.0065  3
  max valid BA                0.7171      0.7066     0.0189  3
  best valid F1               0.6279      0.6182     0.0192  3
  test BA                     0.6144      0.6314     0.0398  3
  test F1                     0.4657      0.4571     0.0309  3
  test sensitivity            0.4203      0.4348     0.0664  3
  test specificity            0.8085      0.8511     0.1329  3
  test precision              0.5541      0.5882     0.1330  3
  test loss                   0.6435      0.6465     0.0418  3
  FPR (FP/(FP+TN))            0.1915      0.1489     0.1329  3
  FNR (FN/(FN+TP))            0.5797      0.5652     0.0664  3

groups_ML (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5833      0.5500     0.1041  3
  max valid BA                0.6333      0.6500     0.0764  3
  best valid F1               0.5573      0.5455     0.0382  3
  test BA                     0.4500      0.4500     0.0500  3
  test F1                     0.3444      0.3333     0.1503  3
  test sensitivity            0.5333      0.4000     0.4163  3
  test specificity            0.3667      0.5000     0.3215  3
  test precision              0.2730      0.2857     0.0676  3
  test loss                   0.7214      0.7269     0.0235  3
  FPR (FP/(FP+TN))            0.6333      0.5000     0.3215  3
  FNR (FN/(FN+TP))            0.4667      0.6000     0.4163  3

groups_OSBP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7500      0.7500     0.0833  3
  max valid BA                0.8056      0.8333     0.1273  3
  best valid F1               0.7524      0.8000     0.1350  3
  test BA                     0.3056      0.2500     0.1735  3
  test F1                     0.1481      0.0000     0.2566  3
  test sensitivity            0.2222      0.0000     0.3849  3
  test specificity            0.3889      0.3333     0.0962  3
  test precision              0.1111      0.0000     0.1924  3
  test loss                   0.6972      0.6931     0.0102  3
  FPR (FP/(FP+TN))            0.6111      0.6667     0.0962  3
  FNR (FN/(FN+TP))            0.7778      1.0000     0.3849  3

groups_START (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5287      0.5287     0.0049  2
  max valid BA                0.5351      0.5351     0.0118  2
  best valid F1               0.5847      0.5847     0.0074  2
  test BA                     0.4896      0.4896     0.0273  2
  test F1                     0.2961      0.2961     0.1713  2
  test sensitivity            0.2769      0.2769     0.2393  2
  test specificity            0.7022      0.7022     0.2940  2
  test precision              0.4293      0.4293     0.0529  2
  test loss                   0.6993      0.6993     0.0273  2
  FPR (FP/(FP+TN))            0.2978      0.2978     0.2940  2
  FNR (FN/(FN+TP))            0.7231      0.7231     0.2393  2

groups_lipocalin (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0000  1
  max valid BA                0.5000      0.5000     0.0000  1
  best valid F1               0.2963      0.2963     0.0000  1
  test BA                     0.5000      0.5000     0.0000  1
  test F1                     0.0000      0.0000     0.0000  1
  test sensitivity            0.0000      0.0000     0.0000  1
  test specificity            1.0000      1.0000     0.0000  1
  test loss                   0.8225      0.8225     0.0000  1
  FPR (FP/(FP+TN))            0.0000      0.0000     0.0000  1
  FNR (FN/(FN+TP))            1.0000      1.0000     0.0000  1

groups_scp2 (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5956      0.5956     0.1352  2
  max valid BA                0.6176      0.6176     0.1456  2
  best valid F1               0.5737      0.5737     0.0937  2
  test BA                     0.4926      0.4926     0.0104  2
  test F1                     0.4295      0.4295     0.0997  2
  test sensitivity            0.7059      0.7059     0.4159  2
  test specificity            0.2794      0.2794     0.3951  2
  test precision              0.3258      0.3258     0.0107  2
  test loss                   0.7065      0.7065     0.0154  2
  FPR (FP/(FP+TN))            0.7206      0.7206     0.3951  2
  FNR (FN/(FN+TP))            0.2941      0.2941     0.4159  2
```

## AUC vs chemistry null model, in-sample increment

