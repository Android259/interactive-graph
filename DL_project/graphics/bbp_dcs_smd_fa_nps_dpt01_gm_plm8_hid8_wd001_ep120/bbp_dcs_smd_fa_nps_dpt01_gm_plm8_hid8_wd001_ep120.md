# bbp_dcs_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120

## Summary (analysis/summarize_label.py)

```
Summary: 'bbp_dcs_smd_fa_nps_dpt01_gm_plm8_hid8_wd001_ep120'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4373      0.6504         n/a         n/a         n/a         n/a
groups_GLTP            5      0.1282      0.9221         n/a         n/a         n/a         n/a
groups_IP_trans        5      0.4141      0.7274         n/a         n/a         n/a         n/a
groups_LBP_BPI_CETP    5      0.3495      0.8739         n/a         n/a         n/a         n/a
groups_START           5      0.2105      0.7750         n/a         n/a         n/a         n/a
groups_lipocalin       5      0.2478      0.7409         n/a         n/a         n/a         n/a
groups_scp2            5      0.4705      0.6890         n/a         n/a         n/a         n/a
ALL                   35      0.3226      0.7684         n/a         n/a         n/a         n/a

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5742      0.5632     0.0567  35
max valid BA                0.6047      0.6237     0.0624  35
best valid F1               0.5394      0.5655     0.1188  35
test BA                     0.5455      0.5500     0.0572  35
test F1                     0.3378      0.3789     0.1956  35
test sensitivity            0.3226      0.2941     0.2435  35
test specificity            0.7684      0.8298     0.2141  35
test precision              0.4914      0.4706     0.2291  33
test loss                   0.7434      0.6932     0.1408  35
FPR (FP/(FP+TN))            0.2316      0.1702     0.2141  35
FNR (FN/(FN+TP))            0.6774      0.7059     0.2435  35

=== abs(sensitivity-specificity) gap: mean=0.5396 median=0.5680 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5378      0.5549     0.0327  5
  max valid BA                0.5718      0.5643     0.0462  5
  best valid F1               0.6494      0.6484     0.0589  5
  test BA                     0.5439      0.5552     0.0346  5
  test F1                     0.4196      0.5675     0.2844  5
  test sensitivity            0.4373      0.5541     0.3501  5
  test specificity            0.6504      0.5643     0.2902  5
  test precision              0.5765      0.5803     0.0090  4
  test loss                   0.7901      0.7030     0.1916  5
  FPR (FP/(FP+TN))            0.3496      0.4357     0.2902  5
  FNR (FN/(FN+TP))            0.5627      0.4459     0.3501  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5812      0.6029     0.0441  5
  max valid BA                0.6124      0.6154     0.0236  5
  best valid F1               0.5113      0.5000     0.1565  5
  test BA                     0.5252      0.5600     0.0598  5
  test F1                     0.2033      0.2162     0.1301  5
  test sensitivity            0.1282      0.1212     0.0867  5
  test specificity            0.9221      0.9706     0.1176  5
  test precision              0.6227      0.7500     0.4347  5
  test loss                   0.8131      0.7358     0.2048  5
  FPR (FP/(FP+TN))            0.0779      0.0294     0.1176  5
  FNR (FN/(FN+TP))            0.8718      0.8788     0.0867  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6130      0.6130     0.0363  5
  max valid BA                0.6648      0.6440     0.0517  5
  best valid F1               0.5902      0.5758     0.0501  5
  test BA                     0.5708      0.5589     0.0354  5
  test F1                     0.4194      0.4848     0.1390  5
  test sensitivity            0.4141      0.4832     0.2068  5
  test specificity            0.7274      0.6596     0.1453  5
  test precision              0.4700      0.4545     0.0308  5
  test loss                   0.6583      0.6425     0.0453  5
  FPR (FP/(FP+TN))            0.2726      0.3404     0.1453  5
  FNR (FN/(FN+TP))            0.5859      0.5168     0.2068  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6331      0.6512     0.0449  5
  max valid BA                0.6559      0.6512     0.0330  5
  best valid F1               0.5604      0.5846     0.0535  5
  test BA                     0.6117      0.6092     0.0247  5
  test F1                     0.4425      0.4103     0.0718  5
  test sensitivity            0.3495      0.3456     0.0857  5
  test specificity            0.8739      0.8723     0.0622  5
  test precision              0.6334      0.6442     0.1126  5
  test loss                   0.7027      0.6753     0.0578  5
  FPR (FP/(FP+TN))            0.1261      0.1277     0.0622  5
  FNR (FN/(FN+TP))            0.6505      0.6544     0.0857  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5251      0.5311     0.0241  5
  max valid BA                0.5537      0.5528     0.0464  5
  best valid F1               0.5313      0.5655     0.1005  5
  test BA                     0.4927      0.5000     0.0532  5
  test F1                     0.2265      0.3284     0.2096  5
  test sensitivity            0.2105      0.2986     0.1967  5
  test specificity            0.7750      0.8010     0.2345  5
  test precision              0.3181      0.3772     0.2273  4
  test loss                   0.7509      0.6901     0.0886  5
  FPR (FP/(FP+TN))            0.2250      0.1990     0.2345  5
  FNR (FN/(FN+TP))            0.7895      0.7014     0.1967  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5110      0.5069     0.0242  5
  max valid BA                0.5332      0.5428     0.0365  5
  best valid F1               0.3788      0.3729     0.1535  5
  test BA                     0.4943      0.4931     0.0350  5
  test F1                     0.2093      0.0930     0.2236  5
  test sensitivity            0.2478      0.0556     0.3509  5
  test specificity            0.7409      0.9167     0.3024  5
  test precision              0.2992      0.2857     0.1075  5
  test loss                   0.7639      0.6769     0.1861  5
  FPR (FP/(FP+TN))            0.2591      0.0833     0.3024  5
  FNR (FN/(FN+TP))            0.7522      0.9444     0.3509  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6184      0.6176     0.0381  5
  max valid BA                0.6413      0.6439     0.0514  5
  best valid F1               0.5543      0.5600     0.0236  5
  test BA                     0.5797      0.5989     0.0460  5
  test F1                     0.4443      0.4706     0.0750  5
  test sensitivity            0.4705      0.4706     0.1921  5
  test specificity            0.6890      0.7353     0.2198  5
  test precision              0.5020      0.4452     0.1898  5
  test loss                   0.7245      0.7055     0.1451  5
  FPR (FP/(FP+TN))            0.3110      0.2647     0.2198  5
  FNR (FN/(FN+TP))            0.5295      0.5294     0.1921  5
```

