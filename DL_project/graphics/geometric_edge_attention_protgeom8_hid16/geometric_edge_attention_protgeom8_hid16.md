# geometric_edge_attention_protgeom8_hid16

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_attention_protgeom8_hid16'
rows: 21

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.8060      0.4208      0.8162      0.7008      0.7811      0.3656
groups_GLTP            3      0.3600      0.7467      0.6322      0.5712      0.2949      0.8590
groups_IP_trans        3      0.2174      0.8511      0.7034      0.6079      0.4028      0.8723
groups_LBP_BPI_CETP    3      0.0725      0.9716      0.6916      0.6624      0.1111      0.9574
groups_START           3      0.6051      0.4719      0.8271      0.5216      0.6250      0.4494
groups_lipocalin       3      0.7778      0.4213      0.7920      0.4781      0.8704      0.3935
groups_scp2            3      0.3922      0.7157      0.7584      0.5710      0.5490      0.7843
ALL                   21      0.4616      0.6570      0.7458      0.5876      0.5192      0.6688

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5940      0.6033     0.0772  21
max valid BA                0.6782      0.7057     0.0802  21
best valid F1               0.6502      0.6486     0.0535  21
test BA                     0.5593      0.5657     0.0664  21
test F1                     0.4166      0.4706     0.2043  21
test sensitivity            0.4616      0.4706     0.3130  21
test specificity            0.6570      0.7361     0.2754  21
test precision              0.4760      0.4706     0.1764  21
test loss                   0.8958      0.6958     0.7609  21
FPR (FP/(FP+TN))            0.3430      0.2639     0.2754  21
FNR (FN/(FN+TP))            0.5384      0.5294     0.3130  21

=== abs(sensitivity-specificity) gap: mean=0.5241 median=0.5677 n=21 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5733      0.5929     0.0461  3
  max valid BA                0.5919      0.6064     0.0508  3
  best valid F1               0.6959      0.7052     0.0294  3
  test BA                     0.6134      0.6117     0.0227  3
  test F1                     0.6899      0.6792     0.0212  3
  test sensitivity            0.8060      0.8060     0.0896  3
  test specificity            0.4208      0.3770     0.1208  3
  test precision              0.6070      0.5941     0.0288  3
  test loss                   0.7674      0.7148     0.1109  3
  FPR (FP/(FP+TN))            0.5792      0.6230     0.1208  3
  FNR (FN/(FN+TP))            0.1940      0.1940     0.0896  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5769      0.5769     0.0385  3
  max valid BA                0.6410      0.5769     0.1110  3
  best valid F1               0.6738      0.6757     0.0414  3
  test BA                     0.5533      0.5600     0.0902  3
  test F1                     0.4434      0.4706     0.0472  3
  test sensitivity            0.3600      0.3200     0.1058  3
  test specificity            0.7467      0.8400     0.2723  3
  test precision              0.6623      0.6364     0.2148  3
  test loss                   0.7070      0.7018     0.0146  3
  FPR (FP/(FP+TN))            0.2533      0.1600     0.2723  3
  FNR (FN/(FN+TP))            0.6400      0.6800     0.1058  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6376      0.6037     0.0590  3
  max valid BA                0.7339      0.7057     0.0681  3
  best valid F1               0.6545      0.6154     0.0882  3
  test BA                     0.5342      0.5333     0.0439  3
  test F1                     0.2691      0.2069     0.1301  3
  test sensitivity            0.2174      0.1304     0.1506  3
  test specificity            0.8511      0.8511     0.0851  3
  test precision              0.4167      0.4500     0.1041  3
  test loss                   0.6172      0.6083     0.0431  3
  FPR (FP/(FP+TN))            0.1489      0.1489     0.0851  3
  FNR (FN/(FN+TP))            0.7826      0.8696     0.1506  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5343      0.5310     0.0060  3
  max valid BA                0.6928      0.7070     0.0633  3
  best valid F1               0.5963      0.6047     0.0749  3
  test BA                     0.5220      0.5111     0.0393  3
  test F1                     0.1186      0.0800     0.1419  3
  test sensitivity            0.0725      0.0435     0.0905  3
  test specificity            0.9716      0.9787     0.0123  3
  test precision              0.3889      0.5000     0.3469  3
  test loss                   1.9710      1.1316     1.9099  3
  FPR (FP/(FP+TN))            0.0284      0.0213     0.0123  3
  FNR (FN/(FN+TP))            0.9275      0.9565     0.0905  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5372      0.5523     0.1053  3
  max valid BA                0.6078      0.5985     0.0471  3
  best valid F1               0.6212      0.6058     0.0364  3
  test BA                     0.5385      0.5280     0.0721  3
  test F1                     0.4730      0.5444     0.2171  3
  test sensitivity            0.6051      0.7077     0.3947  3
  test specificity            0.4719      0.3483     0.2642  3
  test precision              0.4297      0.4423     0.0694  3
  test loss                   0.7959      0.7006     0.1793  3
  FPR (FP/(FP+TN))            0.5281      0.6517     0.2642  3
  FNR (FN/(FN+TP))            0.3949      0.2923     0.3947  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6319      0.7014     0.1203  3
  max valid BA                0.7546      0.7639     0.0223  3
  best valid F1               0.6713      0.6800     0.0225  3
  test BA                     0.5995      0.6458     0.1116  3
  test F1                     0.5374      0.5333     0.0607  3
  test sensitivity            0.7778      0.8333     0.2003  3
  test specificity            0.4213      0.5278     0.3794  3
  test precision              0.4341      0.4688     0.1006  3
  test loss                   0.6718      0.6945     0.0874  3
  FPR (FP/(FP+TN))            0.5787      0.4722     0.3794  3
  FNR (FN/(FN+TP))            0.2222      0.1667     0.2003  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6667      0.6618     0.0516  3
  max valid BA                0.7255      0.7353     0.0170  3
  best valid F1               0.6383      0.6471     0.0167  3
  test BA                     0.5539      0.5735     0.0612  3
  test F1                     0.3848      0.4615     0.1409  3
  test sensitivity            0.3922      0.4706     0.1891  3
  test specificity            0.7157      0.7353     0.0899  3
  test precision              0.3932      0.4091     0.0864  3
  test loss                   0.7403      0.6690     0.1810  3
  FPR (FP/(FP+TN))            0.2843      0.2647     0.0899  3
  FNR (FN/(FN+TP))            0.6078      0.5294     0.1891  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.475    0.588     4.000              0.348         0.490   5.000               0.467          0.622
