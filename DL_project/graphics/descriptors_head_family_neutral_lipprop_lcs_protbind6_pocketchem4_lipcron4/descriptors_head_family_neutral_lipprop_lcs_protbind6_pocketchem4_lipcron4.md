# descriptors_head_family_neutral_lipprop_lcs_protbind6_pocketchem4_lipcron4

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_head_family_neutral_lipprop_lcs_protbind6_pocketchem4_lipcron4'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6581      0.5246      0.6290      0.5841      0.7247      0.5484
groups_choline            5      0.3802      0.6178      0.3713      0.6781      0.4268      0.6663
groups_phosphorus_free    5      0.3806      0.5429      0.6007      0.5013      0.5000      0.6857
groups_sphingolipids      5      0.6000      0.5024      0.5187      0.5865      0.6242      0.6450
ALL                      20      0.5047      0.5469      0.5299      0.5875      0.5689      0.6364

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5849      0.5885     0.0515  20
max valid BA                0.6026      0.6025     0.0591  20
best valid F1               0.5420      0.5451     0.0849  20
test BA                     0.5258      0.5151     0.0760  20
test AUC                    0.5216      0.5146     0.1034  20
test AUC in-protein         0.5016      0.5610     0.1670  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5508      0.5521     0.1391  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.4205      0.4628     0.1616  20
test sensitivity            0.5047      0.5699     0.2413  20
test specificity            0.5469      0.5266     0.2064  20
test precision              0.4039      0.4259     0.0965  19
test loss                   0.8879      0.7240     0.3872  20
FPR (FP/(FP+TN))            0.4531      0.4734     0.2064  20
FNR (FN/(FN+TP))            0.4953      0.4301     0.2413  20

=== abs(sensitivity-specificity) gap: mean=0.3431 median=0.3062 n=20 ===
sensitivity std across seeds (by group): mean=0.2055 median=0.2057 n=4
specificity std across seeds (by group): mean=0.2096 median=0.2170 n=4

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6187      0.6442     0.0490  5
  max valid BA                0.6365      0.6457     0.0596  5
  best valid F1               0.5616      0.5656     0.0447  5
  test BA                     0.5913      0.6146     0.0774  5
  test AUC                    0.6078      0.6246     0.1000  5
  test AUC in-protein         0.5396      0.5645     0.0701  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.5381      0.5496     0.0447  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.5089      0.5274     0.0706  5
  test sensitivity            0.6581      0.6452     0.1024  5
  test specificity            0.5246      0.5410     0.1193  5
  test precision              0.4190      0.4324     0.0708  5
  test loss                   0.8143      0.6927     0.2913  5
  FPR (FP/(FP+TN))            0.4754      0.4590     0.1193  5
  FNR (FN/(FN+TP))            0.3419      0.3548     0.1024  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5395      0.5260     0.0466  5
  max valid BA                0.5466      0.5362     0.0407  5
  best valid F1               0.4878      0.4915     0.0374  5
  test BA                     0.4990      0.5000     0.0447  5
  test AUC                    0.4559      0.4629     0.0928  5
  test AUC in-protein         0.4799      0.4904     0.1647  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.4725      0.4966     0.1171  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.3072      0.4201     0.2053  5
  test sensitivity            0.3802      0.4144     0.3082  5
  test specificity            0.6178      0.6881     0.2852  5
  test precision              0.3434      0.3579     0.0811  4
  test loss                   1.1710      0.8203     0.6239  5
  FPR (FP/(FP+TN))            0.3822      0.3119     0.2852  5
  FNR (FN/(FN+TP))            0.6198      0.5856     0.3082  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5804      0.5735     0.0454  5
  max valid BA                0.5929      0.5874     0.0473  5
  best valid F1               0.5015      0.5263     0.1183  5
  test BA                     0.4618      0.4250     0.0787  5
  test AUC                    0.4693      0.4325     0.0781  5
  test AUC in-protein         0.3578      0.3333     0.1916  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.5433      0.5909     0.2002  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.3310      0.2712     0.1481  5
  test sensitivity            0.3806      0.2581     0.2654  5
  test specificity            0.5429      0.5918     0.2576  5
  test precision              0.3386      0.3103     0.0874  5
  test loss                   0.8636      0.7302     0.2941  5
  FPR (FP/(FP+TN))            0.4571      0.4082     0.2576  5
  FNR (FN/(FN+TP))            0.6194      0.7419     0.2654  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6012      0.6091     0.0398  5
  max valid BA                0.6346      0.6458     0.0485  5
  best valid F1               0.6170      0.6067     0.0601  5
  test BA                     0.5512      0.5499     0.0325  5
  test AUC                    0.5533      0.5432     0.0823  5
  test AUC in-protein         0.6293      0.6093     0.1233  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.6493      0.6194     0.1268  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5351      0.5526     0.0529  5
  test sensitivity            0.6000      0.6364     0.1460  5
  test specificity            0.5024      0.4634     0.1764  5
  test precision              0.5026      0.4884     0.0536  5
  test loss                   0.7028      0.7138     0.0313  5
  FPR (FP/(FP+TN))            0.4976      0.5366     0.1764  5
  FNR (FN/(FN+TP))            0.4000      0.3636     0.1460  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (apolar_sasa_share,aromatic_share,aromatic_share_rim,basic_share_core,basic_share_rim,buriedness_q50,chain,depth_q10,ev14_q10,ev28_q10,experimental_lipid_volume,hbond,hbond_donor_share_core,heavy,hydropathy_core,hydropathy_mean,hydropathy_rim,logp,pocket_elongation,pocket_flatness,pocket_free_volume,pocket_volume_per_sasa,tail_double_bonds,tail_unsaturation_density,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                      
anionic                     0.474         0.771    0.641              0.512         0.553
choline                     0.376         0.404    0.368              0.557         0.471
phosphorus_free             0.221         0.393    0.458              0.535         0.523
sphingolipids               0.343         0.181    0.375              0.384         0.560

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.437               0.397                  0.030                     0.245
net_AUC           0.460               0.435                  0.089                     0.127

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.497               0.508                  0.049                     0.078
net_AUC_pair           0.527               0.516                  0.073                     0.041

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.437  0.526      0.497     0.486
10     0.437  0.488      0.497     0.478
49     0.437  0.460      0.497     0.494
51     0.437  0.465      0.497     0.498
120    0.437  0.460      0.497     0.527

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.698         0.711      0.013
10        0.698         0.710      0.012
49        0.698         0.711      0.013
51        0.698         0.708      0.010
120       0.698         0.710      0.012

3. mean over seeds, epoch 120
                  chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                                  
anionic          0.771  0.641      0.512     0.553     0.771         0.771     -0.000
choline          0.404  0.368      0.557     0.471     0.596         0.635      0.039
phosphorus_free  0.393  0.458      0.535     0.523     0.607         0.611      0.003
sphingolipids    0.181  0.375      0.384     0.560     0.819         0.825      0.006

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.437               0.397                  0.030                     0.245
net               0.460               0.435                  0.089                     0.127
fit_chem          0.698               0.694                  0.030                     0.113
fit_chem_net      0.710               0.730                  0.040                     0.104
increment         0.012               0.004                  0.020                     0.018

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.497               0.508                  0.049                     0.078
net_pair       0.527               0.516                  0.073                     0.041
```
