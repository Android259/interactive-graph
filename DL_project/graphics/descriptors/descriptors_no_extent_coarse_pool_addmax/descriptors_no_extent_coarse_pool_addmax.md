# descriptors_no_extent_coarse_pool_addmax

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_pool_addmax'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4328      0.6984      0.6120      0.4836      0.5224      0.6806
groups_GLTP            5      0.4000      0.4960      0.5982      0.5434      0.4692      0.6231
groups_IP_trans        5      0.5739      0.6851      0.6562      0.4868      0.5833      0.7191
groups_LBP_BPI_CETP    5      0.7478      0.8511      0.6722      0.4784      0.8083      0.8213
groups_START           5      0.4862      0.5281      0.6321      0.4614      0.5344      0.5303
groups_lipocalin       5      0.4778      0.7056      0.6116      0.5578      0.5111      0.6722
groups_scp2            5      0.8118      0.3176      0.6245      0.5097      0.8118      0.4235
ALL                   35      0.5615      0.6117      0.6295      0.5030      0.6058      0.6386

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6222      0.5905     0.1059  35
max valid BA                0.6338      0.6250     0.1053  35
best valid F1               0.5789      0.5660     0.1125  35
test BA                     0.5866      0.5636     0.1142  35
test F1                     0.5067      0.4925     0.1245  35
test sensitivity            0.5615      0.5224     0.2091  35
test specificity            0.6117      0.6557     0.2083  35
test precision              0.5013      0.4800     0.1233  35
test loss                   0.6754      0.6857     0.0348  35
FPR (FP/(FP+TN))            0.3883      0.3443     0.2083  35
FNR (FN/(FN+TP))            0.4385      0.4776     0.2091  35

=== abs(sensitivity-specificity) gap: mean=0.2551 median=0.1334 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6015      0.5894     0.0487  5
  max valid BA                0.6053      0.5969     0.0483  5
  best valid F1               0.6215      0.6258     0.0455  5
  test BA                     0.5656      0.5636     0.0223  5
  test F1                     0.4974      0.5203     0.0952  5
  test sensitivity            0.4328      0.4776     0.1280  5
  test specificity            0.6984      0.6557     0.1034  5
  test precision              0.6156      0.6250     0.0261  5
  test loss                   0.6845      0.6891     0.0103  5
  FPR (FP/(FP+TN))            0.3016      0.3443     0.1034  5
  FNR (FN/(FN+TP))            0.5672      0.5224     0.1280  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5462      0.5385     0.0443  5
  max valid BA                0.5654      0.5385     0.0661  5
  best valid F1               0.5372      0.5517     0.0779  5
  test BA                     0.4480      0.4600     0.0460  5
  test F1                     0.4187      0.4000     0.0364  5
  test sensitivity            0.4000      0.4000     0.0632  5
  test specificity            0.4960      0.4800     0.1284  5
  test precision              0.4475      0.4500     0.0438  5
  test loss                   0.7170      0.7155     0.0106  5
  FPR (FP/(FP+TN))            0.5040      0.5200     0.1284  5
  FNR (FN/(FN+TP))            0.6000      0.6000     0.0632  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6512      0.6321     0.0698  5
  max valid BA                0.6618      0.6636     0.0660  5
  best valid F1               0.5731      0.5660     0.0598  5
  test BA                     0.6295      0.6240     0.0240  5
  test F1                     0.5155      0.5263     0.0381  5
  test sensitivity            0.5739      0.6087     0.0891  5
  test specificity            0.6851      0.6809     0.0645  5
  test precision              0.4732      0.4667     0.0261  5
  test loss                   0.6562      0.6561     0.0095  5
  FPR (FP/(FP+TN))            0.3149      0.3191     0.0645  5
  FNR (FN/(FN+TP))            0.4261      0.3913     0.0891  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8148      0.8107     0.0218  5
  max valid BA                0.8169      0.8107     0.0205  5
  best valid F1               0.7521      0.7451     0.0258  5
  test BA                     0.7994      0.7946     0.0367  5
  test F1                     0.7269      0.7273     0.0457  5
  test sensitivity            0.7478      0.7391     0.1038  5
  test specificity            0.8511      0.8723     0.0542  5
  test precision              0.7168      0.7368     0.0519  5
  test loss                   0.6118      0.6173     0.0198  5
  FPR (FP/(FP+TN))            0.1489      0.1277     0.0542  5
  FNR (FN/(FN+TP))            0.2522      0.2609     0.1038  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5324      0.5689     0.0615  5
  max valid BA                0.5407      0.5689     0.0640  5
  best valid F1               0.5105      0.5397     0.0825  5
  test BA                     0.5071      0.5117     0.0533  5
  test F1                     0.4427      0.4478     0.0948  5
  test sensitivity            0.4862      0.4615     0.2117  5
  test specificity            0.5281      0.5618     0.2186  5
  test precision              0.4337      0.4348     0.0719  5
  test loss                   0.6952      0.6909     0.0089  5
  FPR (FP/(FP+TN))            0.4719      0.4382     0.2186  5
  FNR (FN/(FN+TP))            0.5138      0.5385     0.2117  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5917      0.5764     0.0594  5
  max valid BA                0.6056      0.6250     0.0543  5
  best valid F1               0.4756      0.5570     0.1250  5
  test BA                     0.5917      0.5556     0.0861  5
  test F1                     0.4403      0.4421     0.1510  5
  test sensitivity            0.4778      0.5833     0.2368  5
  test specificity            0.7056      0.6944     0.1551  5
  test precision              0.4493      0.5000     0.0894  5
  test loss                   0.6677      0.6696     0.0194  5
  FPR (FP/(FP+TN))            0.2944      0.3056     0.1551  5
  FNR (FN/(FN+TP))            0.5222      0.4167     0.2368  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6176      0.6029     0.1091  5
  max valid BA                0.6412      0.6324     0.1188  5
  best valid F1               0.5824      0.5600     0.1078  5
  test BA                     0.5647      0.5735     0.0638  5
  test F1                     0.5055      0.5185     0.0699  5
  test sensitivity            0.8118      0.8824     0.2012  5
  test specificity            0.3176      0.3235     0.1745  5
  test precision              0.3729      0.3784     0.0363  5
  test loss                   0.6954      0.6914     0.0169  5
  FPR (FP/(FP+TN))            0.6824      0.6765     0.1745  5
  FNR (FN/(FN+TP))            0.1882      0.1176     0.2012  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.539         0.509         4         0.340              0.381
   CRAL-TRIO     1   129   67             0.799    0.550         0.492         4         0.551              0.568
   CRAL-TRIO     2   129   67             0.793    0.527         0.438         4         0.472              0.451
   CRAL-TRIO     3   129   67             0.806    0.631         0.479         4         0.469              0.466
   CRAL-TRIO     4   129   67             0.804    0.493         0.478         4         0.433              0.507
        GLTP     0    52   26             0.618    0.583         0.554         2         0.492              0.500
        GLTP     1    52   26             0.601    0.533         0.512         2         0.558              0.500
        GLTP     2    52   26             0.618    0.555         0.496         2         0.547              0.483
        GLTP     3    52   26             0.619    0.553         0.500         2         0.589              0.500
        GLTP     4    52   26             0.621    0.538         0.503         2         0.495              0.509
    IP_trans     0    71   24             0.809    0.711         0.704         3         0.761              0.748
    IP_trans     1    71   24             0.808    0.737         0.751         3         0.720              0.717
    IP_trans     2    71   24             0.810    0.672         0.654         3         0.739              0.784
    IP_trans     3    71   24             0.811    0.610         0.625         3         0.588              0.591
    IP_trans     4    71   24             0.808    0.552         0.553         3         0.623              0.677
