# descriptors_coarse

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_coarse'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4627      0.5410      0.6017      0.5651      0.5552      0.5871
groups_GLTP            5      0.4160      0.6160      0.5975      0.4765      0.4385      0.7077
groups_IP_trans        5      0.6261      0.5617      0.6380      0.4871      0.7500      0.5617
groups_LBP_BPI_CETP    5      0.8522      0.7277      0.6381      0.4840      0.8250      0.7191
groups_START           5      0.5754      0.4944      0.6840      0.4205      0.5969      0.5191
groups_lipocalin       5      0.6167      0.5667      0.6911      0.4602      0.6222      0.5639
groups_scp2            5      0.6471      0.4235      0.5841      0.5187      0.7176      0.4353
ALL                   35      0.5994      0.5616      0.6335      0.4875      0.6436      0.5848

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6131      0.5971     0.0859  35
max valid BA                0.6269      0.6096     0.0886  35
best valid F1               0.5846      0.5763     0.0962  35
test BA                     0.5805      0.5764     0.1108  35
test F1                     0.5042      0.5280     0.1380  35
test sensitivity            0.5994      0.6400     0.2476  35
test specificity            0.5616      0.5957     0.2091  35
test precision              0.4743      0.4706     0.1115  35
test loss                   0.6886      0.6912     0.0309  35
FPR (FP/(FP+TN))            0.4384      0.4043     0.2091  35
FNR (FN/(FN+TP))            0.4006      0.3600     0.2476  35

