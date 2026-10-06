# descriptors_pair_only

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_pair_only'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.3104      0.5803      0.4423      0.6072      0.3761      0.6677
groups_GLTP            5      0.8320      0.2960      0.5524      0.5233      0.8846      0.4385
groups_IP_trans        5      0.4870      0.6468      0.6028      0.5072      0.5500      0.6468
groups_LBP_BPI_CETP    5      0.7739      0.5149      0.4598      0.6340      0.7750      0.5404
groups_START           5      0.4062      0.6135      0.5747      0.4829      0.4188      0.6247
groups_lipocalin       5      0.4944      0.5611      0.5327      0.5645      0.4944      0.5806
groups_scp2            5      0.7176      0.4118      0.6271      0.4787      0.7059      0.5000
ALL                   35      0.5745      0.5178      0.5417      0.5426      0.6007      0.5712

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5860      0.5607     0.0823  35
max valid BA                0.6013      0.6029     0.0825  35
best valid F1               0.5248      0.5429     0.1605  35
test BA                     0.5461      0.5208     0.0899  35
test F1                     0.4348      0.5185     0.2121  35
test sensitivity            0.5745      0.6522     0.3539  35
test specificity            0.5178      0.5319     0.2695  35
test precision              0.4039      0.4096     0.1210  34
test loss                   0.6998      0.6890     0.0618  35
FPR (FP/(FP+TN))            0.4822      0.4681     0.2695  35
FNR (FN/(FN+TP))            0.4255      0.3478     0.3539  35

=== abs(sensitivity-specificity) gap: mean=0.5201 median=0.4861 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5219      0.5232     0.0216  5
  max valid BA                0.5244      0.5232     0.0186  5
  best valid F1               0.4491      0.4696     0.1630  5
  test BA                     0.4454      0.4331     0.0458  5
  test F1                     0.2872      0.2549     0.2424  5
  test sensitivity            0.3104      0.1940     0.3782  5
  test specificity            0.5803      0.6393     0.3623  5
  test precision              0.4058      0.3827     0.0764  4
  test loss                   0.7735      0.7103     0.1418  5
  FPR (FP/(FP+TN))            0.4197      0.3607     0.3623  5
  FNR (FN/(FN+TP))            0.6896      0.8060     0.3782  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6615      0.6346     0.0375  5
  max valid BA                0.6692      0.6538     0.0316  5
  best valid F1               0.7254      0.7222     0.0383  5
  test BA                     0.5640      0.5600     0.0669  5
  test F1                     0.6532      0.6765     0.0721  5
  test sensitivity            0.8320      0.8800     0.1339  5
  test specificity            0.2960      0.3200     0.0921  5
  test precision              0.5401      0.5349     0.0452  5
  test loss                   0.6890      0.6836     0.0225  5
  FPR (FP/(FP+TN))            0.7040      0.6800     0.0921  5
  FNR (FN/(FN+TP))            0.1680      0.1200     0.1339  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5984      0.5771     0.0847  5
  max valid BA                0.6340      0.6339     0.0678  5
  best valid F1               0.5263      0.5429     0.1060  5
  test BA                     0.5669      0.5920     0.0561  5
  test F1                     0.3877      0.5000     0.1987  5
  test sensitivity            0.4870      0.6522     0.3230  5
  test specificity            0.6468      0.5957     0.2214  5
  test precision              0.3857      0.3958     0.0430  5
  test loss                   0.6739      0.6841     0.0198  5
  FPR (FP/(FP+TN))            0.3532      0.4043     0.2214  5
  FNR (FN/(FN+TP))            0.5130      0.3478     0.3230  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6577      0.6738     0.0838  5
  max valid BA                0.7004      0.7141     0.0369  5
  best valid F1               0.6134      0.6275     0.0491  5
  test BA                     0.6444      0.6383     0.1061  5
  test F1                     0.5582      0.5750     0.1145  5
  test sensitivity            0.7739      0.7391     0.2117  5
  test specificity            0.5149      0.5319     0.1751  5
  test precision              0.4468      0.4035     0.1078  5
  test loss                   0.6858      0.6874     0.0127  5
  FPR (FP/(FP+TN))            0.4851      0.4681     0.1751  5
  FNR (FN/(FN+TP))            0.2261      0.2609     0.2117  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5217      0.5163     0.0390  5
  max valid BA                0.5290      0.5469     0.0383  5
  best valid F1               0.4543      0.5248     0.1661  5
  test BA                     0.5098      0.5000     0.0337  5
  test F1                     0.3536      0.2708     0.1973  5
  test sensitivity            0.4062      0.2000     0.3838  5
  test specificity            0.6135      0.7978     0.3659  5
  test precision              0.4193      0.4221     0.0553  5
  test loss                   0.7066      0.6971     0.0308  5
  FPR (FP/(FP+TN))            0.3865      0.2022     0.3659  5
  FNR (FN/(FN+TP))            0.5938      0.8000     0.3838  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5375      0.5347     0.0817  5
  max valid BA                0.5431      0.5486     0.0775  5
  best valid F1               0.3758      0.4494     0.2081  5
  test BA                     0.5278      0.5208     0.0924  5
  test F1                     0.3320      0.4675     0.2606  5
  test sensitivity            0.4944      0.5000     0.4541  5
  test specificity            0.5611      0.6806     0.3469  5
  test precision              0.2703      0.3429     0.1920  5
  test loss                   0.6827      0.6849     0.0317  5
  FPR (FP/(FP+TN))            0.4389      0.3194     0.3469  5
  FNR (FN/(FN+TP))            0.5056      0.5000     0.4541  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6029      0.6029     0.0771  5
  max valid BA                0.6088      0.6029     0.0740  5
  best valid F1               0.5292      0.5000     0.0714  5
  test BA                     0.5647      0.5882     0.0995  5
  test F1                     0.4717      0.5217     0.1645  5
  test sensitivity            0.7176      0.8235     0.3206  5
  test specificity            0.4118      0.4412     0.1690  5
  test precision              0.3597      0.3784     0.0999  5
  test loss                   0.6871      0.6903     0.0273  5
  FPR (FP/(FP+TN))            0.5882      0.5588     0.1690  5
  FNR (FN/(FN+TP))            0.2824      0.1765     0.3206  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (aromatic_contact,chain_extent_gap,depth_bulk_match,hbond_match,hbond_match_min,occupancy,volume_fit), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.417         0.537    0.498              0.503         0.455
