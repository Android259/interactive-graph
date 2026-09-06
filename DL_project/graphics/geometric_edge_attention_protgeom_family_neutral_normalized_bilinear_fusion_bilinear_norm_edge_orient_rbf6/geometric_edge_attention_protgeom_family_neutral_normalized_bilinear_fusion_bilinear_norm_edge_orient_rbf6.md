# geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_edge_orient_rbf6

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_edge_orient_rbf6'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.2716      0.7639      0.6697      0.6418      0.3403      0.7548
groups_GLTP            5      0.2400      0.6480      0.6158      0.6373      0.3462      0.7615
groups_IP_trans        5      0.3478      0.7957      0.6848      0.6523      0.4417      0.8170
groups_LBP_BPI_CETP    5      0.2000      0.9362      0.7541      0.6430      0.2583      0.9064
groups_START           5      0.4677      0.5169      0.8457      0.4304      0.5000      0.5461
groups_lipocalin       5      0.4333      0.5500      0.7651      0.6667      0.5444      0.5556
groups_scp2            5      0.3059      0.7824      0.7114      0.6299      0.3765      0.8118
ALL                   35      0.3238      0.7133      0.7210      0.6145      0.4011      0.7362

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5686      0.5668     0.0479  35
max valid BA                0.6019      0.6026     0.0533  35
best valid F1               0.5636      0.5405     0.0695  35
test BA                     0.5185      0.5000     0.0642  35
test F1                     0.3199      0.3200     0.1722  35
test sensitivity            0.3238      0.2941     0.2587  35
test specificity            0.7133      0.8090     0.2593  35
test precision              0.4214      0.4075     0.1554  34
test loss                   0.7305      0.6950     0.1460  35
FPR (FP/(FP+TN))            0.2867      0.1910     0.2593  35
FNR (FN/(FN+TP))            0.6762      0.7059     0.2587  35

=== abs(sensitivity-specificity) gap: mean=0.5481 median=0.6250 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5476      0.5590     0.0258  5
  max valid BA                0.5901      0.6026     0.0334  5
  best valid F1               0.6236      0.6837     0.1149  5
  test BA                     0.5178      0.5100     0.0430  5
  test F1                     0.3342      0.4324     0.2037  5
  test sensitivity            0.2716      0.3433     0.1795  5
  test specificity            0.7639      0.8033     0.1523  5
  test precision              0.4594      0.5345     0.2666  5
  test loss                   0.7123      0.7055     0.0359  5
  FPR (FP/(FP+TN))            0.2361      0.1967     0.1523  5
  FNR (FN/(FN+TP))            0.7284      0.6567     0.1795  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5538      0.5577     0.0417  5
  max valid BA                0.5692      0.5577     0.0292  5
  best valid F1               0.5957      0.6667     0.0975  5
  test BA                     0.4440      0.4400     0.0434  5
  test F1                     0.2566      0.3000     0.1950  5
  test sensitivity            0.2400      0.2400     0.2098  5
  test specificity            0.6480      0.6400     0.2598  5
  test precision              0.3812      0.3875     0.0740  4
  test loss                   0.7790      0.7394     0.1180  5
  FPR (FP/(FP+TN))            0.3520      0.3600     0.2598  5
  FNR (FN/(FN+TP))            0.7600      0.7600     0.2098  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6293      0.6033     0.0506  5
  max valid BA                0.6724      0.6644     0.0395  5
  best valid F1               0.5709      0.5660     0.0552  5
  test BA                     0.5718      0.5449     0.0749  5
  test F1                     0.3609      0.2941     0.1717  5
  test sensitivity            0.3478      0.2174     0.2421  5
  test specificity            0.7957      0.8511     0.0959  5
  test precision              0.4272      0.4545     0.0805  5
  test loss                   0.6588      0.6651     0.0338  5
  FPR (FP/(FP+TN))            0.2043      0.1489     0.0959  5
  FNR (FN/(FN+TP))            0.6522      0.7826     0.2421  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5824      0.5918     0.0407  5
  max valid BA                0.6343      0.6348     0.0202  5
  best valid F1               0.5419      0.5312     0.0266  5
  test BA                     0.5681      0.5227     0.0732  5
  test F1                     0.2793      0.2000     0.1934  5
  test sensitivity            0.2000      0.1304     0.1586  5
  test specificity            0.9362      0.9574     0.0301  5
  test precision              0.5410      0.5000     0.1836  5
  test loss                   0.6356      0.6288     0.0186  5
  FPR (FP/(FP+TN))            0.0638      0.0426     0.0301  5
  FNR (FN/(FN+TP))            0.8000      0.8696     0.1586  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5230      0.5320     0.0184  5
  max valid BA                0.5309      0.5344     0.0286  5
  best valid F1               0.5830      0.5899     0.0316  5
  test BA                     0.4923      0.4861     0.0321  5
  test F1                     0.3539      0.2619     0.2153  5
  test sensitivity            0.4677      0.1692     0.4592  5
  test specificity            0.5169      0.8090     0.4581  5
  test precision              0.4104      0.4150     0.1142  5
  test loss                   0.8538      0.7245     0.3163  5
  FPR (FP/(FP+TN))            0.4831      0.1910     0.4581  5
  FNR (FN/(FN+TP))            0.5323      0.8308     0.4592  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5694     0.0403  5
  max valid BA                0.5931      0.5764     0.0335  5
  best valid F1               0.5194      0.5254     0.0185  5
  test BA                     0.4917      0.4861     0.0345  5
  test F1                     0.3256      0.3529     0.1739  5
  test sensitivity            0.4333      0.4167     0.3078  5
  test specificity            0.5500      0.5278     0.2458  5
  test precision              0.2840      0.3143     0.0988  5
  test loss                   0.7863      0.7627     0.1201  5
  FPR (FP/(FP+TN))            0.4500      0.4722     0.2458  5
  FNR (FN/(FN+TP))            0.5667      0.5833     0.3078  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5941      0.5735     0.0369  5
  max valid BA                0.6235      0.6471     0.0472  5
  best valid F1               0.5106      0.5000     0.0198  5
  test BA                     0.5441      0.5588     0.0441  5
  test F1                     0.3285      0.3902     0.1342  5
  test sensitivity            0.3059      0.2941     0.1735  5
  test specificity            0.7824      0.8824     0.1832  5
  test precision              0.4383      0.4000     0.1247  5
  test loss                   0.6876      0.6835     0.0620  5
  FPR (FP/(FP+TN))            0.2176      0.1176     0.1832  5
  FNR (FN/(FN+TP))            0.6941      0.7059     0.1735  5
```

## AUC vs chemistry null model, in-sample increment

