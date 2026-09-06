# geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_edge_raw3

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_edge_raw3'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5910      0.5213      0.7931      0.6072      0.5881      0.5516
groups_GLTP            5      0.3200      0.6240      0.6781      0.4995      0.3923      0.7231
groups_IP_trans        5      0.3391      0.7787      0.7868      0.6625      0.4500      0.7957
groups_LBP_BPI_CETP    5      0.3913      0.7787      0.7325      0.5773      0.4667      0.7532
groups_START           5      0.3631      0.6225      0.7706      0.5017      0.3812      0.6157
groups_lipocalin       5      0.6556      0.4972      0.7872      0.4948      0.6944      0.5306
groups_scp2            5      0.2000      0.9059      0.6680      0.6710      0.2706      0.9294
ALL                   35      0.4086      0.6755      0.7452      0.5734      0.4633      0.6999

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5816      0.5769     0.0640  35
max valid BA                0.6138      0.6176     0.0622  35
best valid F1               0.5554      0.5625     0.0979  35
test BA                     0.5420      0.5259     0.0909  35
test F1                     0.3808      0.3500     0.2032  35
test sensitivity            0.4086      0.3433     0.3017  35
test specificity            0.6755      0.7234     0.2542  35
test precision              0.4307      0.4286     0.1606  35
test loss                   0.6993      0.6937     0.1005  35
FPR (FP/(FP+TN))            0.3245      0.2766     0.2542  35
FNR (FN/(FN+TP))            0.5914      0.6567     0.3017  35

=== abs(sensitivity-specificity) gap: mean=0.5095 median=0.5203 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5698      0.5268     0.0721  5
  max valid BA                0.6239      0.6455     0.0609  5
  best valid F1               0.6959      0.6952     0.0123  5
  test BA                     0.5562      0.5475     0.0759  5
  test F1                     0.5318      0.6225     0.2365  5
  test sensitivity            0.5910      0.7015     0.3563  5
  test specificity            0.5213      0.4918     0.2665  5
  test precision              0.5501      0.5595     0.0868  5
  test loss                   0.7043      0.6980     0.0150  5
  FPR (FP/(FP+TN))            0.4787      0.5082     0.2665  5
  FNR (FN/(FN+TP))            0.4090      0.2985     0.3563  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5577      0.5577     0.0236  5
  max valid BA                0.5615      0.5577     0.0161  5
  best valid F1               0.5669      0.5806     0.0880  5
  test BA                     0.4720      0.4800     0.0460  5
  test F1                     0.3451      0.3000     0.1787  5
  test sensitivity            0.3200      0.2400     0.2263  5
  test specificity            0.6240      0.6400     0.1802  5
  test precision              0.4308      0.4286     0.0911  5
  test loss                   0.7779      0.7182     0.1356  5
  FPR (FP/(FP+TN))            0.3760      0.3600     0.1802  5
  FNR (FN/(FN+TP))            0.6800      0.7600     0.2263  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6229      0.6228     0.0275  5
  max valid BA                0.6477      0.6414     0.0279  5
  best valid F1               0.5454      0.5600     0.0330  5
  test BA                     0.5589      0.5444     0.0754  5
  test F1                     0.3541      0.3500     0.1543  5
  test sensitivity            0.3391      0.3043     0.2117  5
  test specificity            0.7787      0.7872     0.1152  5
  test precision              0.4209      0.4118     0.0977  5
  test loss                   0.6841      0.6844     0.0721  5
  FPR (FP/(FP+TN))            0.2213      0.2128     0.1152  5
  FNR (FN/(FN+TP))            0.6609      0.6957     0.2117  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6099      0.6210     0.0340  5
  max valid BA                0.6229      0.6228     0.0294  5
  best valid F1               0.4719      0.4889     0.0940  5
  test BA                     0.5850      0.5241     0.1344  5
  test F1                     0.3764      0.3333     0.2633  5
  test sensitivity            0.3913      0.3913     0.3028  5
  test specificity            0.7787      0.7872     0.1679  5
  test precision              0.3812      0.3750     0.2596  5
  test loss                   0.7168      0.6429     0.2055  5
  FPR (FP/(FP+TN))            0.2213      0.2128     0.1679  5
  FNR (FN/(FN+TP))            0.6087      0.6087     0.3028  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4985      0.5000     0.0197  5
  max valid BA                0.5503      0.5295     0.0404  5
  best valid F1               0.5371      0.5899     0.1183  5
  test BA                     0.4928      0.5000     0.0605  5
  test F1                     0.3206      0.2000     0.2025  5
  test sensitivity            0.3631      0.1538     0.3832  5
  test specificity            0.6225      0.6966     0.3620  5
  test precision              0.4005      0.4221     0.1313  5
  test loss                   0.7041      0.7006     0.0093  5
  FPR (FP/(FP+TN))            0.3775      0.3034     0.3620  5
  FNR (FN/(FN+TP))            0.6369      0.8462     0.3832  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6125      0.5764     0.1071  5
  max valid BA                0.6375      0.6319     0.1107  5
  best valid F1               0.5414      0.4965     0.1144  5
  test BA                     0.5764      0.5556     0.1346  5
  test F1                     0.4804      0.4902     0.1548  5
  test sensitivity            0.6556      0.6944     0.3040  5
  test specificity            0.4972      0.5139     0.3123  5
  test precision              0.4127      0.3788     0.1199  5
  test loss                   0.6770      0.7020     0.0675  5
  FPR (FP/(FP+TN))            0.5028      0.4861     0.3123  5
  FNR (FN/(FN+TP))            0.3444      0.3056     0.3040  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6000      0.6029     0.0319  5
  max valid BA                0.6529      0.6471     0.0246  5
  best valid F1               0.5291      0.5405     0.0375  5
  test BA                     0.5529      0.5882     0.0556  5
  test F1                     0.2571      0.3478     0.1949  5
  test sensitivity            0.2000      0.2353     0.1695  5
  test specificity            0.9059      0.9412     0.0816  5
  test precision              0.4183      0.4667     0.2688  5
  test loss                   0.6311      0.6218     0.0153  5
  FPR (FP/(FP+TN))            0.0941      0.0588     0.0816  5
  FNR (FN/(FN+TP))            0.8000      0.7647     0.1695  5
```

## AUC vs chemistry null model, in-sample increment

