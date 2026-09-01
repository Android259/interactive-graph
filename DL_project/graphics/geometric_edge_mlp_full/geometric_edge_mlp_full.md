# geometric_edge_mlp_full

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_full'
rows: 21

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.6667      0.3333      0.7410      0.2685      0.6667      0.3333
groups_GLTP            3      0.6667      0.3333      0.7688      0.2318      0.6667      0.3333
groups_IP_trans        3      1.0000      0.0355      0.6979      0.3017      0.9861      0.0426
groups_LBP_BPI_CETP    3      0.5507      0.5177      0.5816      0.4128      0.5694      0.5248
groups_START           3      0.9590      0.1273      0.7998      0.1945      0.9323      0.1086
groups_lipocalin       3      0.7407      0.2222      0.8135      0.1942      0.7500      0.2546
groups_scp2            3      0.6471      0.3431      0.5986      0.3885      0.7059      0.4412
ALL                   21      0.7473      0.2732      0.7144      0.2846      0.7539      0.2912

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5225      0.5000     0.0400  21
max valid BA                0.5240      0.5000     0.0397  21
best valid F1               0.5688      0.5227     0.0755  21
test BA                     0.5102      0.5000     0.0399  21
test F1                     0.4522      0.5000     0.2217  21
test sensitivity            0.7473      1.0000     0.3973  21
test specificity            0.2732      0.0000     0.3878  21
test precision              0.3933      0.3538     0.0943  19
test loss                   0.7191      0.6935     0.0404  21
FPR (FP/(FP+TN))            0.7268      1.0000     0.3878  21
FNR (FN/(FN+TP))            0.2527      0.0000     0.3973  21

=== abs(sensitivity-specificity) gap: mean=0.8603 median=1.0000 n=21 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0000  3
  max valid BA                0.5000      0.5000     0.0000  3
  best valid F1               0.6837      0.6837     0.0000  3
  test BA                     0.5000      0.5000     0.0000  3
  test F1                     0.4581      0.6872     0.3967  3
  test sensitivity            0.6667      1.0000     0.5774  3
  test specificity            0.3333      0.0000     0.5774  3
  test precision              0.5234      0.5234     0.0000  2
  test loss                   0.6979      0.6933     0.0089  3
  FPR (FP/(FP+TN))            0.6667      1.0000     0.5774  3
  FNR (FN/(FN+TP))            0.3333      0.0000     0.5774  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0000  3
  max valid BA                0.5000      0.5000     0.0000  3
  best valid F1               0.6667      0.6667     0.0000  3
  test BA                     0.5000      0.5000     0.0000  3
  test F1                     0.4444      0.6667     0.3849  3
  test sensitivity            0.6667      1.0000     0.5774  3
  test specificity            0.3333      0.0000     0.5774  3
  test precision              0.5000      0.5000     0.0000  2
  test loss                   0.6998      0.6940     0.0107  3
  FPR (FP/(FP+TN))            0.6667      1.0000     0.5774  3
  FNR (FN/(FN+TP))            0.3333      0.0000     0.5774  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5143      0.5000     0.0248  3
  max valid BA                0.5242      0.5297     0.0220  3
  best valid F1               0.5129      0.5106     0.0089  3
  test BA                     0.5177      0.5000     0.0307  3
  test F1                     0.5040      0.4946     0.0162  3
  test sensitivity            1.0000      1.0000     0.0000  3
  test specificity            0.0355      0.0000     0.0614  3
  test precision              0.3370      0.3286     0.0146  3
  test loss                   0.7258      0.6935     0.0563  3
  FPR (FP/(FP+TN))            0.9645      1.0000     0.0614  3
  FNR (FN/(FN+TP))            0.0000      0.0000     0.0000  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5471      0.5417     0.0501  3
  max valid BA                0.5471      0.5417     0.0501  3
  best valid F1               0.5083      0.5053     0.0052  3
  test BA                     0.5342      0.5111     0.0500  3
  test F1                     0.3553      0.4912     0.2384  3
  test sensitivity            0.5507      0.6087     0.4809  3
  test specificity            0.5177      0.5745     0.4918  3
  test precision              0.4134      0.4118     0.0857  3
  test loss                   0.7272      0.6931     0.0590  3
  FPR (FP/(FP+TN))            0.4823      0.4255     0.4918  3
  FNR (FN/(FN+TP))            0.4493      0.3913     0.4809  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5205      0.5000     0.0354  3
  max valid BA                0.5205      0.5000     0.0354  3
  best valid F1               0.5899      0.5899     0.0000  3
  test BA                     0.5432      0.5000     0.0748  3
  test F1                     0.6104      0.5936     0.0291  3
  test sensitivity            0.9590      1.0000     0.0711  3
  test specificity            0.1273      0.0000     0.2206  3
  test precision              0.4510      0.4221     0.0501  3
  test loss                   0.7208      0.7070     0.0366  3
  FPR (FP/(FP+TN))            0.8727      1.0000     0.2206  3
  FNR (FN/(FN+TP))            0.0410      0.0000     0.0711  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5023      0.5000     0.0040  3
  max valid BA                0.5023      0.5000     0.0040  3
  best valid F1               0.5000      0.5000     0.0000  3
  test BA                     0.4815      0.5000     0.0321  3
  test F1                     0.4118      0.5000     0.1528  3
  test sensitivity            0.7407      1.0000     0.4491  3
  test specificity            0.2222      0.0000     0.3849  3
  test precision              0.3056      0.3333     0.0481  3
  test loss                   0.7396      0.7196     0.0591  3
  FPR (FP/(FP+TN))            0.7778      1.0000     0.3849  3
  FNR (FN/(FN+TP))            0.2593      0.0000     0.4491  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5735      0.5882     0.0674  3
  max valid BA                0.5735      0.5882     0.0674  3
  best valid F1               0.5200      0.5000     0.0346  3
  test BA                     0.4951      0.5000     0.0370  3
  test F1                     0.3817      0.4912     0.1974  3
  test sensitivity            0.6471      0.8235     0.4669  3
  test specificity            0.3431      0.2353     0.4079  3
  test precision              0.3019      0.3333     0.0695  3
  test loss                   0.7228      0.6932     0.0514  3
  FPR (FP/(FP+TN))            0.6569      0.7647     0.4079  3
  FNR (FN/(FN+TP))            0.3529      0.1765     0.4669  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.475    0.500     4.000              0.348           0.5   5.000               0.467            0.5
