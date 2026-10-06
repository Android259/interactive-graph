# descriptors_2paths_protgeom

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_2paths_protgeom'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6328      0.4820      0.4629      0.6104      0.7015      0.5032
groups_GLTP            5      0.3280      0.5920      0.6158      0.5471      0.4462      0.6692
groups_IP_trans        5      0.5739      0.5149      0.4854      0.6223      0.6667      0.5702
groups_LBP_BPI_CETP    5      0.7913      0.8085      0.5835      0.5448      0.7750      0.8213
groups_START           5      0.6338      0.4899      0.5044      0.5867      0.6000      0.5281
groups_lipocalin       5      0.1722      0.8306      0.4514      0.6419      0.2556      0.8306
groups_scp2            5      0.3412      0.7118      0.5523      0.5647      0.3765      0.7824
ALL                   35      0.4962      0.6328      0.5222      0.5883      0.5459      0.6721

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6085      0.5882     0.0920  35
max valid BA                0.6315      0.6104     0.1007  35
best valid F1               0.5981      0.5918     0.1293  35
test BA                     0.5645      0.5208     0.1180  35
test F1                     0.4478      0.4643     0.2077  35
test sensitivity            0.4962      0.5200     0.2769  35
test specificity            0.6328      0.7021     0.2218  35
test precision              0.4710      0.4706     0.1325  33
test loss                   0.7149      0.6846     0.2522  35
FPR (FP/(FP+TN))            0.3672      0.2979     0.2218  35
FNR (FN/(FN+TP))            0.5038      0.4800     0.2769  35

