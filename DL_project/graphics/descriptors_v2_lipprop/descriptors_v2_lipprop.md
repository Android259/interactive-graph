# descriptors_v2_lipprop

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_v2_lipprop'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4507      0.6689      0.6234      0.4625      0.4627      0.6645
groups_GLTP            5      0.2560      0.8800      0.6088      0.4939      0.3231      0.9308
groups_IP_trans        5      0.7652      0.3830      0.4948      0.6041      0.8167      0.4553
groups_LBP_BPI_CETP    5      0.7478      0.7064      0.5000      0.5662      0.7000      0.7447
groups_START           5      0.5631      0.4494      0.3918      0.6396      0.5844      0.4764
groups_lipocalin       5      0.5944      0.5667      0.3474      0.7141      0.6722      0.5861
groups_scp2            5      0.4353      0.6706      0.5725      0.5275      0.4235      0.7882
ALL                   35      0.5447      0.6178      0.5055      0.5726      0.5689      0.6637

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6173      0.6029     0.0818  35
max valid BA                0.6398      0.6324     0.0865  35
best valid F1               0.5723      0.5926     0.1201  35
test BA                     0.5813      0.5833     0.1013  35
test F1                     0.4644      0.5106     0.1737  35
test sensitivity            0.5447      0.5231     0.2921  35
test specificity            0.6178      0.5738     0.2728  35
test precision              0.5200      0.4343     0.2035  34
test loss                   0.6907      0.6934     0.0221  35
FPR (FP/(FP+TN))            0.3822      0.4262     0.2728  35
FNR (FN/(FN+TP))            0.4553      0.4769     0.2921  35

=== abs(sensitivity-specificity) gap: mean=0.4368 median=0.4118 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5636      0.5658     0.0487  5
  max valid BA                0.5784      0.5743     0.0567  5
  best valid F1               0.5455      0.6412     0.2317  5
  test BA                     0.5598      0.5182     0.0786  5
  test F1                     0.4636      0.5185     0.2690  5
  test sensitivity            0.4507      0.5224     0.2669  5
  test specificity            0.6689      0.5738     0.2101  5
  test precision              0.6015      0.5938     0.0877  4
  test loss                   0.6963      0.6963     0.0228  5
  FPR (FP/(FP+TN))            0.3311      0.4262     0.2101  5
  FNR (FN/(FN+TP))            0.5493      0.4776     0.2669  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6269      0.6538     0.0646  5
  max valid BA                0.6577      0.6923     0.0583  5
  best valid F1               0.5714      0.5789     0.0464  5
  test BA                     0.5680      0.5600     0.0944  5
  test F1                     0.3654      0.3636     0.1347  5
  test sensitivity            0.2560      0.3200     0.1081  5
  test specificity            0.8800      0.9600     0.1855  5
  test precision              0.7785      0.9000     0.2662  5
  test loss                   0.6869      0.6909     0.0231  5
  FPR (FP/(FP+TN))            0.1200      0.0400     0.1855  5
  FNR (FN/(FN+TP))            0.7440      0.6800     0.1081  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6360      0.6423     0.0461  5
  max valid BA                0.6527      0.6609     0.0397  5
  best valid F1               0.5841      0.5862     0.0294  5
  test BA                     0.5741      0.5842     0.0534  5
  test F1                     0.4987      0.5316     0.0756  5
  test sensitivity            0.7652      0.8696     0.2053  5
  test specificity            0.3830      0.2979     0.1466  5
  test precision              0.3758      0.3774     0.0426  5
  test loss                   0.7003      0.7005     0.0099  5
  FPR (FP/(FP+TN))            0.6170      0.7021     0.1466  5
  FNR (FN/(FN+TP))            0.2348      0.1304     0.2053  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7223      0.7580     0.1090  5
  max valid BA                0.7874      0.7695     0.0319  5
  best valid F1               0.7152      0.6957     0.0398  5
  test BA                     0.7271      0.7544     0.1570  5
  test F1                     0.6458      0.6667     0.1683  5
  test sensitivity            0.7478      0.8696     0.1880  5
  test specificity            0.7064      0.8298     0.1888  5
  test precision              0.5814      0.6190     0.1750  5
  test loss                   0.6655      0.6590     0.0171  5
  FPR (FP/(FP+TN))            0.2936      0.1702     0.1888  5
  FNR (FN/(FN+TP))            0.2522      0.1304     0.1880  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5304      0.5273     0.0211  5
  max valid BA                0.5358      0.5306     0.0193  5
  best valid F1               0.5580      0.5926     0.0733  5
  test BA                     0.5063      0.5056     0.0506  5
  test F1                     0.4394      0.4444     0.1536  5
  test sensitivity            0.5631      0.5231     0.3758  5
  test specificity            0.4494      0.3933     0.3957  5
  test precision              0.4909      0.4248     0.2075  5
  test loss                   0.7052      0.6979     0.0190  5
  FPR (FP/(FP+TN))            0.5506      0.6067     0.3957  5
  FNR (FN/(FN+TP))            0.4369      0.4769     0.3758  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6361      0.6528     0.0799  5
  max valid BA                0.6403      0.6528     0.0731  5
  best valid F1               0.5465      0.5769     0.1042  5
  test BA                     0.5806      0.5833     0.0360  5
  test F1                     0.4587      0.4839     0.1093  5
  test sensitivity            0.5944      0.6389     0.3002  5
  test specificity            0.5667      0.4861     0.2877  5
  test precision              0.4339      0.3913     0.0832  5
  test loss                   0.6979      0.7036     0.0192  5
  FPR (FP/(FP+TN))            0.4333      0.5139     0.2877  5
  FNR (FN/(FN+TP))            0.4056      0.3611     0.3002  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6059      0.6029     0.0381  5
  max valid BA                0.6265      0.6324     0.0494  5
  best valid F1               0.4852      0.5000     0.1042  5
  test BA                     0.5529      0.5882     0.0725  5
  test F1                     0.3795      0.4000     0.1783  5
  test sensitivity            0.4353      0.3529     0.2959  5
  test specificity            0.6706      0.7647     0.2175  5
  test precision              0.3945      0.4000     0.1782  5
  test loss                   0.6830      0.6830     0.0244  5
  FPR (FP/(FP+TN))            0.3294      0.2353     0.2175  5
  FNR (FN/(FN+TP))            0.5647      0.6471     0.2959  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label descriptors_v2_lipprop --seeds=0,1,2,3,4`
