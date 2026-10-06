# bbp_dcs_rand_smd_fa_nps_dpt01_add_plm8_hid8_wd001_ep120

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'bbp_dcs_rand_smd_fa_nps_dpt01_add_plm8_hid8_wd001_ep120'
rows: 30

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.8060      0.3224      0.7390      0.7257      0.8060      0.2796
groups_GLTP            4      0.2000      0.8400      0.7443      0.6594      0.3462      0.9038
groups_IP_trans        4      0.5543      0.5372      0.8774      0.7393      0.5521      0.5798
groups_LBP_BPI_CETP    4      0.5217      0.6436      0.8293      0.6930      0.6250      0.6702
groups_START           5      0.5200      0.5169      0.6949      0.6823      0.5594      0.5618
groups_lipocalin       5      0.4500      0.6444      0.6043      0.5703      0.4222      0.6722
groups_scp2            5      0.3647      0.8059      0.7557      0.6559      0.4941      0.8529
ALL                   30      0.4732      0.6296      0.7432      0.6695      0.5296      0.6630

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5968      0.5946     0.0786  30
max valid BA                0.6557      0.6382     0.0960  30
best valid F1               0.6121      0.6087     0.1130  30
test BA                     0.5514      0.5394     0.0726  30
test F1                     0.4078      0.4629     0.1986  30
test sensitivity            0.4732      0.4706     0.3104  30
test specificity            0.6296      0.7017     0.2944  30
test precision              0.4853      0.4595     0.1968  29
test loss                   0.7758      0.6929     0.2694  30
FPR (FP/(FP+TN))            0.3704      0.2983     0.2944  30
FNR (FN/(FN+TP))            0.5268      0.5294     0.3104  30

=== abs(sensitivity-specificity) gap: mean=0.5211 median=0.4931 n=30 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5428      0.5433     0.0256  3
  max valid BA                0.5869      0.5781     0.0164  3
  best valid F1               0.6932      0.6932     0.0025  3
  test BA                     0.5642      0.5521     0.0356  3
  test F1                     0.6594      0.6961     0.0728  3
  test sensitivity            0.8060      0.8806     0.1834  3
  test specificity            0.3224      0.3279     0.1558  3
  test precision              0.5661      0.5556     0.0208  3
  test loss                   0.6930      0.6842     0.0176  3
  FPR (FP/(FP+TN))            0.6776      0.6721     0.1558  3
  FNR (FN/(FN+TP))            0.1940      0.1194     0.1834  3

