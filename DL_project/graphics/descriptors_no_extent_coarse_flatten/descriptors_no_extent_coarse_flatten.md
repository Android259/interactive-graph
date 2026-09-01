# descriptors_no_extent_coarse_flatten

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_flatten'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.3522      0.7115      0.6257      0.4784      0.4179      0.7032
groups_GLTP            5      0.5120      0.4400      0.5699      0.5440      0.5692      0.5231
groups_IP_trans        5      0.4000      0.6979      0.6303      0.5085      0.4417      0.7106
groups_LBP_BPI_CETP    5      0.5565      0.8851      0.6330      0.5219      0.6000      0.7872
groups_START           5      0.3692      0.5910      0.6396      0.4543      0.4062      0.6517
groups_lipocalin       5      0.4611      0.6417      0.5193      0.6153      0.4500      0.6861
groups_scp2            5      0.5176      0.5471      0.6348      0.5069      0.6353      0.6882
ALL                   35      0.4527      0.6449      0.6075      0.5185      0.5029      0.6786

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5908      0.5723     0.0843  35
max valid BA                0.6011      0.5879     0.0891  35
best valid F1               0.5147      0.5200     0.1341  35
test BA                     0.5488      0.5206     0.0965  35
test F1                     0.4187      0.4444     0.1825  35
test sensitivity            0.4527      0.4400     0.2569  35
test specificity            0.6449      0.6471     0.2289  35
test precision              0.4671      0.4205     0.1705  34
test loss                   0.6776      0.6874     0.0328  35
FPR (FP/(FP+TN))            0.3551      0.3529     0.2289  35
FNR (FN/(FN+TP))            0.5473      0.5600     0.2569  35

=== abs(sensitivity-specificity) gap: mean=0.3637 median=0.2000 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5606      0.5774     0.0639  5
  max valid BA                0.5676      0.5879     0.0644  5
  best valid F1               0.4697      0.5965     0.2249  5
  test BA                     0.5319      0.5487     0.0465  5
  test F1                     0.3717      0.4381     0.2528  5
  test sensitivity            0.3522      0.3433     0.3269  5
  test specificity            0.7115      0.7541     0.2705  5
  test precision              0.5097      0.6000     0.2073  5
  test loss                   0.6959      0.6930     0.0074  5
  FPR (FP/(FP+TN))            0.2885      0.2459     0.2705  5
  FNR (FN/(FN+TP))            0.6478      0.6567     0.3269  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5462      0.5385     0.0105  5
  max valid BA                0.5538      0.5577     0.0161  5
  best valid F1               0.5587      0.5385     0.0825  5
  test BA                     0.4760      0.5000     0.0477  5
  test F1                     0.4723      0.4444     0.1223  5
  test sensitivity            0.5120      0.4000     0.2763  5
  test specificity            0.4400      0.5200     0.2280  5
  test precision              0.4691      0.5000     0.0538  5
  test loss                   0.7099      0.7067     0.0135  5
  FPR (FP/(FP+TN))            0.5600      0.4800     0.2280  5
  FNR (FN/(FN+TP))            0.4880      0.6000     0.2763  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5762      0.5723     0.0461  5
  max valid BA                0.5994      0.5918     0.0640  5
  best valid F1               0.4704      0.4478     0.0824  5
  test BA                     0.5489      0.5698     0.0765  5
  test F1                     0.3583      0.4643     0.1901  5
  test sensitivity            0.4000      0.5652     0.2670  5
  test specificity            0.6979      0.6596     0.1398  5
  test precision              0.3628      0.3939     0.1149  5
  test loss                   0.6707      0.6700     0.0136  5
  FPR (FP/(FP+TN))            0.3021      0.3404     0.1398  5
  FNR (FN/(FN+TP))            0.6000      0.4348     0.2670  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6936      0.7371     0.0788  5
  max valid BA                0.7168      0.7580     0.0898  5
  best valid F1               0.6033      0.6792     0.1429  5
  test BA                     0.7208      0.6984     0.1087  5
  test F1                     0.5857      0.6000     0.2172  5
  test sensitivity            0.5565      0.6522     0.2687  5
  test specificity            0.8851      0.8936     0.0923  5
  test precision              0.7622      0.7600     0.1582  5
  test loss                   0.6154      0.6211     0.0333  5
  FPR (FP/(FP+TN))            0.1149      0.1064     0.0923  5
  FNR (FN/(FN+TP))            0.4435      0.3478     0.2687  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5290      0.5187     0.0653  5
  max valid BA                0.5345      0.5343     0.0611  5
  best valid F1               0.4902      0.4966     0.0715  5
  test BA                     0.4801      0.4951     0.0452  5
  test F1                     0.3685      0.3729     0.1105  5
  test sensitivity            0.3692      0.3692     0.1565  5
  test specificity            0.5910      0.5730     0.1534  5
  test precision              0.3928      0.4151     0.0488  5
  test loss                   0.6939      0.6937     0.0103  5
  FPR (FP/(FP+TN))            0.4090      0.4270     0.1534  5
  FNR (FN/(FN+TP))            0.6308      0.6308     0.1565  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5681      0.5625     0.0717  5
  max valid BA                0.5681      0.5625     0.0717  5
  best valid F1               0.4388      0.4598     0.1325  5
  test BA                     0.5514      0.5694     0.0416  5
  test F1                     0.3523      0.4500     0.2214  5
  test sensitivity            0.4611      0.5000     0.3725  5
  test specificity            0.6417      0.6389     0.2960  5
  test precision              0.3901      0.3939     0.0220  4
  test loss                   0.6721      0.6771     0.0164  5
  FPR (FP/(FP+TN))            0.3583      0.3611     0.2960  5
  FNR (FN/(FN+TP))            0.5389      0.5000     0.3725  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6618      0.6324     0.0981  5
  max valid BA                0.6676      0.6324     0.0928  5
  best valid F1               0.5717      0.5417     0.1275  5
  test BA                     0.5324      0.5294     0.0554  5
  test F1                     0.4222      0.4364     0.0733  5
  test sensitivity            0.5176      0.5294     0.1523  5
  test specificity            0.5471      0.5882     0.1784  5
  test precision              0.3674      0.3636     0.0545  5
  test loss                   0.6853      0.6846     0.0127  5
  FPR (FP/(FP+TN))            0.4529      0.4118     0.1784  5
  FNR (FN/(FN+TP))            0.4824      0.4706     0.1523  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.454         0.439         4         0.340              0.381
   CRAL-TRIO     1   129   67             0.799    0.457         0.425         4         0.551              0.568
   CRAL-TRIO     2   129   67             0.793    0.496         0.474         4         0.472              0.451
   CRAL-TRIO     3   129   67             0.806    0.627         0.535         4         0.469              0.466
   CRAL-TRIO     4   129   67             0.804    0.473         0.421         4         0.433              0.507
        GLTP     0    52   26             0.618    0.482         0.425         2         0.492              0.500
        GLTP     1    52   26             0.601    0.531         0.534         2         0.558              0.500
        GLTP     2    52   26             0.618    0.550         0.518         2         0.547              0.483
        GLTP     3    52   26             0.619    0.550         0.488         2         0.589              0.500
        GLTP     4    52   26             0.621    0.559         0.523         2         0.495              0.509
    IP_trans     0    71   24             0.809    0.579         0.579         3         0.761              0.748
    IP_trans     1    71   24             0.808    0.630         0.662         3         0.720              0.717
    IP_trans     2    71   24             0.810    0.473         0.503         3         0.739              0.784
    IP_trans     3    71   24             0.811    0.576         0.567         3         0.588              0.591
    IP_trans     4    71   24             0.808    0.531         0.546         3         0.623              0.677
