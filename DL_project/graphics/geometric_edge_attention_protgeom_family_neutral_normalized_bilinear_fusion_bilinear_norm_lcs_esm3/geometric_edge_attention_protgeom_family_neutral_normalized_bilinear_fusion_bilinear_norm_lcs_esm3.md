# geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.5527      0.6000      0.9317      0.8362      0.5871      0.5934
groups_choline            5      0.5856      0.5509      0.9231      0.7246      0.5661      0.6750
groups_phosphorus_free    5      0.2516      0.8175      0.8506      0.6901      0.4400      0.7607
groups_sphingolipids      5      0.4606      0.4073      0.8317      0.5224      0.6424      0.4556
ALL                      20      0.4626      0.5939      0.8843      0.6933      0.5589      0.6212

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5552      0.5613     0.0508  20
max valid BA                0.5900      0.5904     0.0563  20
best valid F1               0.5409      0.5532     0.0859  20
test BA                     0.5283      0.5360     0.0753  20
test F1                     0.3988      0.4546     0.1724  20
test sensitivity            0.4626      0.4699     0.2704  20
test specificity            0.5939      0.6228     0.2554  20
test precision              0.4027      0.4376     0.1340  20
test loss                   1.0192      0.9289     0.3246  20
FPR (FP/(FP+TN))            0.4061      0.3772     0.2554  20
FNR (FN/(FN+TP))            0.5374      0.5301     0.2704  20

=== abs(sensitivity-specificity) gap: mean=0.3959 median=0.2230 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5671      0.5755     0.0328  5
  max valid BA                0.5902      0.5908     0.0186  5
  best valid F1               0.5491      0.5478     0.0117  5
  test BA                     0.5763      0.5706     0.0214  5
  test F1                     0.4982      0.5000     0.0442  5
  test sensitivity            0.5527      0.5699     0.1101  5
  test specificity            0.6000      0.5629     0.0989  5
  test precision              0.4622      0.4725     0.0229  5
  test loss                   1.2658      1.2496     0.1761  5
  FPR (FP/(FP+TN))            0.4000      0.4371     0.0989  5
  FNR (FN/(FN+TP))            0.4473      0.4301     0.1101  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5807      0.5804     0.0329  5
  max valid BA                0.6205      0.6235     0.0059  5
  best valid F1               0.5976      0.6000     0.0124  5
  test BA                     0.5682      0.5748     0.0350  5
  test F1                     0.5083      0.5246     0.0686  5
  test sensitivity            0.5856      0.5135     0.2098  5
  test specificity            0.5509      0.6048     0.2006  5
  test precision              0.4700      0.4454     0.0473  5
  test loss                   0.8132      0.7545     0.1721  5
  FPR (FP/(FP+TN))            0.4491      0.3952     0.2006  5
  FNR (FN/(FN+TP))            0.4144      0.4865     0.2098  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5630      0.5637     0.0673  5
  max valid BA                0.6004      0.5744     0.0799  5
  best valid F1               0.4851      0.5172     0.1461  5
  test BA                     0.5346      0.5119     0.0721  5
  test F1                     0.2781      0.1951     0.1860  5
  test sensitivity            0.2516      0.1290     0.2240  5
  test specificity            0.8175      0.8947     0.1492  5
  test precision              0.4277      0.4000     0.1441  5
  test loss                   1.0116      0.9972     0.2952  5
  FPR (FP/(FP+TN))            0.1825      0.1053     0.1492  5
  FNR (FN/(FN+TP))            0.7484      0.8710     0.2240  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5103      0.5185     0.0444  5
  max valid BA                0.5490      0.5261     0.0700  5
  best valid F1               0.5319      0.5500     0.0728  5
  test BA                     0.4339      0.4364     0.0631  5
  test F1                     0.3105      0.3059     0.2114  5
  test sensitivity            0.4606      0.3939     0.3953  5
  test specificity            0.4073      0.2909     0.3594  5
  test precision              0.2508      0.2917     0.1486  5
  test loss                   0.9863      0.8485     0.4714  5
  FPR (FP/(FP+TN))            0.5927      0.7091     0.3594  5
  FNR (FN/(FN+TP))            0.5394      0.6061     0.3953  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.557      11.6              0.530         0.497     5.4               0.501          0.616              0.501         0.559
choline                     0.687         0.646    0.547       9.4              0.696         0.596     1.8               0.565          0.537              0.622         0.535
phosphorus_free             0.396         0.499    0.406       1.2              0.739         0.476     5.4               0.514          0.688              0.484         0.594
sphingolipids               0.599         0.543    0.401       1.6              0.496         0.313     3.2               0.537          0.454              0.490         0.388

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.478               0.488                  0.081                     0.086

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.471               0.485                  0.093                     0.117

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.574               0.550                  0.139                     0.101

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.519               0.534                  0.104                     0.090

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.516  0.467      0.501     0.443
10     0.516  0.486      0.501     0.473
49     0.516  0.468      0.501     0.468
51     0.516  0.468      0.501     0.467
120    0.516  0.478      0.501     0.471

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.648      0.020          0.708              0.725           0.018
10        0.628         0.653      0.025          0.708              0.727           0.020
49        0.628         0.669      0.041          0.708              0.737           0.030
51        0.628         0.663      0.036          0.708              0.739           0.032
120       0.628         0.655      0.027          0.708              0.732           0.025

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.585  0.557      0.566     0.497     0.585         0.611      0.026          0.657              0.662           0.006
choline          0.671  0.547      0.671     0.596     0.671         0.683      0.012          0.767              0.768           0.001
phosphorus_free  0.289  0.406      0.289     0.476     0.711         0.728      0.016          0.772              0.788           0.016
sphingolipids    0.521  0.401      0.480     0.313     0.544         0.600      0.056          0.635              0.712           0.077

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.516               0.553                  0.041                     0.164
net               0.478               0.488                  0.081                     0.086
fit_chem          0.628               0.637                  0.034                     0.077
fit_chem_net      0.655               0.647                  0.031                     0.061
increment         0.027               0.020                  0.019                     0.020

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.501               0.527                  0.043                     0.162
net_prot               0.471               0.485                  0.093                     0.117
fit_chem_prot          0.708               0.701                  0.042                     0.072
fit_chem_net_prot      0.732               0.725                  0.032                     0.057
increment_prot         0.025               0.006                  0.023                     0.035
```
