# descriptors_no_extent_coarse_pool_max

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_pool_max'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5313      0.5475      0.6480      0.4487      0.5642      0.5774
groups_GLTP            5      0.5280      0.4000      0.7236      0.3853      0.6308      0.4692
groups_IP_trans        5      0.5391      0.6851      0.6176      0.4972      0.5583      0.6936
groups_LBP_BPI_CETP    5      0.8087      0.8596      0.6861      0.4613      0.8083      0.8213
groups_START           5      0.2738      0.6944      0.4109      0.6396      0.2969      0.7326
groups_lipocalin       5      0.5611      0.6361      0.5657      0.5547      0.6278      0.6361
groups_scp2            5      0.8000      0.3000      0.5716      0.5252      0.8000      0.4118
ALL                   35      0.5774      0.5890      0.6034      0.5017      0.6123      0.6203

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6169      0.5873     0.1012  35
max valid BA                0.6240      0.6029     0.1006  35
best valid F1               0.5803      0.5882     0.1207  35
test BA                     0.5832      0.5556     0.1278  35
test F1                     0.4877      0.5091     0.1992  35
test sensitivity            0.5774      0.6087     0.2932  35
test specificity            0.5890      0.6111     0.2787  35
test precision              0.5089      0.4667     0.1607  33
test loss                   0.6760      0.6843     0.0303  35
FPR (FP/(FP+TN))            0.4110      0.3889     0.2787  35
FNR (FN/(FN+TP))            0.4226      0.3913     0.2932  35

=== abs(sensitivity-specificity) gap: mean=0.3888 median=0.2112 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5708      0.5697     0.0423  5
  max valid BA                0.5739      0.5802     0.0406  5
  best valid F1               0.6062      0.6369     0.0942  5
  test BA                     0.5394      0.5494     0.0590  5
  test F1                     0.5273      0.4462     0.1252  5
  test sensitivity            0.5313      0.4328     0.2357  5
  test specificity            0.5475      0.4754     0.2076  5
  test precision              0.5681      0.5897     0.0620  5
  test loss                   0.6883      0.6903     0.0067  5
  FPR (FP/(FP+TN))            0.4525      0.5246     0.2076  5
  FNR (FN/(FN+TP))            0.4687      0.5672     0.2357  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5538      0.5577     0.0370  5
  max valid BA                0.5577      0.5577     0.0430  5
  best valid F1               0.6199      0.6667     0.0682  5
  test BA                     0.4640      0.4600     0.0297  5
  test F1                     0.4667      0.4528     0.1428  5
  test sensitivity            0.5280      0.4800     0.2958  5
  test specificity            0.4000      0.3600     0.2698  5
  test precision              0.4576      0.4667     0.0344  5
  test loss                   0.6990      0.6980     0.0047  5
  FPR (FP/(FP+TN))            0.6000      0.6400     0.2698  5
  FNR (FN/(FN+TP))            0.4720      0.5200     0.2958  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6260      0.6210     0.0581  5
  max valid BA                0.6324      0.6529     0.0591  5
  best valid F1               0.5308      0.5556     0.0791  5
  test BA                     0.6121      0.6230     0.0667  5
  test F1                     0.4777      0.5098     0.1227  5
  test sensitivity            0.5391      0.5652     0.2053  5
  test specificity            0.6851      0.6809     0.1002  5
  test precision              0.4502      0.4643     0.0470  5
  test loss                   0.6715      0.6719     0.0085  5
  FPR (FP/(FP+TN))            0.3149      0.3191     0.1002  5
  FNR (FN/(FN+TP))            0.4609      0.4348     0.2053  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8148      0.8001     0.0355  5
  max valid BA                0.8168      0.8001     0.0332  5
  best valid F1               0.7519      0.7308     0.0445  5
  test BA                     0.8341      0.8284     0.0357  5
  test F1                     0.7710      0.7547     0.0435  5
  test sensitivity            0.8087      0.8261     0.0902  5
  test specificity            0.8596      0.8723     0.0512  5
  test precision              0.7436      0.7391     0.0580  5
  test loss                   0.6109      0.6258     0.0239  5
  FPR (FP/(FP+TN))            0.1404      0.1277     0.0512  5
  FNR (FN/(FN+TP))            0.1913      0.1739     0.0902  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5147      0.5012     0.0251  5
  max valid BA                0.5162      0.5012     0.0273  5
  best valid F1               0.4949      0.4595     0.1010  5
  test BA                     0.4841      0.5000     0.0475  5
  test F1                     0.2141      0.2326     0.2444  5
  test sensitivity            0.2738      0.1538     0.4169  5
  test specificity            0.6944      0.8764     0.4180  5
  test precision              0.3918      0.4248     0.1048  3
  test loss                   0.6920      0.6858     0.0111  5
  FPR (FP/(FP+TN))            0.3056      0.1236     0.4180  5
  FNR (FN/(FN+TP))            0.7262      0.8462     0.4169  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6319      0.6458     0.0689  5
  max valid BA                0.6361      0.6458     0.0701  5
  best valid F1               0.5051      0.5607     0.1745  5
  test BA                     0.5986      0.5694     0.0777  5
  test F1                     0.4536      0.4545     0.1516  5
  test sensitivity            0.5611      0.5556     0.3139  5
  test specificity            0.6361      0.5694     0.2126  5
  test precision              0.5313      0.4561     0.2666  5
  test loss                   0.6789      0.6801     0.0055  5
  FPR (FP/(FP+TN))            0.3639      0.4306     0.2125  5
  FNR (FN/(FN+TP))            0.4389      0.4444     0.3139  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6059      0.5882     0.0610  5
  max valid BA                0.6353      0.6176     0.0481  5
  best valid F1               0.5535      0.5357     0.0407  5
  test BA                     0.5500      0.5588     0.0816  5
  test F1                     0.5032      0.5172     0.0581  5
  test sensitivity            0.8000      0.8824     0.1147  5
  test specificity            0.3000      0.2941     0.2021  5
  test precision              0.3728      0.3659     0.0670  5
  test loss                   0.6915      0.6927     0.0116  5
  FPR (FP/(FP+TN))            0.7000      0.7059     0.2021  5
  FNR (FN/(FN+TP))            0.2000      0.1176     0.1147  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.505         0.466         4         0.340              0.381
   CRAL-TRIO     1   129   67             0.799    0.430         0.421         4         0.551              0.568
   CRAL-TRIO     2   129   67             0.793    0.561         0.516         4         0.472              0.451
   CRAL-TRIO     3   129   67             0.806    0.620         0.496         4         0.469              0.466
   CRAL-TRIO     4   129   67             0.804    0.474         0.437         4         0.433              0.507
        GLTP     0    52   26             0.618    0.522         0.468         2         0.492              0.500
        GLTP     1    52   26             0.601    0.531         0.529         2         0.558              0.500
        GLTP     2    52   26             0.618    0.516         0.486         2         0.547              0.483
        GLTP     3    52   26             0.619    0.501         0.464         2         0.589              0.500
        GLTP     4    52   26             0.621    0.510         0.500         2         0.495              0.509
    IP_trans     0    71   24             0.809    0.686         0.671         3         0.761              0.748
    IP_trans     1    71   24             0.808    0.699         0.725         3         0.720              0.717
    IP_trans     2    71   24             0.810    0.597         0.605         3         0.739              0.784
    IP_trans     3    71   24             0.811    0.609         0.609         3         0.588              0.591
    IP_trans     4    71   24             0.808    0.547         0.564         3         0.623              0.677
