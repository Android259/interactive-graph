# descriptors_no_extent_coarse_add_lipprop

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_add_lipprop'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5642      0.5705      0.6046      0.4816      0.6179      0.5452
groups_GLTP            5      0.4320      0.4960      0.5534      0.5398      0.4538      0.6231
groups_IP_trans        5      0.4957      0.6596      0.6138      0.4601      0.5833      0.6936
groups_LBP_BPI_CETP    5      0.8261      0.8255      0.6201      0.4670      0.7833      0.7574
groups_START           5      0.3815      0.5865      0.5270      0.5232      0.4250      0.6112
groups_lipocalin       5      0.6222      0.6167      0.6281      0.4887      0.6278      0.6583
groups_scp2            5      0.6588      0.5059      0.6305      0.4699      0.7294      0.6000
ALL                   35      0.5686      0.6087      0.5968      0.4900      0.6029      0.6413

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6213      0.5957     0.0941  35
max valid BA                0.6439      0.6346     0.0968  35
best valid F1               0.5917      0.5931     0.1148  35
test BA                     0.5887      0.5833     0.1183  35
test F1                     0.5133      0.4762     0.1347  35
test sensitivity            0.5686      0.5385     0.2038  35
test specificity            0.6087      0.6170     0.1794  35
test precision              0.4977      0.4706     0.1245  35
test loss                   0.6857      0.6875     0.0136  35
FPR (FP/(FP+TN))            0.3913      0.3830     0.1794  35
FNR (FN/(FN+TP))            0.4314      0.4615     0.2038  35

=== abs(sensitivity-specificity) gap: mean=0.2325 median=0.2400 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5815      0.5691     0.0315  5
  max valid BA                0.5980      0.5719     0.0447  5
  best valid F1               0.6391      0.6667     0.0794  5
  test BA                     0.5673      0.5861     0.0549  5
  test F1                     0.5666      0.5954     0.1138  5
  test sensitivity            0.5642      0.5821     0.1700  5
  test specificity            0.5705      0.5902     0.1179  5
  test precision              0.5861      0.6049     0.0640  5
  test loss                   0.6882      0.6897     0.0107  5
  FPR (FP/(FP+TN))            0.4295      0.4098     0.1179  5
  FNR (FN/(FN+TP))            0.4358      0.4179     0.1700  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5385      0.5385     0.0192  5
  max valid BA                0.5846      0.5769     0.0399  5
  best valid F1               0.6044      0.6129     0.0988  5
  test BA                     0.4640      0.4800     0.0385  5
  test F1                     0.4446      0.4444     0.0246  5
  test sensitivity            0.4320      0.4000     0.0657  5
  test specificity            0.4960      0.5600     0.1374  5
  test precision              0.4662      0.4737     0.0296  5
  test loss                   0.6979      0.6956     0.0075  5
  FPR (FP/(FP+TN))            0.5040      0.4400     0.1374  5
  FNR (FN/(FN+TP))            0.5680      0.6000     0.0657  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6385      0.6215     0.0780  5
  max valid BA                0.6614      0.6853     0.0783  5
  best valid F1               0.5745      0.5846     0.0702  5
  test BA                     0.5776      0.5800     0.0404  5
  test F1                     0.4439      0.4651     0.0826  5
  test sensitivity            0.4957      0.5217     0.1556  5
  test specificity            0.6596      0.6383     0.1213  5
  test precision              0.4178      0.4138     0.0558  5
  test loss                   0.6806      0.6824     0.0132  5
  FPR (FP/(FP+TN))            0.3404      0.3617     0.1213  5
  FNR (FN/(FN+TP))            0.5043      0.4783     0.1556  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7662      0.7584     0.0364  5
  max valid BA                0.8017      0.8103     0.0469  5
  best valid F1               0.7315      0.7407     0.0560  5
  test BA                     0.8258      0.8386     0.0391  5
  test F1                     0.7581      0.7755     0.0492  5
  test sensitivity            0.8261      0.8696     0.1020  5
  test specificity            0.8255      0.8511     0.0980  5
  test precision              0.7143      0.7308     0.0873  5
  test loss                   0.6681      0.6673     0.0130  5
  FPR (FP/(FP+TN))            0.1745      0.1489     0.0980  5
  FNR (FN/(FN+TP))            0.1739      0.1304     0.1020  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5181      0.5241     0.0340  5
  max valid BA                0.5394      0.5241     0.0586  5
  best valid F1               0.4625      0.4655     0.1066  5
  test BA                     0.4840      0.4814     0.0491  5
  test F1                     0.3807      0.4262     0.0963  5
  test sensitivity            0.3815      0.4000     0.1399  5
  test specificity            0.5865      0.6517     0.1774  5
  test precision              0.4052      0.3977     0.0546  5
  test loss                   0.6941      0.6908     0.0083  5
  FPR (FP/(FP+TN))            0.4135      0.3483     0.1774  5
  FNR (FN/(FN+TP))            0.6185      0.6000     0.1399  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6417      0.6528     0.0667  5
  max valid BA                0.6431      0.6597     0.0671  5
  best valid F1               0.5289      0.5766     0.1279  5
  test BA                     0.6194      0.6042     0.0409  5
  test F1                     0.5076      0.5143     0.0782  5
  test sensitivity            0.6222      0.6667     0.2227  5
  test specificity            0.6167      0.6111     0.2005  5
  test precision              0.4827      0.4493     0.1092  5
  test loss                   0.6805      0.6826     0.0134  5
  FPR (FP/(FP+TN))            0.3833      0.3889     0.2005  5
  FNR (FN/(FN+TP))            0.3778      0.3333     0.2227  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6647      0.6324     0.0866  5
  max valid BA                0.6794      0.6618     0.0774  5
  best valid F1               0.6011      0.5714     0.0800  5
  test BA                     0.5824      0.6029     0.0436  5
  test F1                     0.4918      0.5000     0.0547  5
  test sensitivity            0.6588      0.5882     0.2137  5
  test specificity            0.5059      0.5882     0.2263  5
  test precision              0.4119      0.3902     0.0574  5
  test loss                   0.6903      0.6929     0.0064  5
  FPR (FP/(FP+TN))            0.4941      0.4118     0.2263  5
  FNR (FN/(FN+TP))            0.3412      0.4118     0.2137  5