GLTP                     0.595         0.484    0.422     2.000              0.488         0.436   3.000               0.494          0.407
IP_trans                 0.727         0.726    0.624     3.000              0.719         0.666   2.667               0.664          0.562
LBP_BPI_CETP             0.721         0.811    0.671     2.000              0.812         0.691   1.667               0.792          0.577
START                    0.574         0.487    0.555     3.000              0.461         0.508   4.000               0.517          0.646
lipocalin                0.558         0.302    0.550     5.000              0.222         0.501   2.000               0.681          0.583
scp2                     0.632         0.430    0.739     2.667              0.528         0.637   2.667               0.630          0.693

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.531               0.487                  0.032                     0.176
net_AUC           0.593               0.607                  0.103                     0.101

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.472                  0.041                     0.203
net_AUC_prot           0.561               0.541                  0.109                     0.101

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.606               0.581                  0.084                     0.119
net_AUC_lipid           0.584               0.603                  0.092                     0.090

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.531  0.500      0.511     0.484
10     0.531  0.598      0.511     0.599
49     0.531  0.599      0.511     0.573
51     0.531  0.595      0.511     0.571
120    0.531  0.593      0.511     0.561

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.623         0.658      0.035          0.656              0.686           0.030
10        0.623         0.686      0.063          0.656              0.704           0.048
49        0.623         0.664      0.041          0.656              0.693           0.037
51        0.623         0.676      0.052          0.656              0.696           0.040
120       0.623         0.696      0.073          0.656              0.712           0.056

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.475  0.588      0.348     0.490     0.525         0.616      0.091          0.589              0.660           0.070
GLTP          0.484  0.422      0.488     0.436     0.519         0.656      0.137          0.547              0.640           0.092
IP_trans      0.726  0.624      0.719     0.666     0.726         0.750      0.024          0.729              0.753           0.024
LBP_BPI_CETP  0.811  0.671      0.812     0.691     0.811         0.823      0.012          0.815              0.829           0.014
START         0.487  0.555      0.461     0.508     0.513         0.606      0.093          0.559              0.637           0.078
lipocalin     0.302  0.550      0.222     0.501     0.698         0.760      0.062          0.696              0.762           0.066
scp2          0.430  0.739      0.528     0.637     0.570         0.663      0.092          0.655              0.706           0.051

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.531               0.487                  0.032                     0.176
net               0.593               0.607                  0.103                     0.101
fit_chem          0.623               0.580                  0.031                     0.120
fit_chem_net      0.696               0.708                  0.053                     0.082
increment         0.073               0.063                  0.055                     0.044

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.472                  0.041                     0.203
net_prot               0.561               0.541                  0.109                     0.101
fit_chem_prot          0.656               0.655                  0.032                     0.098
fit_chem_net_prot      0.712               0.715                  0.061                     0.072
increment_prot         0.056               0.033                  0.054                     0.029
```
