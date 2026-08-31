# descriptors_coarse_pocket_elongation

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_coarse_pocket_elongation'
rows: 7

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_GLTP            1      0.3600      0.6400      0.6480      0.4238      0.3462      0.6923
groups_IP_trans        2      0.8043      0.4362      0.5207      0.5496      0.8125      0.3936
groups_LBP_BPI_CETP    3      0.8841      0.7305      0.5326      0.5747      0.8611      0.7589
groups_START           1      0.1692      0.8764      0.4334      0.6399      0.0625      0.8764
ALL                    7      0.6843      0.6543      0.5315      0.5553      0.6596      0.6618

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6607      0.6299     0.1497  7
max valid BA                0.6940      0.6746     0.1356  7
best valid F1               0.6312      0.5938     0.1351  7
test BA                     0.6693      0.6573     0.1400  7
test F1                     0.5638      0.5714     0.1844  7
test sensitivity            0.6843      0.7826     0.3042  7
test specificity            0.6543      0.6400     0.1906  7
test precision              0.5318      0.5000     0.1118  7
test loss                   0.6748      0.6801     0.0250  7
FPR (FP/(FP+TN))            0.3457      0.3600     0.1906  7
FNR (FN/(FN+TP))            0.3157      0.2174     0.3042  7

=== abs(sensitivity-specificity) gap: mean=0.3379 median=0.2800 n=7 ===

=== By group ===
groups_GLTP (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5192      0.5192     0.0000  1
  max valid BA                0.5385      0.5385     0.0000  1
  best valid F1               0.5938      0.5938     0.0000  1
  test BA                     0.5000      0.5000     0.0000  1
  test F1                     0.4186      0.4186     0.0000  1
  test sensitivity            0.3600      0.3600     0.0000  1
  test specificity            0.6400      0.6400     0.0000  1
  test precision              0.5000      0.5000     0.0000  1
  test loss                   0.6996      0.6996     0.0000  1
  FPR (FP/(FP+TN))            0.3600      0.3600     0.0000  1
  FNR (FN/(FN+TP))            0.6400      0.6400     0.0000  1

groups_IP_trans (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6031      0.6031     0.0379  2
  max valid BA                0.6631      0.6631     0.0163  2
  best valid F1               0.5752      0.5752     0.0053  2
  test BA                     0.6203      0.6203     0.0523  2
  test F1                     0.5460      0.5460     0.0360  2
  test sensitivity            0.8043      0.8043     0.0307  2
  test specificity            0.4362      0.4362     0.1354  2
  test precision              0.4150      0.4150     0.0495  2
  test loss                   0.6942      0.6942     0.0023  2
  FPR (FP/(FP+TN))            0.5638      0.5638     0.1354  2
  FNR (FN/(FN+TP))            0.1957      0.1957     0.0307  2

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8100      0.8200     0.0382  3
  max valid BA                0.8239      0.8307     0.0430  3
  best valid F1               0.7554      0.7586     0.0539  3
  test BA                     0.8073      0.7872     0.0371  3
  test F1                     0.7277      0.7083     0.0437  3
  test sensitivity            0.8841      0.9130     0.1328  3
  test specificity            0.7305      0.7872     0.1368  3
  test precision              0.6308      0.6774     0.0830  3
  test loss                   0.6518      0.6574     0.0196  3
  FPR (FP/(FP+TN))            0.2695      0.2128     0.1368  3
  FNR (FN/(FN+TP))            0.1159      0.0870     0.1328  3

groups_START (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4695      0.4695     0.0000  1
  max valid BA                0.5219      0.5219     0.0000  1
  best valid F1               0.4082      0.4082     0.0000  1
  test BA                     0.5228      0.5228     0.0000  1
  test F1                     0.2529      0.2529     0.0000  1
  test sensitivity            0.1692      0.1692     0.0000  1
  test specificity            0.8764      0.8764     0.0000  1
  test precision              0.5000      0.5000     0.0000  1
  test loss                   0.6801      0.6801     0.0000  1
  FPR (FP/(FP+TN))            0.1236      0.1236     0.0000  1
  FNR (FN/(FN+TP))            0.8308      0.8308     0.0000  1
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.630         0.484    0.518       4.0              0.369         0.538     5.0               0.458          0.482
GLTP                     0.605         0.521    0.526       2.0              0.512         0.517     3.0               0.523          0.540
IP_trans                 0.722         0.680    0.659       3.0              0.677         0.673     2.4               0.590          0.594
LBP_BPI_CETP             0.719         0.798    0.764       2.0              0.798         0.756     1.6               0.784          0.741
START                    0.576         0.508    0.445       3.0              0.474         0.468     4.0               0.536          0.496
lipocalin                0.565         0.331    0.490       5.0              0.246         0.441     2.2               0.646          0.727
scp2                     0.651         0.489    0.472       2.8              0.593         0.472     2.6               0.642          0.551

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.545               0.503                  0.065                     0.151
net_AUC           0.553               0.534                  0.082                     0.115

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.524               0.493                  0.065                     0.186
net_AUC_prot           0.552               0.536                  0.089                     0.118

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.597               0.581                  0.085                     0.106
net_AUC_lipid           0.590               0.594                  0.101                     0.105

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.450      0.524     0.477
10     0.545  0.547      0.524     0.551
49     0.545  0.558      0.524     0.564
51     0.545  0.555      0.524     0.561
120    0.545  0.553      0.524     0.552

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.618         0.677      0.059          0.653              0.708           0.054
10        0.618         0.656      0.038          0.653              0.689           0.036
49        0.618         0.663      0.045          0.653              0.694           0.041
51        0.618         0.664      0.046          0.653              0.694           0.041
120       0.618         0.657      0.039          0.653              0.685           0.032

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.484  0.518      0.369     0.538     0.539         0.572      0.033          0.613              0.653           0.039
GLTP          0.521  0.526      0.512     0.517     0.543         0.620      0.076          0.565              0.617           0.052
IP_trans      0.680  0.659      0.677     0.673     0.680         0.693      0.013          0.693              0.708           0.015
LBP_BPI_CETP  0.798  0.764      0.798     0.756     0.798         0.819      0.021          0.801              0.823           0.022
START         0.508  0.445      0.474     0.468     0.536         0.585      0.049          0.606              0.625           0.020
lipocalin     0.331  0.490      0.246     0.441     0.669         0.709      0.040          0.673              0.730           0.057
scp2          0.489  0.472      0.593     0.472     0.562         0.603      0.042          0.622              0.641           0.019

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.545               0.503                  0.065                     0.151
net               0.553               0.534                  0.082                     0.115
fit_chem          0.618               0.590                  0.052                     0.101
fit_chem_net      0.657               0.614                  0.056                     0.088
increment         0.039               0.023                  0.038                     0.021

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.524               0.493                  0.065                     0.186
net_prot               0.552               0.536                  0.089                     0.118
fit_chem_prot          0.653               0.662                  0.055                     0.078
fit_chem_net_prot      0.685               0.681                  0.057                     0.074
increment_prot         0.032               0.021                  0.033                     0.017
```
