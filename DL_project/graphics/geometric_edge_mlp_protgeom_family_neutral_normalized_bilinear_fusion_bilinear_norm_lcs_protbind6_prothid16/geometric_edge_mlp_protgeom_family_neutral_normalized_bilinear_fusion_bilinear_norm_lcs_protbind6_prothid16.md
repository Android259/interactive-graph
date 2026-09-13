# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_protbind6_prothid16

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_protbind6_prothid16'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.5118      0.5351      0.6201      0.6333      0.5011      0.5669
groups_choline            5      0.3495      0.8431      0.6487      0.6662      0.4214      0.8214
groups_phosphorus_free    5      0.1935      0.7965      0.5382      0.6518      0.3467      0.6714
groups_sphingolipids      5      0.2364      0.7382      0.4789      0.6790      0.4485      0.6481
ALL                      20      0.3228      0.7282      0.5715      0.6576      0.4294      0.6770

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5390      0.5266     0.0468  20
max valid BA                0.5532      0.5444     0.0501  20
best valid F1               0.4728      0.5106     0.1148  20
test BA                     0.5255      0.5127     0.0565  20
test AUC                    0.5254      0.5211     0.1081  20
test AUC in-protein         0.5145      0.4970     0.1109  20
  (proteins averaged)       7.9000      8.5000     3.5968  20
test AUC in-protein (pairs)      0.5277      0.5525     0.1209  20
  (proteins contributing)     11.7000     14.0000     5.3024  20
test F1                     0.3036      0.2983     0.1981  20
test sensitivity            0.3228      0.2727     0.2812  20
test specificity            0.7282      0.7998     0.2775  20
test precision              0.4527      0.4030     0.1667  17
test loss                   0.6834      0.6802     0.0366  20
FPR (FP/(FP+TN))            0.2718      0.2002     0.2775  20
FNR (FN/(FN+TP))            0.6772      0.7273     0.2812  20

=== abs(sensitivity-specificity) gap: mean=0.6108 median=0.6014 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5199      0.5156     0.0209  5
  max valid BA                0.5340      0.5407     0.0225  5
  best valid F1               0.5213      0.5329     0.0363  5
  test BA                     0.5235      0.5254     0.0278  5
  test AUC                    0.5462      0.5221     0.0496  5
  test AUC in-protein         0.5081      0.4961     0.0876  5
    (proteins averaged)      12.2000     12.0000     0.4472  5
  test AUC in-protein (pairs)      0.5699      0.5536     0.0407  5
    (proteins contributing)     16.4000     17.0000     1.5166  5
  test F1                     0.3839      0.4758     0.2147  5
  test sensitivity            0.5118      0.5806     0.3817  5
  test specificity            0.5351      0.4702     0.3403  5
  test precision              0.3952      0.3955     0.0206  5
  test loss                   0.7129      0.6933     0.0469  5
  FPR (FP/(FP+TN))            0.4649      0.5298     0.3403  5
  FNR (FN/(FN+TP))            0.4882      0.4194     0.3817  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5964      0.5759     0.0585  5
  max valid BA                0.6214      0.5997     0.0430  5
  best valid F1               0.5303      0.5130     0.0726  5
  test BA                     0.5963      0.6190     0.0432  5
  test AUC                    0.6283      0.6430     0.0708  5
  test AUC in-protein         0.6382      0.6276     0.0733  5
    (proteins averaged)       9.8000     10.0000     0.4472  5
  test AUC in-protein (pairs)      0.6307      0.6479     0.0670  5
    (proteins contributing)     14.8000     15.0000     0.4472  5
  test F1                     0.4243      0.5056     0.1336  5
  test sensitivity            0.3495      0.4054     0.1428  5
  test specificity            0.8431      0.8204     0.0945  5
  test precision              0.6530      0.6154     0.1694  5
  test loss                   0.6486      0.6400     0.0232  5
  FPR (FP/(FP+TN))            0.1569      0.1796     0.0945  5
  FNR (FN/(FN+TP))            0.6505      0.5946     0.1428  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5067      0.5000     0.0136  5
  max valid BA                0.5090      0.5024     0.0173  5
  best valid F1               0.3314      0.2651     0.1425  5
  test BA                     0.4950      0.5000     0.0345  5
  test AUC                    0.4274      0.3704     0.1291  5
  test AUC in-protein         0.4383      0.4347     0.1275  5
    (proteins averaged)       6.6000      7.0000     1.1402  5
  test AUC in-protein (pairs)      0.4045      0.3500     0.1508  5
    (proteins contributing)     12.2000     13.0000     2.1679  5
  test F1                     0.1451      0.0000     0.2087  5
  test sensitivity            0.1935      0.0000     0.3352  5
  test specificity            0.7965      1.0000     0.3901  5
  test precision              0.3908      0.3908     0.1001  2
  test loss                   0.6830      0.6755     0.0233  5
  FPR (FP/(FP+TN))            0.2035      0.0000     0.3901  5
  FNR (FN/(FN+TP))            0.8065      1.0000     0.3352  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5330      0.5328     0.0203  5
  max valid BA                0.5483      0.5606     0.0227  5
  best valid F1               0.5083      0.5238     0.0461  5
  test BA                     0.4873      0.4879     0.0457  5
  test AUC                    0.4997      0.4948     0.0688  5
  test AUC in-protein         0.4734      0.4674     0.0243  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5057      0.5025     0.0738  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.2613      0.2540     0.1376  5
  test sensitivity            0.2364      0.2424     0.1460  5
  test specificity            0.7382      0.6727     0.1412  5
  test precision              0.3348      0.3448     0.0776  5
  test loss                   0.6891      0.6809     0.0205  5
  FPR (FP/(FP+TN))            0.2618      0.3273     0.1412  5
  FNR (FN/(FN+TP))            0.7636      0.7576     0.1460  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.490      11.6              0.530         0.456     5.4               0.501          0.527              0.501         0.507
