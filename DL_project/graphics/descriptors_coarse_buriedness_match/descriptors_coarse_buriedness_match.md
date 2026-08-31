# descriptors_coarse_buriedness_match

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_coarse_buriedness_match'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6388      0.4984      0.6023      0.4620      0.6269      0.5129
groups_GLTP            5      0.5920      0.4160      0.5898      0.5081      0.6615      0.5000
groups_IP_trans        5      0.6522      0.5702      0.6292      0.5096      0.6833      0.5915
groups_LBP_BPI_CETP    5      0.7913      0.6511      0.6737      0.4701      0.8583      0.6596
groups_START           5      0.4123      0.6697      0.4894      0.5751      0.3719      0.7034
groups_lipocalin       5      0.6056      0.5750      0.5217      0.5774      0.5778      0.5861
groups_scp2            5      0.5294      0.5824      0.5811      0.5034      0.5412      0.6647
ALL                   35      0.6031      0.5661      0.5839      0.5151      0.6173      0.6026

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6099      0.5862     0.0856  35
max valid BA                0.6276      0.6026     0.0854  35
best valid F1               0.5797      0.6038     0.1294  35
test BA                     0.5846      0.5850     0.0888  35
test F1                     0.5076      0.5370     0.1470  35
test sensitivity            0.6031      0.6389     0.2575  35
test specificity            0.5661      0.5745     0.2386  35
test precision              0.4944      0.4936     0.1145  34
test loss                   0.6906      0.6904     0.0364  35
FPR (FP/(FP+TN))            0.4339      0.4255     0.2386  35
FNR (FN/(FN+TP))            0.3969      0.3611     0.2575  35

