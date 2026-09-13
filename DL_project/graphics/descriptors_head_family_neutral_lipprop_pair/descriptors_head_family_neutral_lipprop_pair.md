# descriptors_head_family_neutral_lipprop_pair

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_head_family_neutral_lipprop_pair'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4269      0.5934      0.5937      0.4732      0.3373      0.8000
groups_GLTP            5      0.5440      0.5120      0.5919      0.4834      0.6692      0.6692
groups_IP_trans        5      0.5304      0.5064      0.5433      0.5656      0.6417      0.5872
groups_LBP_BPI_CETP    5      0.5391      0.7404      0.5464      0.5294      0.7417      0.7404
groups_START           5      0.5662      0.5528      0.4846      0.5440      0.5188      0.5865
groups_lipocalin       5      0.8222      0.3528      0.6813      0.3755      0.8278      0.3722
groups_scp2            5      0.6118      0.4529      0.5131      0.5882      0.7176      0.5529
ALL                   35      0.5772      0.5301      0.5649      0.5085      0.6363      0.6155

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5965      0.5951     0.0797  35
max valid BA                0.6259      0.6316     0.0814  35
best valid F1               0.5816      0.5926     0.1007  35
test BA                     0.5537      0.5564     0.0814  35
test AUC                    0.5486      0.5320     0.1238  35
test AUC in-protein         0.5645      0.5402     0.1320  35
  (proteins averaged)       3.1429      3.0000     1.0042  35
test AUC in-protein (pairs)      0.5688      0.5404     0.1429  35
  (proteins contributing)      3.5143      3.0000     1.7213  35
test F1                     0.4571      0.5200     0.1805  35
test sensitivity            0.5772      0.5652     0.2911  35
test specificity            0.5301      0.5556     0.2947  35
test precision              0.4572      0.4437     0.1134  32
test loss                   0.7610      0.6969     0.2069  35
FPR (FP/(FP+TN))            0.4699      0.4444     0.2947  35
FNR (FN/(FN+TP))            0.4228      0.4348     0.2911  35

