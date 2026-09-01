# descriptors_no_extent_coarse_add_no_chain_lipprop

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_add_no_chain_lipprop'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4030      0.6262      0.5029      0.5741      0.4537      0.6387
groups_GLTP            5      0.4720      0.5120      0.6067      0.5093      0.6077      0.6538
groups_IP_trans        5      0.5391      0.6255      0.4799      0.6030      0.6083      0.6426
groups_LBP_BPI_CETP    5      0.4522      0.8340      0.3938      0.7170      0.5000      0.7872
groups_START           5      0.3200      0.6742      0.4020      0.6635      0.3594      0.7079
groups_lipocalin       5      0.5111      0.5389      0.6281      0.4853      0.5444      0.5472
groups_scp2            5      0.4588      0.6471      0.4770      0.6520      0.4471      0.6529
ALL                   35      0.4509      0.6368      0.4986      0.6006      0.5029      0.6615

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5822      0.5577     0.0802  35
max valid BA                0.5985      0.5837     0.0805  35
best valid F1               0.5220      0.5437     0.1391  35
test BA                     0.5439      0.5287     0.0844  35
test F1                     0.3887      0.4727     0.2143  35
test sensitivity            0.4509      0.4800     0.3032  35
test specificity            0.6368      0.6400     0.2396  35
test precision              0.4358      0.4483     0.1422  31
test loss                   0.6961      0.6934     0.0385  35
FPR (FP/(FP+TN))            0.3632      0.3600     0.2396  35
FNR (FN/(FN+TP))            0.5491      0.5200     0.3032  35

