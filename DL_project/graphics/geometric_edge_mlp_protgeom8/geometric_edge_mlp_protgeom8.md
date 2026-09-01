# geometric_edge_mlp_protgeom8

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom8'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6985      0.4230      0.6446      0.6161      0.7373      0.4097
groups_GLTP            5      0.4960      0.5440      0.6900      0.5602      0.5462      0.6538
groups_IP_trans        5      0.4957      0.7574      0.7366      0.6107      0.5917      0.7191
groups_LBP_BPI_CETP    5      0.4870      0.7787      0.5680      0.5704      0.5583      0.7277
groups_START           5      0.6862      0.5213      0.8464      0.5802      0.7094      0.5079
groups_lipocalin       5      0.6778      0.7194      0.6752      0.5287      0.7278      0.7056
groups_scp2            5      0.3882      0.7412      0.8026      0.6297      0.4706      0.7882
ALL                   35      0.5613      0.6407      0.7091      0.5852      0.6202      0.6446

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6324      0.6175     0.0714  35
max valid BA                0.6695      0.6520     0.0692  35
best valid F1               0.6427      0.6531     0.0727  35
test BA                     0.6010      0.5882     0.0905  35
test F1                     0.5163      0.5556     0.1529  35
test sensitivity            0.5613      0.5882     0.2290  35
test specificity            0.6407      0.6596     0.1992  35
test precision              0.5163      0.5000     0.1318  35
test loss                   0.6950      0.6856     0.0753  35
FPR (FP/(FP+TN))            0.3593      0.3404     0.1992  35
FNR (FN/(FN+TP))            0.4387      0.4118     0.2290  35

=== abs(sensitivity-specificity) gap: mean=0.3129 median=0.2800 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5735      0.5837     0.0315  5
  max valid BA                0.6001      0.6068     0.0221  5
  best valid F1               0.7071      0.7065     0.0144  5
  test BA                     0.5607      0.5700     0.0262  5
  test F1                     0.6178      0.6027     0.0813  5
  test sensitivity            0.6985      0.6567     0.2039  5
  test specificity            0.4230      0.4262     0.1860  5
  test precision              0.5729      0.5648     0.0277  5
  test loss                   0.7056      0.6869     0.0297  5
  FPR (FP/(FP+TN))            0.5770      0.5738     0.1860  5
  FNR (FN/(FN+TP))            0.3015      0.3433     0.2039  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6000      0.5962     0.0672  5
  max valid BA                0.6500      0.6538     0.0551  5
  best valid F1               0.7094      0.7143     0.0295  5
  test BA                     0.5200      0.4600     0.1122  5
  test F1                     0.4911      0.5263     0.1458  5
  test sensitivity            0.4960      0.4000     0.2508  5
  test specificity            0.5440      0.5200     0.3001  5
  test precision              0.5668      0.4688     0.2475  5
  test loss                   0.7128      0.7137     0.0262  5
  FPR (FP/(FP+TN))            0.4560      0.4800     0.3001  5
  FNR (FN/(FN+TP))            0.5040      0.6000     0.2508  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6554      0.6649     0.0484  5
  max valid BA                0.7159      0.7061     0.0534  5
  best valid F1               0.6322      0.6207     0.0557  5
  test BA                     0.6265      0.6559     0.0857  5
  test F1                     0.4687      0.5556     0.1945  5
  test sensitivity            0.4957      0.5652     0.2432  5
  test specificity            0.7574      0.7234     0.1091  5
  test precision              0.4756      0.4839     0.1298  5
  test loss                   0.6719      0.6576     0.0713  5
  FPR (FP/(FP+TN))            0.2426      0.2766     0.1091  5
  FNR (FN/(FN+TP))            0.5043      0.4348     0.2432  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6430      0.5988     0.1003  5
  max valid BA                0.6767      0.6520     0.1063  5
  best valid F1               0.5895      0.5778     0.1124  5
  test BA                     0.6328      0.6346     0.1304  5
  test F1                     0.4483      0.5357     0.2589  5
  test sensitivity            0.4870      0.5652     0.3401  5
  test specificity            0.7787      0.7660     0.1317  5
  test precision              0.4782      0.4545     0.1428  5
  test loss                   0.7174      0.6814     0.1454  5
  FPR (FP/(FP+TN))            0.2213      0.2340     0.1317  5
  FNR (FN/(FN+TP))            0.5130      0.4348     0.3401  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6086      0.6175     0.0283  5
  max valid BA                0.6300      0.6232     0.0192  5
  best valid F1               0.6284      0.6294     0.0169  5
  test BA                     0.6038      0.5800     0.0498  5
  test F1                     0.5827      0.5677     0.0641  5
  test sensitivity            0.6862      0.6769     0.1248  5
  test specificity            0.5213      0.5393     0.0760  5
  test precision              0.5105      0.4951     0.0360  5
  test loss                   0.6885      0.6903     0.0148  5
  FPR (FP/(FP+TN))            0.4787      0.4607     0.0760  5
  FNR (FN/(FN+TP))            0.3138      0.3231     0.1248  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7167      0.7083     0.0193  5
  max valid BA                0.7347      0.7431     0.0257  5
  best valid F1               0.6493      0.6588     0.0298  5
  test BA                     0.6986      0.7083     0.0493  5
  test F1                     0.6046      0.5965     0.0520  5
  test sensitivity            0.6778      0.7222     0.1451  5
  test specificity            0.7194      0.7083     0.1461  5
  test precision              0.5807      0.5532     0.1369  5
  test loss                   0.6472      0.6782     0.0660  5
  FPR (FP/(FP+TN))            0.2806      0.2917     0.1461  5
  FNR (FN/(FN+TP))            0.3222      0.2778     0.1451  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6294      0.6176     0.0909  5
  max valid BA                0.6794      0.6471     0.0731  5
  best valid F1               0.5832      0.5652     0.0882  5
  test BA                     0.5647      0.5735     0.0354  5
  test F1                     0.4011      0.4138     0.0704  5
  test sensitivity            0.3882      0.3529     0.1220  5
  test specificity            0.7412      0.7353     0.0789  5
  test precision              0.4292      0.4348     0.0511  5
  test loss                   0.7219      0.6736     0.1008  5
  FPR (FP/(FP+TN))            0.2588      0.2647     0.0789  5
  FNR (FN/(FN+TP))            0.6118      0.6471     0.1220  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.630         0.483    0.572       4.0              0.365         0.503     5.0               0.449          0.608
