# geometric_edge_mlp_protgeom8_no_pocket_elongation

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom8_no_pocket_elongation'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5881      0.5377      0.6949      0.6130      0.5910      0.5548
groups_GLTP            5      0.4640      0.5120      0.8063      0.6114      0.5077      0.6769
groups_IP_trans        5      0.5565      0.6894      0.6650      0.6198      0.6167      0.6851
groups_LBP_BPI_CETP    5      0.2522      0.8723      0.7608      0.5410      0.2833      0.8766
groups_START           5      0.7631      0.4360      0.8410      0.5666      0.7937      0.4135
groups_lipocalin       5      0.7722      0.4528      0.8575      0.4969      0.8278      0.4667
groups_scp2            5      0.5176      0.6706      0.7794      0.5385      0.6588      0.7353
ALL                   35      0.5591      0.5958      0.7721      0.5696      0.6113      0.6298

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6206      0.6130     0.0834  35
max valid BA                0.6564      0.6458     0.0767  35
best valid F1               0.6320      0.6477     0.0765  35
test BA                     0.5775      0.5892     0.0838  35
test F1                     0.4779      0.5185     0.1874  35
test sensitivity            0.5591      0.6471     0.2780  35
test specificity            0.5958      0.5882     0.2440  35
test precision              0.4641      0.4783     0.1363  35
test loss                   0.7363      0.7033     0.1448  35
FPR (FP/(FP+TN))            0.4042      0.4118     0.2440  35
FNR (FN/(FN+TP))            0.4409      0.3529     0.2780  35

=== abs(sensitivity-specificity) gap: mean=0.3967 median=0.3215 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5729      0.5995     0.0639  5
  max valid BA                0.6075      0.6094     0.0569  5
  best valid F1               0.7063      0.7111     0.0129  5
  test BA                     0.5629      0.5728     0.0685  5
  test F1                     0.5323      0.6301     0.2708  5
  test sensitivity            0.5881      0.6866     0.3186  5
  test specificity            0.5377      0.4590     0.1975  5
  test precision              0.5181      0.5823     0.1671  5
  test loss                   0.7081      0.7164     0.0225  5
  FPR (FP/(FP+TN))            0.4623      0.5410     0.1975  5
  FNR (FN/(FN+TP))            0.4119      0.3134     0.3186  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5923      0.5577     0.0583  5
  max valid BA                0.6346      0.6346     0.0827  5
  best valid F1               0.6853      0.6769     0.0176  5
  test BA                     0.4880      0.4800     0.0912  5
  test F1                     0.4706      0.5185     0.1055  5
  test sensitivity            0.4640      0.4800     0.1315  5
  test specificity            0.5120      0.4000     0.2008  5
  test precision              0.4970      0.4828     0.1229  5
  test loss                   0.7921      0.7453     0.1140  5
  FPR (FP/(FP+TN))            0.4880      0.6000     0.2008  5
  FNR (FN/(FN+TP))            0.5360      0.5200     0.1315  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6509      0.6343     0.0508  5
  max valid BA                0.7031      0.6946     0.0471  5
  best valid F1               0.6216      0.6071     0.0508  5
  test BA                     0.6229      0.6226     0.0384  5
  test F1                     0.4911      0.5000     0.0822  5
  test sensitivity            0.5565      0.4783     0.2616  5
  test specificity            0.6894      0.7447     0.1999  5
  test precision              0.4802      0.4783     0.0447  5
  test loss                   0.6853      0.6758     0.0832  5
  FPR (FP/(FP+TN))            0.3106      0.2553     0.1999  5
  FNR (FN/(FN+TP))            0.4435      0.5217     0.2616  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5800      0.5519     0.0805  5
  max valid BA                0.6359      0.6241     0.0648  5
  best valid F1               0.5347      0.5393     0.0971  5
  test BA                     0.5623      0.5111     0.1110  5
  test F1                     0.2637      0.1818     0.2685  5
  test sensitivity            0.2522      0.1304     0.3034  5
  test specificity            0.8723      0.8511     0.1020  5
  test precision              0.3703      0.4444     0.2348  5
  test loss                   0.9303      0.8823     0.2861  5
  FPR (FP/(FP+TN))            0.1277      0.1489     0.1020  5
  FNR (FN/(FN+TP))            0.7478      0.8696     0.3034  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6036      0.5760     0.0443  5
  max valid BA                0.6172      0.6131     0.0369  5
  best valid F1               0.6219      0.6211     0.0299  5
  test BA                     0.5995      0.6105     0.0430  5
  test F1                     0.6000      0.6099     0.0436  5
  test sensitivity            0.7631      0.6923     0.1285  5
  test specificity            0.4360      0.3708     0.1338  5
  test precision              0.5006      0.4959     0.0428  5
  test loss                   0.7021      0.7022     0.0297  5
  FPR (FP/(FP+TN))            0.5640      0.6292     0.1338  5
  FNR (FN/(FN+TP))            0.2369      0.3077     0.1285  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6472      0.6875     0.1366  5
  max valid BA                0.6847      0.7083     0.1150  5
  best valid F1               0.6181      0.6239     0.0891  5
  test BA                     0.6125      0.6181     0.1073  5
  test F1                     0.5499      0.5109     0.0883  5
  test sensitivity            0.7722      0.8056     0.2234  5
  test specificity            0.4528      0.4861     0.3909  5
  test precision              0.4725      0.4394     0.1606  5
  test loss                   0.6793      0.6734     0.0799  5
  FPR (FP/(FP+TN))            0.5472      0.5139     0.3909  5
  FNR (FN/(FN+TP))            0.2278      0.1944     0.2234  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6971      0.6618     0.0796  5
  max valid BA                0.7118      0.6912     0.0732  5
  best valid F1               0.6362      0.6047     0.0748  5
  test BA                     0.5941      0.6176     0.0629  5
  test F1                     0.4378      0.5116     0.1927  5
  test sensitivity            0.5176      0.6471     0.2644  5
  test specificity            0.6706      0.5882     0.1462  5
  test precision              0.4097      0.4400     0.0914  5
  test loss                   0.6568      0.6635     0.0126  5
  FPR (FP/(FP+TN))            0.3294      0.4118     0.1462  5
  FNR (FN/(FN+TP))            0.4824      0.3529     0.2644  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.630         0.483    0.565       4.0              0.365         0.505     5.0               0.449          0.616
