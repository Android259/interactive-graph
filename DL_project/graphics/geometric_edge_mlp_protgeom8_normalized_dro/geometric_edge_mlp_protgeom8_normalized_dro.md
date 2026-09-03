# geometric_edge_mlp_protgeom8_normalized_dro

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom8_normalized_dro'
rows: 19

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.6517      0.3661      0.4990      0.5562      0.6816      0.4409
groups_GLTP            3      0.5067      0.5467      0.6924      0.6381      0.5256      0.7308
groups_IP_trans        2      0.8043      0.5000      0.6019      0.6012      0.8958      0.5213
groups_LBP_BPI_CETP    3      0.5072      0.7730      0.5378      0.6211      0.5417      0.7801
groups_START           2      0.8846      0.2360      0.7201      0.6510      0.9297      0.2753
groups_lipocalin       3      0.5093      0.7639      0.5759      0.5581      0.6389      0.6898
groups_scp2            3      0.6078      0.6569      0.6502      0.5957      0.6667      0.7059
ALL                   19      0.6172      0.5680      0.6058      0.6006      0.6744      0.6124

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6434      0.6346     0.0725  19
max valid BA                0.6784      0.6731     0.0739  19
best valid F1               0.6534      0.6667     0.0665  19
test BA                     0.5926      0.6200     0.0829  19
test F1                     0.5285      0.5405     0.1272  19
test sensitivity            0.6172      0.6111     0.2376  19
test specificity            0.5680      0.6170     0.2492  19
test precision              0.5076      0.4769     0.1305  19
test loss                   0.6901      0.6907     0.0642  19
FPR (FP/(FP+TN))            0.4320      0.3830     0.2492  19
FNR (FN/(FN+TP))            0.3828      0.3889     0.2376  19

=== abs(sensitivity-specificity) gap: mean=0.3794 median=0.2800 n=19 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5612      0.5484     0.0241  3
  max valid BA                0.5819      0.5717     0.0380  3
  best valid F1               0.6916      0.7053     0.0420  3
  test BA                     0.5089      0.5410     0.1234  3
  test F1                     0.5134      0.7053     0.3341  3
  test sensitivity            0.6517      0.8657     0.4915  3
  test specificity            0.3661      0.3607     0.2869  3
  test precision              0.4550      0.5447     0.2033  3
  test loss                   0.6929      0.6850     0.0220  3
  FPR (FP/(FP+TN))            0.6339      0.6393     0.2869  3
  FNR (FN/(FN+TP))            0.3483      0.1343     0.4915  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6282      0.6346     0.0484  3
  max valid BA                0.6795      0.6731     0.0294  3
  best valid F1               0.7093      0.7246     0.0288  3
  test BA                     0.5267      0.5000     0.0833  3
  test F1                     0.5040      0.5263     0.0713  3
  test sensitivity            0.5067      0.6000     0.1973  3
  test specificity            0.5467      0.3600     0.3585  3
  test precision              0.6146      0.5000     0.2261  3
  test loss                   0.7140      0.7342     0.0358  3
  FPR (FP/(FP+TN))            0.4533      0.6400     0.3585  3
  FNR (FN/(FN+TP))            0.4933      0.4000     0.1973  3

