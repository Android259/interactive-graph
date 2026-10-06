# descriptors_no_extent_coarse_pool_gem

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_pool_gem'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4776      0.6918      0.5931      0.4793      0.5582      0.6710
groups_GLTP            5      0.5040      0.4400      0.5940      0.4566      0.5846      0.5385
groups_IP_trans        5      0.5652      0.6936      0.6187      0.4923      0.5917      0.6851
groups_LBP_BPI_CETP    5      0.8174      0.7957      0.6577      0.4474      0.8333      0.7702
groups_START           5      0.4123      0.5820      0.5918      0.5099      0.4469      0.6202
groups_lipocalin       5      0.6611      0.5583      0.6257      0.4979      0.6444      0.6000
groups_scp2            5      0.6235      0.5824      0.6465      0.4852      0.6588      0.6882
ALL                   35      0.5802      0.6206      0.6182      0.4812      0.6169      0.6533

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6351      0.6184     0.0923  35
max valid BA                0.6415      0.6346     0.0911  35
best valid F1               0.5899      0.5926     0.1065  35
test BA                     0.6004      0.5882     0.1127  35
test F1                     0.5166      0.5306     0.1472  35
test sensitivity            0.5802      0.5652     0.2223  35
test specificity            0.6206      0.6557     0.1894  35
test precision              0.5060      0.4735     0.1079  34
test loss                   0.6828      0.6876     0.0176  35
FPR (FP/(FP+TN))            0.3794      0.3443     0.1894  35
FNR (FN/(FN+TP))            0.4198      0.4348     0.2223  35

=== abs(sensitivity-specificity) gap: mean=0.2457 median=0.1796 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6146      0.6184     0.0478  5
  max valid BA                0.6170      0.6184     0.0441  5
  best valid F1               0.6388      0.6357     0.0635  5
  test BA                     0.5847      0.5823     0.0432  5
  test F1                     0.5371      0.5500     0.0897  5
  test sensitivity            0.4776      0.4925     0.1194  5
  test specificity            0.6918      0.6721     0.0536  5
  test precision              0.6262      0.6226     0.0378  5
  test loss                   0.6897      0.6905     0.0038  5
  FPR (FP/(FP+TN))            0.3082      0.3279     0.0536  5
  FNR (FN/(FN+TP))            0.5224      0.5075     0.1194  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5615      0.5385     0.0344  5
  max valid BA                0.5808      0.5385     0.0583  5
  best valid F1               0.5953      0.6667     0.1229  5
  test BA                     0.4720      0.4600     0.0657  5
  test F1                     0.4637      0.4255     0.1383  5
  test sensitivity            0.5040      0.4000     0.2851  5
  test specificity            0.4400      0.5200     0.1939  5
  test precision              0.4601      0.4444     0.0490  5
  test loss                   0.6977      0.6953     0.0059  5
  FPR (FP/(FP+TN))            0.5600      0.4800     0.1939  5
  FNR (FN/(FN+TP))            0.4960      0.6000     0.2851  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6384      0.6215     0.0681  5
  max valid BA                0.6446      0.6321     0.0692  5
  best valid F1               0.5585      0.5283     0.0569  5
  test BA                     0.6294      0.6443     0.0307  5
  test F1                     0.5124      0.5306     0.0541  5
  test sensitivity            0.5652      0.6087     0.1020  5
  test specificity            0.6936      0.6809     0.0512  5
  test precision              0.4736      0.4828     0.0219  5
  test loss                   0.6746      0.6736     0.0087  5
  FPR (FP/(FP+TN))            0.3064      0.3191     0.0512  5
  FNR (FN/(FN+TP))            0.4348      0.3913     0.1020  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8018      0.7988     0.0266  5
  max valid BA                0.8037      0.7988     0.0304  5
  best valid F1               0.7333      0.7213     0.0381  5
  test BA                     0.8066      0.8076     0.0265  5
  test F1                     0.7316      0.7391     0.0321  5
  test sensitivity            0.8174      0.8261     0.0778  5
  test specificity            0.7957      0.7872     0.0631  5
  test precision              0.6678      0.6667     0.0557  5
  test loss                   0.6553      0.6580     0.0246  5
  FPR (FP/(FP+TN))            0.2043      0.2128     0.0631  5
  FNR (FN/(FN+TP))            0.1826      0.1739     0.0778  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5335      0.5358     0.0259  5
  max valid BA                0.5412      0.5377     0.0320  5
  best valid F1               0.4946      0.4651     0.0950  5
  test BA                     0.4972      0.4963     0.0564  5
  test F1                     0.3608      0.4242     0.2114  5
  test sensitivity            0.4123      0.4308     0.3010  5
  test specificity            0.5820      0.5618     0.3407  5
  test precision              0.4391      0.4157     0.0958  4
  test loss                   0.6951      0.6901     0.0101  5
  FPR (FP/(FP+TN))            0.4180      0.4382     0.3407  5
  FNR (FN/(FN+TP))            0.5877      0.5692     0.3010  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6222      0.6389     0.0537  5
  max valid BA                0.6264      0.6458     0.0541  5
  best valid F1               0.5134      0.5432     0.1100  5
  test BA                     0.6097      0.6111     0.0576  5
  test F1                     0.5069      0.5385     0.0925  5
  test sensitivity            0.6611      0.6667     0.2393  5
  test specificity            0.5583      0.5417     0.1739  5
  test precision              0.4310      0.4268     0.0490  5
  test loss                   0.6810      0.6838     0.0147  5
  FPR (FP/(FP+TN))            0.4417      0.4583     0.1739  5
  FNR (FN/(FN+TP))            0.3389      0.3333     0.2393  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6735      0.6618     0.0554  5
  max valid BA                0.6765      0.6618     0.0540  5
  best valid F1               0.5955      0.5778     0.0524  5
  test BA                     0.6029      0.6324     0.0713  5
  test F1                     0.5039      0.5294     0.0860  5
  test sensitivity            0.6235      0.6471     0.1534  5
  test specificity            0.5824      0.5588     0.1048  5
  test precision              0.4305      0.4333     0.0776  5
  test loss                   0.6858      0.6852     0.0047  5
  FPR (FP/(FP+TN))            0.4176      0.4412     0.1048  5
  FNR (FN/(FN+TP))            0.3765      0.3529     0.1534  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.521         0.496         4         0.340              0.381
   CRAL-TRIO     1   129   67             0.799    0.623         0.581         4         0.551              0.568
   CRAL-TRIO     2   129   67             0.793    0.533         0.484         4         0.472              0.451
   CRAL-TRIO     3   129   67             0.806    0.670         0.598         4         0.469              0.466
   CRAL-TRIO     4   129   67             0.804    0.543         0.537         4         0.433              0.507
        GLTP     0    52   26             0.618    0.577         0.557         2         0.492              0.500
        GLTP     1    52   26             0.601    0.503         0.499         2         0.558              0.500
        GLTP     2    52   26             0.618    0.516         0.501         2         0.547              0.483
        GLTP     3    52   26             0.619    0.512         0.490         2         0.589              0.500
        GLTP     4    52   26             0.621    0.497         0.513         2         0.495              0.509
    IP_trans     0    71   24             0.809    0.694         0.683         3         0.761              0.748
    IP_trans     1    71   24             0.808    0.672         0.699         3         0.720              0.717
    IP_trans     2    71   24             0.810    0.584         0.559         3         0.739              0.784
    IP_trans     3    71   24             0.811    0.601         0.597         3         0.588              0.591
    IP_trans     4    71   24             0.808    0.547         0.571         3         0.623              0.677
