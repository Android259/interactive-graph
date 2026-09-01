# descriptors_lipprop

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_lipprop'
rows: 25

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5284      0.5705      0.6040      0.4666      0.5194      0.5806
groups_IP_trans        5      0.6435      0.4979      0.7152      0.3275      0.6750      0.5106
groups_LBP_BPI_CETP    5      0.8174      0.6936      0.6737      0.4003      0.8583      0.6340
groups_START           5      0.4738      0.5034      0.6334      0.3942      0.5062      0.5663
groups_lipocalin       5      0.6111      0.5000      0.5511      0.5031      0.6444      0.4944
ALL                   25      0.6148      0.5531      0.6355      0.4183      0.6407      0.5572

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5989      0.5691     0.0914  25
max valid BA                0.6059      0.5804     0.0931  25
best valid F1               0.5526      0.5785     0.1410  25
test BA                     0.5840      0.5417     0.1090  25
test F1                     0.5013      0.5000     0.1641  25
test sensitivity            0.6148      0.6087     0.2647  25
test specificity            0.5531      0.6383     0.2567  25
test precision              0.4763      0.4550     0.1162  24
test loss                   0.6920      0.6928     0.0160  25
FPR (FP/(FP+TN))            0.4469      0.3617     0.2567  25
FNR (FN/(FN+TP))            0.3852      0.3913     0.2647  25

=== abs(sensitivity-specificity) gap: mean=0.3561 median=0.2451 n=25 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5500     0.0303  5
  max valid BA                0.5600      0.5556     0.0322  5
  best valid F1               0.6326      0.6378     0.0565  5
  test BA                     0.5494      0.5352     0.0283  5
  test F1                     0.5353      0.5600     0.1106  5
  test sensitivity            0.5284      0.5224     0.1925  5
  test specificity            0.5705      0.6230     0.1677  5
  test precision              0.5768      0.5882     0.0257  5
  test loss                   0.6908      0.6929     0.0048  5
  FPR (FP/(FP+TN))            0.4295      0.3770     0.1677  5
  FNR (FN/(FN+TP))            0.4716      0.4776     0.1925  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5928      0.6019     0.0638  5
  max valid BA                0.6076      0.6215     0.0773  5
  best valid F1               0.5337      0.5306     0.0596  5
  test BA                     0.5707      0.6008     0.0623  5
  test F1                     0.4824      0.4946     0.0340  5
  test sensitivity            0.6435      0.6087     0.2072  5
  test specificity            0.4979      0.6383     0.3074  5
  test precision              0.4104      0.4516     0.0733  5
  test loss                   0.6976      0.6915     0.0216  5
  FPR (FP/(FP+TN))            0.5021      0.3617     0.3074  5
  FNR (FN/(FN+TP))            0.3565      0.3913     0.2072  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7462      0.7668     0.0499  5
  max valid BA                0.7506      0.7695     0.0512  5
  best valid F1               0.6780      0.6957     0.0442  5
  test BA                     0.7555      0.7539     0.0948  5
  test F1                     0.6724      0.6667     0.1076  5
  test sensitivity            0.8174      0.8696     0.1667  5
  test specificity            0.6936      0.8085     0.1901  5
  test precision              0.5900      0.6000     0.1156  5
  test loss                   0.6875      0.6909     0.0077  5
  FPR (FP/(FP+TN))            0.3064      0.1915     0.1901  5
  FNR (FN/(FN+TP))            0.1826      0.1304     0.1667  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5363      0.5473     0.0309  5
  max valid BA                0.5416      0.5517     0.0334  5
  best valid F1               0.4865      0.4626     0.1088  5
  test BA                     0.4886      0.5023     0.0401  5
  test F1                     0.4089      0.4559     0.1506  5
  test sensitivity            0.4738      0.4769     0.2881  5
  test specificity            0.5034      0.5506     0.2380  5
  test precision              0.3922      0.4234     0.0680  5
  test loss                   0.6945      0.6954     0.0016  5
  FPR (FP/(FP+TN))            0.4966      0.4494     0.2380  5
  FNR (FN/(FN+TP))            0.5262      0.5231     0.2881  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5694      0.5833     0.0748  5
  max valid BA                0.5694      0.5833     0.0748  5
  best valid F1               0.4323      0.5000     0.2170  5
  test BA                     0.5556      0.5417     0.0713  5
  test F1                     0.4074      0.4957     0.2320  5
  test sensitivity            0.6111      0.6944     0.3783  5
  test specificity            0.5000      0.5694     0.3800  5
  test precision              0.3959      0.3751     0.0735  4
  test loss                   0.6897      0.6915     0.0302  5
  FPR (FP/(FP+TN))            0.5000      0.4306     0.3800  5
  FNR (FN/(FN+TP))            0.3889      0.3056     0.3783  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.473         0.445         4         0.340              0.381
   CRAL-TRIO     1   129   67             0.799    0.596         0.648         4         0.551              0.568
   CRAL-TRIO     2   129   67             0.793    0.499         0.483         4         0.472              0.451
   CRAL-TRIO     3   129   67             0.806    0.607         0.591         4         0.469              0.466
   CRAL-TRIO     4   129   67             0.804    0.464         0.496         4         0.433              0.507
        GLTP     0    52   26             0.618    0.437         0.459         2         0.492              0.500
        GLTP     1    52   26             0.601    0.521         0.501         2         0.558              0.500
        GLTP     2    52   26             0.618    0.509         0.486         2         0.547              0.483
        GLTP     3    52   26             0.619    0.531         0.474         2         0.589              0.500
        GLTP     4    52   26             0.621    0.533         0.524         2         0.495              0.509
    IP_trans     0    71   24             0.809    0.711         0.708         3         0.761              0.748
    IP_trans     1    71   24             0.808    0.656         0.666         3         0.720              0.717
    IP_trans     2    71   24             0.810    0.588         0.575         3         0.739              0.784
    IP_trans     3    71   24             0.811    0.666         0.640         3         0.588              0.591
    IP_trans     4    71   24             0.808    0.586         0.621         3         0.623              0.677
