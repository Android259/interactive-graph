# geometric_edge_mlp_protgeom8_no_buriedness_q50

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom8_no_buriedness_q50'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.7343      0.3574      0.7686      0.5813      0.7791      0.4097
groups_GLTP            5      0.3840      0.6320      0.7692      0.5361      0.4538      0.7154
groups_IP_trans        5      0.5565      0.6468      0.6314      0.6311      0.6750      0.6511
groups_LBP_BPI_CETP    5      0.2348      0.8255      0.8139      0.5103      0.3500      0.8383
groups_START           5      0.6923      0.4427      0.8273      0.5529      0.7156      0.4472
groups_lipocalin       5      0.6167      0.6139      0.7199      0.5495      0.6556      0.6194
groups_scp2            5      0.5059      0.6882      0.7781      0.5286      0.6235      0.7529
ALL                   35      0.5321      0.6009      0.7583      0.5557      0.6075      0.6334

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6205      0.6154     0.0785  35
max valid BA                0.6509      0.6330     0.0769  35
best valid F1               0.6238      0.6545     0.0842  35
test BA                     0.5665      0.5600     0.0727  35
test F1                     0.4595      0.5143     0.1819  35
test sensitivity            0.5321      0.5652     0.2848  35
test specificity            0.6009      0.6170     0.2636  35
test precision              0.4687      0.4857     0.1253  35
test loss                   0.7132      0.6967     0.0832  35
FPR (FP/(FP+TN))            0.3991      0.3830     0.2636  35
FNR (FN/(FN+TP))            0.4679      0.4348     0.2848  35

=== abs(sensitivity-specificity) gap: mean=0.4339 median=0.3889 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5944      0.5882     0.0492  5
  max valid BA                0.6105      0.6201     0.0520  5
  best valid F1               0.7108      0.7104     0.0132  5
  test BA                     0.5459      0.5416     0.0150  5
  test F1                     0.6249      0.6587     0.0649  5
  test sensitivity            0.7343      0.8060     0.1913  5
  test specificity            0.3574      0.3115     0.2085  5
  test precision              0.5603      0.5625     0.0187  5
  test loss                   0.7144      0.6895     0.0405  5
  FPR (FP/(FP+TN))            0.6426      0.6885     0.2085  5
  FNR (FN/(FN+TP))            0.2657      0.1940     0.1913  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5846      0.5577     0.0586  5
  max valid BA                0.6115      0.5962     0.0599  5
  best valid F1               0.6738      0.6753     0.0074  5
  test BA                     0.5080      0.5000     0.0610  5
  test F1                     0.3954      0.4211     0.1635  5
  test sensitivity            0.3840      0.3200     0.3106  5
  test specificity            0.6320      0.8000     0.3649  5
  test precision              0.5322      0.5000     0.1076  5
  test loss                   0.7886      0.7657     0.0631  5
  FPR (FP/(FP+TN))            0.3680      0.2000     0.3649  5
  FNR (FN/(FN+TP))            0.6160      0.6800     0.3106  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6630      0.6525     0.0722  5
  max valid BA                0.6888      0.6826     0.0630  5
  best valid F1               0.6103      0.6061     0.0667  5
  test BA                     0.6017      0.6230     0.0838  5
  test F1                     0.4597      0.5098     0.1544  5
  test sensitivity            0.5565      0.5652     0.2891  5
  test specificity            0.6468      0.6170     0.1531  5
  test precision              0.4260      0.4468     0.0607  5
  test loss                   0.6590      0.6517     0.0659  5
  FPR (FP/(FP+TN))            0.3532      0.3830     0.1531  5
  FNR (FN/(FN+TP))            0.4435      0.4348     0.2891  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5941      0.5931     0.0664  5
  max valid BA                0.6681      0.6738     0.0567  5
  best valid F1               0.5478      0.5867     0.1162  5
  test BA                     0.5302      0.5111     0.0414  5
  test F1                     0.2332      0.1875     0.2087  5
  test sensitivity            0.2348      0.1304     0.2509  5
  test specificity            0.8255      0.8723     0.1711  5
  test precision              0.3312      0.4062     0.1944  5
  test loss                   0.7725      0.7822     0.0845  5
  FPR (FP/(FP+TN))            0.1745      0.1277     0.1711  5
  FNR (FN/(FN+TP))            0.7652      0.8696     0.2509  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5814      0.5726     0.0488  5
  max valid BA                0.6008      0.6066     0.0531  5
  best valid F1               0.5968      0.6190     0.0612  5
  test BA                     0.5675      0.5738     0.0438  5
  test F1                     0.5610      0.5562     0.0588  5
  test sensitivity            0.6923      0.7231     0.1167  5
  test specificity            0.4427      0.4270     0.0634  5
  test precision              0.4740      0.4881     0.0321  5
  test loss                   0.7538      0.7081     0.0983  5
  FPR (FP/(FP+TN))            0.5573      0.5730     0.0634  5
  FNR (FN/(FN+TP))            0.3077      0.2769     0.1167  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6375      0.6806     0.1271  5
  max valid BA                0.6681      0.6806     0.1231  5
  best valid F1               0.6057      0.6018     0.1011  5
  test BA                     0.6153      0.6389     0.1193  5
  test F1                     0.4958      0.5660     0.1889  5
  test sensitivity            0.6167      0.6389     0.3071  5
  test specificity            0.6139      0.7639     0.3813  5
  test precision              0.5193      0.5641     0.1541  5
  test loss                   0.6559      0.6607     0.0643  5
  FPR (FP/(FP+TN))            0.3861      0.2361     0.3813  5
  FNR (FN/(FN+TP))            0.3833      0.3611     0.3071  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6882      0.6765     0.0685  5
  max valid BA                0.7088      0.6912     0.0708  5
  best valid F1               0.6212      0.6047     0.0825  5
  test BA                     0.5971      0.6176     0.0629  5
  test F1                     0.4463      0.5143     0.1598  5
  test sensitivity            0.5059      0.5294     0.2650  5
  test specificity            0.6882      0.7353     0.1723  5
  test precision              0.4377      0.4400     0.0966  5
  test loss                   0.6481      0.6508     0.0357  5
  FPR (FP/(FP+TN))            0.3118      0.2647     0.1723  5
  FNR (FN/(FN+TP))            0.4941      0.4706     0.2650  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.630         0.484    0.574       4.0              0.369         0.513     5.0               0.458          0.567
