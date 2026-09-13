# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protbind6

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protbind6'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.5914      0.5219      0.9259      0.8125      0.7011      0.4503
groups_choline            5      0.3586      0.8120      0.8560      0.7251      0.4107      0.8357
groups_phosphorus_free    5      0.1226      0.9298      0.9086      0.7386      0.4533      0.7929
groups_sphingolipids      5      0.2970      0.6655      0.7268      0.6923      0.4364      0.7333
ALL                      20      0.3424      0.7323      0.8543      0.7421      0.5004      0.7031

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5651      0.5543     0.0485  20
max valid BA                0.6017      0.5991     0.0588  20
best valid F1               0.5058      0.5389     0.1176  20
test BA                     0.5373      0.5351     0.0787  20
test AUC                    0.5459      0.5614     0.1239  20
test AUC in-protein         0.5434      0.5345     0.1485  20
  (proteins averaged)       7.9000      8.5000     3.5968  20
test AUC in-protein (pairs)      0.5570      0.5529     0.1521  20
  (proteins contributing)     11.7000     14.0000     5.3024  20
test F1                     0.3453      0.4123     0.1887  20
test sensitivity            0.3424      0.3854     0.2334  20
test specificity            0.7323      0.7557     0.2114  20
test precision              0.4502      0.4694     0.1556  19
test loss                   0.9972      0.8677     0.4192  20
FPR (FP/(FP+TN))            0.2677      0.2443     0.2114  20
FNR (FN/(FN+TP))            0.6576      0.6146     0.2334  20

=== abs(sensitivity-specificity) gap: mean=0.4798 median=0.4587 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5333      0.5383     0.0153  5
  max valid BA                0.5757      0.5882     0.0325  5
  best valid F1               0.5512      0.5506     0.0151  5
  test BA                     0.5566      0.5751     0.0309  5
  test AUC                    0.5650      0.5612     0.0284  5
  test AUC in-protein         0.5261      0.5034     0.0733  5
    (proteins averaged)      12.2000     12.0000     0.4472  5
  test AUC in-protein (pairs)      0.5633      0.5711     0.0401  5
    (proteins contributing)     16.4000     17.0000     1.5166  5
  test F1                     0.4971      0.4851     0.0260  5
  test sensitivity            0.5914      0.6129     0.1233  5
  test specificity            0.5219      0.5298     0.1728  5
  test precision              0.4415      0.4538     0.0417  5
  test loss                   1.1499      1.2815     0.2620  5
  FPR (FP/(FP+TN))            0.4781      0.4702     0.1728  5
  FNR (FN/(FN+TP))            0.4086      0.3871     0.1233  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6089      0.6012     0.0332  5
  max valid BA                0.6232      0.6057     0.0300  5
  best valid F1               0.5527      0.5714     0.0573  5
  test BA                     0.5853      0.5859     0.0660  5
  test AUC                    0.6081      0.6571     0.1329  5
  test AUC in-protein         0.6614      0.6857     0.0568  5
    (proteins averaged)       9.8000     10.0000     0.4472  5
  test AUC in-protein (pairs)      0.6152      0.6667     0.0951  5
    (proteins contributing)     14.8000     15.0000     0.4472  5
  test F1                     0.4086      0.4333     0.1762  5
  test sensitivity            0.3586      0.3514     0.2148  5
  test specificity            0.8120      0.8204     0.0851  5
  test precision              0.5337      0.5652     0.0761  5
  test loss                   0.9639      0.6772     0.5759  5
  FPR (FP/(FP+TN))            0.1880      0.1796     0.0851  5
  FNR (FN/(FN+TP))            0.6414      0.6486     0.2148  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5511      0.5321     0.0675  5
  max valid BA                0.6231      0.6232     0.1006  5
  best valid F1               0.4572      0.5098     0.2069  5
  test BA                     0.5262      0.5000     0.0604  5
  test AUC                    0.5808      0.6169     0.1410  5
  test AUC in-protein         0.6151      0.6956     0.1565  5
    (proteins averaged)       6.6000      7.0000     1.1402  5
  test AUC in-protein (pairs)      0.6363      0.7214     0.2215  5
    (proteins contributing)     12.2000     13.0000     2.1679  5
  test F1                     0.1628      0.1176     0.1921  5
  test sensitivity            0.1226      0.0645     0.1698  5
  test specificity            0.9298      0.9298     0.0645  5
  test precision              0.4477      0.4621     0.2182  4
  test loss                   0.7746      0.7543     0.1180  5
  FPR (FP/(FP+TN))            0.0702      0.0702     0.0645  5
  FNR (FN/(FN+TP))            0.8774      0.9355     0.1698  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5672      0.5589     0.0369  5
  max valid BA                0.5848      0.5749     0.0450  5
  best valid F1               0.4623      0.4179     0.0932  5
  test BA                     0.4812      0.4667     0.1143  5
  test AUC                    0.4299      0.4121     0.1047  5
  test AUC in-protein         0.3710      0.4122     0.1016  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4134      0.4114     0.1108  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.3127      0.3256     0.1540  5
  test sensitivity            0.2970      0.2727     0.1665  5
  test specificity            0.6655      0.7091     0.2309  5
  test precision              0.3775      0.3200     0.2243  5
  test loss                   1.1002      1.0195     0.5611  5
  FPR (FP/(FP+TN))            0.3345      0.2909     0.2309  5
  FNR (FN/(FN+TP))            0.7030      0.7273     0.1665  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.533      11.6              0.530         0.446     5.4               0.501          0.555              0.501         0.524
choline                     0.687         0.646    0.491       9.4              0.696         0.567     1.8               0.565          0.437              0.622         0.548
phosphorus_free             0.396         0.499    0.585       1.2              0.739         0.651     5.4               0.514          0.657              0.484         0.620
sphingolipids               0.599         0.543    0.476       1.6              0.496         0.399     3.2               0.537          0.548              0.490         0.380

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.521               0.525                  0.063                     0.049

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.516               0.508                  0.113                     0.115

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.549               0.566                  0.138                     0.090

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.518               0.538                  0.082                     0.101

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.516  0.449      0.501     0.425
10     0.516  0.451      0.501     0.440
49     0.516  0.516      0.501     0.510
51     0.516  0.518      0.501     0.513
120    0.516  0.521      0.501     0.516

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.642      0.014          0.708              0.721           0.013
10        0.628         0.658      0.030          0.708              0.724           0.017
49        0.628         0.667      0.039          0.708              0.739           0.031
51        0.628         0.664      0.036          0.708              0.735           0.028
120       0.628         0.656      0.028          0.708              0.730           0.023

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.585  0.533      0.566     0.446     0.585         0.586      0.001          0.657              0.662           0.006
choline          0.671  0.491      0.671     0.567     0.671         0.675      0.004          0.767              0.774           0.007
phosphorus_free  0.289  0.585      0.289     0.651     0.711         0.743      0.032          0.772              0.789           0.017
sphingolipids    0.521  0.476      0.480     0.399     0.544         0.622      0.078          0.635              0.695           0.060

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.516               0.553                  0.041                     0.164
net               0.521               0.525                  0.063                     0.049
fit_chem          0.628               0.637                  0.034                     0.077
fit_chem_net      0.656               0.655                  0.046                     0.068
increment         0.028               0.005                  0.020                     0.036

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.501               0.527                  0.043                     0.162
net_prot               0.516               0.508                  0.113                     0.115
fit_chem_prot          0.708               0.701                  0.042                     0.072
fit_chem_net_prot      0.730               0.735                  0.056                     0.061
increment_prot         0.023               0.005                  0.028                     0.026
```
