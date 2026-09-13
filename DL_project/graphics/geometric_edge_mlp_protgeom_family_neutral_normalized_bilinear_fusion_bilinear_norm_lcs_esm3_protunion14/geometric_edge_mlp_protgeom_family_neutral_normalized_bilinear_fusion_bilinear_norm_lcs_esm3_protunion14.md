# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protunion14

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protunion14'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.5269      0.5589      0.9188      0.7962      0.5075      0.6371
groups_choline            5      0.3315      0.8994      0.7538      0.7934      0.4196      0.8083
groups_phosphorus_free    5      0.2903      0.7860      0.8866      0.7454      0.4533      0.7429
groups_sphingolipids      5      0.1818      0.7527      0.4799      0.6806      0.2788      0.7704
ALL                      20      0.3326      0.7493      0.7598      0.7539      0.4148      0.7397

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5479      0.5468     0.0585  20
max valid BA                0.5772      0.5720     0.0588  20
best valid F1               0.4865      0.5315     0.1137  20
test BA                     0.5409      0.5463     0.0718  20
test AUC                    0.6004      0.6089     0.0940  20
test AUC in-protein         0.5780      0.5878     0.1259  20
  (proteins averaged)       7.9000      8.5000     3.5968  20
test AUC in-protein (pairs)      0.6063      0.5948     0.1177  20
  (proteins contributing)     11.7000     14.0000     5.3024  20
test F1                     0.3457      0.3542     0.1713  20
test sensitivity            0.3326      0.3099     0.2180  20
test specificity            0.7493      0.7780     0.1968  20
test precision              0.4575      0.4464     0.1995  19
test loss                   0.9416      0.7999     0.3280  20
FPR (FP/(FP+TN))            0.2507      0.2220     0.1968  20
FNR (FN/(FN+TP))            0.6674      0.6901     0.2180  20

=== abs(sensitivity-specificity) gap: mean=0.4829 median=0.4789 n=20 ===
sensitivity std across seeds (by group): mean=0.1741 median=0.1389 n=4
specificity std across seeds (by group): mean=0.1552 median=0.1566 n=4

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5418      0.5499     0.0232  5
  max valid BA                0.5723      0.5710     0.0256  5
  best valid F1               0.5419      0.5462     0.0288  5
  test BA                     0.5429      0.5499     0.0512  5
  test AUC                    0.5702      0.5851     0.0521  5
  test AUC in-protein         0.5341      0.5192     0.0705  5
    (proteins averaged)      12.2000     12.0000     0.4472  5
  test AUC in-protein (pairs)      0.5766      0.5847     0.0362  5
    (proteins contributing)     16.4000     17.0000     1.5166  5
  test F1                     0.4679      0.4592     0.0574  5
  test sensitivity            0.5269      0.4839     0.1051  5
  test specificity            0.5589      0.5960     0.1205  5
  test precision              0.4277      0.4369     0.0526  5
  test loss                   1.1657      1.3227     0.2915  5
  FPR (FP/(FP+TN))            0.4411      0.4040     0.1205  5
  FNR (FN/(FN+TP))            0.4731      0.5161     0.1051  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5949      0.5848     0.0344  5
  max valid BA                0.6140      0.6339     0.0350  5
  best valid F1               0.5378      0.5566     0.0695  5
  test BA                     0.6155      0.6277     0.0317  5
  test AUC                    0.6952      0.6838     0.0338  5
  test AUC in-protein         0.6538      0.6427     0.0476  5
    (proteins averaged)       9.8000     10.0000     0.4472  5
  test AUC in-protein (pairs)      0.6610      0.7009     0.0799  5
    (proteins contributing)     14.8000     15.0000     0.4472  5
  test F1                     0.4334      0.4371     0.1048  5
  test sensitivity            0.3315      0.2973     0.1373  5
  test specificity            0.8994      0.9401     0.0836  5
  test precision              0.7195      0.7059     0.0906  5
  test loss                   0.6989      0.6759     0.0547  5
  FPR (FP/(FP+TN))            0.1006      0.0599     0.0836  5
  FNR (FN/(FN+TP))            0.6685      0.7027     0.1373  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5370      0.5054     0.0976  5
  max valid BA                0.5981      0.5976     0.0856  5
  best valid F1               0.4469      0.5246     0.1841  5
  test BA                     0.5381      0.5427     0.0628  5
  test AUC                    0.6334      0.6327     0.0316  5
  test AUC in-protein         0.6628      0.6794     0.1056  5
    (proteins averaged)       6.6000      7.0000     1.1402  5
  test AUC in-protein (pairs)      0.6912      0.7006     0.0920  5
    (proteins contributing)     12.2000     13.0000     2.1679  5
  test F1                     0.2806      0.3043     0.2198  5
  test sensitivity            0.2903      0.2258     0.3136  5
  test specificity            0.7860      0.8596     0.1927  5
  test precision              0.3335      0.4464     0.1984  5
  test loss                   0.9575      0.9835     0.1629  5
  FPR (FP/(FP+TN))            0.2140      0.1404     0.1927  5
  FNR (FN/(FN+TP))            0.7097      0.7742     0.3136  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5180      0.5034     0.0303  5
  max valid BA                0.5246      0.5034     0.0388  5
  best valid F1               0.4195      0.3908     0.0845  5
  test BA                     0.4673      0.4970     0.0562  5
  test AUC                    0.5027      0.5284     0.1070  5
  test AUC in-protein         0.4614      0.4928     0.1461  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4964      0.5508     0.1440  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.2011      0.1887     0.1306  5
  test sensitivity            0.1818      0.1515     0.1405  5
  test specificity            0.7527      0.7636     0.2240  5
  test precision              0.3223      0.3152     0.0765  4
  test loss                   0.9444      0.6927     0.5098  5
  FPR (FP/(FP+TN))            0.2473      0.2364     0.2240  5
  FNR (FN/(FN+TP))            0.8182      0.8485     0.1405  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.556      11.6              0.530         0.497     5.4               0.501          0.634              0.501         0.539
