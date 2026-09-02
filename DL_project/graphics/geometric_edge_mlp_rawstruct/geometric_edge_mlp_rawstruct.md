# geometric_edge_mlp_rawstruct

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_rawstruct'
rows: 21

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.8358      0.3279      0.8019      0.5379      0.8209      0.3333
groups_GLTP            3      0.6667      0.3067      0.6060      0.5555      0.7564      0.3462
groups_IP_trans        3      0.4348      0.7943      0.7218      0.5422      0.5556      0.8227
groups_LBP_BPI_CETP    3      0.3913      0.9078      0.7595      0.4712      0.3611      0.8723
groups_START           3      0.4103      0.6704      0.7895      0.4488      0.4792      0.6367
groups_lipocalin       3      0.7222      0.5093      0.7452      0.5158      0.7778      0.4815
groups_scp2            3      0.6471      0.6275      0.7699      0.5007      0.7059      0.7059
ALL                   21      0.5869      0.5920      0.7420      0.5103      0.6367      0.5998

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6182      0.5935     0.0818  21
max valid BA                0.6584      0.6336     0.0790  21
best valid F1               0.6130      0.6452     0.1207  21
test BA                     0.5894      0.5803     0.0903  21
test F1                     0.5119      0.5238     0.1640  21
test sensitivity            0.5869      0.6471     0.2673  21
test specificity            0.5920      0.5882     0.2797  21
test precision              0.5278      0.5000     0.0988  21
test loss                   0.8141      0.6938     0.5086  21
FPR (FP/(FP+TN))            0.4080      0.4118     0.2797  21
FNR (FN/(FN+TP))            0.4131      0.3529     0.2673  21

=== abs(sensitivity-specificity) gap: mean=0.4032 median=0.2941 n=21 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5771      0.5562     0.0415  3
  max valid BA                0.5856      0.5655     0.0418  3
  best valid F1               0.6998      0.7011     0.0037  3
  test BA                     0.5818      0.5803     0.0172  3
  test F1                     0.6801      0.6747     0.0437  3
  test sensitivity            0.8358      0.8358     0.1343  3
  test specificity            0.3279      0.2951     0.1182  3
  test precision              0.5778      0.5804     0.0111  3
  test loss                   0.7625      0.7249     0.1257  3
  FPR (FP/(FP+TN))            0.6721      0.7049     0.1182  3
  FNR (FN/(FN+TP))            0.1642      0.1642     0.1343  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5513      0.5385     0.0222  3
  max valid BA                0.6218      0.6154     0.0484  3
  best valid F1               0.6865      0.6842     0.0425  3
  test BA                     0.4867      0.4600     0.0643  3
  test F1                     0.5584      0.5484     0.0932  3
  test sensitivity            0.6667      0.6800     0.1804  3
  test specificity            0.3067      0.2800     0.1222  3
  test precision              0.4865      0.4615     0.0450  3
  test loss                   0.6945      0.6938     0.0041  3
  FPR (FP/(FP+TN))            0.6933      0.7200     0.1222  3
  FNR (FN/(FN+TP))            0.3333      0.3200     0.1804  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6891      0.6946     0.0930  3
  max valid BA                0.6962      0.6950     0.0825  3
  best valid F1               0.5667      0.6071     0.1632  3
  test BA                     0.6146      0.6105     0.0722  3
  test F1                     0.4349      0.4500     0.1697  3
  test sensitivity            0.4348      0.3913     0.2851  3
  test specificity            0.7943      0.8298     0.1417  3
  test precision              0.5098      0.5000     0.0170  3
  test loss                   0.7944      0.7553     0.1960  3
  FPR (FP/(FP+TN))            0.2057      0.1702     0.1417  3
  FNR (FN/(FN+TP))            0.5652      0.6087     0.2851  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6167      0.6033     0.0932  3
  max valid BA                0.6184      0.6082     0.0928  3
  best valid F1               0.4759      0.5479     0.1998  3
  test BA                     0.6496      0.6092     0.1625  3
  test F1                     0.4073      0.3871     0.3378  3
  test sensitivity            0.3913      0.2609     0.4282  3
  test specificity            0.9078      0.9574     0.1050  3
  test precision              0.6389      0.6667     0.1273  3
  test loss                   1.4092      0.6818     1.3720  3
  FPR (FP/(FP+TN))            0.0922      0.0426     0.1050  3
  FNR (FN/(FN+TP))            0.6087      0.7391     0.4282  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5579      0.5801     0.0501  3
  max valid BA                0.6054      0.6049     0.0256  3
  best valid F1               0.5467      0.5759     0.0913  3
  test BA                     0.5403      0.5507     0.0182  3
  test F1                     0.4160      0.4593     0.1316  3
  test sensitivity            0.4103      0.4769     0.2156  3
  test specificity            0.6704      0.5618     0.2282  3
  test precision              0.5197      0.4691     0.1111  3
  test loss                   0.7284      0.7024     0.0497  3
  FPR (FP/(FP+TN))            0.3296      0.4382     0.2282  3
  FNR (FN/(FN+TP))            0.5897      0.5231     0.2156  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6296      0.6875     0.1002  3
  max valid BA                0.7361      0.7292     0.0524  3
  best valid F1               0.6522      0.6452     0.0693  3
  test BA                     0.6157      0.5903     0.1167  3
  test F1                     0.5440      0.5070     0.1003  3
  test sensitivity            0.7222      0.6667     0.2546  3
  test specificity            0.5093      0.6806     0.4227  3
  test precision              0.4758      0.4390     0.1578  3
  test loss                   0.6568      0.6610     0.0462  3
  FPR (FP/(FP+TN))            0.4907      0.3194     0.4227  3
  FNR (FN/(FN+TP))            0.2778      0.3333     0.2546  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7059      0.7059     0.0294  3
  max valid BA                0.7451      0.7500     0.0225  3
  best valid F1               0.6635      0.6667     0.0257  3
  test BA                     0.6373      0.6176     0.0340  3
  test F1                     0.5427      0.5417     0.0194  3
  test sensitivity            0.6471      0.6471     0.1176  3
  test specificity            0.6275      0.5882     0.1797  3
  test precision              0.4865      0.4400     0.0989  3
  test loss                   0.6529      0.6535     0.0386  3
  FPR (FP/(FP+TN))            0.3725      0.4118     0.1797  3
  FNR (FN/(FN+TP))            0.3529      0.3529     0.1176  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.476    0.600     4.000              0.347         0.520   5.000               0.480          0.590
