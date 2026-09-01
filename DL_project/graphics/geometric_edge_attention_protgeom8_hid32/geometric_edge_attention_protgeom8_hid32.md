# geometric_edge_attention_protgeom8_hid32

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_attention_protgeom8_hid32'
rows: 21

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.5771      0.6448      0.6981      0.6873      0.5572      0.7097
groups_GLTP            3      0.4800      0.6000      0.8290      0.6988      0.6410      0.5897
groups_IP_trans        3      0.6232      0.6879      0.6924      0.6203      0.7639      0.6383
groups_LBP_BPI_CETP    3      0.2319      0.8865      0.6495      0.5816      0.2917      0.8936
groups_START           3      0.7282      0.5243      0.8510      0.6581      0.7188      0.5206
groups_lipocalin       3      0.7963      0.5093      0.7961      0.5591      0.7963      0.4954
groups_scp2            3      0.5882      0.6667      0.6961      0.5971      0.6667      0.7255
ALL                   21      0.5750      0.6456      0.7446      0.6289      0.6336      0.6533

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6435      0.6454     0.0663  21
max valid BA                0.7043      0.7057     0.0621  21
best valid F1               0.6576      0.6667     0.0830  21
test BA                     0.6103      0.6195     0.0732  21
test F1                     0.5133      0.5254     0.1660  21
test sensitivity            0.5750      0.6418     0.2386  21
test specificity            0.6456      0.6383     0.1700  21
test precision              0.4953      0.5000     0.1445  21
test loss                   0.7028      0.6663     0.1089  21
FPR (FP/(FP+TN))            0.3544      0.3617     0.1700  21
FNR (FN/(FN+TP))            0.4250      0.3582     0.2386  21

=== abs(sensitivity-specificity) gap: mean=0.2903 median=0.2059 n=21 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6334      0.6279     0.0318  3
  max valid BA                0.6394      0.6459     0.0320  3
  best valid F1               0.7040      0.7052     0.0162  3
  test BA                     0.6110      0.6078     0.0075  3
  test F1                     0.5998      0.6324     0.0702  3
  test sensitivity            0.5771      0.6418     0.1525  3
  test specificity            0.6448      0.5738     0.1674  3
  test precision              0.6554      0.6232     0.0645  3
  test loss                   0.6667      0.6656     0.0056  3
  FPR (FP/(FP+TN))            0.3552      0.4262     0.1674  3
  FNR (FN/(FN+TP))            0.4229      0.3582     0.1525  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6154      0.5962     0.0693  3
  max valid BA                0.7244      0.7692     0.1309  3
  best valid F1               0.7597      0.7600     0.0929  3
  test BA                     0.5400      0.5000     0.1249  3
  test F1                     0.4667      0.4444     0.2563  3
  test sensitivity            0.4800      0.4000     0.3666  3
  test specificity            0.6000      0.6000     0.1200  3
  test precision              0.4974      0.5000     0.1325  3
  test loss                   0.7805      0.7519     0.0816  3
  FPR (FP/(FP+TN))            0.4000      0.4000     0.1200  3
  FNR (FN/(FN+TP))            0.5200      0.6000     0.3666  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7011      0.7159     0.0444  3
  max valid BA                0.7256      0.7261     0.0197  3
  best valid F1               0.6448      0.6429     0.0209  3
  test BA                     0.6556      0.6540     0.0112  3
  test F1                     0.5485      0.5455     0.0264  3
  test sensitivity            0.6232      0.6522     0.1328  3
  test specificity            0.6879      0.6383     0.1247  3
  test precision              0.5066      0.4722     0.0626  3
  test loss                   0.6373      0.6509     0.0302  3
  FPR (FP/(FP+TN))            0.3121      0.3617     0.1247  3
  FNR (FN/(FN+TP))            0.3768      0.3478     0.1328  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5926      0.6126     0.0651  3
  max valid BA                0.6721      0.6454     0.0562  3
  best valid F1               0.5331      0.4737     0.1057  3
  test BA                     0.5592      0.5555     0.0718  3
  test F1                     0.2677      0.3030     0.2519  3
  test sensitivity            0.2319      0.2174     0.2395  3
  test specificity            0.8865      0.8936     0.0959  3
  test precision              0.3413      0.5000     0.2958  3
  test loss                   0.7771      0.7679     0.2594  3
  FPR (FP/(FP+TN))            0.1135      0.1064     0.0959  3
  FNR (FN/(FN+TP))            0.7681      0.7826     0.2395  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6197      0.6227     0.0300  3
  max valid BA                0.7018      0.6930     0.0242  3
  best valid F1               0.6605      0.6667     0.0257  3
  test BA                     0.6263      0.5804     0.0964  3
  test F1                     0.6103      0.6077     0.1007  3
  test sensitivity            0.7282      0.8000     0.1659  3
  test specificity            0.5243      0.5843     0.1871  3
  test precision              0.5341      0.4861     0.0936  3
  test loss                   0.7075      0.7590     0.0925  3
  FPR (FP/(FP+TN))            0.4757      0.4157     0.1871  3
  FNR (FN/(FN+TP))            0.2718      0.2000     0.1659  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6458      0.6597     0.1049  3
  max valid BA                0.7269      0.7222     0.0488  3
  best valid F1               0.6449      0.6400     0.0495  3
  test BA                     0.6528      0.6667     0.0705  3
  test F1                     0.5789      0.5833     0.0514  3
  test sensitivity            0.7963      0.7778     0.0578  3
  test specificity            0.5093      0.5556     0.1985  3
  test precision              0.4616      0.4667     0.0811  3
  test loss                   0.6939      0.6862     0.0763  3
  FPR (FP/(FP+TN))            0.4907      0.4444     0.1985  3
  FNR (FN/(FN+TP))            0.2037      0.2222     0.0578  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6961      0.7206     0.0695  3
  max valid BA                0.7402      0.7500     0.0449  3
  best valid F1               0.6565      0.6667     0.0521  3
  test BA                     0.6275      0.6324     0.0225  3
  test F1                     0.5214      0.5143     0.0258  3
  test sensitivity            0.5882      0.5882     0.0588  3
  test specificity            0.6667      0.6471     0.0612  3
  test precision              0.4710      0.4783     0.0332  3
  test loss                   0.6564      0.6628     0.0142  3
  FPR (FP/(FP+TN))            0.3333      0.3529     0.0612  3
  FNR (FN/(FN+TP))            0.4118      0.4118     0.0588  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.475    0.515     4.000              0.348         0.416   5.000               0.467          0.575