choline                     0.687         0.646    0.499       9.4              0.696         0.534     1.8               0.565          0.310              0.622         0.485
phosphorus_free             0.396         0.499    0.574       1.2              0.739         0.622     5.4               0.514          0.672              0.484         0.618
sphingolipids               0.599         0.543    0.374       1.6              0.496         0.341     3.2               0.537          0.461              0.490         0.384

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.501               0.518                  0.078                     0.091

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.498               0.499                  0.113                     0.117

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.519               0.523                  0.102                     0.167

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.506               0.522                  0.074                     0.098

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.516  0.457      0.501     0.443
10     0.516  0.457      0.501     0.419
49     0.516  0.512      0.501     0.514
51     0.516  0.522      0.501     0.523
120    0.516  0.501      0.501     0.498

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.645      0.017          0.708              0.722           0.014
10        0.628         0.672      0.044          0.708              0.732           0.025
49        0.628         0.662      0.034          0.708              0.731           0.024
51        0.628         0.662      0.034          0.708              0.740           0.033
120       0.628         0.659      0.031          0.708              0.719           0.012

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.585  0.556      0.566     0.497     0.585         0.599      0.014          0.657              0.661           0.005
choline          0.671  0.499      0.671     0.534     0.671         0.679      0.008          0.767              0.769           0.002
phosphorus_free  0.289  0.574      0.289     0.622     0.711         0.720      0.008          0.772              0.779           0.007
sphingolipids    0.521  0.374      0.480     0.341     0.544         0.640      0.096          0.635              0.668           0.033

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.516               0.553                  0.041                     0.164
net               0.501               0.518                  0.078                     0.091
fit_chem          0.628               0.637                  0.034                     0.077
fit_chem_net      0.659               0.661                  0.037                     0.052
increment         0.031               0.011                  0.027                     0.043

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.501               0.527                  0.043                     0.162
net_prot               0.498               0.499                  0.113                     0.117
fit_chem_prot          0.708               0.701                  0.042                     0.072
fit_chem_net_prot      0.719               0.723                  0.044                     0.063
increment_prot         0.012               0.006                  0.014                     0.015
```
