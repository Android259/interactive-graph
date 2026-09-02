# geometric_edge_mlp_protgeom8_no_depth_q10

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom8_no_depth_q10'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.7463      0.4066      0.7594      0.5798      0.7194      0.4323
groups_GLTP            5      0.3840      0.6240      0.7979      0.6096      0.4385      0.7385
groups_IP_trans        5      0.3652      0.7830      0.6672      0.5964      0.5000      0.8085
groups_LBP_BPI_CETP    5      0.2870      0.7915      0.7979      0.5111      0.3250      0.7957
groups_START           5      0.6462      0.4629      0.8451      0.5464      0.6906      0.4180
groups_lipocalin       5      0.6944      0.5389      0.6985      0.5682      0.7556      0.5639
groups_scp2            5      0.4588      0.7235      0.7910      0.5510      0.5647      0.7824
ALL                   35      0.5117      0.6186      0.7653      0.5661      0.5705      0.6485

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6095      0.5918     0.0855  35
max valid BA                0.6523      0.6321     0.0780  35
best valid F1               0.6222      0.6383     0.0988  35
test BA                     0.5652      0.5564     0.0674  35
test F1                     0.4502      0.5000     0.1783  35
test sensitivity            0.5117      0.4776     0.2864  35
test specificity            0.6186      0.6393     0.2431  35
test precision              0.4808      0.4583     0.1445  35
test loss                   0.7279      0.7276     0.0885  35
FPR (FP/(FP+TN))            0.3814      0.3607     0.2431  35
FNR (FN/(FN+TP))            0.4883      0.5224     0.2864  35

=== abs(sensitivity-specificity) gap: mean=0.4508 median=0.4000 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5758      0.5693     0.0433  5
  max valid BA                0.6184      0.6130     0.0597  5
  best valid F1               0.7168      0.7182     0.0156  5
  test BA                     0.5764      0.5782     0.0463  5
  test F1                     0.6467      0.6797     0.0690  5
  test sensitivity            0.7463      0.7761     0.1625  5
  test specificity            0.4066      0.4426     0.1842  5
  test precision              0.5842      0.5926     0.0368  5
  test loss                   0.7183      0.7356     0.0392  5
  FPR (FP/(FP+TN))            0.5934      0.5574     0.1842  5
  FNR (FN/(FN+TP))            0.2537      0.2239     0.1625  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5885      0.5577     0.0845  5
  max valid BA                0.6231      0.5962     0.0845  5
  best valid F1               0.6802      0.6753     0.0207  5
  test BA                     0.5040      0.4600     0.0865  5
  test F1                     0.4324      0.4390     0.1025  5
  test sensitivity            0.3840      0.3600     0.1220  5
  test specificity            0.6240      0.6400     0.1802  5
  test precision              0.5167      0.4667     0.1363  5
  test loss                   0.7831      0.7794     0.0411  5
  FPR (FP/(FP+TN))            0.3760      0.3600     0.1802  5
  FNR (FN/(FN+TP))            0.6160      0.6400     0.1220  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6543      0.6228     0.0800  5
  max valid BA                0.6928      0.7039     0.0636  5
  best valid F1               0.6125      0.6250     0.0685  5
  test BA                     0.5741      0.5467     0.0641  5
  test F1                     0.3877      0.3590     0.1239  5
  test sensitivity            0.3652      0.3043     0.1782  5
  test specificity            0.7830      0.7872     0.0758  5
  test precision              0.4441      0.4375     0.0554  5
  test loss                   0.6759      0.6459     0.0991  5
  FPR (FP/(FP+TN))            0.2170      0.2128     0.0758  5
  FNR (FN/(FN+TP))            0.6348      0.6957     0.1782  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5604      0.5412     0.0373  5
  max valid BA                0.6434      0.6538     0.0596  5
  best valid F1               0.5054      0.5797     0.1682  5
  test BA                     0.5392      0.5342     0.0445  5
  test F1                     0.2530      0.2857     0.2173  5
  test sensitivity            0.2870      0.2174     0.3486  5
  test specificity            0.7915      0.8511     0.2633  5
  test precision              0.3493      0.4167     0.1993  5
  test loss                   0.8586      0.8116     0.1150  5
  FPR (FP/(FP+TN))            0.2085      0.1489     0.2633  5
  FNR (FN/(FN+TP))            0.7130      0.7826     0.3486  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5543      0.5701     0.0588  5
  max valid BA                0.6034      0.6212     0.0355  5
  best valid F1               0.6032      0.6203     0.0400  5
  test BA                     0.5545      0.5461     0.0351  5
  test F1                     0.5246      0.5778     0.1065  5
  test sensitivity            0.6462      0.8000     0.2493  5
  test specificity            0.4629      0.3596     0.1912  5
  test precision              0.4649      0.4583     0.0164  5
  test loss                   0.7117      0.7042     0.0365  5
  FPR (FP/(FP+TN))            0.5371      0.6404     0.1912  5
  FNR (FN/(FN+TP))            0.3538      0.2000     0.2493  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6597      0.7222     0.1228  5
  max valid BA                0.6792      0.7222     0.1161  5
  best valid F1               0.6047      0.6383     0.0988  5
  test BA                     0.6167      0.6597     0.0964  5
  test F1                     0.4824      0.5800     0.2166  5
  test sensitivity            0.6944      0.8056     0.3638  5
  test specificity            0.5389      0.5278     0.3471  5
  test precision              0.5546      0.4688     0.2580  5
  test loss                   0.6774      0.6610     0.0340  5
  FPR (FP/(FP+TN))            0.4611      0.4722     0.3471  5
  FNR (FN/(FN+TP))            0.3056      0.1944     0.3638  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6735      0.6765     0.0854  5
  max valid BA                0.7059      0.7059     0.0812  5
  best valid F1               0.6324      0.6222     0.0665  5
  test BA                     0.5912      0.6176     0.0481  5
  test F1                     0.4243      0.5000     0.1517  5
  test sensitivity            0.4588      0.5294     0.2475  5
  test specificity            0.7235      0.7059     0.1565  5
  test precision              0.4516      0.4444     0.0377  5
  test loss                   0.6701      0.6666     0.0374  5
  FPR (FP/(FP+TN))            0.2765      0.2941     0.1565  5
  FNR (FN/(FN+TP))            0.5412      0.4706     0.2475  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.630         0.484    0.575       4.0              0.369         0.523     5.0               0.458          0.591
