# descriptors_2paths_extent_protgeom

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_2paths_extent_protgeom'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.7015      0.4066      0.5269      0.6017      0.6955      0.4710
groups_GLTP            5      0.4960      0.6080      0.5632      0.6109      0.5385      0.6308
groups_IP_trans        5      0.4348      0.6936      0.5950      0.5364      0.4917      0.7191
groups_LBP_BPI_CETP    5      0.7130      0.7957      0.6572      0.4961      0.7333      0.8043
groups_START           5      0.6185      0.3933      0.6123      0.4573      0.6844      0.4517
groups_lipocalin       5      0.3111      0.7417      0.5468      0.5621      0.3222      0.7750
groups_scp2            5      0.6824      0.3118      0.5686      0.5297      0.7176      0.3706
ALL                   35      0.5653      0.5644      0.5814      0.5420      0.5976      0.6032

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6004      0.5769     0.0937  35
max valid BA                0.6275      0.6002     0.0933  35
best valid F1               0.6119      0.6030     0.1041  35
test BA                     0.5648      0.5294     0.1084  35
test F1                     0.4759      0.5085     0.1896  35
test sensitivity            0.5653      0.6087     0.2785  35
test specificity            0.5644      0.5532     0.2587  35
test precision              0.4890      0.4935     0.1673  35
test loss                   0.6971      0.6859     0.1629  35
FPR (FP/(FP+TN))            0.4356      0.4468     0.2587  35
FNR (FN/(FN+TP))            0.4347      0.3913     0.2785  35

=== abs(sensitivity-specificity) gap: mean=0.3987 median=0.3515 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5832      0.5899     0.0530  5
  max valid BA                0.6056      0.5948     0.0393  5
  best valid F1               0.7076      0.7051     0.0156  5
  test BA                     0.5540      0.5514     0.0291  5
  test F1                     0.6123      0.6395     0.1046  5
  test sensitivity            0.7015      0.7164     0.2168  5
  test specificity            0.4066      0.3934     0.1888  5
  test precision              0.5641      0.5517     0.0201  5
  test loss                   0.8213      0.6815     0.3170  5
  FPR (FP/(FP+TN))            0.5934      0.6066     0.1888  5
  FNR (FN/(FN+TP))            0.2985      0.2836     0.2168  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5846      0.5385     0.1059  5
  max valid BA                0.6115      0.5577     0.1227  5
  best valid F1               0.6904      0.6667     0.0962  5
  test BA                     0.5520      0.5200     0.1346  5
  test F1                     0.4848      0.5085     0.2230  5
  test sensitivity            0.4960      0.6000     0.3080  5
  test specificity            0.6080      0.6800     0.2791  5
  test precision              0.5635      0.5556     0.1074  5
  test loss                   0.7611      0.7063     0.1238  5
  FPR (FP/(FP+TN))            0.3920      0.3200     0.2791  5
  FNR (FN/(FN+TP))            0.5040      0.4000     0.3080  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6054      0.6210     0.0811  5
  max valid BA                0.6279      0.6325     0.0647  5
  best valid F1               0.5407      0.5263     0.0747  5
  test BA                     0.5642      0.5809     0.0751  5
  test F1                     0.3772      0.4828     0.1965  5
  test sensitivity            0.4348      0.4783     0.2900  5
  test specificity            0.6936      0.6596     0.2265  5
  test precision              0.5303      0.4000     0.2843  5
  test loss                   0.6613      0.6695     0.0305  5
  FPR (FP/(FP+TN))            0.3064      0.3404     0.2265  5
  FNR (FN/(FN+TP))            0.5652      0.5217     0.2900  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7688      0.7695     0.0352  5
  max valid BA                0.7995      0.7983     0.0409  5
  best valid F1               0.7245      0.7200     0.0450  5
  test BA                     0.7544      0.7516     0.0903  5
  test F1                     0.6553      0.6667     0.1133  5
  test sensitivity            0.7130      0.6522     0.2373  5
  test specificity            0.7957      0.7660     0.0761  5
  test precision              0.6336      0.6562     0.0560  5
  test loss                   0.5025      0.5133     0.0731  5
  FPR (FP/(FP+TN))            0.2043      0.2340     0.0761  5
  FNR (FN/(FN+TP))            0.2870      0.3478     0.2373  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5680      0.5519     0.0259  5
  max valid BA                0.5764      0.5823     0.0256  5
  best valid F1               0.5927      0.5972     0.0156  5
  test BA                     0.5059      0.5080     0.0719  5
  test F1                     0.5005      0.5352     0.0806  5
  test sensitivity            0.6185      0.5846     0.1701  5
  test specificity            0.3933      0.4045     0.1691  5
  test precision              0.4281      0.4265     0.0649  5
  test loss                   0.7023      0.6981     0.0261  5
  FPR (FP/(FP+TN))            0.6067      0.5955     0.1691  5
  FNR (FN/(FN+TP))            0.3815      0.4154     0.1701  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5486      0.5347     0.0653  5
  max valid BA                0.5806      0.5486     0.0694  5
  best valid F1               0.5107      0.5120     0.0831  5
  test BA                     0.5264      0.5208     0.0578  5
  test F1                     0.2676      0.1923     0.2186  5
  test sensitivity            0.3111      0.1389     0.3277  5
  test specificity            0.7417      0.8472     0.2269  5
  test precision              0.3758      0.3966     0.2036  5
  test loss                   0.6550      0.6708     0.0440  5
  FPR (FP/(FP+TN))            0.2583      0.1528     0.2269  5
  FNR (FN/(FN+TP))            0.6889      0.8611     0.3277  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5441      0.5588     0.0560  5
  max valid BA                0.5912      0.6029     0.0242  5
  best valid F1               0.5164      0.5246     0.0434  5
  test BA                     0.4971      0.5000     0.0366  5
  test F1                     0.4337      0.4667     0.0778  5
  test sensitivity            0.6824      0.8235     0.2482  5
  test specificity            0.3118      0.1765     0.2033  5
  test precision              0.3273      0.3333     0.0283  5
  test loss                   0.7765      0.7285     0.1321  5
  FPR (FP/(FP+TN))            0.6882      0.8235     0.2033  5
  FNR (FN/(FN+TP))            0.3176      0.1765     0.2482  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.479         0.456         4         0.365              0.395
   CRAL-TRIO     1   129   67             0.799    0.556         0.447         4         0.552              0.525
   CRAL-TRIO     2   129   67             0.793    0.555         0.459         4         0.492              0.531
   CRAL-TRIO     3   129   67             0.806    0.678         0.556         4         0.510              0.501
   CRAL-TRIO     4   129   67             0.804    0.541         0.520         4         0.451              0.532
        GLTP     0    52   26             0.618    0.339         0.393         2         0.492              0.491
        GLTP     1    52   26             0.601    0.463         0.502         2         0.564              0.507
        GLTP     2    52   26             0.618    0.436         0.444         2         0.559              0.497
        GLTP     3    52   26             0.619    0.562         0.501         2         0.578              0.500
        GLTP     4    52   26             0.621    0.738         0.747         2         0.500              0.509
    IP_trans     0    71   24             0.809    0.689         0.704         3         0.753              0.743
    IP_trans     1    71   24             0.808    0.614         0.668         3         0.709              0.707
    IP_trans     2    71   24             0.810    0.504         0.477         3         0.742              0.786
    IP_trans     3    71   24             0.811    0.601         0.599         3         0.587              0.586
    IP_trans     4    71   24             0.808    0.543         0.518         3         0.608              0.659