choline                     0.687         0.646    0.618       9.4              0.696         0.648     1.8               0.565          0.548              0.622         0.616
phosphorus_free             0.396         0.499    0.381       1.2              0.739         0.349     5.4               0.514          0.616              0.484         0.508
sphingolipids               0.599         0.543    0.466       1.6              0.496         0.432     3.2               0.537          0.478              0.490         0.440

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.489               0.486                  0.065                     0.098

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.471               0.470                  0.074                     0.126

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.542               0.521                  0.107                     0.057

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.518               0.521                  0.066                     0.073

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.516  0.494      0.501     0.488
10     0.516  0.487      0.501     0.467
49     0.516  0.465      0.501     0.446
51     0.516  0.479      0.501     0.458
120    0.516  0.489      0.501     0.471

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.656      0.028          0.708              0.721           0.014
10        0.628         0.629      0.002          0.708              0.710           0.003
49        0.628         0.640      0.012          0.708              0.719           0.011
51        0.628         0.638      0.010          0.708              0.717           0.010
120       0.628         0.640      0.012          0.708              0.722           0.014

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.585  0.490      0.566     0.456     0.585         0.587      0.002          0.657              0.662           0.006
choline          0.671  0.618      0.671     0.648     0.671         0.685      0.014          0.767              0.782           0.016
phosphorus_free  0.289  0.381      0.289     0.349     0.711         0.723      0.012          0.772              0.791           0.019
sphingolipids    0.521  0.466      0.480     0.432     0.544         0.566      0.022          0.635              0.651           0.016

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.516               0.553                  0.041                     0.164
net               0.489               0.486                  0.065                     0.098
fit_chem          0.628               0.637                  0.034                     0.077
fit_chem_net      0.640               0.633                  0.037                     0.076
increment         0.012               0.004                  0.020                     0.008

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.501               0.527                  0.043                     0.162
net_prot               0.471               0.470                  0.074                     0.126
fit_chem_prot          0.708               0.701                  0.042                     0.072
fit_chem_net_prot      0.722               0.704                  0.040                     0.075
increment_prot         0.014               0.003                  0.025                     0.006
```
