# geometric_edge_mlp_protgeom8_hid32

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom8_hid32'
rows: 21

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.5075      0.5956      0.5781      0.6527      0.5075      0.6774
groups_GLTP            3      0.5067      0.4533      0.8231      0.6211      0.6154      0.5128
groups_IP_trans        3      0.4928      0.8156      0.7677      0.6263      0.5972      0.8440
groups_LBP_BPI_CETP    3      0.4493      0.5816      0.4931      0.5631      0.5278      0.5745
groups_START           3      0.6821      0.5843      0.8544      0.6792      0.7031      0.6067
groups_lipocalin       3      0.7500      0.6806      0.8532      0.5683      0.8056      0.6157
groups_scp2            3      0.4510      0.7745      0.7211      0.6645      0.5098      0.8333
ALL                   21      0.5485      0.6408      0.7273      0.6250      0.6095      0.6664

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6370      0.6324     0.0768  21
max valid BA                0.6791      0.6912     0.0836  21
best valid F1               0.6549      0.6757     0.0647  21
test BA                     0.5946      0.5882     0.0925  21
test F1                     0.4878      0.5417     0.1828  21
test sensitivity            0.5485      0.6000     0.2756  21
test specificity            0.6408      0.7234     0.2745  21
test precision              0.5297      0.5263     0.1873  21
test loss                   0.7554      0.6851     0.2759  21
FPR (FP/(FP+TN))            0.3592      0.2766     0.2745  21
FNR (FN/(FN+TP))            0.4515      0.4000     0.2756  21

=== abs(sensitivity-specificity) gap: mean=0.3990 median=0.3068 n=21 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5924      0.5864     0.0329  3
  max valid BA                0.6062      0.6058     0.0434  3
  best valid F1               0.6959      0.7033     0.0298  3
  test BA                     0.5515      0.5393     0.0519  3
  test F1                     0.5103      0.6184     0.1946  3
  test sensitivity            0.5075      0.6269     0.2740  3
  test specificity            0.5956      0.5902     0.2214  3
  test precision              0.5738      0.5529     0.0463  3
  test loss                   0.6927      0.6881     0.0216  3
  FPR (FP/(FP+TN))            0.4044      0.4098     0.2214  3
  FNR (FN/(FN+TP))            0.4925      0.3731     0.2740  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5577      0.5385     0.0333  3
  max valid BA                0.5962      0.6154     0.0509  3
  best valid F1               0.6795      0.6757     0.0069  3
  test BA                     0.4800      0.4600     0.0529  3
  test F1                     0.4226      0.5000     0.2451  3
  test sensitivity            0.5067      0.5600     0.4027  3
  test specificity            0.4533      0.3200     0.4937  3
  test precision              0.6433      0.4783     0.3092  3
  test loss                   0.8933      0.7156     0.3099  3
  FPR (FP/(FP+TN))            0.5467      0.6800     0.4937  3
  FNR (FN/(FN+TP))            0.4933      0.4400     0.4027  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7206      0.7261     0.0722  3
  max valid BA                0.7244      0.7376     0.0729  3
  best valid F1               0.6379      0.6531     0.0907  3
  test BA                     0.6542      0.6549     0.0775  3
  test F1                     0.4896      0.5417     0.1835  3
  test sensitivity            0.4928      0.5652     0.2895  3
  test specificity            0.8156      0.7447     0.1417  3
  test precision              0.6289      0.5667     0.1500  3
  test loss                   0.7173      0.6851     0.1294  3
  FPR (FP/(FP+TN))            0.1844      0.2553     0.1417  3
  FNR (FN/(FN+TP))            0.5072      0.4348     0.2895  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5511      0.5199     0.0622  3
  max valid BA                0.6299      0.6334     0.1175  3
  best valid F1               0.5650      0.5176     0.0881  3
  test BA                     0.5154      0.5106     0.0287  3
  test F1                     0.2907      0.3721     0.2597  3
  test sensitivity            0.4493      0.3478     0.5077  3
  test specificity            0.5816      0.7447     0.4991  3
  test precision              0.2444      0.3333     0.2143  3
  test loss                   1.0319      0.6710     0.6495  3
  FPR (FP/(FP+TN))            0.4184      0.2553     0.4991  3
  FNR (FN/(FN+TP))            0.5507      0.6522     0.5077  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6549      0.6483     0.0331  3
  max valid BA                0.6971      0.7030     0.0461  3
  best valid F1               0.6669      0.6759     0.0543  3
  test BA                     0.6332      0.6652     0.0805  3
  test F1                     0.6042      0.6094     0.0817  3
  test sensitivity            0.6821      0.6000     0.1421  3
  test specificity            0.5843      0.5393     0.1296  3
  test precision              0.5503      0.5729     0.0825  3
  test loss                   0.6667      0.6934     0.0716  3
  FPR (FP/(FP+TN))            0.4157      0.4607     0.1296  3
  FNR (FN/(FN+TP))            0.3179      0.4000     0.1421  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7106      0.7014     0.0160  3
  max valid BA                0.7500      0.7639     0.0303  3
  best valid F1               0.6666      0.6804     0.0339  3
  test BA                     0.7153      0.7292     0.0636  3
  test F1                     0.6329      0.6452     0.0685  3
  test sensitivity            0.7500      0.7222     0.0735  3
  test specificity            0.6806      0.6250     0.1470  3
  test precision              0.5590      0.5263     0.1225  3
  test loss                   0.5885      0.6095     0.0522  3
  FPR (FP/(FP+TN))            0.3194      0.3750     0.1470  3
  FNR (FN/(FN+TP))            0.2500      0.2778     0.0735  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6716      0.6618     0.0449  3
  max valid BA                0.7500      0.7794     0.0509  3
  best valid F1               0.6723      0.7027     0.0629  3
  test BA                     0.6127      0.6029     0.0306  3
  test F1                     0.4641      0.4286     0.0747  3
  test sensitivity            0.4510      0.3529     0.1698  3
  test specificity            0.7745      0.8235     0.1114  3
  test precision              0.5079      0.5000     0.0343  3
  test loss                   0.6970      0.6466     0.0896  3
  FPR (FP/(FP+TN))            0.2255      0.1765     0.1114  3
  FNR (FN/(FN+TP))            0.5490      0.6471     0.1698  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.475    0.547     4.000              0.348         0.482   5.000               0.467          0.564
