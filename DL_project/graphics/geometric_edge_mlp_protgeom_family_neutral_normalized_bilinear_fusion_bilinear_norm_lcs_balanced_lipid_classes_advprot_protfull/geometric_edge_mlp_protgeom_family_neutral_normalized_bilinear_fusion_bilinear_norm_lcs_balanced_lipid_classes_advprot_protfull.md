# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_balanced_lipid_classes_advprot_protfull

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_balanced_lipid_classes_advprot_protfull'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.8903      0.1115      0.6683      0.5656      0.8387      0.2275
groups_choline            5      0.6847      0.4158      0.4423      0.6100      0.6446      0.5040
groups_phosphorus_free    5      0.1742      0.7714      0.5560      0.5757      0.5200      0.6408
groups_sphingolipids      5      0.3576      0.5610      0.5313      0.5650      0.4727      0.7000
ALL                      20      0.5267      0.4649      0.5495      0.5791      0.6190      0.5181

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5423      0.5393     0.0330  20
max valid BA                0.5685      0.5587     0.0373  20
best valid F1               0.5589      0.5505     0.0390  20
test BA                     0.4958      0.4979     0.0478  20
test AUC                    0.5043      0.5112     0.0600  20
test AUC in-protein         0.5388      0.5300     0.0754  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5336      0.5449     0.1164  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.3748      0.4437     0.1621  20
test sensitivity            0.5267      0.5762     0.3452  20
test specificity            0.4649      0.4241     0.3262  20
test precision              0.3635      0.3478     0.0534  19
test loss                   0.7070      0.6979     0.0285  20
FPR (FP/(FP+TN))            0.5351      0.5759     0.3262  20
FNR (FN/(FN+TP))            0.4733      0.4238     0.3452  20

=== abs(sensitivity-specificity) gap: mean=0.5985 median=0.5591 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5239      0.5111     0.0218  5
  max valid BA                0.5331      0.5369     0.0181  5
  best valid F1               0.5144      0.5138     0.0057  5
  test BA                     0.5009      0.5004     0.0067  5
  test AUC                    0.5246      0.5153     0.0338  5
  test AUC in-protein         0.5273      0.5593     0.0477  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.5268      0.5047     0.0599  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.4886      0.4802     0.0139  5
  test sensitivity            0.8903      0.8495     0.0848  5
  test specificity            0.1115      0.1366     0.0817  5
  test precision              0.3374      0.3371     0.0034  5
  test loss                   0.7481      0.7478     0.0253  5
  FPR (FP/(FP+TN))            0.8885      0.8634     0.0817  5
  FNR (FN/(FN+TP))            0.1097      0.1505     0.0848  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5460      0.5502     0.0310  5
  max valid BA                0.5743      0.5874     0.0346  5
  best valid F1               0.5463      0.5471     0.0106  5
  test BA                     0.5503      0.5721     0.0419  5
  test AUC                    0.5603      0.5727     0.0493  5
  test AUC in-protein         0.5611      0.5732     0.0706  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.5642      0.5680     0.0564  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.4652      0.5309     0.1484  5
  test sensitivity            0.6847      0.7748     0.3231  5
  test specificity            0.4158      0.3713     0.3104  5
  test precision              0.3945      0.4018     0.0261  5
  test loss                   0.6961      0.6967     0.0036  5
  FPR (FP/(FP+TN))            0.5842      0.6287     0.3104  5
  FNR (FN/(FN+TP))            0.3153      0.2252     0.3231  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5456      0.5221     0.0506  5
  max valid BA                0.5804      0.5878     0.0463  5
  best valid F1               0.5583      0.5505     0.0108  5
  test BA                     0.4728      0.4641     0.0200  5
  test AUC                    0.4801      0.4697     0.0293  5
  test AUC in-protein         0.5633      0.5333     0.1282  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.6295      0.6562     0.0787  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.1811      0.1500     0.1572  5
  test sensitivity            0.1742      0.0968     0.2035  5
  test specificity            0.7714      0.8571     0.2342  5
  test precision              0.3048      0.3246     0.0566  4
  test loss                   0.6829      0.6857     0.0098  5
  FPR (FP/(FP+TN))            0.2286      0.1429     0.2342  5
  FNR (FN/(FN+TP))            0.8258      0.9032     0.2035  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5537      0.5489     0.0235  5
  max valid BA                0.5864      0.5905     0.0278  5
  best valid F1               0.6167      0.6226     0.0113  5
  test BA                     0.4593      0.4871     0.0507  5
  test AUC                    0.4522      0.4383     0.0638  5
  test AUC in-protein         0.5034      0.5000     0.0136  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4140      0.3631     0.1442  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3643      0.3333     0.0670  5
  test sensitivity            0.3576      0.3030     0.1595  5
  test specificity            0.5610      0.6829     0.2439  5
  test precision              0.4056      0.4211     0.0452  5
  test loss                   0.7011      0.7019     0.0080  5
  FPR (FP/(FP+TN))            0.4390      0.3171     0.2439  5
  FNR (FN/(FN+TP))            0.6424      0.6970     0.1595  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.521      11.6              0.530         0.491     5.4               0.501          0.521              0.501         0.500
choline                     0.687         0.646    0.531       9.4              0.696         0.562     1.8               0.565          0.466              0.622         0.537
phosphorus_free             0.396         0.499    0.521       1.2              0.739         0.521     5.4               0.514          0.615              0.484         0.523
sphingolipids               0.599         0.543    0.508       1.6              0.496         0.476     3.2               0.537          0.463              0.490         0.428

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                      0.07
net_AUC           0.520               0.515                  0.044                      0.01

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.512               0.527                  0.142                     0.038

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.516               0.503                  0.082                     0.071

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.497               0.514                  0.068                     0.049

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.542  0.524      0.602     0.495
10     0.542  0.501      0.602     0.535
49     0.542  0.506      0.602     0.512
51     0.542  0.519      0.602     0.543
120    0.542  0.520      0.602     0.512

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.557         0.579      0.021          0.881              0.887           0.005
10        0.557         0.577      0.020          0.881              0.887           0.006
49        0.557         0.583      0.025          0.881              0.888           0.007
51        0.557         0.578      0.021          0.881              0.889           0.008
120       0.557         0.570      0.013          0.881              0.886           0.005

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.495  0.521      0.530     0.491     0.512         0.524      0.012          0.889              0.890           0.001
choline          0.646  0.531      0.696     0.562     0.646         0.652      0.006          0.867              0.868           0.001
phosphorus_free  0.499  0.521      0.739     0.521     0.536         0.535     -0.001          0.967              0.969           0.001
sphingolipids    0.526  0.508      0.496     0.476     0.535         0.569      0.034          0.802              0.819           0.017

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.542               0.514                  0.038                     0.071
net               0.520               0.515                  0.044                     0.010
fit_chem          0.557               0.533                  0.028                     0.060
fit_chem_net      0.570               0.536                  0.028                     0.058
increment         0.013               0.009                  0.023                     0.015

=== the same rows ranked INSIDE each protein, epoch 120 ===
121 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.602               0.553                  0.039                     0.120
net_prot               0.512               0.527                  0.142                     0.038
fit_chem_prot          0.881               0.871                  0.022                     0.068
fit_chem_net_prot      0.886               0.874                  0.021                     0.062
increment_prot         0.005               0.001                  0.014                     0.008
```
