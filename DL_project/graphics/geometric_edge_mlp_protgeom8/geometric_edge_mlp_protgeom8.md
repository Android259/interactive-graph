# geometric_edge_mlp_protgeom8

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom8'
rows: 19

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.6418      0.4809      0.6514      0.5965      0.6517      0.5000
groups_GLTP            3      0.6267      0.5200      0.6818      0.6051      0.5641      0.6667
groups_IP_trans        3      0.4493      0.8014      0.7190      0.6368      0.5833      0.7447
groups_LBP_BPI_CETP    2      0.1522      0.8617      0.4523      0.5309      0.2917      0.8404
groups_START           3      0.7128      0.5281      0.8248      0.6104      0.6927      0.4981
groups_lipocalin       2      0.6667      0.8056      0.6835      0.4694      0.7083      0.7292
groups_scp2            3      0.4510      0.7255      0.8409      0.6290      0.5686      0.7745
ALL                   19      0.5412      0.6580      0.7066      0.5913      0.5885      0.6680

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6282      0.6068     0.0704  19
max valid BA                0.6645      0.6538     0.0618  19
best valid F1               0.6399      0.6531     0.0718  19
test BA                     0.5996      0.5882     0.0861  19
test F1                     0.5084      0.5714     0.1744  19
test sensitivity            0.5412      0.5373     0.2517  19
test specificity            0.6580      0.6596     0.2333  19
test precision              0.5358      0.5000     0.1634  19
test loss                   0.7088      0.7004     0.0968  19
FPR (FP/(FP+TN))            0.3420      0.3404     0.2333  19
FNR (FN/(FN+TP))            0.4588      0.4627     0.2517  19

=== abs(sensitivity-specificity) gap: mean=0.3779 median=0.3235 n=19 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5759      0.5837     0.0354  3
  max valid BA                0.6005      0.6068     0.0152  3
  best valid F1               0.7017      0.7065     0.0089  3
  test BA                     0.5613      0.5700     0.0322  3
  test F1                     0.5950      0.5760     0.0940  3
  test sensitivity            0.6418      0.5373     0.2346  3
  test specificity            0.4809      0.5738     0.2201  3
  test precision              0.5791      0.5648     0.0366  3
  test loss                   0.7195      0.7371     0.0324  3
  FPR (FP/(FP+TN))            0.5191      0.4262     0.2201  3
  FNR (FN/(FN+TP))            0.3582      0.4627     0.2346  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6154      0.5962     0.0881  3
  max valid BA                0.6859      0.6923     0.0294  3
  best valid F1               0.7221      0.7333     0.0241  3
  test BA                     0.5733      0.5600     0.1206  3
  test F1                     0.5881      0.5714     0.0717  3
  test sensitivity            0.6267      0.6000     0.2411  3
  test specificity            0.5200      0.3200     0.4176  3
  test precision              0.6684      0.5366     0.2891  3
  test loss                   0.7069      0.6907     0.0344  3
  FPR (FP/(FP+TN))            0.4800      0.6800     0.4176  3
  FNR (FN/(FN+TP))            0.3733      0.4000     0.2411  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6640      0.6937     0.0625  3
  max valid BA                0.7162      0.7061     0.0186  3
  best valid F1               0.6297      0.6207     0.0204  3
  test BA                     0.6253      0.6776     0.1180  3
  test F1                     0.4399      0.5818     0.2658  3
  test sensitivity            0.4493      0.5652     0.3205  3
  test specificity            0.8014      0.8511     0.1247  3
  test precision              0.4786      0.5000     0.1831  3
  test loss                   0.6992      0.7324     0.0818  3
  FPR (FP/(FP+TN))            0.1986      0.1489     0.1247  3
  FNR (FN/(FN+TP))            0.5507      0.4348     0.3205  3

