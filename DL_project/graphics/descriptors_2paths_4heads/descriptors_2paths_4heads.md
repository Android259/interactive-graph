# descriptors_2paths_4heads

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_2paths_4heads'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6090      0.4197      0.5154      0.6164      0.6209      0.4484
groups_GLTP            5      0.5120      0.5440      0.6196      0.5676      0.5308      0.6538
groups_IP_trans        5      0.4870      0.6638      0.7152      0.5198      0.6000      0.6766
groups_LBP_BPI_CETP    5      0.8000      0.6383      0.6531      0.5500      0.8250      0.6340
groups_START           5      0.6338      0.5348      0.6710      0.5130      0.6750      0.4989
groups_lipocalin       5      0.4222      0.6056      0.5125      0.5966      0.4500      0.6194
groups_scp2            5      0.6588      0.3588      0.6413      0.4869      0.6588      0.4118
ALL                   35      0.5890      0.5379      0.6183      0.5500      0.6229      0.5633

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5931      0.5769     0.0779  35
max valid BA                0.6261      0.5962     0.0973  35
best valid F1               0.6037      0.6118     0.1068  35
test BA                     0.5634      0.5417     0.0970  35
test F1                     0.4842      0.5109     0.1658  35
test sensitivity            0.5890      0.6087     0.2837  35
test specificity            0.5379      0.5745     0.2723  35
test precision              0.4644      0.4706     0.1526  35
test loss                   0.7164      0.6865     0.1544  35
FPR (FP/(FP+TN))            0.4621      0.4255     0.2723  35
FNR (FN/(FN+TP))            0.4110      0.3913     0.2837  35

