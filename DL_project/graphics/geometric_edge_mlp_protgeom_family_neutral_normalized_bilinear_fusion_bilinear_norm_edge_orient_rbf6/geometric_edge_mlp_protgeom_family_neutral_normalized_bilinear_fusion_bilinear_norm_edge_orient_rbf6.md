# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_edge_orient_rbf6

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_edge_orient_rbf6'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.3821      0.7082      0.5977      0.7219      0.4537      0.6903
groups_GLTP            5      0.1920      0.7040      0.5695      0.6326      0.3077      0.7923
groups_IP_trans        5      0.3826      0.8085      0.6402      0.6719      0.4333      0.8340
groups_LBP_BPI_CETP    5      0.2261      0.9404      0.6180      0.6307      0.2500      0.9021
groups_START           5      0.0277      0.9596      0.5440      0.6567      0.0375      0.9685
groups_lipocalin       5      0.4333      0.7333      0.5719      0.5312      0.3944      0.7111
groups_scp2            5      0.3294      0.8647      0.6159      0.6415      0.3412      0.8529
ALL                   35      0.2819      0.8170      0.5939      0.6409      0.3168      0.8216

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5692      0.5612     0.0578  35
max valid BA                0.5978      0.5962     0.0723  35
best valid F1               0.4935      0.5217     0.1482  35
test BA                     0.5494      0.5240     0.0788  35
test F1                     0.3149      0.2889     0.1999  35
test sensitivity            0.2819      0.2174     0.2356  35
test specificity            0.8170      0.8511     0.1960  35
test precision              0.4956      0.5000     0.1498  33
test loss                   0.6697      0.6736     0.0454  35
FPR (FP/(FP+TN))            0.1830      0.1489     0.1960  35
FNR (FN/(FN+TP))            0.7181      0.7826     0.2356  35

=== abs(sensitivity-specificity) gap: mean=0.6143 median=0.5882 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5720      0.5605     0.0425  5
  max valid BA                0.5966      0.5995     0.0270  5
  best valid F1               0.6539      0.6623     0.0508  5
  test BA                     0.5451      0.5378     0.0279  5
  test F1                     0.4334      0.4286     0.1551  5
  test sensitivity            0.3821      0.3134     0.2321  5
  test specificity            0.7082      0.8361     0.2201  5
  test precision              0.6009      0.6000     0.0494  5
  test loss                   0.6957      0.6893     0.0187  5
  FPR (FP/(FP+TN))            0.2918      0.1639     0.2201  5
  FNR (FN/(FN+TP))            0.6179      0.6866     0.2321  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5577     0.0322  5
  max valid BA                0.5654      0.5577     0.0219  5
  best valid F1               0.4969      0.4889     0.1093  5
  test BA                     0.4480      0.4400     0.0335  5
  test F1                     0.2577      0.2703     0.0393  5
  test sensitivity            0.1920      0.2000     0.0335  5
  test specificity            0.7040      0.6800     0.0607  5
  test precision              0.3967      0.4000     0.0691  5
  test loss                   0.7298      0.7306     0.0297  5
  FPR (FP/(FP+TN))            0.2960      0.3200     0.0607  5
  FNR (FN/(FN+TP))            0.8080      0.8000     0.0335  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6337      0.6228     0.0429  5
  max valid BA                0.6793      0.6950     0.0403  5
  best valid F1               0.5704      0.5957     0.0621  5
  test BA                     0.5956      0.6110     0.0366  5
  test F1                     0.4266      0.4615     0.0796  5
  test sensitivity            0.3826      0.4348     0.0943  5
  test specificity            0.8085      0.8085     0.0451  5
  test precision              0.4920      0.5000     0.0576  5
  test loss                   0.6364      0.6288     0.0295  5
  FPR (FP/(FP+TN))            0.1915      0.1915     0.0451  5
  FNR (FN/(FN+TP))            0.6174      0.5652     0.0943  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5761      0.5612     0.0541  5
  max valid BA                0.6156      0.6228     0.0793  5
  best valid F1               0.4103      0.4889     0.1929  5
  test BA                     0.5833      0.5874     0.0827  5
  test F1                     0.2927      0.3333     0.2458  5
  test sensitivity            0.2261      0.2174     0.2094  5
  test specificity            0.9404      0.9574     0.0461  5
  test precision              0.5107      0.6471     0.2975  5
  test loss                   0.6164      0.6024     0.0381  5
  FPR (FP/(FP+TN))            0.0596      0.0426     0.0461  5
  FNR (FN/(FN+TP))            0.7739      0.7826     0.2094  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5030      0.5000     0.0183  5
  max valid BA                0.5122      0.5078     0.0215  5
  best valid F1               0.3865      0.3667     0.1292  5
  test BA                     0.4936      0.5000     0.0149  5
  test F1                     0.0457      0.0294     0.0585  5
  test sensitivity            0.0277      0.0154     0.0383  5
  test specificity            0.9596      0.9775     0.0663  5
  test precision              0.3778      0.3333     0.1072  3
  test loss                   0.6985      0.6962     0.0107  5
  FPR (FP/(FP+TN))            0.0404      0.0225     0.0663  5
  FNR (FN/(FN+TP))            0.9723      0.9846     0.0383  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5528      0.5139     0.0849  5
  max valid BA                0.5569      0.5278     0.0824  5
  best valid F1               0.3892      0.4681     0.1805  5
  test BA                     0.5833      0.5139     0.1061  5
  test F1                     0.3726      0.5000     0.2585  5
  test sensitivity            0.4333      0.4444     0.3999  5
  test specificity            0.7333      0.9028     0.4138  5
  test precision              0.5209      0.5000     0.1505  5
  test loss                   0.6584      0.6584     0.0431  5
  FPR (FP/(FP+TN))            0.2667      0.0972     0.4138  5
  FNR (FN/(FN+TP))            0.5667      0.5556     0.3999  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5971      0.6029     0.0267  5
  max valid BA                0.6588      0.6471     0.0470  5
  best valid F1               0.5476      0.5294     0.0459  5
  test BA                     0.5971      0.5882     0.0775  5
  test F1                     0.3755      0.3846     0.1994  5
  test sensitivity            0.3294      0.2941     0.2263  5
  test specificity            0.8647      0.8824     0.0872  5
  test precision              0.5228      0.5556     0.1161  5
  test loss                   0.6527      0.6532     0.0119  5
  FPR (FP/(FP+TN))            0.1353      0.1176     0.0872  5
  FNR (FN/(FN+TP))            0.6706      0.7059     0.2263  5
```

## AUC vs chemistry null model, in-sample increment

