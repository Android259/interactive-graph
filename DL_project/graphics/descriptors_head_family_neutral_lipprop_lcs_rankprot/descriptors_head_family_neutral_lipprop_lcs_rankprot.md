# descriptors_head_family_neutral_lipprop_lcs_rankprot

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_head_family_neutral_lipprop_lcs_rankprot'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.3656      0.6404      0.2540      0.7700      0.1699      0.8912
groups_choline            5      0.5027      0.6050      0.4574      0.5132      0.5768      0.5901
groups_phosphorus_free    5      0.4387      0.6327      0.5344      0.4642      0.5800      0.6082
groups_sphingolipids      5      0.4303      0.8488      0.5246      0.4190      0.5818      0.8500
ALL                      20      0.4343      0.6817      0.4426      0.5416      0.4771      0.7349

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5906      0.5908     0.0718  20
max valid BA                0.6060      0.5912     0.0795  20
best valid F1               0.5044      0.5317     0.1624  20
test BA                     0.5580      0.5418     0.0737  20
test AUC                    0.5085      0.5189     0.0904  20
test AUC in-protein         0.5105      0.4886     0.2046  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5039      0.4954     0.1260  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.3917      0.4881     0.1923  20
test sensitivity            0.4343      0.4091     0.3045  20
test specificity            0.6817      0.7439     0.2946  20
test precision              0.5275      0.4583     0.2353  20
test loss                   0.7355      0.7095     0.1633  20
FPR (FP/(FP+TN))            0.3183      0.2561     0.2946  20
FNR (FN/(FN+TP))            0.5657      0.5909     0.3045  20

=== abs(sensitivity-specificity) gap: mean=0.5396 median=0.6084 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5232      0.5045     0.0451  5
  max valid BA                0.5306      0.5108     0.0423  5
  best valid F1               0.3675      0.3911     0.1585  5
  test BA                     0.5030      0.5054     0.0713  5
  test AUC                    0.4331      0.3990     0.1017  5
  test AUC in-protein         0.4919      0.4770     0.0479  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.4855      0.4953     0.0495  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.2558      0.2234     0.2441  5
  test sensitivity            0.3656      0.2258     0.4217  5
  test specificity            0.6404      0.6284     0.3917  5
  test precision              0.4238      0.3395     0.3459  5
  test loss                   0.7235      0.6939     0.0892  5
  FPR (FP/(FP+TN))            0.3596      0.3716     0.3917  5
  FNR (FN/(FN+TP))            0.6344      0.7742     0.4217  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5717      0.5742     0.0342  5
  max valid BA                0.5834      0.5836     0.0411  5
  best valid F1               0.4542      0.5290     0.1824  5
  test BA                     0.5538      0.5392     0.0374  5
  test AUC                    0.5341      0.5219     0.0696  5
  test AUC in-protein         0.6389      0.7106     0.1679  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.6146      0.6859     0.1417  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.3824      0.4115     0.2024  5
  test sensitivity            0.5027      0.4505     0.3950  5
  test specificity            0.6050      0.5941     0.3285  5
  test precision              0.5000      0.4113     0.1892  5
  test loss                   0.6853      0.6812     0.0207  5
  FPR (FP/(FP+TN))            0.3950      0.4059     0.3285  5
  FNR (FN/(FN+TP))            0.4973      0.5495     0.3950  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5829      0.5861     0.0312  5
  max valid BA                0.5941      0.5867     0.0307  5
  best valid F1               0.5407      0.5455     0.0480  5
  test BA                     0.5357      0.5273     0.0489  5
  test AUC                    0.5225      0.5158     0.1109  5
  test AUC in-protein         0.4189      0.4000     0.3683  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.4672      0.4545     0.0699  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.3949      0.3548     0.1505  5
  test sensitivity            0.4387      0.3548     0.3023  5
  test specificity            0.6327      0.5918     0.2940  5
  test precision              0.4546      0.4444     0.0871  5
  test loss                   0.6341      0.6992     0.2000  5
  FPR (FP/(FP+TN))            0.3673      0.4082     0.2940  5
  FNR (FN/(FN+TP))            0.5613      0.6452     0.3023  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6845      0.6773     0.0553  5
  max valid BA                0.7159      0.6958     0.0510  5
  best valid F1               0.6553      0.6667     0.0885  5
  test BA                     0.6395      0.6390     0.0649  5
  test AUC                    0.5444      0.5691     0.0393  5
  test AUC in-protein         0.4924      0.4937     0.0262  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4482      0.3639     0.1634  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5335      0.5217     0.0637  5
  test sensitivity            0.4303      0.4242     0.0583  5
  test specificity            0.8488      0.8537     0.1307  5
  test precision              0.7315      0.7000     0.1640  5
  test loss                   0.8992      0.8582     0.1692  5
  FPR (FP/(FP+TN))            0.1512      0.1463     0.1307  5
  FNR (FN/(FN+TP))            0.5697      0.5758     0.0583  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (apolar_sasa_share,aromatic_share,buriedness_q50,chain,hbond,heavy,hydropathy_rim,pocket_elongation,pocket_flatness,pocket_volume_per_sasa,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                      
anionic                     0.513         0.777    0.381              0.530         0.474
choline                     0.426         0.409    0.569              0.552         0.580
phosphorus_free             0.289         0.498    0.587              0.509         0.513
sphingolipids               0.367         0.391    0.599              0.556         0.376

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.518               0.468                  0.031                     0.178
net_AUC           0.534               0.550                  0.055                     0.103

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.537               0.528                  0.043                     0.022
net_AUC_pair           0.486               0.480                  0.068                     0.085

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.518  0.481      0.537     0.435
10     0.518  0.495      0.537     0.464
49     0.518  0.503      0.537     0.479
51     0.518  0.502      0.537     0.482
120    0.518  0.534      0.537     0.486

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.624         0.651      0.026
10        0.624         0.644      0.020
49        0.624         0.650      0.025
51        0.624         0.650      0.026
120       0.624         0.654      0.029

3. mean over seeds, epoch 120
                  chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                                  
anionic          0.777  0.381      0.530     0.474     0.777         0.785      0.009
choline          0.409  0.569      0.552     0.580     0.591         0.599      0.007
phosphorus_free  0.498  0.587      0.509     0.513     0.521         0.591      0.071
sphingolipids    0.391  0.599      0.556     0.376     0.609         0.639      0.030

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.518               0.468                  0.031                     0.178
net               0.534               0.550                  0.055                     0.103
fit_chem          0.624               0.597                  0.028                     0.108
fit_chem_net      0.654               0.624                  0.042                     0.090
increment         0.029               0.022                  0.036                     0.030

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.537               0.528                  0.043                     0.022
net_pair       0.486               0.480                  0.068                     0.085
```