GLTP                     0.595         0.484    0.464     2.000              0.488         0.471   3.000               0.494          0.440
IP_trans                 0.727         0.726    0.729     3.000              0.719         0.768   2.667               0.664          0.677
LBP_BPI_CETP             0.721         0.811    0.683     2.000              0.812         0.637   1.667               0.792          0.600
START                    0.574         0.487    0.507     3.000              0.461         0.478   4.000               0.517          0.595
lipocalin                0.558         0.302    0.650     5.000              0.222         0.665   2.000               0.681          0.594
scp2                     0.632         0.430    0.748     2.667              0.528         0.621   2.667               0.630          0.709

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.531               0.487                  0.032                     0.176
net_AUC           0.614               0.625                  0.085                     0.116

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.472                  0.041                     0.203
net_AUC_prot           0.580               0.500                  0.099                     0.127

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.606               0.581                  0.084                     0.119
net_AUC_lipid           0.598               0.613                  0.132                     0.086

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.531  0.520      0.511     0.502
10     0.531  0.590      0.511     0.554
49     0.531  0.625      0.511     0.600
51     0.531  0.626      0.511     0.594
120    0.531  0.614      0.511     0.580

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.623         0.662      0.039          0.656              0.696           0.040
10        0.623         0.668      0.045          0.656              0.696           0.040
49        0.623         0.698      0.075          0.656              0.719           0.063
51        0.623         0.693      0.070          0.656              0.715           0.059
120       0.623         0.674      0.051          0.656              0.699           0.043

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.475  0.515      0.348     0.416     0.525         0.568      0.043          0.589              0.634           0.045
GLTP          0.484  0.464      0.488     0.471     0.519         0.568      0.048          0.547              0.586           0.039
IP_trans      0.726  0.729      0.719     0.768     0.726         0.759      0.033          0.729              0.772           0.043
LBP_BPI_CETP  0.811  0.683      0.812     0.637     0.811         0.825      0.014          0.815              0.827           0.012
START         0.487  0.507      0.461     0.478     0.513         0.586      0.073          0.559              0.603           0.043
lipocalin     0.302  0.650      0.222     0.665     0.698         0.757      0.059          0.696              0.769           0.073
scp2          0.430  0.748      0.528     0.621     0.570         0.657      0.086          0.655              0.704           0.050

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.531               0.487                  0.032                     0.176
net               0.614               0.625                  0.085                     0.116
fit_chem          0.623               0.580                  0.031                     0.120
fit_chem_net      0.674               0.660                  0.037                     0.106
increment         0.051               0.041                  0.030                     0.024

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.472                  0.041                     0.203
net_prot               0.580               0.500                  0.099                     0.127
fit_chem_prot          0.656               0.655                  0.032                     0.098
fit_chem_net_prot      0.699               0.718                  0.033                     0.094
increment_prot         0.043               0.041                  0.030                     0.018
```
