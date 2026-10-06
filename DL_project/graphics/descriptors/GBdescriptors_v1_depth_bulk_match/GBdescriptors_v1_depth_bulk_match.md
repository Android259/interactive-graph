# GBdescriptors_v1_depth_bulk_match

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'GBdescriptors_v1_depth_bulk_match'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4030      0.5738      0.4891      0.5588      0.4060      0.6000
groups_GLTP            5      0.7120      0.5280      0.6732      0.4989      0.7000      0.6231
groups_IP_trans        5      0.6957      0.3957      0.7102      0.4069      0.8083      0.4213
groups_LBP_BPI_CETP    5      0.5652      0.6851      0.5005      0.6204      0.5250      0.7064
groups_ML              5      0.2800      0.7000      0.4454      0.6884      0.5200      0.7200
groups_OSBP            5      0.5333      0.4667      0.7067      0.4027      0.8000      0.5667
groups_START           5      0.4462      0.5393      0.5877      0.4706      0.4906      0.6090
groups_lipocalin       5      0.6667      0.3917      0.6086      0.4841      0.7333      0.3944
groups_scp2            5      0.6706      0.4353      0.5269      0.5725      0.6941      0.5471
ALL                   45      0.5525      0.5240      0.5832      0.5226      0.6308      0.5764

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6036      0.5903     0.0931  45
max valid BA                0.6390      0.6176     0.1060  45
best valid F1               0.5909      0.5833     0.1272  45
test BA                     0.5382      0.5000     0.1011  45
test F1                     0.4156      0.4746     0.2137  45
test sensitivity            0.5525      0.5882     0.3443  45
test specificity            0.5240      0.5106     0.3027  45
test precision              0.4105      0.3916     0.1654  42
test loss                   0.8326      0.7015     0.4064  45
FPR (FP/(FP+TN))            0.4760      0.4894     0.3027  45
FNR (FN/(FN+TP))            0.4475      0.4118     0.3443  45

=== abs(sensitivity-specificity) gap: mean=0.5157 median=0.4894 n=45 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5030      0.5000     0.0056  5
  max valid BA                0.5200      0.5235     0.0119  5
  best valid F1               0.5399      0.6738     0.2206  5
  test BA                     0.4884      0.5000     0.0392  5
  test F1                     0.3063      0.1739     0.3474  5
  test sensitivity            0.4030      0.1194     0.5011  5
  test specificity            0.5738      0.7213     0.4733  5
  test precision              0.4597      0.5234     0.1212  3
  test loss                   1.2245      1.0325     0.6708  5
  FPR (FP/(FP+TN))            0.4262      0.2787     0.4733  5
  FNR (FN/(FN+TP))            0.5970      0.8806     0.5011  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6615      0.6731     0.0586  5
  max valid BA                0.7308      0.7308     0.0881  5
  best valid F1               0.6949      0.7692     0.1649  5
  test BA                     0.6200      0.6200     0.1049  5
  test F1                     0.6245      0.6667     0.1617  5
  test sensitivity            0.7120      0.9200     0.3116  5
  test specificity            0.5280      0.5200     0.2876  5
  test precision              0.6410      0.6216     0.1508  5
  test loss                   0.7120      0.6908     0.0811  5
  FPR (FP/(FP+TN))            0.4720      0.4800     0.2876  5
  FNR (FN/(FN+TP))            0.2880      0.0800     0.3116  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6148      0.6073     0.1046  5
  max valid BA                0.6356      0.6494     0.0954  5
  best valid F1               0.5753      0.5897     0.0734  5
  test BA                     0.5457      0.5583     0.1005  5
  test F1                     0.4662      0.4946     0.1084  5
  test sensitivity            0.6957      0.6957     0.2645  5
  test specificity            0.3957      0.4468     0.2367  5
  test precision              0.3617      0.3902     0.0752  5
  test loss                   0.7936      0.6917     0.2187  5
  FPR (FP/(FP+TN))            0.6043      0.5532     0.2367  5
  FNR (FN/(FN+TP))            0.3043      0.3043     0.2645  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6157      0.6099     0.0804  5
  max valid BA                0.6410      0.6210     0.0908  5
  best valid F1               0.5712      0.5263     0.0779  5
  test BA                     0.6252      0.5703     0.0970  5
  test F1                     0.4507      0.4746     0.2086  5
  test sensitivity            0.5652      0.6087     0.3889  5
  test specificity            0.6851      0.5319     0.2228  5
  test precision              0.5063      0.5000     0.1006  5
  test loss                   0.6812      0.6824     0.0053  5
  FPR (FP/(FP+TN))            0.3149      0.4681     0.2228  5
  FNR (FN/(FN+TP))            0.4348      0.3913     0.3889  5

