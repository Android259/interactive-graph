# descriptors_head_family_neutral_lipprop_rankprot

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_head_family_neutral_lipprop_rankprot'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5164      0.5344      0.3377      0.6683      0.4985      0.5710
groups_GLTP            5      0.2960      0.9040      0.3478      0.7074      0.4077      0.9231
groups_IP_trans        5      0.6000      0.5021      0.4562      0.5851      0.6667      0.5617
groups_LBP_BPI_CETP    5      0.8261      0.5787      0.5794      0.4673      0.7417      0.6553
groups_ML              5      0.1200      0.8800      0.1913      0.8188      0.2000      0.9000
groups_OSBP            5      0.5333      0.4000      0.3592      0.6597      0.7333      0.5667
groups_START           5      0.2615      0.7056      0.3256      0.6515      0.1969      0.9011
groups_lipocalin       5      0.5778      0.4556      0.4575      0.6080      0.4889      0.6639
groups_scp2            5      0.0471      0.9294      0.3080      0.6989      0.2824      0.7824
ALL                   45      0.4198      0.6544      0.3736      0.6517      0.4684      0.7250

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5693      0.5427     0.0877  45
max valid BA                0.5967      0.5735     0.0983  45
best valid F1               0.4618      0.5185     0.2257  45
test BA                     0.5371      0.5000     0.1051  45
test AUC                    0.5127      0.5092     0.1387  45
test AUC in-protein         0.5408      0.5104     0.1570  42
  (proteins averaged)       2.6000      3.0000     1.3718  45
test AUC in-protein (pairs)      0.5330      0.5200     0.1673  45
  (proteins contributing)      3.0222      3.0000     1.7900  45
test F1                     0.3227      0.4000     0.2578  45
test sensitivity            0.4198      0.3200     0.3960  45
test specificity            0.6544      0.8085     0.3520  45
test precision              0.4636      0.4018     0.2278  34
test loss                   0.7048      0.6898     0.0614  45
FPR (FP/(FP+TN))            0.3456      0.1915     0.3520  45
FNR (FN/(FN+TP))            0.5802      0.6800     0.3960  45

=== abs(sensitivity-specificity) gap: mean=0.6823 median=0.7854 n=45 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5232      0.5191     0.0247  5
  max valid BA                0.5347      0.5433     0.0340  5
  best valid F1               0.4751      0.6771     0.3078  5
  test BA                     0.5254      0.5261     0.0265  5
  test AUC                    0.5209      0.5092     0.0227  5
  test AUC in-protein         0.4983      0.5102     0.0774  5
    (proteins averaged)       4.0000      4.0000     0.0000  5
  test AUC in-protein (pairs)      0.5862      0.5945     0.0601  5
    (proteins contributing)      4.4000      4.0000     0.5477  5
  test F1                     0.4006      0.6184     0.3670  5
  test sensitivity            0.5164      0.7015     0.4819  5
  test specificity            0.5344      0.3770     0.4377  5
  test precision              0.5499      0.5529     0.0115  3
  test loss                   0.6648      0.6656     0.0212  5
  FPR (FP/(FP+TN))            0.4656      0.6230     0.4377  5
  FNR (FN/(FN+TP))            0.4836      0.2985     0.4819  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6154      0.5769     0.1096  5
  max valid BA                0.6654      0.6346     0.0877  5
  best valid F1               0.5720      0.5455     0.1181  5
  test BA                     0.6000      0.6000     0.0583  5
  test AUC                    0.4499      0.4528     0.0269  5
  test AUC in-protein         0.4415      0.4333     0.0527  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3948      0.3943     0.0584  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4038      0.4571     0.1911  5
  test sensitivity            0.2960      0.3200     0.1513  5
  test specificity            0.9040      0.9200     0.0669  5
  test precision              0.8010      0.8000     0.1337  5
  test loss                   0.8241      0.8003     0.0581  5
  FPR (FP/(FP+TN))            0.0960      0.0800     0.0669  5
  FNR (FN/(FN+TP))            0.7040      0.6800     0.1513  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5760      0.5616     0.0690  5
  max valid BA                0.6142      0.6028     0.0675  5
  best valid F1               0.5299      0.5217     0.0828  5
  test BA                     0.5511      0.5204     0.0815  5
  test AUC                    0.5915      0.5948     0.0755  5
  test AUC in-protein         0.6626      0.6710     0.1153  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.6254      0.6551     0.0781  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.3986      0.4889     0.1860  5
  test sensitivity            0.6000      0.8696     0.4298  5
  test specificity            0.5021      0.5106     0.4185  5
  test precision              0.4364      0.3387     0.1864  5
  test loss                   0.6754      0.6816     0.0168  5
  FPR (FP/(FP+TN))            0.4979      0.4894     0.4185  5
  FNR (FN/(FN+TP))            0.4000      0.1304     0.4298  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6597      0.6494     0.1444  5
  max valid BA                0.6985      0.7575     0.1630  5
  best valid F1               0.5997      0.6786     0.2220  5
  test BA                     0.7024      0.7021     0.1434  5
  test AUC                    0.6934      0.8455     0.2807  5
  test AUC in-protein         0.6985      0.8837     0.3164  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.7033      0.8831     0.3129  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.6095      0.6216     0.1619  5
  test sensitivity            0.8261      0.9565     0.3180  5
  test specificity            0.5787      0.6809     0.3756  5
  test precision              0.5872      0.5946     0.2053  5
  test loss                   0.6679      0.6812     0.0534  5
  FPR (FP/(FP+TN))            0.4213      0.3191     0.3756  5
  FNR (FN/(FN+TP))            0.1739      0.0435     0.3180  5