## AUC vs chemistry null model, in-sample increment

### features = tanimoto (full molecular structure)

```
########## split = valid ##########

--- null model (null_model.py), features = tanimoto (tanimoto), epoch 120 ---
=== valid block, epoch 120 ===

=== mean over seeds ===
               rows   pos  sim_to_train_pos  null_AUC_k15  null_AUC_prot_k15  proteins  net_AUC  net_AUC_prot
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.806         0.340              0.381       4.0    0.589         0.593
GLTP           52.0  26.0             0.618         0.492              0.500       2.0    0.626         0.500
IP_trans       71.0  24.0             0.809         0.761              0.748       3.0    0.610         0.570
LBP_BPI_CETP   71.0  24.0             0.809         0.719              0.701       2.0    0.518         0.472
START         153.0  64.0             0.791         0.508              0.479       3.0    0.380         0.500
lipocalin     108.0  36.0             0.847         0.605              0.655       5.0    0.656         0.718
scp2           51.0  17.0             0.808         0.666              0.619       2.0    0.654         0.582

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
null_AUC_k15      0.584          0.715       0.486
net_AUC           0.576          0.594       0.563

=== the same rows ranked INSIDE each protein (interaction term only) ===
21 protein-blocks across 7 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
null_AUC_prot_k15      0.583          0.690       0.504
net_AUC_prot           0.562          0.542       0.578

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
        chem    net  chem_prot  net_prot
epoch                                   
1      0.584  0.555      0.583     0.565
10     0.584  0.557      0.583     0.483
49     0.584  0.587      0.583     0.561
51     0.584  0.591      0.583     0.569
120    0.584  0.576      0.583     0.562

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1           0.6         0.668      0.067          0.664              0.713           0.048
10          0.6         0.682      0.081          0.664              0.693           0.029
49          0.6         0.666      0.065          0.664              0.707           0.043
51          0.6         0.662      0.062          0.664              0.689           0.024
120         0.6         0.611      0.010          0.664              0.679           0.014

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.340  0.589      0.381     0.593      0.006           0.004
GLTP          0.492  0.626      0.500     0.500     -0.097          -0.018
IP_trans      0.761  0.610      0.748     0.570     -0.033          -0.008
LBP_BPI_CETP  0.719  0.518      0.701     0.472     -0.010          -0.015
START         0.508  0.380      0.479     0.500      0.111           0.064
lipocalin     0.605  0.656      0.655     0.718      0.022           0.028
scp2          0.666  0.654      0.619     0.582      0.074           0.047

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.584          0.715       0.486      0.666
net                 0.576          0.594       0.563      0.654
chem_prot           0.583          0.690       0.504      0.619
net_prot            0.562          0.542       0.578      0.582
increment           0.010          0.010       0.010      0.074
increment_prot      0.014          0.008       0.019      0.047

wrote : /tmp/tmp.JgQ3QLFCPD
```

