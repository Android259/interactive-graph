# descriptors

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5194      0.5836      0.6046      0.4781      0.5522      0.5871
groups_GLTP            5      0.2880      0.6000      0.4788      0.6058      0.4077      0.7077
groups_IP_trans        5      0.5043      0.7021      0.5846      0.4986      0.5583      0.7106
groups_LBP_BPI_CETP    5      0.7913      0.8000      0.6175      0.4853      0.8500      0.7574
groups_START           5      0.5323      0.4494      0.5420      0.4782      0.5500      0.4989
groups_lipocalin       5      0.6500      0.4667      0.6349      0.4859      0.6778      0.4944
groups_scp2            5      0.7412      0.4294      0.6004      0.5080      0.7294      0.5353
ALL                   35      0.5752      0.5759      0.5804      0.5057      0.6179      0.6131

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6155      0.6042     0.0950  35
max valid BA                0.6232      0.6042     0.0951  35
best valid F1               0.5804      0.5802     0.1088  35
test BA                     0.5756      0.5463     0.1119  35
test F1                     0.4875      0.5000     0.1659  35
test sensitivity            0.5752      0.5846     0.2441  35
test specificity            0.5759      0.6230     0.2313  35
test precision              0.4758      0.4444     0.1084  33
test loss                   0.6882      0.6914     0.0146  35
FPR (FP/(FP+TN))            0.4241      0.3770     0.2313  35
FNR (FN/(FN+TP))            0.4248      0.4154     0.2441  35

=== abs(sensitivity-specificity) gap: mean=0.3112 median=0.2528 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5697      0.5550     0.0397  5
  max valid BA                0.5761      0.5762     0.0401  5
  best valid F1               0.6213      0.6260     0.0736  5
  test BA                     0.5515      0.5371     0.0377  5
  test F1                     0.5390      0.5124     0.0824  5
  test sensitivity            0.5194      0.4627     0.1513  5
  test specificity            0.5836      0.6393     0.1441  5
  test precision              0.5793      0.5652     0.0379  5
  test loss                   0.6903      0.6922     0.0043  5
  FPR (FP/(FP+TN))            0.4164      0.3607     0.1441  5
  FNR (FN/(FN+TP))            0.4806      0.5373     0.1513  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5577      0.5577     0.0490  5
  max valid BA                0.5615      0.5577     0.0479  5
  best valid F1               0.5976      0.6667     0.1160  5
  test BA                     0.4440      0.4600     0.0518  5
  test F1                     0.3051      0.3636     0.1752  5
  test sensitivity            0.2880      0.3200     0.1863  5
  test specificity            0.6000      0.6000     0.2843  5
  test precision              0.4242      0.4293     0.0225  4
  test loss                   0.6983      0.6975     0.0042  5
  FPR (FP/(FP+TN))            0.4000      0.4000     0.2843  5
  FNR (FN/(FN+TP))            0.7120      0.6800     0.1863  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6345      0.6325     0.0622  5
  max valid BA                0.6513      0.6325     0.0607  5
  best valid F1               0.5545      0.5455     0.0679  5
  test BA                     0.6032      0.6124     0.0372  5
  test F1                     0.4747      0.5000     0.0611  5
  test sensitivity            0.5043      0.5217     0.0902  5
  test specificity            0.7021      0.7234     0.0398  5
  test precision              0.4514      0.4483     0.0399  5
  test loss                   0.6813      0.6834     0.0069  5
  FPR (FP/(FP+TN))            0.2979      0.2766     0.0398  5
  FNR (FN/(FN+TP))            0.4957      0.4783     0.0902  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8037      0.7894     0.0206  5
  max valid BA                0.8079      0.7894     0.0264  5
  best valid F1               0.7368      0.7170     0.0330  5
  test BA                     0.7957      0.7956     0.0243  5
  test F1                     0.7191      0.7200     0.0291  5
  test sensitivity            0.7913      0.7826     0.0567  5
  test specificity            0.8000      0.8085     0.0356  5
  test precision              0.6610      0.6667     0.0335  5
  test loss                   0.6646      0.6705     0.0229  5
  FPR (FP/(FP+TN))            0.2000      0.1915     0.0356  5
  FNR (FN/(FN+TP))            0.2087      0.2174     0.0567  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5244      0.5000     0.0357  5
  max valid BA                0.5347      0.5377     0.0338  5
  best valid F1               0.4998      0.4800     0.0985  5
  test BA                     0.4909      0.5000     0.0470  5
  test F1                     0.3932      0.5135     0.2446  5
  test sensitivity            0.5323      0.5846     0.3910  5
  test specificity            0.4494      0.4944     0.3732  5
  test precision              0.4053      0.4229     0.0608  4
  test loss                   0.6988      0.6969     0.0101  5
  FPR (FP/(FP+TN))            0.5506      0.5056     0.3732  5
  FNR (FN/(FN+TP))            0.4677      0.4154     0.3910  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5861      0.6042     0.0516  5
  max valid BA                0.5958      0.6042     0.0624  5
  best valid F1               0.4940      0.5528     0.1164  5
  test BA                     0.5583      0.5694     0.0293  5
  test F1                     0.4670      0.4660     0.0624  5
  test sensitivity            0.6500      0.6667     0.2337  5
  test specificity            0.4667      0.4306     0.2164  5
  test precision              0.3878      0.3804     0.0440  5
  test loss                   0.6912      0.6933     0.0041  5
  FPR (FP/(FP+TN))            0.5333      0.5694     0.2164  5
  FNR (FN/(FN+TP))            0.3500      0.3333     0.2337  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6324      0.6471     0.0345  5
  max valid BA                0.6353      0.6471     0.0381  5
  best valid F1               0.5589      0.5652     0.0299  5
  test BA                     0.5853      0.5588     0.0627  5
  test F1                     0.5143      0.5172     0.0587  5
  test sensitivity            0.7412      0.7647     0.1220  5
  test specificity            0.4294      0.4118     0.1373  5
  test precision              0.3975      0.3846     0.0532  5
  test loss                   0.6925      0.6914     0.0050  5
  FPR (FP/(FP+TN))            0.5706      0.5882     0.1373  5
  FNR (FN/(FN+TP))            0.2588      0.2353     0.1220  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.540         0.519         4         0.340              0.381
   CRAL-TRIO     1   129   67             0.799    0.586         0.627         4         0.551              0.568
   CRAL-TRIO     2   129   67             0.793    0.491         0.477         4         0.472              0.451
   CRAL-TRIO     3   129   67             0.806    0.596         0.609         4         0.469              0.466
   CRAL-TRIO     4   129   67             0.804    0.484         0.538         4         0.433              0.507
        GLTP     0    52   26             0.618    0.586         0.552         2         0.492              0.500
        GLTP     1    52   26             0.601    0.496         0.501         2         0.558              0.500
        GLTP     2    52   26             0.618    0.525         0.486         2         0.547              0.483
        GLTP     3    52   26             0.619    0.531         0.477         2         0.589              0.500
        GLTP     4    52   26             0.621    0.530         0.513         2         0.495              0.509
    IP_trans     0    71   24             0.809    0.712         0.707         3         0.761              0.748
    IP_trans     1    71   24             0.808    0.667         0.681         3         0.720              0.717
    IP_trans     2    71   24             0.810    0.574         0.559         3         0.739              0.784
    IP_trans     3    71   24             0.811    0.629         0.597         3         0.588              0.591
    IP_trans     4    71   24             0.808    0.545         0.570         3         0.623              0.677
