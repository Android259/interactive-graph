# descriptors_head_family_neutral_lipprop_heads1

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_head_family_neutral_lipprop_heads1'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6925      0.3836      0.6451      0.4138      0.7254      0.4452
groups_GLTP            5      0.4800      0.6080      0.6452      0.4240      0.5385      0.7692
groups_IP_trans        5      0.4087      0.6851      0.5961      0.4686      0.7000      0.4809
groups_LBP_BPI_CETP    5      0.7565      0.7957      0.6376      0.4278      0.8417      0.7149
groups_ML              5      0.4400      0.5000      0.4464      0.6251      0.7600      0.5800
groups_OSBP            5      0.6667      0.3000      0.5734      0.4441      0.9333      0.3667
groups_START           5      0.3446      0.7843      0.2915      0.6826      0.2656      0.8315
groups_lipocalin       5      0.5333      0.4361      0.6037      0.4440      0.6111      0.5278
groups_scp2            5      0.7882      0.2824      0.6378      0.4219      0.8706      0.3353
ALL                   45      0.5678      0.5306      0.5641      0.4836      0.6940      0.5613

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6005      0.5778     0.0865  45
max valid BA                0.6276      0.6000     0.0911  45
best valid F1               0.5830      0.5882     0.0947  45
test BA                     0.5492      0.5441     0.1122  45
test AUC                    0.5660      0.5407     0.1458  45
test AUC in-protein         0.5511      0.5102     0.1658  42
  (proteins averaged)       2.6000      3.0000     1.3718  45
test AUC in-protein (pairs)      0.5928      0.5822     0.1674  45
  (proteins contributing)      3.0222      3.0000     1.7900  45
test F1                     0.4651      0.4906     0.1610  45
test sensitivity            0.5678      0.5692     0.2504  45
test specificity            0.5306      0.5000     0.2408  45
test precision              0.4486      0.4174     0.1549  44
test loss                   0.6937      0.6914     0.0198  45
FPR (FP/(FP+TN))            0.4694      0.5000     0.2408  45
FNR (FN/(FN+TP))            0.4322      0.4308     0.2504  45

=== abs(sensitivity-specificity) gap: mean=0.3368 median=0.2118 n=45 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5682      0.5685     0.0320  5
  max valid BA                0.5853      0.5858     0.0300  5
  best valid F1               0.6633      0.6588     0.0493  5
  test BA                     0.5381      0.5543     0.0465  5
  test AUC                    0.5622      0.5547     0.0422  5
  test AUC in-protein         0.5371      0.5579     0.0556  5
    (proteins averaged)       4.0000      4.0000     0.0000  5
  test AUC in-protein (pairs)      0.6261      0.6205     0.0528  5
    (proteins contributing)      4.4000      4.0000     0.5477  5
  test F1                     0.6109      0.5781     0.0550  5
  test sensitivity            0.6925      0.6418     0.1329  5
  test specificity            0.3836      0.3770     0.1455  5
  test precision              0.5549      0.5556     0.0408  5
  test loss                   0.6847      0.6839     0.0028  5
  FPR (FP/(FP+TN))            0.6164      0.6230     0.1455  5
  FNR (FN/(FN+TP))            0.3075      0.3582     0.1329  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6038      0.5769     0.1023  5
  max valid BA                0.6538      0.6538     0.0707  5
  best valid F1               0.6176      0.6316     0.0525  5
  test BA                     0.5440      0.5200     0.0740  5
  test AUC                    0.4675      0.4464     0.0945  5
  test AUC in-protein         0.4645      0.4518     0.0328  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4097      0.4140     0.0541  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5115      0.4906     0.0647  5
  test sensitivity            0.4800      0.4800     0.0894  5
  test specificity            0.6080      0.5600     0.1635  5
  test precision              0.5661      0.5217     0.1001  5
  test loss                   0.7344      0.7243     0.0231  5
  FPR (FP/(FP+TN))            0.3920      0.4400     0.1635  5
  FNR (FN/(FN+TP))            0.5200      0.5200     0.0894  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5776      0.5793     0.0373  5
  max valid BA                0.5904      0.6006     0.0408  5
  best valid F1               0.5181      0.5161     0.0320  5
  test BA                     0.5469      0.5379     0.0650  5
  test AUC                    0.5191      0.5328     0.0800  5
  test AUC in-protein         0.5629      0.6128     0.1429  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5339      0.5708     0.0900  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.3835      0.4348     0.1345  5
  test sensitivity            0.4087      0.4348     0.1808  5
  test specificity            0.6851      0.7021     0.1036  5
  test precision              0.3744      0.3636     0.0949  5
  test loss                   0.6845      0.6890     0.0102  5
  FPR (FP/(FP+TN))            0.3149      0.2979     0.1036  5
  FNR (FN/(FN+TP))            0.5913      0.5652     0.1808  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7473      0.7788     0.0752  5
  max valid BA                0.7783      0.8200     0.0792  5
  best valid F1               0.7046      0.7458     0.0891  5
  test BA                     0.7761      0.7623     0.0628  5
  test AUC                    0.8540      0.8326     0.0444  5
  test AUC in-protein         0.8726      0.8561     0.0330  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.8713      0.8686     0.0261  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.6915      0.6818     0.0728  5
  test sensitivity            0.7565      0.6957     0.1494  5
  test specificity            0.7957      0.7872     0.0466  5
  test precision              0.6453      0.6471     0.0499  5
  test loss                   0.6776      0.6804     0.0089  5
  FPR (FP/(FP+TN))            0.2043      0.2128     0.0466  5
  FNR (FN/(FN+TP))            0.2435      0.3043     0.1494  5

