# geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_hid16

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_hid16'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.3522      0.7443      0.7611      0.6720      0.3493      0.7774
groups_GLTP            5      0.3200      0.6720      0.6620      0.6667      0.4385      0.6923
groups_IP_trans        5      0.5130      0.7617      0.6165      0.6523      0.5333      0.8000
groups_LBP_BPI_CETP    5      0.1652      0.9532      0.7175      0.6500      0.2000      0.9362
groups_START           5      0.1692      0.7753      0.6846      0.6109      0.2250      0.8000
groups_lipocalin       5      0.2333      0.8694      0.5523      0.6489      0.2167      0.8722
groups_scp2            5      0.2588      0.8824      0.6340      0.6467      0.2824      0.9059
ALL                   35      0.2874      0.8083      0.6612      0.6497      0.3207      0.8263

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5748      0.5723     0.0642  35
max valid BA                0.6063      0.6042     0.0705  35
best valid F1               0.5069      0.5306     0.1400  35
test BA                     0.5479      0.5441     0.0913  35
test F1                     0.3239      0.2703     0.2030  35
test sensitivity            0.2874      0.2000     0.2386  35
test specificity            0.8083      0.8197     0.1518  35
test precision              0.4887      0.5000     0.1799  34
test loss                   0.7124      0.6815     0.1453  35
FPR (FP/(FP+TN))            0.1917      0.1803     0.1518  35
FNR (FN/(FN+TP))            0.7126      0.8000     0.2386  35

=== abs(sensitivity-specificity) gap: mean=0.5761 median=0.5694 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5633      0.5498     0.0531  5
  max valid BA                0.6185      0.6195     0.0591  5
  best valid F1               0.6465      0.6982     0.0982  5
  test BA                     0.5483      0.5711     0.0668  5
  test F1                     0.3921      0.4706     0.2421  5
  test sensitivity            0.3522      0.3582     0.2986  5
  test specificity            0.7443      0.8197     0.1839  5
  test precision              0.5462      0.6111     0.1534  5
  test loss                   0.7133      0.7077     0.0228  5
  FPR (FP/(FP+TN))            0.2557      0.1803     0.1839  5
  FNR (FN/(FN+TP))            0.6478      0.6418     0.2986  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5654      0.5769     0.0172  5
  max valid BA                0.5769      0.5769     0.0236  5
  best valid F1               0.5315      0.4889     0.0867  5
  test BA                     0.4960      0.4400     0.1374  5
  test F1                     0.3460      0.2703     0.2432  5
  test sensitivity            0.3200      0.2000     0.3162  5
  test specificity            0.6720      0.6800     0.0522  5
  test precision              0.4275      0.4000     0.1530  5
  test loss                   0.7669      0.7450     0.0642  5
  FPR (FP/(FP+TN))            0.3280      0.3200     0.0522  5
  FNR (FN/(FN+TP))            0.6800      0.8000     0.3162  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6667      0.6733     0.0597  5
  max valid BA                0.6926      0.7243     0.0582  5
  best valid F1               0.6101      0.6383     0.0567  5
  test BA                     0.6374      0.6549     0.0528  5
  test F1                     0.4993      0.5417     0.1143  5
  test sensitivity            0.5130      0.5217     0.1880  5
  test specificity            0.7617      0.7447     0.1289  5
  test precision              0.5252      0.5000     0.0822  5
  test loss                   0.6485      0.6626     0.0296  5
  FPR (FP/(FP+TN))            0.2383      0.2553     0.1289  5
  FNR (FN/(FN+TP))            0.4870      0.4783     0.1880  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5681      0.5616     0.0251  5
  max valid BA                0.6030      0.6042     0.0473  5
  best valid F1               0.3845      0.3636     0.1509  5
  test BA                     0.5592      0.5439     0.0533  5
  test F1                     0.2438      0.2143     0.1693  5
  test sensitivity            0.1652      0.1304     0.1282  5
  test specificity            0.9532      0.9574     0.0233  5
  test precision              0.5162      0.6000     0.2926  5
  test loss                   0.7281      0.6096     0.2733  5
  FPR (FP/(FP+TN))            0.0468      0.0426     0.0233  5
  FNR (FN/(FN+TP))            0.8348      0.8696     0.1282  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5125      0.5078     0.0472  5
  max valid BA                0.5303      0.5132     0.0323  5
  best valid F1               0.4669      0.4029     0.1225  5
  test BA                     0.4723      0.4904     0.0332  5
  test F1                     0.1757      0.1319     0.1852  5
  test sensitivity            0.1692      0.0923     0.2245  5
  test specificity            0.7753      0.7753     0.2307  5
  test precision              0.3355      0.3486     0.0870  4
  test loss                   0.8212      0.7202     0.2537  5
  FPR (FP/(FP+TN))            0.2247      0.2247     0.2307  5
  FNR (FN/(FN+TP))            0.8308      0.9077     0.2245  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5444      0.5208     0.0706  5
  max valid BA                0.5667      0.5208     0.0831  5
  best valid F1               0.3663      0.3175     0.1474  5
  test BA                     0.5514      0.5069     0.1370  5
  test F1                     0.2860      0.1967     0.2437  5
  test sensitivity            0.2333      0.1389     0.2442  5
  test specificity            0.8694      0.9028     0.0965  5
  test precision              0.4651      0.3750     0.2624  5
  test loss                   0.6732      0.6542     0.0312  5
  FPR (FP/(FP+TN))            0.1306      0.0972     0.0965  5
  FNR (FN/(FN+TP))            0.7667      0.8611     0.2442  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6029      0.6176     0.0509  5
  max valid BA                0.6559      0.6765     0.0424  5
  best valid F1               0.5428      0.5600     0.0369  5
  test BA                     0.5706      0.5735     0.0263  5
  test F1                     0.3245      0.3333     0.1225  5
  test sensitivity            0.2588      0.2353     0.1476  5
  test specificity            0.8824      0.9118     0.0975  5
  test precision              0.5743      0.5714     0.0924  5
  test loss                   0.6357      0.6332     0.0275  5
  FPR (FP/(FP+TN))            0.1176      0.0882     0.0975  5
  FNR (FN/(FN+TP))            0.7412      0.7647     0.1476  5
```

## AUC vs chemistry null model, in-sample increment

