# descriptors_no_extent_coarse_add_lipprop_lr005

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_add_lipprop_lr005'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4119      0.7213      0.7171      0.2997      0.4358      0.6871
groups_GLTP            5      0.7040      0.2320      0.4921      0.5550      0.7923      0.2769
groups_IP_trans        5      0.6348      0.6128      0.5030      0.5303      0.6250      0.6085
groups_LBP_BPI_CETP    5      0.8087      0.7021      0.5881      0.4513      0.7917      0.6681
groups_START           5      0.8369      0.1483      0.4751      0.5543      0.8656      0.1820
groups_lipocalin       5      0.8333      0.3222      0.4789      0.5428      0.8556      0.3500
groups_scp2            5      0.7882      0.4118      0.5806      0.4761      0.7765      0.4824
ALL                   35      0.7168      0.4501      0.5479      0.4871      0.7346      0.4650

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5998      0.6006     0.0802  35
max valid BA                0.6246      0.6104     0.0940  35
best valid F1               0.6216      0.6000     0.0774  35
test BA                     0.5835      0.5791     0.1041  35
test F1                     0.5410      0.5487     0.1346  35
test sensitivity            0.7168      0.7647     0.2465  35
test specificity            0.4501      0.4426     0.3069  35
test precision              0.4705      0.4483     0.1454  35
test loss                   0.6922      0.6931     0.0102  35
FPR (FP/(FP+TN))            0.5499      0.5574     0.3069  35
FNR (FN/(FN+TP))            0.2832      0.2353     0.2465  35

=== abs(sensitivity-specificity) gap: mean=0.4653 median=0.4006 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5615      0.5823     0.0390  5
  max valid BA                0.5804      0.5831     0.0456  5
  best valid F1               0.6929      0.6923     0.0101  5
  test BA                     0.5666      0.5755     0.0443  5
  test F1                     0.4398      0.5487     0.2603  5
  test sensitivity            0.4119      0.4627     0.2789  5
  test specificity            0.7213      0.7541     0.2159  5
  test precision              0.5095      0.5938     0.2884  5
  test loss                   0.6921      0.6930     0.0019  5
  FPR (FP/(FP+TN))            0.2787      0.2459     0.2159  5
  FNR (FN/(FN+TP))            0.5881      0.5373     0.2789  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5346      0.5385     0.0394  5
  max valid BA                0.5385      0.5385     0.0360  5
  best valid F1               0.6702      0.6667     0.0078  5
  test BA                     0.4680      0.4800     0.0415  5
  test F1                     0.5336      0.6389     0.1726  5
  test sensitivity            0.7040      0.9200     0.3483  5
  test specificity            0.2320      0.0800     0.2999  5
  test precision              0.4640      0.4894     0.0447  5
  test loss                   0.6959      0.6937     0.0048  5
  FPR (FP/(FP+TN))            0.7680      0.9200     0.2999  5
  FNR (FN/(FN+TP))            0.2960      0.0800     0.3483  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6168      0.6113     0.0559  5
  max valid BA                0.6351      0.6312     0.0632  5
  best valid F1               0.5561      0.5417     0.0483  5
  test BA                     0.6238      0.6341     0.0259  5
  test F1                     0.5190      0.5357     0.0479  5
  test sensitivity            0.6348      0.6522     0.1395  5
  test specificity            0.6128      0.6383     0.1120  5
  test precision              0.4476      0.4545     0.0235  5
  test loss                   0.6848      0.6830     0.0083  5
  FPR (FP/(FP+TN))            0.3872      0.3617     0.1120  5
  FNR (FN/(FN+TP))            0.3652      0.3478     0.1395  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7299      0.7460     0.0762  5
  max valid BA                0.7700      0.7779     0.1013  5
  best valid F1               0.7066      0.7000     0.0996  5
  test BA                     0.7554      0.7766     0.0836  5
  test F1                     0.6802      0.6866     0.0853  5
  test sensitivity            0.8087      0.8696     0.1910  5
  test specificity            0.7021      0.8298     0.2708  5
  test precision              0.6385      0.7143     0.1739  5
  test loss                   0.6817      0.6832     0.0091  5
  FPR (FP/(FP+TN))            0.2979      0.1702     0.2708  5
  FNR (FN/(FN+TP))            0.1913      0.1304     0.1910  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5238      0.5000     0.0381  5
  max valid BA                0.5335      0.5316     0.0357  5
  best valid F1               0.5917      0.5899     0.0041  5
  test BA                     0.4926      0.5000     0.0350  5
  test F1                     0.5495      0.5936     0.0664  5
  test sensitivity            0.8369      1.0000     0.2250  5
  test specificity            0.1483      0.0000     0.2069  5
  test precision              0.4166      0.4221     0.0274  5
  test loss                   0.7056      0.7023     0.0127  5
  FPR (FP/(FP+TN))            0.8517      1.0000     0.2069  5
  FNR (FN/(FN+TP))            0.1631      0.0000     0.2250  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6028      0.6181     0.0604  5
  max valid BA                0.6528      0.6389     0.0635  5
  best valid F1               0.5650      0.5739     0.0693  5
  test BA                     0.5778      0.5972     0.0541  5
  test F1                     0.5237      0.5263     0.0232  5
  test sensitivity            0.8333      0.8611     0.1724  5
  test specificity            0.3222      0.2917     0.2601  5
  test precision              0.3959      0.3864     0.0632  5
  test loss                   0.6965      0.6945     0.0042  5
  FPR (FP/(FP+TN))            0.6778      0.7083     0.2601  5
  FNR (FN/(FN+TP))            0.1667      0.1389     0.1724  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6294      0.6176     0.0242  5
  max valid BA                0.6618      0.6618     0.0294  5
  best valid F1               0.5686      0.5667     0.0361  5
  test BA                     0.6000      0.6471     0.0994  5
  test F1                     0.5412      0.5652     0.0617  5
  test sensitivity            0.7882      0.7647     0.0671  5
  test specificity            0.4118      0.5294     0.2606  5
  test precision              0.4215      0.4483     0.0865  5
  test loss                   0.6892      0.6887     0.0073  5
  FPR (FP/(FP+TN))            0.5882      0.4706     0.2606  5
  FNR (FN/(FN+TP))            0.2118      0.2353     0.0671  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.500         0.500         4         0.340              0.381
   CRAL-TRIO     1   129   67             0.799    0.656         0.636         4         0.551              0.568
   CRAL-TRIO     2   129   67             0.793    0.500         0.500         4         0.472              0.451
   CRAL-TRIO     3   129   67             0.806    0.500         0.500         4         0.469              0.466
   CRAL-TRIO     4   129   67             0.804    0.500         0.500         4         0.433              0.507
        GLTP     0    52   26             0.618    0.500         0.500         2         0.492              0.500
        GLTP     1    52   26             0.601    0.500         0.500         2         0.558              0.500
        GLTP     2    52   26             0.618    0.500         0.500         2         0.547              0.483
        GLTP     3    52   26             0.619    0.500         0.500         2         0.589              0.500
        GLTP     4    52   26             0.621    0.500         0.500         2         0.495              0.509
    IP_trans     0    71   24             0.809    0.500         0.500         3         0.761              0.748
    IP_trans     1    71   24             0.808    0.500         0.500         3         0.720              0.717
    IP_trans     2    71   24             0.810    0.500         0.500         3         0.739              0.784
    IP_trans     3    71   24             0.811    0.500         0.500         3         0.588              0.591
    IP_trans     4    71   24             0.808    0.500         0.500         3         0.623              0.677