LBP_BPI_CETP     0    71   24             0.809    0.806         0.807         2         0.719              0.701
LBP_BPI_CETP     1    71   24             0.816    0.803         0.798         2         0.601              0.675
LBP_BPI_CETP     2    71   24             0.808    0.679         0.690         2         0.623              0.625
LBP_BPI_CETP     3    71   24             0.807    0.697         0.703         2         0.812              0.814
LBP_BPI_CETP     4    71   24             0.804    0.798         0.821         2         0.769              0.764
       START     0   153   64             0.791    0.448         0.427         3         0.508              0.479
       START     1   153   64             0.784    0.517         0.512         3         0.454              0.439
       START     2   153   64             0.794    0.443         0.443         3         0.525              0.558
       START     3   153   64             0.797    0.597         0.574         3         0.596              0.608
       START     4   153   64             0.779    0.449         0.456         3         0.441              0.460
   lipocalin     0   108   36             0.847    0.295         0.214         5         0.605              0.655
   lipocalin     1   108   36             0.827    0.423         0.370         5         0.284              0.217
   lipocalin     2   108   36             0.829    0.395         0.327         5         0.585              0.548
   lipocalin     3   108   36             0.846    0.467         0.407         5         0.352              0.289
   lipocalin     4   108   36             0.810    0.436         0.426         5         0.541              0.463
        scp2     0    51   17             0.808    0.702         0.641         2         0.666              0.619
        scp2     1    51   17             0.837    0.636         0.570         3         0.693              0.626
        scp2     2    51   17             0.851    0.619         0.571         3         0.536              0.417
        scp2     3    51   17             0.842    0.538         0.382         3         0.668              0.576
        scp2     4    51   17             0.834    0.509         0.484         3         0.580              0.405

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.501         0.459       4.0         0.453              0.475
GLTP           52.0  26.0             0.615    0.535         0.497       2.0         0.536              0.499
IP_trans       71.0  24.0             0.809    0.558         0.571       3.0         0.686              0.703
LBP_BPI_CETP   71.0  24.0             0.809    0.757         0.764       2.0         0.705              0.716
START         153.0  64.0             0.789    0.491         0.482       3.0         0.505              0.509
lipocalin     108.0  36.0             0.832    0.403         0.349       5.0         0.473              0.434
scp2           51.0  17.0             0.834    0.601         0.530       2.8         0.629              0.529

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.549          0.638       0.483
null_AUC_k15      0.570          0.673       0.492

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.522          0.622       0.447
null_AUC_prot_k15      0.552          0.649       0.479

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.530      0.552     0.525
10     0.57  0.585      0.552     0.556
49     0.57  0.564      0.552     0.536
51     0.57  0.562      0.552     0.534
120    0.57  0.549      0.552     0.522

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.659      0.052          0.657              0.704           0.047
10        0.607         0.642      0.035          0.657              0.685           0.028
49        0.607         0.635      0.029          0.657              0.681           0.025
51        0.607         0.636      0.029          0.657              0.681           0.025
120       0.607         0.647      0.040          0.657              0.682           0.025

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.501      0.475     0.459      0.019           0.019
GLTP          0.536  0.535      0.499     0.497      0.014           0.011
IP_trans      0.686  0.558      0.703     0.571      0.013           0.012
LBP_BPI_CETP  0.705  0.757      0.716     0.764      0.087           0.064
START         0.505  0.491      0.509     0.482      0.035           0.014
lipocalin     0.473  0.403      0.434     0.349      0.060           0.038
scp2          0.629  0.601      0.529     0.530      0.055           0.021

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.549          0.638       0.483      0.601
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.522          0.622       0.447      0.530
increment           0.040          0.052       0.032      0.055
increment_prot      0.025          0.032       0.020      0.021
```
