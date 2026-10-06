# descriptors_no_extent_coarse_add_lipprop_lr0005

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_add_lipprop_lr0005'
rows: 34

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6448      0.5148      0.6446      0.4231      0.6687      0.5000
groups_GLTP            5      0.4480      0.4960      0.5825      0.5256      0.5077      0.6000
groups_IP_trans        5      0.6087      0.5787      0.5190      0.5474      0.6333      0.6298
groups_LBP_BPI_CETP    5      0.7652      0.7702      0.5397      0.5170      0.8083      0.7617
groups_START           4      0.3385      0.6404      0.5085      0.5213      0.3672      0.6854
groups_lipocalin       5      0.5722      0.6972      0.5554      0.5511      0.5444      0.7194
groups_scp2            5      0.6706      0.5059      0.6090      0.5069      0.6824      0.6529
ALL                   34      0.5853      0.5993      0.5672      0.5129      0.6086      0.6489

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6287      0.6167     0.0924  34
max valid BA                0.6534      0.6435     0.0953  34
best valid F1               0.6119      0.6324     0.0970  34
test BA                     0.5923      0.5831     0.1050  34
test F1                     0.5122      0.5242     0.1483  34
test sensitivity            0.5853      0.6043     0.2156  34
test specificity            0.5993      0.6056     0.1795  34
test precision              0.4890      0.4794     0.1428  34
test loss                   0.6862      0.6881     0.0139  34
FPR (FP/(FP+TN))            0.4007      0.3944     0.1795  34
FNR (FN/(FN+TP))            0.4147      0.3957     0.2156  34

=== abs(sensitivity-specificity) gap: mean=0.2592 median=0.2220 n=34 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5843      0.5816     0.0268  5
  max valid BA                0.6150      0.5951     0.0483  5
  best valid F1               0.6838      0.6839     0.0266  5
  test BA                     0.5798      0.5772     0.0205  5
  test F1                     0.6159      0.6056     0.0297  5
  test sensitivity            0.6448      0.6418     0.0904  5
  test specificity            0.5148      0.4754     0.1208  5
  test precision              0.5981      0.5814     0.0359  5
  test loss                   0.6905      0.6903     0.0050  5
  FPR (FP/(FP+TN))            0.4852      0.5246     0.1208  5
  FNR (FN/(FN+TP))            0.3552      0.3582     0.0904  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5538      0.5577     0.0459  5
  max valid BA                0.5731      0.5769     0.0498  5
  best valid F1               0.5877      0.6667     0.1138  5
  test BA                     0.4720      0.4800     0.0335  5
  test F1                     0.4533      0.4490     0.0609  5
  test sensitivity            0.4480      0.4400     0.1145  5
  test specificity            0.4960      0.4800     0.1459  5
  test precision              0.4731      0.4737     0.0285  5
  test loss                   0.6999      0.6994     0.0081  5
  FPR (FP/(FP+TN))            0.5040      0.5200     0.1459  5
  FNR (FN/(FN+TP))            0.5520      0.5600     0.1145  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6316      0.6219     0.0666  5
  max valid BA                0.6566      0.6525     0.0711  5
  best valid F1               0.5775      0.5614     0.0592  5
  test BA                     0.5937      0.5920     0.0472  5
  test F1                     0.4945      0.5000     0.0315  5
  test sensitivity            0.6087      0.6087     0.0972  5
  test specificity            0.5787      0.6596     0.1718  5
  test precision              0.4267      0.4400     0.0564  5
  test loss                   0.6838      0.6868     0.0185  5
  FPR (FP/(FP+TN))            0.4213      0.3404     0.1718  5
  FNR (FN/(FN+TP))            0.3913      0.3913     0.0972  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7850      0.7793     0.0304  5
  max valid BA                0.8060      0.8094     0.0383  5
  best valid F1               0.7358      0.7333     0.0485  5
  test BA                     0.7677      0.7623     0.0722  5
  test F1                     0.6851      0.6818     0.0838  5
  test sensitivity            0.7652      0.6957     0.1175  5
  test specificity            0.7702      0.7447     0.0830  5
  test precision              0.6273      0.6364     0.0929  5
  test loss                   0.6673      0.6640     0.0082  5
  FPR (FP/(FP+TN))            0.2298      0.2553     0.0830  5
  FNR (FN/(FN+TP))            0.2348      0.3043     0.1175  5

