# descriptors_no_extent_coarse

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4925      0.6852         n/a         n/a         n/a         n/a
groups_GLTP            5      0.5040      0.4400         n/a         n/a         n/a         n/a
groups_IP_trans        5      0.6000      0.6851         n/a         n/a         n/a         n/a
groups_LBP_BPI_CETP    5      0.8087      0.7915         n/a         n/a         n/a         n/a
groups_START           5      0.4123      0.5753         n/a         n/a         n/a         n/a
groups_lipocalin       5      0.6611      0.5556         n/a         n/a         n/a         n/a
groups_scp2            5      0.5882      0.6118         n/a         n/a         n/a         n/a
ALL                   35      0.5810      0.6206         n/a         n/a         n/a         n/a

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6341      0.6215     0.0922  35
max valid BA                0.6400      0.6219     0.0912  35
best valid F1               0.5900      0.5909     0.1060  35
test BA                     0.6008      0.6040     0.1106  35
test F1                     0.5179      0.5306     0.1451  35
test sensitivity            0.5810      0.5556     0.2196  35
test specificity            0.6206      0.6596     0.1926  35
test precision              0.5073      0.4819     0.1060  34
test loss                   0.6822      0.6873     0.0177  35
FPR (FP/(FP+TN))            0.3794      0.3404     0.1926  35
FNR (FN/(FN+TP))            0.4190      0.4444     0.2196  35

=== abs(sensitivity-specificity) gap: mean=0.2455 median=0.1796 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6095      0.6184     0.0481  5
  max valid BA                0.6160      0.6184     0.0469  5
  best valid F1               0.6386      0.6357     0.0633  5
  test BA                     0.5889      0.5823     0.0365  5
  test F1                     0.5470      0.5500     0.0888  5
  test sensitivity            0.4925      0.4925     0.1213  5
  test specificity            0.6852      0.6721     0.0511  5
  test precision              0.6284      0.6226     0.0229  5
  test loss                   0.6895      0.6901     0.0037  5
  FPR (FP/(FP+TN))            0.3148      0.3279     0.0511  5
  FNR (FN/(FN+TP))            0.5075      0.5075     0.1213  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5615      0.5385     0.0344  5
  max valid BA                0.5769      0.5385     0.0544  5
  best valid F1               0.5953      0.6667     0.1229  5
  test BA                     0.4720      0.4600     0.0657  5
  test F1                     0.4637      0.4255     0.1383  5
  test sensitivity            0.5040      0.4000     0.2851  5
  test specificity            0.4400      0.5200     0.1939  5
  test precision              0.4601      0.4444     0.0490  5
  test loss                   0.6984      0.6953     0.0071  5
  FPR (FP/(FP+TN))            0.5600      0.4800     0.1939  5
  FNR (FN/(FN+TP))            0.4960      0.6000     0.2851  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6404      0.6219     0.0671  5
  max valid BA                0.6426      0.6219     0.0698  5
  best valid F1               0.5564      0.5185     0.0584  5
  test BA                     0.6426      0.6443     0.0195  5
  test F1                     0.5341      0.5306     0.0269  5
  test sensitivity            0.6000      0.6087     0.0567  5
  test specificity            0.6851      0.6809     0.0381  5
  test precision              0.4831      0.4839     0.0198  5
  test loss                   0.6710      0.6650     0.0104  5
  FPR (FP/(FP+TN))            0.3149      0.3191     0.0381  5
  FNR (FN/(FN+TP))            0.4000      0.3913     0.0567  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7996      0.7988     0.0293  5
  max valid BA                0.8019      0.7996     0.0328  5
  best valid F1               0.7325      0.7273     0.0403  5
  test BA                     0.8001      0.8057     0.0236  5
  test F1                     0.7244      0.7308     0.0302  5
  test sensitivity            0.8087      0.8261     0.0728  5
  test specificity            0.7915      0.7872     0.0712  5
  test precision              0.6622      0.6552     0.0612  5
  test loss                   0.6564      0.6604     0.0232  5
  FPR (FP/(FP+TN))            0.2085      0.2128     0.0712  5
  FNR (FN/(FN+TP))            0.1913      0.1739     0.0728  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5331      0.5336     0.0258  5
  max valid BA                0.5401      0.5377     0.0304  5
  best valid F1               0.4982      0.4651     0.0896  5
  test BA                     0.4938      0.4963     0.0581  5
  test F1                     0.3579      0.4242     0.2101  5
  test sensitivity            0.4123      0.4308     0.3074  5
  test specificity            0.5753      0.5618     0.3554  5
  test precision              0.4378      0.4133     0.0994  4
  test loss                   0.6952      0.6901     0.0102  5
  FPR (FP/(FP+TN))            0.4247      0.4382     0.3554  5
  FNR (FN/(FN+TP))            0.5877      0.5692     0.3074  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6208      0.6389     0.0561  5
  max valid BA                0.6264      0.6458     0.0541  5
  best valid F1               0.5123      0.5432     0.1125  5
  test BA                     0.6083      0.6111     0.0593  5
  test F1                     0.5057      0.5385     0.0946  5
  test sensitivity            0.6611      0.6667     0.2393  5
  test specificity            0.5556      0.5417     0.1695  5
  test precision              0.4281      0.4138     0.0496  5
  test loss                   0.6808      0.6841     0.0144  5
  FPR (FP/(FP+TN))            0.4444      0.4583     0.1695  5
  FNR (FN/(FN+TP))            0.3389      0.3333     0.2393  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6735      0.6618     0.0554  5
  max valid BA                0.6765      0.6618     0.0540  5
  best valid F1               0.5966      0.5833     0.0520  5
  test BA                     0.6000      0.6176     0.0583  5
  test F1                     0.4927      0.5294     0.0764  5
  test sensitivity            0.5882      0.5294     0.1664  5
  test specificity            0.6118      0.5882     0.1338  5
  test precision              0.4372      0.4333     0.0720  5
  test loss                   0.6840      0.6862     0.0072  5
  FPR (FP/(FP+TN))            0.3882      0.4118     0.1338  5
  FNR (FN/(FN+TP))            0.4118      0.4706     0.1664  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.523         0.497         4         0.340              0.381
   CRAL-TRIO     1   129   67             0.799    0.625         0.589         4         0.551              0.568
   CRAL-TRIO     2   129   67             0.793    0.532         0.484         4         0.472              0.451
   CRAL-TRIO     3   129   67             0.806    0.663         0.574         4         0.469              0.466
   CRAL-TRIO     4   129   67             0.804    0.542         0.535         4         0.433              0.507
        GLTP     0    52   26             0.618    0.572         0.550         2         0.492              0.500
        GLTP     1    52   26             0.601    0.503         0.498         2         0.558              0.500
        GLTP     2    52   26             0.618    0.513         0.501         2         0.547              0.483
        GLTP     3    52   26             0.619    0.516         0.490         2         0.589              0.500
        GLTP     4    52   26             0.621    0.493         0.513         2         0.495              0.509
    IP_trans     0    71   24             0.809    0.688         0.670         3         0.761              0.748
    IP_trans     1    71   24             0.808    0.673         0.695         3         0.720              0.717
    IP_trans     2    71   24             0.810    0.585         0.559         3         0.739              0.784
    IP_trans     3    71   24             0.811    0.600         0.596         3         0.588              0.591
    IP_trans     4    71   24             0.808    0.547         0.571         3         0.623              0.677
