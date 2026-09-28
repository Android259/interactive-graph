# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protunion14_prothid32_rotneg

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protunion14_prothid32_rotneg'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.5591      0.5338      0.9924      0.7362      0.6753      0.4980
groups_choline            5      0.5405      0.4575      0.9903      0.2995      0.7768      0.3488
groups_phosphorus_free    5      0.2258      0.8140      0.9906      0.6421      0.3067      0.8393
groups_sphingolipids      5      0.7212      0.2400      0.9838      0.4254      0.5455      0.5259
ALL                      20      0.5117      0.5113      0.9893      0.5258      0.5760      0.5530

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5365      0.5375     0.0319  20
max valid BA                0.5645      0.5660     0.0364  20
best valid F1               0.5438      0.5510     0.0377  20
test BA                     0.5115      0.5000     0.0356  20
test AUC                    0.4695      0.4537     0.0947  20
test AUC in-protein         0.4491      0.4426     0.1150  20
  (proteins averaged)       7.9000      8.5000     3.5968  20
test AUC in-protein (pairs)      0.4574      0.4810     0.1319  20
  (proteins contributing)     11.7000     14.0000     5.3024  20
test F1                     0.3901      0.4452     0.1671  20
test sensitivity            0.5117      0.4809     0.3430  20
test specificity            0.5113      0.5517     0.3389  20
test precision              0.3812      0.3983     0.0604  20
test loss                   1.2726      1.2693     0.3306  20
FPR (FP/(FP+TN))            0.4887      0.4483     0.3389  20
FNR (FN/(FN+TP))            0.4883      0.5191     0.3430  20

=== abs(sensitivity-specificity) gap: mean=0.5833 median=0.5673 n=20 ===
sensitivity std across seeds (by group): mean=0.2769 median=0.2786 n=4
specificity std across seeds (by group): mean=0.2406 median=0.2331 n=4

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5670      0.5689     0.0203  5
  max valid BA                0.5866      0.5891     0.0175  5
  best valid F1               0.5592      0.5576     0.0062  5
  test BA                     0.5465      0.5544     0.0241  5
  test AUC                    0.5621      0.5735     0.0238  5
  test AUC in-protein         0.5342      0.5402     0.0365  5
    (proteins averaged)      12.2000     12.0000     0.4472  5
  test AUC in-protein (pairs)      0.5565      0.5479     0.0361  5
    (proteins contributing)     16.4000     17.0000     1.5166  5
  test F1                     0.4726      0.4979     0.0816  5
  test sensitivity            0.5591      0.6452     0.1659  5
  test specificity            0.5338      0.4636     0.1335  5
  test precision              0.4234      0.4255     0.0172  5
  test loss                   1.3980      1.2781     0.2809  5
  FPR (FP/(FP+TN))            0.4662      0.5364     0.1335  5
  FNR (FN/(FN+TP))            0.4409      0.3548     0.1659  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5164      0.5060     0.0213  5
  max valid BA                0.5628      0.5402     0.0535  5
  best valid F1               0.5736      0.5723     0.0027  5
  test BA                     0.4990      0.4971     0.0041  5
  test AUC                    0.4780      0.4448     0.1195  5
  test AUC in-protein         0.5023      0.4722     0.1122  5
    (proteins averaged)       9.8000     10.0000     0.4472  5
  test AUC in-protein (pairs)      0.5210      0.4834     0.1052  5
    (proteins contributing)     14.8000     15.0000     0.4472  5
  test F1                     0.3603      0.5321     0.2588  5
  test sensitivity            0.5405      0.7838     0.4565  5
  test specificity            0.4575      0.2275     0.4521  5
  test precision              0.3668      0.3974     0.0657  5
  test loss                   1.1781      1.0593     0.2097  5
  FPR (FP/(FP+TN))            0.5425      0.7725     0.4521  5
  FNR (FN/(FN+TP))            0.4595      0.2162     0.4565  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5437      0.5518     0.0308  5
  max valid BA                0.5730      0.5863     0.0242  5
  best valid F1               0.4925      0.5172     0.0443  5
  test BA                     0.5199      0.5192     0.0377  5
  test AUC                    0.4007      0.3978     0.0598  5
  test AUC in-protein         0.3341      0.3841     0.0896  5
    (proteins averaged)       6.6000      7.0000     1.1402  5
  test AUC in-protein (pairs)      0.3199      0.3458     0.1212  5
    (proteins contributing)     12.2000     13.0000     2.1679  5
  test F1                     0.2816      0.2400     0.0923  5
  test sensitivity            0.2258      0.1935     0.0940  5
  test specificity            0.8140      0.7895     0.0440  5
  test precision              0.3894      0.4167     0.0746  5
  test loss                   1.5016      1.5700     0.2874  5
  FPR (FP/(FP+TN))            0.1860      0.2105     0.0440  5
  FNR (FN/(FN+TP))            0.7742      0.8065     0.0940  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5189      0.5000     0.0301  5
  max valid BA                0.5357      0.5421     0.0282  5
  best valid F1               0.5500      0.5500     0.0000  5
  test BA                     0.4806      0.5000     0.0316  5
  test AUC                    0.4374      0.4259     0.0782  5
  test AUC in-protein         0.4260      0.4263     0.1052  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4321      0.4185     0.1175  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.4461      0.5455     0.1492  5
  test sensitivity            0.7212      1.0000     0.3912  5
  test specificity            0.2400      0.0000     0.3326  5
  test precision              0.3450      0.3750     0.0542  5
  test loss                   1.0127      0.8162     0.3643  5
  FPR (FP/(FP+TN))            0.7600      1.0000     0.3326  5
  FNR (FN/(FN+TP))            0.2788      0.0000     0.3912  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.586    0.555      12.0              0.567         0.482     6.8               0.518          0.570              0.522         0.544
