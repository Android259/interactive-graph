# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protbind6_prothid16

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protbind6_prothid16'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.5957      0.5868      0.9170      0.8625      0.6387      0.5311
groups_choline            5      0.4685      0.7210      0.8978      0.7326      0.5054      0.7226
groups_phosphorus_free    5      0.2710      0.8421      0.8873      0.7658      0.3400      0.8679
groups_sphingolipids      5      0.3455      0.7455      0.6461      0.7739      0.4182      0.7778
ALL                      20      0.4201      0.7238      0.8370      0.7837      0.4756      0.7248

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5770      0.5768     0.0521  20
max valid BA                0.6002      0.5982     0.0545  20
best valid F1               0.5077      0.5371     0.1057  20
test BA                     0.5720      0.5722     0.0796  20
test AUC                    0.5459      0.5724     0.1313  20
test AUC in-protein         0.5467      0.5534     0.1254  20
  (proteins averaged)       7.9000      8.5000     3.5968  20
test AUC in-protein (pairs)      0.5543      0.5782     0.1506  20
  (proteins contributing)     11.7000     14.0000     5.3024  20
test F1                     0.3961      0.4974     0.2194  20
test sensitivity            0.4201      0.4767     0.2811  20
test specificity            0.7238      0.7413     0.2057  20
test precision              0.4556      0.4857     0.1620  19
test loss                   1.0531      0.9943     0.4017  20
FPR (FP/(FP+TN))            0.2762      0.2587     0.2057  20
FNR (FN/(FN+TP))            0.5799      0.5233     0.2811  20

=== abs(sensitivity-specificity) gap: mean=0.4363 median=0.3908 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5668      0.5726     0.0125  5
  max valid BA                0.5849      0.5897     0.0180  5
  best valid F1               0.5434      0.5517     0.0259  5
  test BA                     0.5912      0.5747     0.0345  5
  test AUC                    0.5899      0.5882     0.0214  5
  test AUC in-protein         0.5368      0.5383     0.0289  5
    (proteins averaged)      12.2000     12.0000     0.4472  5
  test AUC in-protein (pairs)      0.5733      0.5638     0.0551  5
    (proteins contributing)     16.4000     17.0000     1.5166  5
  test F1                     0.5253      0.5152     0.0347  5
  test sensitivity            0.5957      0.5699     0.0732  5
  test specificity            0.5868      0.6225     0.0989  5
  test precision              0.4741      0.4623     0.0428  5
  test loss                   1.1826      1.1294     0.2819  5
  FPR (FP/(FP+TN))            0.4132      0.3775     0.0989  5
  FNR (FN/(FN+TP))            0.4043      0.4301     0.0732  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5735      0.5789     0.0544  5
  max valid BA                0.6140      0.6488     0.0513  5
  best valid F1               0.5491      0.5600     0.0623  5
  test BA                     0.5947      0.6267     0.1028  5
  test AUC                    0.6204      0.6797     0.1329  5
  test AUC in-protein         0.6610      0.6804     0.1015  5
    (proteins averaged)       9.8000     10.0000     0.4472  5
  test AUC in-protein (pairs)      0.6437      0.6333     0.1280  5
    (proteins contributing)     14.8000     15.0000     0.4472  5
  test F1                     0.4580      0.5591     0.2211  5
  test sensitivity            0.4685      0.4685     0.2817  5
  test specificity            0.7210      0.6228     0.1583  5
  test precision              0.5087      0.5175     0.1374  5
  test loss                   0.9035      0.9441     0.2632  5
  FPR (FP/(FP+TN))            0.2790      0.3772     0.1583  5
  FNR (FN/(FN+TP))            0.5315      0.5315     0.2817  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5725      0.5554     0.0740  5
  max valid BA                0.6039      0.5821     0.0825  5
  best valid F1               0.4218      0.3333     0.1627  5
  test BA                     0.5565      0.5147     0.0912  5
  test AUC                    0.4436      0.3933     0.1910  5
  test AUC in-protein         0.4368      0.3733     0.1677  5
    (proteins averaged)       6.6000      7.0000     1.1402  5
  test AUC in-protein (pairs)      0.4222      0.3458     0.2297  5
    (proteins contributing)     12.2000     13.0000     2.1679  5
  test F1                     0.2830      0.2553     0.2486  5
  test sensitivity            0.2710      0.1935     0.2962  5
  test specificity            0.8421      0.8246     0.1209  5
  test precision              0.3845      0.5000     0.2243  5
  test loss                   1.1787      0.9386     0.6791  5
  FPR (FP/(FP+TN))            0.1579      0.1754     0.1209  5
  FNR (FN/(FN+TP))            0.7290      0.8065     0.2962  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5951      0.5993     0.0610  5
  max valid BA                0.5980      0.6103     0.0614  5
  best valid F1               0.5166      0.4898     0.0950  5
  test BA                     0.5455      0.5212     0.0880  5
  test AUC                    0.5299      0.5174     0.0669  5
  test AUC in-protein         0.5522      0.5627     0.0616  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5782      0.5753     0.0504  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.3183      0.3922     0.2600  5
  test sensitivity            0.3455      0.3030     0.3557  5
  test specificity            0.7455      0.8545     0.3315  5
  test precision              0.4549      0.4711     0.2216  4
  test loss                   0.9477      0.8856     0.2719  5
  FPR (FP/(FP+TN))            0.2545      0.1455     0.3315  5
  FNR (FN/(FN+TP))            0.6545      0.6970     0.3557  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.560      11.6              0.530         0.456     5.4               0.501          0.587              0.501         0.554
choline                     0.687         0.646    0.469       9.4              0.696         0.542     1.8               0.565          0.332              0.622         0.510
phosphorus_free             0.396         0.499    0.585       1.2              0.739         0.595     5.4               0.514          0.715              0.484         0.543
sphingolipids               0.599         0.543    0.468       1.6              0.496         0.457     3.2               0.537          0.563              0.490         0.484

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.520               0.530                  0.084                     0.061

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.513               0.518                  0.113                     0.068

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.549               0.572                  0.140                     0.160

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.523               0.523                  0.104                     0.032

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.516  0.461      0.501     0.433
10     0.516  0.453      0.501     0.437
49     0.516  0.507      0.501     0.494
51     0.516  0.510      0.501     0.499
120    0.516  0.520      0.501     0.513

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.645      0.017          0.708              0.727           0.019
10        0.628         0.670      0.043          0.708              0.725           0.018
49        0.628         0.639      0.012          0.708              0.717           0.009
51        0.628         0.634      0.006          0.708              0.719           0.011
120       0.628         0.650      0.022          0.708              0.719           0.011

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.585  0.560      0.566     0.456     0.585         0.602      0.017          0.657              0.667           0.011
choline          0.671  0.469      0.671     0.542     0.671         0.683      0.012          0.767              0.767           0.000
phosphorus_free  0.289  0.585      0.289     0.595     0.711         0.728      0.016          0.772              0.784           0.012
sphingolipids    0.521  0.468      0.480     0.457     0.544         0.585      0.041          0.635              0.657           0.022

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.516               0.553                  0.041                     0.164
net               0.520               0.530                  0.084                     0.061
fit_chem          0.628               0.637                  0.034                     0.077
fit_chem_net      0.650               0.648                  0.028                     0.067
increment         0.022               0.009                  0.025                     0.013

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.501               0.527                  0.043                     0.162
net_prot               0.513               0.518                  0.113                     0.068
fit_chem_prot          0.708               0.701                  0.042                     0.072
fit_chem_net_prot      0.719               0.734                  0.048                     0.066
increment_prot         0.011               0.004                  0.015                     0.009
```