=== abs(sensitivity-specificity) gap: mean=0.4390 median=0.3824 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5462      0.5406     0.0458  5
  max valid BA                0.5628      0.5469     0.0448  5
  best valid F1               0.5307      0.6065     0.1729  5
  test BA                     0.5146      0.5311     0.0598  5
  test F1                     0.4158      0.5620     0.2334  5
  test sensitivity            0.4030      0.5075     0.2818  5
  test specificity            0.6262      0.6721     0.2032  5
  test precision              0.4966      0.5465     0.1342  5
  test loss                   0.7104      0.7011     0.0277  5
  FPR (FP/(FP+TN))            0.3738      0.3279     0.2032  5
  FNR (FN/(FN+TP))            0.5970      0.4925     0.2818  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6308      0.6538     0.0854  5
  max valid BA                0.6462      0.6538     0.0776  5
  best valid F1               0.6633      0.6552     0.0638  5
  test BA                     0.4920      0.5000     0.0593  5
  test F1                     0.4803      0.4727     0.0575  5
  test sensitivity            0.4720      0.4800     0.0769  5
  test specificity            0.5120      0.5200     0.1246  5
  test precision              0.4950      0.5000     0.0570  5
  test loss                   0.6913      0.6927     0.0059  5
  FPR (FP/(FP+TN))            0.4880      0.4800     0.1246  5
  FNR (FN/(FN+TP))            0.5280      0.5200     0.0769  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6254      0.5971     0.0994  5
  max valid BA                0.6377      0.6192     0.0935  5
  best valid F1               0.5642      0.5542     0.0847  5
  test BA                     0.5823      0.5934     0.0701  5
  test F1                     0.4125      0.5000     0.2342  5
  test sensitivity            0.5391      0.6522     0.3114  5
  test specificity            0.6255      0.6596     0.2578  5
  test precision              0.4262      0.4198     0.0733  4
  test loss                   0.6878      0.6853     0.0084  5
  FPR (FP/(FP+TN))            0.3745      0.3404     0.2578  5
  FNR (FN/(FN+TP))            0.4609      0.3478     0.3114  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6436      0.6622     0.1077  5
  max valid BA                0.6641      0.7145     0.1052  5
  best valid F1               0.5468      0.6349     0.1801  5
  test BA                     0.6431      0.6457     0.1056  5
  test F1                     0.4381      0.5000     0.2670  5
  test sensitivity            0.4522      0.3913     0.3404  5
  test specificity            0.8340      0.9149     0.1685  5
  test precision              0.6139      0.6492     0.1128  4
  test loss                   0.6546      0.6657     0.0570  5
  FPR (FP/(FP+TN))            0.1660      0.0851     0.1685  5
  FNR (FN/(FN+TP))            0.5478      0.6087     0.3404  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5336      0.5474     0.0460  5
  max valid BA                0.5394      0.5643     0.0498  5
  best valid F1               0.4793      0.4633     0.0918  5
  test BA                     0.4971      0.4903     0.0429  5
  test F1                     0.2741      0.3178     0.2442  5
  test sensitivity            0.3200      0.2615     0.3756  5
  test specificity            0.6742      0.7191     0.3244  5
  test precision              0.3807      0.3821     0.0674  4
  test loss                   0.7400      0.7315     0.0542  5
  FPR (FP/(FP+TN))            0.3258      0.2809     0.3244  5
  FNR (FN/(FN+TP))            0.6800      0.7385     0.3756  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5458      0.5278     0.0424  5
  max valid BA                0.5778      0.5486     0.0663  5
  best valid F1               0.4274      0.4222     0.1565  5
  test BA                     0.5250      0.5417     0.0723  5
  test F1                     0.3491      0.4762     0.2321  5
  test sensitivity            0.5111      0.6389     0.3980  5
  test specificity            0.5389      0.5556     0.3070  5
  test precision              0.2748      0.3623     0.1701  5
  test loss                   0.6948      0.6912     0.0189  5
  FPR (FP/(FP+TN))            0.4611      0.4444     0.3070  5
  FNR (FN/(FN+TP))            0.4889      0.3611     0.3980  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5294     0.0494  5
  max valid BA                0.5618      0.5441     0.0458  5
  best valid F1               0.4424      0.4706     0.0926  5
  test BA                     0.5529      0.5000     0.0916  5
  test F1                     0.3514      0.3030     0.2404  5
  test sensitivity            0.4588      0.2941     0.3799  5
  test specificity            0.6471      0.6765     0.2334  5
  test precision              0.3734      0.3563     0.0758  4
  test loss                   0.6941      0.6954     0.0165  5
  FPR (FP/(FP+TN))            0.3529      0.3235     0.2334  5
  FNR (FN/(FN+TP))            0.5412      0.7059     0.3799  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (aromatic_share,hbond,heavy,occupancy,polar_share,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.449         0.505    0.545              0.496         0.532
GLTP                     0.496         0.740    0.550              0.741         0.573
IP_trans                 0.476         0.499    0.578              0.507         0.584
LBP_BPI_CETP             0.515         0.730    0.540              0.744         0.530
START                    0.444         0.483    0.490              0.500         0.512
lipocalin                0.394         0.584    0.416              0.588         0.629
scp2                     0.448         0.478    0.471              0.530         0.496

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.574               0.542                  0.077                     0.115
net_AUC           0.513               0.497                  0.109                     0.056

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.587               0.555                  0.076                     0.111
net_AUC_pair           0.551               0.571                  0.111                     0.047

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.574  0.501      0.587     0.497
10     0.574  0.518      0.587     0.524
49     0.574  0.507      0.587     0.532
51     0.574  0.511      0.587     0.536
120    0.574  0.513      0.587     0.551

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.606         0.671      0.065
10        0.606         0.659      0.053
49        0.606         0.650      0.044
51        0.606         0.652      0.046
120       0.606         0.652      0.046

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.505  0.545      0.496     0.532     0.531         0.571      0.040
GLTP          0.740  0.550      0.741     0.573     0.740         0.746      0.006
IP_trans      0.499  0.578      0.507     0.584     0.542         0.634      0.092
LBP_BPI_CETP  0.730  0.540      0.744     0.530     0.730         0.762      0.031
START         0.483  0.490      0.500     0.512     0.551         0.619      0.067
lipocalin     0.584  0.416      0.588     0.629     0.586         0.623      0.037
scp2          0.478  0.471      0.530     0.496     0.561         0.609      0.048

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.574               0.542                  0.077                     0.115
net               0.513               0.497                  0.109                     0.056
fit_chem          0.606               0.573                  0.063                     0.090
fit_chem_net      0.652               0.633                  0.069                     0.073
increment         0.046               0.030                  0.060                     0.027

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.587               0.555                  0.076                     0.111
net_pair       0.551               0.571                  0.111                     0.047
```