choline                     0.687         0.673    0.450      10.2              0.672         0.460     2.0               0.522          0.563              0.662         0.460
phosphorus_free             0.396         0.286    0.484       6.4              0.297         0.463     2.4               0.533          0.682              0.524         0.491
sphingolipids               0.599         0.528    0.422       2.4              0.491         0.328     3.2               0.511          0.568              0.523         0.343

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.518               0.558                  0.041                     0.166
net_AUC           0.478               0.502                  0.074                     0.057

=== the same rows ranked INSIDE each protein ===
155 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.508               0.535                  0.043                     0.159
net_AUC_prot           0.433               0.446                  0.086                     0.071

=== the same rows ranked INSIDE each lipid class ===
72 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.521               0.541                  0.099                     0.009
net_AUC_lipid           0.596               0.578                  0.084                     0.058

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.559               0.551                  0.055                     0.070
net_AUC_pair           0.459               0.471                  0.058                     0.085

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.517  0.491      0.503     0.489
10     0.517  0.459      0.503     0.431
49     0.517  0.439      0.503     0.383
51     0.517  0.443      0.503     0.371
120    0.517  0.478      0.503     0.433

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.642      0.014          0.707              0.719           0.012
10        0.628         0.659      0.031          0.707              0.731           0.024
49        0.628         0.669      0.041          0.707              0.740           0.033
51        0.628         0.665      0.037          0.707              0.743           0.035
120       0.628         0.655      0.027          0.707              0.741           0.034

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.586  0.555      0.567     0.482     0.586         0.599      0.014          0.656              0.664           0.009
choline          0.673  0.450      0.672     0.460     0.673         0.672     -0.001          0.767              0.767          -0.000
phosphorus_free  0.286  0.484      0.297     0.463     0.714         0.728      0.015          0.771              0.784           0.013
sphingolipids    0.521  0.422      0.478     0.328     0.540         0.619      0.079          0.635              0.748           0.113

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.517               0.553                  0.040                     0.165
net               0.478               0.502                  0.074                     0.057
fit_chem          0.628               0.637                  0.035                     0.079
fit_chem_net      0.655               0.656                  0.038                     0.058
increment         0.027               0.014                  0.019                     0.035

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.503               0.526                  0.044                     0.159
net_prot               0.433               0.446                  0.086                     0.071
fit_chem_prot          0.707               0.701                  0.042                     0.072
fit_chem_net_prot      0.741               0.752                  0.036                     0.053
increment_prot         0.034               0.001                  0.034                     0.053
```