### features = lipid4 (chain/unsaturation/hbond/heavy only)

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== valid block, epoch 120 ===

=== mean over seeds ===
               rows   pos  sim_to_train_pos  null_AUC_k15  null_AUC_prot_k15  proteins  net_AUC  net_AUC_prot
fam                                                                                                          
CRAL-TRIO     129.0  67.0             0.622         0.492              0.372       4.0    0.589         0.593
GLTP           52.0  26.0             0.591         0.505              0.493       2.0    0.626         0.500
IP_trans       71.0  24.0             0.758         0.708              0.686       3.0    0.610         0.570
LBP_BPI_CETP   71.0  24.0             0.719         0.809              0.801       2.0    0.518         0.472
START         153.0  64.0             0.575         0.499              0.471       3.0    0.380         0.500
lipocalin     108.0  36.0             0.540         0.238              0.166       5.0    0.656         0.718
scp2           51.0  17.0             0.631         0.420              0.510       2.0    0.654         0.582

=== mean AUC, never over all seven at once (files/signal_state.md 6.4) ===
              all seven  working three  other four
null_AUC_k15      0.524          0.646       0.434
net_AUC           0.576          0.594       0.563

=== the same rows ranked INSIDE each protein (interaction term only) ===
21 protein-blocks across 7 family-seed splits carry a usable ranking (median 3 proteins per split)
                   all seven  working three  other four
null_AUC_prot_k15      0.500          0.666       0.375
net_AUC_prot           0.562          0.542       0.578

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15 ===

1. Each score on its own
        chem    net  chem_prot  net_prot
epoch                                   
1      0.524  0.555        0.5     0.565
10     0.524  0.557        0.5     0.483
49     0.524  0.587        0.5     0.561
51     0.524  0.591        0.5     0.569
120    0.524  0.576        0.5     0.562

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND)
   pooled, then with one intercept per protein
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.625         0.650      0.025          0.669              0.694           0.026
10        0.625         0.640      0.015          0.669              0.676           0.007
49        0.625         0.649      0.024          0.669              0.696           0.027
51        0.625         0.638      0.013          0.669              0.693           0.024
120       0.625         0.639      0.014          0.669              0.692           0.023

3. Increment per family, last epoch
               chem    net  chem_prot  net_prot  increment  increment_prot
fam                                                                       
CRAL-TRIO     0.492  0.589      0.372     0.593      0.088           0.050
GLTP          0.505  0.626      0.493     0.500     -0.115           0.018
IP_trans      0.708  0.610      0.686     0.570     -0.006           0.005
LBP_BPI_CETP  0.809  0.518      0.801     0.472     -0.023          -0.022
START         0.499  0.380      0.471     0.500      0.072           0.033
lipocalin     0.238  0.656      0.166     0.718      0.011           0.018
scp2          0.420  0.654      0.510     0.582      0.073           0.061

4. Never averaged over all seven at once (files/signal_state.md 6.4)
                all seven  working three  other four  scp2 only
chem                0.524          0.646       0.434      0.420
net                 0.576          0.594       0.563      0.654
chem_prot           0.500          0.666       0.375      0.510
net_prot            0.562          0.542       0.578      0.582
increment           0.014          0.014       0.014      0.073
increment_prot      0.023          0.015       0.030      0.061
```
