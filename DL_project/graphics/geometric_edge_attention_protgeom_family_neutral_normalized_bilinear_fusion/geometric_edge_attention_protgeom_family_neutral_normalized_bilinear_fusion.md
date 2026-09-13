# geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5463      0.5639      0.4829      0.5429      0.6030      0.6065
groups_GLTP            5      0.5440      0.4640      0.4897      0.5179      0.6231      0.7385
groups_IP_trans        5      0.3913      0.7149      0.5289      0.5253      0.8000      0.6170
groups_LBP_BPI_CETP    5      0.5565      0.6979      0.5356      0.5534      0.6333      0.7574
groups_ML              5      0.2000      0.7400      0.4589      0.5720      0.7200      0.6200
groups_OSBP            5      0.6000      0.5000      0.4758      0.5481      0.7333      0.9667
groups_START           5      0.6738      0.3820      0.5201      0.5188      0.6781      0.5416
groups_lipocalin       5      0.7556      0.5639      0.5627      0.5150      0.6722      0.7528
groups_scp2            5      0.4824      0.5941      0.5437      0.5071      0.5647      0.7118
ALL                   45      0.5278      0.5801      0.5109      0.5334      0.6698      0.7014

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6264      0.6042     0.0877  45
max valid BA                0.6856      0.6667     0.0957  45
best valid F1               0.6483      0.6400     0.1023  45
test BA                     0.5539      0.5515     0.1068  45
test AUC                    0.5545      0.5583     0.1392  45
test AUC in-protein         0.5519      0.5550     0.1392  42
  (proteins averaged)       2.6000      3.0000     1.3718  45
test AUC in-protein (pairs)      0.5497      0.5402     0.1435  45
  (proteins contributing)      3.0222      3.0000     1.7900  45
test F1                     0.4459      0.4841     0.1836  45
test sensitivity            0.5278      0.5652     0.2828  45
test specificity            0.5801      0.5745     0.2297  45
test precision              0.4479      0.4472     0.1622  44
test loss                   9.5822      0.7853    41.7251  45
FPR (FP/(FP+TN))            0.4199      0.4255     0.2297  45
FNR (FN/(FN+TP))            0.4722      0.4348     0.2828  45

=== abs(sensitivity-specificity) gap: mean=0.3765 median=0.3235 n=45 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5526      0.5504     0.0320  5
  max valid BA                0.6047      0.5958     0.0230  5
  best valid F1               0.6921      0.6952     0.0113  5
  test BA                     0.5551      0.5588     0.0330  5
  test AUC                    0.5820      0.5907     0.0535  5
  test AUC in-protein         0.5267      0.5051     0.0878  5
    (proteins averaged)       4.0000      4.0000     0.0000  5
  test AUC in-protein (pairs)      0.6183      0.6451     0.0768  5
    (proteins contributing)      4.4000      4.0000     0.5477  5
  test F1                     0.5212      0.5667     0.1851  5
  test sensitivity            0.5463      0.5522     0.3020  5
  test specificity            0.5639      0.5410     0.3068  5
  test precision              0.6393      0.5821     0.1456  5
  test loss                   7.5148      0.7214    15.1841  5
  FPR (FP/(FP+TN))            0.4361      0.4590     0.3068  5
  FNR (FN/(FN+TP))            0.4537      0.4478     0.3020  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6038      0.5962     0.0554  5
  max valid BA                0.6808      0.6923     0.0443  5
  best valid F1               0.7032      0.7042     0.0373  5
  test BA                     0.5040      0.4600     0.1178  5
  test AUC                    0.5139      0.5056     0.1409  5
  test AUC in-protein         0.5160      0.5000     0.1064  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4752      0.5331     0.1194  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5104      0.4706     0.1524  5
  test sensitivity            0.5440      0.5200     0.2202  5
  test specificity            0.4640      0.4400     0.2360  5
  test precision              0.5041      0.4615     0.1320  5
  test loss                   0.9961      0.7340     0.5791  5
  FPR (FP/(FP+TN))            0.5360      0.5600     0.2360  5
  FNR (FN/(FN+TP))            0.4560      0.4800     0.2202  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6494      0.6410     0.0657  5
  max valid BA                0.7085      0.7052     0.0576  5
  best valid F1               0.6310      0.6182     0.0563  5
  test BA                     0.5531      0.5458     0.0395  5
  test AUC                    0.5765      0.5782     0.0669  5
  test AUC in-protein         0.6501      0.6585     0.0444  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5536      0.5431     0.0559  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.3694      0.3846     0.1375  5
  test sensitivity            0.3913      0.4348     0.2016  5
  test specificity            0.7149      0.6596     0.1589  5
  test precision              0.4198      0.4118     0.0583  5
  test loss                   0.7021      0.6721     0.0755  5
  FPR (FP/(FP+TN))            0.2851      0.3404     0.1589  5
  FNR (FN/(FN+TP))            0.6087      0.5652     0.2016  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6260      0.6201     0.0397  5
  max valid BA                0.6954      0.7159     0.0387  5
  best valid F1               0.6046      0.6316     0.0469  5
  test BA                     0.6272      0.6309     0.0806  5
  test AUC                    0.6641      0.6984     0.1018  5
  test AUC in-protein         0.6638      0.6806     0.1149  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.6610      0.6809     0.1102  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4938      0.4923     0.1173  5
  test sensitivity            0.5565      0.5652     0.2616  5
  test specificity            0.6979      0.7447     0.1952  5
  test precision              0.5160      0.5122     0.1604  5
  test loss                  61.5410      0.7464   122.0384  5
  FPR (FP/(FP+TN))            0.3021      0.2553     0.1952  5
  FNR (FN/(FN+TP))            0.4435      0.4348     0.2616  5

