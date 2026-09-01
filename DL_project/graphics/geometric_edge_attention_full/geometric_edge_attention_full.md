# geometric_edge_attention_full

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_attention_full'
rows: 4

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_LBP_BPI_CETP    2      0.5000      0.5000      0.2255      0.7552      0.5000      0.5000
groups_lipocalin       2      0.0139      1.0000      0.2829      0.7072      0.0139      1.0000
ALL                    4      0.2569      0.7500      0.2542      0.7312      0.2569      0.7500

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5035      0.5000     0.0069  4
max valid BA                0.5035      0.5000     0.0069  4
best valid F1               0.5026      0.5026     0.0030  4
test BA                     0.5035      0.5000     0.0069  4
test F1                     0.1372      0.0270     0.2397  4
test sensitivity            0.2569      0.0139     0.4955  4
test specificity            0.7500      1.0000     0.5000  4
test precision              0.6643      0.6643     0.4748  2
test loss                   0.6890      0.6893     0.0056  4
FPR (FP/(FP+TN))            0.2500      0.0000     0.5000  4
FNR (FN/(FN+TP))            0.7431      0.9861     0.4955  4

=== abs(sensitivity-specificity) gap: mean=0.9931 median=1.0000 n=4 ===

=== By group ===
groups_LBP_BPI_CETP (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0000  2
  max valid BA                0.5000      0.5000     0.0000  2
  best valid F1               0.5053      0.5053     0.0000  2
  test BA                     0.5000      0.5000     0.0000  2
  test F1                     0.2473      0.2473     0.3498  2
  test sensitivity            0.5000      0.5000     0.7071  2
  test specificity            0.5000      0.5000     0.7071  2
  test precision              0.3286      0.3286     0.0000  1
  test loss                   0.6887      0.6887     0.0090  2
  FPR (FP/(FP+TN))            0.5000      0.5000     0.7071  2
  FNR (FN/(FN+TP))            0.5000      0.5000     0.7071  2

groups_lipocalin (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5069      0.5069     0.0098  2
  max valid BA                0.5069      0.5069     0.0098  2
  best valid F1               0.5000      0.5000     0.0000  2
  test BA                     0.5069      0.5069     0.0098  2
  test F1                     0.0270      0.0270     0.0382  2
  test sensitivity            0.0139      0.0139     0.0196  2
  test specificity            1.0000      1.0000     0.0000  2
  test precision              1.0000      1.0000     0.0000  1
  test loss                   0.6893      0.6893     0.0034  2
  FPR (FP/(FP+TN))            0.0000      0.0000     0.0000  2
  FNR (FN/(FN+TP))            0.9861      0.9861     0.0196  2
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.475    0.500     4.000              0.348         0.500   5.000               0.467          0.500
GLTP                     0.595         0.484    0.500     2.000              0.488         0.500   3.000               0.494          0.500
IP_trans                 0.727         0.726    0.500     3.000              0.719         0.500   2.667               0.664          0.500
LBP_BPI_CETP             0.721         0.811    0.500     2.000              0.812         0.500   1.667               0.792          0.500
START                    0.574         0.487    0.511     3.000              0.461         0.487   4.000               0.517          0.491
lipocalin                0.558         0.302    0.500     5.000              0.222         0.500   2.000               0.681          0.500
scp2                     0.632         0.430    0.500     2.667              0.528         0.500   2.667               0.630          0.500

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.531               0.487                  0.032                     0.176
net_AUC           0.502               0.500                  0.003                     0.004

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.472                  0.041                     0.203
net_AUC_prot           0.498               0.500                  0.003                     0.005

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.606               0.581                  0.084                     0.119
net_AUC_lipid           0.499               0.500                  0.002                     0.004

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.531  0.524      0.511     0.498
10     0.531  0.495      0.511     0.475
49     0.531  0.447      0.511     0.420
51     0.531  0.477      0.511     0.424
120    0.531  0.502      0.511     0.498

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.623         0.650      0.026          0.656              0.682           0.026
10        0.623         0.671      0.048          0.656              0.689           0.033
49        0.623         0.675      0.051          0.656              0.692           0.036
51        0.623         0.682      0.059          0.656              0.703           0.047
120       0.623         0.626      0.002          0.656              0.658           0.002

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.475  0.500      0.348     0.500     0.525         0.525      0.000          0.589              0.589           0.000
GLTP          0.484  0.500      0.488     0.500     0.519         0.519      0.000          0.547              0.547           0.000
IP_trans      0.726  0.500      0.719     0.500     0.726         0.726      0.000          0.729              0.729           0.000
LBP_BPI_CETP  0.811  0.500      0.812     0.500     0.811         0.811      0.000          0.815              0.815           0.000
START         0.487  0.511      0.461     0.487     0.513         0.530      0.017          0.559              0.574           0.015
lipocalin     0.302  0.500      0.222     0.500     0.698         0.698      0.000          0.696              0.696           0.000
scp2          0.430  0.500      0.528     0.500     0.570         0.570      0.000          0.655              0.655           0.000

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.531               0.487                  0.032                     0.176
net               0.502               0.500                  0.003                     0.004
fit_chem          0.623               0.580                  0.031                     0.120
fit_chem_net      0.626               0.580                  0.033                     0.118
increment         0.002               0.000                  0.004                     0.007

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.472                  0.041                     0.203
net_prot               0.498               0.500                  0.003                     0.005
fit_chem_prot          0.656               0.655                  0.032                     0.098
fit_chem_net_prot      0.658               0.655                  0.034                     0.096
increment_prot         0.002               0.000                  0.004                     0.006
```
