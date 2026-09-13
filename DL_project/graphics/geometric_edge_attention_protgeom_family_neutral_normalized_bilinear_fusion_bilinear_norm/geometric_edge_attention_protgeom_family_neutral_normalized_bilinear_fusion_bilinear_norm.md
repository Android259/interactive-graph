# geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.2716      0.8230      0.6309      0.6937      0.3045      0.8161
groups_GLTP            5      0.3360      0.5840      0.6123      0.5615      0.4462      0.6308
groups_IP_trans        5      0.4174      0.7532      0.6667      0.6251      0.5333      0.7574
groups_LBP_BPI_CETP    5      0.3217      0.8553      0.7206      0.6446      0.4083      0.8085
groups_START           5      0.3415      0.6404      0.6812      0.6239      0.3406      0.6697
groups_lipocalin       5      0.5222      0.5861      0.7486      0.5183      0.5389      0.6111
groups_scp2            5      0.4118      0.7353      0.7006      0.6303      0.4353      0.8059
ALL                   35      0.3746      0.7110      0.6801      0.6139      0.4296      0.7285

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5790      0.5824     0.0648  35
max valid BA                0.6041      0.6029     0.0656  35
best valid F1               0.5339      0.5588     0.1224  35
test BA                     0.5428      0.5338     0.0725  35
test F1                     0.3567      0.3590     0.1884  35
test sensitivity            0.3746      0.3913     0.2785  35
test specificity            0.7110      0.7541     0.2754  35
test precision              0.4811      0.4545     0.1617  33
test loss                   0.6993      0.6823     0.1092  35
FPR (FP/(FP+TN))            0.2890      0.2459     0.2754  35
FNR (FN/(FN+TP))            0.6254      0.6087     0.2785  35

=== abs(sensitivity-specificity) gap: mean=0.5179 median=0.5023 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5603      0.5835     0.0472  5
  max valid BA                0.5940      0.5991     0.0476  5
  best valid F1               0.6416      0.6923     0.0902  5
  test BA                     0.5473      0.5038     0.0682  5
  test F1                     0.3290      0.3265     0.2585  5
  test sensitivity            0.2716      0.2388     0.2394  5
  test specificity            0.8230      0.8197     0.1459  5
  test precision              0.6056      0.5811     0.1016  4
  test loss                   0.7022      0.7109     0.0293  5
  FPR (FP/(FP+TN))            0.1770      0.1803     0.1459  5
  FNR (FN/(FN+TP))            0.7284      0.7612     0.2394  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5385      0.5385     0.0304  5
  max valid BA                0.5538      0.5577     0.0316  5
  best valid F1               0.5699      0.5660     0.0975  5
  test BA                     0.4600      0.4600     0.0316  5
  test F1                     0.3059      0.2927     0.2373  5
  test sensitivity            0.3360      0.2400     0.3843  5
  test specificity            0.5840      0.6400     0.3551  5
  test precision              0.3383      0.4000     0.1949  5
  test loss                   0.7274      0.7222     0.0311  5
  FPR (FP/(FP+TN))            0.4160      0.3600     0.3551  5
  FNR (FN/(FN+TP))            0.6640      0.7600     0.3843  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6454      0.6516     0.0597  5
  max valid BA                0.6734      0.6857     0.0625  5
  best valid F1               0.5777      0.6000     0.0763  5
  test BA                     0.5853      0.5694     0.0614  5
  test F1                     0.4112      0.4528     0.1381  5
  test sensitivity            0.4174      0.5217     0.2099  5
  test specificity            0.7532      0.7234     0.1246  5
  test precision              0.4527      0.4444     0.0508  5
  test loss                   0.6654      0.6651     0.0309  5
  FPR (FP/(FP+TN))            0.2468      0.2766     0.1246  5
  FNR (FN/(FN+TP))            0.5826      0.4783     0.2099  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6084      0.5829     0.0634  5
  max valid BA                0.6258      0.6334     0.0655  5
  best valid F1               0.4522      0.5588     0.1768  5
  test BA                     0.5885      0.6133     0.0674  5
  test F1                     0.3489      0.4865     0.2161  5
  test sensitivity            0.3217      0.3913     0.2546  5
  test specificity            0.8553      0.8936     0.1630  5
  test precision              0.5393      0.5000     0.0914  5
  test loss                   0.6309      0.6258     0.0431  5
  FPR (FP/(FP+TN))            0.1447      0.1064     0.1630  5
  FNR (FN/(FN+TP))            0.6783      0.6087     0.2546  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5051      0.5000     0.0305  5
  max valid BA                0.5274      0.5066     0.0354  5
  best valid F1               0.4487      0.5409     0.1764  5
  test BA                     0.4910      0.5000     0.0662  5
  test F1                     0.2884      0.2619     0.2133  5
  test sensitivity            0.3415      0.1692     0.3927  5
  test specificity            0.6404      0.9101     0.4370  5
  test precision              0.4745      0.5005     0.1343  4
  test loss                   0.8336      0.7143     0.2411  5
  FPR (FP/(FP+TN))            0.3596      0.0899     0.4370  5
  FNR (FN/(FN+TP))            0.6585      0.8308     0.3927  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5750      0.5903     0.0532  5
  max valid BA                0.6014      0.6042     0.0457  5
  best valid F1               0.5156      0.5227     0.0397  5
  test BA                     0.5542      0.5208     0.0721  5
  test F1                     0.3979      0.4783     0.2003  5
  test sensitivity            0.5222      0.5000     0.3477  5
  test specificity            0.5861      0.5694     0.3793  5
  test precision              0.4402      0.3929     0.1196  5
  test loss                   0.6855      0.6918     0.0579  5
  FPR (FP/(FP+TN))            0.4139      0.4306     0.3793  5
  FNR (FN/(FN+TP))            0.4778      0.5000     0.3477  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6206      0.5882     0.0554  5
  max valid BA                0.6529      0.6471     0.0397  5
  best valid F1               0.5317      0.5405     0.0605  5
  test BA                     0.5735      0.5882     0.0540  5
  test F1                     0.4155      0.4571     0.0830  5
  test sensitivity            0.4118      0.4706     0.1380  5
  test specificity            0.7353      0.7059     0.1728  5
  test precision              0.5410      0.4444     0.2679  5
  test loss                   0.6502      0.6522     0.0324  5
  FPR (FP/(FP+TN))            0.2647      0.2941     0.1728  5
  FNR (FN/(FN+TP))            0.5882      0.5294     0.1380  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                         
