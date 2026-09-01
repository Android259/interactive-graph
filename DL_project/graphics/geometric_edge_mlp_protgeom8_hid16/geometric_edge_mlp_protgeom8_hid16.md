# geometric_edge_mlp_protgeom8_hid16

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom8_hid16'
rows: 21

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.7164      0.4372      0.7438      0.6263      0.7363      0.4785
groups_GLTP            3      0.5200      0.3467      0.7426      0.5642      0.6154      0.4872
groups_IP_trans        3      0.5507      0.6809      0.6345      0.6024      0.6944      0.7589
groups_LBP_BPI_CETP    3      0.2754      0.8511      0.6581      0.6284      0.3472      0.8369
groups_START           3      0.4769      0.6517      0.7247      0.5853      0.6094      0.6030
groups_lipocalin       3      0.8056      0.6019      0.8522      0.5632      0.8796      0.5741
groups_scp2            3      0.5686      0.6667      0.7154      0.5950      0.6863      0.7353
ALL                   21      0.5591      0.6051      0.7245      0.5950      0.6527      0.6391

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6459      0.6462     0.0782  21
max valid BA                0.6736      0.7163     0.0802  21
best valid F1               0.6565      0.6667     0.0452  21
test BA                     0.5821      0.5984     0.0916  21
test F1                     0.5049      0.5124     0.1372  21
test sensitivity            0.5591      0.5600     0.2004  21
test specificity            0.6051      0.6765     0.1907  21
test precision              0.4925      0.4762     0.0823  21
test loss                   0.8180      0.6653     0.6671  21
FPR (FP/(FP+TN))            0.3949      0.3235     0.1907  21
FNR (FN/(FN+TP))            0.4409      0.4400     0.2004  21

=== abs(sensitivity-specificity) gap: mean=0.2643 median=0.2273 n=21 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6074      0.6046     0.0137  3
  max valid BA                0.6134      0.6133     0.0088  3
  best valid F1               0.7058      0.7104     0.0100  3
  test BA                     0.5768      0.5913     0.0533  3
  test F1                     0.6338      0.6429     0.0827  3
  test sensitivity            0.7164      0.8060     0.2090  3
  test specificity            0.4372      0.3770     0.2433  3
  test precision              0.5929      0.6042     0.0536  3
  test loss                   0.6767      0.6561     0.0363  3
  FPR (FP/(FP+TN))            0.5628      0.6230     0.2433  3
  FNR (FN/(FN+TP))            0.2836      0.1940     0.2090  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5513      0.5385     0.0222  3
  max valid BA                0.5641      0.5577     0.0111  3
  best valid F1               0.6696      0.6667     0.0050  3
  test BA                     0.4333      0.4600     0.0462  3
  test F1                     0.4786      0.4746     0.0106  3
  test sensitivity            0.5200      0.5200     0.0400  3
  test specificity            0.3467      0.4000     0.1286  3
  test precision              0.4459      0.4615     0.0296  3
  test loss                   0.7049      0.7071     0.0042  3
  FPR (FP/(FP+TN))            0.6533      0.6000     0.1286  3
  FNR (FN/(FN+TP))            0.4800      0.4800     0.0400  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7267      0.7172     0.0278  3
  max valid BA                0.7405      0.7584     0.0310  3
  best valid F1               0.6602      0.6800     0.0342  3
  test BA                     0.6158      0.6018     0.0348  3
  test F1                     0.4993      0.4906     0.0460  3
  test sensitivity            0.5507      0.5652     0.0664  3
  test specificity            0.6809      0.7021     0.0369  3
  test precision              0.4578      0.4400     0.0367  3
  test loss                   0.6398      0.6612     0.0428  3
  FPR (FP/(FP+TN))            0.3191      0.2979     0.0369  3
  FNR (FN/(FN+TP))            0.4493      0.4348     0.0664  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5921      0.6011     0.0777  3
  max valid BA                0.6616      0.7163     0.1136  3
  best valid F1               0.5953      0.6275     0.0790  3
  test BA                     0.5632      0.5111     0.1168  3
  test F1                     0.3148      0.2791     0.2546  3
  test sensitivity            0.2754      0.2609     0.2395  3
  test specificity            0.8511      0.8723     0.1395  3
  test precision              0.4889      0.5000     0.1836  3
  test loss                   1.6960      0.7548     1.7529  3
  FPR (FP/(FP+TN))            0.1489      0.1277     0.1395  3
  FNR (FN/(FN+TP))            0.7246      0.7391     0.2395  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6062      0.6156     0.0454  3
  max valid BA                0.6523      0.6363     0.0614  3
  best valid F1               0.6490      0.6477     0.0274  3
  test BA                     0.5643      0.5980     0.0587  3
  test F1                     0.4793      0.5124     0.1124  3
  test sensitivity            0.4769      0.4769     0.1692  3
  test specificity            0.6517      0.6854     0.0892  3
  test precision              0.4941      0.5122     0.0702  3
  test loss                   0.7532      0.7134     0.0695  3
  FPR (FP/(FP+TN))            0.3483      0.3146     0.0892  3
  FNR (FN/(FN+TP))            0.5231      0.5231     0.1692  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7269      0.7222     0.0350  3
  max valid BA                0.7431      0.7222     0.0361  3
  best valid F1               0.6616      0.6408     0.0442  3
  test BA                     0.7037      0.7083     0.0212  3
  test F1                     0.6198      0.6263     0.0195  3
  test sensitivity            0.8056      0.8056     0.0556  3
  test specificity            0.6019      0.5556     0.0802  3
  test precision              0.5062      0.4921     0.0397  3
  test loss                   0.6210      0.6157     0.0116  3
  FPR (FP/(FP+TN))            0.3981      0.4444     0.0802  3
  FNR (FN/(FN+TP))            0.1944      0.1944     0.0556  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7108      0.7206     0.0449  3
  max valid BA                0.7402      0.7500     0.0170  3
  best valid F1               0.6540      0.6667     0.0220  3
  test BA                     0.6176      0.6176     0.0147  3
  test F1                     0.5088      0.5000     0.0152  3
  test sensitivity            0.5686      0.5882     0.0340  3
  test specificity            0.6667      0.6765     0.0449  3
  test precision              0.4616      0.4737     0.0232  3
  test loss                   0.6343      0.6210     0.0269  3
  FPR (FP/(FP+TN))            0.3333      0.3235     0.0449  3
  FNR (FN/(FN+TP))            0.4314      0.4118     0.0340  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.475    0.529     4.000              0.348         0.458   5.000               0.467          0.578
