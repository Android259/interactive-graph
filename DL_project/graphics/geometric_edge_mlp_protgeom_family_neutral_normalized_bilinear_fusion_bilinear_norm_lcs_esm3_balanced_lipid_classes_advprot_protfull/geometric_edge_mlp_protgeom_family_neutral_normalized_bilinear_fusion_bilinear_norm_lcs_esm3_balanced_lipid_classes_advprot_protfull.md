# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_protfull

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_protfull'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.8624      0.1650      0.6254      0.5374      0.7591      0.3110
groups_choline            5      0.7207      0.4158      0.5022      0.5359      0.6571      0.5644
groups_phosphorus_free    5      0.1290      0.8204      0.5976      0.5924      0.2867      0.8408
groups_sphingolipids      5      0.3515      0.6390      0.5792      0.5684      0.5455      0.6900
ALL                      20      0.5159      0.5101      0.5761      0.5585      0.5621      0.6015

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5512      0.5437     0.0442  20
max valid BA                0.5818      0.5859     0.0473  20
best valid F1               0.5301      0.5422     0.1307  20
test BA                     0.5130      0.5042     0.0746  20
test AUC                    0.5445      0.5451     0.0781  20
test AUC in-protein         0.5678      0.5904     0.1706  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5415      0.5589     0.1261  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.3719      0.4583     0.2021  20
test sensitivity            0.5159      0.5937     0.3492  20
test specificity            0.5101      0.4653     0.3207  20
test precision              0.3682      0.3652     0.1044  19
test loss                   0.6991      0.6934     0.0299  20
FPR (FP/(FP+TN))            0.4899      0.5347     0.3207  20
FNR (FN/(FN+TP))            0.4841      0.4063     0.3492  20

=== abs(sensitivity-specificity) gap: mean=0.5433 median=0.5690 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5217      0.5097     0.0178  5
  max valid BA                0.5351      0.5333     0.0094  5
  best valid F1               0.5140      0.5167     0.0066  5
  test BA                     0.5137      0.5056     0.0296  5
  test AUC                    0.5163      0.5268     0.0542  5
  test AUC in-protein         0.4959      0.4687     0.0710  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.4824      0.4617     0.0515  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.4898      0.5041     0.0347  5
  test sensitivity            0.8624      0.9032     0.1451  5
  test specificity            0.1650      0.2022     0.1382  5
  test precision              0.3441      0.3395     0.0172  5
  test loss                   0.7327      0.7440     0.0344  5
  FPR (FP/(FP+TN))            0.8350      0.7978     0.1382  5
  FNR (FN/(FN+TP))            0.1376      0.0968     0.1451  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5753      0.5956     0.0525  5
  max valid BA                0.6107      0.6078     0.0365  5
  best valid F1               0.5580      0.5634     0.0251  5
  test BA                     0.5683      0.5755     0.0270  5
  test AUC                    0.5995      0.6083     0.0520  5
  test AUC in-protein         0.6548      0.6386     0.0420  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.6045      0.6347     0.0536  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.5160      0.5258     0.0194  5
  test sensitivity            0.7207      0.7027     0.1417  5
  test specificity            0.4158      0.4158     0.1875  5
  test precision              0.4105      0.4057     0.0309  5
  test loss                   0.6893      0.6930     0.0089  5
  FPR (FP/(FP+TN))            0.5842      0.5842     0.1875  5
  FNR (FN/(FN+TP))            0.2793      0.2973     0.1417  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5327      0.5296     0.0232  5
  max valid BA                0.5637      0.5857     0.0387  5
  best valid F1               0.4102      0.5316     0.2148  5
  test BA                     0.4747      0.4651     0.0395  5
  test AUC                    0.5472      0.5300     0.0809  5
  test AUC in-protein         0.5800      0.7167     0.3349  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.5883      0.5938     0.1458  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.1373      0.0541     0.1525  5
  test sensitivity            0.1290      0.0323     0.1867  5
  test specificity            0.8204      0.8980     0.2455  5
  test precision              0.2879      0.2424     0.1584  4
  test loss                   0.6743      0.6800     0.0201  5
  FPR (FP/(FP+TN))            0.1796      0.1020     0.2455  5
  FNR (FN/(FN+TP))            0.8710      0.9677     0.1867  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5752      0.5958     0.0522  5
  max valid BA                0.6177      0.6405     0.0435  5
  best valid F1               0.6380      0.6286     0.0217  5
  test BA                     0.4953      0.4782     0.1313  5
  test AUC                    0.5152      0.5262     0.1047  5
  test AUC in-protein         0.5404      0.5158     0.0480  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4909      0.5396     0.1829  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3444      0.3750     0.2368  5
  test sensitivity            0.3515      0.3636     0.2823  5
  test specificity            0.6390      0.6585     0.2702  5
  test precision              0.4144      0.3846     0.1298  5
  test loss                   0.7003      0.6950     0.0167  5
  FPR (FP/(FP+TN))            0.3610      0.3415     0.2702  5
  FNR (FN/(FN+TP))            0.6485      0.6364     0.2823  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.507      11.6              0.530         0.497     5.4               0.501          0.500              0.501         0.510
choline                     0.687         0.646    0.574       9.4              0.696         0.604     1.8               0.565          0.535              0.622         0.558
phosphorus_free             0.396         0.499    0.514       1.2              0.739         0.328     5.4               0.514          0.458              0.484         0.531
sphingolipids               0.599         0.543    0.507       1.6              0.496         0.496     3.2               0.537          0.442              0.490         0.450

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.526               0.523                  0.057                     0.033

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                   0.04                     0.120
net_AUC_prot           0.498               0.507                   0.14                     0.114

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.484               0.497                  0.103                     0.042

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.512               0.505                  0.060                     0.046

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.542  0.506      0.602     0.440
10     0.542  0.497      0.602     0.510
49     0.542  0.513      0.602     0.482
51     0.542  0.500      0.602     0.486
120    0.542  0.526      0.602     0.498

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.557         0.575      0.018          0.881              0.890           0.009
10        0.557         0.580      0.022          0.881              0.890           0.009
49        0.557         0.570      0.012          0.881              0.885           0.004
51        0.557         0.569      0.012          0.881              0.885           0.003
120       0.557         0.575      0.018          0.881              0.889           0.007

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.495  0.507      0.530     0.497     0.512         0.516      0.004          0.889              0.890           0.001
choline          0.646  0.574      0.696     0.604     0.646         0.649      0.003          0.867              0.868           0.001
phosphorus_free  0.499  0.514      0.739     0.328     0.536         0.551      0.015          0.967              0.969           0.002
sphingolipids    0.526  0.507      0.496     0.496     0.535         0.584      0.049          0.802              0.828           0.025

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.542               0.514                  0.038                     0.071
net               0.526               0.523                  0.057                     0.033
fit_chem          0.557               0.533                  0.028                     0.060
fit_chem_net      0.575               0.552                  0.030                     0.057
increment         0.018               0.005                  0.026                     0.021

=== the same rows ranked INSIDE each protein, epoch 120 ===
121 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.602               0.553                  0.039                     0.120
net_prot               0.498               0.507                  0.140                     0.114
fit_chem_prot          0.881               0.871                  0.022                     0.068
fit_chem_net_prot      0.889               0.871                  0.018                     0.059
increment_prot         0.007               0.002                  0.010                     0.012
```
