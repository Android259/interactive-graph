# geometric_edge_mlp_protgeom8_normalized

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom8_normalized'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6627      0.4689      0.6314      0.6372      0.7224      0.4548
groups_GLTP            5      0.5440      0.3600      0.6949      0.5417      0.7000      0.5615
groups_IP_trans        5      0.6696      0.6426      0.7537      0.6011      0.7250      0.6298
groups_LBP_BPI_CETP    5      0.4087      0.8638      0.6773      0.5992      0.4917      0.8511
groups_START           5      0.6738      0.5775      0.8710      0.6065      0.7281      0.5191
groups_lipocalin       5      0.8667      0.4222      0.6428      0.5113      0.8333      0.4889
groups_scp2            5      0.5294      0.6647      0.8022      0.6170      0.6000      0.7294
ALL                   35      0.6221      0.5714      0.7248      0.5877      0.6858      0.6049

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6454      0.6324     0.0688  35
max valid BA                0.6729      0.6559     0.0664  35
best valid F1               0.6312      0.6415     0.1080  35
test BA                     0.5968      0.6029     0.0941  35
test F1                     0.5269      0.5574     0.1336  35
test sensitivity            0.6221      0.6923     0.2404  35
test specificity            0.5714      0.5556     0.2283  35
test precision              0.5059      0.5128     0.0808  35
test loss                   0.6916      0.6891     0.0583  35
FPR (FP/(FP+TN))            0.4286      0.4444     0.2283  35
FNR (FN/(FN+TP))            0.3779      0.3077     0.2404  35

=== abs(sensitivity-specificity) gap: mean=0.3544 median=0.3352 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5886      0.6091     0.0379  5
  max valid BA                0.6202      0.6208     0.0220  5
  best valid F1               0.6931      0.7065     0.0399  5
  test BA                     0.5658      0.5646     0.0417  5
  test F1                     0.6124      0.6259     0.0462  5
  test sensitivity            0.6627      0.6866     0.1495  5
  test specificity            0.4689      0.4426     0.2149  5
  test precision              0.5918      0.5747     0.0684  5
  test loss                   0.7024      0.6916     0.0297  5
  FPR (FP/(FP+TN))            0.5311      0.5574     0.2149  5
  FNR (FN/(FN+TP))            0.3373      0.3134     0.1495  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6308      0.6346     0.0251  5
  max valid BA                0.6615      0.6538     0.0554  5
  best valid F1               0.7155      0.7273     0.0322  5
  test BA                     0.4520      0.4200     0.0729  5
  test F1                     0.4871      0.4918     0.0908  5
  test sensitivity            0.5440      0.6000     0.1889  5
  test specificity            0.3600      0.2400     0.2400  5
  test precision              0.4684      0.4412     0.0719  5
  test loss                   0.7132      0.7130     0.0598  5
  FPR (FP/(FP+TN))            0.6400      0.7600     0.2400  5
  FNR (FN/(FN+TP))            0.4560      0.4000     0.1889  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6774      0.6618     0.0671  5
  max valid BA                0.7071      0.6822     0.0581  5
  best valid F1               0.6204      0.6111     0.0671  5
  test BA                     0.6561      0.6563     0.0774  5
  test F1                     0.5279      0.5614     0.1601  5
  test sensitivity            0.6696      0.7391     0.2894  5
  test specificity            0.6426      0.6170     0.1492  5
  test precision              0.4735      0.4706     0.0335  5
  test loss                   0.6789      0.6758     0.0855  5
  FPR (FP/(FP+TN))            0.3574      0.3830     0.1492  5
  FNR (FN/(FN+TP))            0.3304      0.2609     0.2894  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6714      0.6543     0.1234  5
  max valid BA                0.6832      0.6640     0.1191  5
  best valid F1               0.5358      0.5714     0.2365  5
  test BA                     0.6363      0.6101     0.1052  5
  test F1                     0.4294      0.4324     0.2343  5
  test sensitivity            0.4087      0.3478     0.3099  5
  test specificity            0.8638      0.8723     0.1016  5
  test precision              0.5831      0.5714     0.0606  5
  test loss                   0.6333      0.6255     0.0305  5
  FPR (FP/(FP+TN))            0.1362      0.1277     0.1016  5
  FNR (FN/(FN+TP))            0.5913      0.6522     0.3099  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6236      0.6212     0.0243  5
  max valid BA                0.6487      0.6559     0.0411  5
  best valid F1               0.6402      0.6358     0.0252  5
  test BA                     0.6257      0.6170     0.0421  5
  test F1                     0.5911      0.6000     0.0776  5
  test sensitivity            0.6738      0.7077     0.1589  5
  test specificity            0.5775      0.5506     0.1188  5
  test precision              0.5405      0.5294     0.0337  5
  test loss                   0.6923      0.6815     0.0757  5
  FPR (FP/(FP+TN))            0.4225      0.4494     0.1188  5
  FNR (FN/(FN+TP))            0.3262      0.2923     0.1589  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6611      0.7014     0.0818  5
  max valid BA                0.7042      0.7292     0.0607  5
  best valid F1               0.6204      0.6410     0.0569  5
  test BA                     0.6444      0.6250     0.0944  5
  test F1                     0.5792      0.5667     0.0717  5
  test sensitivity            0.8667      0.9444     0.1201  5
  test specificity            0.4222      0.4861     0.2241  5
  test precision              0.4425      0.4127     0.0807  5
  test loss                   0.7089      0.7068     0.0355  5
  FPR (FP/(FP+TN))            0.5778      0.5139     0.2241  5
  FNR (FN/(FN+TP))            0.1333      0.0556     0.1201  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6647      0.6324     0.0583  5
  max valid BA                0.6853      0.6471     0.0603  5
  best valid F1               0.5931      0.5652     0.0707  5
  test BA                     0.5971      0.5882     0.0526  5
  test F1                     0.4611      0.4878     0.1127  5
  test sensitivity            0.5294      0.5882     0.2353  5
  test specificity            0.6647      0.5882     0.1465  5
  test precision              0.4413      0.4231     0.0410  5
  test loss                   0.7123      0.7422     0.0557  5
  FPR (FP/(FP+TN))            0.3353      0.4118     0.1465  5
  FNR (FN/(FN+TP))            0.4706      0.4118     0.2353  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.630         0.483    0.551       4.0              0.365         0.478     5.0               0.449          0.606
