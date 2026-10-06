# descriptors_no_extent_coarse_add_lipprop_hid4

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_add_lipprop_hid4'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6448      0.4361      0.6040      0.4758      0.6955      0.4710
groups_GLTP            5      0.4720      0.4720      0.7086      0.3676      0.5385      0.5462
groups_IP_trans        5      0.6261      0.5064      0.6986      0.3518      0.6583      0.5021
groups_LBP_BPI_CETP    5      0.8087      0.6000      0.6381      0.4175      0.8250      0.5957
groups_START           5      0.4892      0.4921      0.5317      0.4918      0.5219      0.5348
groups_lipocalin       5      0.7056      0.3778      0.6661      0.3731      0.7389      0.4056
groups_scp2            5      0.6941      0.4529      0.4757      0.5822      0.6471      0.5118
ALL                   35      0.6344      0.4768      0.6175      0.4371      0.6607      0.5096

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5852      0.5643     0.0813  35
max valid BA                0.5999      0.5769     0.0845  35
best valid F1               0.5721      0.5854     0.1066  35
test BA                     0.5556      0.5208     0.0954  35
test F1                     0.4794      0.5152     0.1721  35
test sensitivity            0.6344      0.7059     0.3121  35
test specificity            0.4768      0.4894     0.3145  35
test precision              0.4674      0.4375     0.1310  33
test loss                   0.7099      0.6926     0.0892  35
FPR (FP/(FP+TN))            0.5232      0.5106     0.3145  35
FNR (FN/(FN+TP))            0.3656      0.2941     0.3121  35

