# descriptors_2paths_extent

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_2paths_extent'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6746      0.4000      0.5423      0.5409      0.7104      0.4516
groups_GLTP            5      0.3040      0.6640      0.6245      0.5201      0.3231      0.7692
groups_IP_trans        5      0.4696      0.6851      0.6083      0.5292      0.5167      0.7106
groups_LBP_BPI_CETP    5      0.7913      0.5660      0.6469      0.5753      0.8167      0.5915
groups_START           5      0.7323      0.3618      0.6109      0.4314      0.7281      0.4000
groups_lipocalin       5      0.7167      0.4639      0.6667      0.3927      0.7111      0.4722
groups_scp2            5      0.6941      0.2588      0.5609      0.4613      0.7765      0.3412
ALL                   35      0.6261      0.4857      0.6086      0.4930      0.6547      0.5338

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5942      0.5754     0.0859  35
max valid BA                0.6243      0.6066     0.0910  35
best valid F1               0.6142      0.6145     0.0887  35
test BA                     0.5559      0.5432     0.0936  35
test F1                     0.4931      0.4918     0.1338  35
test sensitivity            0.6261      0.6471     0.2568  35
test specificity            0.4857      0.4412     0.2620  35
test precision              0.4581      0.4412     0.1144  35
test loss                   0.7282      0.6955     0.1473  35
FPR (FP/(FP+TN))            0.5143      0.5588     0.2620  35
FNR (FN/(FN+TP))            0.3739      0.3529     0.2568  35

=== abs(sensitivity-specificity) gap: mean=0.4201 median=0.4197 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5810      0.5731     0.0401  5
  max valid BA                0.6111      0.6195     0.0256  5
  best valid F1               0.6962      0.7052     0.0394  5
  test BA                     0.5373      0.5514     0.0776  5
  test F1                     0.5918      0.6000     0.1134  5
  test sensitivity            0.6746      0.5821     0.2627  5
  test specificity            0.4000      0.3770     0.2708  5
  test precision              0.5606      0.5517     0.0842  5
  test loss                   0.8181      0.6896     0.2861  5
  FPR (FP/(FP+TN))            0.6000      0.6230     0.2708  5
  FNR (FN/(FN+TP))            0.3254      0.4179     0.2627  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5462      0.5192     0.0463  5
  max valid BA                0.5923      0.5962     0.0672  5
  best valid F1               0.6686      0.6667     0.0164  5
  test BA                     0.4840      0.4800     0.0654  5
  test F1                     0.3561      0.3500     0.1351  5
  test sensitivity            0.3040      0.2800     0.1590  5
  test specificity            0.6640      0.6800     0.1565  5
  test precision              0.4757      0.4815     0.1412  5
  test loss                   0.7322      0.7470     0.0377  5
  FPR (FP/(FP+TN))            0.3360      0.3200     0.1565  5
  FNR (FN/(FN+TP))            0.6960      0.7200     0.1590  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6137      0.6507     0.0715  5
  max valid BA                0.6627      0.6733     0.0489  5
  best valid F1               0.5788      0.5862     0.0509  5
  test BA                     0.5773      0.5689     0.0468  5
  test F1                     0.4228      0.4490     0.1244  5
  test sensitivity            0.4696      0.4783     0.2049  5
  test specificity            0.6851      0.6809     0.1888  5
  test precision              0.4575      0.4231     0.0947  5
  test loss                   0.6663      0.6709     0.0191  5
  FPR (FP/(FP+TN))            0.3149      0.3191     0.1888  5
  FNR (FN/(FN+TP))            0.5304      0.5217     0.2049  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7041      0.7269     0.1124  5
  max valid BA                0.7418      0.7979     0.1271  5
  best valid F1               0.6823      0.7164     0.1009  5
  test BA                     0.6786      0.6536     0.1396  5
  test F1                     0.6042      0.5507     0.1280  5
  test sensitivity            0.7913      0.8696     0.2049  5
  test specificity            0.5660      0.6809     0.3511  5
  test precision              0.5295      0.5714     0.1589  5
  test loss                   0.6903      0.5790     0.2683  5
  FPR (FP/(FP+TN))            0.4340      0.3191     0.3511  5
  FNR (FN/(FN+TP))            0.2087      0.1304     0.2049  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5641      0.5667     0.0220  5
  max valid BA                0.5830      0.5885     0.0162  5
  best valid F1               0.6028      0.6010     0.0069  5
  test BA                     0.5471      0.5429     0.0373  5
  test F1                     0.5366      0.6120     0.1344  5
  test sensitivity            0.7323      0.8615     0.2952  5
  test specificity            0.3618      0.3034     0.2537  5
  test precision              0.4540      0.4444     0.0212  5
  test loss                   0.7374      0.6836     0.0857  5
  FPR (FP/(FP+TN))            0.6382      0.6966     0.2537  5
  FNR (FN/(FN+TP))            0.2677      0.1385     0.2952  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5917      0.5278     0.1117  5
  max valid BA                0.6000      0.5278     0.1071  5
  best valid F1               0.5309      0.5143     0.1144  5
  test BA                     0.5903      0.5972     0.0615  5
  test F1                     0.5058      0.5055     0.0740  5
  test sensitivity            0.7167      0.7778     0.2269  5
  test specificity            0.4639      0.5139     0.2415  5
  test precision              0.4105      0.4231     0.0443  5
  test loss                   0.7138      0.7035     0.0225  5
  FPR (FP/(FP+TN))            0.5361      0.4861     0.2415  5
  FNR (FN/(FN+TP))            0.2833      0.2222     0.2269  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5588      0.5147     0.0832  5
  max valid BA                0.5794      0.5294     0.0945  5
  best valid F1               0.5400      0.5000     0.0627  5
  test BA                     0.4765      0.4853     0.0383  5
  test F1                     0.4347      0.4444     0.0400  5
  test sensitivity            0.6941      0.7059     0.1275  5
  test specificity            0.2588      0.2647     0.1147  5
  test precision              0.3186      0.3243     0.0218  5
  test loss                   0.7393      0.6970     0.0609  5
  FPR (FP/(FP+TN))            0.7412      0.7353     0.1147  5
  FNR (FN/(FN+TP))            0.3059      0.2941     0.1275  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.520         0.540         4         0.365              0.395
   CRAL-TRIO     1   129   67             0.799    0.483         0.537         4         0.552              0.525
   CRAL-TRIO     2   129   67             0.793    0.508         0.505         4         0.492              0.531
   CRAL-TRIO     3   129   67             0.806    0.502         0.478         4         0.510              0.501
   CRAL-TRIO     4   129   67             0.804    0.523         0.417         4         0.451              0.532
        GLTP     0    52   26             0.618    0.330         0.373         2         0.492              0.491
        GLTP     1    52   26             0.601    0.496         0.480         2         0.564              0.507
        GLTP     2    52   26             0.618    0.435         0.462         2         0.559              0.497
        GLTP     3    52   26             0.619    0.506         0.499         2         0.578              0.500
        GLTP     4    52   26             0.621    0.636         0.658         2         0.500              0.509
    IP_trans     0    71   24             0.809    0.612         0.625         3         0.753              0.743
    IP_trans     1    71   24             0.808    0.700         0.723         3         0.709              0.707
    IP_trans     2    71   24             0.810    0.649         0.611         3         0.742              0.786
    IP_trans     3    71   24             0.811    0.592         0.584         3         0.587              0.586
    IP_trans     4    71   24             0.808    0.531         0.520         3         0.608              0.659
