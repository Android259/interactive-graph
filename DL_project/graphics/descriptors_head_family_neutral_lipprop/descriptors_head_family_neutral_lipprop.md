# descriptors_head_family_neutral_lipprop

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_head_family_neutral_lipprop'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6239      0.4623      0.6349      0.4144      0.6866      0.4839
groups_GLTP            5      0.5200      0.5600      0.7373      0.3443      0.5385      0.7692
groups_IP_trans        5      0.6348      0.3872      0.6116      0.4311      0.7333      0.4255
groups_LBP_BPI_CETP    5      0.6522      0.7021      0.6222      0.4407      0.8583      0.6894
groups_START           5      0.5754      0.5528      0.4860      0.5072      0.3469      0.7775
groups_lipocalin       5      0.5944      0.4806      0.6985      0.3786      0.6667      0.4472
groups_scp2            5      0.7647      0.2529      0.6452      0.4189      0.8471      0.3176
ALL                   35      0.6236      0.4854      0.6336      0.4193      0.6682      0.5586

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5759      0.5625     0.0852  35
max valid BA                0.6134      0.5882     0.0897  35
best valid F1               0.5843      0.5769     0.0957  35
test BA                     0.5545      0.5481     0.0749  35
test AUC                    0.5560      0.5461     0.1359  35
test AUC in-protein         0.5470      0.4919     0.1535  35
  (proteins averaged)       3.1429      3.0000     1.0042  35
test AUC in-protein (pairs)      0.5857      0.5849     0.1481  35
  (proteins contributing)      3.5143      3.0000     1.7213  35
test F1                     0.4966      0.5000     0.1208  35
test sensitivity            0.6236      0.6389     0.2302  35
test specificity            0.4854      0.4722     0.2629  35
test precision              0.4677      0.4630     0.1238  34
test loss                   0.6931      0.6934     0.0228  35
FPR (FP/(FP+TN))            0.5146      0.5278     0.2629  35
FNR (FN/(FN+TP))            0.3764      0.3611     0.2302  35

