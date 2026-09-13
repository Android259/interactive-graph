# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.7634      0.2929      0.6424      0.5217      0.7548      0.3582
groups_choline            5      0.6595      0.4762      0.4822      0.5859      0.6339      0.6059
groups_phosphorus_free    5      0.0387      0.9143      0.6171      0.5241      0.2800      0.7796
groups_sphingolipids      5      0.2000      0.7659      0.5518      0.6092      0.5636      0.6100
ALL                      20      0.4154      0.6123      0.5734      0.5602      0.5581      0.5884

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5447      0.5223     0.0523  20
max valid BA                0.5733      0.5570     0.0526  20
best valid F1               0.5320      0.5451     0.0957  20
test BA                     0.5139      0.4975     0.0541  20
test AUC                    0.5257      0.5236     0.0629  20
test AUC in-protein         0.5757      0.5651     0.1261  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5495      0.5784     0.1164  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.3220      0.3804     0.2022  20
test sensitivity            0.4154      0.3871     0.3370  20
test specificity            0.6123      0.5894     0.2883  20
test precision              0.3539      0.3517     0.0863  18
test loss                   0.6953      0.6903     0.0185  20
FPR (FP/(FP+TN))            0.3877      0.4106     0.2883  20
FNR (FN/(FN+TP))            0.5846      0.6129     0.3370  20

=== abs(sensitivity-specificity) gap: mean=0.5471 median=0.5726 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5429      0.5107     0.0695  5
  max valid BA                0.5565      0.5376     0.0672  5
  best valid F1               0.5308      0.5138     0.0400  5
  test BA                     0.5282      0.5128     0.0596  5
  test AUC                    0.5267      0.5153     0.0453  5
  test AUC in-protein         0.4724      0.4644     0.0432  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.4849      0.4783     0.0452  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.4797      0.4781     0.0614  5
  test sensitivity            0.7634      0.7742     0.1972  5
  test specificity            0.2929      0.2186     0.2305  5
  test precision              0.3586      0.3490     0.0432  5
  test loss                   0.7117      0.6954     0.0291  5
  FPR (FP/(FP+TN))            0.7071      0.7814     0.2305  5
  FNR (FN/(FN+TP))            0.2366      0.2258     0.1972  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5826      0.5978     0.0628  5
  max valid BA                0.6199      0.6140     0.0408  5
  best valid F1               0.5597      0.5448     0.0290  5
  test BA                     0.5678      0.5941     0.0488  5
  test AUC                    0.5969      0.6122     0.0358  5
  test AUC in-protein         0.6220      0.6229     0.0443  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.6041      0.6152     0.0424  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.5014      0.5211     0.0615  5
  test sensitivity            0.6595      0.6486     0.1463  5
  test specificity            0.4762      0.5396     0.1384  5
  test precision              0.4104      0.4346     0.0443  5
  test loss                   0.6902      0.6923     0.0050  5
  FPR (FP/(FP+TN))            0.5238      0.4604     0.1384  5
  FNR (FN/(FN+TP))            0.3405      0.3514     0.1463  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5127      0.5065     0.0125  5
  max valid BA                0.5298      0.5330     0.0184  5
  best valid F1               0.4384      0.5319     0.1480  5
  test BA                     0.4765      0.4710     0.0161  5
  test AUC                    0.4902      0.4885     0.0267  5
  test AUC in-protein         0.6733      0.7333     0.2006  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.6182      0.6364     0.1173  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.0628      0.0571     0.0419  5
  test sensitivity            0.0387      0.0323     0.0270  5
  test specificity            0.9143      0.8980     0.0566  5
  test precision              0.2222      0.2361     0.0393  4
  test loss                   0.6820      0.6827     0.0057  5
  FPR (FP/(FP+TN))            0.0857      0.1020     0.0566  5
  FNR (FN/(FN+TP))            0.9613      0.9677     0.0270  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5407      0.5436     0.0316  5
  max valid BA                0.5868      0.5894     0.0306  5
  best valid F1               0.5992      0.6000     0.0396  5
  test BA                     0.4829      0.4933     0.0298  5
  test AUC                    0.4890      0.4671     0.0718  5
  test AUC in-protein         0.5350      0.5275     0.0385  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4906      0.3902     0.1660  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.2441      0.2553     0.1483  5
  test sensitivity            0.2000      0.1818     0.1314  5
  test specificity            0.7659      0.7317     0.1586  5
  test precision              0.4093      0.4039     0.0545  4
  test loss                   0.6974      0.6946     0.0113  5
  FPR (FP/(FP+TN))            0.2341      0.2683     0.1586  5
  FNR (FN/(FN+TP))            0.8000      0.8182     0.1314  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.529      11.6              0.530         0.507     5.4               0.501          0.519              0.501         0.494
choline                     0.687         0.646    0.574       9.4              0.696         0.579     1.8               0.565          0.596              0.622         0.524
phosphorus_free             0.396         0.499    0.496       1.2              0.739         0.294     5.4               0.514          0.588              0.484         0.520
sphingolipids               0.599         0.543    0.493       1.6              0.496         0.473     3.2               0.537          0.477              0.490         0.457

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.523               0.514                  0.065                     0.038

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.482               0.511                  0.144                     0.121

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.545               0.520                  0.083                     0.057

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.499               0.509                  0.079                     0.031

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.542  0.510      0.602     0.457
10     0.542  0.520      0.602     0.522
49     0.542  0.500      0.602     0.513
51     0.542  0.500      0.602     0.502
120    0.542  0.523      0.602     0.482

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.557         0.584      0.027          0.881              0.889           0.008
10        0.557         0.573      0.016          0.881              0.885           0.004
49        0.557         0.580      0.023          0.881              0.887           0.005
51        0.557         0.576      0.019          0.881              0.887           0.006
120       0.557         0.582      0.025          0.881              0.887           0.006

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.495  0.529      0.530     0.507     0.512         0.545      0.033          0.889              0.888          -0.000
choline          0.646  0.574      0.696     0.579     0.646         0.655      0.009          0.867              0.868           0.002
phosphorus_free  0.499  0.496      0.739     0.294     0.536         0.555      0.019          0.967              0.971           0.004
sphingolipids    0.526  0.493      0.496     0.473     0.535         0.574      0.039          0.802              0.820           0.018

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.542               0.514                  0.038                     0.071
net               0.523               0.514                  0.065                     0.038
fit_chem          0.557               0.533                  0.028                     0.060
fit_chem_net      0.582               0.559                  0.037                     0.050
increment         0.025               0.019                  0.031                     0.014

=== the same rows ranked INSIDE each protein, epoch 120 ===
121 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.602               0.553                  0.039                     0.120
net_prot               0.482               0.511                  0.144                     0.121
fit_chem_prot          0.881               0.871                  0.022                     0.068
fit_chem_net_prot      0.887               0.871                  0.021                     0.063
increment_prot         0.006               0.001                  0.007                     0.008
```
