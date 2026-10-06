# ge_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28_rotneg

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28_rotneg'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.7642      0.2754      0.9909      0.4371      0.8955      0.3000
groups_GLTP            5      0.8640      0.3120      0.9923      0.1182      0.9846      0.1769
groups_IP_trans        5      0.1217      0.8809      0.9906      0.4832      0.3250      0.9447
groups_LBP_BPI_CETP    5      0.6435      0.3106      0.9943      0.4825      0.6917      0.4894
groups_ML              5      0.8000      0.1600      0.7778      0.3140      0.8400      0.2000
groups_OSBP            5      0.6667      0.1000      0.9909      0.2585      1.0000      0.3667
groups_START           5      0.6123      0.5685      0.9925      0.4290      0.6844      0.5820
groups_lipocalin       5      0.5056      0.6583      0.9920      0.2936      0.6167      0.7194
groups_scp2            5      0.6235      0.3765      0.7045      0.5047      0.6706      0.3882
ALL                   45      0.6224      0.4047      0.9362      0.3690      0.7454      0.4630

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5704      0.5683     0.0639  45
max valid BA                0.6042      0.6029     0.0794  45
best valid F1               0.5898      0.5500     0.0877  45
test BA                     0.5135      0.5000     0.0999  45
test AUC                    0.4699      0.4992     0.1396  45
test AUC in-protein         0.4935      0.4836     0.1389  42
  (proteins averaged)       2.6000      3.0000     1.3718  45
test AUC in-protein (pairs)      0.4551      0.4691     0.1452  45
  (proteins contributing)      3.0222      3.0000     1.7900  45
test F1                     0.4461      0.5000     0.1918  45
test sensitivity            0.6224      0.6308     0.3416  45
test specificity            0.4047      0.4468     0.3388  45
test precision              0.4065      0.3369     0.1547  44
test loss                   0.9837      0.8662     0.2925  45
FPR (FP/(FP+TN))            0.5953      0.5532     0.3388  45
FNR (FN/(FN+TP))            0.3776      0.3692     0.3416  45

=== abs(sensitivity-specificity) gap: mean=0.5831 median=0.6568 n=45 ===
sensitivity std across seeds (by group): mean=0.2620 median=0.2639 n=9
specificity std across seeds (by group): mean=0.2394 median=0.2210 n=9

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5570      0.5416     0.0528  5
  max valid BA                0.5978      0.6004     0.0390  5
  best valid F1               0.7067      0.7093     0.0169  5
  test BA                     0.5198      0.5213     0.0448  5
  test AUC                    0.5521      0.5639     0.0731  5
  test AUC in-protein         0.4464      0.4728     0.1006  5
    (proteins averaged)       4.0000      4.0000     0.0000  5
  test AUC in-protein (pairs)      0.5618      0.5692     0.0976  5
    (proteins contributing)      4.4000      4.0000     0.5477  5
  test F1                     0.6141      0.6857     0.1168  5
  test sensitivity            0.7642      0.8955     0.2639  5
  test specificity            0.2754      0.2131     0.2139  5
  test precision              0.5314      0.5429     0.0354  5
  test loss                   1.0196      1.0264     0.2076  5
  FPR (FP/(FP+TN))            0.7246      0.7869     0.2139  5
  FNR (FN/(FN+TP))            0.2358      0.1045     0.2639  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5385     0.0520  5
  max valid BA                0.5808      0.5769     0.0583  5
  best valid F1               0.7023      0.7027     0.0274  5
  test BA                     0.5880      0.5800     0.1064  5
  test AUC                    0.4627      0.4960     0.1129  5
  test AUC in-protein         0.4508      0.4306     0.0837  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4522      0.4690     0.0907  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.6604      0.7042     0.1472  5
  test sensitivity            0.8640      1.0000     0.2823  5
  test specificity            0.3120      0.2800     0.2488  5
  test precision              0.5530      0.5435     0.0757  5
  test loss                   0.9331      0.8607     0.1990  5
  FPR (FP/(FP+TN))            0.6880      0.7200     0.2488  5
  FNR (FN/(FN+TP))            0.1360      0.0000     0.2823  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5866      0.5824     0.0286  5
  max valid BA                0.6348      0.6144     0.0412  5
  best valid F1               0.5302      0.5161     0.0358  5
  test BA                     0.5013      0.4903     0.0467  5
  test AUC                    0.4353      0.4302     0.1069  5
  test AUC in-protein         0.5382      0.5338     0.0611  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.3959      0.4085     0.0877  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.1809      0.1667     0.0647  5
  test sensitivity            0.1217      0.1304     0.0364  5
  test specificity            0.8809      0.8936     0.0699  5
  test precision              0.3827      0.2857     0.2411  5
  test loss                   0.7720      0.7495     0.0499  5
  FPR (FP/(FP+TN))            0.1191      0.1064     0.0699  5
  FNR (FN/(FN+TP))            0.8783      0.8696     0.0364  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5556      0.5683     0.0380  5
  max valid BA                0.5905      0.5966     0.0454  5
  best valid F1               0.5324      0.5275     0.0235  5
  test BA                     0.4771      0.5000     0.0415  5
  test AUC                    0.5042      0.5208     0.0747  5
  test AUC in-protein         0.5788      0.5914     0.0422  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.5456      0.5890     0.0782  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4151      0.4068     0.0543  5
  test sensitivity            0.6435      0.5652     0.2094  5
  test specificity            0.3106      0.3617     0.1954  5
  test precision              0.3127      0.3286     0.0278  5
  test loss                   1.0370      1.1031     0.1721  5
  FPR (FP/(FP+TN))            0.6894      0.6383     0.1954  5
  FNR (FN/(FN+TP))            0.3565      0.4348     0.2094  5

