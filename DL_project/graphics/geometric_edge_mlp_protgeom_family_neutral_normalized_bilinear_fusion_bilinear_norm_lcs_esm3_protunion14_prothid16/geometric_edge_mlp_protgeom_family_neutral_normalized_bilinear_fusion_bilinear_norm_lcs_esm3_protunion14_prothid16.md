# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protunion14_prothid16

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protunion14_prothid16'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.5355      0.5709      0.9509      0.8924      0.6387      0.5656
groups_choline            5      0.3604      0.8072      0.8876      0.6545      0.4446      0.8024
groups_phosphorus_free    5      0.4387      0.7754      0.9103      0.7909      0.5200      0.8286
groups_sphingolipids      5      0.3697      0.6255      0.8951      0.5127      0.5273      0.6296
ALL                      20      0.4261      0.6947      0.9110      0.7126      0.5327      0.7065

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5785      0.5816     0.0651  20
max valid BA                0.6196      0.6184     0.0669  20
best valid F1               0.5577      0.5658     0.0681  20
test BA                     0.5604      0.5572     0.0715  20
test AUC                    0.5586      0.5673     0.0979  20
test AUC in-protein         0.5627      0.5362     0.0951  20
  (proteins averaged)       7.9000      8.5000     3.5968  20
test AUC in-protein (pairs)      0.5778      0.5857     0.1091  20
  (proteins contributing)     11.7000     14.0000     5.3024  20
test F1                     0.4105      0.4457     0.1554  20
test sensitivity            0.4261      0.3926     0.2456  20
test specificity            0.6947      0.7206     0.2176  20
test precision              0.4646      0.4649     0.1353  20
test loss                   1.0602      0.8439     0.4445  20
FPR (FP/(FP+TN))            0.3053      0.2794     0.2176  20
FNR (FN/(FN+TP))            0.5739      0.6074     0.2456  20

=== abs(sensitivity-specificity) gap: mean=0.4159 median=0.4348 n=20 ===
sensitivity std across seeds (by group): mean=0.2256 median=0.2231 n=4
specificity std across seeds (by group): mean=0.1816 median=0.1309 n=4

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5825      0.5871     0.0256  5
  max valid BA                0.6021      0.5970     0.0232  5
  best valid F1               0.5668      0.5587     0.0179  5
  test BA                     0.5532      0.5599     0.0185  5
  test AUC                    0.5682      0.5661     0.0163  5
  test AUC in-protein         0.5072      0.4927     0.0480  5
    (proteins averaged)      12.2000     12.0000     0.4472  5
  test AUC in-protein (pairs)      0.5562      0.5710     0.0350  5
    (proteins contributing)     16.4000     17.0000     1.5166  5
  test F1                     0.4755      0.4679     0.0457  5
  test sensitivity            0.5355      0.5484     0.1152  5
  test specificity            0.5709      0.5166     0.1046  5
  test precision              0.4366      0.4366     0.0221  5
  test loss                   1.5221      1.5058     0.0727  5
  FPR (FP/(FP+TN))            0.4291      0.4834     0.1046  5
  FNR (FN/(FN+TP))            0.4645      0.4516     0.1152  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6039      0.5908     0.0272  5
  max valid BA                0.6235      0.6295     0.0194  5
  best valid F1               0.5526      0.5729     0.0599  5
  test BA                     0.5838      0.5843     0.0337  5
  test AUC                    0.6003      0.5972     0.0552  5
  test AUC in-protein         0.6510      0.6547     0.0946  5
    (proteins averaged)       9.8000     10.0000     0.4472  5
  test AUC in-protein (pairs)      0.6218      0.6250     0.1026  5
    (proteins contributing)     14.8000     15.0000     0.4472  5
  test F1                     0.4318      0.4574     0.0681  5
  test sensitivity            0.3604      0.3784     0.0956  5
  test specificity            0.8072      0.8443     0.1096  5
  test precision              0.5712      0.5584     0.0853  5
  test loss                   0.7453      0.7134     0.0999  5
  FPR (FP/(FP+TN))            0.1928      0.1557     0.1096  5
  FNR (FN/(FN+TP))            0.6396      0.6216     0.0956  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6139      0.6179     0.0929  5
  max valid BA                0.6743      0.6952     0.0871  5
  best valid F1               0.5795      0.6061     0.1067  5
  test BA                     0.6071      0.6443     0.0979  5
  test AUC                    0.6198      0.6327     0.1223  5
  test AUC in-protein         0.6048      0.5935     0.0799  5
    (proteins averaged)       6.6000      7.0000     1.1402  5
  test AUC in-protein (pairs)      0.6531      0.6512     0.0947  5
    (proteins contributing)     12.2000     13.0000     2.1679  5
  test F1                     0.4091      0.5714     0.2612  5
  test sensitivity            0.4387      0.6129     0.3310  5
  test specificity            0.7754      0.7193     0.1521  5
  test precision              0.4600      0.5000     0.1505  5
  test loss                   0.9000      0.6662     0.3537  5
  FPR (FP/(FP+TN))            0.2246      0.2807     0.1521  5
  FNR (FN/(FN+TP))            0.5613      0.3871     0.3310  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5136      0.5126     0.0496  5
  max valid BA                0.5785      0.5808     0.0805  5
  best valid F1               0.5320      0.5500     0.0718  5
  test BA                     0.4976      0.5000     0.0693  5
  test AUC                    0.4462      0.4314     0.0669  5
  test AUC in-protein         0.4878      0.4951     0.0505  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4803      0.5197     0.1176  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.3256      0.3556     0.1577  5
  test sensitivity            0.3697      0.2424     0.3607  5
  test specificity            0.6255      0.7273     0.3601  5
  test precision              0.3905      0.3750     0.1856  5
  test loss                   1.0734      0.7737     0.6126  5
  FPR (FP/(FP+TN))            0.3745      0.2727     0.3601  5
  FNR (FN/(FN+TP))            0.6303      0.7576     0.3607  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.567      11.6              0.530         0.504     5.4               0.501          0.632              0.501         0.568
