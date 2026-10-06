# dh_lcs_family_neutral_pb6_lipprop

## Summary (analysis/summarize_label.py)

```
Summary: 'dh_lcs_family_neutral_pb6_lipprop'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6387      0.6262      0.5437      0.6739      0.6538      0.6604
groups_choline            5      0.4414      0.6545      0.6297      0.4749      0.5661      0.6228
groups_phosphorus_free    5      0.4065      0.6245      0.3965      0.7329      0.3467      0.7796
groups_sphingolipids      5      0.5939      0.5268      0.4944      0.5966      0.5939      0.5900
ALL                      20      0.5201      0.6080      0.5161      0.6196      0.5401      0.6632

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5772      0.5636     0.0622  20
max valid BA                0.6017      0.6012     0.0615  20
best valid F1               0.5297      0.5448     0.0841  20
test BA                     0.5641      0.5662     0.0677  20
test AUC                    0.5621      0.5824     0.1093  20
test AUC in-protein         0.5203      0.5113     0.2256  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5666      0.5584     0.1540  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.4566      0.4858     0.1260  20
test sensitivity            0.5201      0.5103     0.2570  20
test specificity            0.6080      0.6804     0.2440  20
test precision              0.4788      0.4540     0.1360  20
test loss                   0.7120      0.6907     0.0794  20
FPR (FP/(FP+TN))            0.3920      0.3196     0.2440  20
FNR (FN/(FN+TP))            0.4799      0.4897     0.2570  20

=== abs(sensitivity-specificity) gap: mean=0.4059 median=0.3341 n=20 ===
sensitivity std across seeds (by group): mean=0.2356 median=0.2236 n=4
specificity std across seeds (by group): mean=0.2263 median=0.2497 n=4

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6368      0.6509     0.0495  5
  max valid BA                0.6571      0.6563     0.0300  5
  best valid F1               0.5645      0.5498     0.0266  5
  test BA                     0.6325      0.6108     0.0426  5
  test AUC                    0.6899      0.6952     0.0376  5
  test AUC in-protein         0.5324      0.5340     0.0386  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.5511      0.5596     0.0827  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.5366      0.5401     0.0524  5
  test sensitivity            0.6387      0.6559     0.1349  5
  test specificity            0.6262      0.6776     0.1509  5
  test precision              0.4755      0.4587     0.0648  5
  test loss                   0.6561      0.6521     0.0327  5
  FPR (FP/(FP+TN))            0.3738      0.3224     0.1509  5
  FNR (FN/(FN+TP))            0.3613      0.3441     0.1349  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5629      0.5370     0.0476  5
  max valid BA                0.5944      0.5956     0.0560  5
  best valid F1               0.4946      0.5040     0.0914  5
  test BA                     0.5479      0.5398     0.0540  5
  test AUC                    0.5280      0.5425     0.0826  5
  test AUC in-protein         0.4562      0.4613     0.0833  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.4802      0.4949     0.0913  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.4210      0.4018     0.0857  5
  test sensitivity            0.4414      0.3964     0.1310  5
  test specificity            0.6545      0.6832     0.0537  5
  test precision              0.4077      0.4074     0.0586  5
  test loss                   0.7769      0.7386     0.1108  5
  FPR (FP/(FP+TN))            0.3455      0.3168     0.0537  5
  FNR (FN/(FN+TP))            0.5586      0.6036     0.1310  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5495      0.5619     0.0232  5
  max valid BA                0.5631      0.5619     0.0143  5
  best valid F1               0.4760      0.4857     0.0851  5
  test BA                     0.5155      0.5398     0.0562  5
  test AUC                    0.4475      0.4365     0.0737  5
  test AUC in-protein         0.4467      0.5000     0.3798  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.4960      0.5217     0.1419  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.3531      0.3000     0.1554  5
  test sensitivity            0.4065      0.1935     0.3640  5
  test specificity            0.6245      0.7347     0.3522  5
  test precision              0.4549      0.4189     0.1561  5
  test loss                   0.6980      0.6902     0.0290  5
  FPR (FP/(FP+TN))            0.3755      0.2653     0.3522  5
  FNR (FN/(FN+TP))            0.5935      0.8065     0.3640  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5595      0.5568     0.0840  5
  max valid BA                0.5920      0.6068     0.0885  5
  best valid F1               0.5835      0.6042     0.0836  5
  test BA                     0.5604      0.5661     0.0688  5
  test AUC                    0.5831      0.5928     0.0651  5
  test AUC in-protein         0.6460      0.5091     0.2393  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.7392      0.7139     0.1556  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5155      0.4878     0.1175  5
  test sensitivity            0.5939      0.6061     0.3124  5
  test specificity            0.5268      0.3171     0.3486  5
  test precision              0.5771      0.5077     0.1916  5
  test loss                   0.7171      0.6913     0.0793  5
  FPR (FP/(FP+TN))            0.4732      0.6829     0.3486  5
  FNR (FN/(FN+TP))            0.4061      0.3939     0.3124  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (apolar_sasa_share,aromatic_share,aromatic_share_rim,buriedness_q50,chain,depth_q10,ev14_q10,ev28_q10,hbond,heavy,hydropathy_core,hydropathy_mean,hydropathy_rim,pocket_elongation,pocket_flatness,pocket_volume_per_sasa,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                      
anionic                     0.502         0.770    0.682              0.524         0.527
choline                     0.412         0.395    0.399              0.525         0.475
phosphorus_free             0.260         0.400    0.449              0.519         0.488
sphingolipids               0.367         0.320    0.440              0.440         0.529

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.471               0.395                  0.037                     0.203
net_AUC           0.492               0.478                  0.064                     0.128

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.502               0.518                  0.062                     0.042
net_AUC_pair           0.505               0.503                  0.104                     0.027

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.471  0.504      0.502     0.529
10     0.471  0.489      0.502     0.471
49     0.471  0.490      0.502     0.487
51     0.471  0.492      0.502     0.486
120    0.471  0.492      0.502     0.505

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.664         0.679      0.015
10        0.664         0.694      0.030
49        0.664         0.681      0.017
51        0.664         0.681      0.017
120       0.664         0.677      0.014

3. mean over seeds, epoch 120
                  chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                                  
anionic          0.770  0.682      0.524     0.527     0.770         0.773      0.003
choline          0.395  0.399      0.525     0.475     0.605         0.619      0.014
phosphorus_free  0.400  0.449      0.519     0.488     0.600         0.614      0.014
sphingolipids    0.320  0.440      0.440     0.529     0.680         0.704      0.024

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.471               0.395                  0.037                     0.203
net               0.492               0.478                  0.064                     0.128
fit_chem          0.664               0.628                  0.037                     0.080
fit_chem_net      0.677               0.639                  0.037                     0.076
increment         0.014               0.006                  0.032                     0.008

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.502               0.518                  0.062                     0.042
net_pair       0.505               0.503                  0.104                     0.027
```
