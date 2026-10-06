# descriptors_no_extent_coarse_add_lipprop_hid2

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_add_lipprop_hid2'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.7164      0.3311      0.7149      0.2879      0.7134      0.3323
groups_GLTP            5      0.3840      0.5520      0.7944      0.2081      0.4538      0.6308
groups_IP_trans        5      0.4348      0.6255      0.4182      0.5741      0.4500      0.6681
groups_LBP_BPI_CETP    5      0.6870      0.5021      0.7000      0.3131      0.7000      0.4511
groups_START           5      0.5969      0.4315      0.7474      0.2621      0.6062      0.4292
groups_lipocalin       5      0.7556      0.3056      0.7144      0.3141      0.7333      0.2944
groups_scp2            5      0.3765      0.6118      0.5006      0.5329      0.3882      0.6235
ALL                   35      0.5644      0.4799      0.6557      0.3560      0.5779      0.4899

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5339      0.5192     0.0532  35
max valid BA                0.5537      0.5204     0.0739  35
best valid F1               0.5602      0.5614     0.1194  35
test BA                     0.5222      0.5000     0.0754  35
test F1                     0.3960      0.4946     0.2381  35
test sensitivity            0.5644      0.6087     0.4066  35
test specificity            0.4799      0.5574     0.4073  35
test precision              0.4164      0.4310     0.1911  32
test loss                   0.8462      0.6932     0.5248  35
FPR (FP/(FP+TN))            0.5201      0.4426     0.4073  35
FNR (FN/(FN+TP))            0.4356      0.3913     0.4066  35

=== abs(sensitivity-specificity) gap: mean=0.7199 median=0.8299 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5228      0.5057     0.0367  5
  max valid BA                0.5228      0.5057     0.0367  5
  best valid F1               0.6753      0.6837     0.0126  5
  test BA                     0.5238      0.5195     0.0316  5
  test F1                     0.5635      0.6667     0.2178  5
  test sensitivity            0.7164      0.8806     0.3796  5
  test specificity            0.3311      0.1639     0.4069  5
  test precision              0.5633      0.5364     0.0509  5
  test loss                   0.7198      0.6930     0.0498  5
  FPR (FP/(FP+TN))            0.6689      0.8361     0.4069  5
  FNR (FN/(FN+TP))            0.2836      0.1194     0.3796  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5423      0.5577     0.0316  5
  max valid BA                0.5731      0.5577     0.0916  5
  best valid F1               0.6851      0.6667     0.0411  5
  test BA                     0.4680      0.4800     0.0268  5
  test F1                     0.3384      0.4091     0.2568  5
  test sensitivity            0.3840      0.3600     0.3874  5
  test specificity            0.5520      0.6000     0.3638  5
  test precision              0.3494      0.4400     0.2053  5
  test loss                   0.7213      0.6932     0.0556  5
  FPR (FP/(FP+TN))            0.4480      0.4000     0.3638  5
  FNR (FN/(FN+TP))            0.6160      0.6400     0.3874  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5590      0.5301     0.0835  5
  max valid BA                0.5960      0.5386     0.1055  5
  best valid F1               0.4798      0.5053     0.1974  5
  test BA                     0.5302      0.5000     0.0908  5
  test F1                     0.3370      0.4783     0.2220  5
  test sensitivity            0.4348      0.4783     0.3913  5
  test specificity            0.6255      0.7447     0.3569  5
  test precision              0.3330      0.3286     0.1613  5
  test loss                   0.7501      0.6899     0.1260  5
  FPR (FP/(FP+TN))            0.3745      0.2553     0.3569  5
  FNR (FN/(FN+TP))            0.5652      0.5217     0.3913  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5755      0.5514     0.0869  5
  max valid BA                0.5784      0.5514     0.0926  5
  best valid F1               0.4824      0.5053     0.1379  5
  test BA                     0.5945      0.5014     0.1452  5
  test F1                     0.4927      0.4946     0.1963  5
  test sensitivity            0.6870      0.8261     0.3415  5
  test specificity            0.5021      0.6596     0.4206  5
  test precision              0.4458      0.3333     0.1740  5
  test loss                   0.8632      0.6904     0.2647  5
  FPR (FP/(FP+TN))            0.4979      0.3404     0.4206  5
  FNR (FN/(FN+TP))            0.3130      0.1739     0.3415  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5177      0.5000     0.0243  5
  max valid BA                0.5177      0.5000     0.0243  5
  best valid F1               0.5842      0.5899     0.0127  5
  test BA                     0.5142      0.5000     0.0223  5
  test F1                     0.4133      0.5698     0.2604  5
  test sensitivity            0.5969      0.7538     0.4582  5
  test specificity            0.4315      0.3483     0.4596  5
  test precision              0.4427      0.4400     0.0242  4
  test loss                   0.7502      0.7291     0.0825  5
  FPR (FP/(FP+TN))            0.5685      0.6517     0.4596  5
  FNR (FN/(FN+TP))            0.4031      0.2462     0.4582  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5139      0.5000     0.0311  5
  max valid BA                0.5528      0.5000     0.0729  5
  best valid F1               0.5086      0.5000     0.0193  5
  test BA                     0.5306      0.5000     0.0683  5
  test F1                     0.4143      0.5000     0.2336  5
  test sensitivity            0.7556      1.0000     0.4332  5
  test specificity            0.3056      0.0000     0.4505  5
  test precision              0.3629      0.3333     0.0591  4
  test loss                   1.3710      0.7842     1.3432  5
  FPR (FP/(FP+TN))            0.6944      1.0000     0.4505  5
  FNR (FN/(FN+TP))            0.2444      0.0000     0.4332  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5059      0.5000     0.0246  5
  max valid BA                0.5353      0.5000     0.0663  5
  best valid F1               0.5058      0.5000     0.0361  5
  test BA                     0.4941      0.5000     0.0267  5
  test F1                     0.2125      0.1111     0.2452  5
  test sensitivity            0.3765      0.0588     0.4932  5
  test specificity            0.6118      0.9706     0.5193  5
  test precision              0.4111      0.3222     0.4211  4
  test loss                   0.7476      0.6943     0.1374  5
  FPR (FP/(FP+TN))            0.3882      0.0294     0.5193  5
  FNR (FN/(FN+TP))            0.6235      0.9412     0.4932  5