```

## AUC vs chemistry null model, in-sample increment

### similarity = tanimoto (full molecular structure)

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.565         0.551         4         0.340              0.381
   CRAL-TRIO     1   129   67             0.799    0.572         0.542         4         0.551              0.568
   CRAL-TRIO     2   129   67             0.793    0.551         0.525         4         0.472              0.451
   CRAL-TRIO     3   129   67             0.806    0.677         0.530         4         0.469              0.466
   CRAL-TRIO     4   129   67             0.804    0.561         0.508         4         0.433              0.507
        GLTP     0    52   26             0.618    0.518         0.522         2         0.492              0.500
        GLTP     1    52   26             0.601    0.512         0.494         2         0.558              0.500
        GLTP     2    52   26             0.618    0.507         0.485         2         0.547              0.483
        GLTP     3    52   26             0.619    0.525         0.500         2         0.589              0.500
        GLTP     4    52   26             0.621    0.556         0.524         2         0.495              0.509
    IP_trans     0    71   24             0.809    0.723         0.720         3         0.761              0.748
    IP_trans     1    71   24             0.808    0.727         0.752         3         0.720              0.717
    IP_trans     2    71   24             0.810    0.570         0.557         3         0.739              0.784
    IP_trans     3    71   24             0.811    0.570         0.567         3         0.588              0.591
    IP_trans     4    71   24             0.808    0.507         0.507         3         0.623              0.677
LBP_BPI_CETP     0    71   24             0.809    0.771         0.758         2         0.719              0.701
LBP_BPI_CETP     1    71   24             0.816    0.863         0.843         2         0.601              0.675
LBP_BPI_CETP     2    71   24             0.808    0.853         0.853         2         0.623              0.625
LBP_BPI_CETP     3    71   24             0.807    0.770         0.751         2         0.812              0.814
LBP_BPI_CETP     4    71   24             0.804    0.689         0.702         2         0.769              0.764
       START     0   153   64             0.791    0.409         0.439         3         0.508              0.479
       START     1   153   64             0.784    0.485         0.474         3         0.454              0.439
       START     2   153   64             0.794    0.369         0.416         3         0.525              0.558
       START     3   153   64             0.797    0.571         0.552         3         0.596              0.608
       START     4   153   64             0.779    0.440         0.487         3         0.441              0.460
   lipocalin     0   108   36             0.847    0.281         0.232         5         0.605              0.655
   lipocalin     1   108   36             0.827    0.537         0.486         5         0.284              0.217
   lipocalin     2   108   36             0.829    0.750         0.784         5         0.585              0.548
   lipocalin     3   108   36             0.846    0.680         0.723         5         0.352              0.289
   lipocalin     4   108   36             0.810    0.630         0.681         5         0.541              0.463
        scp2     0    51   17             0.808    0.792         0.788         2         0.666              0.619
        scp2     1    51   17             0.837    0.641         0.612         3         0.693              0.626
        scp2     2    51   17             0.851    0.625         0.511         3         0.536              0.417
        scp2     3    51   17             0.842    0.657         0.597         3         0.668              0.576
        scp2     4    51   17             0.834    0.623         0.692         3         0.580              0.405

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.585         0.531       4.0         0.453              0.475
GLTP           52.0  26.0             0.615    0.524         0.505       2.0         0.536              0.499
IP_trans       71.0  24.0             0.809    0.619         0.621       3.0         0.686              0.703
LBP_BPI_CETP   71.0  24.0             0.809    0.789         0.781       2.0         0.705              0.716
START         153.0  64.0             0.789    0.455         0.474       3.0         0.505              0.509
lipocalin     108.0  36.0             0.832    0.576         0.581       5.0         0.473              0.434
scp2           51.0  17.0             0.834    0.668         0.640       2.8         0.629              0.529

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.602          0.692       0.535
null_AUC_k15      0.570          0.673       0.492

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.590          0.681       0.523
null_AUC_prot_k15      0.552          0.649       0.479

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.530      0.552     0.538
10     0.57  0.578      0.552     0.582
49     0.57  0.608      0.552     0.603
51     0.57  0.607      0.552     0.600
120    0.57  0.602      0.552     0.590

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.672      0.066          0.657              0.702           0.046
10        0.607         0.660      0.054          0.657              0.692           0.036
49        0.607         0.659      0.052          0.657              0.699           0.043
51        0.607         0.660      0.053          0.657              0.696           0.040
120       0.607         0.667      0.061          0.657              0.702           0.045

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.585      0.475     0.531      0.036           0.028
GLTP          0.536  0.524      0.499     0.505      0.012           0.012
IP_trans      0.686  0.619      0.703     0.621      0.006           0.008
LBP_BPI_CETP  0.705  0.789      0.716     0.781      0.117           0.087
START         0.505  0.455      0.509     0.474      0.047           0.030
lipocalin     0.473  0.576      0.434     0.581      0.139           0.111
scp2          0.629  0.668      0.529     0.640      0.067           0.042

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.602          0.692       0.535      0.668
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.590          0.681       0.523      0.640
increment           0.061          0.063       0.059      0.067
increment_prot      0.045          0.045       0.045      0.042

wrote : /tmp/tmp.ULIuHrRec7
```

