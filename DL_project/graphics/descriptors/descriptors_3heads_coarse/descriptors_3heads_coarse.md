# descriptors_3heads_coarse

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_3heads_coarse'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6388      0.5016      0.5800      0.5086      0.6836      0.5323
groups_GLTP            5      0.4880      0.4800      0.5982      0.5105      0.5923      0.5846
groups_IP_trans        5      0.5826      0.6383      0.6231      0.5333      0.6333      0.6298
groups_LBP_BPI_CETP    5      0.8783      0.6553      0.6289      0.5054      0.8583      0.6723
groups_START           5      0.5815      0.3685      0.6805      0.4509      0.5969      0.4135
groups_lipocalin       5      0.7278      0.5250      0.5780      0.5294      0.7444      0.5056
groups_scp2            5      0.4706      0.5118      0.5768      0.4753      0.5529      0.5647
ALL                   35      0.6239      0.5258      0.6094      0.5019      0.6660      0.5575

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6118      0.6111     0.0902  35
max valid BA                0.6229      0.6139     0.0932  35
best valid F1               0.5903      0.5862     0.0926  35
test BA                     0.5749      0.5625     0.1098  35
test F1                     0.5164      0.5490     0.1219  35
test sensitivity            0.6239      0.6000     0.2283  35
test specificity            0.5258      0.5506     0.2043  35
test precision              0.4738      0.4737     0.1081  35
test loss                   0.6924      0.6920     0.0247  35
FPR (FP/(FP+TN))            0.4742      0.4494     0.2043  35
FNR (FN/(FN+TP))            0.3761      0.4000     0.2283  35