groups_START (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5263      0.5259     0.0374  4
  max valid BA                0.5389      0.5259     0.0526  4
  best valid F1               0.4874      0.4942     0.0782  4
  test BA                     0.4895      0.4902     0.0361  4
  test F1                     0.3169      0.3792     0.2200  4
  test sensitivity            0.3385      0.3538     0.2656  4
  test specificity            0.6404      0.6236     0.2708  4
  test precision              0.3149      0.3912     0.2151  4
  test loss                   0.6954      0.6952     0.0091  4
  FPR (FP/(FP+TN))            0.3596      0.3764     0.2708  4
  FNR (FN/(FN+TP))            0.6615      0.6462     0.2656  4

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6319      0.6181     0.0808  5
  max valid BA                0.6556      0.6319     0.0628  5
  best valid F1               0.5660      0.5556     0.0686  5
  test BA                     0.6347      0.6042     0.0868  5
  test F1                     0.4868      0.4545     0.1688  5
  test sensitivity            0.5722      0.5556     0.3146  5
  test specificity            0.6972      0.6111     0.1898  5
  test precision              0.5471      0.5000     0.1693  5
  test loss                   0.6795      0.6852     0.0122  5
  FPR (FP/(FP+TN))            0.3028      0.3889     0.1898  5
  FNR (FN/(FN+TP))            0.4278      0.4444     0.3146  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6676      0.6471     0.0472  5
  max valid BA                0.7059      0.6912     0.0441  5
  best valid F1               0.6205      0.6122     0.0520  5
  test BA                     0.5882      0.6029     0.0615  5
  test F1                     0.4937      0.5283     0.0950  5
  test sensitivity            0.6706      0.8235     0.2185  5
  test specificity            0.5059      0.4706     0.1370  5
  test precision              0.4008      0.4118     0.0530  5
  test loss                   0.6891      0.6887     0.0037  5
  FPR (FP/(FP+TN))            0.4941      0.5294     0.1370  5
  FNR (FN/(FN+TP))            0.3294      0.1765     0.2185  5
```

## AUC vs chemistry null model, in-sample increment

### features = tanimoto (full molecular structure)

```
########## split = valid ##########

--- null model (null_model.py), features = tanimoto (tanimoto), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  net_AUC_lipid
fam                                                                                                                    
CRAL-TRIO                0.802         0.453    0.516       4.0              0.475         0.505     0.0            NaN
GLTP                     0.615         0.536    0.526       2.0              0.499         0.510     0.0            NaN
IP_trans                 0.809         0.686    0.628       3.0              0.703         0.638     0.0            NaN
LBP_BPI_CETP             0.809         0.705    0.811       2.0              0.716         0.808     0.0            NaN
START                    0.789         0.505    0.452       3.0              0.509         0.480     0.0            NaN
lipocalin                0.832         0.473    0.636       5.0              0.434         0.675     0.0            NaN
scp2                     0.834         0.629    0.631       2.8              0.529         0.591     0.0            NaN

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
null_AUC_k15       0.57          0.673       0.492
net_AUC            0.60          0.690       0.532

=== the same rows ranked INSIDE each protein ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
null_AUC_prot_k15      0.552          0.649       0.479
net_AUC_prot           0.601          0.679       0.543

=== the same rows ranked INSIDE each lipid ===
0 lipid-blocks across 35 family-seed splits carry a usable ranking (median 0 lipids per split)
               all seven  working three  other four
net_AUC_lipid        NaN            NaN         NaN

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
       chem    net  chem_prot  net_prot
epoch                                  
1      0.57  0.536      0.552     0.537
10     0.57  0.609      0.552     0.597
49     0.57  0.593      0.552     0.589
51     0.57  0.593      0.552     0.586
120    0.57  0.600      0.552     0.601

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.607         0.657      0.050          0.657              0.694           0.038
10        0.607         0.662      0.055          0.657              0.700           0.043
49        0.607         0.666      0.059          0.657              0.700           0.044
51        0.607         0.666      0.059          0.657              0.697           0.040
120       0.607         0.671      0.065          0.657              0.700           0.044

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.453  0.516      0.475     0.505      0.043           0.033
GLTP          0.536  0.526      0.499     0.510      0.019          -0.004
IP_trans      0.686  0.628      0.703     0.638      0.009           0.008
LBP_BPI_CETP  0.705  0.811      0.716     0.808      0.140           0.105
START         0.505  0.452      0.509     0.480      0.053           0.034
lipocalin     0.473  0.636      0.434     0.675      0.136           0.110
scp2          0.629  0.631      0.529     0.591      0.051           0.019

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.570          0.673       0.492      0.629
net                 0.600          0.690       0.532      0.631
chem_prot           0.552          0.649       0.479      0.529
net_prot            0.601          0.679       0.543      0.591
increment           0.065          0.067       0.063      0.051
increment_prot      0.044          0.044       0.043      0.019

wrote : /tmp/tmp.m3nhFAKSUk
```

### features = lipid4 (chain/unsaturation/hbond/heavy only)

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  net_AUC_lipid
fam                                                                                                                    
CRAL-TRIO                0.630         0.483    0.516       4.0              0.365         0.505     0.0            NaN
GLTP                     0.605         0.521    0.526       2.0              0.511         0.510     0.0            NaN
IP_trans                 0.722         0.681    0.628       3.0              0.677         0.638     0.0            NaN
LBP_BPI_CETP             0.719         0.798    0.811       2.0              0.798         0.808     0.0            NaN
START                    0.576         0.508    0.452       3.0              0.475         0.480     0.0            NaN
lipocalin                0.565         0.334    0.636       5.0              0.252         0.675     0.0            NaN
scp2                     0.651         0.488    0.631       2.8              0.592         0.591     0.0            NaN

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
null_AUC_k15      0.545          0.656       0.461
net_AUC           0.600          0.690       0.532

=== the same rows ranked INSIDE each protein ===
109 protein-blocks across 35 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
null_AUC_prot_k15      0.524          0.689       0.401
net_AUC_prot           0.601          0.679       0.543

=== the same rows ranked INSIDE each lipid ===
0 lipid-blocks across 35 family-seed splits carry a usable ranking (median 0 lipids per split)
               all seven  working three  other four
net_AUC_lipid        NaN            NaN         NaN

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.536      0.524     0.537
10     0.545  0.609      0.524     0.597
49     0.545  0.593      0.524     0.589
51     0.545  0.593      0.524     0.586
120    0.545  0.600      0.524     0.601

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.619         0.671      0.052          0.655              0.698           0.043
10        0.619         0.669      0.050          0.655              0.699           0.044
49        0.619         0.668      0.049          0.655              0.698           0.043
51        0.619         0.664      0.045          0.655              0.696           0.041
120       0.619         0.663      0.044          0.655              0.693           0.038

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.483  0.516      0.365     0.505      0.026           0.027
GLTP          0.521  0.526      0.511     0.510      0.039           0.014
IP_trans      0.681  0.628      0.677     0.638      0.007           0.014
LBP_BPI_CETP  0.798  0.811      0.798     0.808      0.017           0.020
START         0.508  0.452      0.475     0.480      0.056           0.034
lipocalin     0.334  0.636      0.252     0.675      0.083           0.102
scp2          0.488  0.631      0.592     0.591      0.078           0.055

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.545          0.656       0.461      0.488
net                 0.600          0.690       0.532      0.631
chem_prot           0.524          0.689       0.401      0.592
net_prot            0.601          0.679       0.543      0.591
increment           0.044          0.034       0.051      0.078
increment_prot      0.038          0.029       0.044      0.055
```