groups_ML (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5200      0.5000     0.0274  5
  max valid BA                0.5200      0.5000     0.0274  5
  best valid F1               0.5053      0.5000     0.0118  5
  test BA                     0.4800      0.5000     0.0447  5
  test AUC                    0.4040      0.4000     0.0477  5
  test AUC in-protein         0.4040      0.4000     0.0477  5
    (proteins averaged)       1.0000      1.0000     0.0000  5
  test AUC in-protein (pairs)      0.4040      0.4000     0.0477  5
    (proteins contributing)      1.0000      1.0000     0.0000  5
  test F1                     0.4342      0.5000     0.1085  5
  test sensitivity            0.8000      1.0000     0.3464  5
  test specificity            0.1600      0.0000     0.3578  5
  test precision              0.3238      0.3333     0.0213  5
  test loss                   0.7827      0.7797     0.0567  5
  FPR (FP/(FP+TN))            0.8400      1.0000     0.3578  5
  FNR (FN/(FN+TP))            0.2000      0.0000     0.3464  5

groups_OSBP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6000      0.5833     0.0913  5
  max valid BA                0.6833      0.7500     0.1369  5
  best valid F1               0.6258      0.6667     0.1013  5
  test BA                     0.3833      0.5000     0.1624  5
  test AUC                    0.2778      0.3333     0.2664  5
  test AUC in-protein         0.2500      0.2500     0.3536  2
    (proteins averaged)       0.4000      0.0000     0.5477  5
  test AUC in-protein (pairs)      0.2917      0.3333     0.2857  5
    (proteins contributing)      1.6000      2.0000     0.5477  5
  test F1                     0.3400      0.5000     0.2302  5
  test sensitivity            0.6667      1.0000     0.4714  5
  test specificity            0.1000      0.0000     0.2236  5
  test precision              0.2286      0.3333     0.1521  5
  test loss                   1.5146      1.6802     0.3941  5
  FPR (FP/(FP+TN))            0.9000      1.0000     0.2236  5
  FNR (FN/(FN+TP))            0.3333      0.0000     0.4714  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6092      0.6175     0.0218  5
  max valid BA                0.6332      0.6312     0.0277  5
  best valid F1               0.6223      0.6294     0.0185  5
  test BA                     0.5904      0.5889     0.0157  5
  test AUC                    0.5752      0.5907     0.0430  5
  test AUC in-protein         0.4381      0.4422     0.0263  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4697      0.5027     0.0783  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.5506      0.5641     0.0485  5
  test sensitivity            0.6123      0.6308     0.1382  5
  test specificity            0.5685      0.5618     0.1425  5
  test precision              0.5151      0.5125     0.0316  5
  test loss                   0.9488      0.8914     0.1576  5
  FPR (FP/(FP+TN))            0.4315      0.4382     0.1425  5
  FNR (FN/(FN+TP))            0.3877      0.3692     0.1382  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6292      0.5694     0.1095  5
  max valid BA                0.6681      0.6181     0.0815  5
  best valid F1               0.5741      0.5400     0.0958  5
  test BA                     0.5819      0.5625     0.1373  5
  test AUC                    0.5688      0.5737     0.0955  5
  test AUC in-protein         0.7246      0.6701     0.0948  5
    (proteins averaged)       5.0000      5.0000     0.0000  5
  test AUC in-protein (pairs)      0.5146      0.5189     0.0571  5
    (proteins contributing)      7.2000      7.0000     0.4472  5
  test F1                     0.4752      0.4375     0.1406  5
  test sensitivity            0.5056      0.4722     0.1169  5
  test specificity            0.6583      0.7361     0.2210  5
  test precision              0.4683      0.4242     0.1854  5
  test loss                   0.8286      0.8139     0.2481  5
  FPR (FP/(FP+TN))            0.3417      0.2639     0.2210  5
  FNR (FN/(FN+TP))            0.4944      0.5278     0.1169  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5265      0.5147     0.0366  5
  max valid BA                0.5294      0.5147     0.0429  5
  best valid F1               0.5094      0.5075     0.0105  5
  test BA                     0.5000      0.5000     0.0104  5
  test AUC                    0.4488      0.4542     0.0737  5
  test AUC in-protein         0.4643      0.4561     0.0621  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4603      0.4808     0.1917  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.3444      0.5000     0.2270  5
  test sensitivity            0.6235      0.9412     0.4932  5
  test specificity            0.3765      0.0882     0.4821  5
  test precision              0.3268      0.3333     0.0182  4
  test loss                   1.0168      0.9528     0.2850  5
  FPR (FP/(FP+TN))            0.6235      0.9118     0.4821  5
  FNR (FN/(FN+TP))            0.3765      0.0588     0.4932  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                         
CRAL-TRIO                0.630         0.483    0.533       4.0              0.365         0.487     5.0               0.449          0.448              0.432         0.547
GLTP                     0.605         0.521    0.529       2.0              0.511         0.519     3.0               0.523          0.550              0.524         0.550
IP_trans                 0.722         0.681    0.550       3.0              0.677         0.577     2.4               0.590          0.692              0.669         0.547
LBP_BPI_CETP             0.719         0.798    0.573       2.0              0.798         0.548     1.6               0.784          0.500              0.821         0.515
START                    0.576         0.508    0.581       3.0              0.475         0.500     4.0               0.535          0.502              0.519         0.634
lipocalin                0.565         0.334    0.577       5.0              0.252         0.657     2.2               0.647          0.589              0.623         0.482
scp2                     0.651         0.488    0.394       2.8              0.592         0.473     2.6               0.649          0.510              0.577         0.530

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.545               0.499                  0.066                     0.151
net_AUC           0.534               0.541                  0.100                     0.065

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.524               0.493                  0.065                     0.185
net_AUC_prot           0.537               0.520                  0.098                     0.064

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.597               0.581                  0.085                     0.109
net_AUC_lipid           0.542               0.524                  0.126                     0.080

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.595               0.575                  0.056                     0.126
net_AUC_pair           0.543               0.544                  0.117                     0.047

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.469      0.524     0.475
10     0.545  0.532      0.524     0.527
49     0.545  0.510      0.524     0.524
51     0.545  0.520      0.524     0.534
120    0.545  0.534      0.524     0.537

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.619         0.653      0.034          0.655              0.685           0.030
10        0.619         0.646      0.027          0.655              0.678           0.023
49        0.619         0.652      0.033          0.655              0.689           0.034
51        0.619         0.663      0.044          0.655              0.695           0.040
120       0.619         0.669      0.050          0.655              0.704           0.049

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.483  0.533      0.365     0.487     0.539         0.577      0.038          0.614              0.672           0.058
GLTP          0.521  0.529      0.511     0.519     0.542         0.647      0.105          0.565              0.673           0.108
IP_trans      0.681  0.550      0.677     0.577     0.681         0.710      0.030          0.692              0.732           0.040
LBP_BPI_CETP  0.798  0.573      0.798     0.548     0.798         0.811      0.013          0.801              0.819           0.018
START         0.508  0.581      0.475     0.500     0.536         0.633      0.097          0.604              0.643           0.039
lipocalin     0.334  0.577      0.252     0.657     0.666         0.667      0.001          0.672              0.700           0.029
scp2          0.488  0.394      0.592     0.473     0.572         0.640      0.068          0.636              0.692           0.055

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.545               0.499                  0.066                     0.151
net               0.534               0.541                  0.100                     0.065
fit_chem          0.619               0.580                  0.052                     0.100
fit_chem_net      0.669               0.663                  0.075                     0.074
increment         0.050               0.035                  0.056                     0.041

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.524               0.493                  0.065                     0.185
net_prot               0.537               0.520                  0.098                     0.064
fit_chem_prot          0.655               0.658                  0.053                     0.077
fit_chem_net_prot      0.704               0.697                  0.068                     0.057
increment_prot         0.049               0.038                  0.047                     0.029
```