choline                     0.687         0.646    0.488       9.4              0.696         0.586     1.8               0.565          0.440              0.622         0.529
phosphorus_free             0.396         0.499    0.631       1.2              0.739         0.645     5.4               0.514          0.639              0.484         0.600
sphingolipids               0.599         0.543    0.423       1.6              0.496         0.428     3.2               0.537          0.490              0.490         0.432

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.527               0.542                  0.078                     0.091

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.541               0.562                  0.108                     0.095

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.550               0.589                  0.144                     0.101

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.532               0.561                  0.083                     0.073

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.516  0.468      0.501     0.454
10     0.516  0.482      0.501     0.469
49     0.516  0.545      0.501     0.540
51     0.516  0.531      0.501     0.555
120    0.516  0.527      0.501     0.541

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.651      0.024          0.708              0.722           0.015
10        0.628         0.666      0.038          0.708              0.727           0.019
49        0.628         0.648      0.021          0.708              0.727           0.020
51        0.628         0.651      0.023          0.708              0.725           0.018
120       0.628         0.666      0.038          0.708              0.731           0.024

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.585  0.567      0.566     0.504     0.585         0.603      0.018          0.657              0.667           0.011
choline          0.671  0.488      0.671     0.586     0.671         0.684      0.013          0.767              0.770           0.003
phosphorus_free  0.289  0.631      0.289     0.645     0.711         0.728      0.017          0.772              0.786           0.014
sphingolipids    0.521  0.423      0.480     0.428     0.544         0.648      0.104          0.635              0.702           0.067

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.516               0.553                  0.041                     0.164
net               0.527               0.542                  0.078                     0.091
fit_chem          0.628               0.637                  0.034                     0.077
fit_chem_net      0.666               0.674                  0.045                     0.053
increment         0.038               0.024                  0.047                     0.044

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.501               0.527                  0.043                     0.162
net_prot               0.541               0.562                  0.108                     0.095
fit_chem_prot          0.708               0.701                  0.042                     0.072
fit_chem_net_prot      0.731               0.751                  0.044                     0.056
increment_prot         0.024               0.008                  0.036                     0.029
```
