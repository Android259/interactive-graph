# geometric_edge_mlp_nwd

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_nwd'
rows: 14

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       2      0.6642      0.4262      0.6800      0.4589      0.6791      0.4435
groups_GLTP            2      0.5600      0.3600      0.6629      0.4672      0.6538      0.4231
groups_IP_trans        2      0.9130      0.2872      0.9008      0.2955      0.9583      0.3723
groups_LBP_BPI_CETP    2      0.6304      0.5106      0.7513      0.6347      0.7500      0.5319
groups_START           2      0.4000      0.6573      0.7594      0.5000      0.4219      0.6685
groups_lipocalin       2      0.6944      0.2639      0.6346      0.3654      0.7917      0.2917
groups_scp2            2      0.4706      0.7353      0.7204      0.5828      0.5882      0.8824
ALL                   14      0.6190      0.4629      0.7299      0.4721      0.6919      0.5162

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6040      0.5769     0.0906  14
max valid BA                0.6294      0.6061     0.0881  14
best valid F1               0.6224      0.6128     0.0805  14
test BA                     0.5409      0.5452     0.0644  14
test F1                     0.4628      0.5000     0.1738  14
test sensitivity            0.6190      0.6304     0.3121  14
test specificity            0.4629      0.4341     0.2997  14
test precision              0.4045      0.4155     0.1471  14
test loss                   0.7115      0.6969     0.0446  14
FPR (FP/(FP+TN))            0.5371      0.5659     0.2997  14
FNR (FN/(FN+TP))            0.3810      0.3696     0.3121  14

=== abs(sensitivity-specificity) gap: mean=0.5108 median=0.4900 n=14 ===

