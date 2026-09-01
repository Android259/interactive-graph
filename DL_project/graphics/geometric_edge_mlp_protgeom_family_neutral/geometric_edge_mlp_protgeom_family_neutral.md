# geometric_edge_mlp_protgeom_family_neutral

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral'
rows: 21

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.8607      0.2678      0.6514      0.5999      0.8557      0.2903
groups_GLTP            3      0.7067      0.4533      0.7863      0.5295      0.6923      0.5385
groups_IP_trans        3      0.5217      0.7021      0.5886      0.7112      0.6528      0.7234
groups_LBP_BPI_CETP    3      0.1739      0.8227      0.5962      0.6933      0.3056      0.8227
groups_START           3      0.7795      0.3071      0.8714      0.6069      0.8646      0.2809
groups_lipocalin       3      0.5185      0.5787      0.5770      0.5744      0.5370      0.5787
groups_scp2            3      0.6667      0.5980      0.7534      0.5713      0.7843      0.6667
ALL                   21      0.6040      0.5328      0.6892      0.6124      0.6703      0.5573

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6138      0.6118     0.0827  21
max valid BA                0.6565      0.6479     0.0743  21
best valid F1               0.6348      0.6452     0.0673  21
test BA                     0.5684      0.5739     0.0582  21
test F1                     0.4867      0.5283     0.1888  21
test sensitivity            0.6040      0.6418     0.3099  21
test specificity            0.5328      0.5393     0.3026  21
test precision              0.4893      0.4737     0.1210  21
test loss                   0.7856      0.7171     0.2387  21
FPR (FP/(FP+TN))            0.4672      0.4607     0.3026  21
FNR (FN/(FN+TP))            0.3960      0.3582     0.3099  21

=== abs(sensitivity-specificity) gap: mean=0.4970 median=0.4400 n=21 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5730      0.5738     0.0392  3
  max valid BA                0.5920      0.5843     0.0524  3
  best valid F1               0.7097      0.7135     0.0130  3
  test BA                     0.5642      0.5752     0.0191  3
  test F1                     0.6753      0.7143     0.0676  3
  test sensitivity            0.8607      0.9701     0.1896  3
  test specificity            0.2678      0.1803     0.1514  3
  test precision              0.5630      0.5652     0.0039  3
  test loss                   0.6834      0.6875     0.0073  3
  FPR (FP/(FP+TN))            0.7322      0.8197     0.1514  3
  FNR (FN/(FN+TP))            0.1393      0.0299     0.1896  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6154      0.6346     0.0881  3
  max valid BA                0.6474      0.6346     0.0968  3
  best valid F1               0.6934      0.6970     0.0251  3
  test BA                     0.5800      0.6200     0.0872  3
  test F1                     0.6138      0.6286     0.0945  3
  test sensitivity            0.7067      0.8400     0.2663  3
  test specificity            0.4533      0.4400     0.3802  3
  test precision              0.6011      0.6000     0.1127  3
  test loss                   0.7537      0.7520     0.0489  3
  FPR (FP/(FP+TN))            0.5467      0.5600     0.3802  3
  FNR (FN/(FN+TP))            0.2933      0.1600     0.2663  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6881      0.7145     0.0849  3
  max valid BA                0.7228      0.7269     0.0361  3
  best valid F1               0.6369      0.6452     0.0452  3
  test BA                     0.6119      0.6341     0.0401  3
  test F1                     0.4527      0.5283     0.1537  3
  test sensitivity            0.5217      0.6087     0.3135  3
  test specificity            0.7021      0.6596     0.2369  3
  test precision              0.5206      0.4667     0.1279  3
  test loss                   0.7102      0.7171     0.0335  3
  FPR (FP/(FP+TN))            0.2979      0.3404     0.2369  3
  FNR (FN/(FN+TP))            0.4783      0.3913     0.3135  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5641      0.5408     0.0491  3
  max valid BA                0.6712      0.6742     0.0665  3
  best valid F1               0.5901      0.5818     0.0613  3
  test BA                     0.4983      0.5046     0.0169  3
  test F1                     0.1763      0.0800     0.1742  3
  test sensitivity            0.1739      0.0435     0.2259  3
  test specificity            0.8227      0.9149     0.2173  3
  test precision              0.3444      0.3333     0.1503  3
  test loss                   1.2396      1.0293     0.4253  3
  FPR (FP/(FP+TN))            0.1773      0.0851     0.2173  3
  FNR (FN/(FN+TP))            0.8261      0.9565     0.2259  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5727      0.5743     0.0558  3
  max valid BA                0.6034      0.5936     0.0213  3
  best valid F1               0.6184      0.6263     0.0178  3
  test BA                     0.5433      0.5402     0.0292  3
  test F1                     0.5608      0.6000     0.0845  3
  test sensitivity            0.7795      0.9231     0.2487  3
  test specificity            0.3071      0.2247     0.2039  3
  test precision              0.4493      0.4444     0.0140  3
  test loss                   0.7877      0.7792     0.0349  3
  FPR (FP/(FP+TN))            0.6929      0.7753     0.2039  3
  FNR (FN/(FN+TP))            0.2205      0.0769     0.2487  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5579      0.5347     0.0526  3
  max valid BA                0.6181      0.6181     0.0556  3
  best valid F1               0.5373      0.5147     0.0407  3
  test BA                     0.5486      0.5417     0.0593  3
  test F1                     0.3898      0.4853     0.1726  3
  test sensitivity            0.5185      0.5278     0.4029  3
  test specificity            0.5787      0.6944     0.4624  3
  test precision              0.4867      0.4634     0.1695  3
  test loss                   0.6837      0.6610     0.0430  3
  FPR (FP/(FP+TN))            0.4213      0.3056     0.4624  3
  FNR (FN/(FN+TP))            0.4815      0.4722     0.4029  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7255      0.7500     0.0557  3
  max valid BA                0.7402      0.7500     0.0594  3
  best valid F1               0.6581      0.6667     0.0688  3
  test BA                     0.6324      0.6176     0.0389  3
  test F1                     0.5387      0.5306     0.0432  3
  test sensitivity            0.6667      0.7059     0.1225  3
  test specificity            0.5980      0.6471     0.1390  3
  test precision              0.4600      0.4737     0.0484  3
  test loss                   0.6410      0.6539     0.0250  3
  FPR (FP/(FP+TN))            0.4020      0.3529     0.1390  3
  FNR (FN/(FN+TP))            0.3333      0.2941     0.1225  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.475    0.534     4.000              0.348         0.466   5.000               0.467          0.637