groups_ML (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6200      0.6000     0.0570  5
  max valid BA                0.6700      0.6500     0.0758  5
  best valid F1               0.6000      0.5556     0.0609  5
  test BA                     0.4700      0.4500     0.1037  5
  test AUC                    0.4440      0.4600     0.0410  5
  test AUC in-protein         0.4440      0.4600     0.0410  5
    (proteins averaged)       1.0000      1.0000     0.0000  5
  test AUC in-protein (pairs)      0.4440      0.4600     0.0410  5
    (proteins contributing)      1.0000      1.0000     0.0000  5
  test F1                     0.2268      0.2222     0.1615  5
  test sensitivity            0.2000      0.2000     0.1414  5
  test specificity            0.7400      0.8000     0.1517  5
  test precision              0.2833      0.2500     0.2173  5
  test loss                   8.3427      5.0147    11.3960  5
  FPR (FP/(FP+TN))            0.2600      0.2000     0.1517  5
  FNR (FN/(FN+TP))            0.8000      0.8000     0.1414  5

groups_OSBP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7667      0.7500     0.1603  5
  max valid BA                0.8500      0.8333     0.1491  5
  best valid F1               0.8024      0.8000     0.2016  5
  test BA                     0.5500      0.5000     0.2173  5
  test AUC                    0.4667      0.5000     0.3230  5
  test AUC in-protein         0.1806      0.1806     0.0982  2
    (proteins averaged)       0.4000      0.0000     0.5477  5
  test AUC in-protein (pairs)      0.4933      0.5000     0.3332  5
    (proteins contributing)      1.6000      2.0000     0.5477  5
  test F1                     0.3700      0.5000     0.3493  5
  test sensitivity            0.6000      1.0000     0.5477  5
  test specificity            0.5000      0.5000     0.3727  5
  test precision              0.3405      0.3810     0.2524  4
  test loss                   1.8684      0.7949     2.0569  5
  FPR (FP/(FP+TN))            0.5000      0.5000     0.3727  5
  FNR (FN/(FN+TP))            0.4000      0.0000     0.5477  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5724      0.5614     0.0337  5
  max valid BA                0.6098      0.6012     0.0352  5
  best valid F1               0.6160      0.6263     0.0191  5
  test BA                     0.5279      0.4889     0.0794  5
  test AUC                    0.5297      0.5343     0.0813  5
  test AUC in-protein         0.5015      0.5152     0.0775  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5155      0.5295     0.0923  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.5353      0.5326     0.0682  5
  test sensitivity            0.6738      0.6923     0.0932  5
  test specificity            0.3820      0.3933     0.1231  5
  test precision              0.4460      0.4130     0.0635  5
  test loss                   1.4965      1.7059     0.7109  5
  FPR (FP/(FP+TN))            0.6180      0.6067     0.1231  5
  FNR (FN/(FN+TP))            0.3262      0.3077     0.0932  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6583      0.6389     0.0543  5
  max valid BA                0.7125      0.7431     0.0765  5
  best valid F1               0.6253      0.6582     0.0814  5
  test BA                     0.6597      0.6528     0.0361  5
  test AUC                    0.6549      0.6489     0.0446  5
  test AUC in-protein         0.7008      0.6948     0.0501  5
    (proteins averaged)       5.0000      5.0000     0.0000  5
  test AUC in-protein (pairs)      0.5586      0.5314     0.0495  5
    (proteins contributing)      7.2000      7.0000     0.4472  5
  test F1                     0.5740      0.5743     0.0401  5
  test sensitivity            0.7556      0.8056     0.0950  5
  test specificity            0.5639      0.5972     0.0732  5
  test precision              0.4654      0.4528     0.0309  5
  test loss                   1.4861      0.8343     1.6325  5
  FPR (FP/(FP+TN))            0.4361      0.4028     0.0732  5
  FNR (FN/(FN+TP))            0.2444      0.1944     0.0950  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5882      0.5882     0.0465  5
  max valid BA                0.6382      0.6176     0.0671  5
  best valid F1               0.5599      0.5333     0.0599  5
  test BA                     0.5382      0.5294     0.0556  5
  test AUC                    0.5592      0.5571     0.0650  5
  test AUC in-protein         0.5611      0.5486     0.0845  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.6275      0.6318     0.1097  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.4120      0.3846     0.0676  5
  test sensitivity            0.4824      0.4706     0.1832  5
  test specificity            0.5941      0.5000     0.1944  5
  test precision              0.3956      0.3750     0.0966  5
  test loss                   2.2921      0.7004     3.4897  5
  FPR (FP/(FP+TN))            0.4059      0.5000     0.1944  5
  FNR (FN/(FN+TP))            0.5176      0.5294     0.1832  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                         
CRAL-TRIO                0.630         0.484    0.517       4.0              0.369         0.444     5.0               0.458          0.472              0.432         0.518
GLTP                     0.605         0.521    0.547       2.0              0.512         0.520     3.0               0.523          0.513              0.526         0.494
IP_trans                 0.722         0.680    0.676       3.0              0.677         0.695     2.4               0.590          0.545              0.669         0.604
LBP_BPI_CETP             0.719         0.798    0.660       2.0              0.798         0.667     1.6               0.784          0.707              0.821         0.673
START                    0.576         0.508    0.470       3.0              0.474         0.479     4.0               0.536          0.589              0.524         0.560
lipocalin                0.565         0.331    0.578       5.0              0.246         0.571     2.2               0.646          0.639              0.622         0.515
scp2                     0.651         0.489    0.493       2.8              0.593         0.524     2.6               0.642          0.582              0.577         0.587

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.545               0.503                  0.065                     0.151
net_AUC           0.563               0.549                  0.087                     0.080

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.524               0.493                  0.065                     0.186
net_AUC_prot           0.557               0.516                  0.084                     0.094

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.597               0.581                  0.085                     0.106
net_AUC_lipid           0.578               0.571                  0.107                     0.079

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.596               0.561                  0.058                     0.125
net_AUC_pair           0.564               0.570                  0.085                     0.062

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.525      0.524     0.535
10     0.545  0.515      0.524     0.491
49     0.545  0.531      0.524     0.550
51     0.545  0.545      0.524     0.535
120    0.545  0.563      0.524     0.557

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.618         0.649      0.031          0.653              0.677           0.023
10        0.618         0.656      0.038          0.653              0.698           0.045
49        0.618         0.652      0.034          0.653              0.685           0.031
51        0.618         0.653      0.035          0.653              0.686           0.033
120       0.618         0.654      0.036          0.653              0.683           0.030

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.484  0.517      0.369     0.444     0.539         0.605      0.066          0.613              0.653           0.040
GLTP          0.521  0.547      0.512     0.520     0.543         0.586      0.042          0.565              0.603           0.038
IP_trans      0.680  0.676      0.677     0.695     0.680         0.722      0.041          0.693              0.735           0.042
LBP_BPI_CETP  0.798  0.660      0.798     0.667     0.798         0.799      0.001          0.801              0.808           0.006
START         0.508  0.470      0.474     0.479     0.536         0.573      0.037          0.606              0.622           0.016
lipocalin     0.331  0.578      0.246     0.571     0.669         0.730      0.062          0.673              0.742           0.068
scp2          0.489  0.493      0.593     0.524     0.562         0.566      0.005          0.622              0.620          -0.002

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.545               0.503                  0.065                     0.151
net               0.563               0.549                  0.087                     0.080
fit_chem          0.618               0.590                  0.052                     0.101
fit_chem_net      0.654               0.617                  0.051                     0.094
increment         0.036               0.025                  0.033                     0.025

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.524               0.493                  0.065                     0.186
net_prot               0.557               0.516                  0.084                     0.094
fit_chem_prot          0.653               0.662                  0.055                     0.078
fit_chem_net_prot      0.683               0.672                  0.055                     0.078
increment_prot         0.030               0.017                  0.028                     0.024
```
