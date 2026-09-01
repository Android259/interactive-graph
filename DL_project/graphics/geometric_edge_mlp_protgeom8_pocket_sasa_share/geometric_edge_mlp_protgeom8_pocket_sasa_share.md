# geometric_edge_mlp_protgeom8_pocket_sasa_share

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom8_pocket_sasa_share'
rows: 21

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.6368      0.5355      0.6571      0.7046      0.5672      0.5968
groups_GLTP            3      0.6000      0.7467      0.7513      0.5336      0.5769      0.8333
groups_IP_trans        3      0.2464      0.8865      0.7750      0.5482      0.3611      0.8723
groups_LBP_BPI_CETP    3      0.1594      0.8936      0.6160      0.5700      0.2083      0.8652
groups_START           3      0.4667      0.7678      0.7224      0.5939      0.4323      0.7266
groups_lipocalin       3      0.2222      0.7593      0.7197      0.5586      0.2407      0.7639
groups_scp2            3      0.5490      0.6765      0.7871      0.5118      0.6275      0.7255
ALL                   21      0.4115      0.7523      0.7184      0.5744      0.4306      0.7691

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5998      0.5793     0.0960  21
max valid BA                0.6421      0.6241     0.1031  21
best valid F1               0.5642      0.5909     0.1811  21
test BA                     0.5819      0.5795     0.0960  21
test F1                     0.4165      0.4667     0.2408  21
test sensitivity            0.4115      0.4706     0.2659  21
test specificity            0.7523      0.8085     0.1993  21
test precision              0.5511      0.5385     0.2103  19
test loss                   1.1302      0.7586     0.8534  21
FPR (FP/(FP+TN))            0.2477      0.1915     0.1993  21
FNR (FN/(FN+TP))            0.5885      0.5294     0.2659  21

=== abs(sensitivity-specificity) gap: mean=0.4573 median=0.2868 n=21 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5820      0.5739     0.0305  3
  max valid BA                0.5943      0.5922     0.0270  3
  best valid F1               0.6966      0.6927     0.0123  3
  test BA                     0.5862      0.5795     0.0115  3
  test F1                     0.6134      0.6443     0.0534  3
  test sensitivity            0.6368      0.7164     0.1379  3
  test specificity            0.5355      0.4426     0.1609  3
  test precision              0.6079      0.5854     0.0391  3
  test loss                   0.7226      0.7334     0.0731  3
  FPR (FP/(FP+TN))            0.4645      0.5574     0.1609  3
  FNR (FN/(FN+TP))            0.3632      0.2836     0.1379  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7051      0.7115     0.1636  3
  max valid BA                0.7500      0.7115     0.1952  3
  best valid F1               0.6985      0.6154     0.2315  3
  test BA                     0.6733      0.7600     0.1858  3
  test F1                     0.6606      0.7000     0.1362  3
  test sensitivity            0.6000      0.5600     0.0693  3
  test specificity            0.7467      0.9200     0.3355  3
  test precision              0.7649      0.8947     0.2590  3
  test loss                   0.7739      0.7331     0.2464  3
  FPR (FP/(FP+TN))            0.2533      0.0800     0.3355  3
  FNR (FN/(FN+TP))            0.4000      0.4400     0.0693  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6167      0.6033     0.0321  3
  max valid BA                0.6445      0.6534     0.0177  3
  best valid F1               0.5377      0.5333     0.0099  3
  test BA                     0.5665      0.5435     0.0894  3
  test F1                     0.2958      0.1818     0.2165  3
  test sensitivity            0.2464      0.1304     0.2395  3
  test specificity            0.8865      0.8511     0.1005  3
  test precision              0.6238      0.5714     0.3529  3
  test loss                   0.7796      0.7504     0.1543  3
  FPR (FP/(FP+TN))            0.1135      0.1489     0.1005  3
  FNR (FN/(FN+TP))            0.7536      0.8696     0.2395  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5368      0.5310     0.0400  3
  max valid BA                0.5675      0.5412     0.0838  3
  best valid F1               0.2897      0.2069     0.2669  3
  test BA                     0.5265      0.5111     0.0367  3
  test F1                     0.1685      0.0800     0.2262  3
  test sensitivity            0.1594      0.0435     0.2395  3
  test specificity            0.8936      0.9787     0.1662  3
  test precision              0.4583      0.4583     0.0589  2
  test loss                   2.2376      2.0785     1.5469  3
  FPR (FP/(FP+TN))            0.1064      0.0213     0.1662  3
  FNR (FN/(FN+TP))            0.8406      0.9565     0.2395  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5794      0.5722     0.0833  3
  max valid BA                0.6098      0.6197     0.0730  3
  best valid F1               0.5631      0.6228     0.1211  3
  test BA                     0.6172      0.6729     0.1016  3
  test F1                     0.4275      0.6202     0.3708  3
  test sensitivity            0.4667      0.6154     0.4129  3
  test specificity            0.7678      0.7303     0.2159  3
  test precision              0.5990      0.5990     0.0367  2
  test loss                   1.5167      1.0908     1.1624  3
  FPR (FP/(FP+TN))            0.2322      0.2697     0.2159  3
  FNR (FN/(FN+TP))            0.5333      0.3846     0.4129  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5023      0.4931     0.0699  3
  max valid BA                0.6227      0.5903     0.1281  3
  best valid F1               0.5497      0.5289     0.1254  3
  test BA                     0.4907      0.4653     0.0630  3
  test F1                     0.2570      0.2535     0.1079  3
  test sensitivity            0.2222      0.2500     0.1002  3
  test specificity            0.7593      0.8194     0.1042  3
  test precision              0.3169      0.2571     0.1230  3
  test loss                   0.7895      0.7586     0.1160  3
  FPR (FP/(FP+TN))            0.2407      0.1806     0.1042  3
  FNR (FN/(FN+TP))            0.7778      0.7500     0.1002  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6765      0.6618     0.0530  3
  max valid BA                0.7059      0.7059     0.0294  3
  best valid F1               0.6140      0.6000     0.0325  3
  test BA                     0.6127      0.6176     0.0225  3
  test F1                     0.4923      0.4667     0.0529  3
  test sensitivity            0.5490      0.4706     0.1891  3
  test specificity            0.6765      0.7059     0.1638  3
  test precision              0.4721      0.4444     0.0578  3
  test loss                   1.0913      0.7104     0.7557  3
  FPR (FP/(FP+TN))            0.3235      0.2941     0.1638  3
  FNR (FN/(FN+TP))            0.4510      0.5294     0.1891  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.475    0.586     4.000              0.348         0.513   5.000               0.467          0.630
