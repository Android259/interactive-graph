# descriptors_head_family_neutral_lipprop_lcs_protbind6_lipvol

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_head_family_neutral_lipprop_lcs_protbind6_lipvol'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.5441      0.6077      0.5741      0.6950      0.5548      0.5813
groups_choline            5      0.4342      0.5386      0.7090      0.5014      0.4964      0.5455
groups_phosphorus_free    5      0.4258      0.5673      0.5162      0.6426      0.3400      0.7469
groups_sphingolipids      5      0.6061      0.4585      0.6204      0.4948      0.6848      0.4950
ALL                      20      0.5025      0.5430      0.6049      0.5835      0.5190      0.5922

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5369      0.5204     0.0463  20
max valid BA                0.5556      0.5453     0.0545  20
best valid F1               0.5081      0.5057     0.0839  20
test BA                     0.5228      0.5105     0.0565  20
test AUC                    0.5083      0.4778     0.1065  20
test AUC in-protein         0.4845      0.4664     0.1602  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.4963      0.4849     0.1331  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.4110      0.4533     0.1500  20
test sensitivity            0.5025      0.4996     0.2945  20
test specificity            0.5430      0.5866     0.2945  20
test precision              0.4156      0.4000     0.1035  20
test loss                   0.8924      0.7213     0.5713  20
FPR (FP/(FP+TN))            0.4570      0.4134     0.2945  20
FNR (FN/(FN+TP))            0.4975      0.5004     0.2945  20

=== abs(sensitivity-specificity) gap: mean=0.4513 median=0.4109 n=20 ===
sensitivity std across seeds (by group): mean=0.2784 median=0.3267 n=4
specificity std across seeds (by group): mean=0.2881 median=0.3514 n=4

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5638      0.5788     0.0382  5
  max valid BA                0.5681      0.5804     0.0417  5
  best valid F1               0.5033      0.5054     0.0049  5
  test BA                     0.5759      0.5690     0.0520  5
  test AUC                    0.5855      0.5869     0.0834  5
  test AUC in-protein         0.4881      0.4866     0.0559  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.5324      0.5276     0.0573  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.4711      0.4685     0.0556  5
  test sensitivity            0.5441      0.5591     0.0525  5
  test specificity            0.6077      0.5792     0.0689  5
  test precision              0.4167      0.4000     0.0626  5
  test loss                   0.6843      0.6878     0.0296  5
  FPR (FP/(FP+TN))            0.3923      0.4208     0.0689  5
  FNR (FN/(FN+TP))            0.4559      0.4409     0.0525  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4994      0.5004     0.0138  5
  max valid BA                0.5210      0.5183     0.0349  5
  best valid F1               0.4429      0.4050     0.0782  5
  test BA                     0.4864      0.4998     0.0243  5
  test AUC                    0.4072      0.3971     0.0538  5
  test AUC in-protein         0.4254      0.3989     0.1281  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.4039      0.4252     0.1006  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.3386      0.2996     0.1333  5
  test sensitivity            0.4342      0.3063     0.3458  5
  test specificity            0.5386      0.5941     0.3367  5
  test precision              0.3413      0.3544     0.0400  5
  test loss                   1.2528      0.7482     1.1038  5
  FPR (FP/(FP+TN))            0.4614      0.4059     0.3367  5
  FNR (FN/(FN+TP))            0.5658      0.6937     0.3458  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5142      0.5007     0.0221  5
  max valid BA                0.5435      0.5347     0.0371  5
  best valid F1               0.4778      0.4865     0.0751  5
  test BA                     0.4966      0.5000     0.0560  5
  test AUC                    0.4727      0.4625     0.0732  5
  test AUC in-protein         0.4256      0.3333     0.2120  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.4713      0.3939     0.1325  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.3315      0.2264     0.2078  5
  test sensitivity            0.4258      0.1935     0.4077  5
  test specificity            0.5673      0.6735     0.3660  5
  test precision              0.3807      0.3875     0.0976  5
  test loss                   0.7717      0.7430     0.1061  5
  FPR (FP/(FP+TN))            0.4327      0.3265     0.3660  5
  FNR (FN/(FN+TP))            0.5742      0.8065     0.4077  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5700      0.5792     0.0579  5
  max valid BA                0.5899      0.5792     0.0801  5
  best valid F1               0.6082      0.6226     0.0515  5
  test BA                     0.5323      0.5588     0.0511  5
  test AUC                    0.5679      0.6105     0.1114  5
  test AUC in-protein         0.5991      0.5355     0.1797  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.5775      0.5029     0.1785  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5030      0.5227     0.1152  5
  test sensitivity            0.6061      0.6970     0.3075  5
  test specificity            0.4585      0.3902     0.3808  5
  test precision              0.5238      0.4898     0.1131  5
  test loss                   0.8609      0.7157     0.2896  5
  FPR (FP/(FP+TN))            0.5415      0.6098     0.3808  5
  FNR (FN/(FN+TP))            0.3939      0.3030     0.3075  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (apolar_sasa_share,aromatic_share,aromatic_share_rim,buriedness_q50,chain,depth_q10,ev14_q10,ev28_q10,experimental_lipid_volume,hbond,heavy,hydropathy_core,hydropathy_mean,hydropathy_rim,pocket_elongation,pocket_flatness,pocket_volume_per_sasa,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                      
anionic                     0.497         0.767    0.582              0.527         0.525
choline                     0.407         0.421    0.375              0.530         0.476
phosphorus_free             0.248         0.459    0.445              0.526         0.486
sphingolipids               0.347         0.382    0.337              0.535         0.426

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.507               0.446                  0.033                     0.176
net_AUC           0.435               0.425                  0.077                     0.108

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.529               0.523                  0.059                     0.004
net_AUC_pair           0.478               0.503                  0.068                     0.041

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.507  0.459      0.529     0.522
10     0.507  0.446      0.529     0.476
49     0.507  0.420      0.529     0.464
51     0.507  0.423      0.529     0.468
120    0.507  0.435      0.529     0.478

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.626         0.644      0.019
10        0.626         0.652      0.026
49        0.626         0.656      0.030
51        0.626         0.653      0.027
120       0.626         0.664      0.038

3. mean over seeds, epoch 120
                  chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                                  
anionic          0.767  0.582      0.527     0.525     0.767         0.770      0.003
choline          0.421  0.375      0.530     0.476     0.579         0.628      0.049
phosphorus_free  0.459  0.445      0.526     0.486     0.539         0.561      0.021
sphingolipids    0.382  0.337      0.535     0.426     0.618         0.698      0.080

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.507               0.446                  0.033                     0.176
net               0.435               0.425                  0.077                     0.108
fit_chem          0.626               0.590                  0.034                     0.099
fit_chem_net      0.664               0.633                  0.061                     0.090
increment         0.038               0.020                  0.042                     0.034

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.529               0.523                  0.059                     0.004
net_pair       0.478               0.503                  0.068                     0.041
```