GLTP                     0.595         0.484    0.455     2.000              0.488         0.441   3.000               0.494          0.465
IP_trans                 0.727         0.726    0.610     3.000              0.719         0.658   2.667               0.664          0.708
LBP_BPI_CETP             0.721         0.811    0.746     2.000              0.812         0.740   1.667               0.792          0.629
START                    0.574         0.487    0.605     3.000              0.461         0.552   4.000               0.517          0.671
lipocalin                0.558         0.302    0.578     5.000              0.222         0.568   2.000               0.681          0.543
scp2                     0.632         0.430    0.738     2.667              0.528         0.630   2.667               0.630          0.732

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.531               0.487                  0.032                     0.176
net_AUC           0.611               0.629                  0.074                     0.103

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.472                  0.041                     0.203
net_AUC_prot           0.582               0.605                  0.068                     0.103

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.606               0.581                  0.084                     0.119
net_AUC_lipid           0.616               0.597                  0.106                     0.096

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.531  0.495      0.511     0.486
10     0.531  0.579      0.511     0.565
49     0.531  0.624      0.511     0.603
51     0.531  0.608      0.511     0.582
120    0.531  0.611      0.511     0.582

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.623         0.655      0.032          0.656              0.680           0.024
10        0.623         0.676      0.053          0.656              0.705           0.049
49        0.623         0.688      0.065          0.656              0.708           0.052
51        0.623         0.691      0.068          0.656              0.714           0.059
120       0.623         0.668      0.044          0.656              0.694           0.038

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.475  0.547      0.348     0.482     0.525         0.557      0.032          0.589              0.622           0.032
GLTP          0.484  0.455      0.488     0.441     0.519         0.515     -0.004          0.547              0.543          -0.004
IP_trans      0.726  0.610      0.719     0.658     0.726         0.742      0.016          0.729              0.763           0.034
LBP_BPI_CETP  0.811  0.746      0.812     0.740     0.811         0.827      0.016          0.815              0.830           0.014
START         0.487  0.605      0.461     0.552     0.513         0.628      0.115          0.559              0.639           0.080
lipocalin     0.302  0.578      0.222     0.568     0.698         0.727      0.029          0.696              0.741           0.044
scp2          0.430  0.738      0.528     0.630     0.570         0.678      0.107          0.655              0.718           0.063

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.531               0.487                  0.032                     0.176
net               0.611               0.629                  0.074                     0.103
fit_chem          0.623               0.580                  0.031                     0.120
fit_chem_net      0.668               0.680                  0.060                     0.109
increment         0.044               0.028                  0.050                     0.047

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.472                  0.041                     0.203
net_prot               0.582               0.605                  0.068                     0.103
fit_chem_prot          0.656               0.655                  0.032                     0.098
fit_chem_net_prot      0.694               0.699                  0.052                     0.097
increment_prot         0.038               0.020                  0.047                     0.028
```