groups_LBP_BPI_CETP (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5660      0.5660     0.0219  2
  max valid BA                0.5971      0.5971     0.0357  2
  best valid F1               0.5056      0.5056     0.0079  2
  test BA                     0.5069      0.5069     0.0092  2
  test F1                     0.1885      0.1885     0.1577  2
  test sensitivity            0.1522      0.1522     0.1537  2
  test specificity            0.8617      0.8617     0.1354  2
  test precision              0.3431      0.3431     0.0139  2
  test loss                   0.7951      0.7951     0.2461  2
  FPR (FP/(FP+TN))            0.1383      0.1383     0.1354  2
  FNR (FN/(FN+TP))            0.8478      0.8478     0.1537  2

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5954      0.6078     0.0303  3
  max valid BA                0.6226      0.6232     0.0145  3
  best valid F1               0.6206      0.6184     0.0152  3
  test BA                     0.6205      0.6002     0.0626  3
  test F1                     0.5992      0.6071     0.0843  3
  test sensitivity            0.7128      0.7846     0.1659  3
  test specificity            0.5281      0.5506     0.1030  3
  test precision              0.5232      0.5000     0.0445  3
  test loss                   0.6888      0.7004     0.0209  3
  FPR (FP/(FP+TN))            0.4719      0.4494     0.1030  3
  FNR (FN/(FN+TP))            0.2872      0.2154     0.1659  3

groups_lipocalin (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7188      0.7188     0.0344  2
  max valid BA                0.7188      0.7188     0.0344  2
  best valid F1               0.6313      0.6313     0.0409  2
  test BA                     0.7361      0.7361     0.0393  2
  test F1                     0.6389      0.6389     0.0600  2
  test sensitivity            0.6667      0.6667     0.2750  2
  test specificity            0.8056      0.8056     0.1964  2
  test precision              0.6866      0.6866     0.1739  2
  test loss                   0.5807      0.5807     0.0414  2
  FPR (FP/(FP+TN))            0.1944      0.1944     0.1964  2
  FNR (FN/(FN+TP))            0.3333      0.3333     0.2750  2

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6716      0.7206     0.0849  3
  max valid BA                0.7059      0.7500     0.0895  3
  best valid F1               0.6204      0.6667     0.0946  3
  test BA                     0.5882      0.5882     0.0147  3
  test F1                     0.4460      0.4242     0.0470  3
  test sensitivity            0.4510      0.4118     0.1225  3
  test specificity            0.7255      0.7353     0.1033  3
  test precision              0.4574      0.4375     0.0369  3
  test loss                   0.7576      0.7308     0.1245  3
  FPR (FP/(FP+TN))            0.2745      0.2647     0.1033  3
  FNR (FN/(FN+TP))            0.5490      0.5882     0.1225  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.476    0.534     4.000              0.347         0.466   5.000               0.480          0.554
GLTP                     0.595         0.484    0.453     2.000              0.488         0.450   3.000               0.494          0.550
IP_trans                 0.727         0.727    0.643     3.000              0.720         0.677   2.667               0.664          0.636
LBP_BPI_CETP             0.721         0.811    0.707     2.000              0.811         0.718   1.667               0.792          0.726
START                    0.574         0.487    0.567     3.000              0.460         0.546   4.000               0.519          0.565
lipocalin                0.558         0.299    0.563     5.000              0.215         0.584   2.000               0.679          0.487
scp2                     0.632         0.441    0.727     2.667              0.538         0.570   2.667               0.621          0.637

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.532               0.488                  0.036                     0.176
net_AUC           0.599               0.621                  0.078                     0.098

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.471                  0.044                     0.205
net_AUC_prot           0.573               0.563                  0.081                     0.099

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.607               0.581                  0.084                     0.115
net_AUC_lipid           0.594               0.597                  0.079                     0.078

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.532  0.470      0.511     0.478
10     0.532  0.551      0.511     0.547
49     0.532  0.581      0.511     0.552
51     0.532  0.593      0.511     0.559
120    0.532  0.599      0.511     0.573

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.622         0.668      0.046          0.654              0.689           0.036
10        0.622         0.660      0.038          0.654              0.688           0.035
49        0.622         0.661      0.039          0.654              0.690           0.036
51        0.622         0.673      0.050          0.654              0.689           0.035
120       0.622         0.676      0.054          0.654              0.704           0.051

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.476  0.534      0.347     0.466     0.524         0.561      0.037          0.589              0.634           0.045
GLTP          0.484  0.453      0.488     0.450     0.520         0.514     -0.005          0.547              0.561           0.014
IP_trans      0.727  0.643      0.720     0.677     0.727         0.744      0.018          0.730              0.751           0.021
LBP_BPI_CETP  0.811  0.707      0.811     0.718     0.811         0.836      0.026          0.815              0.841           0.025
START         0.487  0.567      0.460     0.546     0.513         0.607      0.094          0.561              0.637           0.076
lipocalin     0.299  0.563      0.215     0.584     0.701         0.747      0.047          0.698              0.759           0.060
scp2          0.441  0.727      0.538     0.570     0.562         0.724      0.162          0.634              0.748           0.114

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.532               0.488                  0.036                     0.176
net               0.599               0.621                  0.078                     0.098
fit_chem          0.622               0.590                  0.035                     0.121
fit_chem_net      0.676               0.701                  0.037                     0.117
increment         0.054               0.036                  0.041                     0.057

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.471                  0.044                     0.205
net_prot               0.573               0.563                  0.081                     0.099
fit_chem_prot          0.654               0.659                  0.037                     0.099
fit_chem_net_prot      0.704               0.715                  0.048                     0.096
increment_prot         0.051               0.039                  0.034                     0.036
```
