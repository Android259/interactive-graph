# geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28_ckpt30

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28_ckpt30'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4060      0.6689      0.7743      0.6804      0.4060      0.6968
groups_GLTP            5      0.2560      0.6720      0.6035      0.5853      0.3538      0.7231
groups_IP_trans        5      0.3913      0.7660      0.6915      0.6631      0.4417      0.7957
groups_LBP_BPI_CETP    5      0.3565      0.8681      0.6026      0.6059      0.3833      0.8426
groups_START           5      0.4154      0.7326      0.7782      0.6795      0.3906      0.7303
groups_lipocalin       5      0.3722      0.8250      0.4654      0.7232      0.3889      0.8222
groups_scp2            5      0.2824      0.7647      0.5918      0.6968      0.3294      0.8471
ALL                   35      0.3543      0.7567      0.6439      0.6620      0.3848      0.7797

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5922      0.5778     0.0620  35
max valid BA                0.6341      0.6389     0.0649  35
best valid F1               0.5506      0.5763     0.1211  35
test BA                     0.5555      0.5441     0.0788  35
test F1                     0.3694      0.3590     0.1910  35
test sensitivity            0.3543      0.3478     0.2370  35
test specificity            0.7567      0.7778     0.1812  35
test precision              0.5007      0.4875     0.1824  34
test loss                   0.7276      0.6866     0.1141  35
FPR (FP/(FP+TN))            0.2433      0.2222     0.1812  35
FNR (FN/(FN+TP))            0.6457      0.6522     0.2370  35

=== abs(sensitivity-specificity) gap: mean=0.4861 median=0.4380 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5870      0.5922     0.0355  5
  max valid BA                0.6246      0.6384     0.0278  5
  best valid F1               0.6753      0.6826     0.0243  5
  test BA                     0.5374      0.5522     0.0401  5
  test F1                     0.4162      0.5217     0.2292  5
  test sensitivity            0.4060      0.4478     0.3050  5
  test specificity            0.6689      0.7049     0.3013  5
  test precision              0.6509      0.5714     0.1995  5
  test loss                   0.7964      0.7181     0.1922  5
  FPR (FP/(FP+TN))            0.3311      0.2951     0.3013  5
  FNR (FN/(FN+TP))            0.5940      0.5522     0.3050  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5423      0.5385     0.0211  5
  max valid BA                0.5577      0.5577     0.0272  5
  best valid F1               0.5077      0.5185     0.0628  5
  test BA                     0.4640      0.4600     0.0434  5
  test F1                     0.2855      0.3077     0.1734  5
  test sensitivity            0.2560      0.2400     0.2147  5
  test specificity            0.6720      0.6800     0.2407  5
  test precision              0.5273      0.4667     0.2762  5
  test loss                   0.7397      0.7603     0.0423  5
  FPR (FP/(FP+TN))            0.3280      0.3200     0.2407  5
  FNR (FN/(FN+TP))            0.7440      0.7600     0.2147  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6389      0.6418     0.0485  5
  max valid BA                0.6728      0.6968     0.0482  5
  best valid F1               0.5761      0.5909     0.0530  5
  test BA                     0.5786      0.5680     0.0724  5
  test F1                     0.3871      0.4091     0.1539  5
  test sensitivity            0.3913      0.3913     0.2662  5
  test specificity            0.7660      0.8298     0.1395  5
  test precision              0.4376      0.4286     0.0846  5
  test loss                   0.6718      0.6585     0.0674  5
  FPR (FP/(FP+TN))            0.2340      0.1702     0.1395  5
  FNR (FN/(FN+TP))            0.6087      0.6087     0.2662  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5637      0.5399     0.0760  5
  max valid BA                0.6377      0.6436     0.0810  5
  best valid F1               0.4732      0.5217     0.1767  5
  test BA                     0.6123      0.6314     0.1082  5
  test F1                     0.3550      0.4571     0.2966  5
  test sensitivity            0.3565      0.3478     0.3497  5
  test specificity            0.8681      0.9149     0.1500  5
  test precision              0.4660      0.5135     0.2714  5
  test loss                   0.6486      0.6721     0.0411  5
  FPR (FP/(FP+TN))            0.1319      0.0851     0.1500  5
  FNR (FN/(FN+TP))            0.6435      0.6522     0.3497  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6141      0.5778     0.0930  5
  max valid BA                0.6429      0.6843     0.0947  5
  best valid F1               0.5623      0.6418     0.2102  5
  test BA                     0.5740      0.5525     0.0667  5
  test F1                     0.4454      0.4590     0.1549  5
  test sensitivity            0.4154      0.4308     0.1961  5
  test specificity            0.7326      0.7191     0.0997  5
  test precision              0.5234      0.5263     0.0660  5
  test loss                   0.8417      0.8269     0.1187  5
  FPR (FP/(FP+TN))            0.2674      0.2809     0.0997  5
  FNR (FN/(FN+TP))            0.5846      0.5692     0.1961  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6083      0.6389     0.0702  5
  max valid BA                0.6472      0.6389     0.0596  5
  best valid F1               0.5304      0.5143     0.0657  5
  test BA                     0.5986      0.5972     0.0804  5
  test F1                     0.3871      0.4478     0.2372  5
  test sensitivity            0.3722      0.4167     0.2450  5
  test specificity            0.8250      0.8611     0.1501  5
  test precision              0.5324      0.4919     0.1248  4
  test loss                   0.6738      0.6787     0.0211  5
  FPR (FP/(FP+TN))            0.1750      0.1389     0.1501  5
  FNR (FN/(FN+TP))            0.6278      0.5833     0.2450  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5912      0.6029     0.0381  5
  max valid BA                0.6559      0.6765     0.0516  5
  best valid F1               0.5292      0.5556     0.0794  5
  test BA                     0.5235      0.5000     0.0424  5
  test F1                     0.3092      0.3448     0.1057  5
  test sensitivity            0.2824      0.2941     0.1341  5
  test specificity            0.7647      0.7941     0.1230  5
  test precision              0.3736      0.3333     0.0649  5
  test loss                   0.7212      0.6822     0.1161  5
  FPR (FP/(FP+TN))            0.2353      0.2059     0.1230  5
  FNR (FN/(FN+TP))            0.7176      0.7059     0.1341  5
```

## AUC vs chemistry null model, in-sample increment

(skipped: SKIP_AUC=1 -- rerun without it to fill this in: `python3 analysis/full_label_report.py --label geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28_ckpt30 --seeds=0,1,2,3,4`)
