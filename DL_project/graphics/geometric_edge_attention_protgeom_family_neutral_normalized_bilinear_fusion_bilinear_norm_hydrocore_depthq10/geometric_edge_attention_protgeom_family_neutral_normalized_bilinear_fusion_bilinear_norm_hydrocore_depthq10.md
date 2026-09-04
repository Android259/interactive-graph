# geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_hydrocore_depthq10

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_hydrocore_depthq10'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.2806      0.7541      0.7691      0.7179      0.3612      0.7452
groups_GLTP            5      0.2400      0.7760      0.6627      0.6618      0.3077      0.8077
groups_IP_trans        5      0.3043      0.8298      0.6612      0.6455      0.3833      0.8681
groups_LBP_BPI_CETP    5      0.1391      0.9277      0.6572      0.6652      0.1917      0.9489
groups_START           5      0.2215      0.7865      0.8826      0.7003      0.2969      0.8180
groups_lipocalin       5      0.4222      0.7583      0.7266      0.6327      0.4333      0.7806
groups_scp2            5      0.2706      0.8118      0.6022      0.6933      0.3294      0.8529
ALL                   35      0.2683      0.8063      0.7088      0.6738      0.3291      0.8316

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5803      0.5824     0.0591  35
max valid BA                0.6190      0.6139     0.0558  35
best valid F1               0.5424      0.5517     0.0965  35
test BA                     0.5373      0.5147     0.0786  35
test F1                     0.3038      0.2609     0.1847  35
test sensitivity            0.2683      0.1765     0.2200  35
test specificity            0.8063      0.8529     0.1754  35
test precision              0.4739      0.4495     0.1562  34
test loss                   0.7763      0.6868     0.2648  35
FPR (FP/(FP+TN))            0.1937      0.1471     0.1754  35
FNR (FN/(FN+TP))            0.7317      0.8235     0.2200  35

=== abs(sensitivity-specificity) gap: mean=0.6018 median=0.6115 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5532      0.5438     0.0278  5
  max valid BA                0.6034      0.6068     0.0318  5
  best valid F1               0.6328      0.6277     0.0578  5
  test BA                     0.5173      0.5276     0.0312  5
  test F1                     0.2835      0.1818     0.2598  5
  test sensitivity            0.2806      0.1045     0.3736  5
  test specificity            0.7541      0.8852     0.3362  5
  test precision              0.5450      0.5487     0.1261  5
  test loss                   0.8113      0.8292     0.1066  5
  FPR (FP/(FP+TN))            0.2459      0.1148     0.3362  5
  FNR (FN/(FN+TP))            0.7194      0.8955     0.3736  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5577      0.5577     0.0304  5
  max valid BA                0.5808      0.5962     0.0211  5
  best valid F1               0.5456      0.5283     0.0926  5
  test BA                     0.5080      0.4800     0.1331  5
  test F1                     0.3260      0.2778     0.1887  5
  test sensitivity            0.2400      0.2000     0.1414  5
  test specificity            0.7760      0.7200     0.1284  5
  test precision              0.5099      0.4545     0.2832  5
  test loss                   0.7358      0.7266     0.0394  5
  FPR (FP/(FP+TN))            0.2240      0.2800     0.1284  5
  FNR (FN/(FN+TP))            0.7600      0.8000     0.1414  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6257      0.6241     0.0505  5
  max valid BA                0.6565      0.6653     0.0488  5
  best valid F1               0.5384      0.5366     0.0669  5
  test BA                     0.5671      0.5463     0.0710  5
  test F1                     0.3543      0.3429     0.1388  5
  test sensitivity            0.3043      0.2609     0.1627  5
  test specificity            0.8298      0.8298     0.0583  5
  test precision              0.4537      0.4444     0.0980  5
  test loss                   0.6417      0.6392     0.0255  5
  FPR (FP/(FP+TN))            0.1702      0.1702     0.0583  5
  FNR (FN/(FN+TP))            0.6957      0.7391     0.1627  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5703      0.5310     0.0635  5
  max valid BA                0.6434      0.6348     0.0271  5
  best valid F1               0.5346      0.5283     0.0555  5
  test BA                     0.5334      0.5116     0.0770  5
  test F1                     0.2013      0.1429     0.1770  5
  test sensitivity            0.1391      0.0870     0.1422  5
  test specificity            0.9277      0.9362     0.0575  5
  test precision              0.4700      0.5000     0.1987  5
  test loss                   0.8474      0.6726     0.4106  5
  FPR (FP/(FP+TN))            0.0723      0.0638     0.0575  5
  FNR (FN/(FN+TP))            0.8609      0.9130     0.1422  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5574      0.5607     0.0622  5
  max valid BA                0.5941      0.5941     0.0483  5
  best valid F1               0.5340      0.5926     0.1442  5
  test BA                     0.5040      0.5000     0.0180  5
  test F1                     0.2314      0.1558     0.2058  5
  test sensitivity            0.2215      0.0923     0.2444  5
  test specificity            0.7865      0.9326     0.2527  5
  test precision              0.4424      0.4348     0.0477  4
  test loss                   1.1003      0.8533     0.4468  5
  FPR (FP/(FP+TN))            0.2135      0.0674     0.2527  5
  FNR (FN/(FN+TP))            0.7785      0.9077     0.2444  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6069      0.6111     0.0943  5
  max valid BA                0.6403      0.6389     0.1094  5
  best valid F1               0.5246      0.5316     0.1450  5
  test BA                     0.5903      0.5069     0.1206  5
  test F1                     0.4164      0.3514     0.2146  5
  test sensitivity            0.4222      0.3611     0.2667  5
  test specificity            0.7583      0.6667     0.1517  5
  test precision              0.4637      0.3421     0.1995  5
  test loss                   0.6424      0.6760     0.0959  5
  FPR (FP/(FP+TN))            0.2417      0.3333     0.1517  5
  FNR (FN/(FN+TP))            0.5778      0.6389     0.2667  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5912      0.5882     0.0524  5
  max valid BA                0.6147      0.6176     0.0395  5
  best valid F1               0.4865      0.4762     0.0566  5
  test BA                     0.5412      0.5441     0.0192  5
  test F1                     0.3141      0.2609     0.0891  5
  test sensitivity            0.2706      0.1765     0.1354  5
  test specificity            0.8118      0.8529     0.1073  5
  test precision              0.4264      0.4286     0.0468  5
  test loss                   0.6549      0.6538     0.0237  5
  FPR (FP/(FP+TN))            0.1882      0.1471     0.1073  5
  FNR (FN/(FN+TP))            0.7294      0.8235     0.1354  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                         
