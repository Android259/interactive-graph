# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_protbind6_prothid32

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_protbind6_prothid32'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.5118      0.4887      0.6652      0.5955      0.6409      0.4344
groups_choline            5      0.3658      0.8192      0.6715      0.6231      0.5089      0.7524
groups_phosphorus_free    5      0.4581      0.4316      0.6614      0.5098      0.3600      0.5893
groups_sphingolipids      5      0.3636      0.6000      0.5768      0.5967      0.5091      0.5815
ALL                      20      0.4248      0.5849      0.6437      0.5813      0.5047      0.5894

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5230      0.5257     0.0626  20
max valid BA                0.5471      0.5443     0.0714  20
best valid F1               0.4909      0.5275     0.1218  20
test BA                     0.5048      0.5110     0.0801  20
test AUC                    0.5114      0.5268     0.1255  20
test AUC in-protein         0.4923      0.4773     0.1275  20
  (proteins averaged)       7.9000      8.5000     3.5968  20
test AUC in-protein (pairs)      0.5160      0.5539     0.1394  20
  (proteins contributing)     11.7000     14.0000     5.3024  20
test F1                     0.3564      0.3891     0.1776  20
test sensitivity            0.4248      0.3833     0.2893  20
test specificity            0.5849      0.6313     0.3028  20
test precision              0.4015      0.3931     0.1343  18
test loss                   0.6934      0.6891     0.0368  20
FPR (FP/(FP+TN))            0.4151      0.3687     0.3028  20
FNR (FN/(FN+TP))            0.5752      0.6167     0.2893  20

=== abs(sensitivity-specificity) gap: mean=0.5024 median=0.5130 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4997      0.5000     0.0276  5
  max valid BA                0.5376      0.5436     0.0126  5
  best valid F1               0.5339      0.5367     0.0164  5
  test BA                     0.5003      0.5130     0.0375  5
  test AUC                    0.5125      0.5106     0.0552  5
  test AUC in-protein         0.4787      0.4744     0.0741  5
    (proteins averaged)      12.2000     12.0000     0.4472  5
  test AUC in-protein (pairs)      0.5502      0.5634     0.0515  5
    (proteins contributing)     16.4000     17.0000     1.5166  5
  test F1                     0.3672      0.4981     0.2318  5
  test sensitivity            0.5118      0.6882     0.3647  5
  test specificity            0.4887      0.3377     0.3249  5
  test precision              0.3693      0.3906     0.0514  4
  test loss                   0.7055      0.7093     0.0209  5
  FPR (FP/(FP+TN))            0.5113      0.6623     0.3249  5
  FNR (FN/(FN+TP))            0.4882      0.3118     0.3647  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5836      0.5774     0.0432  5
  max valid BA                0.6307      0.6339     0.0415  5
  best valid F1               0.5740      0.5773     0.0515  5
  test BA                     0.5925      0.6053     0.0501  5
  test AUC                    0.6598      0.6496     0.0363  5
  test AUC in-protein         0.6617      0.6450     0.0401  5
    (proteins averaged)       9.8000     10.0000     0.4472  5
  test AUC in-protein (pairs)      0.6575      0.6498     0.0305  5
    (proteins contributing)     14.8000     15.0000     0.4472  5
  test F1                     0.4281      0.4444     0.1403  5
  test sensitivity            0.3658      0.3423     0.1729  5
  test specificity            0.8192      0.8383     0.1001  5
  test precision              0.5698      0.5500     0.0718  5
  test loss                   0.6627      0.6571     0.0167  5
  FPR (FP/(FP+TN))            0.1808      0.1617     0.1001  5
  FNR (FN/(FN+TP))            0.6342      0.6577     0.1729  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4735      0.5000     0.0843  5
  max valid BA                0.4746      0.5000     0.0821  5
  best valid F1               0.3540      0.3925     0.1723  5
  test BA                     0.4448      0.5000     0.1017  5
  test AUC                    0.3604      0.3396     0.1121  5
  test AUC in-protein         0.3610      0.3183     0.1021  5
    (proteins averaged)       6.6000      7.0000     1.1402  5
  test AUC in-protein (pairs)      0.3261      0.3458     0.1143  5
    (proteins contributing)     12.2000     13.0000     2.1679  5
  test F1                     0.2939      0.3922     0.2312  5
  test sensitivity            0.4581      0.5484     0.4115  5
  test specificity            0.4316      0.5088     0.3982  5
  test precision              0.2815      0.3170     0.1318  4
  test loss                   0.7181      0.7026     0.0578  5
  FPR (FP/(FP+TN))            0.5684      0.4912     0.3982  5
  FNR (FN/(FN+TP))            0.5419      0.4516     0.4115  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5352      0.5295     0.0184  5
  max valid BA                0.5453      0.5446     0.0139  5
  best valid F1               0.5017      0.5217     0.0578  5
  test BA                     0.4818      0.4939     0.0382  5
  test AUC                    0.5131      0.5410     0.0426  5
  test AUC in-protein         0.4677      0.4634     0.0361  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5302      0.5535     0.0616  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.3364      0.3590     0.1046  5
  test sensitivity            0.3636      0.3333     0.2132  5
  test specificity            0.6000      0.7091     0.2271  5
  test precision              0.3550      0.3710     0.0542  5
  test loss                   0.6872      0.6894     0.0138  5
  FPR (FP/(FP+TN))            0.4000      0.2909     0.2271  5
  FNR (FN/(FN+TP))            0.6364      0.6667     0.2132  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.492      11.6              0.530         0.448     5.4               0.501          0.471              0.501         0.495
