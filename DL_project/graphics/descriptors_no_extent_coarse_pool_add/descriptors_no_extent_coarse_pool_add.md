# descriptors_no_extent_coarse_pool_add

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_pool_add'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5313      0.5672      0.6223      0.4715      0.5791      0.6129
groups_GLTP            5      0.5120      0.4320      0.6567      0.4312      0.5615      0.5462
groups_IP_trans        5      0.5826      0.6979      0.6006      0.4824      0.5917      0.6766
groups_LBP_BPI_CETP    5      0.7826      0.8255      0.6649      0.4704      0.8250      0.7957
groups_START           5      0.4000      0.6090      0.5345      0.5481      0.4437      0.6112
groups_lipocalin       5      0.6389      0.5861      0.6618      0.4927      0.6333      0.6083
groups_scp2            5      0.7529      0.3765      0.7006      0.4230      0.7882      0.4647
ALL                   35      0.6001      0.5849      0.6345      0.4742      0.6318      0.6165

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6242      0.5962     0.0993  35
max valid BA                0.6367      0.6215     0.1018  35
best valid F1               0.5906      0.5812     0.1096  35
test BA                     0.5925      0.5735     0.1135  35
test F1                     0.5253      0.5306     0.1284  35
test sensitivity            0.6001      0.5821     0.1998  35
test specificity            0.5849      0.6170     0.1952  35
test precision              0.4957      0.4828     0.1150  35
test loss                   0.6790      0.6835     0.0300  35
FPR (FP/(FP+TN))            0.4151      0.3830     0.1952  35
FNR (FN/(FN+TP))            0.3999      0.4179     0.1998  35

=== abs(sensitivity-specificity) gap: mean=0.2375 median=0.1776 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5960      0.5784     0.0362  5
  max valid BA                0.6155      0.5912     0.0372  5
  best valid F1               0.6566      0.6497     0.0433  5
  test BA                     0.5493      0.5533     0.0430  5
  test F1                     0.5454      0.5778     0.0919  5
  test sensitivity            0.5313      0.5821     0.1273  5
  test specificity            0.5672      0.5246     0.0757  5
  test precision              0.5699      0.5735     0.0442  5
  test loss                   0.6870      0.6855     0.0126  5
  FPR (FP/(FP+TN))            0.4328      0.4754     0.0757  5
  FNR (FN/(FN+TP))            0.4687      0.4179     0.1273  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5538      0.5577     0.0370  5
  max valid BA                0.5577      0.5577     0.0408  5
  best valid F1               0.5625      0.5517     0.0800  5
  test BA                     0.4720      0.4800     0.0335  5
  test F1                     0.4862      0.4727     0.0703  5
  test sensitivity            0.5120      0.5200     0.1339  5
  test specificity            0.4320      0.4800     0.1246  5
  test precision              0.4723      0.4783     0.0299  5
  test loss                   0.7150      0.7055     0.0200  5
  FPR (FP/(FP+TN))            0.5680      0.5200     0.1246  5
  FNR (FN/(FN+TP))            0.4880      0.4800     0.1339  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6341      0.6215     0.0749  5
  max valid BA                0.6616      0.6636     0.0637  5
  best valid F1               0.5697      0.5714     0.0696  5
  test BA                     0.6402      0.6443     0.0192  5
  test F1                     0.5303      0.5306     0.0169  5
  test sensitivity            0.5826      0.5652     0.0238  5
  test specificity            0.6979      0.7021     0.0551  5
  test precision              0.4887      0.4828     0.0376  5
  test loss                   0.6641      0.6695     0.0124  5
  FPR (FP/(FP+TN))            0.3021      0.2979     0.0551  5
  FNR (FN/(FN+TP))            0.4174      0.4348     0.0238  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8104      0.8112     0.0274  5
  max valid BA                0.8230      0.8320     0.0223  5
  best valid F1               0.7594      0.7755     0.0340  5
  test BA                     0.8041      0.7858     0.0541  5
  test F1                     0.7293      0.7018     0.0643  5
  test sensitivity            0.7826      0.8696     0.1409  5
  test specificity            0.8255      0.8298     0.0843  5
  test precision              0.7009      0.7000     0.0890  5
  test loss                   0.6260      0.6211     0.0129  5
  FPR (FP/(FP+TN))            0.1745      0.1702     0.0843  5
  FNR (FN/(FN+TP))            0.2174      0.1304     0.1409  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5275      0.5288     0.0626  5
  max valid BA                0.5317      0.5341     0.0605  5
  best valid F1               0.5012      0.5029     0.0581  5
  test BA                     0.5045      0.5099     0.0570  5
  test F1                     0.3875      0.4144     0.1553  5
  test sensitivity            0.4000      0.4462     0.2041  5
  test specificity            0.6090      0.6180     0.2143  5
  test precision              0.4211      0.4301     0.0779  5
  test loss                   0.6937      0.6881     0.0122  5
  FPR (FP/(FP+TN))            0.3910      0.3820     0.2143  5
  FNR (FN/(FN+TP))            0.6000      0.5538     0.2041  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6208      0.6319     0.0582  5
  max valid BA                0.6292      0.6389     0.0582  5
  best valid F1               0.5090      0.5510     0.1367  5
  test BA                     0.6125      0.6111     0.0480  5
  test F1                     0.5050      0.5385     0.0899  5
  test sensitivity            0.6389      0.6667     0.2240  5
  test specificity            0.5861      0.5833     0.1711  5
  test precision              0.4415      0.4267     0.0444  5
  test loss                   0.6710      0.6767     0.0142  5
  FPR (FP/(FP+TN))            0.4139      0.4167     0.1711  5
  FNR (FN/(FN+TP))            0.3611      0.3333     0.2240  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6265      0.6176     0.0717  5
  max valid BA                0.6382      0.6324     0.0836  5
  best valid F1               0.5759      0.5660     0.0670  5
  test BA                     0.5647      0.5735     0.0855  5
  test F1                     0.4933      0.5185     0.1003  5
  test sensitivity            0.7529      0.8235     0.2331  5
  test specificity            0.3765      0.3824     0.2105  5
  test precision              0.3758      0.3784     0.0577  5
  test loss                   0.6959      0.6904     0.0144  5
  FPR (FP/(FP+TN))            0.6235      0.6176     0.2105  5
  FNR (FN/(FN+TP))            0.2471      0.1765     0.2331  5