groups_IP_trans (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7086      0.7086     0.0066  2
  max valid BA                0.7733      0.7733     0.0367  2
  best valid F1               0.6954      0.6954     0.0406  2
  test BA                     0.6522      0.6522     0.0242  2
  test F1                     0.5670      0.5670     0.0348  2
  test sensitivity            0.8043      0.8043     0.1537  2
  test specificity            0.5000      0.5000     0.1053  2
  test precision              0.4410      0.4410     0.0049  2
  test loss                   0.6571      0.6571     0.1297  2
  FPR (FP/(FP+TN))            0.5000      0.5000     0.1053  2
  FNR (FN/(FN+TP))            0.1957      0.1957     0.1537  2

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6609      0.6751     0.0755  3
  max valid BA                0.7030      0.6751     0.0574  3
  best valid F1               0.6127      0.5789     0.0707  3
  test BA                     0.6401      0.6346     0.0125  3
  test F1                     0.5087      0.5333     0.0447  3
  test sensitivity            0.5072      0.5217     0.1527  3
  test specificity            0.7730      0.7872     0.1494  3
  test precision              0.5556      0.5455     0.1064  3
  test loss                   0.6705      0.6520     0.0803  3
  FPR (FP/(FP+TN))            0.2270      0.2128     0.1494  3
  FNR (FN/(FN+TP))            0.4928      0.4783     0.1527  3

groups_START (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6025      0.6025     0.0143  2
  max valid BA                0.6122      0.6122     0.0031  2
  best valid F1               0.6402      0.6402     0.0033  2
  test BA                     0.5603      0.5603     0.0490  2
  test F1                     0.6029      0.6029     0.0467  2
  test sensitivity            0.8846      0.8846     0.0979  2
  test specificity            0.2360      0.2360     0.0000  2
  test precision              0.4575      0.4575     0.0275  2
  test loss                   0.7384      0.7384     0.0139  2
  FPR (FP/(FP+TN))            0.7640      0.7640     0.0000  2
  FNR (FN/(FN+TP))            0.1154      0.1154     0.0979  2

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6644      0.6875     0.0723  3
  max valid BA                0.6782      0.6875     0.0493  3
  best valid F1               0.5927      0.6000     0.0478  3
  test BA                     0.6366      0.6389     0.0868  3
  test F1                     0.5124      0.5263     0.1237  3
  test sensitivity            0.5093      0.5556     0.1313  3
  test specificity            0.7639      0.7361     0.0605  3
  test precision              0.5178      0.5000     0.1214  3
  test loss                   0.6620      0.6907     0.1062  3
  FPR (FP/(FP+TN))            0.2361      0.2639     0.0605  3
  FNR (FN/(FN+TP))            0.4907      0.4444     0.1313  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6863      0.7206     0.1142  3
  max valid BA                0.7304      0.7500     0.0899  3
  best valid F1               0.6417      0.6667     0.1097  3
  test BA                     0.6324      0.6324     0.0147  3
  test F1                     0.5287      0.5405     0.0249  3
  test sensitivity            0.6078      0.5882     0.0899  3
  test specificity            0.6569      0.7059     0.0849  3
  test precision              0.4727      0.4737     0.0278  3
  test loss                   0.7006      0.6811     0.0540  3
  FPR (FP/(FP+TN))            0.3431      0.2941     0.0849  3
  FNR (FN/(FN+TP))            0.3922      0.4118     0.0899  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.475    0.465     4.000              0.348         0.484   5.000               0.467          0.491
GLTP                     0.595         0.484    0.524     2.000              0.488         0.559   3.000               0.494          0.575
IP_trans                 0.727         0.726    0.588     3.000              0.719         0.616   2.667               0.664          0.633
LBP_BPI_CETP             0.721         0.811    0.591     2.000              0.812         0.594   1.667               0.792          0.588
START                    0.574         0.487    0.493     3.000              0.461         0.467   4.000               0.517          0.441
lipocalin                0.558         0.302    0.371     5.000              0.222         0.315   2.000               0.681          0.453
scp2                     0.632         0.430    0.729     2.667              0.528         0.589   2.667               0.630          0.565

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.531               0.487                  0.032                     0.176
net_AUC           0.537               0.526                  0.109                     0.113

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.472                  0.041                     0.203
net_AUC_prot           0.518               0.516                  0.128                     0.106

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.606               0.581                  0.084                     0.119
net_AUC_lipid           0.535               0.536                  0.102                     0.073

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.531  0.447      0.511     0.481
10     0.531  0.579      0.511     0.544
49     0.531  0.563      0.511     0.540
51     0.531  0.548      0.511     0.538
120    0.531  0.537      0.511     0.518

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.623         0.680      0.057          0.656              0.689           0.033
10        0.623         0.657      0.034          0.656              0.686           0.030
49        0.623         0.667      0.043          0.656              0.694           0.038
51        0.623         0.671      0.048          0.656              0.693           0.037
120       0.623         0.680      0.056          0.656              0.704           0.048

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.475  0.465      0.348     0.484     0.525         0.553      0.028          0.589              0.613           0.024
GLTP          0.484  0.524      0.488     0.559     0.519         0.661      0.142          0.547              0.687           0.140
IP_trans      0.726  0.588      0.719     0.616     0.726         0.751      0.025          0.729              0.762           0.033
LBP_BPI_CETP  0.811  0.591      0.812     0.594     0.811         0.820      0.009          0.815              0.825           0.010
START         0.487  0.493      0.461     0.467     0.513         0.546      0.034          0.559              0.584           0.024
lipocalin     0.302  0.371      0.222     0.315     0.698         0.735      0.037          0.696              0.758           0.061
scp2          0.430  0.729      0.528     0.589     0.570         0.690      0.120          0.655              0.696           0.042

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.531               0.487                  0.032                     0.176
net               0.537               0.526                  0.109                     0.113
fit_chem          0.623               0.580                  0.031                     0.120
fit_chem_net      0.680               0.691                  0.067                     0.102
increment         0.056               0.022                  0.046                     0.052

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.472                  0.041                     0.203
net_prot               0.518               0.516                  0.128                     0.106
fit_chem_prot          0.656               0.655                  0.032                     0.098
fit_chem_net_prot      0.704               0.704                  0.069                     0.086
increment_prot         0.048               0.026                  0.045                     0.044
```