groups_ML (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6400      0.6500     0.0652  5
  max valid BA                0.6700      0.6500     0.1037  5
  best valid F1               0.5627      0.5882     0.1368  5
  test BA                     0.4700      0.5000     0.0975  5
  test AUC                    0.4880      0.5000     0.0879  5
  test AUC in-protein         0.4880      0.5000     0.0879  5
    (proteins averaged)       1.0000      1.0000     0.0000  5
  test AUC in-protein (pairs)      0.4880      0.5000     0.0879  5
    (proteins contributing)      1.0000      1.0000     0.0000  5
  test F1                     0.3055      0.4286     0.2118  5
  test sensitivity            0.4400      0.6000     0.3286  5
  test specificity            0.5000      0.4000     0.3000  5
  test precision              0.2961      0.3333     0.1041  4
  test loss                   0.6893      0.6938     0.0182  5
  FPR (FP/(FP+TN))            0.5000      0.6000     0.3000  5
  FNR (FN/(FN+TP))            0.5600      0.4000     0.3286  5

groups_OSBP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6000      0.5833     0.0913  5
  max valid BA                0.6500      0.6667     0.0697  5
  best valid F1               0.5858      0.5714     0.0505  5
  test BA                     0.4833      0.5833     0.1491  5
  test AUC                    0.6778      0.6667     0.1817  5
  test AUC in-protein         0.6875      0.6875     0.4419  2
    (proteins averaged)       0.4000      0.0000     0.5477  5
  test AUC in-protein (pairs)      0.7522      0.7778     0.2195  5
    (proteins contributing)      1.6000      2.0000     0.5477  5
  test F1                     0.4198      0.5000     0.1541  5
  test sensitivity            0.6667      0.6667     0.3333  5
  test specificity            0.3000      0.1667     0.1826  5
  test precision              0.3133      0.3750     0.1008  5
  test loss                   0.6957      0.6931     0.0099  5
  FPR (FP/(FP+TN))            0.7000      0.8333     0.1826  5
  FNR (FN/(FN+TP))            0.3333      0.3333     0.3333  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5421      0.5680     0.0688  5
  max valid BA                0.5485      0.5766     0.0735  5
  best valid F1               0.5723      0.6029     0.0692  5
  test BA                     0.5644      0.5649     0.0373  5
  test AUC                    0.5544      0.5739     0.0585  5
  test AUC in-protein         0.4720      0.4661     0.0427  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5237      0.5305     0.0940  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.3928      0.4130     0.1472  5
  test sensitivity            0.3446      0.2923     0.1963  5
  test specificity            0.7843      0.7978     0.1650  5
  test precision              0.5915      0.5286     0.1412  5
  test loss                   0.6826      0.6829     0.0162  5
  FPR (FP/(FP+TN))            0.2157      0.2022     0.1650  5
  FNR (FN/(FN+TP))            0.6554      0.7077     0.1963  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5403      0.5625     0.0418  5
  max valid BA                0.5694      0.5764     0.0299  5
  best valid F1               0.4743      0.5077     0.0649  5
  test BA                     0.4847      0.4792     0.0650  5
  test AUC                    0.4656      0.4649     0.0567  5
  test AUC in-protein         0.4866      0.4465     0.0963  5
    (proteins averaged)       5.0000      5.0000     0.0000  5
  test AUC in-protein (pairs)      0.5805      0.5927     0.0735  5
    (proteins contributing)      7.2000      7.0000     0.4472  5
  test F1                     0.3878      0.3696     0.0994  5
  test sensitivity            0.5333      0.4722     0.2352  5
  test specificity            0.4361      0.4444     0.1485  5
  test precision              0.3133      0.3077     0.0542  5
  test loss                   0.6985      0.6974     0.0076  5
  FPR (FP/(FP+TN))            0.5639      0.5556     0.1485  5
  FNR (FN/(FN+TP))            0.4667      0.5278     0.2352  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5853      0.5735     0.0685  5
  max valid BA                0.6029      0.6176     0.0819  5
  best valid F1               0.5478      0.5614     0.0630  5
  test BA                     0.5353      0.5441     0.0424  5
  test AUC                    0.5052      0.5095     0.0901  5
  test AUC in-protein         0.4703      0.5130     0.1180  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5499      0.5979     0.1583  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.4830      0.5000     0.0622  5
  test sensitivity            0.7882      0.8235     0.1841  5
  test specificity            0.2824      0.2353     0.1258  5
  test precision              0.3518      0.3590     0.0248  5
  test loss                   0.6955      0.6950     0.0055  5
  FPR (FP/(FP+TN))            0.7176      0.7647     0.1258  5
  FNR (FN/(FN+TP))            0.2118      0.1765     0.1841  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (apolar_sasa_share,aromatic_share,buriedness_q50,chain,hbond,heavy,hydropathy_rim,pocket_elongation,pocket_flatness,pocket_volume_per_sasa,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.263         0.636    0.478              0.609         0.510
GLTP                     0.278         0.679    0.531              0.754         0.281
IP_trans                 0.326         0.509    0.552              0.530         0.492
LBP_BPI_CETP             0.308         0.634    0.753              0.652         0.787
START                    0.273         0.430    0.414              0.498         0.460
lipocalin                0.273         0.664    0.458              0.639         0.511
scp2                     0.275         0.622    0.567              0.617         0.560

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.596               0.617                  0.057                     0.092
net_AUC           0.536               0.519                  0.077                     0.110

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.614               0.617                  0.059                     0.084
net_AUC_pair           0.515               0.485                  0.086                     0.150

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.596  0.470      0.614     0.472
10     0.596  0.519      0.614     0.494
49     0.596  0.535      0.614     0.508
51     0.596  0.528      0.614     0.505
120    0.596  0.536      0.614     0.515

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.621         0.675      0.054
10        0.621         0.682      0.061
49        0.621         0.679      0.058
51        0.621         0.678      0.057
120       0.621         0.674      0.053

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.636  0.478      0.609     0.510     0.636         0.635     -0.000
GLTP          0.679  0.531      0.754     0.281     0.679         0.786      0.108
IP_trans      0.509  0.552      0.530     0.492     0.542         0.584      0.041
LBP_BPI_CETP  0.634  0.753      0.652     0.787     0.634         0.775      0.141
START         0.430  0.414      0.498     0.460     0.570         0.601      0.031
lipocalin     0.664  0.458      0.639     0.511     0.664         0.662     -0.002
scp2          0.622  0.567      0.617     0.560     0.622         0.671      0.050

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.596               0.617                  0.057                     0.092
net               0.536               0.519                  0.077                     0.110
fit_chem          0.621               0.617                  0.054                     0.049
fit_chem_net      0.674               0.659                  0.058                     0.080
increment         0.053               0.027                  0.038                     0.054

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.614               0.617                  0.059                     0.084
net_pair       0.515               0.485                  0.086                     0.150
```
