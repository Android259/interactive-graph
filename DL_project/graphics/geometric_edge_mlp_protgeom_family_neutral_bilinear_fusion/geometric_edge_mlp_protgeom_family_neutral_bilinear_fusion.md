# geometric_edge_mlp_protgeom_family_neutral_bilinear_fusion

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_bilinear_fusion'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5045      0.6164      0.5560      0.5032      0.5373      0.6355
groups_GLTP            5      0.6400      0.4880      0.5327      0.5236      0.6692      0.4846
groups_IP_trans        5      0.5565      0.6298      0.5994      0.4540      0.5667      0.6596
groups_LBP_BPI_CETP    5      0.5478      0.7277      0.6021      0.4902      0.5917      0.7106
groups_START           5      0.6462      0.3348      0.5734      0.5034      0.6625      0.3663
groups_lipocalin       5      0.5111      0.6972      0.5920      0.5242      0.5889      0.7389
groups_scp2            5      0.6824      0.5059      0.5927      0.4583      0.6706      0.6000
ALL                   35      0.5841      0.5714      0.5783      0.4938      0.6124      0.5994

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6059      0.6029     0.0686  35
max valid BA                0.6597      0.6618     0.0657  35
best valid F1               0.6395      0.6286     0.0596  35
test BA                     0.5777      0.5680     0.0980  35
test F1                     0.4939      0.5200     0.1612  35
test sensitivity            0.5841      0.6522     0.2694  35
test specificity            0.5714      0.6596     0.2711  35
test precision              0.4895      0.4595     0.1315  35
test loss                   8.0883      1.0827    23.6079  35
FPR (FP/(FP+TN))            0.4286      0.3404     0.2711  35
FNR (FN/(FN+TP))            0.4159      0.3478     0.2694  35

=== abs(sensitivity-specificity) gap: mean=0.4066 median=0.3600 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5864      0.5792     0.0329  5
  max valid BA                0.6090      0.6172     0.0334  5
  best valid F1               0.7052      0.7000     0.0162  5
  test BA                     0.5604      0.5756     0.0329  5
  test F1                     0.5239      0.5500     0.1384  5
  test sensitivity            0.5045      0.4925     0.2072  5
  test specificity            0.6164      0.6721     0.1893  5
  test precision              0.5932      0.6087     0.0336  5
  test loss                  29.8281      1.3032    60.1876  5
  FPR (FP/(FP+TN))            0.3836      0.3279     0.1893  5
  FNR (FN/(FN+TP))            0.4955      0.5075     0.2072  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5769      0.5769     0.0490  5
  max valid BA                0.6269      0.6154     0.0375  5
  best valid F1               0.6987      0.6944     0.0327  5
  test BA                     0.5640      0.5000     0.1558  5
  test F1                     0.5684      0.6341     0.2144  5
  test sensitivity            0.6400      0.6800     0.3187  5
  test specificity            0.4880      0.6400     0.3526  5
  test precision              0.5630      0.5000     0.1944  5
  test loss                   0.8015      0.7230     0.1663  5
  FPR (FP/(FP+TN))            0.5120      0.3600     0.3526  5
  FNR (FN/(FN+TP))            0.3600      0.3200     0.3187  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6131      0.6215     0.0495  5
  max valid BA                0.6841      0.6742     0.0321  5
  best valid F1               0.5964      0.5862     0.0304  5
  test BA                     0.5932      0.5925     0.0452  5
  test F1                     0.4763      0.5079     0.0684  5
  test sensitivity            0.5565      0.6087     0.1354  5
  test specificity            0.6298      0.6383     0.0923  5
  test precision              0.4241      0.4286     0.0425  5
  test loss                   8.9517      1.9087    15.7707  5
  FPR (FP/(FP+TN))            0.3702      0.3617     0.0923  5
  FNR (FN/(FN+TP))            0.4435      0.3913     0.1354  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6512      0.6348     0.0752  5
  max valid BA                0.7438      0.7482     0.0464  5
  best valid F1               0.6665      0.6667     0.0460  5
  test BA                     0.6377      0.5657     0.1390  5
  test F1                     0.4642      0.4938     0.2518  5
  test sensitivity            0.5478      0.6957     0.3908  5
  test specificity            0.7277      0.7872     0.3150  5
  test precision              0.5526      0.6154     0.1322  5
  test loss                   2.9868      0.6097     5.3314  5
  FPR (FP/(FP+TN))            0.2723      0.2128     0.3150  5
  FNR (FN/(FN+TP))            0.4522      0.3043     0.3908  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5144      0.5084     0.0164  5
  max valid BA                0.5775      0.5561     0.0395  5
  best valid F1               0.6060      0.6009     0.0195  5
  test BA                     0.4905      0.5000     0.0458  5
  test F1                     0.4478      0.5652     0.2174  5
  test sensitivity            0.6462      0.8000     0.4049  5
  test specificity            0.3348      0.2472     0.3371  5
  test precision              0.3779      0.4221     0.0878  5
  test loss                   2.3663      1.7514     2.0099  5
  FPR (FP/(FP+TN))            0.6652      0.7528     0.3371  5
  FNR (FN/(FN+TP))            0.3538      0.2000     0.4049  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6639      0.6597     0.0831  5
  max valid BA                0.6972      0.6944     0.0630  5
  best valid F1               0.6127      0.6087     0.0822  5
  test BA                     0.6042      0.6042     0.0966  5
  test F1                     0.4601      0.3922     0.1492  5
  test sensitivity            0.5111      0.3333     0.2904  5
  test specificity            0.6972      0.7222     0.2021  5
  test precision              0.4804      0.4231     0.1461  5
  test loss                   6.7550      0.9719     8.2778  5
  FPR (FP/(FP+TN))            0.3028      0.2778     0.2021  5
  FNR (FN/(FN+TP))            0.4889      0.6667     0.2904  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6353      0.6324     0.0366  5
  max valid BA                0.6794      0.6912     0.0242  5
  best valid F1               0.5910      0.5882     0.0213  5
  test BA                     0.5941      0.5882     0.0861  5
  test F1                     0.5167      0.5000     0.0612  5
  test sensitivity            0.6824      0.7059     0.1220  5
  test specificity            0.5059      0.4412     0.2473  5
  test precision              0.4354      0.3939     0.0997  5
  test loss                   4.9285      4.9653     4.3372  5
  FPR (FP/(FP+TN))            0.4941      0.5588     0.2473  5
  FNR (FN/(FN+TP))            0.3176      0.2941     0.1220  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                         
