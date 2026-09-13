# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protgeom8

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protgeom8'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.4946      0.6291      0.9210      0.8556      0.5871      0.6185
groups_choline            5      0.3640      0.8084      0.9163      0.7170      0.4250      0.8012
groups_phosphorus_free    5      0.3290      0.8386      0.8300      0.6625      0.3800      0.8929
groups_sphingolipids      5      0.3273      0.6291      0.5461      0.6188      0.5333      0.5815
ALL                      20      0.3787      0.7263      0.8034      0.7135      0.4814      0.7235

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5789      0.5780     0.0475  20
max valid BA                0.6024      0.5921     0.0583  20
best valid F1               0.5196      0.5607     0.1142  20
test BA                     0.5525      0.5588     0.0749  20
test F1                     0.3808      0.4034     0.1684  20
test sensitivity            0.3787      0.3817     0.2109  20
test specificity            0.7263      0.7292     0.2076  20
test precision              0.4893      0.4701     0.1088  18
test loss                   0.8914      0.8054     0.2658  20
FPR (FP/(FP+TN))            0.2737      0.2708     0.2076  20
FNR (FN/(FN+TP))            0.6213      0.6183     0.2109  20

=== abs(sensitivity-specificity) gap: mean=0.4057 median=0.3713 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5738      0.5801     0.0155  5
  max valid BA                0.6028      0.6040     0.0167  5
  best valid F1               0.5600      0.5620     0.0135  5
  test BA                     0.5619      0.5631     0.0115  5
  test F1                     0.4696      0.4583     0.0333  5
  test sensitivity            0.4946      0.4731     0.0772  5
  test specificity            0.6291      0.6358     0.0661  5
  test precision              0.4519      0.4444     0.0146  5
  test loss                   1.2197      1.1789     0.2452  5
  FPR (FP/(FP+TN))            0.3709      0.3642     0.0661  5
  FNR (FN/(FN+TP))            0.5054      0.5269     0.0772  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5911      0.5967     0.0415  5
  max valid BA                0.6131      0.5967     0.0453  5
  best valid F1               0.5705      0.5714     0.0468  5
  test BA                     0.5862      0.5872     0.0390  5
  test F1                     0.4302      0.4022     0.0835  5
  test sensitivity            0.3640      0.3243     0.1417  5
  test specificity            0.8084      0.8084     0.1111  5
  test precision              0.5815      0.5484     0.1046  5
  test loss                   0.8452      0.7986     0.1932  5
  FPR (FP/(FP+TN))            0.1916      0.1916     0.1111  5
  FNR (FN/(FN+TP))            0.6360      0.6757     0.1417  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6079      0.5810     0.0653  5
  max valid BA                0.6364      0.5988     0.0887  5
  best valid F1               0.4450      0.3590     0.1916  5
  test BA                     0.5838      0.5382     0.0923  5
  test F1                     0.3665      0.2800     0.1878  5
  test sensitivity            0.3290      0.2258     0.2635  5
  test specificity            0.8386      0.8421     0.0980  5
  test precision              0.5150      0.5500     0.0881  5
  test loss                   0.7858      0.6912     0.2112  5
  FPR (FP/(FP+TN))            0.1614      0.1579     0.0980  5
  FNR (FN/(FN+TP))            0.6710      0.7742     0.2635  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5429      0.5589     0.0400  5
  max valid BA                0.5574      0.5589     0.0430  5
  best valid F1               0.5031      0.5500     0.1012  5
  test BA                     0.4782      0.5000     0.0824  5
  test F1                     0.2567      0.3529     0.2427  5
  test sensitivity            0.3273      0.4545     0.3041  5
  test specificity            0.6291      0.5818     0.3615  5
  test precision              0.3550      0.3115     0.0960  3
  test loss                   0.7148      0.7026     0.0562  5
  FPR (FP/(FP+TN))            0.3709      0.4182     0.3615  5
  FNR (FN/(FN+TP))            0.6727      0.5455     0.3041  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.571      11.6              0.530         0.498     5.4               0.501          0.606              0.501         0.564
choline                     0.687         0.646    0.549       9.4              0.696         0.587     1.8               0.565          0.392              0.622         0.537
phosphorus_free             0.396         0.499    0.550       1.2              0.739         0.598     5.4               0.514          0.732              0.484         0.629
sphingolipids               0.599         0.543    0.382       1.6              0.496         0.343     3.2               0.537          0.492              0.490         0.379

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.513               0.552                  0.116                     0.088

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                   0.04                     0.120
net_AUC_prot           0.507               0.500                   0.15                     0.118

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.556               0.576                  0.149                     0.146

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.527               0.531                  0.103                     0.106

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.516  0.450      0.501     0.417
10     0.516  0.489      0.501     0.467
49     0.516  0.535      0.501     0.531
51     0.516  0.542      0.501     0.527
120    0.516  0.513      0.501     0.507

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.647      0.019          0.708              0.722           0.014
10        0.628         0.686      0.058          0.708              0.735           0.028
49        0.628         0.664      0.036          0.708              0.740           0.032
51        0.628         0.669      0.042          0.708              0.738           0.030
120       0.628         0.676      0.049          0.708              0.744           0.036

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.585  0.571      0.566     0.498     0.585         0.609      0.024          0.657              0.665           0.009
choline          0.671  0.549      0.671     0.587     0.671         0.698      0.027          0.767              0.776           0.009
phosphorus_free  0.289  0.550      0.289     0.598     0.711         0.751      0.040          0.772              0.811           0.039
sphingolipids    0.521  0.382      0.480     0.343     0.544         0.648      0.104          0.635              0.722           0.088

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.516               0.553                  0.041                     0.164
net               0.513               0.552                  0.116                     0.088
fit_chem          0.628               0.637                  0.034                     0.077
fit_chem_net      0.676               0.683                  0.046                     0.062
increment         0.049               0.032                  0.045                     0.038

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.501               0.527                  0.043                     0.162
net_prot               0.507               0.500                  0.150                     0.118
fit_chem_prot          0.708               0.701                  0.042                     0.072
fit_chem_net_prot      0.744               0.756                  0.043                     0.064
increment_prot         0.036               0.019                  0.048                     0.037
```