GLTP                     0.605         0.521    0.573       2.0              0.511         0.562     3.0               0.523          0.584
IP_trans                 0.722         0.681    0.639       3.0              0.677         0.703     2.4               0.590          0.555
LBP_BPI_CETP             0.719         0.798    0.656       2.0              0.798         0.656     1.6               0.784          0.635
START                    0.576         0.508    0.617       3.0              0.475         0.555     4.0               0.535          0.570
lipocalin                0.565         0.334    0.439       5.0              0.252         0.410     2.2               0.647          0.426
scp2                     0.651         0.488    0.670       2.8              0.592         0.630     2.6               0.649          0.601

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.545               0.499                  0.066                     0.151
net_AUC           0.592               0.624                  0.112                     0.080

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.524               0.493                  0.065                     0.185
net_AUC_prot           0.571               0.573                  0.138                     0.102

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.597               0.581                  0.085                     0.109
net_AUC_lipid           0.568               0.547                  0.124                     0.068

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.490      0.524     0.499
10     0.545  0.562      0.524     0.551
49     0.545  0.577      0.524     0.555
51     0.545  0.581      0.524     0.553
120    0.545  0.592      0.524     0.571

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.619         0.674      0.055          0.655              0.696           0.041
10        0.619         0.666      0.047          0.655              0.691           0.036
49        0.619         0.683      0.064          0.655              0.696           0.041
51        0.619         0.671      0.051          0.655              0.689           0.034
120       0.619         0.684      0.065          0.655              0.720           0.065

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.483  0.551      0.365     0.478     0.539         0.567      0.027          0.614              0.631           0.017
GLTP          0.521  0.573      0.511     0.562     0.542         0.622      0.080          0.565              0.657           0.092
IP_trans      0.681  0.639      0.677     0.703     0.681         0.726      0.046          0.692              0.738           0.046
LBP_BPI_CETP  0.798  0.656      0.798     0.656     0.798         0.808      0.010          0.801              0.809           0.008
START         0.508  0.617      0.475     0.555     0.536         0.666      0.130          0.604              0.695           0.090
lipocalin     0.334  0.439      0.252     0.410     0.666         0.743      0.077          0.672              0.796           0.125
scp2          0.488  0.670      0.592     0.630     0.572         0.659      0.087          0.636              0.713           0.077

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.545               0.499                  0.066                     0.151
net               0.592               0.624                  0.112                     0.080
fit_chem          0.619               0.580                  0.052                     0.100
fit_chem_net      0.684               0.699                  0.060                     0.081
increment         0.065               0.048                  0.049                     0.041

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.524               0.493                  0.065                     0.185
net_prot               0.571               0.573                  0.138                     0.102
fit_chem_prot          0.655               0.658                  0.053                     0.077
fit_chem_net_prot      0.720               0.705                  0.063                     0.067
increment_prot         0.065               0.052                  0.051                     0.043
```