=== abs(sensitivity-specificity) gap: mean=0.4473 median=0.4000 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5346      0.5422     0.0470  5
  max valid BA                0.5715      0.5626     0.0429  5
  best valid F1               0.6639      0.6738     0.0552  5
  test BA                     0.5143      0.5318     0.0476  5
  test F1                     0.5495      0.6093     0.1465  5
  test sensitivity            0.6090      0.6866     0.2373  5
  test specificity            0.4197      0.3770     0.1562  5
  test precision              0.5228      0.5476     0.0512  5
  test loss                   0.7798      0.7034     0.1851  5
  FPR (FP/(FP+TN))            0.5803      0.6230     0.1562  5
  FNR (FN/(FN+TP))            0.3910      0.3134     0.2373  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5923      0.5769     0.0439  5
  max valid BA                0.6154      0.6346     0.0385  5
  best valid F1               0.6737      0.6885     0.0361  5
  test BA                     0.5280      0.5200     0.1083  5
  test F1                     0.4842      0.5641     0.2125  5
  test sensitivity            0.5120      0.4400     0.3217  5
  test specificity            0.5440      0.6400     0.2736  5
  test precision              0.5179      0.5116     0.1928  5
  test loss                   0.7065      0.7012     0.0332  5
  FPR (FP/(FP+TN))            0.4560      0.3600     0.2736  5
  FNR (FN/(FN+TP))            0.4880      0.5600     0.3217  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6383      0.6449     0.0531  5
  max valid BA                0.6901      0.6831     0.0846  5
  best valid F1               0.6138      0.6032     0.0829  5
  test BA                     0.5754      0.5453     0.0718  5
  test F1                     0.4413      0.4000     0.0985  5
  test sensitivity            0.4870      0.5217     0.1580  5
  test specificity            0.6638      0.6383     0.1357  5
  test precision              0.4216      0.4286     0.0746  5
  test loss                   0.6572      0.6459     0.0299  5
  FPR (FP/(FP+TN))            0.3362      0.3617     0.1357  5
  FNR (FN/(FN+TP))            0.5130      0.4783     0.1580  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7295      0.7340     0.0523  5
  max valid BA                0.8073      0.7983     0.0381  5
  best valid F1               0.7343      0.7188     0.0472  5
  test BA                     0.7191      0.7618     0.1022  5
  test F1                     0.6403      0.6829     0.0925  5
  test sensitivity            0.8000      0.7391     0.1701  5
  test specificity            0.6383      0.5745     0.2402  5
  test precision              0.5703      0.5349     0.1683  5
  test loss                   0.6210      0.6128     0.0759  5
  FPR (FP/(FP+TN))            0.3617      0.4255     0.2402  5
  FNR (FN/(FN+TP))            0.2000      0.2609     0.1701  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5869      0.5938     0.0287  5
  max valid BA                0.6026      0.6029     0.0226  5
  best valid F1               0.5869      0.6118     0.0695  5
  test BA                     0.5843      0.5758     0.0511  5
  test F1                     0.5478      0.5714     0.0703  5
  test sensitivity            0.6338      0.6769     0.2316  5
  test specificity            0.5348      0.4944     0.2878  5
  test precision              0.5304      0.4944     0.1029  5
  test loss                   0.6813      0.6862     0.0097  5
  FPR (FP/(FP+TN))            0.4652      0.5056     0.2878  5
  FNR (FN/(FN+TP))            0.3662      0.3231     0.2316  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5347      0.5417     0.0246  5
  max valid BA                0.5431      0.5417     0.0271  5
  best valid F1               0.4900      0.5000     0.0382  5
  test BA                     0.5139      0.5347     0.0527  5
  test F1                     0.3417      0.3469     0.1219  5
  test sensitivity            0.4222      0.3611     0.3224  5
  test specificity            0.6056      0.6667     0.3314  5
  test precision              0.4006      0.3617     0.1129  5
  test loss                   0.8475      0.6904     0.3392  5
  FPR (FP/(FP+TN))            0.3944      0.3333     0.3314  5
  FNR (FN/(FN+TP))            0.5778      0.6389     0.3224  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5353      0.5441     0.0436  5
  max valid BA                0.5529      0.5735     0.0354  5
  best valid F1               0.4635      0.4923     0.0634  5
  test BA                     0.5088      0.5000     0.0505  5
  test F1                     0.3842      0.4848     0.2189  5
  test sensitivity            0.6588      0.9412     0.4390  5
  test specificity            0.3588      0.1765     0.4078  5
  test precision              0.2871      0.3333     0.1639  5
  test loss                   0.7214      0.7233     0.0402  5
  FPR (FP/(FP+TN))            0.6412      0.8235     0.4078  5
  FNR (FN/(FN+TP))            0.3412      0.0588     0.4390  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.515         0.476         4         0.365              0.395
   CRAL-TRIO     1   129   67             0.799    0.513         0.567         4         0.552              0.525
   CRAL-TRIO     2   129   67             0.793    0.525         0.566         4         0.492              0.531
   CRAL-TRIO     3   129   67             0.806    0.517         0.397         4         0.510              0.501
   CRAL-TRIO     4   129   67             0.804    0.538         0.382         4         0.451              0.532
        GLTP     0    52   26             0.618    0.324         0.409         2         0.492              0.491
        GLTP     1    52   26             0.601    0.361         0.490         2         0.564              0.507
        GLTP     2    52   26             0.618    0.470         0.552         2         0.559              0.497
        GLTP     3    52   26             0.619    0.552         0.591         2         0.578              0.500
        GLTP     4    52   26             0.621    0.549         0.584         2         0.500              0.509
    IP_trans     0    71   24             0.809    0.694         0.698         3         0.753              0.743
    IP_trans     1    71   24             0.808    0.633         0.669         3         0.709              0.707
    IP_trans     2    71   24             0.810    0.606         0.629         3         0.742              0.786
    IP_trans     3    71   24             0.811    0.649         0.606         3         0.587              0.586
    IP_trans     4    71   24             0.808    0.530         0.520         3         0.608              0.659
