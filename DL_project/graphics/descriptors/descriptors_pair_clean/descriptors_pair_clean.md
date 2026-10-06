# descriptors_pair_clean

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_pair_clean'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.2716      0.7574      0.5063      0.6023      0.2687      0.8065
groups_GLTP            5      0.6000      0.6400      0.5243      0.5436      0.7154      0.7692
groups_IP_trans        5      0.5043      0.5447      0.5603      0.5322      0.6750      0.6213
groups_LBP_BPI_CETP    5      0.8000      0.4851      0.3753      0.6572      0.7583      0.5787
groups_START           5      0.4677      0.5011      0.4887      0.6212      0.4813      0.5910
groups_lipocalin       5      0.7500      0.4583      0.5621      0.4789      0.7833      0.5333
groups_scp2            5      0.5176      0.5824      0.5157      0.5727      0.6588      0.6706
ALL                   35      0.5588      0.5670      0.5047      0.5726      0.6201      0.6529

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6124      0.6029     0.0893  35
max valid BA                0.6365      0.6609     0.0905  35
best valid F1               0.5676      0.5833     0.1338  35
test BA                     0.5629      0.5527     0.0885  35
test AUC                    0.5638      0.5421     0.1082  35
test AUC in-protein         0.5856      0.5964     0.1356  35
  (proteins averaged)       3.1429      3.0000     1.0042  35
test AUC in-protein (pairs)      0.5712      0.5612     0.1003  35
  (proteins contributing)      3.5143      3.0000     1.7213  35
test F1                     0.4501      0.4667     0.1725  35
test sensitivity            0.5588      0.4800     0.3125  35
test specificity            0.5670      0.5588     0.2467  35
test precision              0.4598      0.4186     0.1660  35
test loss                   0.7070      0.7001     0.0525  35
FPR (FP/(FP+TN))            0.4330      0.4412     0.2467  35
FNR (FN/(FN+TP))            0.4412      0.5200     0.3125  35

=== abs(sensitivity-specificity) gap: mean=0.4602 median=0.4118 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5226      0.5278     0.0198  5
  max valid BA                0.5376      0.5373     0.0138  5
  best valid F1               0.4516      0.5185     0.2116  5
  test BA                     0.5145      0.5291     0.0459  5
  test AUC                    0.5563      0.5705     0.0356  5
  test AUC in-protein         0.5207      0.5652     0.1237  5
    (proteins averaged)       4.0000      4.0000     0.0000  5
  test AUC in-protein (pairs)      0.5902      0.6193     0.0675  5
    (proteins contributing)      4.4000      4.0000     0.5477  5
  test F1                     0.2789      0.1839     0.2368  5
  test sensitivity            0.2716      0.1194     0.3751  5
  test specificity            0.7574      0.8689     0.3496  5
  test precision              0.6150      0.5478     0.2439  5
  test loss                   0.7448      0.7368     0.0381  5
  FPR (FP/(FP+TN))            0.2426      0.1311     0.3496  5
  FNR (FN/(FN+TP))            0.7284      0.8806     0.3751  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7077      0.6538     0.0956  5
  max valid BA                0.7423      0.6923     0.0788  5
  best valid F1               0.7379      0.7241     0.0977  5
  test BA                     0.6200      0.6600     0.0678  5
  test AUC                    0.6198      0.6272     0.0667  5
  test AUC in-protein         0.6152      0.5964     0.0794  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.5632      0.5382     0.1063  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.6025      0.5854     0.0803  5
  test sensitivity            0.6000      0.4800     0.2078  5
  test specificity            0.6400      0.6800     0.2332  5
  test precision              0.6534      0.6000     0.1173  5
  test loss                   0.6846      0.6834     0.0057  5
  FPR (FP/(FP+TN))            0.3600      0.3200     0.2332  5
  FNR (FN/(FN+TP))            0.4000      0.5200     0.2078  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6166      0.6015     0.0438  5
  max valid BA                0.6481      0.6507     0.0641  5
  best valid F1               0.5635      0.5769     0.0660  5
  test BA                     0.5245      0.5278     0.0417  5
  test AUC                    0.5071      0.5162     0.0355  5
  test AUC in-protein         0.5879      0.5943     0.0799  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5245      0.5623     0.0881  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.3982      0.4444     0.0761  5
  test sensitivity            0.5043      0.6087     0.2333  5
  test specificity            0.5447      0.5106     0.2805  5
  test precision              0.3744      0.3500     0.0745  5
  test loss                   0.6954      0.6973     0.0172  5
  FPR (FP/(FP+TN))            0.4553      0.4894     0.2805  5
  FNR (FN/(FN+TP))            0.4957      0.3913     0.2333  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6598      0.6609     0.0768  5
  max valid BA                0.6685      0.6609     0.0700  5
  best valid F1               0.5958      0.5769     0.0652  5
  test BA                     0.6426      0.6115     0.0974  5
  test AUC                    0.6485      0.6549     0.0981  5
  test AUC in-protein         0.6557      0.6826     0.1040  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.6472      0.6679     0.0962  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5607      0.5231     0.0947  5
  test sensitivity            0.8000      0.8696     0.2007  5
  test specificity            0.4851      0.4681     0.2333  5
  test precision              0.4467      0.4167     0.0860  5
  test loss                   0.6767      0.6803     0.0291  5
  FPR (FP/(FP+TN))            0.5149      0.5319     0.2333  5
  FNR (FN/(FN+TP))            0.2000      0.1304     0.2007  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5242      0.5295     0.0160  5
  max valid BA                0.5361      0.5295     0.0212  5
  best valid F1               0.4977      0.4780     0.0584  5
  test BA                     0.4844      0.4936     0.0398  5
  test AUC                    0.4471      0.4479     0.0075  5
  test AUC in-protein         0.5350      0.5169     0.0593  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4794      0.4953     0.0424  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.4085      0.3902     0.1113  5
  test sensitivity            0.4677      0.3692     0.3006  5
  test specificity            0.5011      0.5955     0.2836  5
  test precision              0.4035      0.4138     0.0513  5
  test loss                   0.7604      0.7072     0.1120  5
  FPR (FP/(FP+TN))            0.4989      0.4045     0.2836  5
  FNR (FN/(FN+TP))            0.5323      0.6308     0.3006  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6292      0.6944     0.1143  5
  max valid BA                0.6583      0.6944     0.0860  5
  best valid F1               0.5629      0.6207     0.1310  5
  test BA                     0.6042      0.6528     0.1087  5
  test AUC                    0.5989      0.6489     0.1917  5
  test AUC in-protein         0.6160      0.7247     0.2964  5
    (proteins averaged)       5.0000      5.0000     0.0000  5
  test AUC in-protein (pairs)      0.5857      0.5769     0.1117  5
    (proteins contributing)      7.2000      7.0000     0.4472  5
  test F1                     0.4755      0.5862     0.2444  5
  test sensitivity            0.7500      0.9444     0.4106  5
  test specificity            0.4583      0.3611     0.2008  5
  test precision              0.3548      0.4217     0.1638  5
  test loss                   0.6929      0.7033     0.0205  5
  FPR (FP/(FP+TN))            0.5417      0.6389     0.2008  5
  FNR (FN/(FN+TP))            0.2500      0.0556     0.4106  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6265      0.6324     0.0494  5
  max valid BA                0.6647      0.6618     0.0669  5
  best valid F1               0.5639      0.5714     0.0922  5
  test BA                     0.5500      0.5000     0.0916  5
  test AUC                    0.5690      0.5208     0.1023  5
  test AUC in-protein         0.5687      0.5997     0.0940  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.6082      0.5563     0.1242  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.4260      0.3684     0.1243  5
  test sensitivity            0.5176      0.4118     0.2293  5
  test specificity            0.5824      0.5588     0.0732  5
  test precision              0.3707      0.3333     0.0681  5
  test loss                   0.6941      0.6935     0.0104  5
  FPR (FP/(FP+TN))            0.4176      0.4412     0.0732  5
  FNR (FN/(FN+TP))            0.4824      0.5882     0.2293  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (aromatic_contact,aromatic_contact_min,buriedness_match,elongation_shape_match,flatness_shape_match,hbond_match,hbond_match_min,hydropathy_rim_match,tail_elongation_fit,volume_fit), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.305         0.540    0.507              0.461         0.508