LBP_BPI_CETP     0    71   24             0.809    0.500         0.500         2         0.719              0.701
LBP_BPI_CETP     1    71   24             0.816    0.500         0.500         2         0.601              0.675
LBP_BPI_CETP     2    71   24             0.808    0.500         0.500         2         0.623              0.625
LBP_BPI_CETP     3    71   24             0.807    0.500         0.500         2         0.812              0.814
LBP_BPI_CETP     4    71   24             0.804    0.500         0.500         2         0.769              0.764
       START     0   153   64             0.791    0.500         0.500         3         0.508              0.479
       START     1   153   64             0.784    0.500         0.500         3         0.454              0.439
       START     2   153   64             0.794    0.500         0.500         3         0.525              0.558
       START     3   153   64             0.797    0.500         0.500         3         0.596              0.608
       START     4   153   64             0.779    0.452         0.486         3         0.441              0.460
   lipocalin     0   108   36             0.847    0.500         0.500         5         0.605              0.655
   lipocalin     1   108   36             0.827    0.500         0.500         5         0.284              0.217
   lipocalin     2   108   36             0.829    0.500         0.500         5         0.585              0.548
   lipocalin     3   108   36             0.846    0.500         0.500         5         0.352              0.289
   lipocalin     4   108   36             0.810    0.500         0.500         5         0.541              0.463
        scp2     0    51   17             0.808    0.500         0.500         2         0.666              0.619
        scp2     1    51   17             0.837    0.500         0.500         3         0.693              0.626
        scp2     2    51   17             0.851    0.500         0.500         3         0.536              0.417
        scp2     3    51   17             0.842    0.500         0.500         3         0.668              0.576
        scp2     4    51   17             0.834    0.500         0.500         3         0.580              0.405

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.531         0.527       4.0         0.453              0.475
GLTP           52.0  26.0             0.615    0.500         0.500       2.0         0.536              0.499
IP_trans       71.0  24.0             0.809    0.500         0.500       3.0         0.686              0.703
LBP_BPI_CETP   71.0  24.0             0.809    0.500         0.500       2.0         0.705              0.716
START         153.0  64.0             0.789    0.490         0.497       3.0         0.505              0.509
lipocalin     108.0  36.0             0.832    0.500         0.500       5.0         0.473              0.434
scp2           51.0  17.0             0.834    0.500         0.500       2.8         0.629              0.529

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.503          0.500       0.505
null_AUC_k15      0.570          0.673       0.492

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.503          0.500       0.506
null_AUC_prot_k15      0.552          0.649       0.479

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.579      0.552     0.562
10     0.57  0.614      0.552     0.608
49     0.57  0.517      0.552     0.518
51     0.57  0.519      0.552     0.518
120    0.57  0.503      0.552     0.503

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.662      0.056          0.657              0.702           0.045
10        0.607         0.665      0.059          0.657              0.701           0.045
49        0.607         0.619      0.013          0.657              0.666           0.009
51        0.607         0.619      0.012          0.657              0.665           0.009
120       0.607         0.608      0.002          0.657              0.657           0.000

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.531      0.475     0.527      0.007           0.002
GLTP          0.536  0.500      0.499     0.500      0.000           0.000
IP_trans      0.686  0.500      0.703     0.500      0.000           0.000
LBP_BPI_CETP  0.705  0.500      0.716     0.500      0.000           0.000
START         0.505  0.490      0.509     0.497      0.003           0.001
lipocalin     0.473  0.500      0.434     0.500      0.000           0.000
scp2          0.629  0.500      0.529     0.500      0.000           0.000

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.503          0.500       0.505      0.500
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.503          0.500       0.506      0.500
increment           0.002          0.000       0.003      0.000
increment_prot      0.000          0.000       0.001      0.000
```