CRAL-TRIO                0.630         0.483    0.577       4.0              0.365         0.513     5.0               0.449          0.553              0.432         0.569
GLTP                     0.605         0.521    0.553       2.0              0.511         0.524     3.0               0.523          0.525              0.524         0.556
IP_trans                 0.722         0.681    0.611       3.0              0.677         0.640     2.4               0.590          0.517              0.669         0.519
LBP_BPI_CETP             0.719         0.798    0.667       2.0              0.798         0.667     1.6               0.784          0.613              0.821         0.689
START                    0.576         0.508    0.454       3.0              0.475         0.502     4.0               0.535          0.625              0.519         0.548
lipocalin                0.565         0.334    0.563       5.0              0.252         0.596     2.2               0.647          0.428              0.623         0.504
scp2                     0.651         0.488    0.568       2.8              0.592         0.519     2.6               0.649          0.542              0.577         0.544

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.545               0.499                  0.066                     0.151
net_AUC           0.570               0.587                  0.118                     0.064

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.524               0.493                  0.065                     0.185
net_AUC_prot           0.566               0.553                  0.117                     0.068

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.597               0.581                  0.085                     0.109
net_AUC_lipid           0.543               0.555                  0.159                     0.066

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.595               0.575                  0.056                     0.126
net_AUC_pair           0.561               0.566                  0.123                     0.061

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.564      0.524     0.565
10     0.545  0.565      0.524     0.573
49     0.545  0.522      0.524     0.527
51     0.545  0.546      0.524     0.542
120    0.545  0.570      0.524     0.566

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.619         0.655      0.036          0.655              0.693           0.038
10        0.619         0.657      0.038          0.655              0.688           0.033
49        0.619         0.658      0.039          0.655              0.686           0.031
51        0.619         0.659      0.040          0.655              0.692           0.037
120       0.619         0.662      0.042          0.655              0.685           0.031

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.483  0.577      0.365     0.513     0.539         0.596      0.057          0.614              0.662           0.048
GLTP          0.521  0.553      0.511     0.524     0.542         0.582      0.040          0.565              0.593           0.028
IP_trans      0.681  0.611      0.677     0.640     0.681         0.693      0.013          0.692              0.699           0.007
LBP_BPI_CETP  0.798  0.667      0.798     0.667     0.798         0.803      0.005          0.801              0.803           0.002
START         0.508  0.454      0.475     0.502     0.536         0.601      0.065          0.604              0.629           0.024
lipocalin     0.334  0.563      0.252     0.596     0.666         0.720      0.054          0.672              0.732           0.060
scp2          0.488  0.568      0.592     0.519     0.572         0.635      0.063          0.636              0.680           0.044

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.545               0.499                  0.066                     0.151
net               0.570               0.587                  0.118                     0.064
fit_chem          0.619               0.580                  0.052                     0.100
fit_chem_net      0.662               0.649                  0.061                     0.081
increment         0.042               0.025                  0.040                     0.024

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.524               0.493                  0.065                     0.185
net_prot               0.566               0.553                  0.117                     0.068
fit_chem_prot          0.655               0.658                  0.053                     0.077
fit_chem_net_prot      0.685               0.695                  0.059                     0.069
increment_prot         0.031               0.026                  0.022                     0.022
```
