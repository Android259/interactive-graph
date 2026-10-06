# descriptors_2heads_coarse

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_2heads_coarse'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5522      0.5311      0.5966      0.4957      0.6149      0.5484
groups_GLTP            5      0.4000      0.5680      0.6588      0.4564      0.4538      0.6769
groups_IP_trans        5      0.6000      0.5660      0.6612      0.4667      0.6750      0.5957
groups_LBP_BPI_CETP    5      0.7913      0.7489      0.6438      0.4972      0.8250      0.7532
groups_START           5      0.5692      0.4472      0.7317      0.3614      0.5687      0.4494
groups_lipocalin       5      0.5778      0.5639      0.6771      0.5113      0.6111      0.5778
groups_scp2            5      0.6706      0.4294      0.6301      0.4690      0.7059      0.4588
ALL                   35      0.5944      0.5506      0.6570      0.4654      0.6364      0.5800

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6082      0.5923     0.0942  35
max valid BA                0.6243      0.6110     0.0980  35
best valid F1               0.5877      0.5797     0.1031  35
test BA                     0.5725      0.5400     0.1044  35
test F1                     0.5019      0.5116     0.1275  35
test sensitivity            0.5944      0.6400     0.2369  35
test specificity            0.5506      0.5972     0.2378  35
test precision              0.4762      0.4545     0.1139  35
test loss                   0.6864      0.6897     0.0325  35
FPR (FP/(FP+TN))            0.4494      0.4028     0.2378  35
FNR (FN/(FN+TP))            0.4056      0.3600     0.2369  35

