# descriptors_head_family_neutral_lipprop_lcs

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_head_family_neutral_lipprop_lcs'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.7355      0.4754      0.7049      0.5315      0.7505      0.5242
groups_choline            5      0.5676      0.5079      0.5616      0.6462      0.5232      0.5802
groups_phosphorus_free    5      0.2323      0.7224      0.3532      0.6985      0.3267      0.7184
groups_sphingolipids      5      0.4061      0.5073      0.4246      0.5923      0.4303      0.5500
ALL                      20      0.4853      0.5533      0.5111      0.6171      0.5077      0.5932

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5414      0.5294     0.0655  20
max valid BA                0.5504      0.5409     0.0696  20
best valid F1               0.4783      0.4923     0.0948  20
test BA                     0.5193      0.5000     0.0795  20
test AUC                    0.5068      0.4608     0.1312  20
test AUC in-protein         0.4185      0.3688     0.2311  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.4397      0.4270     0.1877  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.3866      0.4489     0.1935  20
test sensitivity            0.4853      0.5445     0.2744  20
test specificity            0.5533      0.5247     0.2324  20
test precision              0.3679      0.3966     0.1140  18
test loss                   0.7009      0.6945     0.0372  20
FPR (FP/(FP+TN))            0.4467      0.4753     0.2324  20
FNR (FN/(FN+TP))            0.5147      0.4555     0.2744  20

=== abs(sensitivity-specificity) gap: mean=0.3731 median=0.2930 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6240      0.6469     0.0563  5
  max valid BA                0.6374      0.6561     0.0538  5
  best valid F1               0.5636      0.5804     0.0385  5
  test BA                     0.6054      0.6075     0.0501  5
  test AUC                    0.6856      0.6695     0.0338  5
  test AUC in-protein         0.5453      0.5134     0.0665  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.5557      0.5690     0.0602  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.5321      0.5166     0.0382  5
  test sensitivity            0.7355      0.7634     0.1098  5
  test specificity            0.4754      0.5246     0.1649  5
  test precision              0.4237      0.4528     0.0467  5
  test loss                   0.6598      0.6692     0.0275  5
  FPR (FP/(FP+TN))            0.5246      0.4754     0.1649  5
  FNR (FN/(FN+TP))            0.2645      0.2366     0.1098  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5379      0.5422     0.0422  5
  max valid BA                0.5517      0.5457     0.0545  5
  best valid F1               0.4845      0.4846     0.0369  5
  test BA                     0.5377      0.5128     0.0537  5
  test AUC                    0.5153      0.5235     0.0685  5
  test AUC in-protein         0.3707      0.3349     0.1206  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.4149      0.4243     0.0986  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.4606      0.4400     0.0538  5
  test sensitivity            0.5676      0.5405     0.0896  5
  test specificity            0.5079      0.4851     0.1020  5
  test precision              0.3912      0.3659     0.0545  5
  test loss                   0.7128      0.7178     0.0318  5
  FPR (FP/(FP+TN))            0.4921      0.5149     0.1020  5
  FNR (FN/(FN+TP))            0.4324      0.4595     0.0896  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5181      0.5272     0.0169  5
  max valid BA                0.5225      0.5276     0.0220  5
  best valid F1               0.3970      0.3793     0.1107  5
  test BA                     0.4774      0.4898     0.0812  5
  test AUC                    0.4602      0.4345     0.0801  5
  test AUC in-protein         0.5178      0.3889     0.3785  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.5331      0.4242     0.2144  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.2031      0.1852     0.2342  5
  test sensitivity            0.2323      0.1613     0.3055  5
  test specificity            0.7224      0.6327     0.2527  5
  test precision              0.2360      0.2420     0.1890  4
  test loss                   0.6963      0.6900     0.0171  5
  FPR (FP/(FP+TN))            0.2776      0.3673     0.2527  5
  FNR (FN/(FN+TP))            0.7677      0.8387     0.3055  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4857      0.4905     0.0451  5
  max valid BA                0.4902      0.4905     0.0413  5
  best valid F1               0.4679      0.4691     0.1003  5
  test BA                     0.4567      0.4497     0.0349  5
  test AUC                    0.3660      0.3577     0.0448  5
  test AUC in-protein         0.2403      0.2333     0.1283  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.2551      0.1778     0.1922  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3506      0.4384     0.2038  5
  test sensitivity            0.4061      0.4848     0.2638  5
  test specificity            0.5073      0.4146     0.3265  5
  test precision              0.4010      0.4037     0.0156  4
  test loss                   0.7347      0.7277     0.0277  5
  FPR (FP/(FP+TN))            0.4927      0.5854     0.3265  5
  FNR (FN/(FN+TP))            0.5939      0.5152     0.2638  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (apolar_sasa_share,aromatic_share,buriedness_q50,chain,hbond,heavy,hydropathy_rim,pocket_elongation,pocket_flatness,pocket_volume_per_sasa,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                      
anionic                     0.513         0.777    0.697              0.530         0.491
choline                     0.426         0.409    0.452              0.552         0.447
phosphorus_free             0.289         0.498    0.451              0.509         0.488
sphingolipids               0.367         0.391    0.356              0.556         0.419

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.518               0.468                  0.031                     0.178
net_AUC           0.489               0.464                  0.064                     0.146

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.537               0.528                  0.043                     0.022
net_AUC_pair           0.461               0.477                  0.083                     0.035

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.518  0.464      0.537     0.442
10     0.518  0.428      0.537     0.412
49     0.518  0.473      0.537     0.406
51     0.518  0.472      0.537     0.405
120    0.518  0.489      0.537     0.461

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.624         0.647      0.022
10        0.624         0.667      0.043
49        0.624         0.671      0.047
51        0.624         0.673      0.048
120       0.624         0.659      0.035

3. mean over seeds, epoch 120
                  chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                                  
anionic          0.777  0.697      0.530     0.491     0.777         0.783      0.007
choline          0.409  0.452      0.552     0.447     0.591         0.601      0.009
phosphorus_free  0.498  0.451      0.509     0.488     0.521         0.571      0.051
sphingolipids    0.391  0.356      0.556     0.419     0.609         0.682      0.073

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.518               0.468                  0.031                     0.178
net               0.489               0.464                  0.064                     0.146
fit_chem          0.624               0.597                  0.028                     0.108
fit_chem_net      0.659               0.642                  0.049                     0.095
increment         0.035               0.015                  0.047                     0.032

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.537               0.528                  0.043                     0.022
net_pair       0.461               0.477                  0.083                     0.035
```
