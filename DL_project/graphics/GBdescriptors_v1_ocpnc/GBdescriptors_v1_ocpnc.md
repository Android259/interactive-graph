# GBdescriptors_v1_ocpnc

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'GBdescriptors_v1_ocpnc'
rows: 16

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.3085      0.6230      0.6457      0.4433      0.3433      0.6828
groups_GLTP            3      0.7467      0.3467      0.6801      0.4597      0.7692      0.4615
groups_IP_trans        2      0.5000      0.6489      0.6694      0.4945      0.6042      0.6064
groups_LBP_BPI_CETP    1      0.9565      0.4043      0.6211      0.5515      0.8750      0.5106
groups_ML              1      0.8000      0.3000      0.7101      0.5773      1.0000      0.2000
groups_OSBP            2      0.5000      0.5833      0.5291      0.5205      0.8333      0.6667
groups_START           2      0.5692      0.5562      0.5648      0.4735      0.6328      0.5281
groups_lipocalin       1      0.5278      0.2222      0.7187      0.4771      0.5833      0.3056
groups_scp2            1      0.7647      0.4412      0.6151      0.4935      0.6471      0.5882
ALL                   16      0.5846      0.4908      0.6356      0.4866      0.6615      0.5400

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6007      0.6071     0.0927  16
max valid BA                0.6293      0.6071     0.0935  16
best valid F1               0.6260      0.6395     0.0925  16
test BA                     0.5377      0.5459     0.1073  16
test F1                     0.4590      0.5042     0.1941  16
test sensitivity            0.5846      0.6395     0.3167  16
test specificity            0.4908      0.4800     0.2089  16
test precision              0.4180      0.4343     0.1364  16
test loss                   0.7062      0.6959     0.0346  16
FPR (FP/(FP+TN))            0.5092      0.5200     0.2089  16
FNR (FN/(FN+TP))            0.4154      0.3605     0.3167  16

=== abs(sensitivity-specificity) gap: mean=0.4297 median=0.4224 n=16 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5130      0.5138     0.0106  3
  max valid BA                0.5355      0.5433     0.0303  3
  best valid F1               0.6773      0.6837     0.0123  3
  test BA                     0.4657      0.4792     0.0367  3
  test F1                     0.3292      0.2718     0.2155  3
  test sensitivity            0.3085      0.2090     0.2821  3
  test specificity            0.6230      0.6393     0.2545  3
  test precision              0.4453      0.4286     0.0664  3
  test loss                   0.7348      0.7175     0.0478  3
  FPR (FP/(FP+TN))            0.3770      0.3607     0.2545  3
  FNR (FN/(FN+TP))            0.6915      0.7910     0.2821  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6154      0.6346     0.0509  3
  max valid BA                0.6538      0.6923     0.0666  3
  best valid F1               0.6930      0.7027     0.0369  3
  test BA                     0.5467      0.5400     0.0702  3
  test F1                     0.6105      0.6667     0.1134  3
  test sensitivity            0.7467      0.7600     0.2603  3
  test specificity            0.3467      0.4800     0.2309  3
  test precision              0.5315      0.5208     0.0576  3
  test loss                   0.6827      0.6663     0.0304  3
  FPR (FP/(FP+TN))            0.6533      0.5200     0.2309  3
  FNR (FN/(FN+TP))            0.2533      0.2400     0.2603  3

