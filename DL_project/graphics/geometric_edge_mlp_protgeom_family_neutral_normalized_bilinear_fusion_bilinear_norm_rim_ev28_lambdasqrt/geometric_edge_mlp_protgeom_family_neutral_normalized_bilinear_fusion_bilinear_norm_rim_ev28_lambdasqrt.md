# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28_lambdasqrt

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28_lambdasqrt'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.7104      0.4689      0.7549      0.7334      0.6925      0.5032
groups_GLTP            5      0.3600      0.5680      0.5909      0.6067      0.3769      0.7462
groups_IP_trans        5      0.4261      0.7915      0.6683      0.6725      0.6500      0.7574
groups_LBP_BPI_CETP    5      0.2348      0.9191      0.7320      0.4634      0.3333      0.8638
groups_START           5      0.4492      0.5528      0.5686      0.6874      0.2000      0.8180
groups_lipocalin       5      0.2611      0.7500      0.5945      0.6560      0.4389      0.7611
groups_scp2            5      0.4235      0.7353      0.6460      0.6854      0.5647      0.7765
ALL                   35      0.4093      0.6837      0.6507      0.6435      0.4652      0.7466

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5754      0.5577     0.0662  35
max valid BA                0.6059      0.5909     0.0779  35
best valid F1               0.5258      0.5862     0.1698  35
test BA                     0.5465      0.5441     0.0726  35
test AUC                    0.5703      0.5957     0.1272  35
test AUC in-protein         0.5540      0.5116     0.1541  35
  (proteins averaged)       3.1429      3.0000     1.0042  35
test AUC in-protein (pairs)      0.5704      0.5673     0.1288  35
  (proteins contributing)      3.5143      3.0000     1.7213  35
test F1                     0.3827      0.4516     0.2178  35
test sensitivity            0.4093      0.4179     0.3073  35
test specificity            0.6837      0.7660     0.2807  35
test precision              0.4523      0.4800     0.1567  33
test loss                   0.6795      0.6803     0.0459  35
FPR (FP/(FP+TN))            0.3163      0.2340     0.2807  35
FNR (FN/(FN+TP))            0.5907      0.5821     0.3073  35

