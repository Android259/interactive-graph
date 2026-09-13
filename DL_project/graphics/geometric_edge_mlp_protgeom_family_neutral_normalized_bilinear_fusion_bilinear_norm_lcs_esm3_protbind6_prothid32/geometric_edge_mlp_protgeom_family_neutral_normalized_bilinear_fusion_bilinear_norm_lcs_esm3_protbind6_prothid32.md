# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protbind6_prothid32

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protbind6_prothid32'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6796      0.4450      0.9379      0.8560      0.6151      0.5576
groups_choline            5      0.4360      0.6778      0.9182      0.7526      0.5268      0.7262
groups_phosphorus_free    5      0.5871      0.6035      0.8031      0.6825      0.7733      0.5929
groups_sphingolipids      5      0.2727      0.6291      0.8025      0.6019      0.3576      0.7593
ALL                      20      0.4939      0.5889      0.8655      0.7233      0.5682      0.6590

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5820      0.5741     0.0487  20
max valid BA                0.6136      0.5955     0.0577  20
best valid F1               0.5503      0.5429     0.0612  20
test BA                     0.5414      0.5466     0.0766  20
test AUC                    0.5707      0.5802     0.1028  20
test AUC in-protein         0.5687      0.5392     0.1362  20
  (proteins averaged)       7.9000      8.5000     3.5968  20
test AUC in-protein (pairs)      0.6025      0.5924     0.1220  20
  (proteins contributing)     11.7000     14.0000     5.3024  20
test F1                     0.4393      0.4900     0.1222  20
test sensitivity            0.4939      0.5418     0.1948  20
test specificity            0.5889      0.5928     0.1716  20
test precision              0.4235      0.4368     0.1036  20
test loss                   1.0527      0.8967     0.4584  20
FPR (FP/(FP+TN))            0.4111      0.4072     0.1716  20
FNR (FN/(FN+TP))            0.5061      0.4582     0.1948  20

=== abs(sensitivity-specificity) gap: mean=0.2914 median=0.2739 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5720      0.5693     0.0151  5
  max valid BA                0.5863      0.5888     0.0102  5
  best valid F1               0.5507      0.5447     0.0154  5
  test BA                     0.5623      0.5635     0.0309  5
  test AUC                    0.5727      0.5794     0.0355  5
  test AUC in-protein         0.5188      0.5151     0.0217  5
    (proteins averaged)      12.2000     12.0000     0.4472  5
  test AUC in-protein (pairs)      0.5882      0.5949     0.0344  5
    (proteins contributing)     16.4000     17.0000     1.5166  5
  test F1                     0.5263      0.5133     0.0276  5
  test sensitivity            0.6796      0.6989     0.0642  5
  test specificity            0.4450      0.4437     0.0779  5
  test precision              0.4310      0.4375     0.0239  5
  test loss                   1.4142      1.5117     0.3255  5
  FPR (FP/(FP+TN))            0.5550      0.5563     0.0779  5
  FNR (FN/(FN+TP))            0.3204      0.3011     0.0642  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5667      0.5565     0.0379  5
  max valid BA                0.6265      0.6339     0.0208  5
  best valid F1               0.5670      0.5691     0.0272  5
  test BA                     0.5569      0.5306     0.0650  5
  test AUC                    0.6080      0.6190     0.0793  5
  test AUC in-protein         0.6697      0.6642     0.0579  5
    (proteins averaged)       9.8000     10.0000     0.4472  5
  test AUC in-protein (pairs)      0.6300      0.6672     0.0903  5
    (proteins contributing)     14.8000     15.0000     0.4472  5
  test F1                     0.4455      0.4425     0.1114  5
  test sensitivity            0.4360      0.4505     0.1480  5
  test specificity            0.6778      0.6467     0.0976  5
  test precision              0.4712      0.4576     0.0798  5
  test loss                   0.9638      1.0299     0.2967  5
  FPR (FP/(FP+TN))            0.3222      0.3533     0.0976  5
  FNR (FN/(FN+TP))            0.5640      0.5495     0.1480  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6394      0.6226     0.0530  5
  max valid BA                0.6831      0.7101     0.0556  5
  best valid F1               0.6084      0.6420     0.0626  5
  test BA                     0.5953      0.6194     0.0458  5
  test AUC                    0.6374      0.6389     0.0935  5
  test AUC in-protein         0.6651      0.7060     0.1160  5
    (proteins averaged)       6.6000      7.0000     1.1402  5
  test AUC in-protein (pairs)      0.7023      0.6951     0.1041  5
    (proteins contributing)     12.2000     13.0000     2.1679  5
  test F1                     0.5060      0.5161     0.0305  5
  test sensitivity            0.5871      0.6452     0.1338  5
  test specificity            0.6035      0.5614     0.2010  5
  test precision              0.4764      0.4565     0.1025  5
  test loss                   0.7106      0.6879     0.1330  5
  FPR (FP/(FP+TN))            0.3965      0.4386     0.2010  5
  FNR (FN/(FN+TP))            0.4129      0.3548     0.1338  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5498      0.5446     0.0313  5
  max valid BA                0.5584      0.5522     0.0350  5
  best valid F1               0.4752      0.4783     0.0359  5
  test BA                     0.4509      0.4455     0.0766  5
  test AUC                    0.4648      0.4386     0.1122  5
  test AUC in-protein         0.4212      0.4685     0.1273  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4896      0.5607     0.1447  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.2796      0.2857     0.0996  5
  test sensitivity            0.2727      0.2727     0.1303  5
  test specificity            0.6291      0.6909     0.2142  5
  test precision              0.3154      0.3000     0.1119  5
  test loss                   1.1220      0.6947     0.6788  5
  FPR (FP/(FP+TN))            0.3709      0.3091     0.2142  5
  FNR (FN/(FN+TP))            0.7273      0.7273     0.1303  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.551      11.6              0.530         0.454     5.4               0.501          0.590              0.501         0.569