LBP_BPI_CETP     0    71   24             0.809    0.805         0.783         2         0.719              0.701
LBP_BPI_CETP     1    71   24             0.816    0.873         0.851         2         0.601              0.675
LBP_BPI_CETP     2    71   24             0.808    0.840         0.832         2         0.623              0.625
LBP_BPI_CETP     3    71   24             0.807    0.769         0.758         2         0.812              0.814
LBP_BPI_CETP     4    71   24             0.804    0.793         0.823         2         0.769              0.764
       START     0   153   64             0.791    0.452         0.417         3         0.508              0.479
       START     1   153   64             0.784    0.516         0.509         3         0.454              0.439
       START     2   153   64             0.794    0.410         0.403         3         0.525              0.558
       START     3   153   64             0.797    0.603         0.565         3         0.596              0.608
       START     4   153   64             0.779    0.500         0.467         3         0.441              0.460
   lipocalin     0   108   36             0.847    0.475         0.378         5         0.605              0.655
   lipocalin     1   108   36             0.827    0.598         0.696         5         0.284              0.217
   lipocalin     2   108   36             0.829    0.623         0.566         5         0.585              0.548
   lipocalin     3   108   36             0.846    0.710         0.747         5         0.352              0.289
   lipocalin     4   108   36             0.810    0.533         0.564         5         0.541              0.463
        scp2     0    51   17             0.808    0.720         0.751         2         0.666              0.619
        scp2     1    51   17             0.837    0.665         0.680         3         0.693              0.626
        scp2     2    51   17             0.851    0.578         0.407         3         0.536              0.417
        scp2     3    51   17             0.842    0.619         0.576         3         0.668              0.576
        scp2     4    51   17             0.834    0.606         0.608         3         0.580              0.405

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.539         0.554       4.0         0.453              0.475
GLTP           52.0  26.0             0.615    0.533         0.506       2.0         0.536              0.499
IP_trans       71.0  24.0             0.809    0.625         0.623       3.0         0.686              0.703
LBP_BPI_CETP   71.0  24.0             0.809    0.816         0.809       2.0         0.705              0.716
START         153.0  64.0             0.789    0.496         0.472       3.0         0.505              0.509
lipocalin     108.0  36.0             0.832    0.588         0.590       5.0         0.473              0.434
scp2           51.0  17.0             0.834    0.638         0.604       2.8         0.629              0.529

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.605          0.693       0.539
null_AUC_k15      0.570          0.673       0.492

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.594          0.679       0.530
null_AUC_prot_k15      0.552          0.649       0.479

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.445      0.552     0.458
10     0.57  0.551      0.552     0.559
49     0.57  0.608      0.552     0.601
51     0.57  0.607      0.552     0.600
120    0.57  0.605      0.552     0.594

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.651      0.044          0.657              0.691           0.034
10        0.607         0.655      0.048          0.657              0.691           0.034
49        0.607         0.658      0.051          0.657              0.696           0.039
51        0.607         0.658      0.051          0.657              0.696           0.040
120       0.607         0.648      0.042          0.657              0.696           0.039

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.539      0.475     0.554      0.007           0.028
GLTP          0.536  0.533      0.499     0.506      0.038           0.014
IP_trans      0.686  0.625      0.703     0.623     -0.006          -0.005
LBP_BPI_CETP  0.705  0.816      0.716     0.809      0.129           0.114
START         0.505  0.496      0.509     0.472      0.038           0.028
lipocalin     0.473  0.588      0.434     0.590      0.061           0.074
scp2          0.629  0.638      0.529     0.604      0.024           0.020

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.605          0.693       0.539      0.638
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.594          0.679       0.530      0.604
increment           0.042          0.049       0.036      0.024
increment_prot      0.039          0.043       0.036      0.020
```