groups_ML (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6200      0.6500     0.0908  5
  max valid BA                0.6300      0.6500     0.0837  5
  best valid F1               0.5315      0.5556     0.0894  5
  test BA                     0.4900      0.5000     0.0224  5
  test F1                     0.2168      0.2500     0.2128  5
  test sensitivity            0.2800      0.2000     0.3347  5
  test specificity            0.7000      0.8000     0.3162  5
  test precision              0.2500      0.3333     0.1667  4
  test loss                   0.7940      0.7231     0.1881  5
  FPR (FP/(FP+TN))            0.3000      0.2000     0.3162  5
  FNR (FN/(FN+TP))            0.7200      0.8000     0.3347  5

groups_OSBP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6833      0.7500     0.1087  5
  max valid BA                0.7500      0.8333     0.1443  5
  best valid F1               0.7133      0.8000     0.1325  5
  test BA                     0.5000      0.4167     0.1443  5
  test F1                     0.3476      0.2857     0.2518  5
  test sensitivity            0.5333      0.3333     0.4472  5
  test specificity            0.4667      0.5000     0.2981  5
  test precision              0.2667      0.2500     0.1807  5
  test loss                   1.1045      0.7015     0.9232  5
  FPR (FP/(FP+TN))            0.5333      0.5000     0.2981  5
  FNR (FN/(FN+TP))            0.4667      0.6667     0.4472  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5498      0.5519     0.0387  5
  max valid BA                0.5596      0.5587     0.0328  5
  best valid F1               0.5552      0.5769     0.0563  5
  test BA                     0.4927      0.4823     0.0802  5
  test F1                     0.3870      0.3636     0.1757  5
  test sensitivity            0.4462      0.4308     0.3073  5
  test specificity            0.5393      0.5281     0.3491  5
  test precision              0.4274      0.4088     0.1150  5
  test loss                   0.7057      0.7018     0.0298  5
  FPR (FP/(FP+TN))            0.4607      0.4719     0.3491  5
  FNR (FN/(FN+TP))            0.5538      0.5692     0.3073  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5639      0.5000     0.1210  5
  max valid BA                0.6194      0.6111     0.0959  5
  best valid F1               0.5451      0.5347     0.0977  5
  test BA                     0.5292      0.5694     0.1233  5
  test F1                     0.4571      0.5133     0.1318  5
  test sensitivity            0.6667      0.7778     0.2880  5
  test specificity            0.3917      0.3889     0.3018  5
  test precision              0.3782      0.3766     0.1515  5
  test loss                   0.7763      0.7169     0.2083  5
  FPR (FP/(FP+TN))            0.6083      0.6111     0.3018  5
  FNR (FN/(FN+TP))            0.3333      0.2222     0.2880  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6206      0.6324     0.0828  5
  max valid BA                0.6647      0.6471     0.0854  5
  best valid F1               0.5921      0.5667     0.0857  5
  test BA                     0.5529      0.5882     0.0934  5
  test F1                     0.4842      0.5000     0.0688  5
  test sensitivity            0.6706      0.6471     0.1354  5
  test specificity            0.4353      0.5000     0.2508  5
  test precision              0.3914      0.4074     0.0927  5
  test loss                   0.7019      0.6961     0.0159  5
  FPR (FP/(FP+TN))            0.5647      0.5000     0.2508  5
  FNR (FN/(FN+TP))            0.3294      0.3529     0.1354  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (aromatic_contact,aromatic_share,buriedness_q50,chain,chain_extent_gap,depth_bulk_match,depth_q10,ev14_q50,hbond,hbond_match,heavy,hydropathy_rim,pocket_elongation,pocket_extent,pocket_flatness,polar_share,tail_count,tail_elongation_fit,unsaturation,volume_fit), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.206         0.564    0.466              0.492         0.512
GLTP                     0.234         0.781    0.579              0.810         0.546
IP_trans                 0.255         0.620    0.509              0.681         0.517
LBP_BPI_CETP             0.263         0.674    0.504              0.659         0.552
START                    0.221         0.472    0.459              0.492         0.456
lipocalin                0.211         0.618    0.373              0.578         0.455
scp2                     0.199         0.586    0.619              0.571         0.506

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.616               0.614                  0.054                     0.096
net_AUC           0.501               0.495                  0.117                     0.081

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.612               0.617                  0.050                     0.114
net_AUC_pair           0.506               0.525                  0.122                     0.039

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.616  0.485      0.612     0.466
10     0.616  0.504      0.612     0.506
49     0.616  0.503      0.612     0.517
51     0.616  0.501      0.612     0.515
120    0.616  0.501      0.612     0.506

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.628         0.686      0.058
10        0.628         0.681      0.053
49        0.628         0.679      0.051
51        0.628         0.675      0.047
120       0.628         0.669      0.041

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.564  0.466      0.492     0.512     0.569         0.589      0.020
GLTP          0.781  0.579      0.810     0.546     0.781         0.803      0.022
IP_trans      0.620  0.509      0.681     0.517     0.620         0.683      0.063
LBP_BPI_CETP  0.674  0.504      0.659     0.552     0.674         0.669     -0.005
START         0.472  0.459      0.492     0.456     0.547         0.580      0.032
lipocalin     0.618  0.373      0.578     0.455     0.618         0.717      0.099
scp2          0.586  0.619      0.571     0.506     0.586         0.641      0.055

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.616               0.614                  0.054                     0.096
net               0.501               0.495                  0.117                     0.081
fit_chem          0.628               0.614                  0.050                     0.079
fit_chem_net      0.669               0.669                  0.064                     0.077
increment         0.041               0.022                  0.044                     0.034

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.612               0.617                  0.050                     0.114
net_pair       0.506               0.525                  0.122                     0.039
```
