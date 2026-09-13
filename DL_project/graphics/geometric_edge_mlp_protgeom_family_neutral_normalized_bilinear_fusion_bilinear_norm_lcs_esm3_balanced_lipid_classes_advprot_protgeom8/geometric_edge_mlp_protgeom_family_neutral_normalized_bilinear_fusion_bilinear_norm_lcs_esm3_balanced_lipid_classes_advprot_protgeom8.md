# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_protgeom8

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_protgeom8'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.8473      0.1869      0.6701      0.5471      0.7548      0.3220
groups_choline            5      0.7477      0.4188      0.4487      0.6249      0.6571      0.5426
groups_phosphorus_free    5      0.2839      0.6939      0.5805      0.5488      0.4067      0.7347
groups_sphingolipids      5      0.4545      0.4585      0.5961      0.4371      0.6242      0.5400
ALL                      20      0.5834      0.4395      0.5738      0.5394      0.6107      0.5348

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5621      0.5419     0.0467  20
max valid BA                0.5728      0.5535     0.0459  20
best valid F1               0.5670      0.5591     0.0455  20
test BA                     0.5114      0.5021     0.0664  20
test AUC                    0.5282      0.5163     0.0688  20
test AUC in-protein         0.6149      0.6019     0.1314  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5468      0.5622     0.1330  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.4221      0.4913     0.1597  20
test sensitivity            0.5834      0.6622     0.3038  20
test specificity            0.4395      0.4664     0.2537  20
test precision              0.3623      0.3635     0.0868  20
test loss                   0.7003      0.6935     0.0199  20
FPR (FP/(FP+TN))            0.5605      0.5336     0.2537  20
FNR (FN/(FN+TP))            0.4166      0.3378     0.3038  20

=== abs(sensitivity-specificity) gap: mean=0.4508 median=0.3775 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5268      0.5296     0.0128  5
  max valid BA                0.5384      0.5443     0.0137  5
  best valid F1               0.5151      0.5133     0.0046  5
  test BA                     0.5171      0.5115     0.0271  5
  test AUC                    0.5151      0.5170     0.0247  5
  test AUC in-protein         0.5303      0.5260     0.0620  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.5055      0.5075     0.0555  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.4902      0.4972     0.0127  5
  test sensitivity            0.8473      0.8925     0.1467  5
  test specificity            0.1869      0.0984     0.1979  5
  test precision              0.3502      0.3426     0.0231  5
  test loss                   0.7247      0.7272     0.0273  5
  FPR (FP/(FP+TN))            0.8131      0.9016     0.1979  5
  FNR (FN/(FN+TP))            0.1527      0.1075     0.1467  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5870      0.5972     0.0571  5
  max valid BA                0.5999      0.6228     0.0586  5
  best valid F1               0.5562      0.5589     0.0314  5
  test BA                     0.5833      0.5730     0.0311  5
  test AUC                    0.6039      0.6109     0.0401  5
  test AUC in-protein         0.6335      0.6164     0.0491  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.6027      0.5878     0.0646  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.5322      0.5354     0.0260  5
  test sensitivity            0.7477      0.6847     0.1143  5
  test specificity            0.4188      0.4703     0.1438  5
  test precision              0.4173      0.4138     0.0263  5
  test loss                   0.6921      0.6916     0.0016  5
  FPR (FP/(FP+TN))            0.5812      0.5297     0.1438  5
  FNR (FN/(FN+TP))            0.2523      0.3153     0.1143  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5616      0.5442     0.0492  5
  max valid BA                0.5707      0.5554     0.0431  5
  best valid F1               0.5672      0.5660     0.0193  5
  test BA                     0.4889      0.4651     0.0692  5
  test AUC                    0.5043      0.5049     0.0556  5
  test AUC in-protein         0.7700      0.7500     0.1556  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.6138      0.6522     0.1497  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.2552      0.2128     0.2268  5
  test sensitivity            0.2839      0.1613     0.3164  5
  test specificity            0.6939      0.7755     0.2193  5
  test precision              0.2852      0.3125     0.1339  5
  test loss                   0.6868      0.6843     0.0052  5
  FPR (FP/(FP+TN))            0.3061      0.2245     0.2193  5
  FNR (FN/(FN+TP))            0.7161      0.8387     0.3164  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5729      0.5727     0.0450  5
  max valid BA                0.5821      0.5860     0.0450  5
  best valid F1               0.6296      0.6286     0.0075  5
  test BA                     0.4565      0.4893     0.0594  5
  test AUC                    0.4897      0.4974     0.0851  5
  test AUC in-protein         0.5260      0.5098     0.0466  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4654      0.3930     0.1856  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4106      0.3571     0.1140  5
  test sensitivity            0.4545      0.3636     0.2237  5
  test specificity            0.4585      0.4634     0.1900  5
  test precision              0.3965      0.4348     0.0611  5
  test loss                   0.6977      0.6960     0.0061  5
  FPR (FP/(FP+TN))            0.5415      0.5366     0.1900  5
  FNR (FN/(FN+TP))            0.5455      0.6364     0.2237  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.511      11.6              0.530         0.492     5.4               0.501          0.480              0.501         0.504
choline                     0.687         0.646    0.453       9.4              0.696         0.442     1.8               0.565          0.458              0.622         0.441
phosphorus_free             0.396         0.499    0.505       1.2              0.739         0.547     5.4               0.514          0.555              0.484         0.540
sphingolipids               0.599         0.543    0.467       1.6              0.496         0.468     3.2               0.537          0.455              0.490         0.439

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.484               0.507                  0.074                     0.028

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.481               0.482                  0.135                     0.045

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.487               0.476                  0.070                     0.047

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.481               0.496                  0.067                     0.050

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.542  0.506      0.602     0.521
10     0.542  0.514      0.602     0.519
49     0.542  0.515      0.602     0.504
51     0.542  0.525      0.602     0.518
120    0.542  0.484      0.602     0.481

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.557         0.587      0.030          0.881              0.885           0.004
10        0.557         0.577      0.019          0.881              0.887           0.006
49        0.557         0.580      0.022          0.881              0.886           0.004
51        0.557         0.579      0.022          0.881              0.888           0.007
120       0.557         0.583      0.026          0.881              0.885           0.003

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.495  0.511      0.530     0.492     0.512         0.527      0.015          0.889              0.888          -0.000
choline          0.646  0.453      0.696     0.442     0.646         0.659      0.013          0.867              0.868           0.002
phosphorus_free  0.499  0.505      0.739     0.547     0.536         0.551      0.015          0.967              0.967          -0.001
sphingolipids    0.526  0.467      0.496     0.468     0.535         0.596      0.061          0.802              0.815           0.013

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.542               0.514                  0.038                     0.071
net               0.484               0.507                  0.074                     0.028
fit_chem          0.557               0.533                  0.028                     0.060
fit_chem_net      0.583               0.553                  0.036                     0.058
increment         0.026               0.015                  0.038                     0.023

=== the same rows ranked INSIDE each protein, epoch 120 ===
121 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.602               0.553                  0.039                     0.120
net_prot               0.481               0.482                  0.135                     0.045
fit_chem_prot          0.881               0.871                  0.022                     0.068
fit_chem_net_prot      0.885               0.872                  0.019                     0.063
increment_prot         0.003               0.000                  0.012                     0.006
```
