# descriptors_coarse_hydrocore

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_coarse_hydrocore'
rows: 12

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       2      0.4776      0.6148      0.5486      0.5339      0.5448      0.6290
groups_GLTP            3      0.7867      0.3867      0.6830      0.4337      0.8205      0.4103
groups_IP_trans        1      0.9130      0.2128      0.7741      0.3361      0.8333      0.3404
groups_LBP_BPI_CETP    2      0.6739      0.8511      0.5606      0.5483      0.7500      0.7979
groups_START           3      0.3744      0.7191      0.3868      0.6212      0.4271      0.7715
groups_scp2            1      0.8824      0.1765      0.4452      0.4538      1.0000      0.2647
ALL                   12      0.6318      0.5532      0.5539      0.5099      0.6805      0.5837

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6321      0.6083     0.0754  12
max valid BA                0.6453      0.6253     0.0766  12
best valid F1               0.6323      0.6269     0.0998  12
test BA                     0.5925      0.5778     0.0990  12
test F1                     0.5508      0.5168     0.1229  12
test sensitivity            0.6318      0.5581     0.2482  12
test specificity            0.5532      0.5072     0.2650  12
test precision              0.5514      0.5490     0.1462  12
test loss                   0.6954      0.6934     0.0264  12
FPR (FP/(FP+TN))            0.4468      0.4928     0.2650  12
FNR (FN/(FN+TP))            0.3682      0.4419     0.2482  12

=== abs(sensitivity-specificity) gap: mean=0.3717 median=0.3143 n=12 ===