```

## AUC vs chemistry null model, in-sample increment

### similarity = tanimoto (full molecular structure)

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.560         0.573         4         0.340              0.381
   CRAL-TRIO     1   129   67             0.799    0.562         0.508         4         0.551              0.568
   CRAL-TRIO     2   129   67             0.793    0.532         0.476         4         0.472              0.451
   CRAL-TRIO     3   129   67             0.806    0.625         0.476         4         0.469              0.466
   CRAL-TRIO     4   129   67             0.804    0.537         0.488         4         0.433              0.507
        GLTP     0    52   26             0.618    0.549         0.553         2         0.492              0.500
        GLTP     1    52   26             0.601    0.538         0.507         2         0.558              0.500
        GLTP     2    52   26             0.618    0.506         0.485         2         0.547              0.483
        GLTP     3    52   26             0.619    0.538         0.500         2         0.589              0.500
        GLTP     4    52   26             0.621    0.537         0.506         2         0.495              0.509
    IP_trans     0    71   24             0.809    0.676         0.662         3         0.761              0.748
    IP_trans     1    71   24             0.808    0.687         0.713         3         0.720              0.717
    IP_trans     2    71   24             0.810    0.658         0.663         3         0.739              0.784
    IP_trans     3    71   24             0.811    0.637         0.594         3         0.588              0.591
    IP_trans     4    71   24             0.808    0.525         0.522         3         0.623              0.677
LBP_BPI_CETP     0    71   24             0.809    0.795         0.771         2         0.719              0.701
LBP_BPI_CETP     1    71   24             0.816    0.851         0.836         2         0.601              0.675
LBP_BPI_CETP     2    71   24             0.808    0.801         0.787         2         0.623              0.625
LBP_BPI_CETP     3    71   24             0.807    0.772         0.760         2         0.812              0.814
LBP_BPI_CETP     4    71   24             0.804    0.818         0.829         2         0.769              0.764
       START     0   153   64             0.791    0.432         0.438         3         0.508              0.479
       START     1   153   64             0.784    0.488         0.475         3         0.454              0.439
       START     2   153   64             0.794    0.368         0.414         3         0.525              0.558
       START     3   153   64             0.797    0.574         0.561         3         0.596              0.608
       START     4   153   64             0.779    0.426         0.447         3         0.441              0.460
   lipocalin     0   108   36             0.847    0.274         0.213         5         0.605              0.655
   lipocalin     1   108   36             0.827    0.489         0.445         5         0.284              0.217
   lipocalin     2   108   36             0.829    0.606         0.569         5         0.585              0.548
   lipocalin     3   108   36             0.846    0.633         0.645         5         0.352              0.289
   lipocalin     4   108   36             0.810    0.584         0.553         5         0.541              0.463
        scp2     0    51   17             0.808    0.699         0.744         2         0.666              0.619
        scp2     1    51   17             0.837    0.582         0.499         3         0.693              0.626
        scp2     2    51   17             0.851    0.597         0.469         3         0.536              0.417
        scp2     3    51   17             0.842    0.500         0.375         3         0.668              0.576
        scp2     4    51   17             0.834    0.645         0.696         3         0.580              0.405

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.563         0.504       4.0         0.453              0.475
GLTP           52.0  26.0             0.615    0.534         0.510       2.0         0.536              0.499
IP_trans       71.0  24.0             0.809    0.637         0.631       3.0         0.686              0.703
LBP_BPI_CETP   71.0  24.0             0.809    0.807         0.796       2.0         0.705              0.716
START         153.0  64.0             0.789    0.457         0.467       3.0         0.505              0.509
lipocalin     108.0  36.0             0.832    0.517         0.485       5.0         0.473              0.434
scp2           51.0  17.0             0.834    0.605         0.556       2.8         0.629              0.529

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.589          0.683       0.518
null_AUC_k15      0.570          0.673       0.492

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.564          0.661       0.492
null_AUC_prot_k15      0.552          0.649       0.479

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.543      0.552     0.548
10     0.57  0.596      0.552     0.582
49     0.57  0.602      0.552     0.580
51     0.57  0.601      0.552     0.579
120    0.57  0.589      0.552     0.564

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.669      0.062          0.657              0.703           0.046
10        0.607         0.659      0.052          0.657              0.695           0.038
49        0.607         0.661      0.054          0.657              0.698           0.041
51        0.607         0.661      0.054          0.657              0.698           0.041
120       0.607         0.655      0.048          0.657              0.692           0.035

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.563      0.475     0.504      0.025           0.018
GLTP          0.536  0.534      0.499     0.510      0.017           0.010
IP_trans      0.686  0.637      0.703     0.631     -0.004           0.002
LBP_BPI_CETP  0.705  0.807      0.716     0.796      0.112           0.087
START         0.505  0.457      0.509     0.467      0.045           0.020
lipocalin     0.473  0.517      0.434     0.485      0.100           0.082
scp2          0.629  0.605      0.529     0.556      0.040           0.025

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.589          0.683       0.518      0.605
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.564          0.661       0.492      0.556
increment           0.048          0.049       0.047      0.040
increment_prot      0.035          0.038       0.033      0.025

wrote : /tmp/tmp.jXYaXJyLam
```

