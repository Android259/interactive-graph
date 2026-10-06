# descriptors_1head_coarse

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_1head_coarse'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5403      0.5803      0.5794      0.5622      0.5851      0.5677
groups_GLTP            5      0.4000      0.5360      0.6511      0.4615      0.5000      0.6462
groups_IP_trans        5      0.5913      0.5660      0.6485      0.4928      0.7083      0.5872
groups_LBP_BPI_CETP    5      0.8609      0.7021      0.6634      0.4670      0.8583      0.7021
groups_START           5      0.5723      0.4247      0.7474      0.3539      0.5656      0.4337
groups_lipocalin       5      0.5556      0.5750      0.6771      0.5135      0.6000      0.5806
groups_scp2            5      0.6941      0.3882      0.6297      0.4751      0.7529      0.4353
ALL                   35      0.6021      0.5389      0.6567      0.4751      0.6529      0.5647

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6088      0.5962     0.0961  35
max valid BA                0.6233      0.5987     0.1039  35
best valid F1               0.5869      0.5797     0.1096  35
test BA                     0.5705      0.5400     0.1089  35
test F1                     0.5005      0.5075     0.1313  35
test sensitivity            0.6021      0.6308     0.2418  35
test specificity            0.5389      0.5745     0.2393  35
test precision              0.4693      0.4348     0.1117  35
test loss                   0.6865      0.6882     0.0333  35
FPR (FP/(FP+TN))            0.4611      0.4255     0.2393  35
FNR (FN/(FN+TP))            0.3979      0.3692     0.2418  35

