# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protunion14_prothid32_pocketchem4

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protunion14_prothid32_pocketchem4'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6301      0.5073      0.9545      0.9038      0.6129      0.5907
groups_choline            5      0.3622      0.7964      0.8637      0.7496      0.4607      0.7702
groups_phosphorus_free    5      0.0839      0.9474      0.7103      0.8398      0.2867      0.8536
groups_sphingolipids      5      0.2727      0.6255      0.6972      0.7405      0.4970      0.6481
ALL                      20      0.3372      0.7191      0.8064      0.8084      0.4643      0.7157

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5561      0.5506     0.0559  20
max valid BA                0.5900      0.5809     0.0521  20
best valid F1               0.5057      0.5427     0.1047  20
test BA                     0.5282      0.5252     0.0715  20
test AUC                    0.5628      0.5904     0.1176  20
test AUC in-protein         0.5536      0.5537     0.1312  20
  (proteins averaged)       7.9000      8.5000     3.5968  20
test AUC in-protein (pairs)      0.5627      0.5666     0.1334  20
  (proteins contributing)     11.7000     14.0000     5.3024  20
test F1                     0.3324      0.3793     0.1891  20
test sensitivity            0.3372      0.3378     0.2342  20
test specificity            0.7191      0.7818     0.2236  20
test precision              0.4429      0.4371     0.1552  18
test loss                   1.0788      1.0665     0.2996  20
FPR (FP/(FP+TN))            0.2809      0.2182     0.2236  20
FNR (FN/(FN+TP))            0.6628      0.6622     0.2342  20

=== abs(sensitivity-specificity) gap: mean=0.4718 median=0.5214 n=20 ===
sensitivity std across seeds (by group): mean=0.1160 median=0.1321 n=4
specificity std across seeds (by group): mean=0.1354 median=0.1334 n=4

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5845      0.5821     0.0228  5
  max valid BA                0.6018      0.6115     0.0193  5
  best valid F1               0.5492      0.5524     0.0129  5
  test BA                     0.5687      0.5672     0.0241  5
  test AUC                    0.5922      0.6000     0.0161  5
  test AUC in-protein         0.5656      0.5707     0.0277  5
    (proteins averaged)      12.2000     12.0000     0.4472  5
  test AUC in-protein (pairs)      0.5868      0.5930     0.0328  5
    (proteins contributing)     16.4000     17.0000     1.5166  5
  test F1                     0.5189      0.5130     0.0174  5
  test sensitivity            0.6301      0.6344     0.0223  5
  test specificity            0.5073      0.5298     0.0541  5
  test precision              0.4417      0.4435     0.0236  5
  test loss                   1.3176      1.2628     0.1237  5
  FPR (FP/(FP+TN))            0.4927      0.4702     0.0541  5
  FNR (FN/(FN+TP))            0.3699      0.3656     0.0223  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5833      0.5714     0.0619  5
  max valid BA                0.6155      0.5967     0.0485  5
  best valid F1               0.5561      0.5475     0.0473  5
  test BA                     0.5793      0.5858     0.0775  5
  test AUC                    0.5927      0.6492     0.1091  5
  test AUC in-protein         0.5818      0.5725     0.0701  5
    (proteins averaged)       9.8000     10.0000     0.4472  5
  test AUC in-protein (pairs)      0.5507      0.5560     0.0826  5
    (proteins contributing)     14.8000     15.0000     0.4472  5
  test F1                     0.4172      0.4497     0.1522  5
  test sensitivity            0.3622      0.3423     0.1774  5
  test specificity            0.7964      0.8802     0.2209  5
  test precision              0.5869      0.5781     0.1462  5
  test loss                   0.9889      1.0387     0.1872  5
  FPR (FP/(FP+TN))            0.2036      0.1198     0.2209  5
  FNR (FN/(FN+TP))            0.6378      0.6577     0.1774  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5358      0.5000     0.0632  5
  max valid BA                0.5701      0.5565     0.0729  5
  best valid F1               0.4041      0.3846     0.1714  5
  test BA                     0.5156      0.5000     0.0391  5
  test AUC                    0.6620      0.6539     0.0660  5
  test AUC in-protein         0.6600      0.6583     0.1366  5
    (proteins averaged)       6.6000      7.0000     1.1402  5
  test AUC in-protein (pairs)      0.6972      0.7009     0.1184  5
    (proteins contributing)     12.2000     13.0000     2.1679  5
  test F1                     0.1191      0.0541     0.1584  5
  test sensitivity            0.0839      0.0323     0.1220  5
  test specificity            0.9474      0.9649     0.0608  5
  test precision              0.4320      0.5294     0.2325  3
  test loss                   0.8620      0.8922     0.2142  5
  FPR (FP/(FP+TN))            0.0526      0.0351     0.0608  5
  FNR (FN/(FN+TP))            0.9161      0.9677     0.1220  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5207      0.5160     0.0497  5
  max valid BA                0.5726      0.5589     0.0545  5
  best valid F1               0.5136      0.5122     0.0420  5
  test BA                     0.4491      0.4758     0.0533  5
  test AUC                    0.4043      0.3879     0.0570  5
  test AUC in-protein         0.4068      0.3328     0.1233  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4161      0.3813     0.1105  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.2742      0.2642     0.0877  5
  test sensitivity            0.2727      0.2121     0.1421  5
  test specificity            0.6255      0.7273     0.2059  5
  test precision              0.3065      0.3500     0.0643  5
  test loss                   1.1468      1.0097     0.4291  5
  FPR (FP/(FP+TN))            0.3745      0.2727     0.2059  5
  FNR (FN/(FN+TP))            0.7273      0.7879     0.1421  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.586    0.572      12.0              0.567         0.512     6.8               0.518          0.591              0.522         0.553