GLTP                     0.595         0.484    0.500     2.000              0.488           0.5   3.000               0.494            0.5
IP_trans                 0.727         0.726    0.500     3.000              0.719           0.5   2.667               0.664            0.5
LBP_BPI_CETP             0.721         0.811    0.500     2.000              0.812           0.5   1.667               0.792            0.5
START                    0.574         0.487    0.499     3.000              0.461           0.5   4.000               0.517            0.5
lipocalin                0.558         0.302    0.500     5.000              0.222           0.5   2.000               0.681            0.5
scp2                     0.632         0.430    0.500     2.667              0.528           0.5   2.667               0.630            0.5

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.531               0.487                  0.032                     0.176
net_AUC           0.500               0.500                  0.000                     0.000

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.472                  0.041                     0.203
net_AUC_prot           0.500               0.500                  0.000                     0.000

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.606               0.581                  0.084                     0.119
net_AUC_lipid           0.500               0.500                  0.000                     0.000

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.531  0.526      0.511     0.499
10     0.531  0.534      0.511     0.506
49     0.531  0.555      0.511     0.552
51     0.531  0.545      0.511     0.549
120    0.531  0.500      0.511     0.500

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.623         0.664      0.041          0.656              0.687           0.031
10        0.623         0.653      0.029          0.656              0.682           0.026
49        0.623         0.655      0.032          0.656              0.677           0.021
51        0.623         0.647      0.024          0.656              0.678           0.022
120       0.623         0.623      0.000          0.656              0.656           0.000

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.475  0.500      0.348       0.5     0.525         0.525      0.000          0.589              0.589             0.0
GLTP          0.484  0.500      0.488       0.5     0.519         0.519      0.000          0.547              0.547             0.0
IP_trans      0.726  0.500      0.719       0.5     0.726         0.726      0.000          0.729              0.729             0.0
LBP_BPI_CETP  0.811  0.500      0.812       0.5     0.811         0.811      0.000          0.815              0.815             0.0
START         0.487  0.499      0.461       0.5     0.513         0.514      0.001          0.559              0.560             0.0
lipocalin     0.302  0.500      0.222       0.5     0.698         0.698      0.000          0.696              0.696             0.0
scp2          0.430  0.500      0.528       0.5     0.570         0.570      0.000          0.655              0.655             0.0

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.531               0.487                  0.032                     0.176
net               0.500               0.500                  0.000                     0.000
fit_chem          0.623               0.580                  0.031                     0.120
fit_chem_net      0.623               0.580                  0.031                     0.120
increment         0.000               0.000                  0.000                     0.000

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.472                  0.041                     0.203
net_prot               0.500               0.500                  0.000                     0.000
fit_chem_prot          0.656               0.655                  0.032                     0.098
fit_chem_net_prot      0.656               0.655                  0.032                     0.098
increment_prot         0.000               0.000                  0.000                     0.000
```
