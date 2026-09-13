# descriptors_head_family_neutral_lipprop_lcs_tailtokens

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_head_family_neutral_lipprop_lcs_tailtokens'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.7054      0.5705      0.7174      0.5633      0.7957      0.5670
groups_choline            5      0.6108      0.4713      0.7363      0.4714      0.6268      0.4733
groups_phosphorus_free    5      0.4129      0.5388      0.4468      0.6564      0.4800      0.5755
groups_sphingolipids      5      0.5152      0.5024      0.6303      0.4333      0.5758      0.4650
ALL                      20      0.5611      0.5207      0.6327      0.5311      0.6196      0.5202

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5557      0.5445     0.0792  20
max valid BA                0.5699      0.5575     0.0779  20
best valid F1               0.5300      0.5367     0.0751  20
test BA                     0.5409      0.5335     0.0709  20
test AUC                    0.5408      0.5330     0.1205  20
test AUC in-protein         0.4741      0.5050     0.1515  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.4895      0.5013     0.1129  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.4505      0.4902     0.1523  20
test sensitivity            0.5611      0.5807     0.2307  20
test specificity            0.5207      0.4881     0.2026  20
test precision              0.4096      0.4130     0.0824  19
test loss                   0.7203      0.7153     0.0628  20
FPR (FP/(FP+TN))            0.4793      0.5119     0.2026  20
FNR (FN/(FN+TP))            0.4389      0.4193     0.2307  20

=== abs(sensitivity-specificity) gap: mean=0.2840 median=0.1991 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6637      0.6714     0.0196  5
  max valid BA                0.6814      0.6801     0.0278  5
  best valid F1               0.6030      0.6061     0.0239  5
  test BA                     0.6379      0.6195     0.0315  5
  test AUC                    0.7006      0.6811     0.0368  5
  test AUC in-protein         0.5427      0.5260     0.0533  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.5123      0.5046     0.0277  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.5522      0.5447     0.0370  5
  test sensitivity            0.7054      0.7419     0.0882  5
  test specificity            0.5705      0.5792     0.0836  5
  test precision              0.4571      0.4595     0.0322  5
  test loss                   0.6477      0.6624     0.0235  5
  FPR (FP/(FP+TN))            0.4295      0.4208     0.0836  5
  FNR (FN/(FN+TP))            0.2946      0.2581     0.0882  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5457      0.5431     0.0389  5
  max valid BA                0.5500      0.5569     0.0394  5
  best valid F1               0.5150      0.5167     0.0288  5
  test BA                     0.5410      0.5370     0.0316  5
  test AUC                    0.5331      0.5383     0.0463  5
  test AUC in-protein         0.5810      0.5506     0.1183  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.6084      0.5633     0.1021  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.4735      0.4869     0.0375  5
  test sensitivity            0.6108      0.5856     0.0870  5
  test specificity            0.4713      0.4455     0.0772  5
  test precision              0.3887      0.3893     0.0266  5
  test loss                   0.7393      0.7321     0.0353  5
  FPR (FP/(FP+TN))            0.5287      0.5545     0.0772  5
  FNR (FN/(FN+TP))            0.3892      0.4144     0.0870  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5005      0.5088     0.0369  5
  max valid BA                0.5278      0.5323     0.0368  5
  best valid F1               0.4642      0.4634     0.0698  5
  test BA                     0.4758      0.4868     0.0434  5
  test AUC                    0.4829      0.4700     0.0872  5
  test AUC in-protein         0.3344      0.2889     0.1772  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.4407      0.4348     0.0906  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.3614      0.4000     0.1560  5
  test sensitivity            0.4129      0.4839     0.2071  5
  test specificity            0.5388      0.4898     0.1455  5
  test precision              0.3330      0.3750     0.1034  5
  test loss                   0.7211      0.7137     0.0431  5
  FPR (FP/(FP+TN))            0.4612      0.5102     0.1455  5
  FNR (FN/(FN+TP))            0.5871      0.5161     0.2071  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5127      0.5000     0.0756  5
  max valid BA                0.5204      0.5000     0.0621  5
  best valid F1               0.5377      0.5476     0.0898  5
  test BA                     0.5088      0.5000     0.0409  5
  test AUC                    0.4467      0.4039     0.1033  5
  test AUC in-protein         0.4383      0.4438     0.1209  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3966      0.3988     0.0952  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4148      0.4810     0.2407  5
  test sensitivity            0.5152      0.5758     0.3680  5
  test specificity            0.5024      0.3902     0.3924  5
  test precision              0.4717      0.4512     0.0690  4
  test loss                   0.7732      0.7423     0.0673  5
  FPR (FP/(FP+TN))            0.4976      0.6098     0.3924  5
  FNR (FN/(FN+TP))            0.4848      0.4242     0.3680  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (apolar_sasa_share,aromatic_share,buriedness_q50,chain,hydropathy_rim,pocket_elongation,pocket_flatness,pocket_volume_per_sasa,tail_double_bonds,tail_length_asymmetry,tail_length_mean,tail_unsaturation_density,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                      
anionic                     0.685         0.739    0.716              0.535         0.529
choline                     0.457         0.405    0.488              0.541         0.507
phosphorus_free             0.377         0.426    0.396              0.543         0.517
sphingolipids               0.374         0.272    0.276              0.480         0.352

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.460               0.422                  0.041                     0.198
net_AUC           0.469               0.429                  0.053                     0.186

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.525               0.533                  0.042                     0.030
net_AUC_pair           0.476               0.513                  0.068                     0.083

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
       chem    net  chem_pair  net_pair
epoch                                  
1      0.46  0.477      0.525     0.505
10     0.46  0.440      0.525     0.459
49     0.46  0.437      0.525     0.444
51     0.46  0.440      0.525     0.445
120    0.46  0.469      0.525     0.476

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.657         0.682      0.025
10        0.657         0.683      0.026
49        0.657         0.697      0.040
51        0.657         0.697      0.040
120       0.657         0.688      0.031

3. mean over seeds, epoch 120
                  chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                                  
anionic          0.739  0.716      0.535     0.529     0.739         0.763      0.024
choline          0.405  0.488      0.541     0.507     0.595         0.607      0.012
phosphorus_free  0.426  0.396      0.543     0.517     0.565         0.613      0.048
sphingolipids    0.272  0.276      0.480     0.352     0.728         0.768      0.039

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.460               0.422                  0.041                     0.198
net               0.469               0.429                  0.053                     0.186
fit_chem          0.657               0.665                  0.044                     0.089
fit_chem_net      0.688               0.689                  0.035                     0.089
increment         0.031               0.014                  0.044                     0.016

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.525               0.533                  0.042                     0.030
net_pair       0.476               0.513                  0.068                     0.083
```
