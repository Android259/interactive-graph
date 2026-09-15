# descriptors_head_family_neutral_lipprop_lcs_protbind6_lambdasqrt

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_head_family_neutral_lipprop_lcs_protbind6_lambdasqrt'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6258      0.5585      0.5710      0.6321      0.6645      0.6352
groups_choline            5      0.3838      0.7455      0.5197      0.4792      0.5089      0.7129
groups_phosphorus_free    5      0.5419      0.4898      0.4712      0.6948      0.5267      0.6490
groups_sphingolipids      5      0.5515      0.5756      0.4623      0.6278      0.4485      0.6700
ALL                      20      0.5258      0.5924      0.5061      0.6085      0.5371      0.6668

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5809      0.5886     0.0631  20
max valid BA                0.6020      0.6044     0.0673  20
best valid F1               0.5279      0.5569     0.0999  20
test BA                     0.5591      0.5709     0.0574  20
test AUC                    0.5688      0.5672     0.0872  20
test AUC in-protein         0.4879      0.4835     0.1826  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5193      0.5224     0.1438  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.4503      0.4751     0.1437  20
test sensitivity            0.5258      0.4961     0.2454  20
test specificity            0.5924      0.5627     0.2274  20
test precision              0.4619      0.4430     0.0835  19
test loss                   0.7162      0.7000     0.0719  20
FPR (FP/(FP+TN))            0.4076      0.4373     0.2274  20
FNR (FN/(FN+TP))            0.4742      0.5039     0.2454  20

=== abs(sensitivity-specificity) gap: mean=0.3595 median=0.2707 n=20 ===
sensitivity std across seeds (by group): mean=0.2448 median=0.2544 n=4
specificity std across seeds (by group): mean=0.2133 median=0.1806 n=4

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6349      0.6453     0.0286  5
  max valid BA                0.6498      0.6593     0.0382  5
  best valid F1               0.5610      0.5792     0.0416  5
  test BA                     0.5921      0.5871     0.0238  5
  test AUC                    0.6281      0.6461     0.0254  5
  test AUC in-protein         0.4753      0.4242     0.0982  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.4967      0.4571     0.1151  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.4944      0.4950     0.0525  5
  test sensitivity            0.6258      0.6667     0.1761  5
  test specificity            0.5585      0.4645     0.1591  5
  test precision              0.4257      0.4194     0.0330  5
  test loss                   0.6841      0.6985     0.0376  5
  FPR (FP/(FP+TN))            0.4415      0.5355     0.1591  5
  FNR (FN/(FN+TP))            0.3742      0.3333     0.1761  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5721      0.5770     0.0464  5
  max valid BA                0.6109      0.6264     0.0698  5
  best valid F1               0.4823      0.5547     0.1710  5
  test BA                     0.5647      0.5895     0.0419  5
  test AUC                    0.5697      0.5595     0.0638  5
  test AUC in-protein         0.4561      0.4418     0.0960  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.4584      0.4863     0.0767  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.3628      0.4601     0.2170  5
  test sensitivity            0.3838      0.4414     0.2614  5
  test specificity            0.7455      0.7376     0.1806  5
  test precision              0.4563      0.4510     0.0177  4
  test loss                   0.7358      0.7101     0.1180  5
  FPR (FP/(FP+TN))            0.2545      0.2624     0.1806  5
  FNR (FN/(FN+TP))            0.6162      0.5586     0.2614  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5769      0.5690     0.0255  5
  max valid BA                0.5878      0.5932     0.0215  5
  best valid F1               0.5246      0.5333     0.0583  5
  test BA                     0.5159      0.5171     0.0358  5
  test AUC                    0.4874      0.5115     0.0647  5
  test AUC in-protein         0.4111      0.3333     0.2950  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.4856      0.5312     0.1709  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.4314      0.4516     0.1151  5
  test sensitivity            0.5419      0.4516     0.2942  5
  test specificity            0.4898      0.5306     0.3328  5
  test precision              0.4427      0.3971     0.1074  5
  test loss                   0.7089      0.6971     0.0440  5
  FPR (FP/(FP+TN))            0.5102      0.4694     0.3328  5
  FNR (FN/(FN+TP))            0.4581      0.5484     0.2942  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5397      0.5148     0.0969  5
  max valid BA                0.5592      0.5523     0.0962  5
  best valid F1               0.5438      0.5591     0.0934  5
  test BA                     0.5636      0.5905     0.0909  5
  test AUC                    0.5902      0.5965     0.1181  5
  test AUC in-protein         0.6091      0.5134     0.1589  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.6364      0.7207     0.1615  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5126      0.4286     0.1330  5
  test sensitivity            0.5515      0.4545     0.2475  5
  test specificity            0.5756      0.5610     0.1806  5
  test precision              0.5216      0.5556     0.1092  5
  test loss                   0.7360      0.7215     0.0704  5
  FPR (FP/(FP+TN))            0.4244      0.4390     0.1806  5
  FNR (FN/(FN+TP))            0.4485      0.5455     0.2475  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (apolar_sasa_share,aromatic_share,aromatic_share_rim,buriedness_q50,chain,depth_q10,ev14_q10,ev28_q10,hbond,heavy,hydropathy_core,hydropathy_mean,hydropathy_rim,pocket_elongation_lambda_sqrt,pocket_flatness_lambda_sqrt,pocket_volume_per_sasa,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                      
anionic                     0.503         0.773    0.646              0.529         0.526
choline                     0.404         0.382    0.398              0.521         0.431
phosphorus_free             0.260         0.406    0.470              0.525         0.485
sphingolipids               0.367         0.328    0.438              0.497         0.520

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.472               0.390                  0.028                     0.203
net_AUC           0.488               0.484                  0.063                     0.109

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.518               0.522                  0.052                     0.014
net_AUC_pair           0.490               0.480                  0.087                     0.044

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.472  0.495      0.518     0.501
10     0.472  0.511      0.518     0.452
49     0.472  0.479      0.518     0.464
51     0.472  0.477      0.518     0.466
120    0.472  0.488      0.518     0.490

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.664         0.685      0.021
10        0.664         0.703      0.039
49        0.664         0.689      0.025
51        0.664         0.688      0.024
120       0.664         0.672      0.008

3. mean over seeds, epoch 120
                  chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                                  
anionic          0.773  0.646      0.529     0.526     0.773         0.778      0.005
choline          0.382  0.398      0.521     0.431     0.618         0.633      0.015
phosphorus_free  0.406  0.470      0.525     0.485     0.594         0.594     -0.000
sphingolipids    0.328  0.438      0.497     0.520     0.672         0.684      0.012

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.472               0.390                  0.028                     0.203
net               0.488               0.484                  0.063                     0.109
fit_chem          0.664               0.650                  0.028                     0.079
fit_chem_net      0.672               0.672                  0.027                     0.079
increment         0.008               0.002                  0.022                     0.007

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.518               0.522                  0.052                     0.014
net_pair       0.490               0.480                  0.087                     0.044
```