### similarity = descriptors (chain/unsaturation/hbond/heavy only)

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.622    0.565         0.551         4         0.492              0.372
   CRAL-TRIO     1   129   67             0.632    0.572         0.542         4         0.482              0.363
   CRAL-TRIO     2   129   67             0.624    0.551         0.525         4         0.450              0.308
   CRAL-TRIO     3   129   67             0.651    0.677         0.530         4         0.555              0.390
   CRAL-TRIO     4   129   67             0.620    0.561         0.508         4         0.434              0.394
        GLTP     0    52   26             0.591    0.518         0.522         2         0.505              0.493
        GLTP     1    52   26             0.575    0.512         0.494         2         0.487              0.515
        GLTP     2    52   26             0.620    0.507         0.485         2         0.461              0.456
        GLTP     3    52   26             0.606    0.525         0.500         2         0.500              0.443
        GLTP     4    52   26             0.634    0.556         0.524         2         0.653              0.649
    IP_trans     0    71   24             0.758    0.723         0.720         3         0.708              0.686
    IP_trans     1    71   24             0.726    0.727         0.752         3         0.697              0.706
    IP_trans     2    71   24             0.698    0.570         0.557         3         0.773              0.765
    IP_trans     3    71   24             0.717    0.570         0.567         3         0.668              0.678
    IP_trans     4    71   24             0.711    0.507         0.507         3         0.556              0.547
