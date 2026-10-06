# GBdescriptors_v1

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'GBdescriptors_v1'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.3701      0.7082      0.6246      0.4732      0.3313      0.7161
groups_GLTP            5      0.7200      0.5440      0.6571      0.4345      0.7385      0.5538
groups_IP_trans        5      0.3391      0.6809      0.6997      0.4275      0.4833      0.7404
groups_LBP_BPI_CETP    5      0.7391      0.6340      0.6598      0.5356      0.7583      0.6596
groups_ML              5      0.2000      0.7600      0.4493      0.6821      0.3600      0.8400
groups_OSBP            5      0.3333      0.3667      0.5931      0.5282      0.7333      0.6000
groups_START           5      0.4154      0.6337      0.6150      0.4280      0.4469      0.6360
groups_lipocalin       5      0.4500      0.5778      0.3755      0.6541      0.4944      0.6194
groups_scp2            5      0.5294      0.5765      0.5665      0.5740      0.6118      0.6706
ALL                   45      0.4552      0.6091      0.5823      0.5264      0.5509      0.6707

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6116      0.5972     0.0994  45
max valid BA                0.6322      0.6189     0.0991  45
best valid F1               0.5691      0.5965     0.1436  45
test BA                     0.5321      0.5278     0.1228  45
test F1                     0.3778      0.4444     0.2272  45
test sensitivity            0.4552      0.4030     0.3493  45
test specificity            0.6091      0.6800     0.2889  45
test precision              0.4330      0.4326     0.1880  42
test loss                   0.7517      0.6879     0.2769  45
FPR (FP/(FP+TN))            0.3909      0.3200     0.2889  45
FNR (FN/(FN+TP))            0.5448      0.5970     0.3493  45

=== abs(sensitivity-specificity) gap: mean=0.5294 median=0.4257 n=45 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5237      0.5325     0.0235  5
  max valid BA                0.5388      0.5545     0.0269  5
  best valid F1               0.5459      0.6702     0.2077  5
  test BA                     0.5392      0.5412     0.0457  5
  test F1                     0.3680      0.4231     0.2618  5
  test sensitivity            0.3701      0.3284     0.3861  5
  test specificity            0.7082      0.8197     0.4086  5
  test precision              0.6407      0.5946     0.1545  5
  test loss                   1.1997      0.7556     0.7220  5
  FPR (FP/(FP+TN))            0.2918      0.1803     0.4086  5
  FNR (FN/(FN+TP))            0.6299      0.6716     0.3861  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6538      0.6346     0.1027  5
  max valid BA                0.6654      0.6538     0.0918  5
  best valid F1               0.7110      0.6842     0.0741  5
  test BA                     0.6320      0.6400     0.0460  5
  test F1                     0.6501      0.6800     0.0746  5
  test sensitivity            0.7200      0.6800     0.2366  5
  test specificity            0.5440      0.6800     0.2851  5
  test precision              0.6374      0.6364     0.0761  5
  test loss                   0.6725      0.6826     0.0204  5
  FPR (FP/(FP+TN))            0.4560      0.3200     0.2851  5
  FNR (FN/(FN+TP))            0.2800      0.3200     0.2366  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6119      0.6037     0.0904  5
  max valid BA                0.6223      0.6246     0.0957  5
  best valid F1               0.5030      0.5275     0.1630  5
  test BA                     0.5100      0.5111     0.0421  5
  test F1                     0.2748      0.3030     0.1712  5
  test sensitivity            0.3391      0.2174     0.3707  5
  test specificity            0.6809      0.8298     0.3938  5
  test precision              0.3820      0.3913     0.1275  5
  test loss                   0.6854      0.6789     0.0217  5
  FPR (FP/(FP+TN))            0.3191      0.1702     0.3938  5
  FNR (FN/(FN+TP))            0.6609      0.7826     0.3707  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7090      0.6955     0.0417  5
  max valid BA                0.7324      0.7349     0.0329  5
  best valid F1               0.6474      0.6567     0.0419  5
  test BA                     0.6866      0.6582     0.0773  5
  test F1                     0.5804      0.5797     0.0991  5
  test sensitivity            0.7391      0.8696     0.2627  5
  test specificity            0.6340      0.6170     0.1616  5
  test precision              0.5046      0.5000     0.0522  5
  test loss                   0.6444      0.6519     0.0336  5
  FPR (FP/(FP+TN))            0.3660      0.3830     0.1616  5
  FNR (FN/(FN+TP))            0.2609      0.1304     0.2627  5

