# descriptors_shares_coarse

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_shares_coarse'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4299      0.6557         n/a         n/a         n/a         n/a
groups_GLTP            5      0.2960      0.6080         n/a         n/a         n/a         n/a
groups_IP_trans        5      0.5130      0.7149         n/a         n/a         n/a         n/a
groups_LBP_BPI_CETP    5      0.7652      0.8298         n/a         n/a         n/a         n/a
groups_START           5      0.3015      0.6764         n/a         n/a         n/a         n/a
groups_lipocalin       5      0.5944      0.5556         n/a         n/a         n/a         n/a
groups_scp2            5      0.7647      0.4000         n/a         n/a         n/a         n/a
ALL                   35      0.5235      0.6343         n/a         n/a         n/a         n/a

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6175      0.6110     0.0930  35
max valid BA                0.6284      0.6228     0.0963  35
best valid F1               0.5829      0.5915     0.1111  35
test BA                     0.5789      0.5588     0.1109  35
test F1                     0.4641      0.4828     0.1820  35
test sensitivity            0.5235      0.5652     0.2489  35
test specificity            0.6343      0.6404     0.2126  35
test precision              0.4903      0.4583     0.1144  33
test loss                   0.6848      0.6923     0.0173  35
FPR (FP/(FP+TN))            0.3657      0.3596     0.2126  35
FNR (FN/(FN+TP))            0.4765      0.4348     0.2489  35

=== abs(sensitivity-specificity) gap: mean=0.3260 median=0.2800 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5717      0.5862     0.0401  5
  max valid BA                0.5846      0.6041     0.0442  5
  best valid F1               0.6217      0.6250     0.0656  5
  test BA                     0.5428      0.5368     0.0362  5
  test F1                     0.4860      0.4786     0.0870  5
  test sensitivity            0.4299      0.4179     0.1264  5
  test specificity            0.6557      0.6557     0.0666  5
  test precision              0.5741      0.5714     0.0350  5
  test loss                   0.6901      0.6923     0.0049  5
  FPR (FP/(FP+TN))            0.3443      0.3443     0.0666  5
  FNR (FN/(FN+TP))            0.5701      0.5821     0.1264  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5385     0.0421  5
  max valid BA                0.5615      0.5385     0.0534  5
  best valid F1               0.6011      0.6667     0.1196  5
  test BA                     0.4520      0.4600     0.0438  5
  test F1                     0.3120      0.3721     0.1816  5
  test sensitivity            0.2960      0.3200     0.1992  5
  test specificity            0.6080      0.6000     0.2834  5
  test precision              0.4345      0.4410     0.0155  4
  test loss                   0.6974      0.6974     0.0042  5
  FPR (FP/(FP+TN))            0.3920      0.4000     0.2834  5
  FNR (FN/(FN+TP))            0.7040      0.6800     0.1992  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6493      0.6321     0.0556  5
  max valid BA                0.6515      0.6321     0.0583  5
  best valid F1               0.5488      0.5352     0.0692  5
  test BA                     0.6140      0.6124     0.0264  5
  test F1                     0.4854      0.5000     0.0541  5
  test sensitivity            0.5130      0.5652     0.1038  5
  test specificity            0.7149      0.7234     0.0613  5
  test precision              0.4688      0.4667     0.0194  5
  test loss                   0.6768      0.6751     0.0123  5
  FPR (FP/(FP+TN))            0.2851      0.2766     0.0613  5
  FNR (FN/(FN+TP))            0.4870      0.4348     0.1038  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7935      0.7890     0.0284  5
  max valid BA                0.8104      0.8001     0.0245  5
  best valid F1               0.7415      0.7308     0.0293  5
  test BA                     0.7975      0.7845     0.0357  5
  test F1                     0.7227      0.7083     0.0429  5
  test sensitivity            0.7652      0.7391     0.0848  5
  test specificity            0.8298      0.8298     0.0261  5
  test precision              0.6879      0.6800     0.0248  5
  test loss                   0.6614      0.6684     0.0267  5
  FPR (FP/(FP+TN))            0.1702      0.1702     0.0261  5
  FNR (FN/(FN+TP))            0.2348      0.2609     0.0848  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5292      0.5022     0.0384  5
  max valid BA                0.5349      0.5119     0.0385  5
  best valid F1               0.4960      0.4690     0.0984  5
  test BA                     0.4890      0.5000     0.0407  5
  test F1                     0.2642      0.2364     0.2436  5
  test sensitivity            0.3015      0.2000     0.3191  5
  test specificity            0.6764      0.6404     0.3107  5
  test precision              0.4132      0.4319     0.0897  4
  test loss                   0.6938      0.6949     0.0027  5
  FPR (FP/(FP+TN))            0.3236      0.3596     0.3107  5
  FNR (FN/(FN+TP))            0.6985      0.8000     0.3191  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5875      0.6181     0.0550  5
  max valid BA                0.6028      0.6319     0.0692  5
  best valid F1               0.4941      0.5546     0.1247  5
  test BA                     0.5750      0.5764     0.0388  5
  test F1                     0.4616      0.4800     0.0880  5
  test sensitivity            0.5944      0.6667     0.2304  5
  test specificity            0.5556      0.4861     0.2138  5
  test precision              0.4338      0.4110     0.1050  5
  test loss                   0.6820      0.6932     0.0207  5
  FPR (FP/(FP+TN))            0.4444      0.5139     0.2138  5
  FNR (FN/(FN+TP))            0.4056      0.3333     0.2304  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6412      0.6471     0.0424  5
  max valid BA                0.6529      0.6471     0.0339  5
  best valid F1               0.5769      0.5769     0.0303  5
  test BA                     0.5824      0.6029     0.0556  5
  test F1                     0.5169      0.5306     0.0455  5
  test sensitivity            0.7647      0.7647     0.0930  5
  test specificity            0.4000      0.3824     0.1292  5
  test precision              0.3934      0.4000     0.0480  5
  test loss                   0.6924      0.6923     0.0056  5
  FPR (FP/(FP+TN))            0.6000      0.6176     0.1292  5
  FNR (FN/(FN+TP))            0.2353      0.2353     0.0930  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.533         0.514         4         0.340              0.381
   CRAL-TRIO     1   129   67             0.799    0.602         0.644         4         0.551              0.568
   CRAL-TRIO     2   129   67             0.793    0.492         0.478         4         0.472              0.451
   CRAL-TRIO     3   129   67             0.806    0.604         0.610         4         0.469              0.466
   CRAL-TRIO     4   129   67             0.804    0.487         0.538         4         0.433              0.507
        GLTP     0    52   26             0.618    0.578         0.545         2         0.492              0.500
        GLTP     1    52   26             0.601    0.497         0.501         2         0.558              0.500
        GLTP     2    52   26             0.618    0.531         0.486         2         0.547              0.483
        GLTP     3    52   26             0.619    0.525         0.473         2         0.589              0.500
        GLTP     4    52   26             0.621    0.525         0.521         2         0.495              0.509
    IP_trans     0    71   24             0.809    0.708         0.698         3         0.761              0.748
    IP_trans     1    71   24             0.808    0.661         0.685         3         0.720              0.717
    IP_trans     2    71   24             0.810    0.584         0.559         3         0.739              0.784
    IP_trans     3    71   24             0.811    0.603         0.597         3         0.588              0.591
    IP_trans     4    71   24             0.808    0.546         0.570         3         0.623              0.677