LBP_BPI_CETP     0    71   24             0.809    0.802         0.819         2         0.691              0.698
LBP_BPI_CETP     1    71   24             0.816    0.726         0.767         2         0.586              0.656
LBP_BPI_CETP     2    71   24             0.808    0.330         0.316         2         0.629              0.625
LBP_BPI_CETP     3    71   24             0.807    0.253         0.275         2         0.771              0.772
LBP_BPI_CETP     4    71   24             0.804    0.902         0.916         2         0.710              0.708
       START     0   153   64             0.791    0.520         0.497         3         0.519              0.497
       START     1   153   64             0.784    0.639         0.552         3         0.469              0.438
       START     2   153   64             0.794    0.557         0.478         3         0.507              0.573
       START     3   153   64             0.797    0.552         0.407         3         0.562              0.529
       START     4   153   64             0.779    0.490         0.453         3         0.429              0.454
   lipocalin     0   108   36             0.847    0.199         0.097         5         0.649              0.674
   lipocalin     1   108   36             0.827    0.341         0.257         5         0.276              0.217
   lipocalin     2   108   36             0.829    0.151         0.079         5         0.577              0.541
   lipocalin     3   108   36             0.846    0.296         0.108         5         0.385              0.376
   lipocalin     4   108   36             0.810    0.452         0.339         5         0.550              0.504
        scp2     0    51   17             0.808    0.426         0.426         2         0.637              0.515
        scp2     1    51   17             0.837    0.376         0.381         3         0.674              0.576
        scp2     2    51   17             0.851    0.388         0.512         3         0.526              0.459
        scp2     3    51   17             0.842    0.453         0.561         3         0.675              0.552
        scp2     4    51   17             0.834    0.465         0.565         3         0.596              0.494

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.522         0.478       4.0         0.474              0.497
GLTP           52.0  26.0             0.615    0.451         0.525       2.0         0.539              0.501
IP_trans       71.0  24.0             0.809    0.623         0.624       3.0         0.680              0.696
LBP_BPI_CETP   71.0  24.0             0.809    0.602         0.619       2.0         0.677              0.692
START         153.0  64.0             0.789    0.552         0.477       3.0         0.497              0.498
lipocalin     108.0  36.0             0.832    0.288         0.176       5.0         0.487              0.462
scp2           51.0  17.0             0.834    0.422         0.489       2.8         0.621              0.519

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.494          0.549       0.453
null_AUC_k15      0.568          0.660       0.499

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.484          0.577       0.414
null_AUC_prot_k15      0.552          0.636       0.490

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
        chem    net  chem_prot  net_prot
epoch                                   
1      0.568  0.467      0.552     0.468
10     0.568  0.531      0.552     0.516
49     0.568  0.521      0.552     0.523
51     0.568  0.529      0.552     0.533
120    0.568  0.494      0.552     0.484

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.594         0.644      0.050          0.654              0.693           0.039
10        0.594         0.650      0.056          0.654              0.700           0.046
49        0.594         0.647      0.053          0.654              0.687           0.033
51        0.594         0.652      0.058          0.654              0.694           0.040
120       0.594         0.654      0.060          0.654              0.698           0.044

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.474  0.522      0.497     0.478      0.009           0.000
GLTP          0.539  0.451      0.501     0.525      0.063           0.017
IP_trans      0.680  0.623      0.696     0.624      0.023           0.004
LBP_BPI_CETP  0.677  0.602      0.692     0.619      0.119           0.095
START         0.497  0.552      0.498     0.477      0.052           0.021
lipocalin     0.487  0.288      0.462     0.176      0.152           0.161
scp2          0.621  0.422      0.519     0.489      0.002           0.008

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.568          0.660       0.499      0.621
net                 0.494          0.549       0.453      0.422
chem_prot           0.552          0.636       0.490      0.519
net_prot            0.484          0.577       0.414      0.489
increment           0.060          0.048       0.069      0.002
increment_prot      0.044          0.036       0.050      0.008
```
