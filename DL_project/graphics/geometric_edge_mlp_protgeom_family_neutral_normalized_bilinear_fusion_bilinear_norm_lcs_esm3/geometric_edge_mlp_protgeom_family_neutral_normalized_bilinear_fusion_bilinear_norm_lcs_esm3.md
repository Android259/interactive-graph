# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.5204      0.6079      0.9348      0.8667      0.5097      0.6225
groups_choline            5      0.3081      0.8635      0.9051      0.7136      0.2982      0.8762
groups_phosphorus_free    5      0.2968      0.8456      0.9012      0.7646      0.3000      0.8179
groups_sphingolipids      5      0.2000      0.7818      0.6081      0.7500      0.2182      0.8481
ALL                      20      0.3313      0.7747      0.8373      0.7737      0.3315      0.7912

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5613      0.5591     0.0396  20
max valid BA                0.6031      0.5979     0.0428  20
best valid F1               0.4922      0.4925     0.0828  20
test BA                     0.5530      0.5438     0.0733  20
test F1                     0.3561      0.4027     0.1811  20
test sensitivity            0.3313      0.3387     0.2075  20
test specificity            0.7747      0.7865     0.1375  20
test precision              0.4413      0.4584     0.1854  20
test loss                   1.0299      1.0385     0.3933  20
FPR (FP/(FP+TN))            0.2253      0.2135     0.1375  20
FNR (FN/(FN+TP))            0.6687      0.6613     0.2075  20

=== abs(sensitivity-specificity) gap: mean=0.4476 median=0.4864 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5661      0.5772     0.0257  5
  max valid BA                0.5816      0.5793     0.0258  5
  best valid F1               0.5257      0.5306     0.0368  5
  test BA                     0.5642      0.5722     0.0321  5
  test F1                     0.4829      0.4944     0.0275  5
  test sensitivity            0.5204      0.5484     0.0434  5
  test specificity            0.6079      0.5960     0.0779  5
  test precision              0.4537      0.4554     0.0447  5
  test loss                   1.2558      1.2901     0.1921  5
  FPR (FP/(FP+TN))            0.3921      0.4040     0.0779  5
  FNR (FN/(FN+TP))            0.4796      0.4516     0.0434  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5872      0.5878     0.0440  5
  max valid BA                0.6187      0.6131     0.0253  5
  best valid F1               0.4894      0.4706     0.0649  5
  test BA                     0.5858      0.5841     0.0850  5
  test F1                     0.3755      0.3188     0.2035  5
  test sensitivity            0.3081      0.2252     0.2237  5
  test specificity            0.8635      0.8743     0.0790  5
  test precision              0.5769      0.6283     0.2075  5
  test loss                   0.8364      0.7408     0.1975  5
  FPR (FP/(FP+TN))            0.1365      0.1257     0.0790  5
  FNR (FN/(FN+TP))            0.6919      0.7748     0.2237  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5589      0.5542     0.0435  5
  max valid BA                0.6361      0.6571     0.0627  5
  best valid F1               0.4936      0.5479     0.1243  5
  test BA                     0.5712      0.5897     0.0983  5
  test F1                     0.3356      0.4231     0.2293  5
  test sensitivity            0.2968      0.3226     0.2534  5
  test specificity            0.8456      0.8772     0.0673  5
  test precision              0.4409      0.5238     0.1906  5
  test loss                   0.8917      0.8015     0.3402  5
  FPR (FP/(FP+TN))            0.1544      0.1228     0.0673  5
  FNR (FN/(FN+TP))            0.7032      0.6774     0.2534  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5332      0.5522     0.0331  5
  max valid BA                0.5761      0.5774     0.0178  5
  best valid F1               0.4601      0.4719     0.0941  5
  test BA                     0.4909      0.4939     0.0293  5
  test F1                     0.2305      0.2609     0.1422  5
  test sensitivity            0.2000      0.1818     0.1415  5
  test specificity            0.7818      0.7455     0.1483  5
  test precision              0.2939      0.3636     0.1773  5
  test loss                   1.1358      0.6884     0.6283  5
  FPR (FP/(FP+TN))            0.2182      0.2545     0.1483  5
  FNR (FN/(FN+TP))            0.8000      0.8182     0.1415  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.546      11.6              0.530         0.469     5.4               0.501          0.605              0.501         0.531
choline                     0.687         0.646    0.477       9.4              0.696         0.531     1.8               0.565          0.400              0.622         0.520
phosphorus_free             0.396         0.499    0.620       1.2              0.739         0.627     5.4               0.514          0.715              0.484         0.628
sphingolipids               0.599         0.543    0.433       1.6              0.496         0.391     3.2               0.537          0.557              0.490         0.493

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.519               0.526                  0.078                     0.082

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                      0.12
net_AUC_prot           0.505               0.498                  0.103                      0.10

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.569               0.590                  0.098                     0.131

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.543               0.517                  0.062                     0.059

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.516  0.459      0.501     0.435
10     0.516  0.473      0.501     0.434
49     0.516  0.528      0.501     0.515
51     0.516  0.514      0.501     0.503
120    0.516  0.519      0.501     0.505

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.648      0.020          0.708              0.723           0.015
10        0.628         0.665      0.037          0.708              0.731           0.023
49        0.628         0.663      0.035          0.708              0.740           0.032
51        0.628         0.673      0.045          0.708              0.740           0.032
120       0.628         0.649      0.021          0.708              0.721           0.013

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.585  0.546      0.566     0.469     0.585         0.600      0.015          0.657              0.664           0.008
choline          0.671  0.477      0.671     0.531     0.671         0.677      0.006          0.767              0.769           0.002
phosphorus_free  0.289  0.620      0.289     0.627     0.711         0.740      0.029          0.772              0.797           0.025
sphingolipids    0.521  0.433      0.480     0.391     0.544         0.579      0.035          0.635              0.652           0.017

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.516               0.553                  0.041                     0.164
net               0.519               0.526                  0.078                     0.082
fit_chem          0.628               0.637                  0.034                     0.077
fit_chem_net      0.649               0.648                  0.046                     0.074
increment         0.021               0.010                  0.028                     0.013

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.501               0.527                  0.043                     0.162
net_prot               0.505               0.498                  0.103                     0.100
fit_chem_prot          0.708               0.701                  0.042                     0.072
fit_chem_net_prot      0.721               0.714                  0.041                     0.073
increment_prot         0.013               0.003                  0.021                     0.010
```