GLTP                     0.595         0.484    0.501     2.000              0.488         0.494   3.000               0.494          0.474
IP_trans                 0.727         0.726    0.578     3.000              0.719         0.604   2.667               0.664          0.584
LBP_BPI_CETP             0.721         0.811    0.757     2.000              0.812         0.752   1.667               0.792          0.719
START                    0.574         0.487    0.665     3.000              0.461         0.595   4.000               0.517          0.635
lipocalin                0.558         0.302    0.620     5.000              0.222         0.685   2.000               0.681          0.463
scp2                     0.632         0.430    0.733     2.667              0.528         0.645   2.667               0.630          0.663

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.531               0.487                  0.032                     0.176
net_AUC           0.626               0.676                  0.096                     0.098

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.472                  0.041                     0.203
net_AUC_prot           0.605               0.611                  0.101                     0.103

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.606               0.581                  0.084                     0.119
net_AUC_lipid           0.588               0.567                  0.083                     0.095

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.531  0.508      0.511     0.499
10     0.531  0.575      0.511     0.548
49     0.531  0.610      0.511     0.588
51     0.531  0.637      0.511     0.610
120    0.531  0.626      0.511     0.605

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.623         0.652      0.029          0.656              0.682           0.026
10        0.623         0.672      0.049          0.656              0.692           0.036
49        0.623         0.676      0.053          0.656              0.705           0.049
51        0.623         0.691      0.068          0.656              0.719           0.063
120       0.623         0.685      0.062          0.656              0.712           0.056

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.475  0.529      0.348     0.458     0.525         0.571      0.046          0.589              0.651           0.061
GLTP          0.484  0.501      0.488     0.494     0.519         0.543      0.024          0.547              0.563           0.016
IP_trans      0.726  0.578      0.719     0.604     0.726         0.741      0.015          0.729              0.747           0.018
LBP_BPI_CETP  0.811  0.757      0.812     0.752     0.811         0.826      0.015          0.815              0.831           0.016
START         0.487  0.665      0.461     0.595     0.513         0.664      0.151          0.559              0.673           0.113
lipocalin     0.302  0.620      0.222     0.685     0.698         0.789      0.091          0.696              0.809           0.112
scp2          0.430  0.733      0.528     0.645     0.570         0.662      0.092          0.655              0.713           0.058

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.531               0.487                  0.032                     0.176
net               0.626               0.676                  0.096                     0.098
fit_chem          0.623               0.580                  0.031                     0.120
fit_chem_net      0.685               0.699                  0.045                     0.107
increment         0.062               0.030                  0.045                     0.051

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.472                  0.041                     0.203
net_prot               0.605               0.611                  0.101                     0.103
fit_chem_prot          0.656               0.655                  0.032                     0.098
fit_chem_net_prot      0.712               0.715                  0.049                     0.093
increment_prot         0.056               0.033                  0.042                     0.043
```