LBP_BPI_CETP     0    71   24             0.809    0.796         0.774         2         0.719              0.701
LBP_BPI_CETP     1    71   24             0.816    0.868         0.837         2         0.601              0.675
LBP_BPI_CETP     2    71   24             0.808    0.845         0.833         2         0.623              0.625
LBP_BPI_CETP     3    71   24             0.807    0.775         0.753         2         0.812              0.814
LBP_BPI_CETP     4    71   24             0.804    0.816         0.819         2         0.769              0.764
       START     0   153   64             0.791    0.419         0.417         3         0.508              0.479
       START     1   153   64             0.784    0.492         0.490         3         0.454              0.439
       START     2   153   64             0.794    0.371         0.412         3         0.525              0.558
       START     3   153   64             0.797    0.575         0.565         3         0.596              0.608
       START     4   153   64             0.779    0.443         0.466         3         0.441              0.460
   lipocalin     0   108   36             0.847    0.462         0.384         5         0.605              0.655
   lipocalin     1   108   36             0.827    0.594         0.611         5         0.284              0.217
   lipocalin     2   108   36             0.829    0.654         0.602         5         0.585              0.548
   lipocalin     3   108   36             0.846    0.702         0.750         5         0.352              0.289
   lipocalin     4   108   36             0.810    0.551         0.584         5         0.541              0.463
        scp2     0    51   17             0.808    0.708         0.712         2         0.666              0.619
        scp2     1    51   17             0.837    0.667         0.717         3         0.693              0.626
        scp2     2    51   17             0.851    0.588         0.462         3         0.536              0.417
        scp2     3    51   17             0.842    0.663         0.587         3         0.668              0.576
        scp2     4    51   17             0.834    0.642         0.603         3         0.580              0.405

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.578         0.539       4.0         0.453              0.475
GLTP           52.0  26.0             0.615    0.521         0.512       2.0         0.536              0.499
IP_trans       71.0  24.0             0.809    0.619         0.622       3.0         0.686              0.703
LBP_BPI_CETP   71.0  24.0             0.809    0.820         0.803       2.0         0.705              0.716
START         153.0  64.0             0.789    0.460         0.470       3.0         0.505              0.509
lipocalin     108.0  36.0             0.832    0.593         0.586       5.0         0.473              0.434
scp2           51.0  17.0             0.834    0.653         0.616       2.8         0.629              0.529

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.606          0.698       0.538
null_AUC_k15      0.570          0.673       0.492

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.593          0.680       0.527
null_AUC_prot_k15      0.552          0.649       0.479

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.536      0.552     0.538
10     0.57  0.610      0.552     0.593
49     0.57  0.613      0.552     0.600
51     0.57  0.613      0.552     0.600
120    0.57  0.606      0.552     0.593

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.662      0.055          0.657              0.696           0.040
10        0.607         0.659      0.052          0.657              0.694           0.038
49        0.607         0.660      0.054          0.657              0.694           0.037
51        0.607         0.660      0.053          0.657              0.694           0.037
120       0.607         0.654      0.047          0.657              0.693           0.037

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.578      0.475     0.539      0.040           0.028
GLTP          0.536  0.521      0.499     0.512      0.025           0.019
IP_trans      0.686  0.619      0.703     0.622     -0.011          -0.000
LBP_BPI_CETP  0.705  0.820      0.716     0.803      0.125           0.100
START         0.505  0.460      0.509     0.470      0.041           0.018
lipocalin     0.473  0.593      0.434     0.586      0.078           0.078
scp2          0.629  0.653      0.529     0.616      0.030           0.015

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.606          0.698       0.538      0.653
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.593          0.680       0.527      0.616
increment           0.047          0.048       0.046      0.030
increment_prot      0.037          0.038       0.036      0.015
```