groups_GLTP (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6250      0.6442     0.0974  4
  max valid BA                0.7500      0.7308     0.1132  4
  best valid F1               0.7615      0.7292     0.1042  4
  test BA                     0.5200      0.4900     0.1541  4
  test F1                     0.2692      0.2134     0.2848  4
  test sensitivity            0.2000      0.1400     0.2286  4
  test specificity            0.8400      0.8800     0.1131  4
  test precision              0.4452      0.4571     0.4117  4
  test loss                   0.7426      0.7048     0.1228  4
  FPR (FP/(FP+TN))            0.1600      0.1200     0.1131  4
  FNR (FN/(FN+TP))            0.8000      0.8600     0.2286  4

groups_IP_trans (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5659      0.5674     0.0484  4
  max valid BA                0.6858      0.6611     0.0831  4
  best valid F1               0.6106      0.5927     0.0868  4
  test BA                     0.5458      0.5389     0.0184  4
  test F1                     0.3814      0.4275     0.1724  4
  test sensitivity            0.5543      0.5652     0.4295  4
  test specificity            0.5372      0.5426     0.4079  4
  test precision              0.4441      0.3807     0.1493  4
  test loss                   0.8121      0.7511     0.2117  4
  FPR (FP/(FP+TN))            0.4628      0.4574     0.4079  4
  FNR (FN/(FN+TP))            0.4457      0.4348     0.4295  4

groups_LBP_BPI_CETP (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6476      0.6576     0.0496  4
  max valid BA                0.6884      0.7019     0.0783  4
  best valid F1               0.6012      0.5998     0.0737  4
  test BA                     0.5827      0.5800     0.0728  4
  test F1                     0.4560      0.4658     0.1056  4
  test sensitivity            0.5217      0.5217     0.1775  4
  test specificity            0.6436      0.6489     0.1062  4
  test precision              0.4156      0.4062     0.0759  4
  test loss                   1.0991      0.8947     0.6167  4
  FPR (FP/(FP+TN))            0.3564      0.3511     0.1062  4
  FNR (FN/(FN+TP))            0.4783      0.4783     0.1775  4

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5606      0.5452     0.0517  5
  max valid BA                0.5916      0.6124     0.0530  5
  best valid F1               0.6010      0.6087     0.0352  5
  test BA                     0.5184      0.5000     0.0478  5
  test F1                     0.4079      0.4552     0.2460  5
  test sensitivity            0.5200      0.5077     0.3654  5
  test specificity            0.5169      0.4719     0.3275  5
  test precision              0.4358      0.4205     0.0407  4
  test loss                   0.7985      0.6964     0.2079  5
  FPR (FP/(FP+TN))            0.4831      0.5281     0.3275  5
  FNR (FN/(FN+TP))            0.4800      0.4923     0.3654  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5472      0.5139     0.0891  5
  max valid BA                0.5736      0.5764     0.0854  5
  best valid F1               0.4687      0.4638     0.0912  5
  test BA                     0.5472      0.5139     0.0707  5
  test F1                     0.3559      0.4823     0.2050  5
  test sensitivity            0.4500      0.4167     0.3755  5
  test specificity            0.6444      0.8611     0.4116  5
  test precision              0.5530      0.3846     0.2868  5
  test loss                   0.6731      0.6823     0.0586  5
  FPR (FP/(FP+TN))            0.3556      0.1389     0.4116  5
  FNR (FN/(FN+TP))            0.5500      0.5833     0.3755  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6765      0.6471     0.0633  5
  max valid BA                0.7176      0.7059     0.0669  5
  best valid F1               0.6084      0.6111     0.1088  5
  test BA                     0.5853      0.6029     0.0573  5
  test F1                     0.4022      0.4286     0.1265  5
  test sensitivity            0.3647      0.4118     0.1465  5
  test specificity            0.8059      0.8529     0.1341  5
  test precision              0.5296      0.5455     0.1246  5
  test loss                   0.6446      0.6268     0.0414  5
  FPR (FP/(FP+TN))            0.1941      0.1471     0.1341  5
  FNR (FN/(FN+TP))            0.6353      0.5882     0.1465  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.630         0.484    0.477       4.0              0.369         0.482     5.0               0.458          0.456
GLTP                     0.605         0.521    0.543       2.0              0.512         0.512     3.0               0.523          0.437
IP_trans                 0.722         0.680    0.560       3.0              0.677         0.573     2.4               0.590          0.455
LBP_BPI_CETP             0.719         0.798    0.624       2.0              0.798         0.616     1.6               0.784          0.567
START                    0.576         0.508    0.509       3.0              0.474         0.487     4.0               0.536          0.526
lipocalin                0.565         0.331    0.312       5.0              0.246         0.192     2.2               0.646          0.575
scp2                     0.651         0.489    0.536       2.8              0.593         0.448     2.6               0.642          0.489

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.545               0.503                  0.065                     0.151
net_AUC           0.509               0.536                  0.086                     0.098

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.524               0.493                  0.065                     0.186
net_AUC_prot           0.473               0.497                  0.064                     0.137

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.597               0.581                  0.085                     0.106
net_AUC_lipid           0.501               0.492                  0.132                     0.056

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.479      0.524     0.480
10     0.545  0.541      0.524     0.537
49     0.545  0.527      0.524     0.476
51     0.545  0.521      0.524     0.483
120    0.545  0.509      0.524     0.473

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.618         0.642      0.024          0.653              0.693           0.039
10        0.618         0.663      0.045          0.653              0.699           0.045
49        0.618         0.665      0.047          0.653              0.697           0.044
51        0.618         0.655      0.037          0.653              0.688           0.035
120       0.618         0.650      0.032          0.653              0.691           0.038

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.484  0.477      0.369     0.482     0.539         0.598      0.059          0.613              0.684           0.071
GLTP          0.521  0.543      0.512     0.512     0.543         0.572      0.029          0.565              0.617           0.052
IP_trans      0.680  0.560      0.677     0.573     0.680         0.697      0.017          0.693              0.714           0.021
LBP_BPI_CETP  0.798  0.624      0.798     0.616     0.798         0.798     -0.001          0.801              0.803           0.002
START         0.508  0.509      0.474     0.487     0.536         0.570      0.034          0.606              0.626           0.020
lipocalin     0.331  0.312      0.246     0.192     0.669         0.678      0.010          0.673              0.715           0.041
scp2          0.489  0.536      0.593     0.448     0.562         0.640      0.079          0.622              0.679           0.057

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.545               0.503                  0.065                     0.151
net               0.509               0.536                  0.086                     0.098
fit_chem          0.618               0.590                  0.052                     0.101
fit_chem_net      0.650               0.640                  0.060                     0.082
increment         0.032               0.018                  0.042                     0.028

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.524               0.493                  0.065                     0.186
net_prot               0.473               0.497                  0.064                     0.137
fit_chem_prot          0.653               0.662                  0.055                     0.078
fit_chem_net_prot      0.691               0.691                  0.058                     0.063
increment_prot         0.038               0.018                  0.035                     0.024
```