groups_ML (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5300      0.5000     0.0447  5
  max valid BA                0.5500      0.5000     0.0707  5
  best valid F1               0.2000      0.0000     0.2767  5
  test BA                     0.5000      0.5000     0.0000  5
  test AUC                    0.4440      0.4800     0.1220  5
  test AUC in-protein         0.4440      0.4800     0.1220  5
    (proteins averaged)       1.0000      1.0000     0.0000  5
  test AUC in-protein (pairs)      0.4440      0.4800     0.1220  5
    (proteins contributing)      1.0000      1.0000     0.0000  5
  test F1                     0.0857      0.0000     0.1917  5
  test sensitivity            0.1200      0.0000     0.2683  5
  test specificity            0.8800      1.0000     0.2683  5
  test precision              0.3333      0.3333     0.0000  1
  test loss                   0.7174      0.7031     0.0288  5
  FPR (FP/(FP+TN))            0.1200      0.0000     0.2683  5
  FNR (FN/(FN+TP))            0.8800      1.0000     0.2683  5

groups_OSBP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6167      0.5833     0.1264  5
  max valid BA                0.6500      0.5833     0.1369  5
  best valid F1               0.5115      0.5455     0.3047  5
  test BA                     0.4667      0.5000     0.1728  5
  test AUC                    0.4556      0.5000     0.1774  5
  test AUC in-protein         0.6389      0.6389     0.1964  2
    (proteins averaged)       0.4000      0.0000     0.5477  5
  test AUC in-protein (pairs)      0.5944      0.6667     0.2236  5
    (proteins contributing)      1.6000      2.0000     0.5477  5
  test F1                     0.3091      0.5000     0.2828  5
  test sensitivity            0.5333      0.6667     0.5055  5
  test specificity            0.4000      0.3333     0.3837  5
  test precision              0.2771      0.3542     0.1868  4
  test loss                   0.6845      0.6498     0.0788  5
  FPR (FP/(FP+TN))            0.6000      0.6667     0.3837  5
  FNR (FN/(FN+TP))            0.4667      0.3333     0.5055  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5173      0.5152     0.0157  5
  max valid BA                0.5490      0.5388     0.0446  5
  best valid F1               0.4720      0.5198     0.1593  5
  test BA                     0.4836      0.4894     0.0451  5
  test AUC                    0.4760      0.5231     0.0755  5
  test AUC in-protein         0.4820      0.4690     0.0759  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4561      0.4458     0.0873  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.2280      0.2202     0.2169  5
  test sensitivity            0.2615      0.1846     0.3621  5
  test specificity            0.7056      0.8876     0.3817  5
  test precision              0.3907      0.3723     0.1177  4
  test loss                   0.7115      0.7085     0.0283  5
  FPR (FP/(FP+TN))            0.2944      0.1124     0.3817  5
  FNR (FN/(FN+TP))            0.7385      0.8154     0.3621  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5681      0.5764     0.0216  5
  max valid BA                0.5764      0.5833     0.0163  5
  best valid F1               0.4833      0.5070     0.0591  5
  test BA                     0.5167      0.5278     0.0603  5
  test AUC                    0.5032      0.5222     0.0399  5
  test AUC in-protein         0.5523      0.5179     0.0662  5
    (proteins averaged)       5.0000      5.0000     0.0000  5
  test AUC in-protein (pairs)      0.5752      0.5468     0.0748  5
    (proteins contributing)      7.2000      7.0000     0.4472  5
  test F1                     0.4175      0.4632     0.1062  5
  test sensitivity            0.5778      0.6111     0.2674  5
  test specificity            0.4556      0.5278     0.2132  5
  test precision              0.3400      0.3465     0.0601  5
  test loss                   0.6740      0.6821     0.0311  5
  FPR (FP/(FP+TN))            0.5444      0.4722     0.2132  5
  FNR (FN/(FN+TP))            0.4222      0.3889     0.2674  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5176      0.5000     0.0242  5
  max valid BA                0.5324      0.5147     0.0381  5
  best valid F1               0.3127      0.3704     0.1873  5
  test BA                     0.4882      0.5000     0.0161  5
  test AUC                    0.4801      0.5069     0.0740  5
  test AUC in-protein         0.5078      0.5106     0.0967  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4174      0.4083     0.0586  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.0516      0.0000     0.1154  5
  test sensitivity            0.0471      0.0000     0.1052  5
  test specificity            0.9294      1.0000     0.1275  5
  test precision              0.1429      0.1429     0.2020  2
  test loss                   0.7236      0.7221     0.0267  5
  FPR (FP/(FP+TN))            0.0706      0.0000     0.1275  5
  FNR (FN/(FN+TP))            0.9529      1.0000     0.1052  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (apolar_sasa_share,aromatic_share,buriedness_q50,chain,hbond,heavy,hydropathy_rim,pocket_elongation,pocket_flatness,pocket_volume_per_sasa,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.263         0.636    0.419              0.609         0.416
GLTP                     0.278         0.676    0.494              0.747         0.388
IP_trans                 0.326         0.509    0.605              0.530         0.518
LBP_BPI_CETP             0.308         0.634    0.676              0.652         0.707
START                    0.273         0.430    0.447              0.497         0.487
lipocalin                0.273         0.663    0.545              0.639         0.467
scp2                     0.275         0.622    0.422              0.617         0.487

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.596               0.617                  0.057                     0.091
net_AUC           0.516               0.490                  0.081                     0.098

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.613               0.614                  0.060                     0.082
net_AUC_pair           0.496               0.492                  0.096                     0.103

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.596  0.428      0.613     0.426
10     0.596  0.458      0.613     0.459
49     0.596  0.505      0.613     0.482
51     0.596  0.510      0.613     0.480
120    0.596  0.516      0.613     0.496

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.621         0.675      0.054
10        0.621         0.681      0.060
49        0.621         0.678      0.058
51        0.621         0.678      0.057
120       0.621         0.668      0.048

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.636  0.419      0.609     0.416     0.636         0.666      0.030
GLTP          0.676  0.494      0.747     0.388     0.676         0.741      0.065
IP_trans      0.509  0.605      0.530     0.518     0.542         0.601      0.059
LBP_BPI_CETP  0.634  0.676      0.652     0.707     0.634         0.754      0.120
START         0.430  0.447      0.497     0.487     0.570         0.595      0.025
lipocalin     0.663  0.545      0.639     0.467     0.663         0.674      0.010
scp2          0.622  0.422      0.617     0.487     0.622         0.646      0.025

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.596               0.617                  0.057                     0.091
net               0.516               0.490                  0.081                     0.098
fit_chem          0.621               0.617                  0.054                     0.048
fit_chem_net      0.668               0.655                  0.058                     0.062
increment         0.048               0.027                  0.039                     0.038

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.613               0.614                  0.060                     0.082
net_pair       0.496               0.492                  0.096                     0.103
```
