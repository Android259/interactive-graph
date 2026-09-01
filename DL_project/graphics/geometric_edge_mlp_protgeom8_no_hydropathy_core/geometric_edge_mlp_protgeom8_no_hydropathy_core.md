# geometric_edge_mlp_protgeom8_no_hydropathy_core

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom8_no_hydropathy_core'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5403      0.5049      0.6634      0.6262      0.6179      0.5710
groups_GLTP            5      0.4000      0.5760      0.7884      0.5930      0.4923      0.6692
groups_IP_trans        5      0.3826      0.7319      0.6898      0.6813      0.5083      0.7957
groups_LBP_BPI_CETP    5      0.2609      0.8340      0.7263      0.5626      0.3750      0.8170
groups_START           5      0.6923      0.4494      0.8580      0.5625      0.7688      0.4449
groups_lipocalin       5      0.7278      0.4833      0.7113      0.5703      0.7833      0.5083
groups_scp2            5      0.4941      0.7176      0.7931      0.5411      0.6118      0.7647
ALL                   35      0.4997      0.6139      0.7472      0.5910      0.5939      0.6530

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6235      0.6163     0.0734  35
max valid BA                0.6459      0.6319     0.0730  35
best valid F1               0.6200      0.6250     0.0838  35
test BA                     0.5568      0.5459     0.0739  35
test F1                     0.4479      0.4848     0.1592  35
test sensitivity            0.4997      0.5385     0.2436  35
test specificity            0.6139      0.6000     0.2212  35
test precision              0.4652      0.4706     0.1284  35
test loss                   0.7650      0.7193     0.1682  35
FPR (FP/(FP+TN))            0.3861      0.4000     0.2212  35
FNR (FN/(FN+TP))            0.5003      0.4615     0.2436  35

=== abs(sensitivity-specificity) gap: mean=0.3522 median=0.3200 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5944      0.5904     0.0621  5
  max valid BA                0.6073      0.6136     0.0503  5
  best valid F1               0.7129      0.7143     0.0149  5
  test BA                     0.5226      0.5169     0.0236  5
  test F1                     0.5232      0.5672     0.1374  5
  test sensitivity            0.5403      0.5672     0.2037  5
  test specificity            0.5049      0.5246     0.1831  5
  test precision              0.5408      0.5366     0.0280  5
  test loss                   0.7542      0.7402     0.0680  5
  FPR (FP/(FP+TN))            0.4951      0.4754     0.1831  5
  FNR (FN/(FN+TP))            0.4597      0.4328     0.2037  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5808      0.5769     0.0498  5
  max valid BA                0.6192      0.5769     0.0672  5
  best valid F1               0.6778      0.6757     0.0124  5
  test BA                     0.4880      0.4600     0.1119  5
  test F1                     0.4350      0.4583     0.1215  5
  test sensitivity            0.4000      0.4400     0.1356  5
  test specificity            0.5760      0.6000     0.2308  5
  test precision              0.5030      0.4375     0.1701  5
  test loss                   0.7351      0.7398     0.0257  5
  FPR (FP/(FP+TN))            0.4240      0.4000     0.2308  5
  FNR (FN/(FN+TP))            0.6000      0.5600     0.1356  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6520      0.6627     0.0580  5
  max valid BA                0.6725      0.6751     0.0518  5
  best valid F1               0.5842      0.5750     0.0542  5
  test BA                     0.5573      0.5592     0.0415  5
  test F1                     0.3525      0.2857     0.1390  5
  test sensitivity            0.3826      0.1739     0.3003  5
  test specificity            0.7319      0.8511     0.2419  5
  test precision              0.4700      0.4000     0.1851  5
  test loss                   0.9151      0.8233     0.3685  5
  FPR (FP/(FP+TN))            0.2681      0.1489     0.2419  5
  FNR (FN/(FN+TP))            0.6174      0.8261     0.3003  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5960      0.6223     0.0645  5
  max valid BA                0.6274      0.6237     0.0716  5
  best valid F1               0.5197      0.5106     0.1015  5
  test BA                     0.5475      0.5782     0.0552  5
  test F1                     0.2758      0.4000     0.2186  5
  test sensitivity            0.2609      0.3478     0.2280  5
  test specificity            0.8340      0.8085     0.1271  5
  test precision              0.3746      0.4706     0.2109  5
  test loss                   0.8798      0.9118     0.1386  5
  FPR (FP/(FP+TN))            0.1660      0.1915     0.1271  5
  FNR (FN/(FN+TP))            0.7391      0.6522     0.2280  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6068      0.6107     0.0114  5
  max valid BA                0.6168      0.6212     0.0157  5
  best valid F1               0.6169      0.6196     0.0169  5
  test BA                     0.5709      0.5990     0.0594  5
  test F1                     0.5649      0.5844     0.0619  5
  test sensitivity            0.6923      0.6923     0.0967  5
  test specificity            0.4494      0.4719     0.0745  5
  test precision              0.4785      0.5056     0.0481  5
  test loss                   0.7376      0.7139     0.0749  5
  FPR (FP/(FP+TN))            0.5506      0.5281     0.0745  5
  FNR (FN/(FN+TP))            0.3077      0.3077     0.0967  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6458      0.6389     0.1036  5
  max valid BA                0.6694      0.6528     0.1145  5
  best valid F1               0.6003      0.5607     0.0937  5
  test BA                     0.6056      0.6597     0.0918  5
  test F1                     0.5320      0.5745     0.0726  5
  test sensitivity            0.7278      0.7222     0.1488  5
  test specificity            0.4833      0.5694     0.2608  5
  test precision              0.4306      0.4655     0.0835  5
  test loss                   0.6842      0.6823     0.0493  5
  FPR (FP/(FP+TN))            0.5167      0.4306     0.2608  5
  FNR (FN/(FN+TP))            0.2722      0.2778     0.1488  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6882      0.6912     0.0978  5
  max valid BA                0.7088      0.7206     0.0795  5
  best valid F1               0.6283      0.6341     0.0850  5
  test BA                     0.6059      0.6176     0.0544  5
  test F1                     0.4515      0.5000     0.1548  5
  test sensitivity            0.4941      0.5294     0.2375  5
  test specificity            0.7176      0.7059     0.1325  5
  test precision              0.4585      0.4643     0.0368  5
  test loss                   0.6493      0.6463     0.0176  5
  FPR (FP/(FP+TN))            0.2824      0.2941     0.1325  5
  FNR (FN/(FN+TP))            0.5059      0.4706     0.2375  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.630         0.483    0.582       4.0              0.365         0.522     5.0               0.449          0.607