=== By group ===
groups_CRAL-TRIO (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5869      0.5869     0.0475  2
  max valid BA                0.6156      0.6156     0.0395  2
  best valid F1               0.6933      0.6933     0.0167  2
  test BA                     0.5462      0.5462     0.0658  2
  test F1                     0.5231      0.5231     0.0112  2
  test sensitivity            0.4776      0.4776     0.0422  2
  test specificity            0.6148      0.6148     0.1739  2
  test precision              0.5876      0.5876     0.0913  2
  test loss                   0.6878      0.6878     0.0086  2
  FPR (FP/(FP+TN))            0.3852      0.3852     0.1739  2
  FNR (FN/(FN+TP))            0.5224      0.5224     0.0422  2

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6154      0.5962     0.0509  3
  max valid BA                0.6282      0.6154     0.0400  3
  best valid F1               0.6859      0.7042     0.0784  3
  test BA                     0.5867      0.6200     0.0945  3
  test F1                     0.6374      0.7077     0.1563  3
  test sensitivity            0.7867      0.9200     0.3029  3
  test specificity            0.3867      0.3200     0.1155  3
  test precision              0.5495      0.5750     0.0625  3
  test loss                   0.7085      0.7003     0.0223  3
  FPR (FP/(FP+TN))            0.6133      0.6800     0.1155  3
  FNR (FN/(FN+TP))            0.2133      0.0800     0.3029  3

groups_IP_trans (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5869      0.5869     0.0000  1
  max valid BA                0.5975      0.5975     0.0000  1
  best valid F1               0.5405      0.5405     0.0000  1
  test BA                     0.5629      0.5629     0.0000  1
  test F1                     0.5185      0.5185     0.0000  1
  test sensitivity            0.9130      0.9130     0.0000  1
  test specificity            0.2128      0.2128     0.0000  1
  test precision              0.3621      0.3621     0.0000  1
  test loss                   0.6930      0.6930     0.0000  1
  FPR (FP/(FP+TN))            0.7872      0.7872     0.0000  1
  FNR (FN/(FN+TP))            0.0870      0.0870     0.0000  1

groups_LBP_BPI_CETP (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7739      0.7739     0.0520  2
  max valid BA                0.7897      0.7897     0.0743  2
  best valid F1               0.7191      0.7191     0.0923  2
  test BA                     0.7625      0.7625     0.0612  2
  test F1                     0.6807      0.6807     0.0827  2
  test sensitivity            0.6739      0.6739     0.0922  2
  test specificity            0.8511      0.8511     0.0301  2
  test precision              0.6877      0.6877     0.0727  2
  test loss                   0.6643      0.6643     0.0183  2
  FPR (FP/(FP+TN))            0.1489      0.1489     0.0301  2
  FNR (FN/(FN+TP))            0.3261      0.3261     0.0922  2

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5993      0.5861     0.0314  3
  max valid BA                0.6015      0.5927     0.0303  3
  best valid F1               0.5295      0.5654     0.0839  3
  test BA                     0.5467      0.5385     0.0656  3
  test F1                     0.4236      0.4174     0.0140  3
  test sensitivity            0.3744      0.3692     0.1001  3
  test specificity            0.7191      0.7079     0.2305  3
  test precision              0.5687      0.4800     0.2191  3
  test loss                   0.6897      0.6943     0.0105  3
  FPR (FP/(FP+TN))            0.2809      0.2921     0.2305  3
  FNR (FN/(FN+TP))            0.6256      0.6308     0.1001  3

groups_scp2 (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6324      0.6324     0.0000  1
  max valid BA                0.6471      0.6471     0.0000  1
  best valid F1               0.5763      0.5763     0.0000  1
  test BA                     0.5294      0.5294     0.0000  1
  test F1                     0.5000      0.5000     0.0000  1
  test sensitivity            0.8824      0.8824     0.0000  1
  test specificity            0.1765      0.1765     0.0000  1
  test precision              0.3488      0.3488     0.0000  1
  test loss                   0.7536      0.7536     0.0000  1
  FPR (FP/(FP+TN))            0.8235      0.8235     0.0000  1
  FNR (FN/(FN+TP))            0.1176      0.1176     0.0000  1
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.630         0.484    0.478       4.0              0.369         0.458     5.0               0.458          0.448
GLTP                     0.605         0.521    0.540       2.0              0.512         0.519     3.0               0.523          0.549
IP_trans                 0.722         0.680    0.658       3.0              0.677         0.665     2.4               0.590          0.591
LBP_BPI_CETP             0.719         0.798    0.764       2.0              0.798         0.760     1.6               0.784          0.730
START                    0.576         0.508    0.446       3.0              0.474         0.489     4.0               0.536          0.531
lipocalin                0.565         0.331    0.495       5.0              0.246         0.445     2.2               0.646          0.788
scp2                     0.651         0.489    0.431       2.8              0.593         0.437     2.6               0.642          0.537

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.545               0.503                  0.065                     0.151
net_AUC           0.545               0.527                  0.085                     0.123

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.524               0.493                  0.065                     0.186
net_AUC_prot           0.539               0.497                  0.085                     0.125

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.597               0.581                  0.085                     0.106
net_AUC_lipid           0.596               0.568                  0.090                     0.120

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.435      0.524     0.460
10     0.545  0.555      0.524     0.555
49     0.545  0.553      0.524     0.555
51     0.545  0.554      0.524     0.557
120    0.545  0.545      0.524     0.539

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.618         0.675      0.057          0.653              0.703           0.050
10        0.618         0.662      0.044          0.653              0.695           0.042
49        0.618         0.650      0.032          0.653              0.685           0.031
51        0.618         0.653      0.035          0.653              0.687           0.034
120       0.618         0.657      0.039          0.653              0.689           0.036

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.484  0.478      0.369     0.458     0.539         0.580      0.041          0.613              0.639           0.026
GLTP          0.521  0.540      0.512     0.519     0.543         0.618      0.075          0.565              0.634           0.069
IP_trans      0.680  0.658      0.677     0.665     0.680         0.686      0.006          0.693              0.701           0.008
LBP_BPI_CETP  0.798  0.764      0.798     0.760     0.798         0.809      0.011          0.801              0.816           0.014
START         0.508  0.446      0.474     0.489     0.536         0.601      0.065          0.606              0.633           0.028
lipocalin     0.331  0.495      0.246     0.445     0.669         0.705      0.036          0.673              0.738           0.065
scp2          0.489  0.431      0.593     0.437     0.562         0.603      0.041          0.622              0.665           0.043

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.545               0.503                  0.065                     0.151
net               0.545               0.527                  0.085                     0.123
fit_chem          0.618               0.590                  0.052                     0.101
fit_chem_net      0.657               0.649                  0.052                     0.081
increment         0.039               0.025                  0.036                     0.025

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.524               0.493                  0.065                     0.186
net_prot               0.539               0.497                  0.085                     0.125
fit_chem_prot          0.653               0.662                  0.055                     0.078
fit_chem_net_prot      0.689               0.681                  0.053                     0.068
increment_prot         0.036               0.027                  0.030                     0.024
```