LBP_BPI_CETP     0    71   24             0.809    0.780         0.755         2         0.719              0.701
LBP_BPI_CETP     1    71   24             0.816    0.858         0.831         2         0.601              0.675
LBP_BPI_CETP     2    71   24             0.808    0.812         0.820         2         0.623              0.625
LBP_BPI_CETP     3    71   24             0.807    0.762         0.753         2         0.812              0.814
LBP_BPI_CETP     4    71   24             0.804    0.854         0.858         2         0.769              0.764
       START     0   153   64             0.791    0.424         0.424         3         0.508              0.479
       START     1   153   64             0.784    0.498         0.508         3         0.454              0.439
       START     2   153   64             0.794    0.391         0.428         3         0.525              0.558
       START     3   153   64             0.797    0.574         0.561         3         0.596              0.608
       START     4   153   64             0.779    0.446         0.462         3         0.441              0.460
   lipocalin     0   108   36             0.847    0.279         0.211         5         0.605              0.655
   lipocalin     1   108   36             0.827    0.445         0.411         5         0.284              0.217
   lipocalin     2   108   36             0.829    0.545         0.459         5         0.585              0.548
   lipocalin     3   108   36             0.846    0.562         0.539         5         0.352              0.289
   lipocalin     4   108   36             0.810    0.557         0.575         5         0.541              0.463
        scp2     0    51   17             0.808    0.689         0.749         2         0.666              0.619
        scp2     1    51   17             0.837    0.615         0.466         3         0.693              0.626
        scp2     2    51   17             0.851    0.592         0.409         3         0.536              0.417
        scp2     3    51   17             0.842    0.533         0.383         3         0.668              0.576
        scp2     4    51   17             0.834    0.673         0.744         3         0.580              0.405

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.548         0.479       4.0         0.453              0.475
GLTP           52.0  26.0             0.615    0.552         0.513       2.0         0.536              0.499
IP_trans       71.0  24.0             0.809    0.656         0.657       3.0         0.686              0.703
LBP_BPI_CETP   71.0  24.0             0.809    0.813         0.803       2.0         0.705              0.716
START         153.0  64.0             0.789    0.466         0.477       3.0         0.505              0.509
lipocalin     108.0  36.0             0.832    0.478         0.439       5.0         0.473              0.434
scp2           51.0  17.0             0.834    0.620         0.550       2.8         0.629              0.529

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.591          0.697       0.511
null_AUC_k15      0.570          0.673       0.492

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.560          0.670       0.477
null_AUC_prot_k15      0.552          0.649       0.479

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.512      0.552     0.505
10     0.57  0.568      0.552     0.548
49     0.57  0.606      0.552     0.579
51     0.57  0.605      0.552     0.577
120    0.57  0.591      0.552     0.560

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.671      0.065          0.657              0.705           0.048
10        0.607         0.652      0.046          0.657              0.688           0.031
49        0.607         0.641      0.034          0.657              0.681           0.024
51        0.607         0.639      0.032          0.657              0.681           0.024
120       0.607         0.642      0.036          0.657              0.681           0.025

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.548      0.475     0.479      0.011           0.011
GLTP          0.536  0.552      0.499     0.513      0.022           0.002
IP_trans      0.686  0.656      0.703     0.657     -0.003           0.000
LBP_BPI_CETP  0.705  0.813      0.716     0.803      0.118           0.093
START         0.505  0.466      0.509     0.477      0.035           0.015
lipocalin     0.473  0.478      0.434     0.439      0.049           0.037
scp2          0.629  0.620      0.529     0.550      0.017           0.015

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.591          0.697       0.511      0.620
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.560          0.670       0.477      0.550
increment           0.036          0.044       0.029      0.017
increment_prot      0.025          0.036       0.016      0.015
```
