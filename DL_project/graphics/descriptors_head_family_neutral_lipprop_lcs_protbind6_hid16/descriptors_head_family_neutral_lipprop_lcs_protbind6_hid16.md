# descriptors_head_family_neutral_lipprop_lcs_protbind6_hid16

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_head_family_neutral_lipprop_lcs_protbind6_hid16'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6774      0.4885      0.5536      0.6108      0.6710      0.5857
groups_choline            5      0.6631      0.3713      0.5942      0.5678      0.4857      0.5634
groups_phosphorus_free    5      0.5742      0.4449      0.6143      0.4436      0.5733      0.5510
groups_sphingolipids      5      0.5818      0.4780      0.6532      0.4068      0.4909      0.4950
ALL                      20      0.6241      0.4457      0.6038      0.5072      0.5552      0.5488

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5455      0.5565     0.0655  20
max valid BA                0.5520      0.5571     0.0697  20
best valid F1               0.5163      0.5247     0.0707  20
test BA                     0.5349      0.5270     0.0479  20
test AUC                    0.5155      0.5014     0.0839  20
test AUC in-protein         0.4672      0.5070     0.1833  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.4840      0.4785     0.1141  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.4771      0.4821     0.0870  20
test sensitivity            0.6241      0.6289     0.2205  20
test specificity            0.4457      0.4420     0.2284  20
test precision              0.4165      0.3974     0.0633  20
test loss                   0.7893      0.7082     0.1986  20
FPR (FP/(FP+TN))            0.5543      0.5580     0.2284  20
FNR (FN/(FN+TP))            0.3759      0.3711     0.2205  20

=== abs(sensitivity-specificity) gap: mean=0.3819 median=0.3881 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6130      0.6289     0.0438  5
  max valid BA                0.6283      0.6403     0.0418  5
  best valid F1               0.5519      0.5597     0.0318  5
  test BA                     0.5830      0.5785     0.0237  5
  test AUC                    0.6322      0.6395     0.0241  5
  test AUC in-protein         0.5189      0.5394     0.0785  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.5299      0.5377     0.0700  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.5040      0.5035     0.0249  5
  test sensitivity            0.6774      0.6989     0.0877  5
  test specificity            0.4885      0.5464     0.1015  5
  test precision              0.4045      0.4077     0.0237  5
  test loss                   0.6907      0.6951     0.0098  5
  FPR (FP/(FP+TN))            0.5115      0.4536     0.1015  5
  FNR (FN/(FN+TP))            0.3226      0.3011     0.0877  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5202      0.5174     0.0539  5
  max valid BA                0.5245      0.5174     0.0473  5
  best valid F1               0.4711      0.4630     0.0681  5
  test BA                     0.5172      0.5258     0.0236  5
  test AUC                    0.4782      0.4505     0.0606  5
  test AUC in-protein         0.4302      0.3117     0.1936  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.4720      0.4007     0.1437  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.4630      0.4772     0.0554  5
  test sensitivity            0.6631      0.6126     0.2271  5
  test specificity            0.3713      0.3713     0.2422  5
  test precision              0.3704      0.3733     0.0210  5
  test loss                   0.8878      0.7080     0.3542  5
  FPR (FP/(FP+TN))            0.6287      0.6287     0.2422  5
  FNR (FN/(FN+TP))            0.3369      0.3874     0.2271  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5561      0.5765     0.0493  5
  max valid BA                0.5622      0.5765     0.0575  5
  best valid F1               0.5281      0.5000     0.0596  5
  test BA                     0.5095      0.5145     0.0538  5
  test AUC                    0.4690      0.4700     0.0603  5
  test AUC in-protein         0.4033      0.4167     0.3163  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.4714      0.4848     0.0871  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.4541      0.4384     0.0635  5
  test sensitivity            0.5742      0.5161     0.2544  5
  test specificity            0.4449      0.4694     0.3183  5
  test precision              0.4265      0.3947     0.1001  5
  test loss                   0.7573      0.7337     0.0863  5
  FPR (FP/(FP+TN))            0.5551      0.5306     0.3183  5
  FNR (FN/(FN+TP))            0.4258      0.4839     0.2544  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4927      0.5091     0.0549  5
  max valid BA                0.4930      0.5091     0.0553  5
  best valid F1               0.5140      0.5747     0.1010  5
  test BA                     0.5299      0.5115     0.0528  5
  test AUC                    0.4825      0.4590     0.0526  5
  test AUC in-protein         0.5163      0.5039     0.0520  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4628      0.3832     0.1586  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4873      0.5745     0.1623  5
  test sensitivity            0.5818      0.7879     0.3101  5
  test specificity            0.4780      0.4146     0.2590  5
  test precision              0.4648      0.4706     0.0460  5
  test loss                   0.8214      0.7631     0.1658  5
  FPR (FP/(FP+TN))            0.5220      0.5854     0.2590  5
  FNR (FN/(FN+TP))            0.4182      0.2121     0.3101  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (apolar_sasa_share,aromatic_share,aromatic_share_rim,buriedness_q50,chain,depth_q10,ev14_q10,ev28_q10,hbond,heavy,hydropathy_core,hydropathy_mean,hydropathy_rim,pocket_elongation,pocket_flatness,pocket_volume_per_sasa,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                      
anionic                     0.502         0.770    0.606              0.525         0.518
choline                     0.404         0.384    0.346              0.522         0.529
phosphorus_free             0.261         0.406    0.441              0.525         0.476
sphingolipids               0.367         0.317    0.409              0.478         0.521

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.469               0.395                  0.030                     0.204
net_AUC           0.451               0.413                  0.046                     0.111

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.513               0.512                  0.055                     0.023
net_AUC_pair           0.511               0.509                  0.059                     0.024

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.469  0.502      0.513     0.490
10     0.469  0.442      0.513     0.456
49     0.469  0.428      0.513     0.462
51     0.469  0.422      0.513     0.469
120    0.469  0.451      0.513     0.511

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.666         0.672      0.006
10        0.666         0.693      0.028
49        0.666         0.697      0.031
51        0.666         0.700      0.035
120       0.666         0.691      0.026

3. mean over seeds, epoch 120
                  chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                                  
anionic          0.770  0.606      0.525     0.518     0.770         0.786      0.016
choline          0.384  0.346      0.522     0.529     0.616         0.665      0.050
phosphorus_free  0.406  0.441      0.525     0.476     0.594         0.628      0.035
sphingolipids    0.317  0.409      0.478     0.521     0.683         0.685      0.002

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.469               0.395                  0.030                     0.204
net               0.451               0.413                  0.046                     0.111
fit_chem          0.666               0.646                  0.030                     0.079
fit_chem_net      0.691               0.684                  0.040                     0.067
increment         0.026               0.020                  0.023                     0.021

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.513               0.512                  0.055                     0.023
net_pair       0.511               0.509                  0.059                     0.024
```
