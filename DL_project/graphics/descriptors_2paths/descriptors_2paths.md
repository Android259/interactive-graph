# descriptors_2paths

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_2paths'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5313      0.5574      0.5103      0.7046      0.5791      0.5516
groups_GLTP            5      0.3920      0.5440      0.6602      0.4986      0.4692      0.6308
groups_IP_trans        5      0.3913      0.7404      0.4303      0.6826      0.4667      0.6979
groups_LBP_BPI_CETP    5      0.6087      0.7106      0.6088      0.5639      0.7000      0.6638
groups_START           5      0.4492      0.5551      0.5556      0.5082      0.5062      0.5933
groups_lipocalin       5      0.6611      0.3500      0.5761      0.4899      0.7111      0.3722
groups_scp2            5      0.5647      0.5706      0.4529      0.6381      0.5529      0.6118
ALL                   35      0.5141      0.5754      0.5420      0.5837      0.5693      0.5888

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5788      0.5390     0.0872  35
max valid BA                0.6086      0.5962     0.0909  35
best valid F1               0.5975      0.6070     0.1064  35
test BA                     0.5447      0.5294     0.0936  35
test F1                     0.4215      0.4638     0.1968  35
test sensitivity            0.5141      0.4923     0.3329  35
test specificity            0.5754      0.6400     0.3121  35
test precision              0.4700      0.4490     0.1638  33
test loss                   0.7679      0.6973     0.3803  35
FPR (FP/(FP+TN))            0.4246      0.3600     0.3121  35
FNR (FN/(FN+TP))            0.4859      0.5077     0.3329  35

=== abs(sensitivity-specificity) gap: mean=0.5470 median=0.5236 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5654      0.5500     0.0498  5
  max valid BA                0.5957      0.6003     0.0464  5
  best valid F1               0.6828      0.6907     0.0134  5
  test BA                     0.5444      0.5647     0.0375  5
  test F1                     0.5137      0.5455     0.1732  5
  test sensitivity            0.5313      0.4925     0.2969  5
  test specificity            0.5574      0.6557     0.2401  5
  test precision              0.5644      0.5644     0.0349  5
  test loss                   1.1424      0.6977     0.9831  5
  FPR (FP/(FP+TN))            0.4426      0.3443     0.2401  5
  FNR (FN/(FN+TP))            0.4687      0.5075     0.2969  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5385     0.0586  5
  max valid BA                0.5692      0.5769     0.0520  5
  best valid F1               0.6661      0.6667     0.0120  5
  test BA                     0.4680      0.4400     0.0844  5
  test F1                     0.3509      0.3000     0.2780  5
  test sensitivity            0.3920      0.2400     0.3841  5
  test specificity            0.5440      0.6400     0.2377  5
  test precision              0.3692      0.4000     0.1721  5
  test loss                   0.7271      0.6973     0.0707  5
  FPR (FP/(FP+TN))            0.4560      0.3600     0.2377  5
  FNR (FN/(FN+TP))            0.6080      0.7600     0.3841  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5823      0.5957     0.0643  5
  max valid BA                0.6033      0.5962     0.0857  5
  best valid F1               0.5517      0.5385     0.0570  5
  test BA                     0.5659      0.5888     0.0885  5
  test F1                     0.3436      0.4103     0.2307  5
  test sensitivity            0.3913      0.3478     0.3727  5
  test specificity            0.7404      0.8298     0.2848  5
  test precision              0.4615      0.4518     0.1852  4
  test loss                   0.6631      0.6689     0.0379  5
  FPR (FP/(FP+TN))            0.2596      0.1702     0.2848  5
  FNR (FN/(FN+TP))            0.6087      0.6522     0.3727  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6819      0.7589     0.1591  5
  max valid BA                0.7400      0.7899     0.1379  5
  best valid F1               0.6817      0.7200     0.1136  5
  test BA                     0.6597      0.6429     0.1363  5
  test F1                     0.5305      0.5000     0.2078  5
  test sensitivity            0.6087      0.6522     0.3354  5
  test specificity            0.7106      0.8511     0.3672  5
  test precision              0.6086      0.6818     0.1644  5
  test loss                   0.6133      0.5937     0.0810  5
  FPR (FP/(FP+TN))            0.2894      0.1489     0.3672  5
  FNR (FN/(FN+TP))            0.3913      0.3478     0.3354  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5498      0.5256     0.0509  5
  max valid BA                0.5833      0.5926     0.0437  5
  best valid F1               0.5934      0.5953     0.0216  5
  test BA                     0.5021      0.5000     0.0550  5
  test F1                     0.3977      0.3860     0.1308  5
  test sensitivity            0.4492      0.3385     0.3306  5
  test specificity            0.5551      0.6067     0.3620  5
  test precision              0.5023      0.4221     0.2372  5
  test loss                   0.7352      0.7139     0.0656  5
  FPR (FP/(FP+TN))            0.4449      0.3933     0.3620  5
  FNR (FN/(FN+TP))            0.5508      0.6615     0.3306  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5403      0.5139     0.0800  5
  max valid BA                0.5778      0.5208     0.0946  5
  best valid F1               0.5402      0.5106     0.0529  5
  test BA                     0.5056      0.5139     0.0576  5
  test F1                     0.4217      0.4638     0.1022  5
  test sensitivity            0.6611      0.6667     0.3230  5
  test specificity            0.3500      0.2083     0.3863  5
  test precision              0.3707      0.3396     0.0830  5
  test loss                   0.7307      0.7022     0.0682  5
  FPR (FP/(FP+TN))            0.6500      0.7917     0.3863  5
  FNR (FN/(FN+TP))            0.3389      0.3333     0.3230  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5824      0.5882     0.0526  5
  max valid BA                0.5912      0.5882     0.0446  5
  best valid F1               0.4666      0.5283     0.1563  5
  test BA                     0.5676      0.5588     0.0620  5
  test F1                     0.3923      0.5091     0.2388  5
  test sensitivity            0.5647      0.8235     0.3959  5
  test specificity            0.5706      0.5000     0.3082  5
  test precision              0.3973      0.3846     0.0370  4
  test loss                   0.7635      0.7085     0.1308  5
  FPR (FP/(FP+TN))            0.4294      0.5000     0.3082  5
  FNR (FN/(FN+TP))            0.4353      0.1765     0.3959  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (chemistry_null_model.py), epoch 120 ---