=== abs(sensitivity-specificity) gap: mean=0.3433 median=0.2647 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5764      0.5676     0.0425  5
  max valid BA                0.5873      0.5879     0.0355  5
  best valid F1               0.6397      0.6279     0.0455  5
  test BA                     0.5603      0.5356     0.0471  5
  test F1                     0.5558      0.5455     0.0735  5
  test sensitivity            0.5403      0.4925     0.1445  5
  test specificity            0.5803      0.6557     0.1678  5
  test precision              0.5912      0.5593     0.0583  5
  test loss                   0.6930      0.6916     0.0115  5
  FPR (FP/(FP+TN))            0.4197      0.3443     0.1678  5
  FNR (FN/(FN+TP))            0.4597      0.5075     0.1445  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5731      0.5769     0.0583  5
  max valid BA                0.5769      0.5769     0.0527  5
  best valid F1               0.5794      0.6452     0.1356  5
  test BA                     0.4680      0.4600     0.0540  5
  test F1                     0.4114      0.4186     0.1300  5
  test sensitivity            0.4000      0.3600     0.1855  5
  test specificity            0.5360      0.5600     0.1846  5
  test precision              0.4547      0.4211     0.0583  5
  test loss                   0.7014      0.7026     0.0139  5
  FPR (FP/(FP+TN))            0.4640      0.4400     0.1846  5
  FNR (FN/(FN+TP))            0.6000      0.6400     0.1855  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6478      0.6436     0.0847  5
  max valid BA                0.6771      0.6729     0.0867  5
  best valid F1               0.6038      0.5902     0.0816  5
  test BA                     0.5786      0.5814     0.0495  5
  test F1                     0.4607      0.4918     0.0989  5
  test sensitivity            0.5913      0.6522     0.2452  5
  test specificity            0.5660      0.5745     0.1638  5
  test precision              0.3953      0.3947     0.0335  5
  test loss                   0.6790      0.6882     0.0248  5
  FPR (FP/(FP+TN))            0.4340      0.4255     0.1638  5
  FNR (FN/(FN+TP))            0.4087      0.3478     0.2452  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7802      0.7682     0.0337  5
  max valid BA                0.8079      0.7894     0.0373  5
  best valid F1               0.7390      0.7170     0.0469  5
  test BA                     0.7815      0.7632     0.0540  5
  test F1                     0.7051      0.6800     0.0669  5
  test sensitivity            0.8609      0.8261     0.0991  5
  test specificity            0.7021      0.7872     0.1799  5
  test precision              0.6145      0.6296     0.1233  5
  test loss                   0.6479      0.6657     0.0418  5
  FPR (FP/(FP+TN))            0.2979      0.2128     0.1799  5
  FNR (FN/(FN+TP))            0.1391      0.1739     0.0991  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4997      0.4846     0.0765  5
  max valid BA                0.5104      0.4963     0.0864  5
  best valid F1               0.5300      0.5517     0.0699  5
  test BA                     0.4985      0.4865     0.0655  5
  test F1                     0.4620      0.5248     0.1247  5
  test sensitivity            0.5723      0.6308     0.2692  5
  test specificity            0.4247      0.5730     0.3240  5
  test precision              0.4279      0.4062     0.0558  5
  test loss                   0.7174      0.6997     0.0430  5
  FPR (FP/(FP+TN))            0.5753      0.4270     0.3240  5
  FNR (FN/(FN+TP))            0.4277      0.3692     0.2692  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5903      0.5833     0.0264  5
  max valid BA                0.5972      0.5903     0.0303  5
  best valid F1               0.4860      0.5102     0.1079  5
  test BA                     0.5653      0.5556     0.0728  5
  test F1                     0.4400      0.4158     0.1111  5
  test sensitivity            0.5556      0.5833     0.2927  5
  test specificity            0.5750      0.6111     0.3157  5
  test precision              0.4323      0.4909     0.0891  5
  test loss                   0.6699      0.6577     0.0244  5
  FPR (FP/(FP+TN))            0.4250      0.3889     0.3157  5
  FNR (FN/(FN+TP))            0.4444      0.4167     0.2927  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5941      0.6029     0.0369  5
  max valid BA                0.6059      0.6029     0.0524  5
  best valid F1               0.5302      0.5152     0.0505  5
  test BA                     0.5412      0.5147     0.0644  5
  test F1                     0.4682      0.5000     0.0790  5
  test sensitivity            0.6941      0.7059     0.2440  5
  test specificity            0.3882      0.5294     0.2793  5
  test precision              0.3689      0.3400     0.0580  5
  test loss                   0.6971      0.6956     0.0189  5
  FPR (FP/(FP+TN))            0.6118      0.4706     0.2793  5
  FNR (FN/(FN+TP))            0.3059      0.2941     0.2440  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (aromatic_share,chain,hbond,heavy,occupancy,polar_share,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.425         0.548    0.542              0.542         0.525
GLTP                     0.424         0.685    0.541              0.667         0.552
IP_trans                 0.460         0.574    0.671              0.621         0.622
LBP_BPI_CETP             0.492         0.701    0.733              0.687         0.734
START                    0.421         0.463    0.476              0.473         0.533
lipocalin                0.363         0.645    0.516              0.652         0.686
scp2                     0.435         0.487    0.489              0.549         0.503

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.586               0.570                  0.061                     0.094
net_AUC           0.567               0.559                  0.092                     0.097

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.599               0.599                  0.061                     0.079
net_AUC_pair           0.594               0.579                  0.081                     0.089

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.586  0.505      0.599     0.522
10     0.586  0.566      0.599     0.585
49     0.586  0.571      0.599     0.595
51     0.586  0.572      0.599     0.596
120    0.586  0.567      0.599     0.594

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.607         0.670      0.063
10        0.607         0.665      0.058
49        0.607         0.663      0.056
51        0.607         0.661      0.054
120       0.607         0.663      0.057

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.548  0.542      0.542     0.525     0.555         0.570      0.015
GLTP          0.685  0.541      0.667     0.552     0.680         0.713      0.033
IP_trans      0.574  0.671      0.621     0.622     0.574         0.701      0.127
LBP_BPI_CETP  0.701  0.733      0.687     0.734     0.701         0.774      0.073
START         0.463  0.476      0.473     0.533     0.546         0.591      0.045
lipocalin     0.645  0.516      0.652     0.686     0.645         0.674      0.030
scp2          0.487  0.489      0.549     0.503     0.547         0.620      0.074

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.586               0.570                  0.061                     0.094
net               0.567               0.559                  0.092                     0.097
fit_chem          0.607               0.582                  0.055                     0.067
fit_chem_net      0.663               0.655                  0.062                     0.073
increment         0.057               0.041                  0.064                     0.038

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.599               0.599                  0.061                     0.079
net_pair       0.594               0.579                  0.081                     0.089
```