=== abs(sensitivity-specificity) gap: mean=0.3901 median=0.2469 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5697      0.5688     0.0299  5
  max valid BA                0.5852      0.5894     0.0324  5
  best valid F1               0.6656      0.6424     0.0364  5
  test BA                     0.5431      0.5481     0.0131  5
  test AUC                    0.5529      0.5521     0.0276  5
  test AUC in-protein         0.5086      0.5366     0.0595  5
    (proteins averaged)       4.0000      4.0000     0.0000  5
  test AUC in-protein (pairs)      0.6312      0.6197     0.0235  5
    (proteins contributing)      4.4000      4.0000     0.5477  5
  test F1                     0.5893      0.5957     0.0258  5
  test sensitivity            0.6239      0.6418     0.0591  5
  test specificity            0.4623      0.4426     0.0680  5
  test precision              0.5611      0.5676     0.0130  5
  test loss                   0.6855      0.6851     0.0034  5
  FPR (FP/(FP+TN))            0.5377      0.5574     0.0680  5
  FNR (FN/(FN+TP))            0.3761      0.3582     0.0591  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5885      0.5769     0.1377  5
  max valid BA                0.6538      0.6538     0.0732  5
  best valid F1               0.6319      0.6522     0.0577  5
  test BA                     0.5400      0.5400     0.0616  5
  test AUC                    0.4832      0.4544     0.1060  5
  test AUC in-protein         0.4845      0.4600     0.0612  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4337      0.3981     0.0749  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5277      0.5128     0.0519  5
  test sensitivity            0.5200      0.5200     0.1095  5
  test specificity            0.5600      0.4800     0.1811  5
  test precision              0.5590      0.5500     0.0950  5
  test loss                   0.7295      0.7227     0.0388  5
  FPR (FP/(FP+TN))            0.4400      0.5200     0.1811  5
  FNR (FN/(FN+TP))            0.4800      0.4800     0.1095  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5670      0.5793     0.0362  5
  max valid BA                0.5794      0.5869     0.0426  5
  best valid F1               0.5182      0.5106     0.0353  5
  test BA                     0.5110      0.5106     0.0457  5
  test AUC                    0.5079      0.5079     0.0996  5
  test AUC in-protein         0.5627      0.6353     0.1351  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5268      0.5731     0.1073  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.4243      0.4490     0.0826  5
  test sensitivity            0.6348      0.6957     0.2794  5
  test specificity            0.3872      0.2979     0.3048  5
  test precision              0.3428      0.3333     0.0473  5
  test loss                   0.6862      0.6944     0.0135  5
  FPR (FP/(FP+TN))            0.6128      0.7021     0.3048  5
  FNR (FN/(FN+TP))            0.3652      0.3043     0.2794  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6590      0.6232     0.1435  5
  max valid BA                0.7738      0.8112     0.0646  5
  best valid F1               0.7030      0.7458     0.0690  5
  test BA                     0.6772      0.6425     0.1010  5
  test AUC                    0.8331      0.8261     0.0738  5
  test AUC in-protein         0.8517      0.8805     0.0772  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.8488      0.8843     0.0722  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5704      0.5287     0.1210  5
  test sensitivity            0.6522      0.6522     0.2868  5
  test specificity            0.7021      0.7872     0.3265  5
  test precision              0.5871      0.6429     0.1302  5
  test loss                   0.6757      0.6696     0.0138  5
  FPR (FP/(FP+TN))            0.2979      0.2128     0.3265  5
  FNR (FN/(FN+TP))            0.3478      0.3478     0.2868  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5548      0.5708     0.0499  5
  max valid BA                0.5622      0.5708     0.0549  5
  best valid F1               0.5655      0.5972     0.0597  5
  test BA                     0.5641      0.5602     0.0384  5
  test AUC                    0.5508      0.5621     0.0580  5
  test AUC in-protein         0.4830      0.4647     0.0658  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5344      0.5250     0.0945  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.5144      0.4755     0.0619  5
  test sensitivity            0.5754      0.5231     0.2347  5
  test specificity            0.5528      0.6742     0.2722  5
  test precision              0.5031      0.5000     0.0642  5
  test loss                   0.6889      0.6908     0.0114  5
  FPR (FP/(FP+TN))            0.4472      0.3258     0.2722  5
  FNR (FN/(FN+TP))            0.4246      0.4769     0.2347  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5333      0.5417     0.0238  5
  max valid BA                0.5569      0.5486     0.0292  5
  best valid F1               0.4688      0.5077     0.0756  5
  test BA                     0.5375      0.5486     0.0289  5
  test AUC                    0.4846      0.4630     0.0549  5
  test AUC in-protein         0.5054      0.4491     0.1039  5
    (proteins averaged)       5.0000      5.0000     0.0000  5
  test AUC in-protein (pairs)      0.5897      0.6190     0.0754  5
    (proteins contributing)      7.2000      7.0000     0.4472  5
  test F1                     0.3871      0.4694     0.2200  5
  test sensitivity            0.5944      0.6389     0.3646  5
  test specificity            0.4806      0.4583     0.3128  5
  test precision              0.3629      0.3679     0.0122  4
  test loss                   0.6907      0.6958     0.0132  5
  FPR (FP/(FP+TN))            0.5194      0.5417     0.3128  5
  FNR (FN/(FN+TP))            0.4056      0.3611     0.3646  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5588      0.5441     0.0682  5
  max valid BA                0.5824      0.5588     0.0836  5
  best valid F1               0.5369      0.5312     0.0618  5
  test BA                     0.5088      0.5441     0.0663  5
  test AUC                    0.4796      0.4939     0.0634  5
  test AUC in-protein         0.4335      0.4461     0.0846  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5350      0.5833     0.1417  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.4632      0.5000     0.0695  5
  test sensitivity            0.7647      0.8235     0.2080  5
  test specificity            0.2529      0.2059     0.1645  5
  test precision              0.3372      0.3571     0.0366  5
  test loss                   0.6956      0.6951     0.0020  5
  FPR (FP/(FP+TN))            0.7471      0.7941     0.1645  5
  FNR (FN/(FN+TP))            0.2353      0.1765     0.2080  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (apolar_sasa_share,aromatic_share,buriedness_q50,chain,hbond,heavy,hydropathy_rim,pocket_elongation,pocket_flatness,pocket_volume_per_sasa,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.263         0.636    0.506              0.609         0.526
GLTP                     0.278         0.676    0.488              0.747         0.310
IP_trans                 0.326         0.509    0.544              0.530         0.466
LBP_BPI_CETP             0.308         0.634    0.732              0.652         0.768
START                    0.273         0.430    0.418              0.497         0.469
lipocalin                0.273         0.663    0.461              0.639         0.493
scp2                     0.275         0.622    0.550              0.617         0.553

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.596               0.617                  0.057                     0.091
net_AUC           0.529               0.539                  0.093                     0.101

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.613               0.614                  0.060                     0.082
net_AUC_pair           0.512               0.493                  0.101                     0.137

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.596  0.455      0.613     0.469
10     0.596  0.505      0.613     0.478
49     0.596  0.534      0.613     0.502
51     0.596  0.533      0.613     0.507
120    0.596  0.529      0.613     0.512

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.621         0.680      0.059
10        0.621         0.680      0.060
49        0.621         0.677      0.056
51        0.621         0.678      0.058
120       0.621         0.672      0.051

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.636  0.506      0.609     0.526     0.636         0.634     -0.001
GLTP          0.676  0.488      0.747     0.310     0.676         0.761      0.084
IP_trans      0.509  0.544      0.530     0.466     0.542         0.590      0.047
LBP_BPI_CETP  0.634  0.732      0.652     0.768     0.634         0.774      0.141
START         0.430  0.418      0.497     0.469     0.570         0.599      0.029
lipocalin     0.663  0.461      0.639     0.493     0.663         0.673      0.010
scp2          0.622  0.550      0.617     0.553     0.622         0.672      0.051

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.596               0.617                  0.057                     0.091
net               0.529               0.539                  0.093                     0.101
fit_chem          0.621               0.617                  0.054                     0.048
fit_chem_net      0.672               0.658                  0.052                     0.073
increment         0.051               0.033                  0.029                     0.048

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.613               0.614                  0.060                     0.082
net_pair       0.512               0.493                  0.101                     0.137
```
