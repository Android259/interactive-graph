# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protunion14_prothid32_lambdasqrt

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protunion14_prothid32_lambdasqrt'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6796      0.4768      0.9281      0.8147      0.6323      0.5232
groups_choline            5      0.4577      0.7305      0.8472      0.6954      0.5821      0.6881
groups_phosphorus_free    5      0.4645      0.6667      0.9368      0.6583      0.6133      0.6286
groups_sphingolipids      5      0.3394      0.7127      0.7053      0.6882      0.5273      0.7148
ALL                      20      0.4853      0.6467      0.8544      0.7142      0.5888      0.6387

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5826      0.5732     0.0581  20
max valid BA                0.6137      0.5888     0.0666  20
best valid F1               0.5496      0.5594     0.0834  20
test BA                     0.5660      0.5553     0.0937  20
test AUC                    0.5713      0.5686     0.1107  20
test AUC in-protein         0.5708      0.5687     0.1211  20
  (proteins averaged)       7.9000      8.5000     3.5968  20
test AUC in-protein (pairs)      0.5813      0.5761     0.1242  20
  (proteins contributing)     11.7000     14.0000     5.3024  20
test F1                     0.4361      0.5147     0.1820  20
test sensitivity            0.4853      0.4752     0.2722  20
test specificity            0.6467      0.6922     0.2333  20
test precision              0.4558      0.4356     0.1461  20
test loss                   1.0036      0.9600     0.3304  20
FPR (FP/(FP+TN))            0.3533      0.3078     0.2333  20
FNR (FN/(FN+TP))            0.5147      0.5248     0.2722  20

=== abs(sensitivity-specificity) gap: mean=0.4102 median=0.3376 n=20 ===
sensitivity std across seeds (by group): mean=0.2284 median=0.1989 n=4
specificity std across seeds (by group): mean=0.1981 median=0.1504 n=4

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5659      0.5655     0.0230  5
  max valid BA                0.5777      0.5796     0.0160  5
  best valid F1               0.5413      0.5469     0.0250  5
  test BA                     0.5782      0.5792     0.0338  5
  test AUC                    0.5755      0.5699     0.0289  5
  test AUC in-protein         0.5375      0.5605     0.0548  5
    (proteins averaged)      12.2000     12.0000     0.4472  5
  test AUC in-protein (pairs)      0.5793      0.5758     0.0359  5
    (proteins contributing)     16.4000     17.0000     1.5166  5
  test F1                     0.5368      0.5360     0.0261  5
  test sensitivity            0.6796      0.7097     0.0885  5
  test specificity            0.4768      0.4702     0.1258  5
  test precision              0.4497      0.4444     0.0396  5
  test loss                   1.2502      1.2723     0.3354  5
  FPR (FP/(FP+TN))            0.5232      0.5298     0.1258  5
  FNR (FN/(FN+TP))            0.3204      0.2903     0.0885  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5961      0.6190     0.0727  5
  max valid BA                0.6351      0.6473     0.0315  5
  best valid F1               0.5837      0.5735     0.0279  5
  test BA                     0.5941      0.6399     0.1044  5
  test AUC                    0.6194      0.6533     0.1333  5
  test AUC in-protein         0.6612      0.6602     0.0656  5
    (proteins averaged)       9.8000     10.0000     0.4472  5
  test AUC in-protein (pairs)      0.6504      0.6523     0.1131  5
    (proteins contributing)     14.8000     15.0000     0.4472  5
  test F1                     0.4898      0.5165     0.1328  5
  test sensitivity            0.4577      0.4234     0.1386  5
  test specificity            0.7305      0.7605     0.1039  5
  test precision              0.5352      0.6200     0.1453  5
  test loss                   0.9158      0.8584     0.3155  5
  FPR (FP/(FP+TN))            0.2695      0.2395     0.1039  5
  FNR (FN/(FN+TP))            0.5423      0.5766     0.1386  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5819      0.5476     0.0940  5
  max valid BA                0.6210      0.5810     0.1060  5
  best valid F1               0.5193      0.5172     0.1408  5
  test BA                     0.5656      0.5059     0.1216  5
  test AUC                    0.5572      0.5102     0.1540  5
  test AUC in-protein         0.5809      0.5273     0.1874  5
    (proteins averaged)       6.6000      7.0000     1.1402  5
  test AUC in-protein (pairs)      0.5542      0.4855     0.1911  5
    (proteins contributing)     12.2000     13.0000     2.1679  5
  test F1                     0.3709      0.4000     0.2636  5
  test sensitivity            0.4645      0.3871     0.4271  5
  test specificity            0.6667      0.7544     0.3878  5
  test precision              0.4281      0.4000     0.1236  5
  test loss                   0.9763      0.8109     0.3555  5
  FPR (FP/(FP+TN))            0.3333      0.2456     0.3878  5
  FNR (FN/(FN+TP))            0.5355      0.6129     0.4271  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5865      0.5842     0.0279  5
  max valid BA                0.6210      0.5884     0.0792  5
  best valid F1               0.5543      0.5500     0.0954  5
  test BA                     0.5261      0.5485     0.1082  5
  test AUC                    0.5333      0.5295     0.1046  5
  test AUC in-protein         0.5036      0.4519     0.0993  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5413      0.5502     0.1174  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.3470      0.3860     0.1950  5
  test sensitivity            0.3394      0.3333     0.2593  5
  test specificity            0.7127      0.7636     0.1751  5
  test precision              0.4101      0.4583     0.2278  5
  test loss                   0.8722      0.7119     0.2681  5
  FPR (FP/(FP+TN))            0.2873      0.2364     0.1751  5
  FNR (FN/(FN+TP))            0.6606      0.6667     0.2593  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.544      11.6              0.530         0.466     5.4               0.501          0.605              0.501         0.550
