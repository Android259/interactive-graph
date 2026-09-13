# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_balanced_lipid_classes_advprot_protgeom8

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_balanced_lipid_classes_advprot_protgeom8'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.9032      0.0885      0.6326      0.5510      0.9505      0.1099
groups_choline            5      0.7027      0.4406      0.5168      0.5651      0.7232      0.4871
groups_phosphorus_free    5      0.2774      0.6531      0.6869      0.4298      0.4333      0.6694
groups_sphingolipids      5      0.3758      0.5415      0.6268      0.5138      0.4424      0.7100
ALL                      20      0.5648      0.4309      0.6158      0.5149      0.6374      0.4941

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5469      0.5301     0.0448  20
max valid BA                0.5657      0.5555     0.0496  20
best valid F1               0.5457      0.5355     0.0665  20
test BA                     0.4978      0.4939     0.0559  20
test AUC                    0.5023      0.4712     0.0751  20
test AUC in-protein         0.5762      0.5733     0.1370  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5066      0.5000     0.1173  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.3865      0.4659     0.1834  20
test sensitivity            0.5648      0.6343     0.3527  20
test specificity            0.4309      0.4330     0.3403  20
test precision              0.3523      0.3547     0.0768  19
test loss                   0.7076      0.6990     0.0310  20
FPR (FP/(FP+TN))            0.5691      0.5670     0.3403  20
FNR (FN/(FN+TP))            0.4352      0.3657     0.3527  20

=== abs(sensitivity-specificity) gap: mean=0.5933 median=0.7345 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5214      0.5110     0.0289  5
  max valid BA                0.5302      0.5197     0.0242  5
  best valid F1               0.5162      0.5140     0.0076  5
  test BA                     0.4959      0.4950     0.0180  5
  test AUC                    0.4912      0.4761     0.0453  5
  test AUC in-protein         0.4925      0.4722     0.0793  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.4594      0.4642     0.0585  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.4861      0.4958     0.0338  5
  test sensitivity            0.9032      0.9570     0.1392  5
  test specificity            0.0885      0.0437     0.1070  5
  test precision              0.3339      0.3346     0.0107  5
  test loss                   0.7507      0.7641     0.0310  5
  FPR (FP/(FP+TN))            0.9115      0.9563     0.1070  5
  FNR (FN/(FN+TP))            0.0968      0.0430     0.1392  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5896      0.5970     0.0569  5
  max valid BA                0.6052      0.6159     0.0553  5
  best valid F1               0.5533      0.5373     0.0294  5
  test BA                     0.5716      0.5687     0.0467  5
  test AUC                    0.6010      0.5919     0.0622  5
  test AUC in-protein         0.6549      0.6366     0.0639  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.6028      0.6354     0.0693  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.5116      0.5160     0.0498  5
  test sensitivity            0.7027      0.6667     0.1985  5
  test specificity            0.4406      0.5248     0.2421  5
  test precision              0.4174      0.4273     0.0382  5
  test loss                   0.6858      0.6880     0.0079  5
  FPR (FP/(FP+TN))            0.5594      0.4752     0.2421  5
  FNR (FN/(FN+TP))            0.2973      0.3333     0.1985  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5271      0.5296     0.0155  5
  max valid BA                0.5514      0.5452     0.0318  5
  best valid F1               0.5059      0.5505     0.0974  5
  test BA                     0.4652      0.4753     0.0249  5
  test AUC                    0.4739      0.4625     0.0435  5
  test AUC in-protein         0.6567      0.6000     0.2133  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.5721      0.5455     0.1118  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.2153      0.1053     0.2107  5
  test sensitivity            0.2774      0.0645     0.3752  5
  test specificity            0.6531      0.8980     0.3766  5
  test precision              0.2673      0.2857     0.0848  5
  test loss                   0.6923      0.6890     0.0125  5
  FPR (FP/(FP+TN))            0.3469      0.1020     0.3766  5
  FNR (FN/(FN+TP))            0.7226      0.9355     0.3752  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5494      0.5515     0.0402  5
  max valid BA                0.5762      0.5568     0.0558  5
  best valid F1               0.6073      0.6226     0.0519  5
  test BA                     0.4586      0.4593     0.0405  5
  test AUC                    0.4432      0.4619     0.0352  5
  test AUC in-protein         0.5009      0.5042     0.0402  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3923      0.4164     0.0926  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3331      0.3607     0.1991  5
  test sensitivity            0.3758      0.3333     0.2766  5
  test specificity            0.5415      0.5854     0.3386  5
  test precision              0.4003      0.4013     0.0299  4
  test loss                   0.7016      0.6999     0.0115  5
  FPR (FP/(FP+TN))            0.4585      0.4146     0.3386  5
  FNR (FN/(FN+TP))            0.6242      0.6667     0.2766  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.495      11.6              0.530         0.482     5.4               0.501          0.453              0.501         0.514
choline                     0.687         0.646    0.596       9.4              0.696         0.627     1.8               0.565          0.552              0.622         0.576
phosphorus_free             0.396         0.499    0.512       1.2              0.739         0.605     5.4               0.514          0.506              0.484         0.514
sphingolipids               0.599         0.543    0.485       1.6              0.496         0.483     3.2               0.537          0.447              0.490         0.415

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.522               0.511                  0.046                     0.051

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.543               0.506                  0.138                     0.078

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.489               0.485                  0.062                     0.049

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.505               0.519                  0.049                     0.067

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.542  0.510      0.602     0.515
10     0.542  0.495      0.602     0.464
49     0.542  0.529      0.602     0.567
51     0.542  0.530      0.602     0.551
120    0.542  0.522      0.602     0.543

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.557         0.582      0.025          0.881              0.884           0.003
10        0.557         0.571      0.014          0.881              0.885           0.004
49        0.557         0.569      0.012          0.881              0.885           0.004
51        0.557         0.578      0.021          0.881              0.887           0.005
120       0.557         0.570      0.013          0.881              0.886           0.005

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.495  0.495      0.530     0.482     0.512         0.517      0.005          0.889              0.889           0.001
choline          0.646  0.596      0.696     0.627     0.646         0.657      0.010          0.867              0.869           0.002
phosphorus_free  0.499  0.512      0.739     0.605     0.536         0.524     -0.011          0.967              0.968           0.001
sphingolipids    0.526  0.485      0.496     0.483     0.535         0.582      0.047          0.802              0.817           0.015

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.542               0.514                  0.038                     0.071
net               0.522               0.511                  0.046                     0.051
fit_chem          0.557               0.533                  0.028                     0.060
fit_chem_net      0.570               0.530                  0.034                     0.065
increment         0.013               0.007                  0.025                     0.025

=== the same rows ranked INSIDE each protein, epoch 120 ===
121 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.602               0.553                  0.039                     0.120
net_prot               0.543               0.506                  0.138                     0.078
fit_chem_prot          0.881               0.871                  0.022                     0.068
fit_chem_net_prot      0.886               0.873                  0.019                     0.063
increment_prot         0.005               0.001                  0.011                     0.007
```