GLTP                     0.595         0.484    0.518     2.000              0.488         0.495   3.000               0.494          0.575
IP_trans                 0.727         0.726    0.664     3.000              0.719         0.708   2.667               0.664          0.627
LBP_BPI_CETP             0.721         0.811    0.681     2.000              0.812         0.685   1.667               0.792          0.558
START                    0.574         0.487    0.530     3.000              0.461         0.502   4.000               0.517          0.507
lipocalin                0.558         0.302    0.334     5.000              0.222         0.325   2.000               0.681          0.515
scp2                     0.632         0.430    0.688     2.667              0.528         0.578   2.667               0.630          0.563

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.531               0.487                  0.032                     0.176
net_AUC           0.564               0.584                  0.084                     0.127

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.472                  0.041                     0.203
net_AUC_prot           0.537               0.504                  0.082                     0.133

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.606               0.581                  0.084                     0.119
net_AUC_lipid           0.569               0.601                  0.108                     0.050

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.531  0.554      0.511     0.567
10     0.531  0.568      0.511     0.559
49     0.531  0.565      0.511     0.536
51     0.531  0.583      0.511     0.555
120    0.531  0.564      0.511     0.537

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.623         0.688      0.064          0.656              0.714           0.058
10        0.623         0.666      0.043          0.656              0.686           0.030
49        0.623         0.664      0.041          0.656              0.687           0.031
51        0.623         0.671      0.047          0.656              0.693           0.038
120       0.623         0.670      0.047          0.656              0.693           0.037

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.475  0.534      0.348     0.466     0.525         0.569      0.043          0.589              0.636           0.047
GLTP          0.484  0.518      0.488     0.495     0.519         0.573      0.054          0.547              0.574           0.027
IP_trans      0.726  0.664      0.719     0.708     0.726         0.763      0.037          0.729              0.765           0.036
LBP_BPI_CETP  0.811  0.681      0.812     0.685     0.811         0.813      0.002          0.815              0.825           0.009
START         0.487  0.530      0.461     0.502     0.513         0.597      0.085          0.559              0.615           0.055
lipocalin     0.302  0.334      0.222     0.325     0.698         0.728      0.030          0.696              0.732           0.035
scp2          0.430  0.688      0.528     0.578     0.570         0.649      0.079          0.655              0.707           0.052

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.531               0.487                  0.032                     0.176
net               0.564               0.584                  0.084                     0.127
fit_chem          0.623               0.580                  0.031                     0.120
fit_chem_net      0.670               0.640                  0.042                     0.098
increment         0.047               0.033                  0.040                     0.029

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.472                  0.041                     0.203
net_prot               0.537               0.504                  0.082                     0.133
fit_chem_prot          0.656               0.655                  0.032                     0.098
fit_chem_net_prot      0.693               0.708                  0.048                     0.089
increment_prot         0.037               0.025                  0.038                     0.016
```