=== valid block, epoch 120 ===
         fam  seed  rows  pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
   CRAL-TRIO     0   129   67             0.806    0.526         0.524         4         0.365              0.395
   CRAL-TRIO     1   129   67             0.799    0.617         0.431         4         0.552              0.525
   CRAL-TRIO     2   129   67             0.793    0.463         0.437         4         0.492              0.531
   CRAL-TRIO     3   129   67             0.806    0.542         0.572         4         0.510              0.501
   CRAL-TRIO     4   129   67             0.804    0.564         0.502         4         0.451              0.532
        GLTP     0    52   26             0.618    0.274         0.322         2         0.492              0.491
        GLTP     1    52   26             0.601    0.599         0.534         2         0.564              0.507
        GLTP     2    52   26             0.618    0.447         0.465         2         0.559              0.497
        GLTP     3    52   26             0.619    0.536         0.544         2         0.578              0.500
        GLTP     4    52   26             0.621    0.629         0.623         2         0.500              0.509
    IP_trans     0    71   24             0.809    0.725         0.744         3         0.753              0.743
    IP_trans     1    71   24             0.808    0.395         0.393         3         0.709              0.707
    IP_trans     2    71   24             0.810    0.442         0.426         3         0.742              0.786
    IP_trans     3    71   24             0.811    0.556         0.594         3         0.587              0.586
    IP_trans     4    71   24             0.808    0.535         0.505         3         0.608              0.659