CRAL-TRIO                0.630         0.484    0.518       4.0              0.369         0.479     5.0               0.458          0.482              0.432         0.503
GLTP                     0.605         0.521    0.497       2.0              0.512         0.486     3.0               0.523          0.500              0.526         0.516
IP_trans                 0.722         0.680    0.592       3.0              0.677         0.584     2.4               0.590          0.587              0.669         0.535
LBP_BPI_CETP             0.719         0.798    0.555       2.0              0.798         0.546     1.6               0.784          0.510              0.821         0.538
START                    0.576         0.508    0.503       3.0              0.474         0.478     4.0               0.536          0.559              0.524         0.533
lipocalin                0.565         0.331    0.428       5.0              0.246         0.304     2.2               0.646          0.547              0.622         0.601
scp2                     0.651         0.489    0.578       2.8              0.593         0.574     2.6               0.642          0.610              0.577         0.596

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.545               0.503                  0.065                     0.151
net_AUC           0.524               0.514                  0.091                     0.056

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.524               0.493                  0.065                     0.186
net_AUC_prot           0.493               0.488                  0.111                     0.095

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.597               0.581                  0.085                     0.106
net_AUC_lipid           0.542               0.560                  0.141                     0.047

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.596               0.561                  0.058                     0.125
net_AUC_pair           0.546               0.559                  0.121                     0.038

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.527      0.524     0.524
10     0.545  0.558      0.524     0.555
49     0.545  0.552      0.524     0.544
51     0.545  0.557      0.524     0.556
120    0.545  0.524      0.524     0.493

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.618         0.648      0.030          0.653              0.684           0.030
10        0.618         0.648      0.030          0.653              0.679           0.025
49        0.618         0.649      0.031          0.653              0.687           0.033
51        0.618         0.652      0.034          0.653              0.684           0.031
120       0.618         0.642      0.024          0.653              0.681           0.027

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.484  0.518      0.369     0.479     0.539         0.567      0.028          0.613              0.656           0.042
GLTP          0.521  0.497      0.512     0.486     0.543         0.580      0.037          0.565              0.585           0.020
IP_trans      0.680  0.592      0.677     0.584     0.680         0.703      0.023          0.693              0.727           0.034
LBP_BPI_CETP  0.798  0.555      0.798     0.546     0.798         0.798     -0.001          0.801              0.806           0.004
START         0.508  0.503      0.474     0.478     0.536         0.575      0.039          0.606              0.642           0.036
lipocalin     0.331  0.428      0.246     0.304     0.669         0.668     -0.001          0.673              0.678           0.005
scp2          0.489  0.578      0.593     0.574     0.562         0.606      0.044          0.622              0.671           0.049

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.545               0.503                  0.065                     0.151
net               0.524               0.514                  0.091                     0.056
fit_chem          0.618               0.590                  0.052                     0.101
fit_chem_net      0.642               0.611                  0.055                     0.085
increment         0.024               0.011                  0.028                     0.019

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.524               0.493                  0.065                     0.186
net_prot               0.493               0.488                  0.111                     0.095
fit_chem_prot          0.653               0.662                  0.055                     0.078
fit_chem_net_prot      0.681               0.668                  0.057                     0.070
increment_prot         0.027               0.010                  0.033                     0.018
```
