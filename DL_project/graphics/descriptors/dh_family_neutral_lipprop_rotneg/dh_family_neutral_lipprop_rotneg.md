# dh_family_neutral_lipprop_rotneg

## Summary (analysis/summarize_label.py)

```
Summary: 'dh_family_neutral_lipprop_rotneg'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.9731      0.0885      0.5663      0.4054      0.9343      0.1516
groups_GLTP            5      1.0000      0.0000      0.6063      0.3858      0.9000      0.1231
groups_IP_trans        5      1.0000      0.0000      0.8264      0.1601      0.9583      0.0723
groups_LBP_BPI_CETP    5      0.9652      0.1532      0.5593      0.4428      0.9417      0.1830
groups_ML              5      0.6000      0.4000      0.3932      0.5986      0.6400      0.4800
groups_OSBP            5      0.8667      0.2000      0.5224      0.4738      0.8000      0.2000
groups_START           5      0.7262      0.3011      0.5693      0.4604      0.7188      0.3281
groups_lipocalin       5      0.9500      0.0500      0.8287      0.1761      0.9667      0.0611
groups_scp2            5      1.0000      0.0000      0.7875      0.2041      1.0000      0.0118
ALL                   45      0.8979      0.1325      0.6288      0.3674      0.8733      0.1790

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5180      0.5000     0.0408  45
max valid BA                0.5262      0.5004     0.0533  45
best valid F1               0.5593      0.5053     0.0807  45
test BA                     0.5152      0.5000     0.0637  45
test AUC                    0.5136      0.5094     0.1592  45
test AUC in-protein         0.5160      0.5077     0.1818  42
  (proteins averaged)       2.6000      3.0000     1.3718  45
test AUC in-protein (pairs)      0.5401      0.5600     0.1968  45
  (proteins contributing)      3.0222      3.0000     1.7900  45
test F1                     0.5353      0.5000     0.1061  45
test sensitivity            0.8979      1.0000     0.2152  45
test specificity            0.1325      0.0000     0.2587  45
test precision              0.4077      0.3333     0.1318  45
test loss                   0.8652      0.7817     0.2040  45
FPR (FP/(FP+TN))            0.8675      1.0000     0.2587  45
FNR (FN/(FN+TP))            0.1021      0.0000     0.2152  45

=== abs(sensitivity-specificity) gap: mean=0.8334 median=1.0000 n=45 ===
sensitivity std across seeds (by group): mean=0.1246 median=0.0778 n=9
specificity std across seeds (by group): mean=0.1746 median=0.0974 n=9

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5308      0.5215     0.0259  5
  max valid BA                0.5430      0.5215     0.0522  5
  best valid F1               0.6964      0.6872     0.0205  5
  test BA                     0.5308      0.5171     0.0358  5
  test AUC                    0.5356      0.5190     0.0374  5
  test AUC in-protein         0.5573      0.5463     0.0459  5
    (proteins averaged)       4.0000      4.0000     0.0000  5
  test AUC in-protein (pairs)      0.5924      0.5621     0.0922  5
    (proteins contributing)      4.4000      4.0000     0.5477  5
  test F1                     0.6947      0.6911     0.0113  5
  test sensitivity            0.9731      0.9851     0.0287  5
  test specificity            0.0885      0.0492     0.0974  5
  test precision              0.5408      0.5323     0.0218  5
  test loss                   0.7102      0.6914     0.0475  5
  FPR (FP/(FP+TN))            0.9115      0.9508     0.0974  5
  FNR (FN/(FN+TP))            0.0269      0.0149     0.0287  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0000  5
  max valid BA                0.5115      0.5000     0.0258  5
  best valid F1               0.6667      0.6667     0.0000  5
  test BA                     0.5000      0.5000     0.0000  5
  test AUC                    0.4006      0.4832     0.2217  5
  test AUC in-protein         0.3783      0.4960     0.1929  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3545      0.4139     0.1778  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.6667      0.6667     0.0000  5
  test sensitivity            1.0000      1.0000     0.0000  5
  test specificity            0.0000      0.0000     0.0000  5
  test precision              0.5000      0.5000     0.0000  5
  test loss                   0.8546      0.8377     0.1529  5
  FPR (FP/(FP+TN))            1.0000      1.0000     0.0000  5
  FNR (FN/(FN+TP))            0.0000      0.0000     0.0000  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4980      0.5000     0.0046  5
  max valid BA                0.5153      0.5213     0.0146  5
  best valid F1               0.5099      0.5111     0.0046  5
  test BA                     0.5000      0.5000     0.0000  5
  test AUC                    0.5249      0.5051     0.1032  5
  test AUC in-protein         0.5891      0.6015     0.1422  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5606      0.5809     0.0855  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.4946      0.4946     0.0000  5
  test sensitivity            1.0000      1.0000     0.0000  5
  test specificity            0.0000      0.0000     0.0000  5
  test precision              0.3286      0.3286     0.0000  5
  test loss                   1.0055      1.0255     0.2317  5
  FPR (FP/(FP+TN))            1.0000      1.0000     0.0000  5
  FNR (FN/(FN+TP))            0.0000      0.0000     0.0000  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5448      0.5000     0.1001  5
  max valid BA                0.5623      0.5000     0.1394  5
  best valid F1               0.5553      0.5053     0.1119  5
  test BA                     0.5592      0.5000     0.1324  5
  test AUC                    0.7177      0.8409     0.2870  5
  test AUC in-protein         0.7406      0.8666     0.3273  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.7368      0.8664     0.3237  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5391      0.4946     0.0994  5
  test sensitivity            0.9652      1.0000     0.0778  5
  test specificity            0.1532      0.0000     0.3425  5
  test precision              0.3895      0.3286     0.1363  5
  test loss                   0.8722      0.7708     0.2286  5
  FPR (FP/(FP+TN))            0.8468      1.0000     0.3425  5
  FNR (FN/(FN+TP))            0.0348      0.0000     0.0778  5

groups_ML (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5600      0.5500     0.0418  5
  max valid BA                0.5600      0.5500     0.0418  5
  best valid F1               0.5053      0.5000     0.0118  5
  test BA                     0.5000      0.5000     0.1225  5
  test AUC                    0.5320      0.5600     0.1035  5
  test AUC in-protein         0.5320      0.5600     0.1035  5
    (proteins averaged)       1.0000      1.0000     0.0000  5
  test AUC in-protein (pairs)      0.5320      0.5600     0.1035  5
    (proteins contributing)      1.0000      1.0000     0.0000  5
  test F1                     0.4190      0.5000     0.1444  5
  test sensitivity            0.6000      0.6000     0.2828  5
  test specificity            0.4000      0.4000     0.2449  5
  test precision              0.3333      0.3333     0.1166  5
  test loss                   0.7133      0.6850     0.0615  5
  FPR (FP/(FP+TN))            0.6000      0.6000     0.2449  5
  FNR (FN/(FN+TP))            0.4000      0.4000     0.2828  5

groups_OSBP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0000  5
  max valid BA                0.5000      0.5000     0.0000  5
  best valid F1               0.5000      0.5000     0.0000  5
  test BA                     0.5333      0.5000     0.0745  5
  test AUC                    0.5667      0.5556     0.1069  5
  test AUC in-protein         0.6389      0.6389     0.1964  2
    (proteins averaged)       0.4000      0.0000     0.5477  5
  test AUC in-protein (pairs)      0.6028      0.7778     0.2972  5
    (proteins contributing)      1.6000      2.0000     0.5477  5
  test F1                     0.5000      0.5000     0.0000  5
  test sensitivity            0.8667      1.0000     0.2981  5
  test specificity            0.2000      0.0000     0.4472  5
  test precision              0.4667      0.3333     0.2981  5
  test loss                   0.8642      0.8054     0.1842  5
  FPR (FP/(FP+TN))            0.8000      1.0000     0.4472  5
  FNR (FN/(FN+TP))            0.1333      0.0000     0.2981  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5227      0.5183     0.0218  5
  max valid BA                0.5234      0.5183     0.0210  5
  best valid F1               0.5936      0.5899     0.0069  5
  test BA                     0.5136      0.5004     0.0188  5
  test AUC                    0.5010      0.5089     0.0582  5
  test AUC in-protein         0.4717      0.4776     0.0376  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5298      0.5295     0.0846  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.5112      0.5936     0.1194  5
  test sensitivity            0.7262      0.9231     0.3497  5
  test specificity            0.3011      0.1348     0.3698  5
  test precision              0.4442      0.4225     0.0408  5
  test loss                   0.7434      0.7063     0.0780  5
  FPR (FP/(FP+TN))            0.6989      0.8652     0.3698  5
  FNR (FN/(FN+TP))            0.2738      0.0769     0.3497  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5056      0.5000     0.0091  5
  max valid BA                0.5139      0.5000     0.0214  5
  best valid F1               0.5038      0.5000     0.0085  5
  test BA                     0.5000      0.5000     0.0196  5
  test AUC                    0.4272      0.4252     0.0375  5
  test AUC in-protein         0.3880      0.3468     0.0889  5
    (proteins averaged)       5.0000      5.0000     0.0000  5
  test AUC in-protein (pairs)      0.5660      0.5963     0.0683  5
    (proteins contributing)      7.2000      7.0000     0.4472  5
  test F1                     0.4928      0.5000     0.0205  5
  test sensitivity            0.9500      1.0000     0.0843  5
  test specificity            0.0500      0.0000     0.0692  5
  test precision              0.3331      0.3333     0.0100  5
  test loss                   1.0094      1.0582     0.2693  5
  FPR (FP/(FP+TN))            0.9500      1.0000     0.0692  5
  FNR (FN/(FN+TP))            0.0500      0.0000     0.0843  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0000  5
  max valid BA                0.5059      0.5000     0.0132  5
  best valid F1               0.5030      0.5000     0.0068  5
  test BA                     0.5000      0.5000     0.0000  5
  test AUC                    0.4171      0.3426     0.1204  5
  test AUC in-protein         0.4219      0.4106     0.0696  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.3855      0.3708     0.1780  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.5000      0.5000     0.0000  5
  test sensitivity            1.0000      1.0000     0.0000  5
  test specificity            0.0000      0.0000     0.0000  5
  test precision              0.3333      0.3333     0.0000  5
  test loss                   1.0137      0.9811     0.2325  5
  FPR (FP/(FP+TN))            1.0000      1.0000     0.0000  5
  FNR (FN/(FN+TP))            0.0000      0.0000     0.0000  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (apolar_sasa_share,aromatic_share,buriedness_q50,chain,hbond,heavy,hydropathy_rim,pocket_elongation,pocket_flatness,pocket_volume_per_sasa,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.263         0.636    0.459              0.609         0.494
GLTP                     0.278         0.676    0.364              0.747         0.395
IP_trans                 0.326         0.509    0.434              0.530         0.407
LBP_BPI_CETP             0.308         0.634    0.413              0.652         0.338
START                    0.273         0.430    0.511              0.497         0.474
lipocalin                0.273         0.663    0.445              0.639         0.472
scp2                     0.275         0.622    0.611              0.617         0.556

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.596               0.617                  0.057                     0.091
net_AUC           0.462               0.473                  0.093                     0.079

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.613               0.614                  0.060                     0.082
net_AUC_pair           0.448               0.477                  0.126                     0.073

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
       chem    net  chem_pair  net_pair
epoch                                  
1      0.58  0.468       0.58     0.488
10     0.58  0.536       0.58     0.547
49     0.58  0.427       0.58     0.454
51     0.58  0.423       0.58     0.453
120    0.58  0.462       0.58     0.448

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.621         0.678      0.057
10        0.621         0.666      0.045
49        0.621         0.676      0.055
51        0.621         0.673      0.052
120       0.621         0.673      0.052

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.633  0.459      0.605     0.494     0.633         0.647      0.014
GLTP          0.660  0.364      0.710     0.395     0.660         0.781      0.121
IP_trans      0.425  0.434      0.433     0.407     0.573         0.603      0.030
LBP_BPI_CETP  0.697  0.413      0.737     0.338     0.697         0.769      0.072
START         0.462  0.511      0.466     0.474     0.559         0.596      0.037
lipocalin     0.653  0.445      0.629     0.472     0.653         0.660      0.007
scp2          0.527  0.611      0.477     0.556     0.569         0.655      0.086

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.580               0.598                  0.060                     0.107
net               0.462               0.473                  0.093                     0.079
fit_chem          0.621               0.615                  0.049                     0.054
fit_chem_net      0.673               0.657                  0.046                     0.074
increment         0.052               0.034                  0.051                     0.042

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.580               0.568                  0.070                     0.122
net_pair       0.448               0.477                  0.126                     0.073
```