GLTP                     0.605         0.521    0.502       2.0              0.511         0.489     3.0               0.523          0.557
IP_trans                 0.722         0.681    0.649       3.0              0.677         0.704     2.4               0.590          0.625
LBP_BPI_CETP             0.719         0.798    0.712       2.0              0.798         0.716     1.6               0.784          0.712
START                    0.576         0.508    0.574       3.0              0.475         0.522     4.0               0.535          0.594
lipocalin                0.565         0.334    0.616       5.0              0.252         0.648     2.2               0.647          0.540
scp2                     0.651         0.488    0.700       2.8              0.592         0.573     2.6               0.649          0.647

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.545               0.499                  0.066                     0.151
net_AUC           0.618               0.643                  0.082                     0.075

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.524               0.493                  0.065                     0.185
net_AUC_prot           0.594               0.595                  0.098                     0.096

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.597               0.581                  0.085                     0.109
net_AUC_lipid           0.612               0.610                  0.117                     0.058

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.493      0.524     0.502
10     0.545  0.561      0.524     0.560
49     0.545  0.582      0.524     0.565
51     0.545  0.599      0.524     0.578
120    0.545  0.618      0.524     0.594

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.619         0.670      0.051          0.655              0.691           0.036
10        0.619         0.664      0.045          0.655              0.691           0.036
49        0.619         0.667      0.048          0.655              0.692           0.037
51        0.619         0.673      0.054          0.655              0.693           0.038
120       0.619         0.676      0.057          0.655              0.700           0.045

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.483  0.572      0.365     0.503     0.539         0.575      0.036          0.614              0.644           0.030
GLTP          0.521  0.502      0.511     0.489     0.542         0.566      0.024          0.565              0.576           0.010
IP_trans      0.681  0.649      0.677     0.704     0.681         0.716      0.036          0.692              0.732           0.040
LBP_BPI_CETP  0.798  0.712      0.798     0.716     0.798         0.813      0.015          0.801              0.815           0.014
START         0.508  0.574      0.475     0.522     0.536         0.623      0.087          0.604              0.657           0.053
lipocalin     0.334  0.616      0.252     0.648     0.666         0.735      0.069          0.672              0.749           0.077
scp2          0.488  0.700      0.592     0.573     0.572         0.703      0.131          0.636              0.727           0.091

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.545               0.499                  0.066                     0.151
net               0.618               0.643                  0.082                     0.075
fit_chem          0.619               0.580                  0.052                     0.100
fit_chem_net      0.676               0.693                  0.057                     0.091
increment         0.057               0.043                  0.044                     0.041

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.524               0.493                  0.065                     0.185
net_prot               0.594               0.595                  0.098                     0.096
fit_chem_prot          0.655               0.658                  0.053                     0.077
fit_chem_net_prot      0.700               0.697                  0.053                     0.079
increment_prot         0.045               0.037                  0.032                     0.030
```