LBP_BPI_CETP     0    71   24             0.809    0.772         0.789         2         0.719              0.701
LBP_BPI_CETP     1    71   24             0.816    0.881         0.861         2         0.601              0.675
LBP_BPI_CETP     2    71   24             0.808    0.851         0.844         2         0.623              0.625
LBP_BPI_CETP     3    71   24             0.807    0.809         0.792         2         0.812              0.814
LBP_BPI_CETP     4    71   24             0.804    0.784         0.806         2         0.769              0.764
       START     0   153   64             0.791    0.436         0.493         3         0.508              0.479
       START     1   153   64             0.784    0.515         0.503         3         0.454              0.439
       START     2   153   64             0.794    0.411         0.418         3         0.525              0.558
       START     3   153   64             0.797    0.610         0.576         3         0.596              0.608
       START     4   153   64             0.779    0.454         0.431         3         0.441              0.460
   lipocalin     0   108   36             0.847    0.237         0.245         5         0.605              0.655
   lipocalin     1   108   36             0.827    0.424         0.358         5         0.284              0.217
   lipocalin     2   108   36             0.829    0.591         0.557         5         0.585              0.548
   lipocalin     3   108   36             0.846    0.682         0.714         5         0.352              0.289
   lipocalin     4   108   36             0.810    0.501         0.507         5         0.541              0.463
        scp2     0    51   17             0.808    0.450         0.552         2         0.666              0.619
        scp2     1    51   17             0.837    0.643         0.637         3         0.693              0.626
        scp2     2    51   17             0.851    0.574         0.388         3         0.536              0.417
        scp2     3    51   17             0.842    0.581         0.515         3         0.668              0.576
        scp2     4    51   17             0.834    0.663         0.627         3         0.580              0.405

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.528         0.532       4.0         0.453              0.475
GLTP           52.0  26.0             0.615    0.506         0.489       2.0         0.536              0.499
IP_trans       71.0  24.0             0.809    0.641         0.642       3.0         0.686              0.703
LBP_BPI_CETP   71.0  24.0             0.809    0.819         0.818       2.0         0.705              0.716
START         153.0  64.0             0.789    0.485         0.484       3.0         0.505              0.509
lipocalin     108.0  36.0             0.832    0.487         0.476       5.0         0.473              0.434
scp2           51.0  17.0             0.834    0.582         0.544       2.8         0.629              0.529

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.578          0.681       0.501
null_AUC_k15      0.570          0.673       0.492

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.569          0.668       0.495
null_AUC_prot_k15      0.552          0.649       0.479

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.429      0.552     0.444
10     0.57  0.500      0.552     0.517
49     0.57  0.569      0.552     0.575
51     0.57  0.574      0.552     0.576
120    0.57  0.578      0.552     0.569

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.647      0.040          0.657              0.693           0.037
10        0.607         0.650      0.043          0.657              0.690           0.033
49        0.607         0.650      0.043          0.657              0.691           0.034
51        0.607         0.653      0.046          0.657              0.693           0.036
120       0.607         0.650      0.044          0.657              0.696           0.039

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.528      0.475     0.532      0.013           0.032
GLTP          0.536  0.506      0.499     0.489      0.008          -0.002
IP_trans      0.686  0.641      0.703     0.642     -0.003           0.005
LBP_BPI_CETP  0.705  0.819      0.716     0.818      0.134           0.111
START         0.505  0.485      0.509     0.484      0.040           0.028
lipocalin     0.473  0.487      0.434     0.476      0.108           0.091
scp2          0.629  0.582      0.529     0.544      0.006           0.010

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.578          0.681       0.501      0.582
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.569          0.668       0.495      0.544
increment           0.044          0.046       0.042      0.006
increment_prot      0.039          0.042       0.037      0.010
```
