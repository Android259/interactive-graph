# geometric_edge_mlp_protgeom_full_lcs

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_full_lcs'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6323      0.3550      0.5589      0.5029      0.7355      0.3788
groups_choline            5      0.4414      0.6623      0.5499      0.4905      0.5607      0.6643
groups_phosphorus_free    5      0.4258      0.7088      0.6108      0.4455      0.6067      0.6857
groups_sphingolipids      5      0.4000      0.6436      0.5577      0.4629      0.5758      0.6185
ALL                      20      0.4749      0.5924      0.5693      0.4755      0.6197      0.5868

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5578      0.5427     0.0470  20
max valid BA                0.6032      0.5905     0.0493  20
best valid F1               0.5717      0.5625     0.0322  20
test BA                     0.5336      0.5319     0.0541  20
test AUC                    0.5341      0.5283     0.0975  20
test AUC in-protein         0.5284      0.5209     0.1025  20
  (proteins averaged)       7.9000      8.5000     3.5968  20
test AUC in-protein (pairs)      0.5464      0.5635     0.1016  20
  (proteins contributing)     11.7000     14.0000     5.3024  20
test F1                     0.4010      0.4202     0.1483  20
test sensitivity            0.4749      0.4278     0.2961  20
test specificity            0.5924      0.6746     0.3251  20
test precision              0.4827      0.4094     0.1746  19
test loss                  24.2485      1.5548    59.0218  20
FPR (FP/(FP+TN))            0.4076      0.3254     0.3251  20
FNR (FN/(FN+TP))            0.5251      0.5722     0.2961  20

=== abs(sensitivity-specificity) gap: mean=0.5410 median=0.5784 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5262      0.5211     0.0224  5
  max valid BA                0.5571      0.5581     0.0181  5
  best valid F1               0.5617      0.5613     0.0097  5
  test BA                     0.4936      0.5000     0.0352  5
  test AUC                    0.4943      0.5151     0.0573  5
  test AUC in-protein         0.4899      0.4942     0.0380  5
    (proteins averaged)      12.2000     12.0000     0.4472  5
  test AUC in-protein (pairs)      0.5220      0.5291     0.0736  5
    (proteins contributing)     16.4000     17.0000     1.5166  5
  test F1                     0.4030      0.5279     0.2327  5
  test sensitivity            0.6323      0.7634     0.3942  5
  test specificity            0.3550      0.3046     0.3867  5
  test precision              0.3738      0.3805     0.0306  4
  test loss                  88.2077     33.3797    98.1142  5
  FPR (FP/(FP+TN))            0.6450      0.6954     0.3867  5
  FNR (FN/(FN+TP))            0.3677      0.2366     0.3942  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5494      0.5283     0.0405  5
  max valid BA                0.6125      0.5848     0.0420  5
  best valid F1               0.5889      0.5879     0.0379  5
  test BA                     0.5519      0.5436     0.0426  5
  test AUC                    0.5969      0.6547     0.1139  5
  test AUC in-protein         0.5757      0.5908     0.1139  5
    (proteins averaged)       9.8000     10.0000     0.4472  5
  test AUC in-protein (pairs)      0.5743      0.6088     0.1122  5
    (proteins contributing)     14.8000     15.0000     0.4472  5
  test F1                     0.4000      0.4370     0.1718  5
  test sensitivity            0.4414      0.4685     0.3327  5
  test specificity            0.6623      0.6946     0.3467  5
  test precision              0.5638      0.5446     0.1566  5
  test loss                   4.9796      0.8554     9.3298  5
  FPR (FP/(FP+TN))            0.3377      0.3054     0.3467  5
  FNR (FN/(FN+TP))            0.5586      0.5315     0.3327  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5939      0.5637     0.0608  5
  max valid BA                0.6462      0.6262     0.0547  5
  best valid F1               0.5648      0.5545     0.0491  5
  test BA                     0.5673      0.5501     0.0723  5
  test AUC                    0.5906      0.5688     0.0798  5
  test AUC in-protein         0.6075      0.5561     0.1037  5
    (proteins averaged)       6.6000      7.0000     1.1402  5
  test AUC in-protein (pairs)      0.6212      0.5748     0.1095  5
    (proteins contributing)     12.2000     13.0000     2.1679  5
  test F1                     0.4188      0.4000     0.1161  5
  test sensitivity            0.4258      0.3548     0.2554  5
  test specificity            0.7088      0.7018     0.2604  5
  test precision              0.5215      0.4138     0.2729  5
  test loss                   1.9290      0.7763     2.0849  5
  FPR (FP/(FP+TN))            0.2912      0.2982     0.2604  5
  FNR (FN/(FN+TP))            0.5742      0.6452     0.2554  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5616      0.5438     0.0409  5
  max valid BA                0.5971      0.6019     0.0369  5
  best valid F1               0.5713      0.5664     0.0207  5
  test BA                     0.5218      0.5061     0.0403  5
  test AUC                    0.4544      0.4601     0.0609  5
  test AUC in-protein         0.4405      0.4274     0.0511  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4681      0.4426     0.0512  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.3821      0.3478     0.0806  5
  test sensitivity            0.4000      0.3030     0.2071  5
  test specificity            0.6436      0.6545     0.2605  5
  test precision              0.4501      0.3793     0.1196  5
  test loss                   1.8776      0.7183     1.8226  5
  FPR (FP/(FP+TN))            0.3564      0.3455     0.2605  5
  FNR (FN/(FN+TP))            0.6000      0.6970     0.2071  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.491      11.6              0.530         0.406     5.4               0.501          0.618              0.501         0.541
