# descriptors_no_extent_coarse_add_hid16

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_add_hid16'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5761      0.5672      0.5983      0.4787      0.5881      0.6323
groups_GLTP            5      0.3840      0.5520      0.5345      0.5571      0.4692      0.6615
groups_IP_trans        5      0.5478      0.5957      0.6997      0.4069      0.6250      0.6766
groups_LBP_BPI_CETP    5      0.8348      0.7362      0.6727      0.4552      0.8417      0.7574
groups_START           5      0.5785      0.4337      0.6410      0.3908      0.6188      0.4562
groups_lipocalin       5      0.4556      0.6944      0.6232      0.5028      0.5056      0.6806
groups_scp2            5      0.7059      0.4353      0.6305      0.4860      0.7647      0.4941
ALL                   35      0.5832      0.5735      0.6286      0.4682      0.6304      0.6227

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6265      0.6029     0.0914  35
max valid BA                0.6418      0.6324     0.0926  35
best valid F1               0.5962      0.5926     0.1004  35
test BA                     0.5784      0.5624     0.1058  35
test F1                     0.5071      0.5128     0.1215  35
test sensitivity            0.5832      0.5294     0.2075  35
test specificity            0.5735      0.5833     0.1792  35
test precision              0.4805      0.4545     0.1095  35
test loss                   0.6805      0.6853     0.0301  35
FPR (FP/(FP+TN))            0.4265      0.4167     0.1792  35
FNR (FN/(FN+TP))            0.4168      0.4706     0.2075  35

=== abs(sensitivity-specificity) gap: mean=0.2505 median=0.2059 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6102      0.6172     0.0499  5
  max valid BA                0.6269      0.6429     0.0394  5
  best valid F1               0.6651      0.6875     0.0507  5
  test BA                     0.5717      0.5734     0.0109  5
  test F1                     0.5807      0.5581     0.0498  5
  test sensitivity            0.5761      0.5373     0.1125  5
  test specificity            0.5672      0.5738     0.1021  5
  test precision              0.5955      0.5882     0.0149  5
  test loss                   0.6847      0.6884     0.0093  5
  FPR (FP/(FP+TN))            0.4328      0.4262     0.1021  5
  FNR (FN/(FN+TP))            0.4239      0.4627     0.1125  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5654      0.5577     0.0421  5
  max valid BA                0.5692      0.5577     0.0421  5
  best valid F1               0.5849      0.6316     0.0944  5
  test BA                     0.4680      0.4600     0.0460  5
  test F1                     0.4101      0.4255     0.0643  5
  test sensitivity            0.3840      0.4000     0.1187  5
  test specificity            0.5520      0.5200     0.2105  5
  test precision              0.4853      0.4545     0.0796  5
  test loss                   0.7140      0.7117     0.0122  5
  FPR (FP/(FP+TN))            0.4480      0.4800     0.2105  5
  FNR (FN/(FN+TP))            0.6160      0.6000     0.1187  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6508      0.6538     0.0594  5
  max valid BA                0.6620      0.6755     0.0642  5
  best valid F1               0.5727      0.5581     0.0490  5
  test BA                     0.5718      0.5624     0.0620  5
  test F1                     0.4507      0.4706     0.0966  5
  test sensitivity            0.5478      0.5217     0.2208  5
  test specificity            0.5957      0.6596     0.1921  5
  test precision              0.4013      0.3810     0.0651  5
  test loss                   0.6651      0.6617     0.0232  5
  FPR (FP/(FP+TN))            0.4043      0.3404     0.1921  5
  FNR (FN/(FN+TP))            0.4522      0.4783     0.2208  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7996      0.8001     0.0169  5
  max valid BA                0.8187      0.8103     0.0294  5
  best valid F1               0.7524      0.7407     0.0386  5
  test BA                     0.7855      0.7743     0.0359  5
  test F1                     0.7063      0.6923     0.0483  5
  test sensitivity            0.8348      0.8261     0.0567  5
  test specificity            0.7362      0.7660     0.1005  5
  test precision              0.6191      0.6207     0.0872  5
  test loss                   0.6253      0.6332     0.0138  5
  FPR (FP/(FP+TN))            0.2638      0.2340     0.1005  5
  FNR (FN/(FN+TP))            0.1652      0.1739     0.0567  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5375      0.5450     0.0401  5
  max valid BA                0.5523      0.5450     0.0457  5
  best valid F1               0.5416      0.5325     0.0401  5
  test BA                     0.5061      0.5215     0.0469  5
  test F1                     0.4839      0.5190     0.0840  5
  test sensitivity            0.5785      0.6308     0.1663  5
  test specificity            0.4337      0.4607     0.1114  5
  test precision              0.4229      0.4359     0.0436  5
  test loss                   0.7009      0.6997     0.0104  5
  FPR (FP/(FP+TN))            0.5663      0.5393     0.1114  5
  FNR (FN/(FN+TP))            0.4215      0.3692     0.1663  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5931      0.5625     0.0763  5
  max valid BA                0.6167      0.5972     0.0654  5
  best valid F1               0.4866      0.4941     0.1049  5
  test BA                     0.5750      0.5694     0.0894  5
  test F1                     0.4260      0.3750     0.1236  5
  test sensitivity            0.4556      0.4167     0.2279  5
  test specificity            0.6944      0.5972     0.1687  5
  test precision              0.4525      0.4762     0.1263  5
  test loss                   0.6809      0.6842     0.0111  5
  FPR (FP/(FP+TN))            0.3056      0.4028     0.1687  5
  FNR (FN/(FN+TP))            0.5444      0.5833     0.2279  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6294      0.6471     0.0319  5
  max valid BA                0.6471      0.6618     0.0294  5
  best valid F1               0.5703      0.5882     0.0301  5
  test BA                     0.5706      0.5735     0.0446  5
  test F1                     0.4915      0.5085     0.0595  5
  test sensitivity            0.7059      0.7647     0.1951  5
  test specificity            0.4353      0.4118     0.1720  5
  test precision              0.3870      0.3939     0.0341  5
  test loss                   0.6925      0.6853     0.0165  5
  FPR (FP/(FP+TN))            0.5647      0.5882     0.1720  5
  FNR (FN/(FN+TP))            0.2941      0.2353     0.1951  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.552         0.512         4         0.340              0.381
   CRAL-TRIO     1   129   67             0.799    0.550         0.504         4         0.551              0.568
   CRAL-TRIO     2   129   67             0.793    0.495         0.390         4         0.472              0.451
   CRAL-TRIO     3   129   67             0.806    0.694         0.581         4         0.469              0.466
   CRAL-TRIO     4   129   67             0.804    0.519         0.481         4         0.433              0.507
        GLTP     0    52   26             0.618    0.592         0.567         2         0.492              0.500
        GLTP     1    52   26             0.601    0.467         0.495         2         0.558              0.500
        GLTP     2    52   26             0.618    0.556         0.487         2         0.547              0.483
        GLTP     3    52   26             0.619    0.541         0.501         2         0.589              0.500
        GLTP     4    52   26             0.621    0.540         0.517         2         0.495              0.509
    IP_trans     0    71   24             0.809    0.731         0.723         3         0.761              0.748
    IP_trans     1    71   24             0.808    0.799         0.815         3         0.720              0.717
    IP_trans     2    71   24             0.810    0.666         0.646         3         0.739              0.784
    IP_trans     3    71   24             0.811    0.659         0.655         3         0.588              0.591
    IP_trans     4    71   24             0.808    0.534         0.538         3         0.623              0.677
