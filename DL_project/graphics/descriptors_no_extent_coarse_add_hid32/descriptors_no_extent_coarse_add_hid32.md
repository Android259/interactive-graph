# descriptors_no_extent_coarse_add_hid32

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_add_hid32'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4985      0.6197      0.5274      0.5222      0.5552      0.5903
groups_GLTP            5      0.4560      0.5040      0.5622      0.5193      0.5231      0.5538
groups_IP_trans        5      0.5130      0.6851      0.6292      0.5003      0.5500      0.7404
groups_LBP_BPI_CETP    5      0.7478      0.8128      0.6077      0.5619      0.8083      0.7872
groups_START           5      0.3908      0.5955      0.6355      0.4423      0.4125      0.5775
groups_lipocalin       5      0.5500      0.6222      0.5615      0.5401      0.5444      0.6528
groups_scp2            5      0.8353      0.3294      0.5953      0.4787      0.8471      0.3882
ALL                   35      0.5702      0.5955      0.5884      0.5092      0.6058      0.6129

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6094      0.5723     0.1032  35
max valid BA                0.6308      0.6324     0.1061  35
best valid F1               0.5854      0.5857     0.1090  35
test BA                     0.5829      0.5764     0.1080  35
test F1                     0.4982      0.5075     0.1497  35
test sensitivity            0.5702      0.5672     0.2301  35
test specificity            0.5955      0.6176     0.2049  35
test precision              0.4771      0.4545     0.1379  35
test loss                   0.6768      0.6857     0.0436  35
FPR (FP/(FP+TN))            0.4045      0.3824     0.2049  35
FNR (FN/(FN+TP))            0.4298      0.4328     0.2301  35

=== abs(sensitivity-specificity) gap: mean=0.2707 median=0.1512 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5728      0.5593     0.0443  5
  max valid BA                0.6020      0.6286     0.0535  5
  best valid F1               0.6437      0.6585     0.0380  5
  test BA                     0.5591      0.5535     0.0579  5
  test F1                     0.5176      0.5690     0.1666  5
  test sensitivity            0.4985      0.5373     0.2177  5
  test specificity            0.6197      0.6885     0.1816  5
  test precision              0.5806      0.5618     0.0878  5
  test loss                   0.6893      0.6857     0.0181  5
  FPR (FP/(FP+TN))            0.3803      0.3115     0.1816  5
  FNR (FN/(FN+TP))            0.5015      0.4627     0.2177  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5385      0.5385     0.0236  5
  max valid BA                0.5577      0.5385     0.0333  5
  best valid F1               0.5830      0.5614     0.0493  5
  test BA                     0.4800      0.4600     0.0600  5
  test F1                     0.4591      0.4255     0.1013  5
  test sensitivity            0.4560      0.4000     0.1539  5
  test specificity            0.5040      0.5200     0.0669  5
  test precision              0.4713      0.4545     0.0556  5
  test loss                   0.7183      0.7127     0.0257  5
  FPR (FP/(FP+TN))            0.4960      0.4800     0.0669  5
  FNR (FN/(FN+TP))            0.5440      0.6000     0.1539  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6452      0.6445     0.0725  5
  max valid BA                0.6581      0.6764     0.0772  5
  best valid F1               0.5596      0.5405     0.0742  5
  test BA                     0.5991      0.6124     0.0527  5
  test F1                     0.4685      0.5000     0.0892  5
  test sensitivity            0.5130      0.5652     0.1422  5
  test specificity            0.6851      0.6809     0.0485  5
  test precision              0.4378      0.4483     0.0447  5
  test loss                   0.6620      0.6623     0.0115  5
  FPR (FP/(FP+TN))            0.3149      0.3191     0.0485  5
  FNR (FN/(FN+TP))            0.4870      0.4348     0.1422  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7978      0.7996     0.0353  5
  max valid BA                0.8293      0.8209     0.0336  5
  best valid F1               0.7655      0.7547     0.0409  5
  test BA                     0.7803      0.7525     0.0645  5
  test F1                     0.6989      0.6667     0.0798  5
  test sensitivity            0.7478      0.7391     0.1282  5
  test specificity            0.8128      0.8298     0.0461  5
  test precision              0.6625      0.6842     0.0587  5
  test loss                   0.5924      0.5961     0.0293  5
  FPR (FP/(FP+TN))            0.1872      0.1702     0.0461  5
  FNR (FN/(FN+TP))            0.2522      0.2609     0.1282  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4950      0.4932     0.0478  5
  max valid BA                0.5096      0.5035     0.0573  5
  best valid F1               0.4938      0.4935     0.0508  5
  test BA                     0.4931      0.4831     0.0538  5
  test F1                     0.3599      0.4113     0.2096  5
  test sensitivity            0.3908      0.4462     0.2296  5
  test specificity            0.5955      0.4719     0.2158  5
  test precision              0.3345      0.3816     0.1950  5
  test loss                   0.6965      0.6942     0.0102  5
  FPR (FP/(FP+TN))            0.4045      0.5281     0.2158  5
  FNR (FN/(FN+TP))            0.6092      0.5538     0.2296  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5986      0.5972     0.0552  5
  max valid BA                0.6028      0.5972     0.0518  5
  best valid F1               0.4798      0.5357     0.1261  5
  test BA                     0.5861      0.5833     0.0561  5
  test F1                     0.4567      0.4381     0.0963  5
  test sensitivity            0.5500      0.6389     0.2674  5
  test specificity            0.6222      0.6250     0.2616  5
  test precision              0.4628      0.4706     0.0997  5
  test loss                   0.6827      0.6600     0.0367  5
  FPR (FP/(FP+TN))            0.3778      0.3750     0.2616  5
  FNR (FN/(FN+TP))            0.4500      0.3611     0.2674  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6176      0.6618     0.0750  5
  max valid BA                0.6559      0.6618     0.0246  5
  best valid F1               0.5724      0.5926     0.0335  5
  test BA                     0.5824      0.6029     0.0789  5
  test F1                     0.5265      0.5517     0.0642  5
  test sensitivity            0.8353      0.8824     0.1523  5
  test specificity            0.3294      0.2941     0.1745  5
  test precision              0.3899      0.3902     0.0623  5
  test loss                   0.6966      0.6955     0.0146  5
  FPR (FP/(FP+TN))            0.6706      0.7059     0.1745  5
  FNR (FN/(FN+TP))            0.1647      0.1176     0.1523  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.523         0.501         4         0.340              0.381
   CRAL-TRIO     1   129   67             0.799    0.542         0.492         4         0.551              0.568
   CRAL-TRIO     2   129   67             0.793    0.459         0.335         4         0.472              0.451
   CRAL-TRIO     3   129   67             0.806    0.616         0.514         4         0.469              0.466
   CRAL-TRIO     4   129   67             0.804    0.455         0.417         4         0.433              0.507
        GLTP     0    52   26             0.618    0.577         0.534         2         0.492              0.500
        GLTP     1    52   26             0.601    0.536         0.500         2         0.558              0.500
        GLTP     2    52   26             0.618    0.528         0.485         2         0.547              0.483
        GLTP     3    52   26             0.619    0.531         0.500         2         0.589              0.500
        GLTP     4    52   26             0.621    0.522         0.500         2         0.495              0.509
    IP_trans     0    71   24             0.809    0.688         0.659         3         0.761              0.748
    IP_trans     1    71   24             0.808    0.730         0.748         3         0.720              0.717
    IP_trans     2    71   24             0.810    0.650         0.642         3         0.739              0.784
    IP_trans     3    71   24             0.811    0.638         0.604         3         0.588              0.591
    IP_trans     4    71   24             0.808    0.550         0.573         3         0.623              0.677
