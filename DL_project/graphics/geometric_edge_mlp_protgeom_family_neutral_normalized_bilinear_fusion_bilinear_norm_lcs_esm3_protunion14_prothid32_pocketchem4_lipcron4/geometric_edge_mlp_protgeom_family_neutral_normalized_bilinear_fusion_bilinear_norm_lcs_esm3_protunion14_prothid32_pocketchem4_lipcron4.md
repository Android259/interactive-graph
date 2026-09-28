# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protunion14_prothid32_pocketchem4_lipcron4

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protunion14_prothid32_pocketchem4_lipcron4'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.5441      0.6013      0.8344      0.8138      0.5849      0.6066
groups_choline            5      0.4703      0.7222      0.9324      0.7856      0.5268      0.7798
groups_phosphorus_free    5      0.3355      0.7789      0.9092      0.7834      0.4733      0.7964
groups_sphingolipids      5      0.3333      0.5927      0.7225      0.7107      0.4606      0.7185
ALL                      20      0.4208      0.6738      0.8496      0.7734      0.5114      0.7253

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5959      0.5881     0.0593  20
max valid BA                0.6184      0.6068     0.0497  20
best valid F1               0.5432      0.5536     0.0944  20
test BA                     0.5473      0.5453     0.0920  20
test AUC                    0.5850      0.5933     0.1022  20
test AUC in-protein         0.5834      0.6096     0.1100  20
  (proteins averaged)       7.9000      8.5000     3.5968  20
test AUC in-protein (pairs)      0.5737      0.5874     0.1122  20
  (proteins contributing)     11.7000     14.0000     5.3024  20
test F1                     0.4133      0.4262     0.1546  20
test sensitivity            0.4208      0.3997     0.1928  20
test specificity            0.6738      0.7007     0.1394  20
test precision              0.4302      0.4594     0.1447  20
test loss                   0.9663      0.9417     0.2724  20
FPR (FP/(FP+TN))            0.3262      0.2993     0.1394  20
FNR (FN/(FN+TP))            0.5792      0.6003     0.1928  20

=== abs(sensitivity-specificity) gap: mean=0.3029 median=0.2848 n=20 ===
sensitivity std across seeds (by group): mean=0.1602 median=0.1364 n=4
specificity std across seeds (by group): mean=0.1178 median=0.1190 n=4

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5762      0.5792     0.0196  5
  max valid BA                0.5958      0.6066     0.0239  5
  best valid F1               0.5562      0.5571     0.0237  5
  test BA                     0.5727      0.5669     0.0299  5
  test AUC                    0.5847      0.5793     0.0251  5
  test AUC in-protein         0.5649      0.5699     0.0513  5
    (proteins averaged)      12.2000     12.0000     0.4472  5
  test AUC in-protein (pairs)      0.5607      0.5594     0.0382  5
    (proteins contributing)     16.4000     17.0000     1.5166  5
  test F1                     0.4916      0.4957     0.0583  5
  test sensitivity            0.5441      0.6129     0.1227  5
  test specificity            0.6013      0.5695     0.1009  5
  test precision              0.4578      0.4667     0.0256  5
  test loss                   1.1754      1.1774     0.1039  5
  FPR (FP/(FP+TN))            0.3987      0.4305     0.1009  5
  FNR (FN/(FN+TP))            0.4559      0.3871     0.1227  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6286      0.6414     0.0270  5
  max valid BA                0.6533      0.6577     0.0371  5
  best valid F1               0.5948      0.6031     0.0388  5
  test BA                     0.5962      0.6235     0.0788  5
  test AUC                    0.6354      0.6389     0.0730  5
  test AUC in-protein         0.6381      0.6369     0.0326  5
    (proteins averaged)       9.8000     10.0000     0.4472  5
  test AUC in-protein (pairs)      0.6015      0.6141     0.0626  5
    (proteins contributing)     14.8000     15.0000     0.4472  5
  test F1                     0.4939      0.5294     0.1046  5
  test sensitivity            0.4703      0.4414     0.1501  5
  test specificity            0.7222      0.7425     0.1372  5
  test precision              0.5491      0.5568     0.1493  5
  test loss                   0.8705      0.8848     0.1408  5
  FPR (FP/(FP+TN))            0.2778      0.2575     0.1372  5
  FNR (FN/(FN+TP))            0.5297      0.5586     0.1501  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6105      0.6363     0.1032  5
  max valid BA                0.6349      0.6363     0.0737  5
  best valid F1               0.4849      0.5263     0.1719  5
  test BA                     0.5572      0.5209     0.1300  5
  test AUC                    0.6601      0.6259     0.1104  5
  test AUC in-protein         0.6641      0.6332     0.0745  5
    (proteins averaged)       6.6000      7.0000     1.1402  5
  test AUC in-protein (pairs)      0.6821      0.6279     0.0980  5
    (proteins contributing)     12.2000     13.0000     2.1679  5
  test F1                     0.3367      0.3509     0.2587  5
  test sensitivity            0.3355      0.3226     0.3074  5
  test specificity            0.7789      0.7368     0.0686  5
  test precision              0.3659      0.3846     0.1959  5
  test loss                   0.8184      0.8883     0.2238  5
  FPR (FP/(FP+TN))            0.2211      0.2632     0.0686  5
  FNR (FN/(FN+TP))            0.6645      0.6774     0.3074  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5684      0.5598     0.0434  5
  max valid BA                0.5896      0.5867     0.0286  5
  best valid F1               0.5369      0.5316     0.0539  5
  test BA                     0.4630      0.4606     0.0584  5
  test AUC                    0.4597      0.4705     0.0407  5
  test AUC in-protein         0.4663      0.4802     0.1369  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4506      0.4732     0.0996  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.3310      0.3200     0.0249  5
  test sensitivity            0.3333      0.3636     0.0606  5
  test specificity            0.5927      0.6182     0.1644  5
  test precision              0.3481      0.3226     0.0766  5
  test loss                   1.0008      0.6979     0.4206  5
  FPR (FP/(FP+TN))            0.4073      0.3818     0.1644  5
  FNR (FN/(FN+TP))            0.6667      0.6364     0.0606  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.586    0.566      12.0              0.567         0.497     6.8               0.518          0.634              0.522         0.562
