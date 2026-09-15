# descriptors_head_family_neutral_lipprop_lambdasqrt

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_head_family_neutral_lipprop_lambdasqrt'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6239      0.3803      0.5686      0.4478      0.6687      0.4516
groups_GLTP            5      0.4960      0.5840      0.6396      0.4128      0.5462      0.6692
groups_IP_trans        5      0.6696      0.3617      0.6347      0.4551      0.7583      0.4085
groups_LBP_BPI_CETP    5      0.6522      0.6638      0.6227      0.4425      0.8333      0.6766
groups_START           5      0.5538      0.5506      0.4498      0.5416      0.3406      0.7753
groups_lipocalin       5      0.6222      0.4278      0.5645      0.5223      0.6444      0.5194
groups_scp2            5      0.6235      0.3294      0.6671      0.4200      0.8235      0.3588
ALL                   35      0.6059      0.4711      0.5924      0.4632      0.6593      0.5514

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5770      0.5694     0.0812  35
max valid BA                0.6053      0.5842     0.0910  35
best valid F1               0.5817      0.5625     0.0884  35
test BA                     0.5385      0.5294     0.0868  35
test AUC                    0.5440      0.5239     0.1327  35
test AUC in-protein         0.5465      0.4932     0.1507  35
  (proteins averaged)       3.1429      3.0000     1.0042  35
test AUC in-protein (pairs)      0.5598      0.5561     0.1491  35
  (proteins contributing)      3.5143      3.0000     1.7213  35
test F1                     0.4851      0.4868     0.1054  35
test sensitivity            0.6059      0.5652     0.2285  35
test specificity            0.4711      0.4722     0.2393  35
test precision              0.4420      0.4444     0.1217  35
test loss                   0.6966      0.6926     0.0204  35
FPR (FP/(FP+TN))            0.5289      0.5278     0.2393  35
FNR (FN/(FN+TP))            0.3941      0.4348     0.2285  35

