# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_hydrocore_depthq10

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_hydrocore_depthq10'
rows: 34

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       4      0.5485      0.5902      0.7207      0.5486      0.5560      0.5806
groups_GLTP            5      0.3360      0.6000      0.5706      0.6180      0.4692      0.6615
groups_IP_trans        5      0.3913      0.8298      0.6606      0.6515      0.4750      0.8383
groups_LBP_BPI_CETP    5      0.2174      0.9149      0.6866      0.6101      0.2833      0.8426
groups_START           5      0.4308      0.5483      0.5918      0.5321      0.4406      0.5573
groups_lipocalin       5      0.3333      0.6389      0.5713      0.6572      0.4278      0.6444
groups_scp2            5      0.4824      0.6353      0.6826      0.6445      0.5294      0.7176
ALL                   34      0.3868      0.6823      0.6382      0.6106      0.4515      0.6950

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5739      0.5577     0.0691  34
max valid BA                0.5974      0.5826     0.0752  34
best valid F1               0.5166      0.5566     0.1545  34
test BA                     0.5345      0.5159     0.0738  34
test F1                     0.3476      0.3842     0.2153  34
test sensitivity            0.3868      0.2992     0.3317  34
test specificity            0.6823      0.7979     0.3215  34
test precision              0.4319      0.4381     0.1834  32
test loss                   0.6768      0.6775     0.0550  34
FPR (FP/(FP+TN))            0.3177      0.2021     0.3215  34
FNR (FN/(FN+TP))            0.6132      0.7008     0.3317  34

=== abs(sensitivity-specificity) gap: mean=0.6323 median=0.6488 n=34 ===

=== By group ===
groups_CRAL-TRIO (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5683      0.5747     0.0540  4
  max valid BA                0.5899      0.6033     0.0487  4
  best valid F1               0.6764      0.6798     0.0191  4
  test BA                     0.5693      0.5793     0.0533  4
  test F1                     0.5315      0.5665     0.1638  4
  test sensitivity            0.5485      0.5000     0.3404  4
  test specificity            0.5902      0.7213     0.4121  4
  test precision              0.6482      0.6735     0.0936  4
  test loss                   0.6867      0.6848     0.0158  4
  FPR (FP/(FP+TN))            0.4098      0.2787     0.4121  4
  FNR (FN/(FN+TP))            0.4515      0.5000     0.3404  4

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5654      0.5577     0.0483  5
  max valid BA                0.5769      0.5577     0.0333  5
  best valid F1               0.5678      0.6462     0.1307  5
  test BA                     0.4680      0.4400     0.0502  5
  test F1                     0.3308      0.3000     0.1908  5
  test sensitivity            0.3360      0.2000     0.3517  5
  test specificity            0.6000      0.7200     0.3250  5
  test precision              0.4377      0.4000     0.1273  5
  test loss                   0.7437      0.7420     0.0610  5
  FPR (FP/(FP+TN))            0.4000      0.2800     0.3250  5
  FNR (FN/(FN+TP))            0.6640      0.8000     0.3517  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6566      0.6547     0.0182  5
  max valid BA                0.6996      0.7159     0.0299  5
  best valid F1               0.6035      0.6190     0.0433  5
  test BA                     0.6105      0.5999     0.0659  5
  test F1                     0.4363      0.4390     0.1348  5
  test sensitivity            0.3913      0.3913     0.1597  5
  test specificity            0.8298      0.8298     0.0398  5
  test precision              0.5151      0.5000     0.0694  5
  test loss                   0.6301      0.6292     0.0148  5
  FPR (FP/(FP+TN))            0.1702      0.1702     0.0398  5
  FNR (FN/(FN+TP))            0.6087      0.6087     0.1597  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5629      0.5519     0.0387  5
  max valid BA                0.5885      0.5718     0.0594  5
  best valid F1               0.3869      0.5053     0.1934  5
  test BA                     0.5661      0.5222     0.0867  5
  test F1                     0.2597      0.1481     0.2396  5
  test sensitivity            0.2174      0.0870     0.2460  5
  test specificity            0.9149      0.9362     0.0752  5
  test precision              0.4239      0.5000     0.2533  5
  test loss                   0.6131      0.5994     0.0256  5
  FPR (FP/(FP+TN))            0.0851      0.0638     0.0752  5
  FNR (FN/(FN+TP))            0.7826      0.9130     0.2460  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4990      0.5000     0.0374  5
  max valid BA                0.5157      0.5148     0.0163  5
  best valid F1               0.4425      0.3721     0.1396  5
  test BA                     0.4895      0.5000     0.0245  5
  test F1                     0.3100      0.2600     0.2684  5
  test sensitivity            0.4308      0.2000     0.4709  5
  test specificity            0.5483      0.7528     0.4415  5
  test precision              0.3688      0.3968     0.0835  4
  test loss                   0.7059      0.7052     0.0176  5
  FPR (FP/(FP+TN))            0.4517      0.2472     0.4415  5
  FNR (FN/(FN+TP))            0.5692      0.8000     0.4709  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5403      0.5139     0.0678  5
  max valid BA                0.5597      0.5208     0.0742  5
  best valid F1               0.4055      0.5000     0.1758  5
  test BA                     0.4861      0.5000     0.0461  5
  test F1                     0.2211      0.0870     0.2325  5
  test sensitivity            0.3333      0.0556     0.4357  5
  test specificity            0.6389      0.7778     0.3977  5
  test precision              0.2537      0.2667     0.1200  4
  test loss                   0.6898      0.7055     0.0510  5
  FPR (FP/(FP+TN))            0.3611      0.2222     0.3977  5
  FNR (FN/(FN+TP))            0.6667      0.9444     0.4357  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6235      0.6324     0.0816  5
  max valid BA                0.6500      0.6324     0.0788  5
  best valid F1               0.5652      0.5532     0.0736  5
  test BA                     0.5588      0.5441     0.0658  5
  test F1                     0.3804      0.4727     0.2180  5
  test sensitivity            0.4824      0.5294     0.3415  5
  test specificity            0.6353      0.7647     0.3465  5
  test precision              0.3711      0.3590     0.2389  5
  test loss                   0.6701      0.6579     0.0492  5
  FPR (FP/(FP+TN))            0.3647      0.2353     0.3465  5
  FNR (FN/(FN+TP))            0.5176      0.4706     0.3415  5
```

## AUC vs chemistry null model, in-sample increment

