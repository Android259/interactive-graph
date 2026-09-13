# descriptors_head_family_neutral_lipprop_lcs_protbind6

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_head_family_neutral_lipprop_lcs_protbind6'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6065      0.5803      0.5871      0.6318      0.6645      0.6099
groups_choline            5      0.4180      0.7257      0.5265      0.4797      0.5321      0.6931
groups_phosphorus_free    5      0.5613      0.4449      0.5494      0.6040      0.6800      0.4816
groups_sphingolipids      5      0.5333      0.5610      0.5088      0.5484      0.5879      0.5600
ALL                      20      0.5298      0.5780      0.5429      0.5660      0.6161      0.5861

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5836      0.6000     0.0626  20
max valid BA                0.6011      0.6071     0.0583  20
best valid F1               0.5373      0.5521     0.0878  20
test BA                     0.5539      0.5674     0.0594  20
test AUC                    0.5705      0.5704     0.0840  20
test AUC in-protein         0.4961      0.4888     0.2032  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5322      0.5292     0.1656  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.4501      0.4673     0.1371  20
test sensitivity            0.5298      0.4839     0.2442  20
test specificity            0.5780      0.5848     0.2509  20
test precision              0.4601      0.4437     0.0877  19
test loss                   0.7104      0.6894     0.0714  20
FPR (FP/(FP+TN))            0.4220      0.4152     0.2509  20
FNR (FN/(FN+TP))            0.4702      0.5161     0.2442  20

=== abs(sensitivity-specificity) gap: mean=0.3702 median=0.3142 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6237      0.6187     0.0340  5
  max valid BA                0.6372      0.6409     0.0248  5
  best valid F1               0.5468      0.5462     0.0252  5
  test BA                     0.5934      0.5971     0.0158  5
  test AUC                    0.6199      0.6388     0.0380  5
  test AUC in-protein         0.4748      0.4578     0.1103  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.4963      0.4661     0.1219  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.4914      0.4813     0.0453  5
  test sensitivity            0.6065      0.5376     0.1838  5
  test specificity            0.5803      0.6011     0.1751  5
  test precision              0.4329      0.4101     0.0378  5
  test loss                   0.6892      0.6824     0.0430  5
  FPR (FP/(FP+TN))            0.4197      0.3989     0.1751  5
  FNR (FN/(FN+TP))            0.3935      0.4624     0.1838  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5964      0.6089     0.0586  5
  max valid BA                0.6126      0.6284     0.0745  5
  best valid F1               0.5002      0.5580     0.1491  5
  test BA                     0.5719      0.5939     0.0434  5
  test AUC                    0.5782      0.5760     0.0722  5
  test AUC in-protein         0.4553      0.4427     0.0927  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.4595      0.4770     0.0782  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.3860      0.4717     0.2198  5
  test sensitivity            0.4180      0.4505     0.2549  5
  test specificity            0.7257      0.7277     0.1734  5
  test precision              0.4581      0.4469     0.0247  4
  test loss                   0.7458      0.7226     0.1297  5
  FPR (FP/(FP+TN))            0.2743      0.2723     0.1734  5
  FNR (FN/(FN+TP))            0.5820      0.5495     0.2549  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5621      0.5548     0.0370  5
  max valid BA                0.5808      0.5857     0.0252  5
  best valid F1               0.5450      0.5333     0.0320  5
  test BA                     0.5031      0.5481     0.0713  5
  test AUC                    0.4901      0.4812     0.0630  5
  test AUC in-protein         0.4144      0.5000     0.3060  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.4950      0.5938     0.1708  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.4280      0.4615     0.1271  5
  test sensitivity            0.5613      0.4839     0.3247  5
  test specificity            0.4449      0.4898     0.3652  5
  test precision              0.4311      0.4225     0.1194  5
  test loss                   0.7072      0.6928     0.0378  5
  FPR (FP/(FP+TN))            0.5551      0.5102     0.3652  5
  FNR (FN/(FN+TP))            0.4387      0.5161     0.3247  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5523      0.5148     0.0930  5
  max valid BA                0.5739      0.5523     0.0784  5
  best valid F1               0.5573      0.5600     0.1015  5
  test BA                     0.5472      0.5462     0.0627  5
  test AUC                    0.5938      0.6541     0.1049  5
  test AUC in-protein         0.6401      0.5149     0.2119  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.6781      0.7225     0.2087  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4951      0.4412     0.1111  5
  test sensitivity            0.5333      0.4545     0.2343  5
  test specificity            0.5610      0.5610     0.2346  5
  test precision              0.5180      0.4746     0.1110  5
  test loss                   0.6994      0.6754     0.0426  5
  FPR (FP/(FP+TN))            0.4390      0.4390     0.2346  5
  FNR (FN/(FN+TP))            0.4667      0.5455     0.2343  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (apolar_sasa_share,aromatic_share,aromatic_share_rim,buriedness_q50,chain,depth_q10,ev14_q10,ev28_q10,hbond,heavy,hydropathy_core,hydropathy_mean,hydropathy_rim,pocket_elongation,pocket_flatness,pocket_volume_per_sasa,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                      
anionic                     0.502         0.770    0.624              0.525         0.533
choline                     0.404         0.384    0.427              0.522         0.441
phosphorus_free             0.261         0.406    0.470              0.525         0.497
sphingolipids               0.367         0.317    0.426              0.478         0.496

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.469               0.395                  0.030                     0.204
net_AUC           0.487               0.475                  0.066                     0.094

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.513               0.512                  0.055                     0.023
net_AUC_pair           0.492               0.510                  0.078                     0.038

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.469  0.492      0.513     0.504
10     0.469  0.513      0.513     0.453
49     0.469  0.481      0.513     0.468
51     0.469  0.479      0.513     0.471
120    0.469  0.487      0.513     0.492

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.666         0.689      0.024
10        0.666         0.707      0.041
49        0.666         0.694      0.029
51        0.666         0.691      0.025
120       0.666         0.677      0.011

3. mean over seeds, epoch 120
                  chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                                  
anionic          0.770  0.624      0.525     0.533     0.770         0.781      0.011
choline          0.384  0.427      0.522     0.441     0.616         0.619      0.003
phosphorus_free  0.406  0.470      0.525     0.497     0.594         0.605      0.011
sphingolipids    0.317  0.426      0.478     0.496     0.683         0.702      0.019

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.469               0.395                  0.030                     0.204
net               0.487               0.475                  0.066                     0.094
fit_chem          0.666               0.646                  0.030                     0.079
fit_chem_net      0.677               0.654                  0.035                     0.081
increment         0.011               0.012                  0.016                     0.006

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.513               0.512                  0.055                     0.023
net_pair       0.492               0.510                  0.078                     0.038
```