LBP_BPI_CETP     0    71   24             0.809    0.794         0.793         2         0.691              0.698
LBP_BPI_CETP     1    71   24             0.816    0.867         0.873         2         0.586              0.656
LBP_BPI_CETP     2    71   24             0.808    0.473         0.474         2         0.629              0.625
LBP_BPI_CETP     3    71   24             0.807    0.761         0.759         2         0.771              0.772
LBP_BPI_CETP     4    71   24             0.804    0.897         0.900         2         0.710              0.708
       START     0   153   64             0.791    0.496         0.475         3         0.519              0.497
       START     1   153   64             0.784    0.542         0.469         3         0.469              0.438
       START     2   153   64             0.794    0.628         0.529         3         0.507              0.573
       START     3   153   64             0.797    0.594         0.561         3         0.562              0.529
       START     4   153   64             0.779    0.321         0.377         3         0.429              0.454
   lipocalin     0   108   36             0.847    0.194         0.139         5         0.649              0.674
   lipocalin     1   108   36             0.827    0.314         0.223         5         0.276              0.217
   lipocalin     2   108   36             0.829    0.368         0.162         5         0.577              0.541
   lipocalin     3   108   36             0.846    0.506         0.544         5         0.385              0.376
   lipocalin     4   108   36             0.810    0.404         0.188         5         0.550              0.504
        scp2     0    51   17             0.808    0.407         0.432         2         0.637              0.515
        scp2     1    51   17             0.837    0.482         0.606         3         0.674              0.576
        scp2     2    51   17             0.851    0.413         0.441         3         0.526              0.459
        scp2     3    51   17             0.842    0.462         0.520         3         0.675              0.552
        scp2     4    51   17             0.834    0.456         0.590         3         0.596              0.494

=== mean over seeds ===
               rows   pos  sim_to_train_pos  net_AUC  net_AUC_prot  proteins  null_AUC_k15  null_AUC_prot_k15
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.802    0.542         0.493       4.0         0.474              0.497
GLTP           52.0  26.0             0.615    0.497         0.498       2.0         0.539              0.501
IP_trans       71.0  24.0             0.809    0.531         0.533       3.0         0.680              0.696
LBP_BPI_CETP   71.0  24.0             0.809    0.759         0.760       2.0         0.677              0.692
START         153.0  64.0             0.789    0.516         0.482       3.0         0.497              0.498
lipocalin     108.0  36.0             0.832    0.357         0.251       5.0         0.487              0.462
scp2           51.0  17.0             0.834    0.444         0.518       2.8         0.621              0.519

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
net_AUC           0.521          0.578       0.478
null_AUC_k15      0.568          0.660       0.499

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
net_AUC_prot           0.505          0.603       0.431
null_AUC_prot_k15      0.552          0.636       0.490

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
        chem    net  chem_prot  net_prot
epoch                                   
1      0.568  0.463      0.552     0.470
10     0.568  0.487      0.552     0.479
49     0.568  0.514      0.552     0.506
51     0.568  0.513      0.552     0.503
120    0.568  0.521      0.552     0.505

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.594         0.645      0.050          0.654              0.682           0.028
10        0.594         0.647      0.053          0.654              0.681           0.027
49        0.594         0.647      0.053          0.654              0.687           0.033
51        0.594         0.648      0.053          0.654              0.690           0.036
120       0.594         0.655      0.061          0.654              0.699           0.044

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.474  0.542      0.497     0.493      0.033           0.033
GLTP          0.539  0.497      0.501     0.498      0.070           0.032
IP_trans      0.680  0.531      0.696     0.533      0.022           0.010
LBP_BPI_CETP  0.677  0.759      0.692     0.760      0.116           0.093
START         0.497  0.516      0.498     0.482      0.057           0.022
lipocalin     0.487  0.357      0.462     0.251      0.115           0.110
scp2          0.621  0.444      0.519     0.518      0.015           0.011

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.568          0.660       0.499      0.621
net                 0.521          0.578       0.478      0.444
chem_prot           0.552          0.636       0.490      0.519
net_prot            0.505          0.603       0.431      0.518
increment           0.061          0.051       0.069      0.015
increment_prot      0.044          0.038       0.049      0.011
```
