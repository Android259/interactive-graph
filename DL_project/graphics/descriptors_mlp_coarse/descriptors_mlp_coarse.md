# descriptors_mlp_coarse

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_mlp_coarse'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6149      0.5148      0.4874      0.5657      0.6418      0.5419
groups_GLTP            5      0.3120      0.7120      0.5051      0.5392      0.4308      0.7385
groups_IP_trans        5      0.5391      0.5702      0.5620      0.5702      0.6083      0.6170
groups_LBP_BPI_CETP    5      0.6261      0.7277      0.5082      0.5812      0.7000      0.6851
groups_START           5      0.4246      0.5753      0.4785      0.5939      0.4594      0.6000
groups_lipocalin       5      0.6056      0.5722      0.4924      0.6015      0.6500      0.5778
groups_scp2            5      0.7059      0.3529      0.6469      0.4346      0.7529      0.4118
ALL                   35      0.5469      0.5750      0.5258      0.5552      0.6062      0.5960

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6011      0.6029     0.0720  35
max valid BA                0.6124      0.6104     0.0749  35
best valid F1               0.5658      0.5574     0.0810  35
test BA                     0.5609      0.5600     0.0944  35
test F1                     0.4772      0.4966     0.1281  35
test sensitivity            0.5469      0.5882     0.2103  35
test specificity            0.5750      0.5588     0.1890  35
test precision              0.4616      0.4405     0.1253  35
test loss                   0.6874      0.6862     0.0281  35
FPR (FP/(FP+TN))            0.4250      0.4412     0.1890  35
FNR (FN/(FN+TP))            0.4531      0.4118     0.2103  35

