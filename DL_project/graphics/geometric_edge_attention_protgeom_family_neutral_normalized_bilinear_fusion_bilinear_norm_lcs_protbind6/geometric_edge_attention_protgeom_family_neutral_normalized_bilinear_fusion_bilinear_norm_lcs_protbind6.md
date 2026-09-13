# geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_protbind6

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_protbind6'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6215      0.3960      0.7214      0.6266      0.7269      0.3775
groups_choline            5      0.3063      0.8096      0.7684      0.6229      0.5375      0.7119
groups_phosphorus_free    5      0.6258      0.3509      0.8656      0.3211      0.7133      0.3429
groups_sphingolipids      5      0.4000      0.6509      0.6849      0.5349      0.4364      0.6926
ALL                      20      0.4884      0.5518      0.7601      0.5264      0.6035      0.5312

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5383      0.5347     0.0342  20
max valid BA                0.5674      0.5640     0.0547  20
best valid F1               0.5445      0.5510     0.0463  20
test BA                     0.5201      0.5054     0.0409  20
test AUC                    0.5227      0.5066     0.1047  20
test AUC in-protein         0.5176      0.4961     0.1018  20
  (proteins averaged)       7.9000      8.5000     3.5968  20
test AUC in-protein (pairs)      0.5142      0.5409     0.1187  20
  (proteins contributing)     11.7000     14.0000     5.3024  20
test F1                     0.3833      0.4246     0.1586  20
test sensitivity            0.4884      0.5000     0.3268  20
test specificity            0.5518      0.6000     0.3391  20
test precision              0.4347      0.4000     0.1252  19
test loss                   0.7278      0.6984     0.1002  20
FPR (FP/(FP+TN))            0.4482      0.4000     0.3391  20
FNR (FN/(FN+TP))            0.5116      0.5000     0.3268  20

=== abs(sensitivity-specificity) gap: mean=0.5674 median=0.5734 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5272      0.5315     0.0232  5
  max valid BA                0.5522      0.5581     0.0298  5
  best valid F1               0.5507      0.5519     0.0053  5
  test BA                     0.5088      0.5030     0.0338  5
  test AUC                    0.5205      0.4944     0.0669  5
  test AUC in-protein         0.4825      0.4794     0.0644  5
    (proteins averaged)      12.2000     12.0000     0.4472  5
  test AUC in-protein (pairs)      0.5263      0.5431     0.1027  5
    (proteins contributing)     16.4000     17.0000     1.5166  5
  test F1                     0.4604      0.4923     0.0978  5
  test sensitivity            0.6215      0.6882     0.2382  5
  test specificity            0.3960      0.3179     0.2219  5
  test precision              0.3879      0.3832     0.0218  5
  test loss                   0.7669      0.6999     0.1196  5
  FPR (FP/(FP+TN))            0.6040      0.6821     0.2219  5
  FNR (FN/(FN+TP))            0.3785      0.3118     0.2382  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5690      0.5625     0.0252  5
  max valid BA                0.6247      0.6369     0.0468  5
  best valid F1               0.5846      0.5773     0.0156  5
  test BA                     0.5579      0.5601     0.0151  5
  test AUC                    0.6397      0.6395     0.0203  5
  test AUC in-protein         0.6616      0.6531     0.0239  5
    (proteins averaged)       9.8000     10.0000     0.4472  5
  test AUC in-protein (pairs)      0.6411      0.6354     0.0507  5
    (proteins contributing)     14.8000     15.0000     0.4472  5
  test F1                     0.3477      0.3038     0.1264  5
  test sensitivity            0.3063      0.2162     0.2458  5
  test specificity            0.8096      0.8922     0.2354  5
  test precision              0.5939      0.5938     0.1334  5
  test loss                   0.6623      0.6507     0.0291  5
  FPR (FP/(FP+TN))            0.1904      0.1078     0.2354  5
  FNR (FN/(FN+TP))            0.6937      0.7838     0.2458  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5201      0.5000     0.0402  5
  max valid BA                0.5281      0.5000     0.0580  5
  best valid F1               0.4934      0.5172     0.0675  5
  test BA                     0.4883      0.5000     0.0269  5
  test AUC                    0.3859      0.4058     0.0540  5
  test AUC in-protein         0.4312      0.4020     0.0710  5
    (proteins averaged)       6.6000      7.0000     1.1402  5
  test AUC in-protein (pairs)      0.3660      0.3721     0.0280  5
    (proteins contributing)     12.2000     13.0000     2.1679  5
  test F1                     0.3503      0.5172     0.2418  5
  test sensitivity            0.6258      0.9677     0.5011  5
  test specificity            0.3509      0.0351     0.4751  5
  test precision              0.3239      0.3523     0.0572  4
  test loss                   0.7630      0.7080     0.1328  5
  FPR (FP/(FP+TN))            0.6491      0.9649     0.4751  5
  FNR (FN/(FN+TP))            0.3742      0.0323     0.5011  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5369      0.5337     0.0318  5
  max valid BA                0.5645      0.5699     0.0380  5
  best valid F1               0.5493      0.5500     0.0037  5
  test BA                     0.5255      0.5333     0.0510  5
  test AUC                    0.5447      0.5455     0.0559  5
  test AUC in-protein         0.4953      0.4718     0.0452  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5234      0.5387     0.0717  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.3747      0.4096     0.1584  5
  test sensitivity            0.4000      0.4848     0.2049  5
  test specificity            0.6509      0.6182     0.1993  5
  test precision              0.4108      0.4103     0.0489  5
  test loss                   0.7191      0.6962     0.0776  5
  FPR (FP/(FP+TN))            0.3491      0.3818     0.1993  5
  FNR (FN/(FN+TP))            0.6000      0.5152     0.2049  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.506      11.6              0.530         0.471     5.4               0.501          0.499              0.501         0.546