LBP_BPI_CETP     0    71   24             0.809    0.780         0.769         2         0.719              0.701
LBP_BPI_CETP     1    71   24             0.816    0.819         0.813         2         0.601              0.675
LBP_BPI_CETP     2    71   24             0.808    0.730         0.731         2         0.623              0.625
LBP_BPI_CETP     3    71   24             0.807    0.780         0.768         2         0.812              0.814
LBP_BPI_CETP     4    71   24             0.804    0.839         0.840         2         0.769              0.764
       START     0   153   64             0.791    0.396         0.448         3         0.508              0.479
       START     1   153   64             0.784    0.480         0.486         3         0.454              0.439
       START     2   153   64             0.794    0.384         0.416         3         0.525              0.558
       START     3   153   64             0.797    0.559         0.560         3         0.596              0.608
       START     4   153   64             0.779    0.472         0.463         3         0.441              0.460
   lipocalin     0   108   36             0.847    0.555         0.460         5         0.605              0.655
   lipocalin     1   108   36             0.827    0.357         0.302         5         0.284              0.217
   lipocalin     2   108   36             0.829    0.511         0.415         5         0.585              0.548
   lipocalin     3   108   36             0.846    0.395         0.258         5         0.352              0.289
   lipocalin     4   108   36             0.810    0.386         0.223         5         0.541              0.463
        scp2     0    51   17             0.808    0.730         0.747         2         0.666              0.619
        scp2     1    51   17             0.837    0.619         0.583         3         0.693              0.626
        scp2     2    51   17             0.851    0.564         0.389         3         0.536              0.417
        scp2     3    51   17             0.842    0.706         0.716         3         0.668              0.576
        scp2     4    51   17             0.834    0.557         0.580         3         0.580              0.405

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.562         0.494       4.0         0.453              0.475
GLTP           52.0  26.0             0.615    0.539         0.513       2.0         0.536              0.499
IP_trans       71.0  24.0             0.809    0.678         0.675       3.0         0.686              0.703
LBP_BPI_CETP   71.0  24.0             0.809    0.790         0.784       2.0         0.705              0.716
START         153.0  64.0             0.789    0.458         0.475       3.0         0.505              0.509
lipocalin     108.0  36.0             0.832    0.441         0.332       5.0         0.473              0.434
scp2           51.0  17.0             0.834    0.635         0.603       2.8         0.629              0.529

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.586          0.701       0.500
null_AUC_k15      0.570          0.673       0.492

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.554          0.688       0.453
null_AUC_prot_k15      0.552          0.649       0.479

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.515      0.552     0.509
10     0.57  0.604      0.552     0.578
49     0.57  0.597      0.552     0.566
51     0.57  0.599      0.552     0.571
120    0.57  0.586      0.552     0.554

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.657      0.050          0.657              0.695           0.038
10        0.607         0.654      0.047          0.657              0.688           0.031
49        0.607         0.649      0.042          0.657              0.684           0.027
51        0.607         0.652      0.045          0.657              0.687           0.030
120       0.607         0.649      0.043          0.657              0.684           0.028

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.562      0.475     0.494      0.029           0.017
GLTP          0.536  0.539      0.499     0.513      0.042           0.014
IP_trans      0.686  0.678      0.703     0.675      0.017           0.015
LBP_BPI_CETP  0.705  0.790      0.716     0.784      0.104           0.082
START         0.505  0.458      0.509     0.475      0.043           0.018
lipocalin     0.473  0.441      0.434     0.332      0.040           0.022
scp2          0.629  0.635      0.529     0.603      0.023           0.024

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.586          0.701       0.500      0.635
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.554          0.688       0.453      0.603
increment           0.043          0.048       0.039      0.023
increment_prot      0.028          0.040       0.018      0.024
```