LBP_BPI_CETP     0    71   24             0.809    0.793         0.770         2         0.719              0.701
LBP_BPI_CETP     1    71   24             0.816    0.866         0.836         2         0.601              0.675
LBP_BPI_CETP     2    71   24             0.808    0.849         0.837         2         0.623              0.625
LBP_BPI_CETP     3    71   24             0.807    0.779         0.758         2         0.812              0.814
LBP_BPI_CETP     4    71   24             0.804    0.815         0.818         2         0.769              0.764
       START     0   153   64             0.791    0.419         0.419         3         0.508              0.479
       START     1   153   64             0.784    0.491         0.487         3         0.454              0.439
       START     2   153   64             0.794    0.371         0.409         3         0.525              0.558
       START     3   153   64             0.797    0.575         0.563         3         0.596              0.608
       START     4   153   64             0.779    0.442         0.464         3         0.441              0.460
   lipocalin     0   108   36             0.847    0.495         0.413         5         0.605              0.655
   lipocalin     1   108   36             0.827    0.600         0.620         5         0.284              0.217
   lipocalin     2   108   36             0.829    0.646         0.593         5         0.585              0.548
   lipocalin     3   108   36             0.846    0.706         0.757         5         0.352              0.289
   lipocalin     4   108   36             0.810    0.549         0.584         5         0.541              0.463
        scp2     0    51   17             0.808    0.721         0.714         2         0.666              0.619
        scp2     1    51   17             0.837    0.663         0.714         3         0.693              0.626
        scp2     2    51   17             0.851    0.597         0.469         3         0.536              0.417
        scp2     3    51   17             0.842    0.654         0.586         3         0.668              0.576
        scp2     4    51   17             0.834    0.637         0.603         3         0.580              0.405

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.577         0.536       4.0         0.453              0.475
GLTP           52.0  26.0             0.615    0.520         0.511       2.0         0.536              0.499
IP_trans       71.0  24.0             0.809    0.619         0.618       3.0         0.686              0.703
LBP_BPI_CETP   71.0  24.0             0.809    0.821         0.804       2.0         0.705              0.716
START         153.0  64.0             0.789    0.460         0.468       3.0         0.505              0.509
lipocalin     108.0  36.0             0.832    0.599         0.593       5.0         0.473              0.434
scp2           51.0  17.0             0.834    0.654         0.617       2.8         0.629              0.529

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.607          0.698       0.539
null_AUC_k15      0.570          0.673       0.492

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.592          0.680       0.527
null_AUC_prot_k15      0.552          0.649       0.479

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.536      0.552     0.538
10     0.57  0.609      0.552     0.593
49     0.57  0.613      0.552     0.599
51     0.57  0.613      0.552     0.600
120    0.57  0.607      0.552     0.592

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.661      0.054          0.657              0.697           0.040
10        0.607         0.660      0.053          0.657              0.694           0.038
49        0.607         0.660      0.054          0.657              0.694           0.037
51        0.607         0.660      0.053          0.657              0.693           0.036
120       0.607         0.653      0.046          0.657              0.694           0.037

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.577      0.475     0.536      0.038           0.028
GLTP          0.536  0.520      0.499     0.511      0.024           0.020
IP_trans      0.686  0.619      0.703     0.618     -0.011          -0.002
LBP_BPI_CETP  0.705  0.821      0.716     0.804      0.124           0.100
START         0.505  0.460      0.509     0.468      0.041           0.019
lipocalin     0.473  0.599      0.434     0.593      0.080           0.080
scp2          0.629  0.654      0.529     0.617      0.025           0.015

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.607          0.698       0.539      0.654
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.592          0.680       0.527      0.617
increment           0.046          0.046       0.046      0.025
increment_prot      0.037          0.038       0.037      0.015
```
