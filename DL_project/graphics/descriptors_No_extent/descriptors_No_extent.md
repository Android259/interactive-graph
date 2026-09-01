# descriptors_No_extent

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_No_extent'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4627      0.7016         n/a         n/a         n/a         n/a
groups_GLTP            5      0.5040      0.4240         n/a         n/a         n/a         n/a
groups_IP_trans        5      0.5913      0.6723         n/a         n/a         n/a         n/a
groups_LBP_BPI_CETP    5      0.8348      0.8000         n/a         n/a         n/a         n/a
groups_START           5      0.3969      0.6270         n/a         n/a         n/a         n/a
groups_lipocalin       5      0.6611      0.5556         n/a         n/a         n/a         n/a
groups_scp2            5      0.5882      0.6706         n/a         n/a         n/a         n/a
ALL                   35      0.5770      0.6359         n/a         n/a         n/a         n/a

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6365      0.6215     0.0911  35
max valid BA                0.6419      0.6334     0.0920  35
best valid F1               0.5897      0.5854     0.1074  35
test BA                     0.6064      0.6226     0.1138  35
test F1                     0.5178      0.5294     0.1516  35
test sensitivity            0.5770      0.5556     0.2389  35
test specificity            0.6359      0.6809     0.2073  35
test precision              0.5171      0.4914     0.1055  34
test loss                   0.6829      0.6871     0.0178  35
FPR (FP/(FP+TN))            0.3641      0.3191     0.2073  35
FNR (FN/(FN+TP))            0.4230      0.4444     0.2389  35

=== abs(sensitivity-specificity) gap: mean=0.2771 median=0.2017 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6075      0.6029     0.0496  5
  max valid BA                0.6124      0.6178     0.0482  5
  best valid F1               0.6344      0.6202     0.0647  5
  test BA                     0.5822      0.5614     0.0457  5
  test F1                     0.5254      0.4956     0.1015  5
  test sensitivity            0.4627      0.4179     0.1347  5
  test specificity            0.7016      0.7049     0.0469  5
  test precision              0.6238      0.6087     0.0348  5
  test loss                   0.6901      0.6910     0.0040  5
  FPR (FP/(FP+TN))            0.2984      0.2951     0.0469  5
  FNR (FN/(FN+TP))            0.5373      0.5821     0.1347  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5654      0.5577     0.0322  5
  max valid BA                0.5731      0.5577     0.0417  5
  best valid F1               0.5872      0.6667     0.1310  5
  test BA                     0.4640      0.4600     0.0456  5
  test F1                     0.4598      0.4255     0.1312  5
  test sensitivity            0.5040      0.4000     0.2851  5
  test specificity            0.4240      0.5200     0.2128  5
  test precision              0.4539      0.4444     0.0397  5
  test loss                   0.6977      0.6960     0.0056  5
  FPR (FP/(FP+TN))            0.5760      0.4800     0.2128  5
  FNR (FN/(FN+TP))            0.4960      0.6000     0.2851  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6445      0.6423     0.0663  5
  max valid BA                0.6487      0.6423     0.0681  5
  best valid F1               0.5653      0.5455     0.0522  5
  test BA                     0.6318      0.6240     0.0116  5
  test F1                     0.5228      0.5263     0.0146  5
  test sensitivity            0.5913      0.6087     0.0496  5
  test specificity            0.6723      0.6809     0.0555  5
  test precision              0.4711      0.4800     0.0241  5
  test loss                   0.6755      0.6730     0.0106  5
  FPR (FP/(FP+TN))            0.3277      0.3191     0.0555  5
  FNR (FN/(FN+TP))            0.4087      0.3913     0.0496  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8018      0.7988     0.0275  5
  max valid BA                0.8081      0.7988     0.0340  5
  best valid F1               0.7399      0.7213     0.0459  5
  test BA                     0.8174      0.8178     0.0297  5
  test F1                     0.7440      0.7407     0.0343  5
  test sensitivity            0.8348      0.8696     0.0714  5
  test specificity            0.8000      0.7660     0.0490  5
  test precision              0.6751      0.6562     0.0496  5
  test loss                   0.6536      0.6479     0.0231  5
  FPR (FP/(FP+TN))            0.2000      0.2340     0.0490  5
  FNR (FN/(FN+TP))            0.1652      0.1304     0.0714  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5441      0.5358     0.0434  5
  max valid BA                0.5495      0.5607     0.0438  5
  best valid F1               0.4996      0.4706     0.0874  5
  test BA                     0.5119      0.5000     0.0588  5
  test F1                     0.3482      0.3579     0.2174  5
  test sensitivity            0.3969      0.3538     0.3682  5
  test specificity            0.6270      0.7978     0.3980  5
  test precision              0.4731      0.4915     0.1096  4
  test loss                   0.6963      0.6884     0.0119  5
  FPR (FP/(FP+TN))            0.3730      0.2022     0.3980  5
  FNR (FN/(FN+TP))            0.6031      0.6462     0.3682  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6125      0.6319     0.0424  5
  max valid BA                0.6194      0.6389     0.0497  5
  best valid F1               0.5093      0.5432     0.1070  5
  test BA                     0.6083      0.6250     0.0603  5
  test F1                     0.5056      0.5490     0.0940  5
  test sensitivity            0.6611      0.6667     0.2393  5
  test specificity            0.5556      0.5139     0.1687  5
  test precision              0.4287      0.4268     0.0483  5
  test loss                   0.6849      0.6889     0.0103  5
  FPR (FP/(FP+TN))            0.4444      0.4861     0.1687  5
  FNR (FN/(FN+TP))            0.3389      0.3333     0.2393  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6794      0.6765     0.0534  5
  max valid BA                0.6824      0.6765     0.0526  5
  best valid F1               0.5923      0.5789     0.0550  5
  test BA                     0.6294      0.6471     0.0583  5
  test F1                     0.5186      0.5333     0.0772  5
  test sensitivity            0.5882      0.5294     0.1715  5
  test specificity            0.6706      0.6471     0.1370  5
  test precision              0.4849      0.4667     0.0929  5
  test loss                   0.6823      0.6794     0.0064  5
  FPR (FP/(FP+TN))            0.3294      0.3529     0.1370  5
  FNR (FN/(FN+TP))            0.4118      0.4706     0.1715  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.533         0.518         4         0.340              0.381
   CRAL-TRIO     1   129   67             0.799    0.597         0.571         4         0.551              0.568
   CRAL-TRIO     2   129   67             0.793    0.529         0.485         4         0.472              0.451
   CRAL-TRIO     3   129   67             0.806    0.654         0.596         4         0.469              0.466
   CRAL-TRIO     4   129   67             0.804    0.539         0.532         4         0.433              0.507
        GLTP     0    52   26             0.618    0.581         0.561         2         0.492              0.500
        GLTP     1    52   26             0.601    0.494         0.499         2         0.558              0.500
        GLTP     2    52   26             0.618    0.513         0.496         2         0.547              0.483
        GLTP     3    52   26             0.619    0.513         0.490         2         0.589              0.500
        GLTP     4    52   26             0.621    0.503         0.516         2         0.495              0.509
    IP_trans     0    71   24             0.809    0.691         0.686         3         0.761              0.748
    IP_trans     1    71   24             0.808    0.665         0.683         3         0.720              0.717
    IP_trans     2    71   24             0.810    0.579         0.561         3         0.739              0.784
    IP_trans     3    71   24             0.811    0.627         0.597         3         0.588              0.591
    IP_trans     4    71   24             0.808    0.547         0.570         3         0.623              0.677
