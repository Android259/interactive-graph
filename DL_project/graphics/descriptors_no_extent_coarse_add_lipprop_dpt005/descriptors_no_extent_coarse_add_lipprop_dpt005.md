                                                                                            # descriptors_no_extent_coarse_add_lipprop_dpt005

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_add_lipprop_dpt005'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4090      0.6197      0.5846      0.5602      0.4985      0.6452
groups_GLTP            5      0.5440      0.5840      0.5702      0.5569      0.5462      0.6000
groups_IP_trans        5      0.4174      0.6170      0.6336      0.4972      0.6083      0.6723
groups_LBP_BPI_CETP    5      0.7391      0.6766      0.6526      0.4799      0.7167      0.6979
groups_START           5      0.5723      0.5371      0.7222      0.3853      0.5687      0.5461
groups_lipocalin       5      0.5111      0.5722      0.6086      0.5456      0.5556      0.6000
groups_scp2            5      0.6588      0.4176      0.6159      0.4576      0.6824      0.4235
ALL                   35      0.5502      0.5749      0.6268      0.4975      0.5966      0.5979

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5978      0.5852     0.0888  35
max valid BA                0.6225      0.6104     0.0924  35
best valid F1               0.5826      0.5769     0.0998  35
test BA                     0.5626      0.5560     0.0997  35
test F1                     0.4662      0.5000     0.1630  35
test sensitivity            0.5502      0.6119     0.2699  35
test specificity            0.5749      0.6250     0.2458  35
test precision              0.4628      0.4615     0.1186  35
test loss                   0.6857      0.6861     0.0284  35
FPR (FP/(FP+TN))            0.4251      0.3750     0.2458  35
FNR (FN/(FN+TP))            0.4498      0.3881     0.2699  35