=== abs(sensitivity-specificity) gap: mean=0.4451 median=0.3200 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5543      0.5292     0.0563  5
  max valid BA                0.5687      0.5504     0.0473  5
  best valid F1               0.5756      0.6308     0.1545  5
  test BA                     0.5102      0.5000     0.0395  5
  test AUC                    0.4806      0.4983     0.0931  5
  test AUC in-protein         0.4599      0.4661     0.0662  5
    (proteins averaged)       4.0000      4.0000     0.0000  5
  test AUC in-protein (pairs)      0.4688      0.4600     0.1208  5
    (proteins contributing)      4.4000      4.0000     0.5477  5
  test F1                     0.3742      0.5255     0.3119  5
  test sensitivity            0.4269      0.5373     0.4137  5
  test specificity            0.5934      0.6066     0.4018  5
  test precision              0.5048      0.5189     0.0960  4
  test loss                   0.7366      0.6995     0.0553  5
  FPR (FP/(FP+TN))            0.4066      0.3934     0.4018  5
  FNR (FN/(FN+TP))            0.5731      0.4627     0.4137  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6154      0.6154     0.0860  5
  max valid BA                0.6692      0.6731     0.0712  5
  best valid F1               0.6864      0.7246     0.0730  5
  test BA                     0.5280      0.5200     0.1073  5
  test AUC                    0.4522      0.4640     0.0861  5
  test AUC in-protein         0.4838      0.4985     0.0631  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4539      0.4650     0.0609  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5271      0.5238     0.0972  5
  test sensitivity            0.5440      0.4400     0.2147  5
  test specificity            0.5120      0.5200     0.2999  5
  test precision              0.5564      0.5200     0.1392  5
  test loss                   0.7416      0.6969     0.0844  5
  FPR (FP/(FP+TN))            0.4880      0.4800     0.2999  5
  FNR (FN/(FN+TP))            0.4560      0.5600     0.2147  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5910      0.5864     0.0668  5
  max valid BA                0.6145      0.6600     0.0774  5
  best valid F1               0.5188      0.5806     0.1182  5
  test BA                     0.5184      0.5000     0.0623  5
  test AUC                    0.4884      0.4912     0.0204  5
  test AUC in-protein         0.5357      0.5449     0.0270  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4789      0.4863     0.0598  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.3551      0.4156     0.2111  5
  test sensitivity            0.5304      0.5652     0.3707  5
  test specificity            0.5064      0.5745     0.3422  5
  test precision              0.3460      0.3407     0.0516  4
  test loss                   0.8303      0.7050     0.2863  5
  FPR (FP/(FP+TN))            0.4936      0.4255     0.3422  5
  FNR (FN/(FN+TP))            0.4696      0.4348     0.3707  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7018      0.7181     0.0441  5
  max valid BA                0.7410      0.7478     0.0343  5
  best valid F1               0.6588      0.6667     0.0402  5
  test BA                     0.6398      0.6323     0.0703  5
  test AUC                    0.7315      0.7327     0.0365  5
  test AUC in-protein         0.7720      0.7483     0.0523  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.7577      0.7495     0.0506  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5040      0.4878     0.1121  5
  test sensitivity            0.5391      0.4348     0.2509  5
  test specificity            0.7404      0.8085     0.1446  5
  test precision              0.5090      0.4783     0.0763  5
  test loss                   0.6478      0.6676     0.0387  5
  FPR (FP/(FP+TN))            0.2596      0.1915     0.1446  5
  FNR (FN/(FN+TP))            0.4609      0.5652     0.2509  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5093      0.5000     0.0326  5
  max valid BA                0.5526      0.5506     0.0625  5
  best valid F1               0.5340      0.5026     0.0716  5
  test BA                     0.5595      0.5691     0.0467  5
  test AUC                    0.5594      0.5360     0.0947  5
  test AUC in-protein         0.5968      0.6102     0.0675  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5809      0.5895     0.0899  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.4535      0.5625     0.2555  5
  test sensitivity            0.5662      0.5538     0.3653  5
  test specificity            0.5528      0.5843     0.3450  5
  test precision              0.4946      0.4839     0.0559  4
  test loss                   0.8989      0.7085     0.4428  5
  FPR (FP/(FP+TN))            0.4472      0.4157     0.3450  5
  FNR (FN/(FN+TP))            0.4338      0.4462     0.3653  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5917      0.5972     0.0647  5
  max valid BA                0.6000      0.6042     0.0667  5
  best valid F1               0.5425      0.5349     0.0398  5
  test BA                     0.5875      0.5903     0.0711  5
  test AUC                    0.5897      0.6784     0.1776  5
  test AUC in-protein         0.5812      0.6824     0.2218  5
    (proteins averaged)       5.0000      5.0000     0.0000  5
  test AUC in-protein (pairs)      0.5962      0.6129     0.1801  5
    (proteins contributing)      7.2000      7.0000     0.4472  5
  test F1                     0.5223      0.5496     0.0686  5
  test sensitivity            0.8222      0.9722     0.2394  5
  test specificity            0.3528      0.3611     0.2710  5
  test precision              0.3973      0.4000     0.0476  5
  test loss                   0.7761      0.7608     0.1461  5
  FPR (FP/(FP+TN))            0.6472      0.6389     0.2710  5
  FNR (FN/(FN+TP))            0.1778      0.0278     0.2394  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6118      0.6029     0.0732  5
  max valid BA                0.6353      0.6029     0.0514  5
  best valid F1               0.5548      0.5357     0.0538  5
  test BA                     0.5324      0.4706     0.1052  5
  test AUC                    0.5379      0.5320     0.0764  5
  test AUC in-protein         0.5222      0.5339     0.0431  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.6452      0.6594     0.1283  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.4631      0.4231     0.0855  5
  test sensitivity            0.6118      0.5882     0.0322  5
  test specificity            0.4529      0.3529     0.2177  5
  test precision              0.3868      0.3143     0.1366  5
  test loss                   0.6959      0.6969     0.0110  5
  FPR (FP/(FP+TN))            0.5471      0.6471     0.2177  5
  FNR (FN/(FN+TP))            0.3882      0.4118     0.0322  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (apolar_sasa_share,aromatic_contact,aromatic_contact_min,aromatic_share,buriedness_match,buriedness_q50,chain,elongation_shape_match,flatness_shape_match,hbond,hbond_match,hbond_match_min,heavy,hydropathy_rim,hydropathy_rim_match,pocket_elongation,pocket_flatness,pocket_volume_per_sasa,tail_elongation_fit,unsaturation,volume_fit), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.192         0.536    0.478              0.498         0.454
GLTP                     0.244         0.599    0.437              0.617         0.372
IP_trans                 0.273         0.469    0.528              0.412         0.482
LBP_BPI_CETP             0.241         0.532    0.668              0.537         0.703
START                    0.214         0.452    0.447              0.511         0.539
lipocalin                0.218         0.581    0.458              0.583         0.512
scp2                     0.228         0.565    0.572              0.556         0.553

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.533               0.533                  0.056                     0.055
net_AUC           0.513               0.486                  0.117                     0.084

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.531               0.523                  0.063                     0.067
net_AUC_pair           0.516               0.525                  0.123                     0.102

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.533  0.528      0.531     0.508
10     0.533  0.519      0.531     0.508
49     0.533  0.525      0.531     0.507
51     0.533  0.518      0.531     0.500
120    0.533  0.513      0.531     0.516

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.561         0.659      0.098
10        0.561         0.642      0.081
49        0.561         0.626      0.065
51        0.561         0.629      0.069
120       0.561         0.637      0.076

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.536  0.478      0.498     0.454     0.536         0.558      0.022
GLTP          0.599  0.437      0.617     0.372     0.599         0.720      0.122
IP_trans      0.469  0.528      0.412     0.482     0.531         0.634      0.103
LBP_BPI_CETP  0.532  0.668      0.537     0.703     0.551         0.724      0.173
START         0.452  0.447      0.511     0.539     0.555         0.582      0.026
lipocalin     0.581  0.458      0.583     0.512     0.581         0.613      0.032
scp2          0.565  0.572      0.556     0.553     0.572         0.628      0.056

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.533               0.533                  0.056                     0.055
net               0.513               0.486                  0.117                     0.084
fit_chem          0.561               0.541                  0.050                     0.024
fit_chem_net      0.637               0.616                  0.064                     0.064
increment         0.076               0.046                  0.060                     0.058

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.531               0.523                  0.063                     0.067
net_pair       0.516               0.525                  0.123                     0.102
```