LBP_BPI_CETP     0    71   24             0.809    0.800         0.773         2         0.719              0.701
LBP_BPI_CETP     1    71   24             0.816    0.866         0.842         2         0.601              0.675
LBP_BPI_CETP     2    71   24             0.808    0.839         0.837         2         0.623              0.625
LBP_BPI_CETP     3    71   24             0.807    0.768         0.742         2         0.812              0.814
LBP_BPI_CETP     4    71   24             0.804    0.816         0.821         2         0.769              0.764
       START     0   153   64             0.791    0.417         0.420         3         0.508              0.479
       START     1   153   64             0.784    0.484         0.486         3         0.454              0.439
       START     2   153   64             0.794    0.364         0.407         3         0.525              0.558
       START     3   153   64             0.797    0.547         0.564         3         0.596              0.608
       START     4   153   64             0.779    0.432         0.467         3         0.441              0.460
   lipocalin     0   108   36             0.847    0.463         0.395         5         0.605              0.655
   lipocalin     1   108   36             0.827    0.587         0.602         5         0.284              0.217
   lipocalin     2   108   36             0.829    0.654         0.603         5         0.585              0.548
   lipocalin     3   108   36             0.846    0.689         0.731         5         0.352              0.289
   lipocalin     4   108   36             0.810    0.552         0.583         5         0.541              0.463
        scp2     0    51   17             0.808    0.678         0.708         2         0.666              0.619
        scp2     1    51   17             0.837    0.669         0.716         3         0.693              0.626
        scp2     2    51   17             0.851    0.582         0.426         3         0.536              0.417
        scp2     3    51   17             0.842    0.647         0.587         3         0.668              0.576
        scp2     4    51   17             0.834    0.632         0.603         3         0.580              0.405

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.570         0.541       4.0         0.453              0.475
GLTP           52.0  26.0             0.615    0.521         0.512       2.0         0.536              0.499
IP_trans       71.0  24.0             0.809    0.622         0.619       3.0         0.686              0.703
LBP_BPI_CETP   71.0  24.0             0.809    0.818         0.803       2.0         0.705              0.716
START         153.0  64.0             0.789    0.449         0.469       3.0         0.505              0.509
lipocalin     108.0  36.0             0.832    0.589         0.583       5.0         0.473              0.434
scp2           51.0  17.0             0.834    0.642         0.608       2.8         0.629              0.529

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.601          0.694       0.532
null_AUC_k15      0.570          0.673       0.492

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.591          0.677       0.526
null_AUC_prot_k15      0.552          0.649       0.479

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.536      0.552     0.539
10     0.57  0.607      0.552     0.591
49     0.57  0.610      0.552     0.597
51     0.57  0.610      0.552     0.597
120    0.57  0.601      0.552     0.591

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.658      0.051          0.657              0.696           0.039
10        0.607         0.659      0.052          0.657              0.694           0.038
49        0.607         0.660      0.053          0.657              0.693           0.036
51        0.607         0.660      0.054          0.657              0.693           0.036
120       0.607         0.654      0.047          0.657              0.692           0.035

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.570      0.475     0.541      0.033           0.029
GLTP          0.536  0.521      0.499     0.512      0.027           0.017
IP_trans      0.686  0.622      0.703     0.619     -0.007          -0.003
LBP_BPI_CETP  0.705  0.818      0.716     0.803      0.125           0.100
START         0.505  0.449      0.509     0.469      0.038           0.018
lipocalin     0.473  0.589      0.434     0.583      0.084           0.072
scp2          0.629  0.642      0.529     0.608      0.027           0.013

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.601          0.694       0.532      0.642
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.591          0.677       0.526      0.608
increment           0.047          0.048       0.046      0.027
increment_prot      0.035          0.037       0.034      0.013
```
