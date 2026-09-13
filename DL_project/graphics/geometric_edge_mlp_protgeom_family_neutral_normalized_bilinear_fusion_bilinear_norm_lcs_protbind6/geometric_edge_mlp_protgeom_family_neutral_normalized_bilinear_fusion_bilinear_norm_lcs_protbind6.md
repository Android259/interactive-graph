# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_protbind6

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_protbind6'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.4753      0.5841      0.6415      0.7167      0.5097      0.5775
groups_choline            5      0.3604      0.8455      0.7071      0.6068      0.4107      0.8131
groups_phosphorus_free    5      0.3161      0.6316      0.5476      0.5948      0.2933      0.7357
groups_sphingolipids      5      0.2788      0.7455      0.5824      0.6301      0.5030      0.6148
ALL                      20      0.3576      0.7017      0.6197      0.6371      0.4292      0.6853

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5401      0.5406     0.0497  20
max valid BA                0.5572      0.5577     0.0453  20
best valid F1               0.4918      0.5259     0.1067  20
test BA                     0.5296      0.5212     0.0702  20
test AUC                    0.5397      0.5388     0.1162  20
test AUC in-protein         0.5234      0.4994     0.1000  20
  (proteins averaged)       7.9000      8.5000     3.5968  20
test AUC in-protein (pairs)      0.5417      0.5407     0.1253  20
  (proteins contributing)     11.7000     14.0000     5.3024  20
test F1                     0.3566      0.3812     0.1515  20
test sensitivity            0.3576      0.3342     0.2213  20
test specificity            0.7017      0.7766     0.2390  20
test precision              0.4795      0.4211     0.1839  19
test loss                   0.7038      0.6879     0.0579  20
FPR (FP/(FP+TN))            0.2983      0.2234     0.2390  20
FNR (FN/(FN+TP))            0.6424      0.6658     0.2213  20

=== abs(sensitivity-specificity) gap: mean=0.4501 median=0.5086 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5251      0.5254     0.0205  5
  max valid BA                0.5436      0.5446     0.0136  5
  best valid F1               0.5308      0.5377     0.0258  5
  test BA                     0.5297      0.5193     0.0351  5
  test AUC                    0.5299      0.5447     0.0424  5
  test AUC in-protein         0.5026      0.5048     0.0645  5
    (proteins averaged)      12.2000     12.0000     0.4472  5
  test AUC in-protein (pairs)      0.5786      0.5812     0.0498  5
    (proteins contributing)     16.4000     17.0000     1.5166  5
  test F1                     0.4396      0.4505     0.0544  5
  test sensitivity            0.4753      0.4624     0.0872  5
  test specificity            0.5841      0.5762     0.0697  5
  test precision              0.4126      0.4019     0.0387  5
  test loss                   0.7176      0.7014     0.0489  5
  FPR (FP/(FP+TN))            0.4159      0.4238     0.0697  5
  FNR (FN/(FN+TP))            0.5247      0.5376     0.0872  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5985      0.5893     0.0448  5
  max valid BA                0.6119      0.5952     0.0371  5
  best valid F1               0.5614      0.5776     0.0635  5
  test BA                     0.6029      0.6279     0.0552  5
  test AUC                    0.6833      0.6575     0.0411  5
  test AUC in-protein         0.6512      0.6360     0.0324  5
    (proteins averaged)       9.8000     10.0000     0.4472  5
  test AUC in-protein (pairs)      0.6533      0.6492     0.0431  5
    (proteins contributing)     14.8000     15.0000     0.4472  5
  test F1                     0.4430      0.5062     0.1238  5
  test sensitivity            0.3604      0.3694     0.1288  5
  test specificity            0.8455      0.8204     0.0637  5
  test precision              0.6060      0.6000     0.1229  5
  test loss                   0.7106      0.6686     0.1117  5
  FPR (FP/(FP+TN))            0.1545      0.1796     0.0637  5
  FNR (FN/(FN+TP))            0.6396      0.6306     0.1288  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5050      0.5000     0.0496  5
  max valid BA                0.5145      0.5000     0.0413  5
  best valid F1               0.3581      0.3913     0.1304  5
  test BA                     0.4739      0.5000     0.0814  5
  test AUC                    0.4182      0.4488     0.0776  5
  test AUC in-protein         0.4236      0.4101     0.0579  5
    (proteins averaged)       6.6000      7.0000     1.1402  5
  test AUC in-protein (pairs)      0.3925      0.4393     0.0947  5
    (proteins contributing)     12.2000     13.0000     2.1679  5
  test F1                     0.2268      0.2368     0.2078  5
  test sensitivity            0.3161      0.2581     0.4038  5
  test specificity            0.6316      0.7895     0.4372  5
  test precision              0.4881      0.3761     0.3518  4
  test loss                   0.6990      0.6877     0.0188  5
  FPR (FP/(FP+TN))            0.3684      0.2105     0.4372  5
  FNR (FN/(FN+TP))            0.6839      0.7419     0.4038  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5318      0.5396     0.0259  5
  max valid BA                0.5589      0.5606     0.0154  5
  best valid F1               0.5169      0.5155     0.0366  5
  test BA                     0.5121      0.5212     0.0385  5
  test AUC                    0.5273      0.5328     0.1003  5
  test AUC in-protein         0.5164      0.4940     0.0742  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5426      0.5305     0.1270  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.3169      0.3077     0.0814  5
  test sensitivity            0.2788      0.2424     0.1345  5
  test specificity            0.7455      0.7636     0.1397  5
  test precision              0.4133      0.3953     0.1080  5
  test loss                   0.6881      0.6921     0.0078  5
  FPR (FP/(FP+TN))            0.2545      0.2364     0.1397  5
  FNR (FN/(FN+TP))            0.7212      0.7576     0.1345  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.529      11.6              0.530         0.495     5.4               0.501          0.532              0.501         0.516