=== By group ===
groups_CRAL-TRIO (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5613      0.5613     0.0140  2
  max valid BA                0.6319      0.6319     0.0494  2
  best valid F1               0.7058      0.7058     0.0065  2
  test BA                     0.5452      0.5452     0.0008  2
  test F1                     0.5834      0.5834     0.1492  2
  test sensitivity            0.6642      0.6642     0.3694  2
  test specificity            0.4262      0.4262     0.3709  2
  test precision              0.5678      0.5678     0.0271  2
  test loss                   0.6916      0.6916     0.0021  2
  FPR (FP/(FP+TN))            0.5738      0.5738     0.3709  2
  FNR (FN/(FN+TP))            0.3358      0.3358     0.3694  2

groups_GLTP (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5385      0.5385     0.0272  2
  max valid BA                0.5673      0.5673     0.0680  2
  best valid F1               0.6710      0.6710     0.0061  2
  test BA                     0.4600      0.4600     0.0283  2
  test F1                     0.4510      0.4510     0.2657  2
  test sensitivity            0.5600      0.5600     0.5091  2
  test specificity            0.3600      0.3600     0.4525  2
  test precision              0.4370      0.4370     0.0741  2
  test loss                   0.7024      0.7024     0.0028  2
  FPR (FP/(FP+TN))            0.6400      0.6400     0.4525  2
  FNR (FN/(FN+TP))            0.4400      0.4400     0.5091  2

groups_IP_trans (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6653      0.6653     0.0370  2
  max valid BA                0.6653      0.6653     0.0370  2
  best valid F1               0.6012      0.6012     0.0314  2
  test BA                     0.6001      0.6001     0.0226  2
  test F1                     0.5421      0.5421     0.0148  2
  test sensitivity            0.9130      0.9130     0.0000  2
  test specificity            0.2872      0.2872     0.0451  2
  test precision              0.3856      0.3856     0.0150  2
  test loss                   0.7234      0.7234     0.0428  2
  FPR (FP/(FP+TN))            0.7128      0.7128     0.0451  2
  FNR (FN/(FN+TP))            0.0870      0.0870     0.0000  2

groups_LBP_BPI_CETP (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6410      0.6410     0.1047  2
  max valid BA                0.6676      0.6676     0.1128  2
  best valid F1               0.5942      0.5942     0.1025  2
  test BA                     0.5705      0.5705     0.1050  2
  test F1                     0.4866      0.4866     0.0733  2
  test sensitivity            0.6304      0.6304     0.0307  2
  test specificity            0.5106      0.5106     0.2407  2
  test precision              0.4044      0.4044     0.1108  2
  test loss                   0.6657      0.6657     0.0524  2
  FPR (FP/(FP+TN))            0.4894      0.4894     0.2407  2
  FNR (FN/(FN+TP))            0.3696      0.3696     0.0307  2

groups_START (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5452      0.5452     0.0529  2
  max valid BA                0.5747      0.5747     0.0112  2
  best valid F1               0.6022      0.6022     0.0001  2
  test BA                     0.5287      0.5287     0.0564  2
  test F1                     0.2955      0.2955     0.4178  2
  test sensitivity            0.4000      0.4000     0.5657  2
  test specificity            0.6573      0.6573     0.4529  2
  test precision              0.2342      0.2342     0.3313  2
  test loss                   0.7452      0.7452     0.0737  2
  FPR (FP/(FP+TN))            0.3427      0.3427     0.4529  2
  FNR (FN/(FN+TP))            0.6000      0.6000     0.5657  2

groups_lipocalin (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5417      0.5417     0.0589  2
  max valid BA                0.5417      0.5417     0.0589  2
  best valid F1               0.5000      0.5000     0.0000  2
  test BA                     0.4792      0.4792     0.0295  2
  test F1                     0.4167      0.4167     0.1179  2
  test sensitivity            0.6944      0.6944     0.4321  2
  test specificity            0.2639      0.2639     0.3732  2
  test precision              0.3125      0.3125     0.0295  2
  test loss                   0.7395      0.7395     0.0652  2
  FPR (FP/(FP+TN))            0.7361      0.7361     0.3732  2
  FNR (FN/(FN+TP))            0.3056      0.3056     0.4321  2

groups_scp2 (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7353      0.7353     0.1248  2
  max valid BA                0.7574      0.7574     0.0936  2
  best valid F1               0.6824      0.6824     0.1165  2
  test BA                     0.6029      0.6029     0.0000  2
  test F1                     0.4643      0.4643     0.0505  2
  test sensitivity            0.4706      0.4706     0.1664  2
  test specificity            0.7353      0.7353     0.1664  2
  test precision              0.4901      0.4901     0.0783  2
  test loss                   0.7130      0.7130     0.0472  2
  FPR (FP/(FP+TN))            0.2647      0.2647     0.1664  2
  FNR (FN/(FN+TP))            0.5294      0.5294     0.1664  2
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.627         0.489    0.398       4.0              0.369         0.340     5.0               0.498          0.445
GLTP                     0.583         0.495    0.446       2.0              0.505         0.500     3.0               0.522          0.514
IP_trans                 0.742         0.703    0.527       3.0              0.698         0.632     2.5               0.576          0.320
LBP_BPI_CETP             0.724         0.827    0.603       2.0              0.830         0.618     1.5               0.804          0.524
START                    0.579         0.487    0.525       3.0              0.471         0.527     4.0               0.548          0.457
lipocalin                0.544         0.271    0.301       5.0              0.214         0.257     2.0               0.733          0.475
scp2                     0.645         0.409    0.614       2.5              0.488         0.623     2.0               0.642          0.470

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.526               0.489                  0.018                     0.185
net_AUC           0.488               0.475                  0.090                     0.113

=== the same rows ranked INSIDE each protein ===
43 protein blocks across 14 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15       0.51               0.482                  0.024                     0.203
net_AUC_prot            0.50               0.497                  0.093                     0.148

=== the same rows ranked INSIDE each lipid class ===
40 lipid class blocks across 14 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.618               0.594                  0.072                     0.114
net_AUC_lipid           0.458               0.452                  0.131                     0.067

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.526  0.531       0.51     0.478
10     0.526  0.497       0.51     0.437
49     0.526  0.511       0.51     0.465
51     0.526  0.462       0.51     0.438
120    0.526  0.488       0.51     0.500

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.626         0.656      0.030          0.664              0.689           0.025
10        0.626         0.650      0.024          0.664              0.692           0.027
49        0.626         0.663      0.036          0.664              0.704           0.040
51        0.626         0.668      0.041          0.664              0.705           0.040
120       0.626         0.675      0.049          0.664              0.705           0.041

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.489  0.398      0.369     0.340     0.511         0.597      0.086          0.600              0.664           0.064
GLTP          0.495  0.446      0.505     0.500     0.510         0.573      0.063          0.551              0.578           0.027
IP_trans      0.703  0.527      0.698     0.632     0.703         0.725      0.021          0.704              0.727           0.022
LBP_BPI_CETP  0.827  0.603      0.830     0.618     0.827         0.843      0.015          0.833              0.850           0.017
START         0.487  0.525      0.471     0.527     0.513         0.554      0.040          0.557              0.579           0.022
lipocalin     0.271  0.301      0.214     0.257     0.729         0.754      0.025          0.718              0.755           0.037
scp2          0.409  0.614      0.488     0.623     0.591         0.682      0.091          0.687              0.784           0.097

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.526               0.489                  0.018                     0.185
net               0.488               0.475                  0.090                     0.113
fit_chem          0.626               0.591                  0.017                     0.128
fit_chem_net      0.675               0.660                  0.031                     0.107
increment         0.049               0.040                  0.041                     0.031

=== the same rows ranked INSIDE each protein, epoch 120 ===
43 protein blocks across 14 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.510               0.482                  0.024                     0.203
net_prot               0.500               0.497                  0.093                     0.148
fit_chem_prot          0.664               0.673                  0.020                     0.102
fit_chem_net_prot      0.705               0.701                  0.037                     0.103
increment_prot         0.041               0.031                  0.041                     0.029
```