LBP_BPI_CETP     0    71   24             0.809    0.786         0.767         2         0.719              0.701
LBP_BPI_CETP     1    71   24             0.816    0.870         0.859         2         0.601              0.675
LBP_BPI_CETP     2    71   24             0.808    0.778         0.778         2         0.623              0.625
LBP_BPI_CETP     3    71   24             0.807    0.770         0.766         2         0.812              0.814
LBP_BPI_CETP     4    71   24             0.804    0.880         0.889         2         0.769              0.764
       START     0   153   64             0.791    0.414         0.427         3         0.508              0.479
       START     1   153   64             0.784    0.470         0.478         3         0.454              0.439
       START     2   153   64             0.794    0.372         0.417         3         0.525              0.558
       START     3   153   64             0.797    0.557         0.561         3         0.596              0.608
       START     4   153   64             0.779    0.455         0.479         3         0.441              0.460
   lipocalin     0   108   36             0.847    0.282         0.224         5         0.605              0.655
   lipocalin     1   108   36             0.827    0.352         0.295         5         0.284              0.217
   lipocalin     2   108   36             0.829    0.407         0.244         5         0.585              0.548
   lipocalin     3   108   36             0.846    0.398         0.258         5         0.352              0.289
   lipocalin     4   108   36             0.810    0.397         0.228         5         0.541              0.463
        scp2     0    51   17             0.808    0.622         0.648         2         0.666              0.619
        scp2     1    51   17             0.837    0.382         0.362         3         0.693              0.626
        scp2     2    51   17             0.851    0.593         0.402         3         0.536              0.417
        scp2     3    51   17             0.842    0.606         0.544         3         0.668              0.576
        scp2     4    51   17             0.834    0.670         0.717         3         0.580              0.405

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.519         0.452       4.0         0.453              0.475
GLTP           52.0  26.0             0.615    0.539         0.504       2.0         0.536              0.499
IP_trans       71.0  24.0             0.809    0.651         0.645       3.0         0.686              0.703
LBP_BPI_CETP   71.0  24.0             0.809    0.817         0.812       2.0         0.705              0.716
START         153.0  64.0             0.789    0.454         0.473       3.0         0.505              0.509
lipocalin     108.0  36.0             0.832    0.367         0.250       5.0         0.473              0.434
scp2           51.0  17.0             0.834    0.575         0.535       2.8         0.629              0.529

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC            0.56          0.681       0.470
null_AUC_k15       0.57          0.673       0.492

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.524          0.664       0.419
null_AUC_prot_k15      0.552          0.649       0.479

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.566      0.552     0.571
10     0.57  0.570      0.552     0.544
49     0.57  0.558      0.552     0.520
51     0.57  0.556      0.552     0.519
120    0.57  0.560      0.552     0.524

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.656      0.049          0.657              0.691           0.035
10        0.607         0.639      0.032          0.657              0.674           0.017
49        0.607         0.644      0.038          0.657              0.679           0.022
51        0.607         0.646      0.040          0.657              0.680           0.023
120       0.607         0.648      0.041          0.657              0.682           0.025

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.519      0.475     0.452      0.023           0.012
GLTP          0.536  0.539      0.499     0.504      0.020           0.005
IP_trans      0.686  0.651      0.703     0.645     -0.013           0.004
LBP_BPI_CETP  0.705  0.817      0.716     0.812      0.121           0.094
START         0.505  0.454      0.509     0.473      0.041           0.018
lipocalin     0.473  0.367      0.434     0.250      0.060           0.028
scp2          0.629  0.575      0.529     0.535      0.038           0.013

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.560          0.681       0.470      0.575
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.524          0.664       0.419      0.535
increment           0.041          0.048       0.036      0.038
increment_prot      0.025          0.037       0.016      0.013
```