GLTP                     0.605         0.521    0.510       2.0              0.512         0.507     3.0               0.523          0.540
IP_trans                 0.722         0.680    0.614       3.0              0.677         0.692     2.4               0.590          0.571
LBP_BPI_CETP             0.719         0.798    0.645       2.0              0.798         0.672     1.6               0.784          0.608
START                    0.576         0.508    0.549       3.0              0.474         0.489     4.0               0.536          0.639
lipocalin                0.565         0.331    0.580       5.0              0.246         0.642     2.2               0.646          0.541
scp2                     0.651         0.489    0.703       2.8              0.593         0.639     2.6               0.642          0.660

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.545               0.503                  0.065                     0.151
net_AUC           0.596               0.573                  0.075                     0.064

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.524               0.493                  0.065                     0.186
net_AUC_prot           0.593               0.560                  0.081                     0.087

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.597               0.581                  0.085                     0.106
net_AUC_lipid           0.589               0.565                  0.112                     0.047

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.535      0.524     0.543
10     0.545  0.560      0.524     0.551
49     0.545  0.563      0.524     0.546
51     0.545  0.578      0.524     0.563
120    0.545  0.596      0.524     0.593

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.618         0.657      0.039          0.653              0.689           0.036
10        0.618         0.672      0.054          0.653              0.698           0.044
49        0.618         0.671      0.053          0.653              0.695           0.042
51        0.618         0.682      0.064          0.653              0.712           0.058
120       0.618         0.671      0.053          0.653              0.703           0.049

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.484  0.574      0.369     0.513     0.539         0.599      0.061          0.613              0.667           0.053
GLTP          0.521  0.510      0.512     0.507     0.543         0.593      0.050          0.565              0.604           0.039
IP_trans      0.680  0.614      0.677     0.692     0.680         0.720      0.039          0.693              0.743           0.050
LBP_BPI_CETP  0.798  0.645      0.798     0.672     0.798         0.795     -0.003          0.801              0.805           0.004
START         0.508  0.549      0.474     0.489     0.536         0.593      0.057          0.606              0.639           0.033
lipocalin     0.331  0.580      0.246     0.642     0.669         0.704      0.035          0.673              0.725           0.051
scp2          0.489  0.703      0.593     0.639     0.562         0.697      0.135          0.622              0.736           0.114

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.545               0.503                  0.065                     0.151
net               0.596               0.573                  0.075                     0.064
fit_chem          0.618               0.590                  0.052                     0.101
fit_chem_net      0.671               0.659                  0.057                     0.078
increment         0.053               0.027                  0.046                     0.042

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.524               0.493                  0.065                     0.186
net_prot               0.593               0.560                  0.081                     0.087
fit_chem_prot          0.653               0.662                  0.055                     0.078
fit_chem_net_prot      0.703               0.704                  0.059                     0.069
increment_prot         0.049               0.016                  0.053                     0.033
```
