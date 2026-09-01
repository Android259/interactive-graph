# descriptors_no_extent_coarse_add_dpt005

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_add_dpt005'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4119      0.5803      0.5617      0.5830      0.5104      0.6452
groups_GLTP            5      0.4240      0.6240      0.6347      0.4681      0.4615      0.7154
groups_IP_trans        5      0.5217      0.6723      0.6766      0.5077      0.6500      0.6426
groups_LBP_BPI_CETP    5      0.7913      0.7106      0.6613      0.4851      0.8667      0.6553
groups_START           5      0.5538      0.5596      0.6887      0.4447      0.5719      0.5730
groups_lipocalin       5      0.6278      0.5833      0.7107      0.4602      0.6000      0.5722
groups_scp2            5      0.6235      0.4235      0.6499      0.4426      0.6706      0.4824
ALL                   35      0.5649      0.5934      0.6548      0.4845      0.6187      0.6123

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6161      0.5973     0.0824  35
max valid BA                0.6298      0.6053     0.0860  35
best valid F1               0.5820      0.5763     0.1010  35
test BA                     0.5791      0.5764     0.1066  35
test F1                     0.4882      0.5098     0.1461  35
test sensitivity            0.5649      0.5882     0.2555  35
test specificity            0.5934      0.6765     0.2189  35
test precision              0.4785      0.4783     0.1141  35
test loss                   0.6866      0.6833     0.0312  35
FPR (FP/(FP+TN))            0.4066      0.3235     0.2189  35
FNR (FN/(FN+TP))            0.4351      0.4118     0.2555  35