groups_ML (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6000      0.6000     0.1061  5
  max valid BA                0.6100      0.6500     0.1084  5
  best valid F1               0.4804      0.5455     0.1754  5
  test BA                     0.4800      0.5000     0.0758  5
  test F1                     0.1787      0.1818     0.1930  5
  test sensitivity            0.2000      0.2000     0.2449  5
  test specificity            0.7600      0.8000     0.2510  5
  test precision              0.2917      0.3333     0.1102  3
  test loss                   0.6964      0.7043     0.0333  5
  FPR (FP/(FP+TN))            0.2400      0.2000     0.2510  5
  FNR (FN/(FN+TP))            0.8000      0.8000     0.2449  5

groups_OSBP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6667      0.7500     0.1667  5
  max valid BA                0.7500      0.7500     0.1021  5
  best valid F1               0.6758      0.6667     0.0839  5
  test BA                     0.3500      0.2500     0.2236  5
  test F1                     0.2089      0.0000     0.2913  5
  test sensitivity            0.3333      0.0000     0.4714  5
  test specificity            0.3667      0.3333     0.0745  5
  test precision              0.1524      0.0000     0.2114  5
  test loss                   0.7103      0.7075     0.0155  5
  FPR (FP/(FP+TN))            0.6333      0.6667     0.0745  5
  FNR (FN/(FN+TP))            0.6667      1.0000     0.4714  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5414      0.5337     0.0467  5
  max valid BA                0.5554      0.5477     0.0493  5
  best valid F1               0.5375      0.5687     0.0917  5
  test BA                     0.5245      0.5169     0.0496  5
  test F1                     0.3873      0.3455     0.1595  5
  test sensitivity            0.4154      0.2923     0.3419  5
  test specificity            0.6337      0.7079     0.3517  5
  test precision              0.4808      0.4305     0.0984  5
  test loss                   0.6925      0.6922     0.0276  5
  FPR (FP/(FP+TN))            0.3663      0.2921     0.3517  5
  FNR (FN/(FN+TP))            0.5846      0.7077     0.3419  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5569      0.5486     0.0534  5
  max valid BA                0.5625      0.5486     0.0599  5
  best valid F1               0.4524      0.5195     0.1380  5
  test BA                     0.5139      0.5208     0.0384  5
  test F1                     0.3184      0.3667     0.2064  5
  test sensitivity            0.4500      0.3056     0.4037  5
  test specificity            0.5778      0.6944     0.3840  5
  test precision              0.3545      0.3464     0.0788  4
  test loss                   0.7812      0.7004     0.1479  5
  FPR (FP/(FP+TN))            0.4222      0.3056     0.3840  5
  FNR (FN/(FN+TP))            0.5500      0.6944     0.4037  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6412      0.6765     0.0710  5
  max valid BA                0.6529      0.6912     0.0603  5
  best valid F1               0.5685      0.6000     0.0566  5
  test BA                     0.5529      0.5588     0.0740  5
  test F1                     0.4335      0.4651     0.1166  5
  test sensitivity            0.5294      0.5294     0.2121  5
  test specificity            0.5765      0.5294     0.1389  5
  test precision              0.3804      0.3846     0.0835  5
  test loss                   0.6830      0.6816     0.0107  5
  FPR (FP/(FP+TN))            0.4235      0.4706     0.1389  5
  FNR (FN/(FN+TP))            0.4706      0.4706     0.2121  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (aromatic_contact,aromatic_share,buriedness_q50,chain,chain_extent_gap,depth_q10,ev14_q50,hbond,hbond_match,heavy,hydropathy_rim,pocket_elongation,pocket_extent,pocket_flatness,polar_share,tail_count,tail_elongation_fit,unsaturation,volume_fit), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.207         0.577    0.495              0.504         0.532
GLTP                     0.235         0.783    0.536              0.812         0.474
IP_trans                 0.257         0.615    0.556              0.651         0.541
LBP_BPI_CETP             0.265         0.638    0.705              0.645         0.741
START                    0.222         0.466    0.439              0.491         0.513
lipocalin                0.215         0.630    0.356              0.594         0.486
scp2                     0.202         0.594    0.567              0.595         0.488

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.615               0.612                  0.056                     0.094
net_AUC           0.522               0.491                  0.100                     0.110

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.613               0.606                  0.053                     0.108
net_AUC_pair           0.539               0.537                  0.102                     0.092

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.615  0.489      0.613     0.484
10     0.615  0.533      0.613     0.532
49     0.615  0.526      0.613     0.546
51     0.615  0.523      0.613     0.547
120    0.615  0.522      0.613     0.539

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.626         0.696      0.070
10        0.626         0.665      0.040
49        0.626         0.667      0.041
51        0.626         0.665      0.039
120       0.626         0.668      0.042

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.577  0.495      0.504     0.532     0.577         0.599      0.021
GLTP          0.783  0.536      0.812     0.474     0.783         0.848      0.064
IP_trans      0.615  0.556      0.651     0.541     0.615         0.624      0.009
LBP_BPI_CETP  0.638  0.705      0.645     0.741     0.638         0.715      0.077
START         0.466  0.439      0.491     0.513     0.544         0.589      0.045
lipocalin     0.630  0.356      0.594     0.486     0.630         0.697      0.068
scp2          0.594  0.567      0.595     0.488     0.594         0.603      0.009

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.615               0.612                  0.056                     0.094
net               0.522               0.491                  0.100                     0.110
fit_chem          0.626               0.622                  0.055                     0.077
fit_chem_net      0.668               0.635                  0.057                     0.094
increment         0.042               0.032                  0.045                     0.029

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.613               0.606                  0.053                     0.108
net_pair       0.539               0.537                  0.102                     0.092
```
