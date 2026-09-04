# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lipid_class

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lipid_class'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.2448      0.8131      0.7653      0.8202      0.2597      0.8097
groups_GLTP            5      0.3280      0.6080      0.5871      0.6445      0.4308      0.6462
groups_IP_trans        5      0.2261      0.8511      0.7015      0.7989      0.3417      0.8809
groups_LBP_BPI_CETP    5      0.2783      0.7660      0.7226      0.7631      0.3833      0.7532
groups_START           5      0.0800      0.8652      0.5526      0.7931      0.1094      0.8899
groups_lipocalin       5      0.2500      0.7389      0.7718      0.7864      0.3500      0.7556
groups_scp2            5      0.3412      0.8824      0.7387      0.7547      0.3529      0.8588
ALL                   35      0.2498      0.7892      0.6914      0.7658      0.3183      0.7992

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5587      0.5573     0.0549  35
max valid BA                0.5752      0.5751     0.0534  35
best valid F1               0.4572      0.4762     0.1302  35
test BA                     0.5195      0.5000     0.0633  35
test F1                     0.2746      0.3019     0.1764  35
test sensitivity            0.2498      0.2174     0.2228  35
test specificity            0.7892      0.8511     0.2061  35
test precision              0.4198      0.4286     0.1885  33
test loss                   0.8117      0.6994     0.2888  35
FPR (FP/(FP+TN))            0.2108      0.1489     0.2061  35
FNR (FN/(FN+TP))            0.7502      0.7826     0.2228  35

=== abs(sensitivity-specificity) gap: mean=0.6243 median=0.6176 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5347      0.5255     0.0282  5
  max valid BA                0.5593      0.5617     0.0164  5
  best valid F1               0.4665      0.3830     0.1819  5
  test BA                     0.5289      0.5358     0.0441  5
  test F1                     0.3002      0.3182     0.2144  5
  test sensitivity            0.2448      0.2090     0.2139  5
  test specificity            0.8131      0.8852     0.2380  5
  test precision              0.6550      0.6712     0.1150  4
  test loss                   0.8351      0.7939     0.1063  5
  FPR (FP/(FP+TN))            0.1869      0.1148     0.2380  5
  FNR (FN/(FN+TP))            0.7552      0.7910     0.2139  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5385      0.5385     0.0385  5
  max valid BA                0.5462      0.5385     0.0399  5
  best valid F1               0.4690      0.5000     0.1533  5
  test BA                     0.4680      0.4600     0.0335  5
  test F1                     0.2997      0.3077     0.2406  5
  test sensitivity            0.3280      0.2400     0.3882  5
  test specificity            0.6080      0.6800     0.3670  5
  test precision              0.4226      0.4286     0.0684  4
  test loss                   0.8813      0.7085     0.3822  5
  FPR (FP/(FP+TN))            0.3920      0.3200     0.3670  5
  FNR (FN/(FN+TP))            0.6720      0.7600     0.3882  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6113      0.5922     0.0661  5
  max valid BA                0.6385      0.6232     0.0455  5
  best valid F1               0.5131      0.5053     0.0681  5
  test BA                     0.5386      0.5463     0.0404  5
  test F1                     0.2828      0.3125     0.1118  5
  test sensitivity            0.2261      0.2174     0.1206  5
  test specificity            0.8511      0.8511     0.0877  5
  test precision              0.4444      0.4444     0.1482  5
  test loss                   0.8929      0.6537     0.5710  5
  FPR (FP/(FP+TN))            0.1489      0.1489     0.0877  5
  FNR (FN/(FN+TP))            0.7739      0.7826     0.1206  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5683      0.5519     0.0377  5
  max valid BA                0.5897      0.5993     0.0315  5
  best valid F1               0.4964      0.5053     0.0539  5
  test BA                     0.5221      0.4894     0.0812  5
  test F1                     0.2414      0.2667     0.2223  5
  test sensitivity            0.2783      0.1739     0.3348  5
  test specificity            0.7660      0.9149     0.2449  5
  test precision              0.2940      0.2667     0.2191  5
  test loss                   0.8115      0.6760     0.2428  5
  FPR (FP/(FP+TN))            0.2340      0.0851     0.2449  5
  FNR (FN/(FN+TP))            0.7217      0.8261     0.3348  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4996      0.4944     0.0167  5
  max valid BA                0.5168      0.5141     0.0190  5
  best valid F1               0.3927      0.3492     0.1233  5
  test BA                     0.4726      0.4944     0.0382  5
  test F1                     0.1157      0.1136     0.0902  5
  test sensitivity            0.0800      0.0769     0.0665  5
  test specificity            0.8652      0.8764     0.1210  5
  test precision              0.2675      0.2703     0.1767  5
  test loss                   0.8958      0.7682     0.2839  5
  FPR (FP/(FP+TN))            0.1348      0.1236     0.1210  5
  FNR (FN/(FN+TP))            0.9200      0.9231     0.0665  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5528      0.5625     0.0636  5
  max valid BA                0.5583      0.5625     0.0697  5
  best valid F1               0.3783      0.4762     0.1939  5
  test BA                     0.4944      0.4931     0.0438  5
  test F1                     0.2576      0.2687     0.1440  5
  test sensitivity            0.2500      0.2500     0.1608  5
  test specificity            0.7389      0.7083     0.1301  5
  test precision              0.3042      0.2903     0.0742  5
  test loss                   0.7463      0.7491     0.0936  5
  FPR (FP/(FP+TN))            0.2611      0.2917     0.1301  5
  FNR (FN/(FN+TP))            0.7500      0.7500     0.1608  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6059      0.6029     0.0351  5
  max valid BA                0.6176      0.6176     0.0233  5
  best valid F1               0.4848      0.5263     0.0843  5
  test BA                     0.6118      0.6029     0.0369  5
  test F1                     0.4247      0.4000     0.0824  5
  test sensitivity            0.3412      0.2941     0.1131  5
  test specificity            0.8824      0.8824     0.0465  5
  test precision              0.5985      0.6000     0.0500  5
  test loss                   0.6190      0.6287     0.0410  5
  FPR (FP/(FP+TN))            0.1176      0.1176     0.0465  5
  FNR (FN/(FN+TP))            0.6588      0.7059     0.1131  5
```

## AUC vs chemistry null model, in-sample increment

(skipped: SKIP_AUC=1 -- rerun without it to fill this in: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lipid_class --seeds=0,1,2,3,4`)