### similarity = descriptors (chain/unsaturation/hbond/heavy only)

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.622    0.560         0.573         4         0.492              0.372
   CRAL-TRIO     1   129   67             0.632    0.562         0.508         4         0.482              0.363
   CRAL-TRIO     2   129   67             0.624    0.532         0.476         4         0.450              0.308
   CRAL-TRIO     3   129   67             0.651    0.625         0.476         4         0.555              0.390
   CRAL-TRIO     4   129   67             0.620    0.537         0.488         4         0.434              0.394
        GLTP     0    52   26             0.591    0.549         0.553         2         0.505              0.493
        GLTP     1    52   26             0.575    0.538         0.507         2         0.487              0.515
        GLTP     2    52   26             0.620    0.506         0.485         2         0.461              0.456
        GLTP     3    52   26             0.606    0.538         0.500         2         0.500              0.443
        GLTP     4    52   26             0.634    0.537         0.506         2         0.653              0.649
    IP_trans     0    71   24             0.758    0.676         0.662         3         0.708              0.686
    IP_trans     1    71   24             0.726    0.687         0.713         3         0.697              0.706
    IP_trans     2    71   24             0.698    0.658         0.663         3         0.773              0.765
    IP_trans     3    71   24             0.717    0.637         0.594         3         0.668              0.678
    IP_trans     4    71   24             0.711    0.525         0.522         3         0.556              0.547