LBP_BPI_CETP     0    71   24             0.809    0.672         0.634         2         0.691              0.698
LBP_BPI_CETP     1    71   24             0.816    0.821         0.821         2         0.586              0.656
LBP_BPI_CETP     2    71   24             0.808    0.829         0.830         2         0.629              0.625
LBP_BPI_CETP     3    71   24             0.807    0.751         0.744         2         0.771              0.772
LBP_BPI_CETP     4    71   24             0.804    0.876         0.871         2         0.710              0.708
       START     0   153   64             0.791    0.500         0.493         3         0.519              0.497
       START     1   153   64             0.784    0.530         0.445         3         0.469              0.438
       START     2   153   64             0.794    0.508         0.461         3         0.507              0.573
       START     3   153   64             0.797    0.525         0.578         3         0.562              0.529
       START     4   153   64             0.779    0.523         0.452         3         0.429              0.454
   lipocalin     0   108   36             0.847    0.514         0.572         5         0.649              0.674
   lipocalin     1   108   36             0.827    0.437         0.348         5         0.276              0.217
   lipocalin     2   108   36             0.829    0.332         0.187         5         0.577              0.541
   lipocalin     3   108   36             0.846    0.449         0.375         5         0.385              0.376
   lipocalin     4   108   36             0.810    0.390         0.266         5         0.550              0.504
        scp2     0    51   17             0.808    0.472         0.524         2         0.637              0.515
        scp2     1    51   17             0.837    0.345         0.409         3         0.674              0.576
        scp2     2    51   17             0.851    0.430         0.482         3         0.526              0.459
        scp2     3    51   17             0.842    0.413         0.497         3         0.675              0.552
        scp2     4    51   17             0.834    0.477         0.571         3         0.596              0.494

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.562         0.488       4.0         0.474              0.497
GLTP           52.0  26.0             0.615    0.508         0.517       2.0         0.539              0.501
IP_trans       71.0  24.0             0.809    0.590         0.593       3.0         0.680              0.696
LBP_BPI_CETP   71.0  24.0             0.809    0.790         0.780       2.0         0.677              0.692
START         153.0  64.0             0.789    0.517         0.486       3.0         0.497              0.498
lipocalin     108.0  36.0             0.832    0.424         0.350       5.0         0.487              0.462
scp2           51.0  17.0             0.834    0.428         0.497       2.8         0.621              0.519

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.546          0.602       0.503
null_AUC_k15      0.568          0.660       0.499

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.530          0.623        0.46
null_AUC_prot_k15      0.552          0.636        0.49

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
        chem    net  chem_prot  net_prot
epoch                                   
1      0.568  0.487      0.552     0.471
10     0.568  0.529      0.552     0.515
49     0.568  0.544      0.552     0.531
51     0.568  0.546      0.552     0.541
120    0.568  0.546      0.552     0.530

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.594         0.665      0.071          0.654              0.700           0.046
10        0.594         0.642      0.048          0.654              0.684           0.030
49        0.594         0.659      0.064          0.654              0.695           0.041
51        0.594         0.652      0.058          0.654              0.687           0.033
120       0.594         0.649      0.055          0.654              0.686           0.032

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.474  0.562      0.497     0.488      0.059           0.048
GLTP          0.539  0.508      0.501     0.517      0.063           0.028
IP_trans      0.680  0.590      0.696     0.593      0.028           0.016
LBP_BPI_CETP  0.677  0.790      0.692     0.780      0.136           0.093
START         0.497  0.517      0.498     0.486      0.023           0.011
lipocalin     0.487  0.424      0.462     0.350      0.058           0.016
scp2          0.621  0.428      0.519     0.497      0.018           0.012

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.568          0.660       0.499      0.621
net                 0.546          0.602       0.503      0.428
chem_prot           0.552          0.636       0.490      0.519
net_prot            0.530          0.623       0.460      0.497
increment           0.055          0.061       0.051      0.018
increment_prot      0.032          0.040       0.026      0.012
```