```

## AUC vs chemistry null model, in-sample increment

### features = tanimoto (full molecular structure)

```
########## split = valid ##########

--- null model (null_model.py), features = tanimoto (tanimoto), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  null_AUC_lipid_k15  lipids  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot
fam                                                                                                                         
CRAL-TRIO                0.802         0.453                 NaN     0.0    0.499       4.0              0.475         0.519
GLTP                     0.615         0.536                 NaN     0.0    0.546       2.0              0.499         0.512
IP_trans                 0.809         0.686                 NaN     0.0    0.569       3.0              0.703         0.569
LBP_BPI_CETP             0.809         0.705                 NaN     0.0    0.684       2.0              0.716         0.685
START                    0.789         0.505                 NaN     0.0    0.486       3.0              0.509         0.498
lipocalin                0.832         0.473                 NaN     0.0    0.520       5.0              0.434         0.546
scp2                     0.834         0.629                 NaN     0.0    0.586       2.8              0.529         0.587

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
null_AUC_k15      0.570          0.673       0.492
net_AUC           0.556          0.613       0.513

=== the same rows ranked INSIDE each protein (interaction term only) ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
null_AUC_prot_k15      0.552          0.649       0.479
net_AUC_prot           0.559          0.614       0.518

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.489      0.552     0.473
10     0.57  0.479      0.552     0.466
49     0.57  0.514      0.552     0.516
51     0.57  0.516      0.552     0.515
120    0.57  0.556      0.552     0.559

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.639      0.032          0.657              0.687           0.030
10        0.607         0.644      0.037          0.657              0.695           0.039
49        0.607         0.647      0.040          0.657              0.693           0.037
51        0.607         0.646      0.039          0.657              0.696           0.039
120       0.607         0.645      0.039          0.657              0.698           0.042

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.499      0.475     0.519      0.042           0.037
GLTP          0.536  0.546      0.499     0.512      0.007           0.029
IP_trans      0.686  0.569      0.703     0.569      0.009           0.003
LBP_BPI_CETP  0.705  0.684      0.716     0.685      0.064           0.051
START         0.505  0.486      0.509     0.498      0.027           0.035
lipocalin     0.473  0.520      0.434     0.546      0.088           0.108
scp2          0.629  0.586      0.529     0.587      0.032           0.030

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.556          0.613       0.513      0.586
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.559          0.614       0.518      0.587
increment           0.039          0.035       0.041      0.032
increment_prot      0.042          0.028       0.052      0.030

wrote : /tmp/tmp.ZttDGzFxaa
```

### features = lipid4 (chain/unsaturation/hbond/heavy only)

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  net_AUC_lipid
fam                                                                                                                    
CRAL-TRIO                0.630         0.483    0.499       4.0              0.365         0.519     0.0            NaN
GLTP                     0.605         0.521    0.546       2.0              0.511         0.512     0.0            NaN
IP_trans                 0.722         0.681    0.569       3.0              0.677         0.569     0.0            NaN
LBP_BPI_CETP             0.719         0.798    0.684       2.0              0.798         0.685     0.0            NaN
START                    0.576         0.508    0.486       3.0              0.475         0.498     0.0            NaN
lipocalin                0.565         0.334    0.520       5.0              0.252         0.546     0.0            NaN
scp2                     0.651         0.488    0.586       2.8              0.592         0.587     0.0            NaN

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
null_AUC_k15      0.545          0.656       0.461
net_AUC           0.556          0.613       0.513

=== the same rows ranked INSIDE each protein ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
null_AUC_prot_k15      0.524          0.689       0.401
net_AUC_prot           0.559          0.614       0.518

=== the same rows ranked INSIDE each lipid ===
0 lipid-blocks across 35 family-seed splits carry a usable ranking (median 0 lipids per split)
               all seven  working three  other four
net_AUC_lipid        NaN            NaN         NaN

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.489      0.524     0.473
10     0.545  0.479      0.524     0.466
49     0.545  0.514      0.524     0.516
51     0.545  0.516      0.524     0.515
120    0.545  0.556      0.524     0.559

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.619         0.647      0.028          0.655              0.687           0.032
10        0.619         0.654      0.035          0.655              0.696           0.041
49        0.619         0.655      0.036          0.655              0.696           0.041
51        0.619         0.654      0.035          0.655              0.697           0.042
120       0.619         0.652      0.033          0.655              0.698           0.043

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.483  0.499      0.365     0.519      0.059           0.059
GLTP          0.521  0.546      0.511     0.512      0.017           0.038
IP_trans      0.681  0.569      0.677     0.569      0.019           0.022
LBP_BPI_CETP  0.798  0.684      0.798     0.685      0.021           0.021
START         0.508  0.486      0.475     0.498      0.043           0.040
lipocalin     0.334  0.520      0.252     0.546      0.048           0.099
scp2          0.488  0.586      0.592     0.587      0.026           0.019

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.545          0.656       0.461      0.488
net                 0.556          0.613       0.513      0.586
chem_prot           0.524          0.689       0.401      0.592
net_prot            0.559          0.614       0.518      0.587
increment           0.033          0.022       0.042      0.026
increment_prot      0.043          0.021       0.059      0.019
```