=== abs(sensitivity-specificity) gap: mean=0.5565 median=0.5200 n=35 ===
sensitivity std across seeds (by group): mean=0.2724 median=0.2313 n=7
specificity std across seeds (by group): mean=0.2194 median=0.2016 n=7

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5726      0.5469     0.0557  5
  max valid BA                0.5979      0.5909     0.0347  5
  best valid F1               0.6950      0.6936     0.0220  5
  test BA                     0.5897      0.5833     0.0220  5
  test AUC                    0.6088      0.6003     0.0195  5
  test AUC in-protein         0.4558      0.4565     0.0281  5
    (proteins averaged)       4.0000      4.0000     0.0000  5
  test AUC in-protein (pairs)      0.6247      0.6439     0.0558  5
    (proteins contributing)      4.4000      4.0000     0.5477  5
  test F1                     0.6368      0.6750     0.0798  5
  test sensitivity            0.7104      0.8060     0.1973  5
  test specificity            0.4689      0.3770     0.2016  5
  test precision              0.6049      0.5882     0.0455  5
  test loss                   0.6894      0.6815     0.0245  5
  FPR (FP/(FP+TN))            0.5311      0.6230     0.2016  5
  FNR (FN/(FN+TP))            0.2896      0.1940     0.1973  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5462      0.5577     0.0292  5
  max valid BA                0.5615      0.5577     0.0161  5
  best valid F1               0.5723      0.6269     0.1311  5
  test BA                     0.4640      0.4600     0.0219  5
  test AUC                    0.4669      0.4800     0.0785  5
  test AUC in-protein         0.5038      0.5000     0.0559  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4591      0.4586     0.0747  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3464      0.2703     0.1923  5
  test sensitivity            0.3600      0.2000     0.3476  5
  test specificity            0.5680      0.7200     0.3078  5
  test precision              0.4211      0.4167     0.0559  5
  test loss                   0.7223      0.7386     0.0252  5
  FPR (FP/(FP+TN))            0.4320      0.2800     0.3078  5
  FNR (FN/(FN+TP))            0.6400      0.8000     0.3476  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6481      0.6547     0.0479  5
  max valid BA                0.7037      0.7159     0.0450  5
  best valid F1               0.6107      0.6349     0.0651  5
  test BA                     0.6088      0.6226     0.0488  5
  test AUC                    0.6925      0.6920     0.0222  5
  test AUC in-protein         0.7385      0.7465     0.0382  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.6776      0.6897     0.0310  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.4473      0.5000     0.1167  5
  test sensitivity            0.4261      0.5217     0.1519  5
  test specificity            0.7915      0.7660     0.0663  5
  test precision              0.4928      0.5000     0.0603  5
  test loss                   0.6358      0.6343     0.0138  5
  FPR (FP/(FP+TN))            0.2085      0.2340     0.0663  5
  FNR (FN/(FN+TP))            0.5739      0.4783     0.1519  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5756      0.5519     0.0596  5
  max valid BA                0.5986      0.5820     0.0753  5
  best valid F1               0.3896      0.5053     0.2302  5
  test BA                     0.5770      0.5338     0.0967  5
  test AUC                    0.5678      0.6725     0.2329  5
  test AUC in-protein         0.5772      0.6784     0.2241  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.5638      0.6716     0.2326  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.2885      0.2500     0.2624  5
  test sensitivity            0.2348      0.1739     0.2313  5
  test specificity            0.9191      0.9149     0.0508  5
  test precision              0.4244      0.4444     0.2824  5
  test loss                   0.6348      0.6539     0.0370  5
  FPR (FP/(FP+TN))            0.0809      0.0851     0.0508  5
  FNR (FN/(FN+TP))            0.7652      0.8261     0.2313  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5017      0.5000     0.0167  5
  max valid BA                0.5090      0.5054     0.0196  5
  best valid F1               0.4216      0.3529     0.1563  5
  test BA                     0.5010      0.5000     0.0342  5
  test AUC                    0.5059      0.5039     0.0628  5
  test AUC in-protein         0.4477      0.4407     0.0401  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5022      0.4679     0.0789  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.3146      0.2683     0.2718  5
  test sensitivity            0.4492      0.1692     0.5063  5
  test specificity            0.5528      0.8315     0.5082  5
  test precision              0.4353      0.4221     0.1628  4
  test loss                   0.7002      0.6986     0.0181  5
  FPR (FP/(FP+TN))            0.4472      0.1685     0.5082  5
  FNR (FN/(FN+TP))            0.5508      0.8308     0.5063  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5750      0.5278     0.0865  5
  max valid BA                0.6000      0.6111     0.0876  5
  best valid F1               0.4292      0.5000     0.2078  5
  test BA                     0.5056      0.5000     0.0707  5
  test AUC                    0.5212      0.5247     0.1373  5
  test AUC in-protein         0.5581      0.6768     0.2521  5
    (proteins averaged)       5.0000      5.0000     0.0000  5
  test AUC in-protein (pairs)      0.4946      0.5115     0.0598  5
    (proteins contributing)      7.2000      7.0000     0.4472  5
  test F1                     0.2210      0.0870     0.2340  5
  test sensitivity            0.2611      0.0556     0.3201  5
  test specificity            0.7500      0.7639     0.2118  5
  test precision              0.2752      0.2977     0.1467  4
  test loss                   0.7007      0.6947     0.0739  5
  FPR (FP/(FP+TN))            0.2500      0.2361     0.2118  5
  FNR (FN/(FN+TP))            0.7389      0.9444     0.3201  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6088      0.6324     0.0620  5
  max valid BA                0.6706      0.6618     0.0526  5
  best valid F1               0.5619      0.5484     0.0705  5
  test BA                     0.5794      0.6029     0.0556  5
  test AUC                    0.6289      0.6384     0.0834  5
  test AUC in-protein         0.5967      0.5769     0.0784  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.6707      0.6900     0.0910  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.4246      0.4516     0.0960  5
  test sensitivity            0.4235      0.4706     0.1523  5
  test specificity            0.7353      0.7941     0.1895  5
  test precision              0.4733      0.5000     0.0796  5
  test loss                   0.6729      0.6617     0.0292  5
  FPR (FP/(FP+TN))            0.2647      0.2059     0.1895  5
  FNR (FN/(FN+TP))            0.5765      0.5294     0.1523  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                         