=== abs(sensitivity-specificity) gap: mean=0.4941 median=0.4348 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5832      0.5810     0.0373  5
  max valid BA                0.6037      0.6091     0.0339  5
  best valid F1               0.6736      0.7119     0.0572  5
  test BA                     0.5404      0.5289     0.0431  5
  test F1                     0.5898      0.5763     0.0661  5
  test sensitivity            0.6448      0.5672     0.1795  5
  test specificity            0.4361      0.4426     0.2133  5
  test precision              0.5647      0.5435     0.0574  5
  test loss                   0.6873      0.6911     0.0085  5
  FPR (FP/(FP+TN))            0.5639      0.5574     0.2133  5
  FNR (FN/(FN+TP))            0.3552      0.4328     0.1795  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5423      0.5385     0.0285  5
  max valid BA                0.5577      0.5769     0.0272  5
  best valid F1               0.6000      0.6667     0.0926  5
  test BA                     0.4720      0.4800     0.0335  5
  test F1                     0.4438      0.4091     0.1281  5
  test sensitivity            0.4720      0.3600     0.2972  5
  test specificity            0.4720      0.6000     0.2719  5
  test precision              0.4641      0.4737     0.0400  5
  test loss                   0.8038      0.7020     0.2264  5
  FPR (FP/(FP+TN))            0.5280      0.4000     0.2719  5
  FNR (FN/(FN+TP))            0.5280      0.6400     0.2972  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5802      0.5891     0.0579  5
  max valid BA                0.5924      0.5891     0.0644  5
  best valid F1               0.5231      0.5070     0.0270  5
  test BA                     0.5662      0.5698     0.0527  5
  test F1                     0.4647      0.4643     0.0512  5
  test sensitivity            0.6261      0.5652     0.2708  5
  test specificity            0.5064      0.4894     0.3481  5
  test precision              0.4691      0.3939     0.2195  5
  test loss                   0.6989      0.6922     0.0217  5
  FPR (FP/(FP+TN))            0.4936      0.5106     0.3481  5
  FNR (FN/(FN+TP))            0.3739      0.4348     0.2708  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7104      0.7575     0.1207  5
  max valid BA                0.7254      0.7682     0.1152  5
  best valid F1               0.6654      0.6909     0.0864  5
  test BA                     0.7043      0.7317     0.1249  5
  test F1                     0.6301      0.6429     0.0956  5
  test sensitivity            0.8087      0.7826     0.1885  5
  test specificity            0.6000      0.7021     0.3458  5
  test precision              0.5542      0.5625     0.1411  5
  test loss                   0.6701      0.6810     0.0319  5
  FPR (FP/(FP+TN))            0.4000      0.2979     0.3458  5
  FNR (FN/(FN+TP))            0.1913      0.2174     0.1885  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5284      0.5262     0.0236  5
  max valid BA                0.5328      0.5262     0.0297  5
  best valid F1               0.5240      0.5899     0.1036  5
  test BA                     0.4907      0.5000     0.0522  5
  test F1                     0.3556      0.3841     0.2485  5
  test sensitivity            0.4892      0.4462     0.4351  5
  test specificity            0.4921      0.3596     0.4549  5
  test precision              0.4574      0.4248     0.1304  4
  test loss                   0.7092      0.7165     0.0164  5
  FPR (FP/(FP+TN))            0.5079      0.6404     0.4549  5
  FNR (FN/(FN+TP))            0.5108      0.5538     0.4351  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5722      0.5694     0.0664  5
  max valid BA                0.5903      0.5833     0.0764  5
  best valid F1               0.4878      0.5344     0.1401  5
  test BA                     0.5417      0.5208     0.0631  5
  test F1                     0.4388      0.5000     0.1664  5
  test sensitivity            0.7056      0.8333     0.3735  5
  test specificity            0.3778      0.3611     0.3070  5
  test precision              0.3447      0.3500     0.0596  5
  test loss                   0.7030      0.6950     0.0196  5
  FPR (FP/(FP+TN))            0.6222      0.6389     0.3070  5
  FNR (FN/(FN+TP))            0.2944      0.1667     0.3735  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5794      0.6029     0.0694  5
  max valid BA                0.5971      0.6324     0.0836  5
  best valid F1               0.5304      0.5455     0.0673  5
  test BA                     0.5735      0.5294     0.0812  5
  test F1                     0.4333      0.5152     0.2454  5
  test sensitivity            0.6941      0.8824     0.4020  5
  test specificity            0.4529      0.4412     0.3793  5
  test precision              0.4023      0.3941     0.0692  4
  test loss                   0.6970      0.6935     0.0099  5
  FPR (FP/(FP+TN))            0.5471      0.5588     0.3793  5
  FNR (FN/(FN+TP))            0.3059      0.1176     0.4020  5
```

## AUC vs chemistry null model, in-sample increment

### features = tanimoto (full molecular structure)

```
########## split = valid ##########

--- null model (null_model.py), features = tanimoto (tanimoto), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  net_AUC_lipid
fam                                                                                                                    
CRAL-TRIO                0.802         0.453    0.597       4.0              0.475         0.555     0.0            NaN
GLTP                     0.615         0.536    0.545       2.0              0.499         0.512     0.0            NaN
IP_trans                 0.809         0.686    0.533       3.0              0.703         0.544     0.0            NaN
LBP_BPI_CETP             0.809         0.705    0.653       2.0              0.716         0.654     0.0            NaN
START                    0.789         0.505    0.493       3.0              0.509         0.501     0.0            NaN
lipocalin                0.832         0.473    0.533       5.0              0.434         0.541     0.0            NaN
scp2                     0.834         0.629    0.616       2.8              0.529         0.591     0.0            NaN

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
null_AUC_k15      0.570          0.673       0.492
net_AUC           0.567          0.601       0.542

=== the same rows ranked INSIDE each protein ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
null_AUC_prot_k15      0.552          0.649       0.479
net_AUC_prot           0.557          0.596       0.527

=== the same rows ranked INSIDE each lipid ===
0 lipid-blocks across 35 family-seed splits carry a usable ranking (median 0 lipids per split)
               all seven  working three  other four