=== abs(sensitivity-specificity) gap: mean=0.3193 median=0.2800 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5712      0.5717     0.0352  5
  max valid BA                0.5853      0.5805     0.0235  5
  best valid F1               0.6356      0.6460     0.0508  5
  test BA                     0.5018      0.5084     0.0193  5
  test F1                     0.4852      0.5038     0.0740  5
  test sensitivity            0.4627      0.4925     0.1253  5
  test specificity            0.5410      0.5574     0.1159  5
  test precision              0.5246      0.5309     0.0230  5
  test loss                   0.6961      0.6947     0.0064  5
  FPR (FP/(FP+TN))            0.4590      0.4426     0.1159  5
  FNR (FN/(FN+TP))            0.5373      0.5075     0.1253  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5654      0.5577     0.0322  5
  max valid BA                0.5808      0.5769     0.0479  5
  best valid F1               0.5685      0.6452     0.1261  5
  test BA                     0.5160      0.5000     0.0684  5
  test F1                     0.4448      0.4186     0.1482  5
  test sensitivity            0.4160      0.3600     0.1951  5
  test specificity            0.6160      0.6400     0.1152  5
  test precision              0.5049      0.5000     0.0813  5
  test loss                   0.6966      0.7006     0.0130  5
  FPR (FP/(FP+TN))            0.3840      0.3600     0.1152  5
  FNR (FN/(FN+TP))            0.5840      0.6400     0.1951  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6559      0.6512     0.0503  5
  max valid BA                0.6709      0.6840     0.0513  5
  best valid F1               0.5942      0.6061     0.0383  5
  test BA                     0.5939      0.6147     0.0526  5
  test F1                     0.4751      0.5373     0.1218  5
  test sensitivity            0.6261      0.6957     0.2691  5
  test specificity            0.5617      0.5745     0.1852  5
  test precision              0.4055      0.4091     0.0457  5
  test loss                   0.6850      0.6886     0.0107  5
  FPR (FP/(FP+TN))            0.4383      0.4255     0.1852  5
  FNR (FN/(FN+TP))            0.3739      0.3043     0.2691  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7721      0.7668     0.0427  5
  max valid BA                0.7913      0.7682     0.0428  5
  best valid F1               0.7212      0.6909     0.0555  5
  test BA                     0.7899      0.7632     0.0735  5
  test F1                     0.7135      0.6800     0.0863  5
  test sensitivity            0.8522      0.8696     0.0728  5
  test specificity            0.7277      0.7872     0.1324  5
  test precision              0.6213      0.6296     0.1142  5
  test loss                   0.6512      0.6612     0.0303  5
  FPR (FP/(FP+TN))            0.2723      0.2128     0.1324  5
  FNR (FN/(FN+TP))            0.1478      0.1304     0.0728  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5580      0.5773     0.0912  5
  max valid BA                0.5644      0.6096     0.0940  5
  best valid F1               0.5578      0.5509     0.0458  5
  test BA                     0.5349      0.5960     0.0940  5
  test F1                     0.4985      0.5280     0.1138  5
  test sensitivity            0.5754      0.5385     0.2106  5
  test specificity            0.4944      0.5955     0.2659  5
  test precision              0.4632      0.4949     0.1006  5
  test loss                   0.7086      0.6998     0.0455  5
  FPR (FP/(FP+TN))            0.5056      0.4045     0.2659  5
  FNR (FN/(FN+TP))            0.4246      0.4615     0.2106  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5931      0.5972     0.0438  5
  max valid BA                0.6042      0.6042     0.0286  5
  best valid F1               0.5006      0.5238     0.0942  5
  test BA                     0.5917      0.5764     0.0362  5
  test F1                     0.4693      0.5303     0.1037  5
  test sensitivity            0.6167      0.6667     0.3295  5
  test specificity            0.5667      0.6250     0.3186  5
  test precision              0.4512      0.4583     0.0757  5
  test loss                   0.6726      0.6626     0.0235  5
  FPR (FP/(FP+TN))            0.4333      0.3750     0.3186  5
  FNR (FN/(FN+TP))            0.3833      0.3333     0.3295  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5765      0.5735     0.0319  5
  max valid BA                0.5912      0.6029     0.0408  5
  best valid F1               0.5140      0.5238     0.0414  5
  test BA                     0.5353      0.5441     0.0880  5
  test F1                     0.4428      0.5000     0.1471  5
  test sensitivity            0.6471      0.7059     0.2941  5
  test specificity            0.4235      0.5294     0.2293  5
  test precision              0.3496      0.3556     0.0998  5
  test loss                   0.7102      0.7130     0.0305  5
  FPR (FP/(FP+TN))            0.5765      0.4706     0.2293  5
  FNR (FN/(FN+TP))            0.3529      0.2941     0.2941  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = label_descriptors (aromatic_share,chain,hbond,heavy,occupancy,polar_share,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  null_AUC_pair_k15  net_AUC_pair
fam                                                                                   
CRAL-TRIO                0.425         0.548    0.538              0.542         0.539
GLTP                     0.424         0.685    0.527              0.667         0.528
IP_trans                 0.460         0.574    0.687              0.621         0.648
LBP_BPI_CETP             0.492         0.701    0.751              0.687         0.743
START                    0.421         0.463    0.529              0.473         0.551
lipocalin                0.363         0.645    0.509              0.652         0.703
scp2                     0.435         0.487    0.459              0.549         0.448

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.586               0.570                  0.061                     0.094
net_AUC           0.571               0.567                  0.075                     0.106

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.599               0.599                  0.061                     0.079
net_AUC_pair           0.595               0.596                  0.083                     0.106

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = pair_id ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_pair  net_pair
epoch                                   
1      0.586  0.513      0.599     0.527
10     0.586  0.576      0.599     0.595
49     0.586  0.576      0.599     0.601
51     0.586  0.573      0.599     0.599
120    0.586  0.571      0.599     0.595

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment
epoch                                   
1         0.607         0.673      0.067
10        0.607         0.672      0.065
49        0.607         0.664      0.058
51        0.607         0.664      0.058
120       0.607         0.662      0.055

3. mean over seeds, epoch 120
               chem    net  chem_pair  net_pair  fit_chem  fit_chem_net  increment
fam                                                                               
CRAL-TRIO     0.548  0.538      0.542     0.539     0.555         0.566      0.011
GLTP          0.685  0.527      0.667     0.528     0.680         0.709      0.029
IP_trans      0.574  0.687      0.621     0.648     0.574         0.730      0.156
LBP_BPI_CETP  0.701  0.751      0.687     0.743     0.701         0.775      0.073
START         0.463  0.529      0.473     0.551     0.546         0.593      0.047
lipocalin     0.645  0.509      0.652     0.703     0.645         0.671      0.026
scp2          0.487  0.459      0.549     0.448     0.547         0.589      0.042

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.586               0.570                  0.061                     0.094
net               0.571               0.567                  0.075                     0.106
fit_chem          0.607               0.582                  0.055                     0.067
fit_chem_net      0.662               0.651                  0.054                     0.081
increment         0.055               0.040                  0.052                     0.049

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc), epoch 120 ===
           all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_pair      0.599               0.599                  0.061                     0.079
net_pair       0.595               0.596                  0.083                     0.106
```