=== abs(sensitivity-specificity) gap: mean=0.4010 median=0.4033 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5718      0.5775     0.0258  5
  max valid BA                0.5829      0.5880     0.0294  5
  best valid F1               0.6387      0.6380     0.0384  5
  test BA                     0.5143      0.5038     0.0242  5
  test F1                     0.4298      0.4310     0.1846  5
  test sensitivity            0.4090      0.3731     0.2436  5
  test specificity            0.6197      0.6066     0.2139  5
  test precision              0.5388      0.5412     0.0220  5
  test loss                   0.6914      0.6894     0.0052  5
  FPR (FP/(FP+TN))            0.3803      0.3934     0.2139  5
  FNR (FN/(FN+TP))            0.5910      0.6269     0.2436  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5769      0.5577     0.1276  5
  max valid BA                0.6077      0.5769     0.1143  5
  best valid F1               0.6444      0.6571     0.1114  5
  test BA                     0.5640      0.5800     0.1126  5
  test F1                     0.5179      0.5455     0.2128  5
  test sensitivity            0.5440      0.5200     0.3028  5
  test specificity            0.5840      0.5200     0.2184  5
  test precision              0.5570      0.5714     0.0904  5
  test loss                   0.6919      0.6893     0.0073  5
  FPR (FP/(FP+TN))            0.4160      0.4800     0.2184  5
  FNR (FN/(FN+TP))            0.4560      0.4800     0.3028  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6403      0.6755     0.0600  5
  max valid BA                0.6863      0.6862     0.0636  5
  best valid F1               0.6026      0.5714     0.0637  5
  test BA                     0.5172      0.5083     0.0554  5
  test F1                     0.3449      0.3333     0.1371  5
  test sensitivity            0.4174      0.2609     0.2974  5
  test specificity            0.6170      0.7021     0.2627  5
  test precision              0.3481      0.3333     0.0879  5
  test loss                   0.6817      0.6838     0.0125  5
  FPR (FP/(FP+TN))            0.3830      0.2979     0.2627  5
  FNR (FN/(FN+TP))            0.5826      0.7391     0.2974  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7073      0.7358     0.0856  5
  max valid BA                0.7347      0.7575     0.0874  5
  best valid F1               0.6488      0.6786     0.1027  5
  test BA                     0.7079      0.7549     0.0890  5
  test F1                     0.6218      0.6667     0.0878  5
  test sensitivity            0.7391      0.6957     0.1375  5
  test specificity            0.6766      0.7660     0.1820  5
  test precision              0.5557      0.5600     0.1275  5
  test loss                   0.6614      0.6637     0.0260  5
  FPR (FP/(FP+TN))            0.3234      0.2340     0.1820  5
  FNR (FN/(FN+TP))            0.2609      0.3043     0.1375  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5574      0.5775     0.0855  5
  max valid BA                0.5883      0.6152     0.1005  5
  best valid F1               0.5659      0.5811     0.0570  5
  test BA                     0.5547      0.6010     0.0963  5
  test F1                     0.5028      0.5333     0.1393  5
  test sensitivity            0.5723      0.6462     0.2387  5
  test specificity            0.5371      0.6517     0.3007  5
  test precision              0.4853      0.5055     0.0991  5
  test loss                   0.7039      0.6850     0.0438  5
  FPR (FP/(FP+TN))            0.4629      0.3483     0.3007  5
  FNR (FN/(FN+TP))            0.4277      0.3538     0.2387  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5778      0.5694     0.0608  5
  max valid BA                0.5931      0.5903     0.0526  5
  best valid F1               0.4681      0.4750     0.1099  5
  test BA                     0.5417      0.5347     0.0832  5
  test F1                     0.4030      0.4065     0.1287  5
  test sensitivity            0.5111      0.5556     0.3008  5
  test specificity            0.5722      0.6250     0.3098  5
  test precision              0.3943      0.4211     0.0613  5
  test loss                   0.6647      0.6596     0.0366  5
  FPR (FP/(FP+TN))            0.4278      0.3750     0.3098  5
  FNR (FN/(FN+TP))            0.4889      0.4444     0.3008  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5529      0.5735     0.0671  5
  max valid BA                0.5647      0.5735     0.0654  5
  best valid F1               0.5100      0.5000     0.0535  5
  test BA                     0.5382      0.5588     0.1043  5
  test F1                     0.4435      0.5172     0.1516  5
  test sensitivity            0.6588      0.7059     0.3233  5
  test specificity            0.4176      0.2647     0.2847  5
  test precision              0.3600      0.3659     0.0900  5
  test loss                   0.7045      0.7046     0.0205  5
  FPR (FP/(FP+TN))            0.5824      0.7353     0.2847  5
  FNR (FN/(FN+TP))            0.3412      0.2941     0.3233  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (aromatic_share,chain,hbond,heavy,occupancy,polar_share,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.425         0.548    0.554              0.542         0.553
GLTP                     0.424         0.685    0.455              0.667         0.464
IP_trans                 0.460         0.574    0.691              0.621         0.651
LBP_BPI_CETP             0.492         0.701    0.660              0.687         0.655
START                    0.421         0.463    0.577              0.473         0.594
lipocalin                0.363         0.645    0.583              0.652         0.595
scp2                     0.435         0.487    0.446              0.549         0.471

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.586               0.570                  0.061                     0.094
net_AUC           0.566               0.584                  0.075                     0.093

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.599               0.599                  0.061                     0.079
net_AUC_pair           0.569               0.590                  0.073                     0.078

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.586  0.509      0.599     0.516
10     0.586  0.543      0.599     0.567
49     0.586  0.542      0.599     0.561
51     0.586  0.545      0.599     0.561
120    0.586  0.566      0.599     0.569

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.607         0.670      0.063
10        0.607         0.684      0.078
49        0.607         0.676      0.069
51        0.607         0.675      0.068
120       0.607         0.668      0.061

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.548  0.554      0.542     0.553     0.555         0.589      0.034
GLTP          0.685  0.455      0.667     0.464     0.680         0.721      0.042
IP_trans      0.574  0.691      0.621     0.651     0.574         0.729      0.155
LBP_BPI_CETP  0.701  0.660      0.687     0.655     0.701         0.706      0.004
START         0.463  0.577      0.473     0.594     0.546         0.636      0.091
lipocalin     0.645  0.583      0.652     0.595     0.645         0.676      0.032
scp2          0.487  0.446      0.549     0.471     0.547         0.615      0.068

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.586               0.570                  0.061                     0.094
net               0.566               0.584                  0.075                     0.093
fit_chem          0.607               0.582                  0.055                     0.067
fit_chem_net      0.668               0.655                  0.052                     0.055
increment         0.061               0.044                  0.055                     0.050

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.599               0.599                  0.061                     0.079
net_pair       0.569               0.590                  0.073                     0.078
```