net_AUC_lipid        NaN            NaN         NaN

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.525      0.552     0.530
10     0.57  0.509      0.552     0.523
49     0.57  0.550      0.552     0.543
51     0.57  0.548      0.552     0.542
120    0.57  0.567      0.552     0.557

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.658      0.052          0.657              0.693           0.036
10        0.607         0.667      0.060          0.657              0.701           0.044
49        0.607         0.669      0.062          0.657              0.699           0.042
51        0.607         0.665      0.059          0.657              0.698           0.041
120       0.607         0.658      0.051          0.657              0.695           0.038

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.597      0.475     0.555      0.053           0.036
GLTP          0.536  0.545      0.499     0.512      0.030           0.007
IP_trans      0.686  0.533      0.703     0.544      0.024           0.027
LBP_BPI_CETP  0.705  0.653      0.716     0.654      0.099           0.077
START         0.505  0.493      0.509     0.501      0.028           0.014
lipocalin     0.473  0.533      0.434     0.541      0.082           0.091
scp2          0.629  0.616      0.529     0.591      0.039           0.015

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.567          0.601       0.542      0.616
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.557          0.596       0.527      0.591
increment           0.051          0.054       0.048      0.039
increment_prot      0.038          0.040       0.037      0.015

wrote : /tmp/tmp.tlToA6mcMq
```

### features = lipid4 (chain/unsaturation/hbond/heavy only)

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  net_AUC_lipid
fam                                                                                                                    
CRAL-TRIO                0.630         0.483    0.597       4.0              0.365         0.555     0.0            NaN
GLTP                     0.605         0.521    0.545       2.0              0.511         0.512     0.0            NaN
IP_trans                 0.722         0.681    0.533       3.0              0.677         0.544     0.0            NaN
LBP_BPI_CETP             0.719         0.798    0.653       2.0              0.798         0.654     0.0            NaN
START                    0.576         0.508    0.493       3.0              0.475         0.501     0.0            NaN
lipocalin                0.565         0.334    0.533       5.0              0.252         0.541     0.0            NaN
scp2                     0.651         0.488    0.616       2.8              0.592         0.591     0.0            NaN

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
null_AUC_k15      0.545          0.656       0.461
net_AUC           0.567          0.601       0.542

=== the same rows ranked INSIDE each protein ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
null_AUC_prot_k15      0.524          0.689       0.401
net_AUC_prot           0.557          0.596       0.527

=== the same rows ranked INSIDE each lipid ===
0 lipid-blocks across 35 family-seed splits carry a usable ranking (median 0 lipids per split)
               all seven  working three  other four
net_AUC_lipid        NaN            NaN         NaN

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.525      0.524     0.530
10     0.545  0.509      0.524     0.523
49     0.545  0.550      0.524     0.543
51     0.545  0.548      0.524     0.542
120    0.545  0.567      0.524     0.557

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.619         0.653      0.034          0.655              0.686           0.031
10        0.619         0.669      0.050          0.655              0.695           0.040
49        0.619         0.667      0.048          0.655              0.696           0.041
51        0.619         0.667      0.048          0.655              0.696           0.041
120       0.619         0.663      0.044          0.655              0.694           0.040

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.483  0.597      0.365     0.555      0.071           0.056
GLTP          0.521  0.545      0.511     0.512      0.050           0.032
IP_trans      0.681  0.533      0.677     0.544      0.022           0.032
LBP_BPI_CETP  0.798  0.653      0.798     0.654      0.004           0.009
START         0.508  0.493      0.475     0.501      0.032           0.014
lipocalin     0.334  0.533      0.252     0.541      0.057           0.086
scp2          0.488  0.616      0.592     0.591      0.072           0.047

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.545          0.656       0.461      0.488
net                 0.567          0.601       0.542      0.616
chem_prot           0.524          0.689       0.401      0.592
net_prot            0.557          0.596       0.527      0.591
increment           0.044          0.033       0.052      0.072
increment_prot      0.040          0.029       0.047      0.047
```