LBP_BPI_CETP     0    71   24             0.719    0.771         0.758         2         0.809              0.801
LBP_BPI_CETP     1    71   24             0.730    0.863         0.843         2         0.848              0.861
LBP_BPI_CETP     2    71   24             0.714    0.853         0.853         2         0.776              0.774
LBP_BPI_CETP     3    71   24             0.706    0.770         0.751         2         0.749              0.745
LBP_BPI_CETP     4    71   24             0.729    0.689         0.702         2         0.811              0.810
       START     0   153   64             0.575    0.409         0.439         3         0.499              0.471
       START     1   153   64             0.583    0.485         0.474         3         0.471              0.472
       START     2   153   64             0.565    0.369         0.416         3         0.491              0.442
       START     3   153   64             0.607    0.571         0.552         3         0.609              0.542
       START     4   153   64             0.552    0.440         0.487         3         0.468              0.447
   lipocalin     0   108   36             0.540    0.281         0.232         5         0.238              0.166
   lipocalin     1   108   36             0.548    0.537         0.486         5         0.307              0.276
   lipocalin     2   108   36             0.586    0.750         0.784         5         0.361              0.225
   lipocalin     3   108   36             0.582    0.680         0.723         5         0.324              0.233
   lipocalin     4   108   36             0.568    0.630         0.681         5         0.441              0.361
        scp2     0    51   17             0.631    0.792         0.788         2         0.420              0.510
        scp2     1    51   17             0.658    0.641         0.612         3         0.408              0.472
        scp2     2    51   17             0.607    0.625         0.511         3         0.460              0.602
        scp2     3    51   17             0.669    0.657         0.597         3         0.522              0.658
        scp2     4    51   17             0.690    0.623         0.692         3         0.626              0.717

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.630    0.585         0.531       4.0         0.483              0.365
GLTP           52.0  26.0             0.605    0.524         0.505       2.0         0.521              0.511
IP_trans       71.0  24.0             0.722    0.619         0.621       3.0         0.681              0.677
LBP_BPI_CETP   71.0  24.0             0.719    0.789         0.781       2.0         0.798              0.798
START         153.0  64.0             0.576    0.455         0.474       3.0         0.508              0.475
lipocalin     108.0  36.0             0.565    0.576         0.581       5.0         0.334              0.252
scp2           51.0  17.0             0.651    0.668         0.640       2.8         0.488              0.592

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.602          0.692       0.535
null_AUC_k15      0.545          0.656       0.461

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.590          0.681       0.523
null_AUC_prot_k15      0.524          0.689       0.401

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.530      0.524     0.538
10     0.545  0.578      0.524     0.582
49     0.545  0.608      0.524     0.603
51     0.545  0.607      0.524     0.600
120    0.545  0.602      0.524     0.590

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.619         0.666      0.047          0.655              0.697           0.042
10        0.619         0.670      0.051          0.655              0.698           0.043
49        0.619         0.673      0.054          0.655              0.699           0.044
51        0.619         0.674      0.055          0.655              0.700           0.045
120       0.619         0.670      0.050          0.655              0.698           0.044

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.483  0.585      0.365     0.531      0.055           0.039
GLTP          0.521  0.524      0.511     0.505      0.032           0.035
IP_trans      0.681  0.619      0.677     0.621      0.022           0.021
LBP_BPI_CETP  0.798  0.789      0.798     0.781      0.029           0.026
START         0.508  0.455      0.475     0.474      0.048           0.026
lipocalin     0.334  0.576      0.252     0.581      0.086           0.100
scp2          0.488  0.668      0.592     0.640      0.082           0.058

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.545          0.656       0.461      0.488
net                 0.602          0.692       0.535      0.668
chem_prot           0.524          0.689       0.401      0.592
net_prot            0.590          0.681       0.523      0.640
increment           0.050          0.044       0.055      0.082
increment_prot      0.044          0.035       0.050      0.058
```
