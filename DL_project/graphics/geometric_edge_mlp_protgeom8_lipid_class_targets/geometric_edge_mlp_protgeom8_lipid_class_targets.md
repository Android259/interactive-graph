# geometric_edge_mlp_protgeom8_lipid_class_targets

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom8_lipid_class_targets'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.6965      0.3224      0.7721      0.5062      0.7164      0.3333
groups_GLTP            3      0.8667      0.2400      0.9308      0.4866      0.9103      0.2949
groups_IP_trans        3      0.3913      0.6950      0.8561      0.6347      0.5694      0.6950
groups_LBP_BPI_CETP    2      0.4783      0.6383      0.8346      0.4976      0.4792      0.7021
groups_START           3      0.7128      0.5169      0.9098      0.6087      0.6927      0.5094
groups_lipocalin       3      0.7037      0.5556      0.7286      0.5606      0.7685      0.4259
groups_scp2            3      0.6471      0.6176      0.9019      0.6303      0.7255      0.7549
ALL                   20      0.6505      0.5060      0.8483      0.5638      0.7053      0.5222

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6138      0.6285     0.0840  20
max valid BA                0.6581      0.6636     0.0725  20
best valid F1               0.6361      0.6408     0.0817  20
test BA                     0.5782      0.5761     0.0636  20
test F1                     0.5247      0.5560     0.1448  20
test sensitivity            0.6505      0.7002     0.2637  20
test specificity            0.5060      0.5294     0.2653  20
test precision              0.4747      0.4879     0.0794  20
test loss                   0.8180      0.7424     0.1734  20
FPR (FP/(FP+TN))            0.4940      0.4706     0.2653  20
FNR (FN/(FN+TP))            0.3495      0.2998     0.2637  20

=== abs(sensitivity-specificity) gap: mean=0.4346 median=0.3676 n=20 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5249      0.5208     0.0108  3
  max valid BA                0.5680      0.5768     0.0164  3
  best valid F1               0.6903      0.6989     0.0173  3
  test BA                     0.5095      0.5092     0.0171  3
  test F1                     0.5730      0.6424     0.1543  3
  test sensitivity            0.6965      0.7910     0.3457  3
  test specificity            0.3224      0.2623     0.3563  3
  test precision              0.5330      0.5385     0.0116  3
  test loss                   0.8345      0.7339     0.1879  3
  FPR (FP/(FP+TN))            0.6776      0.7377     0.3563  3
  FNR (FN/(FN+TP))            0.3035      0.2090     0.3457  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6026      0.6346     0.0909  3
  max valid BA                0.7115      0.6923     0.0333  3
  best valid F1               0.7480      0.7429     0.0366  3
  test BA                     0.5533      0.5600     0.0503  3
  test F1                     0.6559      0.6667     0.0364  3
  test sensitivity            0.8667      0.9600     0.1973  3
  test specificity            0.2400      0.1600     0.2884  3
  test precision              0.5420      0.5333     0.0469  3
  test loss                   1.0344      1.0461     0.1840  3
  FPR (FP/(FP+TN))            0.7600      0.8400     0.2884  3
  FNR (FN/(FN+TP))            0.1333      0.0400     0.1973  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6322      0.6343     0.0077  3
  max valid BA                0.6823      0.6658     0.0378  3
  best valid F1               0.5869      0.5882     0.0579  3
  test BA                     0.5432      0.5125     0.0634  3
  test F1                     0.3086      0.2353     0.2169  3
  test sensitivity            0.3913      0.1739     0.4539  3
  test specificity            0.6950      0.8511     0.3271  3
  test precision              0.3644      0.3636     0.0315  3
  test loss                   0.7061      0.7323     0.0723  3
  FPR (FP/(FP+TN))            0.3050      0.1489     0.3271  3
  FNR (FN/(FN+TP))            0.6087      0.8261     0.4539  3

