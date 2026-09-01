# geometric_edge_mlp_protgeom8_nolip_sa

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom8_nolip_sa'
rows: 21

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.6965      0.4317      0.5686      0.6614      0.7015      0.4140
groups_GLTP            3      0.1733      0.8533      0.4839      0.5461      0.1923      0.9231
groups_IP_trans        3      0.6377      0.6809      0.6758      0.6056      0.6667      0.6950
groups_LBP_BPI_CETP    3      0.5362      0.6383      0.5988      0.5189      0.5833      0.6879
groups_START           3      0.3897      0.7266      0.7588      0.5398      0.3802      0.7116
groups_lipocalin       3      0.7685      0.5000      0.6881      0.4918      0.7963      0.5139
groups_scp2            3      0.5294      0.7157      0.7090      0.6362      0.5686      0.7549
ALL                   21      0.5331      0.6495      0.6404      0.5714      0.5556      0.6715

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6135      0.5793     0.0747  21
max valid BA                0.6445      0.6445     0.0741  21
best valid F1               0.6043      0.6129     0.0684  21
test BA                     0.5913      0.5893     0.0798  21
test F1                     0.4675      0.4964     0.1796  21
test sensitivity            0.5331      0.5833     0.3033  21
test specificity            0.6495      0.7447     0.2717  21
test precision              0.5231      0.4881     0.1498  20
test loss                   0.6867      0.6916     0.0540  21
FPR (FP/(FP+TN))            0.3505      0.2553     0.2717  21
FNR (FN/(FN+TP))            0.4669      0.4167     0.3033  21

=== abs(sensitivity-specificity) gap: mean=0.4832 median=0.4556 n=21 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5577      0.5580     0.0149  3
  max valid BA                0.6054      0.6154     0.0292  3
  best valid F1               0.6640      0.6889     0.0536  3
  test BA                     0.5641      0.5745     0.0338  3
  test F1                     0.5963      0.6792     0.1778  3
  test sensitivity            0.6965      0.8060     0.3561  3
  test specificity            0.4317      0.3770     0.2989  3
  test precision              0.5742      0.5714     0.0117  3
  test loss                   0.6917      0.6883     0.0274  3
  FPR (FP/(FP+TN))            0.5683      0.6230     0.2989  3
  FNR (FN/(FN+TP))            0.3035      0.1940     0.3561  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5577      0.5769     0.0333  3
  max valid BA                0.6026      0.5769     0.0801  3
  best valid F1               0.6286      0.6575     0.0797  3
  test BA                     0.5133      0.4800     0.0945  3
  test F1                     0.2663      0.2353     0.1087  3
  test sensitivity            0.1733      0.1600     0.0611  3
  test specificity            0.8533      0.8000     0.1286  3
  test precision              0.5926      0.4444     0.3572  3
  test loss                   0.7164      0.6967     0.0387  3
  FPR (FP/(FP+TN))            0.1467      0.2000     0.1286  3
  FNR (FN/(FN+TP))            0.8267      0.8400     0.0611  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6809      0.6844     0.0268  3
  max valid BA                0.7123      0.7057     0.0214  3
  best valid F1               0.6283      0.6154     0.0246  3
  test BA                     0.6593      0.6684     0.0659  3
  test F1                     0.5469      0.5846     0.1047  3
  test sensitivity            0.6377      0.6957     0.2231  3
  test specificity            0.6809      0.7447     0.1489  3
  test precision              0.4992      0.4737     0.0635  3
  test loss                   0.6374      0.6464     0.0236  3
  FPR (FP/(FP+TN))            0.3191      0.2553     0.1489  3
  FNR (FN/(FN+TP))            0.3623      0.3043     0.2231  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6356      0.6445     0.0555  3
  max valid BA                0.6420      0.6445     0.0645  3
  best valid F1               0.5557      0.5263     0.0541  3
  test BA                     0.5873      0.5772     0.0405  3
  test F1                     0.4481      0.4737     0.0853  3
  test sensitivity            0.5362      0.3913     0.3698  3
  test specificity            0.6383      0.8723     0.4239  3
  test precision              0.5001      0.5455     0.1287  3
  test loss                   0.7297      0.7322     0.0776  3
  FPR (FP/(FP+TN))            0.3617      0.1277     0.4239  3
  FNR (FN/(FN+TP))            0.4638      0.6087     0.3698  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5459      0.5585     0.0411  3
  max valid BA                0.5707      0.6044     0.0613  3
  best valid F1               0.5562      0.5935     0.0757  3
  test BA                     0.5582      0.5217     0.0827  3
  test F1                     0.3509      0.4068     0.3266  3
  test sensitivity            0.3897      0.3692     0.4004  3
  test specificity            0.7266      0.6742     0.2513  3
  test precision              0.4972      0.4972     0.0628  2
  test loss                   0.6807      0.6931     0.0325  3
  FPR (FP/(FP+TN))            0.2734      0.3258     0.2513  3
  FNR (FN/(FN+TP))            0.6103      0.6308     0.4004  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6551      0.6875     0.1146  3
  max valid BA                0.6875      0.7431     0.1023  3
  best valid F1               0.6125      0.6600     0.0880  3
  test BA                     0.6343      0.6528     0.1191  3
  test F1                     0.5747      0.5714     0.0800  3
  test sensitivity            0.7685      0.7778     0.1807  3
  test specificity            0.5000      0.5278     0.4174  3
  test precision              0.5127      0.4516     0.2134  3
  test loss                   0.7084      0.7130     0.0773  3
  FPR (FP/(FP+TN))            0.5000      0.4722     0.4174  3
  FNR (FN/(FN+TP))            0.2315      0.2222     0.1807  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6618      0.6324     0.0778  3
  max valid BA                0.6912      0.6765     0.0530  3
  best valid F1               0.5847      0.5714     0.0761  3
  test BA                     0.6225      0.6324     0.0594  3
  test F1                     0.4896      0.5263     0.1185  3
  test sensitivity            0.5294      0.5882     0.2121  3
  test specificity            0.7157      0.6765     0.0945  3
  test precision              0.4769      0.4762     0.0227  3
  test loss                   0.6425      0.6183     0.0431  3
  FPR (FP/(FP+TN))            0.2843      0.3235     0.0945  3
  FNR (FN/(FN+TP))            0.4706      0.4118     0.2121  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.475    0.541     4.000              0.348         0.480   5.000               0.467          0.575