GLTP                     0.574         0.753    0.603              0.744         0.664
IP_trans                 0.556         0.498    0.637              0.539         0.655
LBP_BPI_CETP             0.520         0.479    0.620              0.446         0.619
START                    0.490         0.659    0.426              0.659         0.456
lipocalin                0.495         0.308    0.397              0.464         0.558
scp2                     0.429         0.599    0.562              0.638         0.551

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.548               0.557                  0.057                     0.143
net_AUC           0.535               0.538                  0.095                     0.096

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.570               0.578                  0.055                     0.112
net_AUC_pair           0.565               0.502                  0.094                     0.087

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.548  0.495       0.57     0.519
10     0.548  0.513       0.57     0.540
49     0.548  0.534       0.57     0.569
51     0.548  0.536       0.57     0.571
120    0.548  0.535       0.57     0.565

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.626         0.692      0.066
10        0.626         0.672      0.046
49        0.626         0.681      0.055
51        0.626         0.683      0.057
120       0.626         0.674      0.048

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.537  0.498      0.503     0.455     0.537         0.562      0.024
GLTP          0.753  0.603      0.744     0.664     0.753         0.797      0.044
IP_trans      0.498  0.637      0.539     0.655     0.555         0.660      0.104
LBP_BPI_CETP  0.479  0.620      0.446     0.619     0.590         0.663      0.073
START         0.659  0.426      0.659     0.456     0.659         0.680      0.021
lipocalin     0.308  0.397      0.464     0.558     0.692         0.718      0.025
scp2          0.599  0.562      0.638     0.551     0.597         0.640      0.043

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.548               0.557                  0.057                     0.143
net               0.535               0.538                  0.095                     0.096
fit_chem          0.626               0.620                  0.042                     0.078
fit_chem_net      0.674               0.667                  0.045                     0.072
increment         0.048               0.031                  0.041                     0.031

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.570               0.578                  0.055                     0.112
net_pair       0.565               0.502                  0.094                     0.087
```