CRAL-TRIO                0.630         0.484    0.479       4.0              0.369         0.454     5.0               0.458          0.401              0.432         0.492
GLTP                     0.605         0.521    0.498       2.0              0.512         0.495     3.0               0.523          0.450              0.526         0.476
IP_trans                 0.722         0.680    0.643       3.0              0.677         0.640     2.4               0.590          0.542              0.669         0.585
LBP_BPI_CETP             0.719         0.798    0.630       2.0              0.798         0.630     1.6               0.784          0.630              0.821         0.610
START                    0.576         0.508    0.487       3.0              0.474         0.457     4.0               0.536          0.579              0.524         0.479
lipocalin                0.565         0.331    0.570       5.0              0.246         0.605     2.2               0.646          0.647              0.622         0.626
scp2                     0.651         0.489    0.563       2.8              0.593         0.531     2.6               0.642          0.621              0.577         0.618

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.545               0.503                  0.065                     0.151
net_AUC           0.553               0.546                  0.071                     0.068

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.524               0.493                  0.065                     0.186
net_AUC_prot           0.545               0.537                  0.075                     0.080

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.597               0.581                  0.085                     0.106
net_AUC_lipid           0.553               0.539                  0.118                     0.095

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.596               0.561                  0.058                     0.125
net_AUC_pair           0.555               0.566                  0.083                     0.069

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.530      0.524     0.501
10     0.545  0.546      0.524     0.540
49     0.545  0.553      0.524     0.543
51     0.545  0.556      0.524     0.542
120    0.545  0.553      0.524     0.545

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.618         0.662      0.044          0.653              0.690           0.037
10        0.618         0.650      0.032          0.653              0.680           0.026
49        0.618         0.655      0.037          0.653              0.690           0.036
51        0.618         0.656      0.038          0.653              0.696           0.042
120       0.618         0.652      0.034          0.653              0.685           0.032

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.484  0.479      0.369     0.454     0.539         0.639      0.101          0.613              0.673           0.060
GLTP          0.521  0.498      0.512     0.495     0.543         0.574      0.030          0.565              0.596           0.031
IP_trans      0.680  0.643      0.677     0.640     0.680         0.722      0.041          0.693              0.728           0.035
LBP_BPI_CETP  0.798  0.630      0.798     0.630     0.798         0.809      0.010          0.801              0.815           0.014
START         0.508  0.487      0.474     0.457     0.536         0.556      0.020          0.606              0.637           0.031
lipocalin     0.331  0.570      0.246     0.605     0.669         0.685      0.017          0.673              0.691           0.018
scp2          0.489  0.563      0.593     0.531     0.562         0.583      0.021          0.622              0.655           0.033

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.545               0.503                  0.065                     0.151
net               0.553               0.546                  0.071                     0.068
fit_chem          0.618               0.590                  0.052                     0.101
fit_chem_net      0.652               0.628                  0.053                     0.092
increment         0.034               0.028                  0.033                     0.031

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.524               0.493                  0.065                     0.186
net_prot               0.545               0.537                  0.075                     0.080
fit_chem_prot          0.653               0.662                  0.055                     0.078
fit_chem_net_prot      0.685               0.677                  0.053                     0.071
increment_prot         0.032               0.028                  0.037                     0.015
```