=== abs(sensitivity-specificity) gap: mean=0.3599 median=0.3362 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6024      0.5977     0.0273  5
  max valid BA                0.6184      0.6175     0.0308  5
  best valid F1               0.6966      0.6988     0.0191  5
  test BA                     0.5574      0.5579     0.0468  5
  test F1                     0.5941      0.5860     0.0699  5
  test sensitivity            0.6328      0.6567     0.1610  5
  test specificity            0.4820      0.4590     0.1846  5
  test precision              0.5811      0.5781     0.0502  5
  test loss                   0.7082      0.6886     0.0577  5
  FPR (FP/(FP+TN))            0.5180      0.5410     0.1846  5
  FNR (FN/(FN+TP))            0.3672      0.3433     0.1610  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5538      0.5577     0.0394  5
  max valid BA                0.6154      0.5577     0.1062  5
  best valid F1               0.6520      0.6667     0.0975  5
  test BA                     0.4600      0.4800     0.0346  5
  test F1                     0.3656      0.3810     0.0888  5
  test sensitivity            0.3280      0.3200     0.1368  5
  test specificity            0.5920      0.6400     0.1906  5
  test precision              0.4475      0.4545     0.0281  5
  test loss                   0.7068      0.7070     0.0204  5
  FPR (FP/(FP+TN))            0.4080      0.3600     0.1906  5
  FNR (FN/(FN+TP))            0.6720      0.6800     0.1368  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6184      0.6303     0.0360  5
  max valid BA                0.6331      0.6334     0.0386  5
  best valid F1               0.5441      0.5538     0.0169  5
  test BA                     0.5444      0.5180     0.0833  5
  test F1                     0.4379      0.4571     0.1205  5
  test sensitivity            0.5739      0.6522     0.2094  5
  test specificity            0.5149      0.5745     0.2187  5
  test precision              0.3700      0.3404     0.0923  5
  test loss                   1.0040      0.6662     0.6178  5
  FPR (FP/(FP+TN))            0.4851      0.4255     0.2187  5
  FNR (FN/(FN+TP))            0.4261      0.3478     0.2094  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7981      0.8001     0.0340  5
  max valid BA                0.8254      0.8107     0.0414  5
  best valid F1               0.7614      0.7451     0.0459  5
  test BA                     0.7999      0.7965     0.0547  5
  test F1                     0.7225      0.7234     0.0669  5
  test sensitivity            0.7913      0.8261     0.1206  5
  test specificity            0.8085      0.8298     0.0499  5
  test precision              0.6707      0.6786     0.0492  5
  test loss                   0.5464      0.5605     0.0959  5
  FPR (FP/(FP+TN))            0.1915      0.1702     0.0499  5
  FNR (FN/(FN+TP))            0.2087      0.1739     0.1206  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5640      0.5535     0.0455  5
  max valid BA                0.5791      0.5654     0.0548  5
  best valid F1               0.5986      0.5943     0.0584  5
  test BA                     0.5619      0.5627     0.0237  5
  test F1                     0.5305      0.5034     0.0771  5
  test sensitivity            0.6338      0.5692     0.2244  5
  test specificity            0.4899      0.4944     0.2112  5
  test precision              0.4823      0.4783     0.0326  5
  test loss                   0.6865      0.6846     0.0097  5
  FPR (FP/(FP+TN))            0.5101      0.5056     0.2112  5
  FNR (FN/(FN+TP))            0.3662      0.4308     0.2244  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5431      0.5417     0.0539  5
  max valid BA                0.5583      0.5556     0.0624  5
  best valid F1               0.4476      0.4800     0.1516  5
  test BA                     0.5014      0.5000     0.0186  5
  test F1                     0.1712      0.1778     0.1724  5
  test sensitivity            0.1722      0.1111     0.2101  5
  test specificity            0.8306      0.9306     0.2341  5
  test precision              0.3716      0.3600     0.0678  3
  test loss                   0.6673      0.6696     0.0236  5
  FPR (FP/(FP+TN))            0.1694      0.0694     0.2341  5
  FNR (FN/(FN+TP))            0.8278      0.8889     0.2101  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5794      0.5588     0.0671  5
  max valid BA                0.5912      0.5588     0.0644  5
  best valid F1               0.4861      0.5000     0.0821  5
  test BA                     0.5265      0.4853     0.1174  5
  test F1                     0.3127      0.2222     0.2061  5
  test sensitivity            0.3412      0.1765     0.3068  5
  test specificity            0.7118      0.7941     0.1707  5
  test precision              0.3341      0.2963     0.1159  5
  test loss                   0.6852      0.6917     0.0174  5
  FPR (FP/(FP+TN))            0.2882      0.2059     0.1707  5
  FNR (FN/(FN+TP))            0.6588      0.8235     0.3068  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.571         0.502         4         0.365              0.395
   CRAL-TRIO     1   129   67             0.799    0.572         0.457         4         0.552              0.525
   CRAL-TRIO     2   129   67             0.793    0.536         0.416         4         0.492              0.531
   CRAL-TRIO     3   129   67             0.806    0.628         0.505         4         0.510              0.501
   CRAL-TRIO     4   129   67             0.804    0.558         0.535         4         0.451              0.532
        GLTP     0    52   26             0.618    0.453         0.422         2         0.492              0.491
        GLTP     1    52   26             0.601    0.430         0.482         2         0.564              0.507
        GLTP     2    52   26             0.618    0.419         0.434         2         0.559              0.497
        GLTP     3    52   26             0.619    0.536         0.473         2         0.578              0.500
        GLTP     4    52   26             0.621    0.638         0.639         2         0.500              0.509
    IP_trans     0    71   24             0.809    0.652         0.639         3         0.753              0.743
    IP_trans     1    71   24             0.808    0.643         0.665         3         0.709              0.707
    IP_trans     2    71   24             0.810    0.616         0.610         3         0.742              0.786
    IP_trans     3    71   24             0.811    0.632         0.644         3         0.587              0.586
    IP_trans     4    71   24             0.808    0.523         0.484         3         0.608              0.659