GLTP                     0.595         0.484    0.681     2.000              0.488         0.670   3.000               0.494          0.660
IP_trans                 0.727         0.726    0.626     3.000              0.719         0.684   2.667               0.664          0.536
LBP_BPI_CETP             0.721         0.811    0.723     2.000              0.812         0.753   1.667               0.792          0.641
START                    0.574         0.487    0.534     3.000              0.461         0.498   4.000               0.517          0.654
lipocalin                0.558         0.302    0.515     5.000              0.222         0.475   2.000               0.681          0.533
scp2                     0.632         0.430    0.665     2.667              0.528         0.531   2.667               0.630          0.638

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.531               0.487                  0.032                     0.176
net_AUC           0.619               0.621                  0.115                     0.077

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.472                  0.041                     0.203
net_AUC_prot           0.589               0.545                  0.136                     0.110

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.606               0.581                  0.084                     0.119
net_AUC_lipid           0.613               0.590                  0.178                     0.055

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.531  0.506      0.511     0.496
10     0.531  0.541      0.511     0.527
49     0.531  0.584      0.511     0.556
51     0.531  0.593      0.511     0.572
120    0.531  0.619      0.511     0.589

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.623         0.677      0.054          0.656              0.701           0.045
10        0.623         0.641      0.018          0.656              0.695           0.039
49        0.623         0.665      0.042          0.656              0.691           0.035
51        0.623         0.656      0.033          0.656              0.683           0.028
120       0.623         0.690      0.067          0.656              0.717           0.061

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.475  0.586      0.348     0.513     0.525         0.599      0.073          0.589              0.674           0.085
GLTP          0.484  0.681      0.488     0.670     0.519         0.680      0.161          0.547              0.716           0.169
IP_trans      0.726  0.626      0.719     0.684     0.726         0.734      0.008          0.729              0.740           0.011
LBP_BPI_CETP  0.811  0.723      0.812     0.753     0.811         0.826      0.015          0.815              0.832           0.017
START         0.487  0.534      0.461     0.498     0.513         0.636      0.123          0.559              0.622           0.063
lipocalin     0.302  0.515      0.222     0.475     0.698         0.704      0.006          0.696              0.733           0.036
scp2          0.430  0.665      0.528     0.531     0.570         0.654      0.083          0.655              0.699           0.045

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.531               0.487                  0.032                     0.176
net               0.619               0.621                  0.115                     0.077
fit_chem          0.623               0.580                  0.031                     0.120
fit_chem_net      0.690               0.665                  0.084                     0.075
increment         0.067               0.021                  0.069                     0.061

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.472                  0.041                     0.203
net_prot               0.589               0.545                  0.136                     0.110
fit_chem_prot          0.656               0.655                  0.032                     0.098
fit_chem_net_prot      0.717               0.716                  0.072                     0.065
increment_prot         0.061               0.036                  0.057                     0.054
```