=== abs(sensitivity-specificity) gap: mean=0.3390 median=0.2866 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5817      0.5784     0.0352  5
  max valid BA                0.5942      0.5921     0.0277  5
  best valid F1               0.6467      0.6627     0.0469  5
  test BA                     0.5417      0.5369     0.0319  5
  test F1                     0.5404      0.5120     0.1081  5
  test sensitivity            0.5522      0.4776     0.2295  5
  test specificity            0.5311      0.5410     0.1993  5
  test precision              0.5689      0.5571     0.0415  5
  test loss                   0.6882      0.6917     0.0115  5
  FPR (FP/(FP+TN))            0.4689      0.4590     0.1993  5
  FNR (FN/(FN+TP))            0.4478      0.5224     0.2295  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5654      0.5577     0.0322  5
  max valid BA                0.5769      0.5769     0.0360  5
  best valid F1               0.5763      0.6452     0.1175  5
  test BA                     0.4840      0.4800     0.0477  5
  test F1                     0.4242      0.3810     0.0981  5
  test sensitivity            0.4000      0.3200     0.1600  5
  test specificity            0.5680      0.6000     0.1730  5
  test precision              0.4845      0.4706     0.0525  5
  test loss                   0.6993      0.7016     0.0112  5
  FPR (FP/(FP+TN))            0.4320      0.4000     0.1730  5
  FNR (FN/(FN+TP))            0.6000      0.6800     0.1600  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6354      0.6618     0.0662  5
  max valid BA                0.6707      0.6733     0.0785  5
  best valid F1               0.5988      0.5938     0.0671  5
  test BA                     0.5830      0.5897     0.0612  5
  test F1                     0.4652      0.5000     0.1132  5
  test sensitivity            0.6000      0.6957     0.2543  5
  test specificity            0.5660      0.5745     0.1666  5
  test precision              0.3986      0.4038     0.0613  5
  test loss                   0.6813      0.6897     0.0226  5
  FPR (FP/(FP+TN))            0.4340      0.4255     0.1666  5
  FNR (FN/(FN+TP))            0.4000      0.3043     0.2543  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7891      0.7686     0.0408  5
  max valid BA                0.7996      0.7894     0.0464  5
  best valid F1               0.7307      0.7170     0.0559  5
  test BA                     0.7701      0.7549     0.0794  5
  test F1                     0.6921      0.6667     0.0982  5
  test sensitivity            0.7913      0.8261     0.1206  5
  test specificity            0.7489      0.8085     0.1462  5
  test precision              0.6288      0.6250     0.1336  5
  test loss                   0.6450      0.6570     0.0348  5
  FPR (FP/(FP+TN))            0.2511      0.1915     0.1462  5
  FNR (FN/(FN+TP))            0.2087      0.1739     0.1206  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5091      0.5015     0.0768  5
  max valid BA                0.5242      0.5127     0.0927  5
  best valid F1               0.5404      0.5758     0.0766  5
  test BA                     0.5082      0.4953     0.0735  5
  test F1                     0.4666      0.5248     0.1295  5
  test sensitivity            0.5692      0.6462     0.2733  5
  test specificity            0.4472      0.6180     0.3232  5
  test precision              0.4361      0.4118     0.0662  5
  test loss                   0.7185      0.7010     0.0430  5
  FPR (FP/(FP+TN))            0.5528      0.3820     0.3232  5
  FNR (FN/(FN+TP))            0.4308      0.3538     0.2733  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5944      0.5972     0.0313  5
  max valid BA                0.6042      0.5972     0.0357  5
  best valid F1               0.4987      0.5349     0.1053  5
  test BA                     0.5708      0.5625     0.0679  5
  test F1                     0.4596      0.4483     0.0815  5
  test sensitivity            0.5778      0.6111     0.2616  5
  test specificity            0.5639      0.5972     0.3216  5
  test precision              0.4427      0.4727     0.1078  5
  test loss                   0.6723      0.6607     0.0241  5
  FPR (FP/(FP+TN))            0.4361      0.4028     0.3216  5
  FNR (FN/(FN+TP))            0.4222      0.3889     0.2616  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5824      0.6029     0.0436  5
  max valid BA                0.6000      0.6176     0.0503  5
  best valid F1               0.5221      0.5238     0.0377  5
  test BA                     0.5500      0.5294     0.0603  5
  test F1                     0.4650      0.5116     0.0960  5
  test sensitivity            0.6706      0.6471     0.2650  5
  test specificity            0.4294      0.5588     0.2676  5
  test precision              0.3737      0.3500     0.0644  5
  test loss                   0.7001      0.6971     0.0204  5
  FPR (FP/(FP+TN))            0.5706      0.4412     0.2676  5
  FNR (FN/(FN+TP))            0.3294      0.3529     0.2650  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (aromatic_share,chain,hbond,heavy,occupancy,polar_share,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.425         0.548    0.537              0.542         0.519
GLTP                     0.424         0.685    0.538              0.667         0.531
IP_trans                 0.460         0.574    0.671              0.621         0.628
LBP_BPI_CETP             0.492         0.701    0.749              0.687         0.739
START                    0.421         0.463    0.479              0.473         0.537
lipocalin                0.363         0.645    0.510              0.652         0.682
scp2                     0.435         0.487    0.484              0.549         0.467

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.586               0.570                  0.061                     0.094
net_AUC           0.567               0.556                  0.084                     0.103

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.599               0.599                  0.061                     0.079
net_AUC_pair           0.586               0.579                  0.083                     0.099

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.586  0.505      0.599     0.524
10     0.586  0.569      0.599     0.588
49     0.586  0.577      0.599     0.595
51     0.586  0.574      0.599     0.593
120    0.586  0.567      0.599     0.586

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.607         0.669      0.062
10        0.607         0.666      0.060
49        0.607         0.663      0.057
51        0.607         0.663      0.056
120       0.607         0.658      0.051

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.548  0.537      0.542     0.519     0.555         0.572      0.017
GLTP          0.685  0.538      0.667     0.531     0.680         0.694      0.015
IP_trans      0.574  0.671      0.621     0.628     0.574         0.705      0.131
LBP_BPI_CETP  0.701  0.749      0.687     0.739     0.701         0.779      0.077
START         0.463  0.479      0.473     0.537     0.546         0.591      0.046
lipocalin     0.645  0.510      0.652     0.682     0.645         0.674      0.030
scp2          0.487  0.484      0.549     0.467     0.547         0.591      0.045

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.586               0.570                  0.061                     0.094
net               0.567               0.556                  0.084                     0.103
fit_chem          0.607               0.582                  0.055                     0.067
fit_chem_net      0.658               0.655                  0.059                     0.076
increment         0.051               0.033                  0.057                     0.041

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.599               0.599                  0.061                     0.079
net_pair       0.586               0.579                  0.083                     0.099
```