choline                     0.687         0.646    0.630       9.4              0.696         0.621     1.8               0.565          0.575              0.622         0.617
phosphorus_free             0.396         0.499    0.345       1.2              0.739         0.345     5.4               0.514          0.473              0.484         0.495
sphingolipids               0.599         0.543    0.485       1.6              0.496         0.455     3.2               0.537          0.461              0.490         0.495

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.497               0.513                  0.032                     0.118

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.479               0.478                  0.066                     0.114

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.510               0.506                  0.090                     0.053

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.531               0.531                  0.055                     0.058

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.516  0.467      0.501     0.444
10     0.516  0.479      0.501     0.471
49     0.516  0.474      0.501     0.452
51     0.516  0.481      0.501     0.467
120    0.516  0.497      0.501     0.479

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.644      0.016          0.708              0.718           0.011
10        0.628         0.637      0.009          0.708              0.714           0.006
49        0.628         0.635      0.007          0.708              0.714           0.006
51        0.628         0.633      0.005          0.708              0.715           0.008
120       0.628         0.638      0.010          0.708              0.716           0.008

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.585  0.529      0.566     0.495     0.585         0.584     -0.001          0.657              0.657           0.001
choline          0.671  0.630      0.671     0.621     0.671         0.698      0.027          0.767              0.778           0.011
phosphorus_free  0.289  0.345      0.289     0.345     0.711         0.714      0.002          0.772              0.792           0.020
sphingolipids    0.521  0.485      0.480     0.455     0.544         0.556      0.012          0.635              0.636           0.001

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.516               0.553                  0.041                     0.164
net               0.497               0.513                  0.032                     0.118
fit_chem          0.628               0.637                  0.034                     0.077
fit_chem_net      0.638               0.635                  0.040                     0.079
increment         0.010               0.008                  0.019                     0.012

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.501               0.527                  0.043                     0.162
net_prot               0.479               0.478                  0.066                     0.114
fit_chem_prot          0.708               0.701                  0.042                     0.072
fit_chem_net_prot      0.716               0.706                  0.044                     0.081
increment_prot         0.008               0.002                  0.014                     0.009
```
