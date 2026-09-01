# descriptors_no_extent_coarse_add_lipprop_lr001

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_add_lipprop_lr001'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6209      0.5148      0.5920      0.4744      0.6567      0.5194
groups_GLTP            5      0.5440      0.4880      0.5860      0.4702      0.5308      0.5846
groups_IP_trans        5      0.6435      0.5660      0.6193      0.4590      0.7250      0.5617
groups_LBP_BPI_CETP    5      0.7913      0.8383      0.6505      0.4593      0.8250      0.7660
groups_START           5      0.6062      0.3955      0.5597      0.5014      0.6250      0.4202
groups_lipocalin       5      0.7944      0.5139      0.5144      0.5581      0.7944      0.5167
groups_scp2            5      0.6824      0.5176      0.5798      0.4968      0.6941      0.6235
ALL                   35      0.6689      0.5477      0.5860      0.4884      0.6930      0.5703

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6316      0.6250     0.0929  35
max valid BA                0.6616      0.6520     0.0919  35
best valid F1               0.6363      0.6500     0.0764  35
test BA                     0.6083      0.5814     0.1095  35
test F1                     0.5551      0.5814     0.1295  35
test sensitivity            0.6689      0.7200     0.2135  35
test specificity            0.5477      0.5532     0.2101  35
test precision              0.5016      0.4815     0.1219  35
test loss                   0.6861      0.6916     0.0164  35
FPR (FP/(FP+TN))            0.4523      0.4468     0.2101  35
FNR (FN/(FN+TP))            0.3311      0.2800     0.2135  35

=== abs(sensitivity-specificity) gap: mean=0.2956 median=0.2400 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5880      0.5725     0.0386  5
  max valid BA                0.6205      0.6237     0.0465  5
  best valid F1               0.6949      0.6839     0.0173  5
  test BA                     0.5678      0.5793     0.0221  5
  test F1                     0.5920      0.5821     0.0727  5
  test sensitivity            0.6209      0.5821     0.1811  5
  test specificity            0.5148      0.5410     0.2101  5
  test precision              0.5947      0.5882     0.0393  5
  test loss                   0.6909      0.6916     0.0051  5
  FPR (FP/(FP+TN))            0.4852      0.4590     0.2101  5
  FNR (FN/(FN+TP))            0.3791      0.4179     0.1811  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5577      0.5385     0.0360  5
  max valid BA                0.5962      0.5769     0.0272  5
  best valid F1               0.6526      0.6761     0.0640  5
  test BA                     0.5160      0.5200     0.0385  5
  test F1                     0.5055      0.5000     0.1308  5
  test sensitivity            0.5440      0.4400     0.2677  5
  test specificity            0.4880      0.6400     0.2423  5
  test precision              0.5114      0.5111     0.0512  5
  test loss                   0.6955      0.6941     0.0033  5
  FPR (FP/(FP+TN))            0.5120      0.3600     0.2423  5
  FNR (FN/(FN+TP))            0.4560      0.5600     0.2677  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6434      0.6520     0.0688  5
  max valid BA                0.6586      0.6520     0.0694  5
  best valid F1               0.5796      0.5667     0.0604  5
  test BA                     0.6047      0.5920     0.0536  5
  test F1                     0.5085      0.5000     0.0581  5
  test sensitivity            0.6435      0.6522     0.0778  5
  test specificity            0.5660      0.5532     0.0490  5
  test precision              0.4208      0.4054     0.0488  5
  test loss                   0.6827      0.6861     0.0105  5
  FPR (FP/(FP+TN))            0.4340      0.4468     0.0490  5
  FNR (FN/(FN+TP))            0.3565      0.3478     0.0778  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7955      0.7996     0.0381  5
  max valid BA                0.8085      0.8001     0.0203  5
  best valid F1               0.7416      0.7308     0.0259  5
  test BA                     0.8148      0.8275     0.0300  5
  test F1                     0.7465      0.7500     0.0408  5
  test sensitivity            0.7913      0.7826     0.0836  5
  test specificity            0.8383      0.8298     0.0715  5
  test precision              0.7163      0.6786     0.0856  5
  test loss                   0.6530      0.6534     0.0141  5
  FPR (FP/(FP+TN))            0.1617      0.1702     0.0715  5
  FNR (FN/(FN+TP))            0.2087      0.2174     0.0836  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5226      0.5474     0.0496  5
  max valid BA                0.5416      0.5474     0.0473  5
  best valid F1               0.5500      0.5630     0.0532  5
  test BA                     0.5008      0.5183     0.0494  5
  test F1                     0.4623      0.5298     0.1547  5
  test sensitivity            0.6062      0.6154     0.3455  5
  test specificity            0.3955      0.4831     0.2987  5
  test precision              0.4132      0.4315     0.0519  5
  test loss                   0.7001      0.7034     0.0100  5
  FPR (FP/(FP+TN))            0.6045      0.5169     0.2987  5
  FNR (FN/(FN+TP))            0.3938      0.3846     0.3455  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6556      0.6389     0.0301  5
  max valid BA                0.6972      0.7014     0.0541  5
  best valid F1               0.6132      0.6200     0.0568  5
  test BA                     0.6542      0.6736     0.0612  5
  test F1                     0.5725      0.5814     0.0613  5
  test sensitivity            0.7944      0.8333     0.1425  5
  test specificity            0.5139      0.5139     0.1107  5
  test precision              0.4519      0.4615     0.0475  5
  test loss                   0.6906      0.6918     0.0031  5
  FPR (FP/(FP+TN))            0.4861      0.4861     0.1107  5
  FNR (FN/(FN+TP))            0.2056      0.1667     0.1425  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6588      0.6471     0.0408  5
  max valid BA                0.7088      0.6912     0.0408  5
  best valid F1               0.6221      0.6122     0.0463  5
  test BA                     0.6000      0.6176     0.0828  5
  test F1                     0.4985      0.5417     0.1377  5
  test sensitivity            0.6824      0.7647     0.2516  5
  test specificity            0.5176      0.5000     0.1420  5
  test precision              0.4033      0.4194     0.0761  5
  test loss                   0.6896      0.6905     0.0047  5
  FPR (FP/(FP+TN))            0.4824      0.5000     0.1420  5
  FNR (FN/(FN+TP))            0.3176      0.2353     0.2516  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.605         0.623         4         0.340              0.381
   CRAL-TRIO     1   129   67             0.799    0.330         0.394         4         0.551              0.568
   CRAL-TRIO     2   129   67             0.793    0.543         0.507         4         0.472              0.451
   CRAL-TRIO     3   129   67             0.806    0.661         0.626         4         0.469              0.466
   CRAL-TRIO     4   129   67             0.804    0.500         0.500         4         0.433              0.507
        GLTP     0    52   26             0.618    0.354         0.500         2         0.492              0.500
        GLTP     1    52   26             0.601    0.546         0.493         2         0.558              0.500
        GLTP     2    52   26             0.618    0.524         0.491         2         0.547              0.483
        GLTP     3    52   26             0.619    0.512         0.496         2         0.589              0.500
        GLTP     4    52   26             0.621    0.500         0.500         2         0.495              0.509
    IP_trans     0    71   24             0.809    0.664         0.654         3         0.761              0.748
    IP_trans     1    71   24             0.808    0.651         0.668         3         0.720              0.717
    IP_trans     2    71   24             0.810    0.572         0.559         3         0.739              0.784
    IP_trans     3    71   24             0.811    0.613         0.593         3         0.588              0.591
    IP_trans     4    71   24             0.808    0.521         0.579         3         0.623              0.677
