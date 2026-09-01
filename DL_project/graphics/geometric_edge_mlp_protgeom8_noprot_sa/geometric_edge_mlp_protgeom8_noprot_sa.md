# geometric_edge_mlp_protgeom8_noprot_sa

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom8_noprot_sa'
rows: 21

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.6020      0.5355      0.6943      0.7272      0.5771      0.5269
groups_GLTP            3      0.3200      0.6000      0.6632      0.5347      0.4615      0.6282
groups_IP_trans        3      0.1449      0.9220      0.6281      0.6373      0.2778      0.9149
groups_LBP_BPI_CETP    3      0.0870      0.9574      0.6985      0.6134      0.1944      0.9645
groups_START           3      0.6103      0.5843      0.8760      0.5273      0.6406      0.5730
groups_lipocalin       3      0.0463      0.9583      0.4608      0.5923      0.0741      0.9630
groups_scp2            3      0.4314      0.7353      0.6975      0.6283      0.5490      0.8235
ALL                   21      0.3203      0.7561      0.6740      0.6086      0.3964      0.7706

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5835      0.5769     0.0694  21
max valid BA                0.6209      0.5875     0.0767  21
best valid F1               0.5668      0.6154     0.1508  21
test BA                     0.5382      0.5543     0.0569  21
test F1                     0.3285      0.3125     0.2199  21
test sensitivity            0.3203      0.2174     0.2730  21
test specificity            0.7561      0.8235     0.2333  21
test precision              0.4725      0.5000     0.1648  19
test loss                   0.7746      0.6929     0.2477  21
FPR (FP/(FP+TN))            0.2439      0.1765     0.2333  21
FNR (FN/(FN+TP))            0.6797      0.7826     0.2730  21

=== abs(sensitivity-specificity) gap: mean=0.5659 median=0.6762 n=21 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5520      0.5330     0.0729  3
  max valid BA                0.6019      0.5816     0.0658  3
  best valid F1               0.6821      0.6788     0.0099  3
  test BA                     0.5688      0.5750     0.0125  3
  test F1                     0.5638      0.6143     0.1536  3
  test sensitivity            0.6020      0.6418     0.3153  3
  test specificity            0.5355      0.5082     0.3369  3
  test precision              0.6215      0.5890     0.0869  3
  test loss                   0.7673      0.7754     0.0863  3
  FPR (FP/(FP+TN))            0.4645      0.4918     0.3369  3
  FNR (FN/(FN+TP))            0.3980      0.3582     0.3153  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5449      0.5385     0.0294  3
  max valid BA                0.5705      0.5769     0.0111  3
  best valid F1               0.6754      0.6753     0.0002  3
  test BA                     0.4600      0.4600     0.0200  3
  test F1                     0.3383      0.3158     0.1688  3
  test sensitivity            0.3200      0.2400     0.2498  3
  test specificity            0.6000      0.7200     0.2800  3
  test precision              0.4304      0.4545     0.0481  3
  test loss                   0.7160      0.6939     0.0392  3
  FPR (FP/(FP+TN))            0.4000      0.2800     0.2800  3
  FNR (FN/(FN+TP))            0.6800      0.7600     0.2498  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5963      0.6028     0.0116  3
  max valid BA                0.7026      0.6933     0.0624  3
  best valid F1               0.5999      0.6154     0.1025  3
  test BA                     0.5335      0.5546     0.0374  3
  test F1                     0.2195      0.2222     0.0849  3
  test sensitivity            0.1449      0.1304     0.0664  3
  test specificity            0.9220      0.8936     0.0491  3
  test precision              0.5119      0.5000     0.2324  3
  test loss                   0.6556      0.6391     0.0414  3
  FPR (FP/(FP+TN))            0.0780      0.1064     0.0491  3
  FNR (FN/(FN+TP))            0.8551      0.8696     0.0664  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5795      0.5310     0.0839  3
  max valid BA                0.5894      0.5417     0.0920  3
  best valid F1               0.3443      0.2791     0.2301  3
  test BA                     0.5222      0.5111     0.0396  3
  test F1                     0.1308      0.0800     0.1623  3
  test sensitivity            0.0870      0.0435     0.1150  3
  test specificity            0.9574      0.9787     0.0369  3
  test precision              0.3519      0.5000     0.3060  3
  test loss                   1.1802      1.3727     0.5100  3
  FPR (FP/(FP+TN))            0.0426      0.0213     0.0369  3
  FNR (FN/(FN+TP))            0.9130      0.9565     0.1150  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6068      0.6044     0.0535  3
  max valid BA                0.6248      0.6153     0.0428  3
  best valid F1               0.6163      0.6135     0.0408  3
  test BA                     0.5973      0.5986     0.0320  3
  test F1                     0.5592      0.5490     0.0341  3
  test sensitivity            0.6103      0.6462     0.0759  3
  test specificity            0.5843      0.5955     0.0960  3
  test precision              0.5204      0.5397     0.0374  3
  test loss                   0.6833      0.6858     0.0142  3
  FPR (FP/(FP+TN))            0.4157      0.4045     0.0960  3
  FNR (FN/(FN+TP))            0.3897      0.3538     0.0759  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5185      0.5000     0.0382  3
  max valid BA                0.5417      0.5417     0.0208  3
  best valid F1               0.4297      0.4823     0.1005  3
  test BA                     0.5023      0.5000     0.0040  3
  test F1                     0.0667      0.0000     0.1155  3
  test sensitivity            0.0463      0.0000     0.0802  3
  test specificity            0.9583      1.0000     0.0722  3
  test precision              0.3571      0.3571     0.0000  1
  test loss                   0.7568      0.6736     0.1696  3
  FPR (FP/(FP+TN))            0.0417      0.0000     0.0722  3
  FNR (FN/(FN+TP))            0.9537      1.0000     0.0802  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6863      0.6765     0.0594  3
  max valid BA                0.7157      0.7059     0.0306  3
  best valid F1               0.6201      0.6222     0.0477  3
  test BA                     0.5833      0.5882     0.0810  3
  test F1                     0.4213      0.4878     0.1675  3
  test sensitivity            0.4314      0.5294     0.2227  3
  test specificity            0.7353      0.7941     0.1282  3
  test precision              0.4375      0.4167     0.1160  3
  test loss                   0.6631      0.6452     0.0932  3
  FPR (FP/(FP+TN))            0.2647      0.2059     0.1282  3
  FNR (FN/(FN+TP))            0.5686      0.4706     0.2227  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.475    0.561     4.000              0.348         0.479   5.000               0.467          0.636