=== abs(sensitivity-specificity) gap: mean=0.4038 median=0.3750 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5699      0.5628     0.0245  5
  max valid BA                0.5884      0.5906     0.0305  5
  best valid F1               0.6700      0.6667     0.0235  5
  test BA                     0.5686      0.5607     0.0473  5
  test F1                     0.6042      0.6331     0.0627  5
  test sensitivity            0.6388      0.6418     0.1487  5
  test specificity            0.4984      0.5410     0.1976  5
  test precision              0.5907      0.6042     0.0474  5
  test loss                   0.6863      0.6884     0.0077  5
  FPR (FP/(FP+TN))            0.5016      0.4590     0.1976  5
  FNR (FN/(FN+TP))            0.3612      0.3582     0.1487  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5808      0.5769     0.0459  5
  max valid BA                0.6077      0.6154     0.0399  5
  best valid F1               0.6593      0.6774     0.0668  5
  test BA                     0.5040      0.5000     0.0385  5
  test F1                     0.5045      0.5862     0.1838  5
  test sensitivity            0.5920      0.6800     0.3267  5
  test specificity            0.4160      0.3600     0.2662  5
  test precision              0.4886      0.5000     0.0396  5
  test loss                   0.6998      0.6945     0.0154  5
  FPR (FP/(FP+TN))            0.5840      0.6400     0.2662  5
  FNR (FN/(FN+TP))            0.4080      0.3200     0.3267  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6374      0.6077     0.0761  5
  max valid BA                0.6565      0.6507     0.0668  5
  best valid F1               0.5729      0.5797     0.0719  5
  test BA                     0.6112      0.6124     0.0514  5
  test F1                     0.5183      0.5263     0.0244  5
  test sensitivity            0.6522      0.5652     0.1627  5
  test specificity            0.5702      0.6596     0.2551  5
  test precision              0.4591      0.4483     0.0977  5
  test loss                   0.6784      0.6669     0.0179  5
  FPR (FP/(FP+TN))            0.4298      0.3404     0.2551  5
  FNR (FN/(FN+TP))            0.3478      0.4348     0.1627  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7590      0.7788     0.0572  5
  max valid BA                0.7674      0.7788     0.0604  5
  best valid F1               0.6972      0.7037     0.0641  5
  test BA                     0.7212      0.7003     0.0853  5
  test F1                     0.6368      0.6129     0.0869  5
  test sensitivity            0.7913      0.8261     0.2025  5
  test specificity            0.6511      0.6596     0.2489  5
  test precision              0.5719      0.5897     0.1481  5
  test loss                   0.6568      0.6453     0.0239  5
  FPR (FP/(FP+TN))            0.3489      0.3404     0.2489  5
  FNR (FN/(FN+TP))            0.2087      0.1739     0.2025  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5376      0.5461     0.0352  5
  max valid BA                0.5455      0.5532     0.0279  5
  best valid F1               0.4643      0.4865     0.1101  5
  test BA                     0.5410      0.5078     0.0712  5
  test F1                     0.4353      0.4314     0.0889  5
  test sensitivity            0.4123      0.3385     0.1597  5
  test specificity            0.6697      0.7079     0.2237  5
  test precision              0.5022      0.4348     0.1248  5
  test loss                   0.6943      0.6915     0.0147  5
  FPR (FP/(FP+TN))            0.3303      0.2921     0.2237  5
  FNR (FN/(FN+TP))            0.5877      0.6615     0.1597  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5819      0.5972     0.0534  5
  max valid BA                0.6069      0.5972     0.0803  5
  best valid F1               0.4714      0.5424     0.1826  5
  test BA                     0.5903      0.6181     0.0587  5
  test F1                     0.4228      0.4923     0.2403  5
  test sensitivity            0.6056      0.6389     0.4075  5
  test specificity            0.5750      0.4861     0.3228  5
  test precision              0.4360      0.4045     0.0779  4
  test loss                   0.7325      0.7056     0.0744  5
  FPR (FP/(FP+TN))            0.4250      0.5139     0.3228  5
  FNR (FN/(FN+TP))            0.3944      0.3611     0.4075  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6029      0.5735     0.0838  5
  max valid BA                0.6206      0.6618     0.0854  5
  best valid F1               0.5230      0.5957     0.1085  5
  test BA                     0.5559      0.6176     0.0938  5
  test F1                     0.4312      0.4444     0.1285  5
  test sensitivity            0.5294      0.3529     0.2728  5
  test specificity            0.5824      0.5588     0.1899  5
  test precision              0.4004      0.4167     0.1325  5
  test loss                   0.6859      0.6910     0.0187  5
  FPR (FP/(FP+TN))            0.4176      0.4412     0.1899  5
  FNR (FN/(FN+TP))            0.4706      0.6471     0.2728  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (aromatic_share,buriedness_match,chain,hbond,heavy,occupancy,polar_share,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.397         0.562    0.535              0.548         0.557
GLTP                     0.395         0.678    0.507              0.662         0.552
IP_trans                 0.441         0.488    0.646              0.483         0.583
LBP_BPI_CETP             0.414         0.671    0.739              0.662         0.768
START                    0.384         0.514    0.423              0.484         0.472
lipocalin                0.343         0.472    0.470              0.559         0.639
scp2                     0.349         0.407    0.494              0.515         0.528

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.542               0.514                  0.065                     0.102
net_AUC           0.545               0.542                  0.096                     0.110

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.559               0.518                  0.063                     0.076
net_AUC_pair           0.586               0.553                  0.078                     0.095

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.542  0.440      0.559     0.453
10     0.542  0.569      0.559     0.581
49     0.542  0.548      0.559     0.583
51     0.542  0.549      0.559     0.584
120    0.542  0.545      0.559     0.586

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.588         0.661      0.073
10        0.588         0.664      0.076
49        0.588         0.660      0.071
51        0.588         0.660      0.072
120       0.588         0.654      0.066

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.562  0.535      0.548     0.557     0.581         0.601      0.020
GLTP          0.678  0.507      0.662     0.552     0.678         0.702      0.024
IP_trans      0.488  0.646      0.483     0.583     0.518         0.638      0.120
LBP_BPI_CETP  0.671  0.739      0.662     0.768     0.671         0.784      0.114
START         0.514  0.423      0.484     0.472     0.519         0.586      0.067
lipocalin     0.472  0.470      0.559     0.639     0.556         0.626      0.070
scp2          0.407  0.494      0.515     0.528     0.593         0.640      0.047

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.542               0.514                  0.065                     0.102
net               0.545               0.542                  0.096                     0.110
fit_chem          0.588               0.568                  0.057                     0.066
fit_chem_net      0.654               0.643                  0.066                     0.068
increment         0.066               0.034                  0.061                     0.040

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.559               0.518                  0.063                     0.076
net_pair       0.586               0.553                  0.078                     0.095
```