choline                     0.687         0.646    0.602       9.4              0.696         0.624     1.8               0.565          0.513              0.622         0.595
phosphorus_free             0.396         0.499    0.350       1.2              0.739         0.320     5.4               0.514          0.520              0.484         0.500
sphingolipids               0.599         0.543    0.497       1.6              0.496         0.479     3.2               0.537          0.482              0.490         0.466

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.485               0.489                  0.063                     0.103

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.468               0.462                  0.075                     0.125

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.496               0.490                  0.065                     0.023

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.514               0.497                  0.042                     0.056

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.516  0.442      0.501     0.427
10     0.516  0.488      0.501     0.468
49     0.516  0.472      0.501     0.459
51     0.516  0.486      0.501     0.480
120    0.516  0.485      0.501     0.468

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.642      0.014          0.708              0.715           0.007
10        0.628         0.627     -0.001          0.708              0.714           0.007
49        0.628         0.638      0.010          0.708              0.719           0.012
51        0.628         0.631      0.003          0.708              0.718           0.010
120       0.628         0.628      0.001          0.708              0.716           0.009

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.585  0.492      0.566     0.448     0.585         0.588      0.003          0.657              0.662           0.006
choline          0.671  0.602      0.671     0.624     0.671         0.681      0.010          0.767              0.778           0.011
phosphorus_free  0.289  0.350      0.289     0.320     0.711         0.699     -0.012          0.772              0.787           0.015
sphingolipids    0.521  0.497      0.480     0.479     0.544         0.545      0.001          0.635              0.637           0.002

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.516               0.553                  0.041                     0.164
net               0.485               0.489                  0.063                     0.103
fit_chem          0.628               0.637                  0.034                     0.077
fit_chem_net      0.628               0.644                  0.041                     0.074
increment         0.001               0.002                  0.017                     0.009

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.501               0.527                  0.043                     0.162
net_prot               0.468               0.462                  0.075                     0.125
fit_chem_prot          0.708               0.701                  0.042                     0.072
fit_chem_net_prot      0.716               0.705                  0.044                     0.077
increment_prot         0.009               0.004                  0.015                     0.006
```