GLTP                     0.605         0.521    0.509       2.0              0.511         0.508     3.0               0.523          0.534
IP_trans                 0.722         0.681    0.616       3.0              0.677         0.700     2.4               0.590          0.588
LBP_BPI_CETP             0.719         0.798    0.640       2.0              0.798         0.651     1.6               0.784          0.624
START                    0.576         0.508    0.553       3.0              0.475         0.521     4.0               0.535          0.605
lipocalin                0.565         0.334    0.566       5.0              0.252         0.634     2.2               0.647          0.554
scp2                     0.651         0.488    0.688       2.8              0.592         0.612     2.6               0.649          0.656

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.545               0.499                  0.066                     0.151
net_AUC           0.591               0.583                  0.088                     0.060

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.524               0.493                  0.065                     0.185
net_AUC_prot           0.590               0.553                  0.087                     0.078

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.597               0.581                  0.085                     0.109
net_AUC_lipid           0.597               0.622                  0.134                     0.042

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.541      0.524     0.550
10     0.545  0.568      0.524     0.560
49     0.545  0.564      0.524     0.541
51     0.545  0.589      0.524     0.576
120    0.545  0.591      0.524     0.590

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.619         0.659      0.040          0.655              0.690           0.035
10        0.619         0.669      0.050          0.655              0.695           0.040
49        0.619         0.670      0.050          0.655              0.695           0.040
51        0.619         0.681      0.062          0.655              0.712           0.057
120       0.619         0.672      0.053          0.655              0.702           0.047

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.483  0.565      0.365     0.505     0.539         0.594      0.054          0.614              0.659           0.045
GLTP          0.521  0.509      0.511     0.508     0.542         0.596      0.054          0.565              0.593           0.028
IP_trans      0.681  0.616      0.677     0.700     0.681         0.724      0.043          0.692              0.746           0.054
LBP_BPI_CETP  0.798  0.640      0.798     0.651     0.798         0.806      0.007          0.801              0.819           0.018
START         0.508  0.553      0.475     0.521     0.536         0.615      0.079          0.604              0.653           0.049
lipocalin     0.334  0.566      0.252     0.634     0.666         0.703      0.038          0.672              0.726           0.055
scp2          0.488  0.688      0.592     0.612     0.572         0.670      0.098          0.636              0.721           0.084

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.545               0.499                  0.066                     0.151
net               0.591               0.583                  0.088                     0.060
fit_chem          0.619               0.580                  0.052                     0.100
fit_chem_net      0.672               0.664                  0.061                     0.078
increment         0.053               0.026                  0.054                     0.029

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.524               0.493                  0.065                     0.185
net_prot               0.590               0.553                  0.087                     0.078
fit_chem_prot          0.655               0.658                  0.053                     0.077
fit_chem_net_prot      0.702               0.710                  0.062                     0.074
increment_prot         0.047               0.022                  0.055                     0.021
```