LBP_BPI_CETP     0    71   24             0.809    0.826         0.829         2         0.691              0.698
LBP_BPI_CETP     1    71   24             0.816    0.836         0.883         2         0.586              0.656
LBP_BPI_CETP     2    71   24             0.808    0.806         0.805         2         0.629              0.625
LBP_BPI_CETP     3    71   24             0.807    0.816         0.800         2         0.771              0.772
LBP_BPI_CETP     4    71   24             0.804    0.889         0.941         2         0.710              0.708
       START     0   153   64             0.791    0.510         0.478         3         0.519              0.497
       START     1   153   64             0.784    0.524         0.465         3         0.469              0.438
       START     2   153   64             0.794    0.531         0.471         3         0.507              0.573
       START     3   153   64             0.797    0.678         0.604         3         0.562              0.529
       START     4   153   64             0.779    0.551         0.459         3         0.429              0.454
   lipocalin     0   108   36             0.847    0.246         0.160         5         0.649              0.674
   lipocalin     1   108   36             0.827    0.355         0.219         5         0.276              0.217
   lipocalin     2   108   36             0.829    0.309         0.167         5         0.577              0.541
   lipocalin     3   108   36             0.846    0.352         0.187         5         0.385              0.376
   lipocalin     4   108   36             0.810    0.418         0.215         5         0.550              0.504
        scp2     0    51   17             0.808    0.453         0.453         2         0.637              0.515
        scp2     1    51   17             0.837    0.359         0.353         3         0.674              0.576
        scp2     2    51   17             0.851    0.407         0.432         3         0.526              0.459
        scp2     3    51   17             0.842    0.410         0.519         3         0.675              0.552
        scp2     4    51   17             0.834    0.503         0.499         3         0.596              0.494

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.573         0.483       4.0         0.474              0.497
GLTP           52.0  26.0             0.615    0.495         0.490       2.0         0.539              0.501
IP_trans       71.0  24.0             0.809    0.613         0.608       3.0         0.680              0.696
LBP_BPI_CETP   71.0  24.0             0.809    0.835         0.852       2.0         0.677              0.692
START         153.0  64.0             0.789    0.559         0.495       3.0         0.497              0.498
lipocalin     108.0  36.0             0.832    0.336         0.190       5.0         0.487              0.462
scp2           51.0  17.0             0.834    0.426         0.451       2.8         0.621              0.519

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.548          0.625       0.491
null_AUC_k15      0.568          0.660       0.499

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.510          0.637       0.414
null_AUC_prot_k15      0.552          0.636       0.490

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
        chem    net  chem_prot  net_prot
epoch                                   
1      0.568  0.519      0.552     0.517
10     0.568  0.549      0.552     0.535
49     0.568  0.537      0.552     0.508
51     0.568  0.530      0.552     0.496
120    0.568  0.548      0.552     0.510

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.594         0.642      0.048          0.654              0.689           0.035
10        0.594         0.647      0.053          0.654              0.690           0.036
49        0.594         0.644      0.050          0.654              0.687           0.033
51        0.594         0.646      0.051          0.654              0.691           0.037
120       0.594         0.648      0.054          0.654              0.696           0.042

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.474  0.573      0.497     0.483      0.052           0.045
GLTP          0.539  0.495      0.501     0.490      0.034           0.009
IP_trans      0.680  0.613      0.696     0.608     -0.003           0.005
LBP_BPI_CETP  0.677  0.835      0.692     0.852      0.166           0.135
START         0.497  0.559      0.498     0.495      0.051           0.020
lipocalin     0.487  0.336      0.462     0.190      0.093           0.074
scp2          0.621  0.426      0.519     0.451     -0.016           0.007

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.568          0.660       0.499      0.621
net                 0.548          0.625       0.491      0.426
chem_prot           0.552          0.636       0.490      0.519
net_prot            0.510          0.637       0.414      0.451
increment           0.054          0.049       0.057     -0.016
increment_prot      0.042          0.049       0.037      0.007
```