choline                     0.687         0.673    0.473      10.2              0.672         0.524     2.0               0.522          0.530              0.662         0.471
phosphorus_free             0.396         0.286    0.523       6.4              0.297         0.488     2.4               0.533          0.731              0.524         0.571
sphingolipids               0.599         0.528    0.432       2.4              0.491         0.447     3.2               0.511          0.570              0.523         0.438

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.518               0.558                  0.041                     0.166
net_AUC           0.500               0.522                  0.093                     0.061

=== the same rows ranked INSIDE each protein ===
155 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.508               0.535                  0.043                     0.159
net_AUC_prot           0.493               0.506                  0.120                     0.034

=== the same rows ranked INSIDE each lipid class ===
72 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.521               0.541                  0.099                     0.009
net_AUC_lipid           0.606               0.613                  0.113                     0.087

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.559               0.551                  0.055                     0.070
net_AUC_pair           0.508               0.522                  0.067                     0.064

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.517  0.464      0.503     0.458
10     0.517  0.517      0.503     0.507
49     0.517  0.512      0.503     0.492
51     0.517  0.517      0.503     0.486
120    0.517  0.500      0.503     0.493

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.650      0.022          0.707              0.726           0.018
10        0.628         0.660      0.032          0.707              0.723           0.015
49        0.628         0.670      0.042          0.707              0.738           0.031
51        0.628         0.671      0.043          0.707              0.737           0.030
120       0.628         0.656      0.028          0.707              0.718           0.011

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.586  0.572      0.567     0.512     0.586         0.605      0.019          0.656              0.668           0.012
choline          0.673  0.473      0.672     0.524     0.673         0.682      0.009          0.767              0.770           0.002
phosphorus_free  0.286  0.523      0.297     0.488     0.714         0.729      0.016          0.771              0.774           0.003
sphingolipids    0.521  0.432      0.478     0.447     0.540         0.610      0.069          0.635              0.660           0.025

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.517               0.553                  0.040                     0.165
net               0.500               0.522                  0.093                     0.061
fit_chem          0.628               0.637                  0.035                     0.079
fit_chem_net      0.656               0.641                  0.037                     0.060
increment         0.028               0.014                  0.020                     0.027

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.503               0.526                  0.044                     0.159
net_prot               0.493               0.506                  0.120                     0.034
fit_chem_prot          0.707               0.701                  0.042                     0.072
fit_chem_net_prot      0.718               0.718                  0.037                     0.062
increment_prot         0.011               0.002                  0.023                     0.011
```