GLTP                     0.605         0.521    0.505       2.0              0.511         0.504     3.0               0.523          0.529
IP_trans                 0.722         0.681    0.630       3.0              0.677         0.716     2.4               0.590          0.613
LBP_BPI_CETP             0.719         0.798    0.659       2.0              0.798         0.667     1.6               0.784          0.642
START                    0.576         0.508    0.558       3.0              0.475         0.487     4.0               0.535          0.616
lipocalin                0.565         0.334    0.574       5.0              0.252         0.586     2.2               0.647          0.593
scp2                     0.651         0.488    0.697       2.8              0.592         0.597     2.6               0.649          0.648

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.545               0.499                  0.066                     0.151
net_AUC           0.601               0.614                  0.085                     0.065

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.524               0.493                  0.065                     0.185
net_AUC_prot           0.583               0.561                  0.092                     0.086

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.597               0.581                  0.085                     0.109
net_AUC_lipid           0.607               0.593                  0.113                     0.039

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.537      0.524     0.549
10     0.545  0.558      0.524     0.545
49     0.545  0.575      0.524     0.556
51     0.545  0.582      0.524     0.565
120    0.545  0.601      0.524     0.583

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.619         0.669      0.050          0.655              0.700           0.045
10        0.619         0.665      0.045          0.655              0.691           0.036
49        0.619         0.672      0.053          0.655              0.695           0.040
51        0.619         0.676      0.057          0.655              0.704           0.049
120       0.619         0.673      0.054          0.655              0.702           0.047

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.483  0.582      0.365     0.522     0.539         0.602      0.063          0.614              0.661           0.047
GLTP          0.521  0.505      0.511     0.504     0.542         0.594      0.052          0.565              0.588           0.023
IP_trans      0.681  0.630      0.677     0.716     0.681         0.726      0.046          0.692              0.746           0.054
LBP_BPI_CETP  0.798  0.659      0.798     0.667     0.798         0.799      0.001          0.801              0.810           0.009
START         0.508  0.558      0.475     0.487     0.536         0.593      0.057          0.604              0.637           0.032
lipocalin     0.334  0.574      0.252     0.586     0.666         0.716      0.050          0.672              0.753           0.081
scp2          0.488  0.697      0.592     0.597     0.572         0.681      0.109          0.636              0.720           0.084

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.545               0.499                  0.066                     0.151
net               0.601               0.614                  0.085                     0.065
fit_chem          0.619               0.580                  0.052                     0.100
fit_chem_net      0.673               0.674                  0.064                     0.080
increment         0.054               0.026                  0.053                     0.032

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.524               0.493                  0.065                     0.185
net_prot               0.583               0.561                  0.092                     0.086
fit_chem_prot          0.655               0.658                  0.053                     0.077
fit_chem_net_prot      0.702               0.718                  0.059                     0.077
increment_prot         0.047               0.036                  0.047                     0.028
```