choline                     0.687         0.646    0.548       9.4              0.696         0.561     1.8               0.565          0.504              0.622         0.540
phosphorus_free             0.396         0.499    0.349       1.2              0.739         0.346     5.4               0.514          0.577              0.484         0.524
sphingolipids               0.599         0.543    0.444       1.6              0.496         0.433     3.2               0.537          0.494              0.490         0.481

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.462               0.482                  0.080                     0.086

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.453               0.479                  0.094                     0.089

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.519               0.495                  0.089                     0.039

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.523               0.530                  0.078                     0.029

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.516  0.476      0.501     0.448
10     0.516  0.492      0.501     0.471
49     0.516  0.444      0.501     0.425
51     0.516  0.462      0.501     0.452
120    0.516  0.462      0.501     0.453

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.640      0.013          0.708              0.709           0.001
10        0.628         0.638      0.011          0.708              0.716           0.008
49        0.628         0.652      0.024          0.708              0.719           0.012
51        0.628         0.652      0.024          0.708              0.723           0.015
120       0.628         0.644      0.016          0.708              0.724           0.016

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.585  0.506      0.566     0.471     0.585         0.584     -0.001          0.657              0.657           0.000
choline          0.671  0.548      0.671     0.561     0.671         0.680      0.009          0.767              0.768           0.001
phosphorus_free  0.289  0.349      0.289     0.346     0.711         0.747      0.036          0.772              0.814           0.042
sphingolipids    0.521  0.444      0.480     0.433     0.544         0.564      0.020          0.635              0.656           0.021

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.516               0.553                  0.041                     0.164
net               0.462               0.482                  0.080                     0.086
fit_chem          0.628               0.637                  0.034                     0.077
fit_chem_net      0.644               0.632                  0.041                     0.085
increment         0.016               0.012                  0.018                     0.016

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.501               0.527                  0.043                     0.162
net_prot               0.453               0.479                  0.094                     0.089
fit_chem_prot          0.708               0.701                  0.042                     0.072
fit_chem_net_prot      0.724               0.723                  0.038                     0.080
increment_prot         0.016               0.003                  0.018                     0.020
```