groups_IP_trans (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6053      0.6053     0.0699  2
  max valid BA                0.6727      0.6727     0.1219  2
  best valid F1               0.6097      0.6097     0.1007  2
  test BA                     0.5745      0.5745     0.0399  2
  test F1                     0.4403      0.4403     0.0964  2
  test sensitivity            0.5000      0.5000     0.2152  2
  test specificity            0.6489      0.6489     0.1354  2
  test precision              0.4083      0.4083     0.0118  2
  test loss                   0.6790      0.6790     0.0076  2
  FPR (FP/(FP+TN))            0.3511      0.3511     0.1354  2
  FNR (FN/(FN+TP))            0.5000      0.5000     0.2152  2

groups_LBP_BPI_CETP (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6928      0.6928     0.0000  1
  max valid BA                0.7048      0.7048     0.0000  1
  best valid F1               0.6269      0.6269     0.0000  1
  test BA                     0.6804      0.6804     0.0000  1
  test F1                     0.6027      0.6027     0.0000  1
  test sensitivity            0.9565      0.9565     0.0000  1
  test specificity            0.4043      0.4043     0.0000  1
  test precision              0.4400      0.4400     0.0000  1
  test loss                   0.6838      0.6838     0.0000  1
  FPR (FP/(FP+TN))            0.5957      0.5957     0.0000  1
  FNR (FN/(FN+TP))            0.0435      0.0435     0.0000  1

groups_ML (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6000      0.6000     0.0000  1
  max valid BA                0.6000      0.6000     0.0000  1
  best valid F1               0.5556      0.5556     0.0000  1
  test BA                     0.5500      0.5500     0.0000  1
  test F1                     0.5000      0.5000     0.0000  1
  test sensitivity            0.8000      0.8000     0.0000  1
  test specificity            0.3000      0.3000     0.0000  1
  test precision              0.3636      0.3636     0.0000  1
  test loss                   0.7354      0.7354     0.0000  1
  FPR (FP/(FP+TN))            0.7000      0.7000     0.0000  1
  FNR (FN/(FN+TP))            0.2000      0.2000     0.0000  1

groups_OSBP (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7500      0.7500     0.1179  2
  max valid BA                0.7500      0.7500     0.1179  2
  best valid F1               0.7000      0.7000     0.1414  2
  test BA                     0.5417      0.5417     0.2946  2
  test F1                     0.3333      0.3333     0.4714  2
  test sensitivity            0.5000      0.5000     0.7071  2
  test specificity            0.5833      0.5833     0.1179  2
  test precision              0.2500      0.2500     0.3536  2
  test loss                   0.6930      0.6930     0.0009  2
  FPR (FP/(FP+TN))            0.4167      0.4167     0.1179  2
  FNR (FN/(FN+TP))            0.5000      0.5000     0.7071  2

groups_START (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5805      0.5805     0.0477  2
  max valid BA                0.5872      0.5872     0.0382  2
  best valid F1               0.5511      0.5511     0.0535  2
  test BA                     0.5627      0.5627     0.0241  2
  test F1                     0.5007      0.5007     0.1372  2
  test sensitivity            0.5692      0.5692     0.3264  2
  test specificity            0.5562      0.5562     0.2781  2
  test precision              0.4885      0.4885     0.0162  2
  test loss                   0.7207      0.7207     0.0046  2
  FPR (FP/(FP+TN))            0.4438      0.4438     0.2781  2
  FNR (FN/(FN+TP))            0.4308      0.4308     0.3264  2

groups_lipocalin (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4444      0.4444     0.0000  1
  max valid BA                0.5000      0.5000     0.0000  1
  best valid F1               0.4231      0.4231     0.0000  1
  test BA                     0.3750      0.3750     0.0000  1
  test F1                     0.3423      0.3423     0.0000  1
  test sensitivity            0.5278      0.5278     0.0000  1
  test specificity            0.2222      0.2222     0.0000  1
  test precision              0.2533      0.2533     0.0000  1
  test loss                   0.7616      0.7616     0.0000  1
  FPR (FP/(FP+TN))            0.7778      0.7778     0.0000  1
  FNR (FN/(FN+TP))            0.4722      0.4722     0.0000  1

groups_scp2 (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6176      0.6176     0.0000  1
  max valid BA                0.6765      0.6765     0.0000  1
  best valid F1               0.5789      0.5789     0.0000  1
  test BA                     0.6029      0.6029     0.0000  1
  test F1                     0.5306      0.5306     0.0000  1
  test sensitivity            0.7647      0.7647     0.0000  1
  test specificity            0.4412      0.4412     0.0000  1
  test precision              0.4062      0.4062     0.0000  1
  test loss                   0.6807      0.6807     0.0000  1
  FPR (FP/(FP+TN))            0.5588      0.5588     0.0000  1
  FNR (FN/(FN+TP))            0.2353      0.2353     0.0000  1
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (aromatic_contact,aromatic_share,buriedness_q50,chain,chain_extent_gap,depth_q10,ev14_q50,hbond,hbond_match,heavy,hydropathy_rim,occupancy,pocket_elongation,pocket_extent,pocket_flatness,polar_share,tail_count,tail_elongation_fit,unsaturation,volume_fit), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.205         0.570    0.495              0.517         0.574
GLTP                     0.232         0.774    0.541              0.806         0.498
IP_trans                 0.257         0.619    0.572              0.672         0.583
LBP_BPI_CETP             0.263         0.627    0.580              0.616         0.599
START                    0.221         0.478    0.417              0.496         0.428
lipocalin                0.212         0.609    0.355              0.593         0.453
scp2                     0.198         0.600    0.595              0.596         0.491

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.611               0.613                  0.052                     0.088
net_AUC           0.508               0.510                  0.082                     0.091

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.614               0.602                  0.055                     0.104
net_AUC_pair           0.518               0.514                  0.105                     0.067

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.611  0.491      0.614     0.477
10     0.611  0.513      0.614     0.499
49     0.611  0.514      0.614     0.515
51     0.611  0.525      0.614     0.520
120    0.611  0.508      0.614     0.518

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.619         0.681      0.061
10        0.619         0.666      0.047
49        0.619         0.664      0.044
51        0.619         0.663      0.043
120       0.619         0.662      0.043

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.570  0.495      0.517     0.574     0.570         0.578      0.008
GLTP          0.774  0.541      0.806     0.498     0.774         0.782      0.008
IP_trans      0.619  0.572      0.672     0.583     0.619         0.670      0.052
LBP_BPI_CETP  0.627  0.580      0.616     0.599     0.627         0.668      0.041
START         0.478  0.417      0.496     0.428     0.537         0.595      0.058
lipocalin     0.609  0.355      0.593     0.453     0.609         0.715      0.106
scp2          0.600  0.595      0.596     0.491     0.600         0.627      0.027

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.611               0.613                  0.052                     0.088
net               0.508               0.510                  0.082                     0.091
fit_chem          0.619               0.613                  0.050                     0.075
fit_chem_net      0.662               0.660                  0.072                     0.071
increment         0.043               0.024                  0.048                     0.034

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.614               0.602                  0.055                     0.104
net_pair       0.518               0.514                  0.105                     0.067
```