choline                     0.687         0.673    0.563      10.2              0.672         0.651     2.0               0.522          0.480              0.662         0.559
phosphorus_free             0.396         0.286    0.582       6.4              0.297         0.613     2.4               0.533          0.726              0.524         0.614
sphingolipids               0.599         0.528    0.455       2.4              0.491         0.481     3.2               0.511          0.496              0.523         0.447

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.518               0.558                  0.041                     0.166
net_AUC           0.542               0.556                  0.066                     0.058

=== the same rows ranked INSIDE each protein ===
155 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.508               0.535                  0.043                     0.159
net_AUC_prot           0.561               0.588                  0.091                     0.084

=== the same rows ranked INSIDE each lipid class ===
72 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.521               0.541                  0.099                     0.009
net_AUC_lipid           0.584               0.572                  0.110                     0.117

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.559               0.551                  0.055                      0.07
net_AUC_pair           0.546               0.574                  0.094                      0.07

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.517  0.438      0.503     0.426
10     0.517  0.503      0.503     0.472
49     0.517  0.558      0.503     0.561
51     0.517  0.578      0.503     0.566
120    0.517  0.542      0.503     0.561

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.639      0.011          0.707              0.716           0.009
10        0.628         0.662      0.034          0.707              0.722           0.015
49        0.628         0.659      0.031          0.707              0.729           0.022
51        0.628         0.660      0.032          0.707              0.730           0.022
120       0.628         0.645      0.017          0.707              0.718           0.010

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.586  0.566      0.567     0.497     0.586         0.597      0.011          0.656              0.671           0.015
choline          0.673  0.563      0.672     0.651     0.673         0.681      0.009          0.767              0.770           0.003
phosphorus_free  0.286  0.582      0.297     0.613     0.714         0.727      0.013          0.771              0.779           0.008
sphingolipids    0.521  0.455      0.478     0.481     0.540         0.574      0.033          0.635              0.650           0.015

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.517               0.553                  0.040                     0.165
net               0.542               0.556                  0.066                     0.058
fit_chem          0.628               0.637                  0.035                     0.079
fit_chem_net      0.645               0.635                  0.042                     0.072
increment         0.017               0.010                  0.020                     0.011

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.503               0.526                  0.044                     0.159
net_prot               0.561               0.588                  0.091                     0.084
fit_chem_prot          0.707               0.701                  0.042                     0.072
fit_chem_net_prot      0.718               0.718                  0.043                     0.067
increment_prot         0.010               0.002                  0.019                     0.006
```