choline                     0.687         0.646    0.497       9.4              0.696         0.489     1.8               0.565          0.519              0.622         0.494
phosphorus_free             0.396         0.499    0.434       1.2              0.739         0.392     5.4               0.514          0.606              0.484         0.467
sphingolipids               0.599         0.543    0.481       1.6              0.496         0.523     3.2               0.537          0.479              0.490         0.491

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.476               0.485                  0.066                     0.029

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.453               0.428                  0.056                     0.064

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.555               0.549                  0.121                     0.068

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.498               0.503                  0.067                     0.031

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.516  0.501      0.501     0.499
10     0.516  0.489      0.501     0.483
49     0.516  0.467      0.501     0.464
51     0.516  0.487      0.501     0.476
120    0.516  0.476      0.501     0.453

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.635      0.008          0.708              0.711           0.004
10        0.628         0.639      0.011          0.708              0.711           0.003
49        0.628         0.640      0.013          0.708              0.719           0.011
51        0.628         0.651      0.023          0.708              0.715           0.008
120       0.628         0.635      0.007          0.708              0.715           0.008

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.585  0.491      0.566     0.406     0.585         0.593      0.008          0.657              0.660           0.004
choline          0.671  0.497      0.671     0.489     0.671         0.676      0.005          0.767              0.775           0.008
phosphorus_free  0.289  0.434      0.289     0.392     0.711         0.717      0.006          0.772              0.778           0.006
sphingolipids    0.521  0.481      0.480     0.523     0.544         0.554      0.010          0.635              0.649           0.015

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.516               0.553                  0.041                     0.164
net               0.476               0.485                  0.066                     0.029
fit_chem          0.628               0.637                  0.034                     0.077
fit_chem_net      0.635               0.659                  0.030                     0.075
increment         0.007               0.001                  0.018                     0.002

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.501               0.527                  0.043                     0.162
net_prot               0.453               0.428                  0.056                     0.064
fit_chem_prot          0.708               0.701                  0.042                     0.072
fit_chem_net_prot      0.715               0.707                  0.039                     0.070
increment_prot         0.008              -0.000                  0.018                     0.005
```