=== abs(sensitivity-specificity) gap: mean=0.2711 median=0.1869 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5919      0.5951     0.0396  5
  max valid BA                0.6093      0.6316     0.0452  5
  best valid F1               0.6714      0.6765     0.0118  5
  test BA                     0.5648      0.5706     0.0466  5
  test F1                     0.5969      0.6029     0.0451  5
  test sensitivity            0.6149      0.6119     0.0793  5
  test specificity            0.5148      0.4754     0.1079  5
  test precision              0.5851      0.5765     0.0527  5
  test loss                   0.6849      0.6844     0.0061  5
  FPR (FP/(FP+TN))            0.4852      0.5246     0.1079  5
  FNR (FN/(FN+TP))            0.3851      0.3881     0.0793  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5846      0.5577     0.0554  5
  max valid BA                0.5846      0.5577     0.0554  5
  best valid F1               0.5511      0.5574     0.0855  5
  test BA                     0.5120      0.4800     0.0642  5
  test F1                     0.3906      0.4091     0.0661  5
  test sensitivity            0.3120      0.3200     0.0522  5
  test specificity            0.7120      0.6800     0.1035  5
  test precision              0.5295      0.4737     0.1179  5
  test loss                   0.6997      0.6922     0.0263  5
  FPR (FP/(FP+TN))            0.2880      0.3200     0.1035  5
  FNR (FN/(FN+TP))            0.6880      0.6800     0.0522  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6127      0.6104     0.0249  5
  max valid BA                0.6316      0.6215     0.0315  5
  best valid F1               0.5401      0.5333     0.0329  5
  test BA                     0.5547      0.5490     0.0544  5
  test F1                     0.4225      0.4800     0.1392  5
  test sensitivity            0.5391      0.6087     0.2471  5
  test specificity            0.5702      0.5745     0.2076  5
  test precision              0.3721      0.3684     0.0689  5
  test loss                   0.6897      0.6848     0.0140  5
  FPR (FP/(FP+TN))            0.4298      0.4255     0.2076  5
  FNR (FN/(FN+TP))            0.4609      0.3913     0.2471  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6926      0.7247     0.0937  5
  max valid BA                0.7137      0.7247     0.0858  5
  best valid F1               0.6253      0.6462     0.1027  5
  test BA                     0.6769      0.6892     0.1506  5
  test F1                     0.5658      0.6000     0.2090  5
  test sensitivity            0.6261      0.6522     0.2509  5
  test specificity            0.7277      0.6809     0.1262  5
  test precision              0.5292      0.4865     0.1983  5
  test loss                   0.6587      0.6507     0.0384  5
  FPR (FP/(FP+TN))            0.2723      0.3191     0.1262  5
  FNR (FN/(FN+TP))            0.3739      0.3478     0.2509  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5297      0.5209     0.0732  5
  max valid BA                0.5357      0.5209     0.0803  5
  best valid F1               0.5148      0.4855     0.0740  5
  test BA                     0.4999      0.5206     0.0611  5
  test F1                     0.4130      0.3652     0.0970  5
  test sensitivity            0.4246      0.3692     0.1601  5
  test specificity            0.5753      0.5056     0.1556  5
  test precision              0.4255      0.4405     0.0632  5
  test loss                   0.7119      0.7079     0.0260  5
  FPR (FP/(FP+TN))            0.4247      0.4944     0.1556  5
  FNR (FN/(FN+TP))            0.5754      0.6308     0.1601  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6139      0.6389     0.0526  5
  max valid BA                0.6208      0.6458     0.0462  5
  best valid F1               0.5325      0.5510     0.0549  5
  test BA                     0.5889      0.5903     0.0394  5
  test F1                     0.4822      0.5000     0.0668  5
  test sensitivity            0.6056      0.6389     0.1918  5
  test specificity            0.5722      0.5000     0.1719  5
  test precision              0.4315      0.4107     0.0712  5
  test loss                   0.6785      0.6808     0.0197  5
  FPR (FP/(FP+TN))            0.4278      0.5000     0.1719  5
  FNR (FN/(FN+TP))            0.3944      0.3611     0.1918  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5824      0.6029     0.0620  5
  max valid BA                0.5912      0.6029     0.0583  5
  best valid F1               0.5254      0.5231     0.0455  5
  test BA                     0.5294      0.5000     0.1086  5
  test F1                     0.4696      0.5000     0.1002  5
  test sensitivity            0.7059      0.6471     0.2080  5
  test specificity            0.3529      0.3529     0.2230  5
  test precision              0.3586      0.3333     0.0837  5
  test loss                   0.6880      0.6986     0.0342  5
  FPR (FP/(FP+TN))            0.6471      0.6471     0.2230  5
  FNR (FN/(FN+TP))            0.2941      0.3529     0.2080  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (aromatic_share,chain,hbond,heavy,occupancy,polar_share,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.425         0.548    0.557              0.542         0.551
GLTP                     0.424         0.685    0.521              0.667         0.517
IP_trans                 0.460         0.574    0.588              0.621         0.555
LBP_BPI_CETP             0.492         0.701    0.640              0.687         0.636
START                    0.421         0.463    0.450              0.473         0.496
lipocalin                0.363         0.645    0.508              0.652         0.621
scp2                     0.435         0.487    0.536              0.549         0.503

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.586               0.570                  0.061                     0.094
net_AUC           0.543               0.543                  0.096                     0.061

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.599               0.599                  0.061                     0.079
net_AUC_pair           0.554               0.559                  0.092                     0.055

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.586  0.511      0.599     0.506
10     0.586  0.523      0.599     0.523
49     0.586  0.550      0.599     0.551
51     0.586  0.551      0.599     0.550
120    0.586  0.543      0.599     0.554

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.607         0.669      0.063
10        0.607         0.664      0.058
49        0.607         0.654      0.047
51        0.607         0.654      0.047
120       0.607         0.650      0.044

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.548  0.557      0.542     0.551     0.555         0.585      0.030
GLTP          0.685  0.521      0.667     0.517     0.680         0.717      0.037
IP_trans      0.574  0.588      0.621     0.555     0.574         0.638      0.064
LBP_BPI_CETP  0.701  0.640      0.687     0.636     0.701         0.766      0.064
START         0.463  0.450      0.473     0.496     0.546         0.607      0.061
lipocalin     0.645  0.508      0.652     0.621     0.645         0.660      0.015
scp2          0.487  0.536      0.549     0.503     0.547         0.580      0.033

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.586               0.570                  0.061                     0.094
net               0.543               0.543                  0.096                     0.061
fit_chem          0.607               0.582                  0.055                     0.067
fit_chem_net      0.650               0.637                  0.049                     0.070
increment         0.044               0.029                  0.050                     0.020

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.599               0.599                  0.061                     0.079
net_pair       0.554               0.559                  0.092                     0.055
```