GLTP                     0.595         0.484    0.497     2.000              0.488         0.480   3.000               0.494          0.482
IP_trans                 0.727         0.727    0.594     3.000              0.720         0.626   2.667               0.664          0.610
LBP_BPI_CETP             0.721         0.811    0.659     2.000              0.811         0.653   1.667               0.792          0.602
START                    0.574         0.487    0.577     3.000              0.460         0.505   4.000               0.519          0.561
lipocalin                0.558         0.299    0.598     5.000              0.215         0.601   2.000               0.679          0.573
scp2                     0.632         0.441    0.720     2.667              0.538         0.640   2.667               0.621          0.629

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.532               0.488                  0.036                     0.176
net_AUC           0.606               0.601                  0.073                     0.069

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.471                  0.044                     0.205
net_AUC_prot           0.575               0.541                  0.083                     0.072

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.607               0.581                  0.084                     0.115
net_AUC_lipid           0.578               0.613                  0.094                     0.048

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.532  0.456      0.511     0.469
10     0.532  0.545      0.511     0.542
49     0.532  0.568      0.511     0.546
51     0.532  0.582      0.511     0.569
120    0.532  0.606      0.511     0.575

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.622         0.671      0.048          0.654              0.700           0.046
10        0.622         0.662      0.039          0.654              0.690           0.036
49        0.622         0.661      0.038          0.654              0.698           0.045
51        0.622         0.673      0.050          0.654              0.708           0.054
120       0.622         0.664      0.042          0.654              0.693           0.039

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.476  0.600      0.347     0.520     0.524         0.566      0.041          0.589              0.647           0.058
GLTP          0.484  0.497      0.488     0.480     0.520         0.517     -0.002          0.547              0.552           0.004
IP_trans      0.727  0.594      0.720     0.626     0.727         0.746      0.020          0.730              0.747           0.017
LBP_BPI_CETP  0.811  0.659      0.811     0.653     0.811         0.822      0.012          0.815              0.830           0.014
START         0.487  0.577      0.460     0.505     0.513         0.579      0.066          0.561              0.591           0.030
lipocalin     0.299  0.598      0.215     0.601     0.701         0.739      0.039          0.698              0.749           0.051
scp2          0.441  0.720      0.538     0.640     0.562         0.680      0.118          0.634              0.736           0.102

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.532               0.488                  0.036                     0.176
net               0.606               0.601                  0.073                     0.069
fit_chem          0.622               0.590                  0.035                     0.121
fit_chem_net      0.664               0.662                  0.038                     0.113
increment         0.042               0.025                  0.031                     0.040

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.471                  0.044                     0.205
net_prot               0.575               0.541                  0.083                     0.072
fit_chem_prot          0.654               0.659                  0.037                     0.099
fit_chem_net_prot      0.693               0.713                  0.038                     0.099
increment_prot         0.039               0.027                  0.028                     0.034
```