=== abs(sensitivity-specificity) gap: mean=0.3477 median=0.3452 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5778      0.5725     0.0154  5
  max valid BA                0.5883      0.5900     0.0220  5
  best valid F1               0.6253      0.6500     0.0628  5
  test BA                     0.4961      0.5005     0.0155  5
  test F1                     0.4379      0.4220     0.1308  5
  test sensitivity            0.4119      0.3433     0.2004  5
  test specificity            0.5803      0.6885     0.1962  5
  test precision              0.5145      0.5238     0.0321  5
  test loss                   0.6935      0.6927     0.0063  5
  FPR (FP/(FP+TN))            0.4197      0.3115     0.1962  5
  FNR (FN/(FN+TP))            0.5881      0.6567     0.2004  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5923      0.5577     0.0786  5
  max valid BA                0.6000      0.5769     0.0737  5
  best valid F1               0.5914      0.6230     0.1343  5
  test BA                     0.5240      0.4800     0.1108  5
  test F1                     0.4351      0.3590     0.2057  5
  test sensitivity            0.4240      0.2800     0.3001  5
  test specificity            0.6240      0.6400     0.1220  5
  test precision              0.4949      0.4800     0.0986  5
  test loss                   0.6958      0.7010     0.0160  5
  FPR (FP/(FP+TN))            0.3760      0.3600     0.1220  5
  FNR (FN/(FN+TP))            0.5760      0.7200     0.3001  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6463      0.6436     0.0442  5
  max valid BA                0.6595      0.6441     0.0471  5
  best valid F1               0.5694      0.5556     0.0483  5
  test BA                     0.5970      0.6230     0.0595  5
  test F1                     0.4626      0.5098     0.1177  5
  test sensitivity            0.5217      0.5652     0.1895  5
  test specificity            0.6723      0.6809     0.0859  5
  test precision              0.4281      0.4444     0.0664  5
  test loss                   0.6732      0.6810     0.0190  5
  FPR (FP/(FP+TN))            0.3277      0.3191     0.0859  5
  FNR (FN/(FN+TP))            0.4783      0.4348     0.1895  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7610      0.7770     0.0518  5
  max valid BA                0.7851      0.7788     0.0525  5
  best valid F1               0.7160      0.7037     0.0638  5
  test BA                     0.7510      0.7655     0.0913  5
  test F1                     0.6657      0.6769     0.1026  5
  test sensitivity            0.7913      0.7826     0.1455  5
  test specificity            0.7106      0.7660     0.1171  5
  test precision              0.5824      0.6154     0.1085  5
  test loss                   0.6532      0.6628     0.0316  5
  FPR (FP/(FP+TN))            0.2894      0.2340     0.1171  5
  FNR (FN/(FN+TP))            0.2087      0.2174     0.1455  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5725      0.6030     0.0920  5
  max valid BA                0.5858      0.6210     0.0999  5
  best valid F1               0.5725      0.5800     0.0523  5
  test BA                     0.5567      0.5990     0.0841  5
  test F1                     0.5047      0.5378     0.0937  5
  test sensitivity            0.5538      0.5077     0.2015  5
  test specificity            0.5596      0.7303     0.3001  5
  test precision              0.5019      0.5056     0.0883  5
  test loss                   0.7054      0.6817     0.0470  5
  FPR (FP/(FP+TN))            0.4404      0.2697     0.3001  5
  FNR (FN/(FN+TP))            0.4462      0.4923     0.2015  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5861      0.5764     0.0356  5
  max valid BA                0.5986      0.6042     0.0300  5
  best valid F1               0.4831      0.5116     0.1077  5
  test BA                     0.6056      0.5972     0.0415  5
  test F1                     0.4869      0.5354     0.0944  5
  test sensitivity            0.6278      0.7500     0.3146  5
  test specificity            0.5833      0.5972     0.3147  5
  test precision              0.4881      0.4783     0.1356  5
  test loss                   0.6760      0.6819     0.0199  5
  FPR (FP/(FP+TN))            0.4167      0.4028     0.3147  5
  FNR (FN/(FN+TP))            0.3722      0.2500     0.3146  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5765      0.5588     0.0395  5
  max valid BA                0.5912      0.6029     0.0319  5
  best valid F1               0.5160      0.5172     0.0323  5
  test BA                     0.5235      0.5294     0.0910  5
  test F1                     0.4245      0.4762     0.1661  5
  test sensitivity            0.6235      0.6471     0.3129  5
  test specificity            0.4235      0.4706     0.2826  5
  test precision              0.3397      0.3488     0.1185  5
  test loss                   0.7092      0.7053     0.0317  5
  FPR (FP/(FP+TN))            0.5765      0.5294     0.2826  5
  FNR (FN/(FN+TP))            0.3765      0.3529     0.3129  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (aromatic_share,chain,hbond,heavy,occupancy,polar_share,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.425         0.548    0.538              0.542         0.514
GLTP                     0.424         0.685    0.513              0.667         0.524
IP_trans                 0.460         0.574    0.687              0.621         0.655
LBP_BPI_CETP             0.492         0.701    0.734              0.687         0.746
START                    0.421         0.463    0.558              0.473         0.576
lipocalin                0.363         0.645    0.492              0.652         0.680
scp2                     0.435         0.487    0.435              0.549         0.475

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.586               0.570                  0.061                     0.094
net_AUC           0.565               0.567                  0.080                     0.107

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.599               0.599                  0.061                     0.079
net_AUC_pair           0.596               0.587                  0.076                     0.100

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.586  0.515      0.599     0.533
10     0.586  0.580      0.599     0.600
49     0.586  0.559      0.599     0.586
51     0.586  0.557      0.599     0.585
120    0.586  0.565      0.599     0.596

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.607         0.671      0.065
10        0.607         0.670      0.064
49        0.607         0.668      0.061
51        0.607         0.668      0.061
120       0.607         0.666      0.059

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.548  0.538      0.542     0.514     0.555         0.567      0.012
GLTP          0.685  0.513      0.667     0.524     0.680         0.688      0.008
IP_trans      0.574  0.687      0.621     0.655     0.574         0.739      0.165
LBP_BPI_CETP  0.701  0.734      0.687     0.746     0.701         0.767      0.066
START         0.463  0.558      0.473     0.576     0.546         0.619      0.074
lipocalin     0.645  0.492      0.652     0.680     0.645         0.674      0.029
scp2          0.487  0.435      0.549     0.475     0.547         0.608      0.062

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.586               0.570                  0.061                     0.094
net               0.565               0.567                  0.080                     0.107
fit_chem          0.607               0.582                  0.055                     0.067
fit_chem_net      0.666               0.649                  0.051                     0.072
increment         0.059               0.038                  0.044                     0.053

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.599               0.599                  0.061                     0.079
net_pair       0.596               0.587                  0.076                     0.100
```
