# geometric_edge_attention_protgeom8

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention_protgeom8'
rows: 21

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.5821      0.5792      0.7362      0.6451      0.6020      0.5914
groups_GLTP            3      0.4933      0.5733      0.6818      0.4793      0.5128      0.7179
groups_IP_trans        3      0.6232      0.6312      0.7539      0.6758      0.6528      0.6099
groups_LBP_BPI_CETP    3      0.2754      0.8227      0.8162      0.6246      0.4583      0.7660
groups_START           3      0.8000      0.4794      0.7019      0.6701      0.7083      0.4607
groups_lipocalin       3      0.5926      0.5046      0.8033      0.5703      0.6481      0.4722
groups_scp2            3      0.4510      0.6078      0.7190      0.5785      0.5882      0.6569
ALL                   21      0.5454      0.5998      0.7446      0.6062      0.5958      0.6107

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6033      0.5882     0.0724  21
max valid BA                0.6724      0.6875     0.0672  21
best valid F1               0.6206      0.6364     0.1107  21
test BA                     0.5726      0.5629     0.0836  21
test F1                     0.4768      0.4870     0.1724  21
test sensitivity            0.5454      0.4800     0.2653  21
test specificity            0.5998      0.6170     0.2302  21
test precision              0.4631      0.5135     0.1569  21
test loss                   0.7280      0.6954     0.2204  21
FPR (FP/(FP+TN))            0.4002      0.3830     0.2302  21
FNR (FN/(FN+TP))            0.4546      0.5200     0.2653  21

=== abs(sensitivity-specificity) gap: mean=0.3903 median=0.3488 n=21 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5967      0.5799     0.0450  3
  max valid BA                0.6298      0.6227     0.0355  3
  best valid F1               0.6903      0.7027     0.0237  3
  test BA                     0.5807      0.5629     0.0471  3
  test F1                     0.5670      0.4870     0.1472  3
  test sensitivity            0.5821      0.4179     0.3106  3
  test specificity            0.5792      0.6721     0.2201  3
  test precision              0.6027      0.6058     0.0181  3
  test loss                   0.7275      0.7192     0.0225  3
  FPR (FP/(FP+TN))            0.4208      0.3279     0.2201  3
  FNR (FN/(FN+TP))            0.4179      0.5821     0.3106  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6154      0.5769     0.1018  3
  max valid BA                0.6410      0.6154     0.0801  3
  best valid F1               0.6719      0.6753     0.1041  3
  test BA                     0.5333      0.5400     0.0702  3
  test F1                     0.4722      0.5106     0.2269  3
  test sensitivity            0.4933      0.4800     0.3402  3
  test specificity            0.5733      0.6000     0.2013  3
  test precision              0.5043      0.5455     0.0910  3
  test loss                   0.7056      0.6971     0.0162  3
  FPR (FP/(FP+TN))            0.4267      0.4000     0.2013  3
  FNR (FN/(FN+TP))            0.5067      0.5200     0.3402  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6314      0.6436     0.0592  3
  max valid BA                0.7302      0.7376     0.0317  3
  best valid F1               0.6446      0.6552     0.0403  3
  test BA                     0.6272      0.6036     0.0851  3
  test F1                     0.5051      0.5231     0.1381  3
  test sensitivity            0.6232      0.7391     0.2795  3
  test specificity            0.6312      0.6170     0.1707  3
  test precision              0.4519      0.4375     0.0558  3
  test loss                   0.6407      0.6489     0.0430  3
  FPR (FP/(FP+TN))            0.3688      0.3830     0.1707  3
  FNR (FN/(FN+TP))            0.3768      0.2609     0.2795  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6121      0.5887     0.1059  3
  max valid BA                0.6683      0.7278     0.1097  3
  best valid F1               0.4975      0.6364     0.2579  3
  test BA                     0.5490      0.4894     0.1094  3
  test F1                     0.2922      0.3265     0.2766  3
  test sensitivity            0.2754      0.3478     0.2472  3
  test specificity            0.8227      0.8723     0.1859  3
  test precision              0.3183      0.3077     0.3237  3
  test loss                   0.9604      0.6628     0.6105  3
  FPR (FP/(FP+TN))            0.1773      0.1277     0.1859  3
  FNR (FN/(FN+TP))            0.7246      0.6522     0.2472  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5845      0.5900     0.0310  3
  max valid BA                0.6146      0.6312     0.0339  3
  best valid F1               0.6089      0.6144     0.0132  3
  test BA                     0.6397      0.6321     0.0594  3
  test F1                     0.6357      0.6162     0.0525  3
  test sensitivity            0.8000      0.8769     0.1332  3
  test specificity            0.4794      0.5281     0.1683  3
  test precision              0.5345      0.5526     0.0528  3
  test loss                   0.6859      0.6951     0.0447  3
  FPR (FP/(FP+TN))            0.5206      0.4719     0.1683  3
  FNR (FN/(FN+TP))            0.2000      0.1231     0.1332  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5602      0.5694     0.0768  3
  max valid BA                0.6875      0.6875     0.0347  3
  best valid F1               0.5848      0.5797     0.0470  3
  test BA                     0.5486      0.5000     0.1028  3
  test F1                     0.4541      0.4783     0.1107  3
  test sensitivity            0.5926      0.5278     0.2970  3
  test specificity            0.5046      0.6667     0.4069  3
  test precision              0.4109      0.3333     0.1429  3
  test loss                   0.7013      0.6868     0.0610  3
  FPR (FP/(FP+TN))            0.4954      0.3333     0.4069  3
  FNR (FN/(FN+TP))            0.4074      0.4722     0.2970  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6225      0.5882     0.1142  3
  max valid BA                0.7353      0.7206     0.0389  3
  best valid F1               0.6464      0.6364     0.0521  3
  test BA                     0.5294      0.5588     0.1060  3
  test F1                     0.4116      0.4444     0.0617  3
  test sensitivity            0.4510      0.4706     0.0899  3
  test specificity            0.6078      0.5882     0.2653  3
  test precision              0.4193      0.3913     0.1684  3
  test loss                   0.6746      0.7025     0.0596  3
  FPR (FP/(FP+TN))            0.3922      0.4118     0.2652  3
  FNR (FN/(FN+TP))            0.5490      0.5294     0.0899  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.476    0.543     4.000              0.347         0.472   5.000               0.480          0.611