=== abs(sensitivity-specificity) gap: mean=0.3656 median=0.3125 n=35 ===
sensitivity std across seeds (by group): mean=0.2298 median=0.2514 n=7
specificity std across seeds (by group): mean=0.2210 median=0.2073 n=7

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5532      0.5408     0.0342  5
  max valid BA                0.5601      0.5608     0.0349  5
  best valid F1               0.6231      0.6296     0.0834  5
  test BA                     0.5021      0.5005     0.0460  5
  test AUC                    0.5233      0.5199     0.0388  5
  test AUC in-protein         0.4854      0.4932     0.0755  5
    (proteins averaged)       4.0000      4.0000     0.0000  5
  test AUC in-protein (pairs)      0.5945      0.6084     0.0258  5
    (proteins contributing)      4.4000      4.0000     0.5477  5
  test F1                     0.5593      0.5828     0.1034  5
  test sensitivity            0.6239      0.6567     0.1984  5
  test specificity            0.3803      0.4426     0.1329  5
  test precision              0.5187      0.5238     0.0447  5
  test loss                   0.6884      0.6875     0.0031  5
  FPR (FP/(FP+TN))            0.6197      0.5574     0.1329  5
  FNR (FN/(FN+TP))            0.3761      0.3433     0.1984  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5462      0.5385     0.0520  5
  max valid BA                0.6077      0.5769     0.0977  5
  best valid F1               0.6265      0.6494     0.0570  5
  test BA                     0.5400      0.5000     0.1030  5
  test AUC                    0.4768      0.4752     0.0878  5
  test AUC in-protein         0.4734      0.4744     0.0274  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4206      0.4204     0.0571  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5230      0.4898     0.0816  5
  test sensitivity            0.4960      0.4800     0.0456  5
  test specificity            0.5840      0.5200     0.1757  5
  test precision              0.5618      0.5000     0.1480  5
  test loss                   0.7309      0.7161     0.0300  5
  FPR (FP/(FP+TN))            0.4160      0.4800     0.1757  5
  FNR (FN/(FN+TP))            0.5040      0.5200     0.0456  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5667      0.5563     0.0406  5
  max valid BA                0.5834      0.5762     0.0370  5
  best valid F1               0.5194      0.5246     0.0416  5
  test BA                     0.5156      0.4977     0.0627  5
  test AUC                    0.5515      0.5495     0.0457  5
  test AUC in-protein         0.6017      0.6168     0.1156  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5773      0.5968     0.0440  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.4328      0.4615     0.1115  5
  test sensitivity            0.6696      0.6957     0.2861  5
  test specificity            0.3617      0.2553     0.2894  5
  test precision              0.3387      0.3273     0.0612  5
  test loss                   0.6909      0.6946     0.0092  5
  FPR (FP/(FP+TN))            0.6383      0.7447     0.2894  5
  FNR (FN/(FN+TP))            0.3304      0.3043     0.2861  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7045      0.7668     0.1257  5
  max valid BA                0.7550      0.7988     0.1144  5
  best valid F1               0.6927      0.7213     0.1014  5
  test BA                     0.6580      0.6105     0.0862  5
  test AUC                    0.8109      0.7845     0.0801  5
  test AUC in-protein         0.8355      0.8242     0.0756  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.8330      0.8313     0.0695  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5399      0.5417     0.1148  5
  test sensitivity            0.6522      0.5652     0.3090  5
  test specificity            0.6638      0.7447     0.2651  5
  test precision              0.5166      0.5294     0.0788  5
  test loss                   0.6797      0.6869     0.0142  5
  FPR (FP/(FP+TN))            0.3362      0.2553     0.2651  5
  FNR (FN/(FN+TP))            0.3478      0.4348     0.3090  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5521      0.5808     0.0641  5
  max valid BA                0.5580      0.5842     0.0676  5
  best valid F1               0.5853      0.6078     0.0507  5
  test BA                     0.5522      0.5448     0.0343  5
  test AUC                    0.5358      0.5557     0.0443  5
  test AUC in-protein         0.4808      0.4742     0.0274  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5106      0.5329     0.0700  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.4956      0.4696     0.0669  5
  test sensitivity            0.5538      0.4154     0.2514  5
  test specificity            0.5506      0.6742     0.2861  5
  test precision              0.4947      0.4821     0.0653  5
  test loss                   0.6886      0.6900     0.0127  5
  FPR (FP/(FP+TN))            0.4494      0.3258     0.2861  5
  FNR (FN/(FN+TP))            0.4462      0.5846     0.2514  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5458      0.5694     0.0454  5
  max valid BA                0.5819      0.5972     0.0400  5
  best valid F1               0.4917      0.5176     0.0528  5
  test BA                     0.5250      0.5278     0.0305  5
  test AUC                    0.4975      0.4803     0.0460  5
  test AUC in-protein         0.4988      0.4471     0.1119  5
    (proteins averaged)       5.0000      5.0000     0.0000  5
  test AUC in-protein (pairs)      0.5931      0.6039     0.0762  5
    (proteins contributing)      7.2000      7.0000     0.4472  5
  test F1                     0.4357      0.4421     0.0790  5
  test sensitivity            0.6222      0.5833     0.2466  5
  test specificity            0.4278      0.4722     0.1908  5
  test precision              0.3478      0.3529     0.0180  5
  test loss                   0.6959      0.6948     0.0047  5
  FPR (FP/(FP+TN))            0.5722      0.5278     0.1908  5
  FNR (FN/(FN+TP))            0.3778      0.4167     0.2466  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5706      0.5735     0.0644  5
  max valid BA                0.5912      0.6029     0.0636  5
  best valid F1               0.5334      0.5217     0.0296  5
  test BA                     0.4765      0.5294     0.1113  5
  test AUC                    0.4123      0.3962     0.0904  5
  test AUC in-protein         0.4503      0.3767     0.1222  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.3897      0.3865     0.0876  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.4094      0.4000     0.1206  5
  test sensitivity            0.6235      0.6471     0.2715  5
  test specificity            0.3294      0.2353     0.2073  5
  test precision              0.3160      0.3500     0.0859  5
  test loss                   0.7016      0.6980     0.0104  5
  FPR (FP/(FP+TN))            0.6706      0.7647     0.2073  5
  FNR (FN/(FN+TP))            0.3765      0.3529     0.2715  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (apolar_sasa_share,aromatic_share,buriedness_q50,chain,hbond,heavy,hydropathy_rim,pocket_elongation_lambda_sqrt,pocket_flatness_lambda_sqrt,pocket_volume_per_sasa,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.272         0.653    0.461              0.612         0.505
GLTP                     0.287         0.757    0.490              0.780         0.233
IP_trans                 0.334         0.400    0.562              0.310         0.498
LBP_BPI_CETP             0.315         0.562    0.783              0.538         0.815
START                    0.274         0.407    0.413              0.457         0.450
lipocalin                0.272         0.683    0.519              0.665         0.539
scp2                     0.280         0.625    0.525              0.620         0.519

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.584               0.612                  0.062                     0.137
net_AUC           0.536               0.512                  0.083                     0.119

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.569               0.594                   0.05                     0.152
net_AUC_pair           0.508               0.495                   0.09                     0.171

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.584  0.432      0.569     0.447
10     0.584  0.503      0.569     0.477
49     0.584  0.537      0.569     0.507
51     0.584  0.536      0.569     0.513
120    0.584  0.536      0.569     0.508

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1          0.64         0.696      0.056
10         0.64         0.703      0.063
49         0.64         0.700      0.060
51         0.64         0.704      0.064
120        0.64         0.697      0.057

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.653  0.461      0.612     0.505     0.653         0.658      0.005
GLTP          0.757  0.490      0.780     0.233     0.757         0.843      0.087
IP_trans      0.400  0.562      0.310     0.498     0.600         0.655      0.054
LBP_BPI_CETP  0.562  0.783      0.538     0.815     0.569         0.786      0.217
START         0.407  0.413      0.457     0.450     0.593         0.613      0.020
lipocalin     0.683  0.519      0.665     0.539     0.683         0.692      0.008
scp2          0.625  0.525      0.620     0.519     0.625         0.633      0.008

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.584               0.612                  0.062                     0.137
net               0.536               0.512                  0.083                     0.119
fit_chem          0.640               0.628                  0.060                     0.064
fit_chem_net      0.697               0.691                  0.057                     0.085
increment         0.057               0.014                  0.046                     0.077

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.569               0.594                   0.05                     0.152
net_pair       0.508               0.495                   0.09                     0.171
```
