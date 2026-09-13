# descriptors_head_family_neutral_lipprop_lcs_protgeom8

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_head_family_neutral_lipprop_lcs_protgeom8'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.7462      0.5082      0.5674      0.6059      0.7742      0.5066
groups_choline            5      0.5009      0.5178      0.6964      0.4868      0.5857      0.4297
groups_phosphorus_free    5      0.3613      0.6449      0.4387      0.6059      0.4467      0.6490
groups_sphingolipids      5      0.6727      0.3659      0.5127      0.5136      0.6485      0.4400
ALL                      20      0.5703      0.5092      0.5538      0.5531      0.6138      0.5063

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5476      0.5327     0.0646  20
max valid BA                0.5600      0.5508     0.0676  20
best valid F1               0.5197      0.5271     0.0914  20
test BA                     0.5397      0.5268     0.0711  20
test AUC                    0.5427      0.5391     0.1351  20
test AUC in-protein         0.5057      0.4926     0.1827  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5072      0.5377     0.1295  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.4338      0.5197     0.1868  20
test sensitivity            0.5703      0.6828     0.3179  20
test specificity            0.5092      0.5164     0.2976  20
test precision              0.4195      0.4108     0.0743  18
test loss                   0.7297      0.7137     0.0856  20
FPR (FP/(FP+TN))            0.4908      0.4836     0.2976  20
FNR (FN/(FN+TP))            0.4297      0.3172     0.3179  20

=== abs(sensitivity-specificity) gap: mean=0.4902 median=0.3714 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6273      0.6444     0.0668  5
  max valid BA                0.6404      0.6526     0.0674  5
  best valid F1               0.5753      0.5839     0.0463  5
  test BA                     0.6272      0.6280     0.0288  5
  test AUC                    0.6845      0.6859     0.0223  5
  test AUC in-protein         0.5751      0.5772     0.0586  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.5766      0.5687     0.0422  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.5502      0.5469     0.0264  5
  test sensitivity            0.7462      0.7527     0.0377  5
  test specificity            0.5082      0.4973     0.0481  5
  test precision              0.4362      0.4408     0.0263  5
  test loss                   0.6730      0.6731     0.0141  5
  FPR (FP/(FP+TN))            0.4918      0.5027     0.0481  5
  FNR (FN/(FN+TP))            0.2538      0.2473     0.0377  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5029      0.5050     0.0430  5
  max valid BA                0.5077      0.5050     0.0477  5
  best valid F1               0.4650      0.5238     0.1045  5
  test BA                     0.5094      0.5000     0.0472  5
  test AUC                    0.4226      0.4652     0.1255  5
  test AUC in-protein         0.4310      0.3996     0.1430  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.4466      0.3998     0.1085  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.3353      0.3791     0.2302  5
  test sensitivity            0.5009      0.3604     0.4534  5
  test specificity            0.5178      0.7030     0.4127  5
  test precision              0.3513      0.3730     0.0648  4
  test loss                   0.8111      0.7570     0.1336  5
  FPR (FP/(FP+TN))            0.4822      0.2970     0.4127  5
  FNR (FN/(FN+TP))            0.4991      0.6396     0.4534  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5369      0.5367     0.0425  5
  max valid BA                0.5478      0.5585     0.0481  5
  best valid F1               0.4725      0.4722     0.0894  5
  test BA                     0.5031      0.4990     0.0322  5
  test AUC                    0.5167      0.5276     0.0555  5
  test AUC in-protein         0.5000      0.5000     0.3171  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.4646      0.4375     0.1105  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.3108      0.4000     0.2027  5
  test sensitivity            0.3613      0.3548     0.3293  5
  test specificity            0.6449      0.7551     0.3609  5
  test precision              0.4038      0.3835     0.0501  4
  test loss                   0.7189      0.7111     0.0411  5
  FPR (FP/(FP+TN))            0.3551      0.2449     0.3609  5
  FNR (FN/(FN+TP))            0.6387      0.6452     0.3293  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5233      0.5220     0.0198  5
  max valid BA                0.5442      0.5451     0.0239  5
  best valid F1               0.5659      0.6105     0.0745  5
  test BA                     0.5193      0.5251     0.0836  5
  test AUC                    0.5469      0.5506     0.1528  5
  test AUC in-protein         0.5167      0.4918     0.1444  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.5410      0.5838     0.1989  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5387      0.5747     0.0965  5
  test sensitivity            0.6727      0.6667     0.2282  5
  test specificity            0.3659      0.3902     0.2627  5
  test precision              0.4698      0.4630     0.0967  5
  test loss                   0.7161      0.7185     0.0484  5
  FPR (FP/(FP+TN))            0.6341      0.6098     0.2627  5
  FNR (FN/(FN+TP))            0.3273      0.3333     0.2282  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (aromatic_share,buriedness_q50,chain,depth_q10,hbond,heavy,hydropathy_core,hydropathy_rim,pocket_elongation,pocket_extent,pocket_flatness,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                      
anionic                     0.509         0.775    0.689              0.512         0.524
choline                     0.422         0.405    0.411              0.540         0.421
phosphorus_free             0.296         0.533    0.392              0.521         0.538
sphingolipids               0.367         0.275    0.329              0.446         0.419

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.497               0.485                  0.028                     0.213
net_AUC           0.455               0.413                  0.093                     0.160

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.505               0.520                  0.046                     0.041
net_AUC_pair           0.475               0.507                  0.091                     0.064

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.497  0.489      0.505     0.512
10     0.497  0.474      0.505     0.465
49     0.497  0.453      0.505     0.473
51     0.497  0.454      0.505     0.478
120    0.497  0.455      0.505     0.475

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.653         0.680      0.027
10        0.653         0.683      0.030
49        0.653         0.686      0.033
51        0.653         0.687      0.033
120       0.653         0.692      0.038

3. mean over seeds, epoch 120
                  chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                                  
anionic          0.775  0.689      0.512     0.524     0.775         0.778      0.003
choline          0.405  0.411      0.540     0.421     0.595         0.613      0.018
phosphorus_free  0.533  0.392      0.521     0.538     0.519         0.618      0.099
sphingolipids    0.275  0.329      0.446     0.419     0.725         0.758      0.033

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.497               0.485                  0.028                     0.213
net               0.455               0.413                  0.093                     0.160
fit_chem          0.653               0.660                  0.032                     0.117
fit_chem_net      0.692               0.699                  0.050                     0.088
increment         0.038               0.010                  0.037                     0.042

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.505               0.520                  0.046                     0.041
net_pair       0.475               0.507                  0.091                     0.064
```