LBP_BPI_CETP     0    71   24             0.809    0.400         0.472         2         0.691              0.698
LBP_BPI_CETP     1    71   24             0.816    0.462         0.489         2         0.586              0.656
LBP_BPI_CETP     2    71   24             0.808    0.787         0.830         2         0.629              0.625
LBP_BPI_CETP     3    71   24             0.807    0.772         0.781         2         0.771              0.772
LBP_BPI_CETP     4    71   24             0.804    0.895         0.894         2         0.710              0.708
       START     0   153   64             0.791    0.537         0.569         3         0.519              0.497
       START     1   153   64             0.784    0.534         0.465         3         0.469              0.438
       START     2   153   64             0.794    0.494         0.468         3         0.507              0.573
       START     3   153   64             0.797    0.628         0.518         3         0.562              0.529
       START     4   153   64             0.779    0.558         0.447         3         0.429              0.454
   lipocalin     0   108   36             0.847    0.318         0.226         5         0.649              0.674
   lipocalin     1   108   36             0.827    0.195         0.106         5         0.276              0.217
   lipocalin     2   108   36             0.829    0.310         0.179         5         0.577              0.541
   lipocalin     3   108   36             0.846    0.408         0.321         5         0.385              0.376
   lipocalin     4   108   36             0.810    0.427         0.345         5         0.550              0.504
        scp2     0    51   17             0.808    0.540         0.576         2         0.637              0.515
        scp2     1    51   17             0.837    0.326         0.321         3         0.674              0.576
        scp2     2    51   17             0.851    0.420         0.405         3         0.526              0.459
        scp2     3    51   17             0.842    0.671         0.614         3         0.675              0.552
        scp2     4    51   17             0.834    0.492         0.623         3         0.596              0.494

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.507         0.495       4.0         0.474              0.497
GLTP           52.0  26.0             0.615    0.480         0.494       2.0         0.539              0.501
IP_trans       71.0  24.0             0.809    0.617         0.613       3.0         0.680              0.696
LBP_BPI_CETP   71.0  24.0             0.809    0.663         0.693       2.0         0.677              0.692
START         153.0  64.0             0.789    0.550         0.494       3.0         0.497              0.498
lipocalin     108.0  36.0             0.832    0.332         0.235       5.0         0.487              0.462
scp2           51.0  17.0             0.834    0.490         0.508       2.8         0.621              0.519

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.520           0.59       0.467
null_AUC_k15      0.568           0.66       0.499

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.505          0.605        0.43
null_AUC_prot_k15      0.552          0.636        0.49

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
        chem    net  chem_prot  net_prot
epoch                                   
1      0.568  0.495      0.552     0.462
10     0.568  0.531      0.552     0.521
49     0.568  0.550      0.552     0.542
51     0.568  0.550      0.552     0.539
120    0.568  0.520      0.552     0.505

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.594         0.641      0.047          0.654              0.689           0.035
10        0.594         0.630      0.036          0.654              0.673           0.019
49        0.594         0.651      0.057          0.654              0.698           0.044
51        0.594         0.652      0.058          0.654              0.696           0.041
120       0.594         0.645      0.050          0.654              0.690           0.036

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.474  0.507      0.497     0.495      0.018          -0.005
GLTP          0.539  0.480      0.501     0.494      0.065           0.032
IP_trans      0.680  0.617      0.696     0.613      0.019           0.014
LBP_BPI_CETP  0.677  0.663      0.692     0.693      0.091           0.074
START         0.497  0.550      0.498     0.494      0.044           0.032
lipocalin     0.487  0.332      0.462     0.235      0.102           0.090
scp2          0.621  0.490      0.519     0.508      0.014           0.013

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.568          0.660       0.499      0.621
net                 0.520          0.590       0.467      0.490
chem_prot           0.552          0.636       0.490      0.519
net_prot            0.505          0.605       0.430      0.508
increment           0.050          0.041       0.057      0.014
increment_prot      0.036          0.033       0.037      0.013
```