choline                     0.687         0.646    0.496       9.4              0.696         0.572     1.8               0.565          0.416              0.622         0.512
phosphorus_free             0.396         0.499    0.556       1.2              0.739         0.573     5.4               0.514          0.631              0.484         0.528
sphingolipids               0.599         0.543    0.426       1.6              0.496         0.416     3.2               0.537          0.503              0.490         0.475

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.505               0.499                  0.100                     0.059

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.507               0.510                  0.108                     0.079

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.539               0.544                  0.108                     0.099

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.516               0.512                  0.056                     0.032

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.516  0.488      0.501     0.484
10     0.516  0.494      0.501     0.478
49     0.516  0.499      0.501     0.490
51     0.516  0.497      0.501     0.489
120    0.516  0.505      0.501     0.507

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.651      0.023          0.708              0.728           0.020
10        0.628         0.656      0.028          0.708              0.721           0.014
49        0.628         0.649      0.022          0.708              0.727           0.019
51        0.628         0.648      0.020          0.708              0.726           0.019
120       0.628         0.648      0.021          0.708              0.720           0.012

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.585  0.544      0.566     0.466     0.585         0.600      0.015          0.657              0.661           0.005
choline          0.671  0.496      0.671     0.572     0.671         0.679      0.008          0.767              0.772           0.005
phosphorus_free  0.289  0.556      0.289     0.573     0.711         0.727      0.016          0.772              0.779           0.006
sphingolipids    0.521  0.426      0.480     0.416     0.544         0.587      0.043          0.635              0.668           0.033

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.516               0.553                  0.041                     0.164
net               0.505               0.499                  0.100                     0.059
fit_chem          0.628               0.637                  0.034                     0.077
fit_chem_net      0.648               0.644                  0.034                     0.066
increment         0.021               0.009                  0.023                     0.016

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.501               0.527                  0.043                     0.162
net_prot               0.507               0.510                  0.108                     0.079
fit_chem_prot          0.708               0.701                  0.042                     0.072
fit_chem_net_prot      0.720               0.725                  0.045                     0.064
increment_prot         0.012               0.005                  0.015                     0.014
```