GLTP                     0.595         0.484    0.507     2.000              0.488         0.471   3.000               0.494          0.509
IP_trans                 0.727         0.727    0.648     3.000              0.720         0.660   2.667               0.664          0.494
LBP_BPI_CETP             0.721         0.811    0.657     2.000              0.811         0.641   1.667               0.792          0.526
START                    0.574         0.487    0.534     3.000              0.460         0.486   4.000               0.519          0.602
lipocalin                0.558         0.299    0.607     5.000              0.215         0.567   2.000               0.679          0.498
scp2                     0.632         0.441    0.713     2.667              0.538         0.694   2.667               0.621          0.689

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.532               0.488                  0.036                     0.176
net_AUC           0.601               0.603                  0.085                     0.076

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.471                  0.044                     0.205
net_AUC_prot           0.570               0.554                  0.103                     0.096

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.607               0.581                  0.084                     0.115
net_AUC_lipid           0.561               0.576                  0.093                     0.074

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.532  0.515      0.511     0.522
10     0.532  0.550      0.511     0.542
49     0.532  0.574      0.511     0.565
51     0.532  0.560      0.511     0.542
120    0.532  0.601      0.511     0.570

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.622         0.649      0.026          0.654              0.682           0.028
10        0.622         0.665      0.043          0.654              0.691           0.037
49        0.622         0.676      0.053          0.654              0.709           0.056
51        0.622         0.674      0.052          0.654              0.702           0.048
120       0.622         0.678      0.055          0.654              0.694           0.041

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.476  0.543      0.347     0.472     0.524         0.583      0.058          0.589              0.634           0.045
GLTP          0.484  0.507      0.488     0.471     0.520         0.568      0.048          0.547              0.558           0.010
IP_trans      0.727  0.648      0.720     0.660     0.727         0.755      0.029          0.730              0.759           0.029
LBP_BPI_CETP  0.811  0.657      0.811     0.641     0.811         0.823      0.013          0.815              0.823           0.008
START         0.487  0.534      0.460     0.486     0.513         0.602      0.089          0.561              0.617           0.057
lipocalin     0.299  0.607      0.215     0.567     0.701         0.719      0.019          0.698              0.729           0.030
scp2          0.441  0.713      0.538     0.694     0.562         0.693      0.131          0.634              0.741           0.107

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.532               0.488                  0.036                     0.176
net               0.601               0.603                  0.085                     0.076
fit_chem          0.622               0.590                  0.035                     0.121
fit_chem_net      0.678               0.673                  0.051                     0.097
increment         0.055               0.042                  0.036                     0.042

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.471                  0.044                     0.205
net_prot               0.570               0.554                  0.103                     0.096
fit_chem_prot          0.654               0.659                  0.037                     0.099
fit_chem_net_prot      0.694               0.698                  0.050                     0.093
increment_prot         0.041               0.016                  0.035                     0.034
```