LBP_BPI_CETP     0    71   24             0.809    0.803         0.783         2         0.719              0.701
LBP_BPI_CETP     1    71   24             0.816    0.829         0.854         2         0.601              0.675
LBP_BPI_CETP     2    71   24             0.808    0.843         0.832         2         0.623              0.625
LBP_BPI_CETP     3    71   24             0.807    0.768         0.756         2         0.812              0.814
LBP_BPI_CETP     4    71   24             0.804    0.791         0.823         2         0.769              0.764
       START     0   153   64             0.791    0.452         0.417         3         0.508              0.479
       START     1   153   64             0.784    0.519         0.509         3         0.454              0.439
       START     2   153   64             0.794    0.409         0.404         3         0.525              0.558
       START     3   153   64             0.797    0.615         0.565         3         0.596              0.608
       START     4   153   64             0.779    0.507         0.465         3         0.441              0.460
   lipocalin     0   108   36             0.847    0.459         0.363         5         0.605              0.655
   lipocalin     1   108   36             0.827    0.631         0.695         5         0.284              0.217
   lipocalin     2   108   36             0.829    0.611         0.565         5         0.585              0.548
   lipocalin     3   108   36             0.846    0.691         0.734         5         0.352              0.289
   lipocalin     4   108   36             0.810    0.529         0.564         5         0.541              0.463
        scp2     0    51   17             0.808    0.706         0.751         2         0.666              0.619
        scp2     1    51   17             0.837    0.644         0.638         3         0.693              0.626
        scp2     2    51   17             0.851    0.582         0.430         3         0.536              0.417
        scp2     3    51   17             0.842    0.690         0.585         3         0.668              0.576
        scp2     4    51   17             0.834    0.613         0.608         3         0.580              0.405

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.544         0.557       4.0         0.453              0.475
GLTP           52.0  26.0             0.615    0.531         0.505       2.0         0.536              0.499
IP_trans       71.0  24.0             0.809    0.620         0.622       3.0         0.686              0.703
LBP_BPI_CETP   71.0  24.0             0.809    0.807         0.810       2.0         0.705              0.716
START         153.0  64.0             0.789    0.500         0.472       3.0         0.505              0.509
lipocalin     108.0  36.0             0.832    0.584         0.584       5.0         0.473              0.434
scp2           51.0  17.0             0.834    0.647         0.602       2.8         0.629              0.529

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.605          0.691       0.540
null_AUC_k15      0.570          0.673       0.492

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.593          0.678       0.530
null_AUC_prot_k15      0.552          0.649       0.479

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.436      0.552     0.449
10     0.57  0.551      0.552     0.560
49     0.57  0.607      0.552     0.600
51     0.57  0.606      0.552     0.599
120    0.57  0.605      0.552     0.593

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.652      0.046          0.657              0.695           0.038
10        0.607         0.654      0.048          0.657              0.693           0.036
49        0.607         0.654      0.047          0.657              0.695           0.039
51        0.607         0.654      0.047          0.657              0.696           0.039
120       0.607         0.649      0.043          0.657              0.695           0.039

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.544      0.475     0.557      0.013           0.026
GLTP          0.536  0.531      0.499     0.505      0.034           0.016
IP_trans      0.686  0.620      0.703     0.622     -0.008          -0.007
LBP_BPI_CETP  0.705  0.807      0.716     0.810      0.134           0.117
START         0.505  0.500      0.509     0.472      0.039           0.029
lipocalin     0.473  0.584      0.434     0.584      0.051           0.068
scp2          0.629  0.647      0.529     0.602      0.034           0.020

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.605          0.691       0.540      0.647
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.593          0.678       0.530      0.602
increment           0.043          0.054       0.034      0.034
increment_prot      0.039          0.043       0.035      0.020
```
