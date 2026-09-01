# descriptors_no_extent_coarse_add_hid24

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_add_hid24'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5134      0.5344      0.6183      0.4493      0.5851      0.5935
groups_GLTP            5      0.4160      0.4640      0.5755      0.5748      0.5231      0.5846
groups_IP_trans        5      0.5652      0.6851      0.6182      0.4873      0.5917      0.7021
groups_LBP_BPI_CETP    5      0.7739      0.8213      0.6387      0.5098      0.7583      0.7830
groups_START           5      0.3385      0.6225      0.5618      0.4662      0.3812      0.6607
groups_lipocalin       5      0.4389      0.6972      0.6300      0.5024      0.4944      0.6944
groups_scp2            5      0.6706      0.4353      0.6546      0.4895      0.7412      0.4647
ALL                   35      0.5309      0.6085      0.6139      0.4970      0.5821      0.6404

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6113      0.5735     0.0877  35
max valid BA                0.6327      0.6154     0.0982  35
best valid F1               0.5813      0.5870     0.1082  35
test BA                     0.5697      0.5377     0.1196  35
test F1                     0.4806      0.4800     0.1544  35
test sensitivity            0.5309      0.5538     0.2157  35
test specificity            0.6085      0.6393     0.2004  35
test precision              0.4843      0.4613     0.1229  34
test loss                   0.6776      0.6865     0.0447  35
FPR (FP/(FP+TN))            0.3915      0.3607     0.2004  35
FNR (FN/(FN+TP))            0.4691      0.4462     0.2157  35

=== abs(sensitivity-specificity) gap: mean=0.2646 median=0.2000 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5893      0.5607     0.0604  5
  max valid BA                0.6000      0.5710     0.0565  5
  best valid F1               0.6537      0.6627     0.0403  5
  test BA                     0.5239      0.5130     0.0394  5
  test F1                     0.5190      0.5179     0.0806  5
  test sensitivity            0.5134      0.4328     0.1811  5
  test specificity            0.5344      0.6230     0.2226  5
  test precision              0.5559      0.5400     0.0524  5
  test loss                   0.6910      0.6935     0.0052  5
  FPR (FP/(FP+TN))            0.4656      0.3770     0.2226  5
  FNR (FN/(FN+TP))            0.4866      0.5672     0.1811  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5538      0.5577     0.0285  5
  max valid BA                0.5692      0.5577     0.0292  5
  best valid F1               0.5866      0.5556     0.0474  5
  test BA                     0.4400      0.4600     0.0490  5
  test F1                     0.4159      0.4151     0.1005  5
  test sensitivity            0.4160      0.4400     0.1431  5
  test specificity            0.4640      0.4400     0.1565  5
  test precision              0.4335      0.4167     0.0481  5
  test loss                   0.7271      0.7320     0.0250  5
  FPR (FP/(FP+TN))            0.5360      0.5600     0.1565  5
  FNR (FN/(FN+TP))            0.5840      0.5600     0.1431  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6469      0.6325     0.0618  5
  max valid BA                0.6599      0.6556     0.0648  5
  best valid F1               0.5650      0.5455     0.0668  5
  test BA                     0.6252      0.6230     0.0272  5
  test F1                     0.5104      0.5098     0.0392  5
  test sensitivity            0.5652      0.5652     0.0687  5
  test specificity            0.6851      0.6809     0.0233  5
  test precision              0.4667      0.4643     0.0205  5
  test loss                   0.6567      0.6509     0.0127  5
  FPR (FP/(FP+TN))            0.3149      0.3191     0.0233  5
  FNR (FN/(FN+TP))            0.4348      0.4348     0.0687  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7707      0.7686     0.0418  5
  max valid BA                0.8167      0.8107     0.0259  5
  best valid F1               0.7515      0.7451     0.0364  5
  test BA                     0.7976      0.7849     0.0357  5
  test F1                     0.7224      0.7059     0.0397  5
  test sensitivity            0.7739      0.7826     0.1038  5
  test specificity            0.8213      0.8085     0.0649  5
  test precision              0.6882      0.6957     0.0674  5
  test loss                   0.5943      0.6029     0.0425  5
  FPR (FP/(FP+TN))            0.1787      0.1915     0.0649  5
  FNR (FN/(FN+TP))            0.2261      0.2174     0.1038  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5210      0.5158     0.0248  5
  max valid BA                0.5288      0.5158     0.0369  5
  best valid F1               0.4796      0.5000     0.0458  5
  test BA                     0.4805      0.4792     0.0307  5
  test F1                     0.3206      0.3636     0.1910  5
  test sensitivity            0.3385      0.3077     0.2258  5
  test specificity            0.6225      0.5730     0.2473  5
  test precision              0.3961      0.4034     0.0461  4
  test loss                   0.7045      0.7032     0.0157  5
  FPR (FP/(FP+TN))            0.3775      0.4270     0.2473  5
  FNR (FN/(FN+TP))            0.6615      0.6923     0.2258  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5944      0.5625     0.0620  5
  max valid BA                0.6250      0.5833     0.0775  5
  best valid F1               0.4885      0.4524     0.1271  5
  test BA                     0.5681      0.5764     0.0528  5
  test F1                     0.4001      0.3667     0.1217  5
  test sensitivity            0.4389      0.3056     0.2682  5
  test specificity            0.6972      0.7222     0.2059  5
  test precision              0.4597      0.4265     0.1452  5
  test loss                   0.6772      0.6806     0.0167  5
  FPR (FP/(FP+TN))            0.3028      0.2778     0.2059  5
  FNR (FN/(FN+TP))            0.5611      0.6944     0.2682  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6029      0.6029     0.0465  5
  max valid BA                0.6294      0.6176     0.0503  5
  best valid F1               0.5440      0.5417     0.0548  5
  test BA                     0.5529      0.5147     0.0956  5
  test F1                     0.4758      0.4490     0.1009  5
  test sensitivity            0.6706      0.6471     0.1745  5
  test specificity            0.4353      0.3824     0.1202  5
  test precision              0.3721      0.3438     0.0753  5
  test loss                   0.6923      0.6913     0.0140  5
  FPR (FP/(FP+TN))            0.5647      0.6176     0.1202  5
  FNR (FN/(FN+TP))            0.3294      0.3529     0.1745  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.552         0.494         4         0.340              0.381
   CRAL-TRIO     1   129   67             0.799    0.680         0.634         4         0.551              0.568
   CRAL-TRIO     2   129   67             0.793    0.470         0.358         4         0.472              0.451
   CRAL-TRIO     3   129   67             0.806    0.575         0.504         4         0.469              0.466
   CRAL-TRIO     4   129   67             0.804    0.492         0.471         4         0.433              0.507
        GLTP     0    52   26             0.618    0.577         0.532         2         0.492              0.500
        GLTP     1    52   26             0.601    0.534         0.498         2         0.558              0.500
        GLTP     2    52   26             0.618    0.540         0.490         2         0.547              0.483
        GLTP     3    52   26             0.619    0.519         0.494         2         0.589              0.500
        GLTP     4    52   26             0.621    0.538         0.523         2         0.495              0.509
    IP_trans     0    71   24             0.809    0.721         0.707         3         0.761              0.748
    IP_trans     1    71   24             0.808    0.749         0.756         3         0.720              0.717
    IP_trans     2    71   24             0.810    0.672         0.665         3         0.739              0.784
    IP_trans     3    71   24             0.811    0.656         0.646         3         0.588              0.591
    IP_trans     4    71   24             0.808    0.566         0.555         3         0.623              0.677