GLTP                     0.595         0.484    0.469     2.000              0.488         0.417   3.000               0.494          0.480
IP_trans                 0.727         0.726    0.604     3.000              0.719         0.626   2.667               0.664          0.573
LBP_BPI_CETP             0.721         0.811    0.659     2.000              0.812         0.659   1.667               0.792          0.576
START                    0.574         0.487    0.637     3.000              0.461         0.559   4.000               0.517          0.633
lipocalin                0.558         0.302    0.296     5.000              0.222         0.223   2.000               0.681          0.634
scp2                     0.632         0.430    0.691     2.667              0.528         0.606   2.667               0.630          0.586

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.531               0.487                  0.032                     0.176
net_AUC           0.560               0.585                  0.069                     0.137

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.472                  0.041                     0.203
net_AUC_prot           0.510               0.529                  0.082                     0.152

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.606               0.581                  0.084                     0.119
net_AUC_lipid           0.588               0.604                  0.090                     0.055

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.531  0.517      0.511     0.513
10     0.531  0.552      0.511     0.529
49     0.531  0.554      0.511     0.517
51     0.531  0.553      0.511     0.512
120    0.531  0.560      0.511     0.510

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.623         0.658      0.035          0.656              0.684           0.028
10        0.623         0.667      0.043          0.656              0.692           0.036
49        0.623         0.669      0.045          0.656              0.693           0.037
51        0.623         0.675      0.052          0.656              0.700           0.044
120       0.623         0.676      0.052          0.656              0.705           0.049

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.475  0.561      0.348     0.479     0.525         0.588      0.063          0.589              0.644           0.055
GLTP          0.484  0.469      0.488     0.417     0.519         0.582      0.063          0.547              0.642           0.094
IP_trans      0.726  0.604      0.719     0.626     0.726         0.741      0.015          0.729              0.751           0.022
LBP_BPI_CETP  0.811  0.659      0.812     0.659     0.811         0.822      0.012          0.815              0.831           0.016
START         0.487  0.637      0.461     0.559     0.513         0.644      0.131          0.559              0.647           0.088
lipocalin     0.302  0.296      0.222     0.223     0.698         0.717      0.019          0.696              0.716           0.020
scp2          0.430  0.691      0.528     0.606     0.570         0.634      0.064          0.655              0.700           0.046

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.531               0.487                  0.032                     0.176
net               0.560               0.585                  0.069                     0.137
fit_chem          0.623               0.580                  0.031                     0.120
fit_chem_net      0.676               0.669                  0.052                     0.088
increment         0.052               0.028                  0.043                     0.042

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.472                  0.041                     0.203
net_prot               0.510               0.529                  0.082                     0.152
fit_chem_prot          0.656               0.655                  0.032                     0.098
fit_chem_net_prot      0.705               0.708                  0.060                     0.070
increment_prot         0.049               0.035                  0.037                     0.032
```