LBP_BPI_CETP     0    71   24             0.809    0.781         0.769         2         0.719              0.701
LBP_BPI_CETP     1    71   24             0.816    0.872         0.867         2         0.601              0.675
LBP_BPI_CETP     2    71   24             0.808    0.807         0.805         2         0.623              0.625
LBP_BPI_CETP     3    71   24             0.807    0.796         0.792         2         0.812              0.814
LBP_BPI_CETP     4    71   24             0.804    0.808         0.820         2         0.769              0.764
       START     0   153   64             0.791    0.436         0.447         3         0.508              0.479
       START     1   153   64             0.784    0.471         0.485         3         0.454              0.439
       START     2   153   64             0.794    0.382         0.418         3         0.525              0.558
       START     3   153   64             0.797    0.614         0.587         3         0.596              0.608
       START     4   153   64             0.779    0.470         0.479         3         0.441              0.460
   lipocalin     0   108   36             0.847    0.380         0.305         5         0.605              0.655
   lipocalin     1   108   36             0.827    0.647         0.659         5         0.284              0.217
   lipocalin     2   108   36             0.829    0.510         0.471         5         0.585              0.548
   lipocalin     3   108   36             0.846    0.608         0.623         5         0.352              0.289
   lipocalin     4   108   36             0.810    0.617         0.739         5         0.541              0.463
        scp2     0    51   17             0.808    0.569         0.591         2         0.666              0.619
        scp2     1    51   17             0.837    0.548         0.461         3         0.693              0.626
        scp2     2    51   17             0.851    0.602         0.547         3         0.536              0.417
        scp2     3    51   17             0.842    0.600         0.527         3         0.668              0.576
        scp2     4    51   17             0.834    0.667         0.631         3         0.580              0.405

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.518         0.467       4.0         0.453              0.475
GLTP           52.0  26.0             0.615    0.516         0.489       2.0         0.536              0.499
IP_trans       71.0  24.0             0.809    0.627         0.635       3.0         0.686              0.703
LBP_BPI_CETP   71.0  24.0             0.809    0.813         0.811       2.0         0.705              0.716
START         153.0  64.0             0.789    0.475         0.483       3.0         0.505              0.509
lipocalin     108.0  36.0             0.832    0.553         0.559       5.0         0.473              0.434
scp2           51.0  17.0             0.834    0.597         0.551       2.8         0.629              0.529

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.586          0.679       0.515
null_AUC_k15      0.570          0.673       0.492

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.571          0.666       0.500
null_AUC_prot_k15      0.552          0.649       0.479

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.522      0.552     0.521
10     0.57  0.583      0.552     0.579
49     0.57  0.591      0.552     0.580
51     0.57  0.592      0.552     0.580
120    0.57  0.586      0.552     0.571

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.644      0.038          0.657              0.690           0.033
10        0.607         0.655      0.048          0.657              0.688           0.032
49        0.607         0.649      0.042          0.657              0.689           0.033
51        0.607         0.648      0.041          0.657              0.688           0.032
120       0.607         0.651      0.044          0.657              0.689           0.032

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.518      0.475     0.467      0.018           0.024
GLTP          0.536  0.516      0.499     0.489      0.013          -0.001
IP_trans      0.686  0.627      0.703     0.635     -0.001          -0.002
LBP_BPI_CETP  0.705  0.813      0.716     0.811      0.131           0.108
START         0.505  0.475      0.509     0.483      0.039           0.015
lipocalin     0.473  0.553      0.434     0.559      0.067           0.062
scp2          0.629  0.597      0.529     0.551      0.043           0.017

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.586          0.679       0.515      0.597
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.571          0.666       0.500      0.551
increment           0.044          0.058       0.034      0.043
increment_prot      0.032          0.041       0.025      0.017
```