GLTP                     0.595         0.484    0.518     2.000              0.488         0.535   3.000               0.494          0.497
IP_trans                 0.727         0.726    0.583     3.000              0.719         0.620   2.667               0.664          0.550
LBP_BPI_CETP             0.721         0.811    0.766     2.000              0.812         0.761   1.667               0.792          0.710
START                    0.574         0.487    0.572     3.000              0.461         0.503   4.000               0.517          0.641
lipocalin                0.558         0.302    0.382     5.000              0.222         0.368   2.000               0.681          0.502
scp2                     0.632         0.430    0.706     2.667              0.528         0.607   2.667               0.630          0.543

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.531               0.487                  0.032                     0.176
net_AUC           0.581               0.586                  0.073                     0.126

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.472                  0.041                     0.203
net_AUC_prot           0.553               0.528                  0.107                     0.125

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.606               0.581                  0.084                     0.119
net_AUC_lipid           0.574               0.569                  0.066                     0.077

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.531  0.563      0.511     0.566
10     0.531  0.549      0.511     0.544
49     0.531  0.540      0.511     0.515
51     0.531  0.540      0.511     0.522
120    0.531  0.581      0.511     0.553

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.623         0.654      0.031          0.656              0.678           0.022
10        0.623         0.659      0.036          0.656              0.689           0.034
49        0.623         0.661      0.037          0.656              0.691           0.035
51        0.623         0.657      0.034          0.656              0.688           0.033
120       0.623         0.669      0.046          0.656              0.693           0.037

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.475  0.541      0.348     0.480     0.525         0.562      0.037          0.589              0.622           0.033
GLTP          0.484  0.518      0.488     0.535     0.519         0.538      0.019          0.547              0.574           0.027
IP_trans      0.726  0.583      0.719     0.620     0.726         0.746      0.020          0.729              0.748           0.019
LBP_BPI_CETP  0.811  0.766      0.812     0.761     0.811         0.815      0.004          0.815              0.822           0.007
START         0.487  0.572      0.461     0.503     0.513         0.598      0.085          0.559              0.619           0.059
lipocalin     0.302  0.382      0.222     0.368     0.698         0.742      0.044          0.696              0.748           0.052
scp2          0.430  0.706      0.528     0.607     0.570         0.680      0.110          0.655              0.714           0.060

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.531               0.487                  0.032                     0.176
net               0.581               0.586                  0.073                     0.126
fit_chem          0.623               0.580                  0.031                     0.120
fit_chem_net      0.669               0.651                  0.042                     0.105
increment         0.046               0.026                  0.035                     0.038

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.472                  0.041                     0.203
net_prot               0.553               0.528                  0.107                     0.125
fit_chem_prot          0.656               0.655                  0.032                     0.098
fit_chem_net_prot      0.693               0.687                  0.049                     0.089
increment_prot         0.037               0.032                  0.033                     0.021
```