GLTP                     0.419         0.743    0.671              0.776         0.685
IP_trans                 0.411         0.503    0.483              0.491         0.445
LBP_BPI_CETP             0.377         0.438    0.490              0.458         0.511
START                    0.341         0.438    0.452              0.489         0.541
lipocalin                0.387         0.314    0.464              0.414         0.475
scp2                     0.363         0.527    0.600              0.497         0.475

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.500               0.470                  0.048                     0.131
net_AUC           0.524               0.549                  0.114                     0.081

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.512               0.473                  0.056                     0.120
net_AUC_pair           0.520               0.497                  0.105                     0.079

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
       chem    net  chem_pair  net_pair
epoch                                  
1       0.5  0.590      0.512     0.589
10      0.5  0.555      0.512     0.541
49      0.5  0.542      0.512     0.531
51      0.5  0.525      0.512     0.521
120     0.5  0.524      0.512     0.520

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1           0.6         0.677      0.077
10          0.6         0.650      0.050
49          0.6         0.655      0.056
51          0.6         0.649      0.049
120         0.6         0.660      0.060

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.540  0.507      0.461     0.508     0.540         0.553      0.013
GLTP          0.743  0.671      0.776     0.685     0.743         0.809      0.066
IP_trans      0.503  0.483      0.491     0.445     0.559         0.649      0.090
LBP_BPI_CETP  0.438  0.490      0.458     0.511     0.562         0.658      0.096
START         0.438  0.452      0.489     0.541     0.562         0.592      0.030
lipocalin     0.314  0.464      0.414     0.475     0.686         0.747      0.061
scp2          0.527  0.600      0.497     0.475     0.547         0.611      0.064

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.500               0.470                  0.048                     0.131
net               0.524               0.549                  0.114                     0.081
fit_chem          0.600               0.576                  0.042                     0.080
fit_chem_net      0.660               0.642                  0.055                     0.090
increment         0.060               0.050                  0.056                     0.030

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.512               0.473                  0.056                     0.120
net_pair       0.520               0.497                  0.105                     0.079
```