choline                     0.687         0.646    0.535       9.4              0.696         0.626     1.8               0.565          0.546              0.622         0.561
phosphorus_free             0.396         0.499    0.594       1.2              0.739         0.601     5.4               0.514          0.538              0.484         0.550
sphingolipids               0.599         0.543    0.450       1.6              0.496         0.390     3.2               0.537          0.542              0.490         0.451

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                      0.07
net_AUC           0.532               0.536                  0.064                      0.06

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.518               0.524                  0.102                     0.114

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.554               0.595                  0.147                     0.024

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.533               0.545                  0.063                     0.055

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.516  0.497      0.501     0.483
10     0.516  0.480      0.501     0.429
49     0.516  0.512      0.501     0.493
51     0.516  0.512      0.501     0.489
120    0.516  0.532      0.501     0.518

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.637      0.009          0.708              0.712           0.005
10        0.628         0.662      0.034          0.708              0.723           0.015
49        0.628         0.641      0.013          0.708              0.729           0.022
51        0.628         0.645      0.017          0.708              0.731           0.023
120       0.628         0.643      0.015          0.708              0.726           0.019

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.585  0.551      0.566     0.454     0.585         0.603      0.018          0.657              0.673           0.017
choline          0.671  0.535      0.671     0.626     0.671         0.673      0.002          0.767              0.769           0.003
phosphorus_free  0.289  0.594      0.289     0.601     0.711         0.732      0.021          0.772              0.786           0.014
sphingolipids    0.521  0.450      0.480     0.390     0.544         0.565      0.021          0.635              0.676           0.042

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.516               0.553                  0.041                     0.164
net               0.532               0.536                  0.064                     0.060
fit_chem          0.628               0.637                  0.034                     0.077
fit_chem_net      0.643               0.637                  0.043                     0.075
increment         0.015               0.009                  0.024                     0.009

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.501               0.527                  0.043                     0.162
net_prot               0.518               0.524                  0.102                     0.114
fit_chem_prot          0.708               0.701                  0.042                     0.072
fit_chem_net_prot      0.726               0.739                  0.037                     0.060
increment_prot         0.019               0.005                  0.020                     0.016
```