groups_LBP_BPI_CETP (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5906      0.5906     0.1175  2
  max valid BA                0.6230      0.6230     0.1019  2
  best valid F1               0.5545      0.5545     0.0697  2
  test BA                     0.5583      0.5583     0.0288  2
  test F1                     0.4296      0.4296     0.0156  2
  test sensitivity            0.4783      0.4783     0.1230  2
  test specificity            0.6383      0.6383     0.1805  2
  test precision              0.4056      0.4056     0.0629  2
  test loss                   0.7267      0.7267     0.0808  2
  FPR (FP/(FP+TN))            0.3617      0.3617     0.1805  2
  FNR (FN/(FN+TP))            0.5217      0.5217     0.1230  2

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6010      0.6232     0.0475  3
  max valid BA                0.6372      0.6422     0.0272  3
  best valid F1               0.6296      0.6400     0.0193  3
  test BA                     0.6148      0.5942     0.0546  3
  test F1                     0.6002      0.5833     0.0514  3
  test sensitivity            0.7128      0.7538     0.0847  3
  test specificity            0.5169      0.5730     0.1072  3
  test precision              0.5211      0.5128     0.0500  3
  test loss                   0.7680      0.7488     0.0853  3
  FPR (FP/(FP+TN))            0.4831      0.4270     0.1072  3
  FNR (FN/(FN+TP))            0.2872      0.2462     0.0847  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5972      0.5764     0.0617  3
  max valid BA                0.6227      0.6042     0.0446  3
  best valid F1               0.5447      0.5484     0.0287  3
  test BA                     0.6296      0.6528     0.0857  3
  test F1                     0.5413      0.5294     0.0762  3
  test sensitivity            0.7037      0.6944     0.2085  3
  test specificity            0.5556      0.4861     0.2235  3
  test precision              0.4637      0.4714     0.1029  3
  test loss                   0.7059      0.7088     0.0315  3
  FPR (FP/(FP+TN))            0.4444      0.5139     0.2235  3
  FNR (FN/(FN+TP))            0.2963      0.3056     0.2085  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7402      0.7500     0.0886  3
  max valid BA                0.7500      0.7500     0.0735  3
  best valid F1               0.6714      0.6667     0.0830  3
  test BA                     0.6324      0.6324     0.0147  3
  test F1                     0.5328      0.5333     0.0326  3
  test sensitivity            0.6471      0.7059     0.1556  3
  test specificity            0.6176      0.5294     0.1528  3
  test precision              0.4701      0.4483     0.0557  3
  test loss                   0.9197      0.8663     0.2528  3
  FPR (FP/(FP+TN))            0.3824      0.4706     0.1528  3
  FNR (FN/(FN+TP))            0.3529      0.2941     0.1556  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.475    0.480     4.000              0.348         0.461   5.000               0.467          0.408
GLTP                     0.595         0.484    0.463     2.000              0.488         0.481   3.000               0.494          0.394
IP_trans                 0.727         0.726    0.589     3.000              0.719         0.641   2.667               0.664          0.621
LBP_BPI_CETP             0.721         0.811    0.583     2.000              0.812         0.574   1.667               0.792          0.534
START                    0.574         0.487    0.599     3.000              0.461         0.498   4.000               0.517          0.694
lipocalin                0.558         0.302    0.482     5.000              0.222         0.492   2.000               0.681          0.503
scp2                     0.632         0.430    0.738     2.667              0.528         0.607   2.667               0.630          0.622

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.531               0.487                  0.032                     0.176
net_AUC           0.562               0.586                  0.091                     0.097

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.472                  0.041                     0.203
net_AUC_prot           0.536               0.524                  0.086                     0.070

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.606               0.581                  0.084                     0.119
net_AUC_lipid           0.539               0.580                  0.090                     0.113

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.531  0.466      0.511     0.477
10     0.531  0.552      0.511     0.527
49     0.531  0.544      0.511     0.506
51     0.531  0.547      0.511     0.504
120    0.531  0.562      0.511     0.536

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.623         0.668      0.045          0.656              0.693           0.037
10        0.623         0.651      0.028          0.656              0.680           0.024
49        0.623         0.673      0.049          0.656              0.700           0.045
51        0.623         0.665      0.042          0.656              0.701           0.045
120       0.623         0.674      0.051          0.656              0.701           0.045

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.475  0.480      0.348     0.461     0.525         0.541      0.016          0.589              0.640           0.051
GLTP          0.484  0.463      0.488     0.481     0.519         0.547      0.028          0.547              0.588           0.041
IP_trans      0.726  0.589      0.719     0.641     0.726         0.742      0.015          0.729              0.751           0.022
LBP_BPI_CETP  0.811  0.583      0.812     0.574     0.811         0.820      0.009          0.815              0.827           0.012
START         0.487  0.599      0.461     0.498     0.513         0.635      0.122          0.559              0.639           0.080
lipocalin     0.302  0.482      0.222     0.492     0.698         0.704      0.006          0.696              0.710           0.014
scp2          0.430  0.738      0.528     0.607     0.570         0.730      0.160          0.655              0.749           0.094

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.531               0.487                  0.032                     0.176
net               0.562               0.586                  0.091                     0.097
fit_chem          0.623               0.580                  0.031                     0.120
fit_chem_net      0.674               0.675                  0.052                     0.104
increment         0.051               0.024                  0.037                     0.063

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.472                  0.041                     0.203
net_prot               0.536               0.524                  0.086                     0.070
fit_chem_prot          0.656               0.655                  0.032                     0.098
fit_chem_net_prot      0.701               0.680                  0.046                     0.083
increment_prot         0.045               0.043                  0.028                     0.032
```
