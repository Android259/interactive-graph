# geometric_edge_mlp_protgeom_family_neutral_bilinear_fusion_hid16

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_bilinear_fusion_hid16'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5045      0.5148      0.5291      0.5395      0.5552      0.5516
groups_GLTP            5      0.4960      0.4800      0.5117      0.5354      0.4231      0.6462
groups_IP_trans        5      0.4435      0.7149      0.4815      0.5504      0.5083      0.7532
groups_LBP_BPI_CETP    5      0.4609      0.7617      0.5021      0.5629      0.4667      0.7489
groups_START           5      0.5538      0.4966      0.4976      0.5423      0.5563      0.5236
groups_lipocalin       5      0.6056      0.5167      0.5401      0.5361      0.6667      0.5083
groups_scp2            5      0.5765      0.4824      0.5260      0.5075      0.5765      0.5824
ALL                   35      0.5201      0.5667      0.5126      0.5392      0.5361      0.6163

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5770      0.5577     0.0669  35
max valid BA                0.6444      0.6181     0.0662  35
best valid F1               0.6229      0.6154     0.0678  35
test BA                     0.5434      0.5201     0.0718  35
test F1                     0.4154      0.4667     0.2091  35
test sensitivity            0.5201      0.5538     0.3326  35
test specificity            0.5667      0.5278     0.3008  35
test precision              0.4270      0.4400     0.1159  33
test loss                  15.9856      1.1810    33.4954  35
FPR (FP/(FP+TN))            0.4333      0.4722     0.3008  35
FNR (FN/(FN+TP))            0.4799      0.4462     0.3326  35

=== abs(sensitivity-specificity) gap: mean=0.5267 median=0.5726 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5534      0.5514     0.0410  5
  max valid BA                0.6030      0.6078     0.0125  5
  best valid F1               0.6986      0.6947     0.0133  5
  test BA                     0.5096      0.5020     0.0205  5
  test F1                     0.4181      0.5714     0.3125  5
  test sensitivity            0.5045      0.6269     0.4293  5
  test specificity            0.5148      0.3770     0.3971  5
  test precision              0.5183      0.5297     0.0356  4
  test loss                  26.0838      2.9509    37.0022  5
  FPR (FP/(FP+TN))            0.4852      0.6230     0.3971  5
  FNR (FN/(FN+TP))            0.4955      0.3731     0.4293  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5346      0.5385     0.0161  5
  max valid BA                0.6115      0.6154     0.0251  5
  best valid F1               0.6859      0.6761     0.0224  5
  test BA                     0.4880      0.5000     0.0303  5
  test F1                     0.4772      0.5000     0.1035  5
  test sensitivity            0.4960      0.4800     0.1889  5
  test specificity            0.4800      0.4400     0.1939  5
  test precision              0.4889      0.5000     0.0306  5
  test loss                   1.9184      0.8883     2.1996  5
  FPR (FP/(FP+TN))            0.5200      0.5600     0.1939  5
  FNR (FN/(FN+TP))            0.5040      0.5200     0.1889  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6308      0.6241     0.0818  5
  max valid BA                0.6879      0.7057     0.0634  5
  best valid F1               0.5977      0.6154     0.0793  5
  test BA                     0.5792      0.5560     0.0910  5
  test F1                     0.3574      0.3333     0.2480  5
  test sensitivity            0.4435      0.2609     0.4060  5
  test specificity            0.7149      0.8085     0.2285  5
  test precision              0.3440      0.4400     0.1971  5
  test loss                   5.5848      0.6725    10.8552  5
  FPR (FP/(FP+TN))            0.2851      0.1915     0.2285  5
  FNR (FN/(FN+TP))            0.5565      0.7391     0.4060  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6078      0.5616     0.0915  5
  max valid BA                0.7308      0.7367     0.0626  5
  best valid F1               0.6521      0.6545     0.0600  5
  test BA                     0.6113      0.6110     0.1165  5
  test F1                     0.4044      0.4651     0.2629  5
  test sensitivity            0.4609      0.4348     0.3847  5
  test specificity            0.7617      0.8085     0.2460  5
  test precision              0.4665      0.4286     0.1268  5
  test loss                   6.2895      1.9487    10.9413  5
  FPR (FP/(FP+TN))            0.2383      0.1915     0.2460  5
  FNR (FN/(FN+TP))            0.5391      0.5652     0.3847  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5399      0.5509     0.0397  5
  max valid BA                0.5681      0.5700     0.0215  5
  best valid F1               0.5956      0.6049     0.0173  5
  test BA                     0.5252      0.5241     0.0541  5
  test F1                     0.4316      0.4932     0.2391  5
  test sensitivity            0.5538      0.5538     0.3676  5
  test specificity            0.4966      0.4944     0.3181  5
  test precision              0.3977      0.4362     0.1178  5
  test loss                  42.9928      4.1929    72.5705  5
  FPR (FP/(FP+TN))            0.5034      0.5056     0.3181  5
  FNR (FN/(FN+TP))            0.4462      0.4462     0.3676  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5875      0.5972     0.0446  5
  max valid BA                0.6681      0.6806     0.0296  5
  best valid F1               0.5746      0.5843     0.0388  5
  test BA                     0.5611      0.5556     0.0338  5
  test F1                     0.4387      0.5106     0.1339  5
  test sensitivity            0.6056      0.6667     0.3200  5
  test specificity            0.5167      0.5278     0.3045  5
  test precision              0.3958      0.3846     0.0405  5
  test loss                  12.9825      0.9699    25.8687  5
  FPR (FP/(FP+TN))            0.4833      0.4722     0.3045  5
  FNR (FN/(FN+TP))            0.3944      0.3333     0.3200  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5853      0.5588     0.0885  5
  max valid BA                0.6412      0.6029     0.0629  5
  best valid F1               0.5560      0.5484     0.0569  5
  test BA                     0.5294      0.5000     0.0540  5
  test F1                     0.3805      0.4667     0.2140  5
  test sensitivity            0.5765      0.7059     0.3776  5
  test specificity            0.4824      0.2941     0.4014  5
  test precision              0.3882      0.3444     0.1010  4
  test loss                  16.0472      1.1810    20.9459  5
  FPR (FP/(FP+TN))            0.5176      0.7059     0.4014  5
  FNR (FN/(FN+TP))            0.4235      0.2941     0.3776  5
```

## AUC vs chemistry null model, in-sample increment