LBP_BPI_CETP     0    71   24             0.809    0.627         0.642         2         0.719              0.701
LBP_BPI_CETP     1    71   24             0.816    0.804         0.805         2         0.601              0.675
LBP_BPI_CETP     2    71   24             0.808    0.829         0.818         2         0.623              0.625
LBP_BPI_CETP     3    71   24             0.807    0.775         0.764         2         0.812              0.814
LBP_BPI_CETP     4    71   24             0.804    0.876         0.887         2         0.769              0.764
       START     0   153   64             0.791    0.418         0.470         3         0.508              0.479
       START     1   153   64             0.784    0.479         0.479         3         0.454              0.439
       START     2   153   64             0.794    0.344         0.382         3         0.525              0.558
       START     3   153   64             0.797    0.560         0.568         3         0.596              0.608
       START     4   153   64             0.779    0.460         0.484         3         0.441              0.460
   lipocalin     0   108   36             0.847    0.500         0.500         5         0.605              0.655
   lipocalin     1   108   36             0.827    0.604         0.649         5         0.284              0.217
   lipocalin     2   108   36             0.829    0.699         0.818         5         0.585              0.548
   lipocalin     3   108   36             0.846    0.700         0.772         5         0.352              0.289
   lipocalin     4   108   36             0.810    0.500         0.500         5         0.541              0.463
        scp2     0    51   17             0.808    0.694         0.691         2         0.666              0.619
        scp2     1    51   17             0.837    0.606         0.575         3         0.693              0.626
        scp2     2    51   17             0.851    0.588         0.530         3         0.536              0.417
        scp2     3    51   17             0.842    0.618         0.587         3         0.668              0.576
        scp2     4    51   17             0.834    0.583         0.619         3         0.580              0.405

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.528         0.530       4.0         0.453              0.475
GLTP           52.0  26.0             0.615    0.487         0.496       2.0         0.536              0.499
IP_trans       71.0  24.0             0.809    0.604         0.611       3.0         0.686              0.703
LBP_BPI_CETP   71.0  24.0             0.809    0.782         0.783       2.0         0.705              0.716
START         153.0  64.0             0.789    0.452         0.477       3.0         0.505              0.509
lipocalin     108.0  36.0             0.832    0.601         0.648       5.0         0.473              0.434
scp2           51.0  17.0             0.834    0.618         0.601       2.8         0.629              0.529

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.582          0.668       0.517
null_AUC_k15      0.570          0.673       0.492

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.592          0.665       0.538
null_AUC_prot_k15      0.552          0.649       0.479

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.557      0.552     0.555
10     0.57  0.590      0.552     0.575
49     0.57  0.606      0.552     0.612
51     0.57  0.602      0.552     0.599
120    0.57  0.582      0.552     0.592

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.655      0.049          0.657              0.697           0.041
10        0.607         0.659      0.053          0.657              0.694           0.037
49        0.607         0.668      0.061          0.657              0.703           0.047
51        0.607         0.665      0.058          0.657              0.699           0.042
120       0.607         0.643      0.037          0.657              0.688           0.032

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.528      0.475     0.530      0.046           0.028
GLTP          0.536  0.487      0.499     0.496      0.007           0.031
IP_trans      0.686  0.604      0.703     0.611     -0.007          -0.002
LBP_BPI_CETP  0.705  0.782      0.716     0.783      0.084           0.066
START         0.505  0.452      0.509     0.477      0.051           0.028
lipocalin     0.473  0.601      0.434     0.648      0.040           0.064
scp2          0.629  0.618      0.529     0.601      0.036           0.007

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.582          0.668       0.517      0.618
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.592          0.665       0.538      0.601
increment           0.037          0.037       0.036      0.036
increment_prot      0.032          0.024       0.038      0.007
```
