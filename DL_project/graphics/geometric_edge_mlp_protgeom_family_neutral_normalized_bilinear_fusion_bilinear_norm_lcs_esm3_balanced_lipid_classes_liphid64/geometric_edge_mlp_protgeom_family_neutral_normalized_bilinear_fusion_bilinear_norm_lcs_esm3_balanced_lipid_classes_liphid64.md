# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_liphid64

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_liphid64'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6946      0.7027      0.8897      0.8295      0.7204      0.7637
groups_choline            5      0.4847      0.6020      0.8715      0.8022      0.5375      0.6495
groups_phosphorus_free    5      0.5419      0.5061      0.8743      0.7434      0.7067      0.6286
groups_sphingolipids      5      0.7455      0.5463      0.8835      0.7691      0.7455      0.6850
ALL                      20      0.6167      0.5893      0.8798      0.7861      0.6775      0.6817

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6505      0.6706     0.0854  20
max valid BA                0.6796      0.7008     0.0967  20
best valid F1               0.6271      0.6466     0.1035  20
test BA                     0.6030      0.6127     0.1056  20
test AUC                    0.5720      0.5965     0.1441  18
test AUC in-protein         0.5484      0.5461     0.1244  10
  (proteins averaged)       6.5000      6.0000     4.9944  10
test F1                     0.5344      0.5840     0.1374  20
test sensitivity            0.6167      0.6613     0.1960  20
test specificity            0.5893      0.6584     0.2005  20
test precision              0.4867      0.4990     0.1255  20
test loss                   0.8821      0.8613     0.1907  20
FPR (FP/(FP+TN))            0.4107      0.3416     0.2005  20
FNR (FN/(FN+TP))            0.3833      0.3387     0.1960  20

=== abs(sensitivity-specificity) gap: mean=0.2277 median=0.1679 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7207      0.7202     0.0153  5
  max valid BA                0.7421      0.7372     0.0124  5
  best valid F1               0.6597      0.6526     0.0156  5
  test BA                     0.6987      0.6910     0.0234  5
  test AUC                    0.7252      0.7164     0.0241  3
  test AUC in-protein         0.4625      0.4625     0.0000  1
    (proteins averaged)      11.0000     11.0000     0.0000  1
  test F1                     0.6091      0.6019     0.0278  5
  test sensitivity            0.6946      0.6882     0.0434  5
  test specificity            0.7027      0.7049     0.0175  5
  test precision              0.5428      0.5289     0.0211  5
  test loss                   0.8790      0.8624     0.1032  5
  FPR (FP/(FP+TN))            0.2973      0.2951     0.0175  5
  FNR (FN/(FN+TP))            0.3054      0.3118     0.0434  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5733      0.5748     0.0572  5
  max valid BA                0.5935      0.5805     0.0621  5
  best valid F1               0.5264      0.5481     0.0584  5
  test BA                     0.5433      0.5400     0.0963  5
  test AUC                    0.5021      0.5041     0.1239  5
  test AUC in-protein         0.5040      0.5461     0.1312  4
    (proteins averaged)      11.2500     11.5000     0.9574  4
  test F1                     0.4344      0.4615     0.1222  5
  test sensitivity            0.4847      0.5315     0.1803  5
  test specificity            0.6020      0.6337     0.2034  5
  test precision              0.4119      0.4176     0.1222  5
  test loss                   0.8969      0.8603     0.1795  5
  FPR (FP/(FP+TN))            0.3980      0.3663     0.2034  5
  FNR (FN/(FN+TP))            0.5153      0.4685     0.1803  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6431      0.6439     0.0583  5
  max valid BA                0.6676      0.6847     0.0691  5
  best valid F1               0.6023      0.6377     0.1101  5
  test BA                     0.5240      0.5504     0.0741  5
  test AUC                    0.5095      0.5451     0.1129  5
  test AUC in-protein         0.5500      0.5500     0.0707  2
    (proteins averaged)       1.5000      1.5000     0.7071  2
  test F1                     0.4430      0.5000     0.1515  5
  test sensitivity            0.5419      0.5806     0.2654  5
  test specificity            0.5061      0.5306     0.1380  5
  test precision              0.3902      0.4211     0.0777  5
  test loss                   1.0063      0.9111     0.2581  5
  FPR (FP/(FP+TN))            0.4939      0.4694     0.1380  5
  FNR (FN/(FN+TP))            0.4581      0.4194     0.2654  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6647      0.7083     0.1174  5
  max valid BA                0.7152      0.7155     0.1406  5
  best valid F1               0.7200      0.6804     0.0979  5
  test BA                     0.6459      0.6593     0.1080  5
  test AUC                    0.6124      0.6009     0.1711  5
  test AUC in-protein         0.6352      0.6097     0.1496  3
    (proteins averaged)       2.0000      2.0000     0.0000  3
  test F1                     0.6509      0.6579     0.0646  5
  test sensitivity            0.7455      0.7576     0.1431  5
  test specificity            0.5463      0.6098     0.3211  5
  test precision              0.6021      0.5814     0.1191  5
  test loss                   0.7461      0.7474     0.1434  5
  FPR (FP/(FP+TN))            0.4537      0.3902     0.3211  5
  FNR (FN/(FN+TP))            0.2545      0.2424     0.1431  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.728      11.6              0.530         0.512     5.4               0.501          0.674              0.501         0.531
choline                     0.687         0.646    0.433       9.4              0.696         0.505     1.8               0.565          0.374              0.622         0.497
phosphorus_free             0.396         0.499    0.617       1.2              0.739         0.864     5.4               0.514          0.574              0.484         0.478
sphingolipids               0.599         0.543    0.558       1.6              0.496         0.384     3.2               0.537          0.480              0.490         0.431

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.584               0.655                  0.135                     0.123

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.533               0.516                  0.146                     0.207

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.526               0.587                  0.167                     0.129

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.484               0.519                  0.111                     0.042

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.542  0.456      0.602     0.515
10     0.542  0.464      0.602     0.534
49     0.542  0.562      0.602     0.572
51     0.542  0.567      0.602     0.543
120    0.542  0.584      0.602     0.533

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.557         0.621      0.064          0.881              0.884           0.003
10        0.557         0.680      0.122          0.881              0.894           0.012
49        0.557         0.668      0.111          0.881              0.900           0.019
51        0.557         0.681      0.123          0.881              0.903           0.021
120       0.557         0.703      0.146          0.881              0.903           0.021

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.495  0.728      0.530     0.512     0.512         0.731      0.219          0.889              0.886          -0.003
choline          0.646  0.433      0.696     0.505     0.646         0.676      0.029          0.867              0.867           0.000
phosphorus_free  0.499  0.617      0.739     0.864     0.536         0.668      0.133          0.967              0.971           0.003
sphingolipids    0.526  0.558      0.496     0.384     0.535         0.739      0.204          0.802              0.888           0.085

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.542               0.514                  0.038                     0.071
net               0.584               0.655                  0.135                     0.123
fit_chem          0.557               0.533                  0.028                     0.060
fit_chem_net      0.703               0.709                  0.069                     0.036
increment         0.146               0.132                  0.072                     0.086

=== the same rows ranked INSIDE each protein, epoch 120 ===
121 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.602               0.553                  0.039                     0.120
net_prot               0.533               0.516                  0.146                     0.207
fit_chem_prot          0.881               0.871                  0.022                     0.068
fit_chem_net_prot      0.903               0.887                  0.031                     0.046
increment_prot         0.021               0.003                  0.024                     0.043
```