GLTP                     0.605         0.521    0.545       2.0              0.512         0.508     3.0               0.523          0.616
IP_trans                 0.722         0.680    0.639       3.0              0.677         0.714     2.4               0.590          0.596
LBP_BPI_CETP             0.719         0.798    0.643       2.0              0.798         0.659     1.6               0.784          0.634
START                    0.576         0.508    0.538       3.0              0.474         0.488     4.0               0.536          0.624
lipocalin                0.565         0.331    0.553       5.0              0.246         0.619     2.2               0.646          0.560
scp2                     0.651         0.489    0.703       2.8              0.593         0.626     2.6               0.642          0.689

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.545               0.503                  0.065                     0.151
net_AUC           0.599               0.605                  0.069                     0.063

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.524               0.493                  0.065                     0.186
net_AUC_prot           0.591               0.555                  0.076                     0.086

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.597               0.581                  0.085                     0.106
net_AUC_lipid           0.616               0.618                  0.121                     0.041

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.540      0.524     0.550
10     0.545  0.562      0.524     0.555
49     0.545  0.562      0.524     0.540
51     0.545  0.590      0.524     0.586
120    0.545  0.599      0.524     0.591

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.618         0.660      0.042          0.653              0.691           0.038
10        0.618         0.672      0.054          0.653              0.701           0.048
49        0.618         0.672      0.054          0.653              0.696           0.042
51        0.618         0.680      0.062          0.653              0.706           0.052
120       0.618         0.670      0.052          0.653              0.698           0.044

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.484  0.575      0.369     0.523     0.539         0.599      0.061          0.613              0.669           0.055
GLTP          0.521  0.545      0.512     0.508     0.543         0.577      0.034          0.565              0.575           0.010
IP_trans      0.680  0.639      0.677     0.714     0.680         0.729      0.049          0.693              0.751           0.058
LBP_BPI_CETP  0.798  0.643      0.798     0.659     0.798         0.801      0.002          0.801              0.810           0.009
START         0.508  0.538      0.474     0.488     0.536         0.586      0.050          0.606              0.642           0.036
lipocalin     0.331  0.553      0.246     0.619     0.669         0.700      0.031          0.673              0.720           0.046
scp2          0.489  0.703      0.593     0.626     0.562         0.696      0.134          0.622              0.716           0.094

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.545               0.503                  0.065                     0.151
net               0.599               0.605                  0.069                     0.063
fit_chem          0.618               0.590                  0.052                     0.101
fit_chem_net      0.670               0.675                  0.064                     0.085
increment         0.052               0.024                  0.046                     0.041

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.524               0.493                  0.065                     0.186
net_prot               0.591               0.555                  0.076                     0.086
fit_chem_prot          0.653               0.662                  0.055                     0.078
fit_chem_net_prot      0.698               0.693                  0.065                     0.077
increment_prot         0.044               0.018                  0.044                     0.030
```