=== abs(sensitivity-specificity) gap: mean=0.3162 median=0.2381 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6079      0.6133     0.0207  5
  max valid BA                0.6131      0.6139     0.0163  5
  best valid F1               0.6659      0.6897     0.0448  5
  test BA                     0.5702      0.5637     0.0444  5
  test F1                     0.6092      0.6107     0.0451  5
  test sensitivity            0.6388      0.6269     0.0807  5
  test specificity            0.5016      0.5082     0.0988  5
  test precision              0.5866      0.5902     0.0398  5
  test loss                   0.6884      0.6892     0.0093  5
  FPR (FP/(FP+TN))            0.4984      0.4918     0.0988  5
  FNR (FN/(FN+TP))            0.3612      0.3731     0.0807  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5885      0.5962     0.0501  5
  max valid BA                0.6115      0.6346     0.0699  5
  best valid F1               0.6423      0.6400     0.0533  5
  test BA                     0.4840      0.4600     0.0434  5
  test F1                     0.4721      0.4906     0.0954  5
  test sensitivity            0.4880      0.5200     0.1863  5
  test specificity            0.4800      0.4400     0.2315  5
  test precision              0.4904      0.4643     0.0539  5
  test loss                   0.7088      0.7093     0.0039  5
  FPR (FP/(FP+TN))            0.5200      0.5600     0.2315  5
  FNR (FN/(FN+TP))            0.5120      0.4800     0.1863  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6316      0.6325     0.0724  5
  max valid BA                0.6487      0.6534     0.0607  5
  best valid F1               0.5587      0.5424     0.0556  5
  test BA                     0.6105      0.6332     0.0472  5
  test F1                     0.5029      0.5106     0.0406  5
  test sensitivity            0.5826      0.5217     0.1214  5
  test specificity            0.6383      0.7021     0.1830  5
  test precision              0.4578      0.5000     0.0703  5
  test loss                   0.6788      0.6775     0.0081  5
  FPR (FP/(FP+TN))            0.3617      0.2979     0.1830  5
  FNR (FN/(FN+TP))            0.4174      0.4783     0.1214  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7653      0.7988     0.0749  5
  max valid BA                0.7844      0.7988     0.0736  5
  best valid F1               0.7152      0.7213     0.0797  5
  test BA                     0.7668      0.7636     0.0343  5
  test F1                     0.6836      0.6792     0.0378  5
  test sensitivity            0.8783      0.9130     0.1125  5
  test specificity            0.6553      0.6596     0.1515  5
  test precision              0.5733      0.5789     0.0911  5
  test loss                   0.6643      0.6582     0.0211  5
  FPR (FP/(FP+TN))            0.3447      0.3404     0.1515  5
  FNR (FN/(FN+TP))            0.1217      0.0870     0.1125  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5052      0.5042     0.0672  5
  max valid BA                0.5161      0.5042     0.0691  5
  best valid F1               0.5241      0.5393     0.0262  5
  test BA                     0.4750      0.4445     0.0500  5
  test F1                     0.4655      0.4688     0.0791  5
  test sensitivity            0.5815      0.5385     0.1986  5
  test specificity            0.3685      0.3483     0.2253  5
  test precision              0.4039      0.3835     0.0485  5
  test loss                   0.7115      0.7141     0.0188  5
  FPR (FP/(FP+TN))            0.6315      0.6517     0.2253  5
  FNR (FN/(FN+TP))            0.4185      0.4615     0.1986  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6250      0.6181     0.0314  5
  max valid BA                0.6250      0.6181     0.0314  5
  best valid F1               0.5499      0.5645     0.0446  5
  test BA                     0.6264      0.6389     0.0435  5
  test F1                     0.5045      0.5785     0.1408  5
  test sensitivity            0.7278      0.9722     0.3790  5
  test specificity            0.5250      0.3611     0.3012  5
  test precision              0.4800      0.4390     0.1075  5
  test loss                   0.6963      0.6944     0.0316  5
  FPR (FP/(FP+TN))            0.4750      0.6389     0.3012  5
  FNR (FN/(FN+TP))            0.2722      0.0278     0.3790  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5588      0.5735     0.0360  5
  max valid BA                0.5618      0.5735     0.0335  5
  best valid F1               0.4762      0.4776     0.0294  5
  test BA                     0.4912      0.4706     0.0916  5
  test F1                     0.3770      0.3500     0.0994  5
  test sensitivity            0.4706      0.4118     0.1995  5
  test specificity            0.5118      0.5294     0.1494  5
  test precision              0.3249      0.3043     0.0698  5
  test loss                   0.6986      0.7026     0.0337  5
  FPR (FP/(FP+TN))            0.4882      0.4706     0.1494  5
  FNR (FN/(FN+TP))            0.5294      0.5882     0.1995  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (aromatic_share,chain,hbond,heavy,occupancy,polar_share,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.425         0.548    0.529              0.542         0.528
GLTP                     0.424         0.685    0.521              0.667         0.503
IP_trans                 0.460         0.574    0.632              0.621         0.599
LBP_BPI_CETP             0.492         0.701    0.762              0.687         0.778
START                    0.421         0.463    0.470              0.473         0.506
lipocalin                0.363         0.645    0.389              0.652         0.652
scp2                     0.435         0.487    0.467              0.549         0.454

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.586               0.570                  0.061                     0.094
net_AUC           0.539               0.534                  0.079                     0.123

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.599               0.599                  0.061                     0.079
net_AUC_pair           0.574               0.562                  0.086                     0.112

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.586  0.494      0.599     0.494
10     0.586  0.525      0.599     0.534
49     0.586  0.544      0.599     0.572
51     0.586  0.542      0.599     0.572
120    0.586  0.539      0.599     0.574

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.607         0.666      0.059
10        0.607         0.663      0.056
49        0.607         0.666      0.059
51        0.607         0.663      0.057
120       0.607         0.662      0.056

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.548  0.529      0.542     0.528     0.555         0.579      0.024
GLTP          0.685  0.521      0.667     0.503     0.680         0.697      0.017
IP_trans      0.574  0.632      0.621     0.599     0.574         0.692      0.118
LBP_BPI_CETP  0.701  0.762      0.687     0.778     0.701         0.812      0.111
START         0.463  0.470      0.473     0.506     0.546         0.579      0.033
lipocalin     0.645  0.389      0.652     0.652     0.645         0.685      0.040
scp2          0.487  0.467      0.549     0.454     0.547         0.592      0.046

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.586               0.570                  0.061                     0.094
net               0.539               0.534                  0.079                     0.123
fit_chem          0.607               0.582                  0.055                     0.067
fit_chem_net      0.662               0.656                  0.063                     0.086
increment         0.056               0.037                  0.056                     0.041

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.599               0.599                  0.061                     0.079
net_pair       0.574               0.562                  0.086                     0.112
```