LBP_BPI_CETP     0    71   24             0.809    0.799         0.776         2         0.719              0.701
LBP_BPI_CETP     1    71   24             0.816    0.824         0.809         2         0.601              0.675
LBP_BPI_CETP     2    71   24             0.808    0.748         0.745         2         0.623              0.625
LBP_BPI_CETP     3    71   24             0.807    0.770         0.753         2         0.812              0.814
LBP_BPI_CETP     4    71   24             0.804    0.824         0.826         2         0.769              0.764
       START     0   153   64             0.791    0.415         0.431         3         0.508              0.479
       START     1   153   64             0.784    0.472         0.486         3         0.454              0.439
       START     2   153   64             0.794    0.391         0.415         3         0.525              0.558
       START     3   153   64             0.797    0.510         0.535         3         0.596              0.608
       START     4   153   64             0.779    0.442         0.460         3         0.441              0.460
   lipocalin     0   108   36             0.847    0.276         0.201         5         0.605              0.655
   lipocalin     1   108   36             0.827    0.436         0.384         5         0.284              0.217
   lipocalin     2   108   36             0.829    0.394         0.229         5         0.585              0.548
   lipocalin     3   108   36             0.846    0.390         0.241         5         0.352              0.289
   lipocalin     4   108   36             0.810    0.444         0.350         5         0.541              0.463
        scp2     0    51   17             0.808    0.697         0.684         2         0.666              0.619
        scp2     1    51   17             0.837    0.594         0.548         3         0.693              0.626
        scp2     2    51   17             0.851    0.496         0.299         3         0.536              0.417
        scp2     3    51   17             0.842    0.516         0.451         3         0.668              0.576
        scp2     4    51   17             0.834    0.505         0.520         3         0.580              0.405

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.554         0.492       4.0         0.453              0.475
GLTP           52.0  26.0             0.615    0.542         0.507       2.0         0.536              0.499
IP_trans       71.0  24.0             0.809    0.673         0.666       3.0         0.686              0.703
LBP_BPI_CETP   71.0  24.0             0.809    0.793         0.782       2.0         0.705              0.716
START         153.0  64.0             0.789    0.446         0.465       3.0         0.505              0.509
lipocalin     108.0  36.0             0.832    0.388         0.281       5.0         0.473              0.434
scp2           51.0  17.0             0.834    0.562         0.500       2.8         0.629              0.529

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.565          0.676       0.482
null_AUC_k15      0.570          0.673       0.492

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.528          0.649       0.436
null_AUC_prot_k15      0.552          0.649       0.479

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.521      0.552     0.496
10     0.57  0.586      0.552     0.553
49     0.57  0.566      0.552     0.531
51     0.57  0.566      0.552     0.531
120    0.57  0.565      0.552     0.528

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.641      0.034          0.657              0.676           0.019
10        0.607         0.637      0.031          0.657              0.682           0.025
49        0.607         0.644      0.038          0.657              0.681           0.024
51        0.607         0.646      0.039          0.657              0.682           0.025
120       0.607         0.645      0.039          0.657              0.685           0.028

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.554      0.475     0.492      0.023           0.017
GLTP          0.536  0.542      0.499     0.507      0.024           0.004
IP_trans      0.686  0.673      0.703     0.666      0.005           0.008
LBP_BPI_CETP  0.705  0.793      0.716     0.782      0.118           0.090
START         0.505  0.446      0.509     0.465      0.039           0.017
lipocalin     0.473  0.388      0.434     0.281      0.035           0.028
scp2          0.629  0.562      0.529     0.500      0.026           0.033

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.565          0.676       0.482      0.562
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.528          0.649       0.436      0.500
increment           0.039          0.050       0.030      0.026
increment_prot      0.028          0.044       0.017      0.033
```