CRAL-TRIO                0.630         0.483    0.527       4.0              0.365         0.408     5.0               0.449          0.453              0.432         0.496
GLTP                     0.605         0.521    0.514       2.0              0.511         0.509     3.0               0.523          0.528              0.524         0.505
IP_trans                 0.722         0.681    0.522       3.0              0.677         0.534     2.4               0.590          0.493              0.669         0.526
LBP_BPI_CETP             0.719         0.798    0.551       2.0              0.798         0.518     1.6               0.784          0.448              0.821         0.516
START                    0.576         0.508    0.500       3.0              0.475         0.481     4.0               0.535          0.580              0.519         0.548
lipocalin                0.565         0.334    0.498       5.0              0.252         0.499     2.2               0.647          0.702              0.623         0.586
scp2                     0.651         0.488    0.562       2.8              0.592         0.563     2.6               0.649          0.493              0.577         0.517

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.545               0.499                  0.066                     0.151
net_AUC           0.525               0.538                  0.071                     0.024

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.524               0.493                  0.065                     0.185
net_AUC_prot           0.502               0.502                  0.086                     0.049

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.597               0.581                  0.085                     0.109
net_AUC_lipid           0.528               0.528                  0.117                     0.089

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.595               0.575                  0.056                     0.126
net_AUC_pair           0.528               0.525                  0.075                     0.031

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.479      0.524     0.474
10     0.545  0.584      0.524     0.580
49     0.545  0.542      0.524     0.538
51     0.545  0.551      0.524     0.551
120    0.545  0.525      0.524     0.502

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.619         0.667      0.048          0.655              0.689           0.034
10        0.619         0.652      0.032          0.655              0.680           0.025
49        0.619         0.649      0.030          0.655              0.682           0.027
51        0.619         0.644      0.025          0.655              0.681           0.026
120       0.619         0.643      0.024          0.655              0.686           0.031

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.483  0.527      0.365     0.408     0.539         0.568      0.028          0.614              0.644           0.030
GLTP          0.521  0.514      0.511     0.509     0.542         0.548      0.005          0.565              0.581           0.016
IP_trans      0.681  0.522      0.677     0.534     0.681         0.706      0.026          0.692              0.726           0.034
LBP_BPI_CETP  0.798  0.551      0.798     0.518     0.798         0.801      0.003          0.801              0.811           0.010
START         0.508  0.500      0.475     0.481     0.536         0.586      0.050          0.604              0.643           0.038
lipocalin     0.334  0.498      0.252     0.499     0.666         0.662     -0.004          0.672              0.719           0.047
scp2          0.488  0.562      0.592     0.563     0.572         0.631      0.059          0.636              0.680           0.044

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.545               0.499                  0.066                     0.151
net               0.525               0.538                  0.071                     0.024
fit_chem          0.619               0.580                  0.052                     0.100
fit_chem_net      0.643               0.630                  0.055                     0.089
increment         0.024               0.010                  0.040                     0.024

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.524               0.493                  0.065                     0.185
net_prot               0.502               0.502                  0.086                     0.049
fit_chem_prot          0.655               0.658                  0.053                     0.077
fit_chem_net_prot      0.686               0.664                  0.049                     0.074
increment_prot         0.031               0.018                  0.037                     0.014
```