LBP_BPI_CETP     0    71   24             0.719    0.795         0.771         2         0.809              0.801
LBP_BPI_CETP     1    71   24             0.730    0.851         0.836         2         0.848              0.861
LBP_BPI_CETP     2    71   24             0.714    0.801         0.787         2         0.776              0.774
LBP_BPI_CETP     3    71   24             0.706    0.772         0.760         2         0.749              0.745
LBP_BPI_CETP     4    71   24             0.729    0.818         0.829         2         0.811              0.810
       START     0   153   64             0.575    0.432         0.438         3         0.499              0.471
       START     1   153   64             0.583    0.488         0.475         3         0.471              0.472
       START     2   153   64             0.565    0.368         0.414         3         0.491              0.442
       START     3   153   64             0.607    0.574         0.561         3         0.609              0.542
       START     4   153   64             0.552    0.426         0.447         3         0.468              0.447
   lipocalin     0   108   36             0.540    0.274         0.213         5         0.238              0.166
   lipocalin     1   108   36             0.548    0.489         0.445         5         0.307              0.276
   lipocalin     2   108   36             0.586    0.606         0.569         5         0.361              0.225
   lipocalin     3   108   36             0.582    0.633         0.645         5         0.324              0.233
   lipocalin     4   108   36             0.568    0.584         0.553         5         0.441              0.361
        scp2     0    51   17             0.631    0.699         0.744         2         0.420              0.510
        scp2     1    51   17             0.658    0.582         0.499         3         0.408              0.472
        scp2     2    51   17             0.607    0.597         0.469         3         0.460              0.602
        scp2     3    51   17             0.669    0.500         0.375         3         0.522              0.658
        scp2     4    51   17             0.690    0.645         0.696         3         0.626              0.717

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.630    0.563         0.504       4.0         0.483              0.365
GLTP           52.0  26.0             0.605    0.534         0.510       2.0         0.521              0.511
IP_trans       71.0  24.0             0.722    0.637         0.631       3.0         0.681              0.677
LBP_BPI_CETP   71.0  24.0             0.719    0.807         0.796       2.0         0.798              0.798
START         153.0  64.0             0.576    0.457         0.467       3.0         0.508              0.475
lipocalin     108.0  36.0             0.565    0.517         0.485       5.0         0.334              0.252
scp2           51.0  17.0             0.651    0.605         0.556       2.8         0.488              0.592

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.589          0.683       0.518
null_AUC_k15      0.545          0.656       0.461

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.564          0.661       0.492
null_AUC_prot_k15      0.524          0.689       0.401

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.543      0.524     0.548
10     0.545  0.596      0.524     0.582
49     0.545  0.602      0.524     0.580
51     0.545  0.601      0.524     0.579
120    0.545  0.589      0.524     0.564

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.619         0.670      0.051          0.655              0.701           0.046
10        0.619         0.657      0.038          0.655              0.693           0.038
49        0.619         0.664      0.045          0.655              0.695           0.040
51        0.619         0.664      0.045          0.655              0.696           0.041
120       0.619         0.660      0.041          0.655              0.688           0.033

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.483  0.563      0.365     0.504      0.052           0.033
GLTP          0.521  0.534      0.511     0.510      0.041           0.036
IP_trans      0.681  0.637      0.677     0.631     -0.003           0.004
LBP_BPI_CETP  0.798  0.807      0.798     0.796      0.016           0.022
START         0.508  0.457      0.475     0.467      0.048           0.021
lipocalin     0.334  0.517      0.252     0.485      0.081           0.086
scp2          0.488  0.605      0.592     0.556      0.053           0.030

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.545          0.656       0.461      0.488
net                 0.589          0.683       0.518      0.605
chem_prot           0.524          0.689       0.401      0.592
net_prot            0.564          0.661       0.492      0.556
increment           0.041          0.022       0.055      0.053
increment_prot      0.033          0.019       0.044      0.030
```
