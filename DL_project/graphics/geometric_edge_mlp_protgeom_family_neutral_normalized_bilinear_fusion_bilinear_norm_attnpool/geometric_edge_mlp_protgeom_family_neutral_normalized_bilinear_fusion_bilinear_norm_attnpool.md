# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_attnpool

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_attnpool'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5403      0.5803      0.6749      0.6951      0.5433      0.6194
groups_GLTP            5      0.1920      0.7120      0.5618      0.5678      0.3154      0.8000
groups_IP_trans        5      0.4348      0.7830      0.7372      0.6780      0.4917      0.8298
groups_LBP_BPI_CETP    5      0.3652      0.8383      0.7443      0.5598      0.4583      0.8000
groups_START           5      0.3600      0.6202      0.6901      0.5300      0.3969      0.6449
groups_lipocalin       5      0.1222      0.9028      0.4343      0.7697      0.1278      0.9083
groups_scp2            5      0.1059      0.9706      0.6258      0.5839      0.2000      0.9824
ALL                   35      0.3029      0.7725      0.6383      0.6263      0.3619      0.7978

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5799      0.5764     0.0610  35
max valid BA                0.5993      0.5817     0.0706  35
best valid F1               0.5169      0.5217     0.1322  35
test BA                     0.5377      0.5294     0.0695  35
test F1                     0.3196      0.3030     0.2009  35
test sensitivity            0.3029      0.2400     0.2645  35
test specificity            0.7725      0.8298     0.2338  35
test precision              0.5008      0.5000     0.1993  33
test loss                   0.6831      0.6868     0.0562  35
FPR (FP/(FP+TN))            0.2275      0.1702     0.2338  35
FNR (FN/(FN+TP))            0.6971      0.7600     0.2645  35

=== abs(sensitivity-specificity) gap: mean=0.6095 median=0.5236 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5813      0.5749     0.0472  5
  max valid BA                0.6182      0.6393     0.0322  5
  best valid F1               0.6728      0.6860     0.0335  5
  test BA                     0.5603      0.5773     0.0524  5
  test F1                     0.5319      0.4800     0.1520  5
  test sensitivity            0.5403      0.3582     0.2920  5
  test specificity            0.5803      0.6393     0.2389  5
  test precision              0.5920      0.5795     0.0803  5
  test loss                   0.6926      0.6878     0.0216  5
  FPR (FP/(FP+TN))            0.4197      0.3607     0.2389  5
  FNR (FN/(FN+TP))            0.4597      0.6418     0.2920  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5577      0.5577     0.0236  5
  max valid BA                0.5615      0.5577     0.0161  5
  best valid F1               0.5328      0.4898     0.0991  5
  test BA                     0.4520      0.4400     0.0268  5
  test F1                     0.2537      0.2632     0.0717  5
  test sensitivity            0.1920      0.2000     0.0657  5
  test specificity            0.7120      0.6800     0.0996  5
  test precision              0.4007      0.4000     0.0383  5
  test loss                   0.7115      0.7135     0.0167  5
  FPR (FP/(FP+TN))            0.2880      0.3200     0.0996  5
  FNR (FN/(FN+TP))            0.8080      0.8000     0.0657  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6607      0.6441     0.0452  5
  max valid BA                0.6879      0.6658     0.0632  5
  best valid F1               0.5863      0.5614     0.0829  5
  test BA                     0.6089      0.5999     0.0507  5
  test F1                     0.4491      0.4390     0.1036  5
  test sensitivity            0.4348      0.4348     0.1712  5
  test specificity            0.7830      0.8085     0.0830  5
  test precision              0.4954      0.5000     0.0357  5
  test loss                   0.7079      0.6421     0.1145  5
  FPR (FP/(FP+TN))            0.2170      0.1915     0.0830  5
  FNR (FN/(FN+TP))            0.5652      0.5652     0.1712  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6292      0.6325     0.0434  5
  max valid BA                0.6567      0.6649     0.0612  5
  best valid F1               0.5270      0.5455     0.1139  5
  test BA                     0.6018      0.6323     0.0965  5
  test F1                     0.4161      0.4878     0.2039  5
  test sensitivity            0.3652      0.4348     0.1834  5
  test specificity            0.8383      0.8723     0.1190  5
  test precision              0.5139      0.5556     0.2548  5
  test loss                   0.6577      0.6796     0.0703  5
  FPR (FP/(FP+TN))            0.1617      0.1277     0.1190  5
  FNR (FN/(FN+TP))            0.6348      0.5652     0.1834  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5209      0.5000     0.0353  5
  max valid BA                0.5311      0.5297     0.0349  5
  best valid F1               0.4427      0.3538     0.1406  5
  test BA                     0.4901      0.5000     0.0224  5
  test F1                     0.2524      0.1364     0.2896  5
  test sensitivity            0.3600      0.0923     0.4640  5
  test specificity            0.6202      0.8090     0.4474  5
  test precision              0.2772      0.3415     0.2002  4
  test loss                   0.7121      0.7007     0.0229  5
  FPR (FP/(FP+TN))            0.3798      0.1910     0.4474  5
  FNR (FN/(FN+TP))            0.6400      0.9077     0.4640  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5181      0.5000     0.0360  5
  max valid BA                0.5278      0.5208     0.0337  5
  best valid F1               0.3533      0.2963     0.1351  5
  test BA                     0.5125      0.5069     0.0134  5
  test F1                     0.1533      0.1000     0.1349  5
  test sensitivity            0.1222      0.0556     0.1425  5
  test specificity            0.9028      0.9583     0.1420  5
  test precision              0.4355      0.4500     0.0781  4
  test loss                   0.6558      0.6550     0.0269  5
  FPR (FP/(FP+TN))            0.0972      0.0417     0.1420  5
  FNR (FN/(FN+TP))            0.8778      0.9444     0.1425  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5912      0.5882     0.0351  5
  max valid BA                0.6118      0.6029     0.0494  5
  best valid F1               0.5031      0.5000     0.0475  5
  test BA                     0.5382      0.5294     0.0132  5
  test F1                     0.1805      0.1905     0.0397  5
  test sensitivity            0.1059      0.1176     0.0263  5
  test specificity            0.9706      0.9706     0.0294  5
  test precision              0.7333      0.6667     0.2528  5
  test loss                   0.6444      0.6460     0.0142  5
  FPR (FP/(FP+TN))            0.0294      0.0294     0.0294  5
  FNR (FN/(FN+TP))            0.8941      0.8824     0.0263  5
```

## AUC vs chemistry null model, in-sample increment

