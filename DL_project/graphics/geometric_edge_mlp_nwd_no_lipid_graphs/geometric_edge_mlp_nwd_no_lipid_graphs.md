# geometric_edge_mlp_nwd_no_lipid_graphs

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_nwd_no_lipid_graphs'
rows: 19

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.5622      0.4645      0.7324      0.7541      0.5721      0.5215
groups_GLTP            3      0.3467      0.8533      0.7075      0.6506      0.2564      0.8590
groups_IP_trans        3      0.3913      0.7660      0.8724      0.6938      0.5972      0.7518
groups_LBP_BPI_CETP    2      0.3261      0.8723      0.8737      0.7610      0.3333      0.8511
groups_START           3      0.2718      0.7491      0.7520      0.6871      0.3177      0.7378
groups_lipocalin       2      0.5000      0.5000      0.7018      0.3379      0.5000      0.5000
groups_scp2            3      0.5098      0.5392      0.8129      0.7194      0.5294      0.6176
ALL                   19      0.4157      0.6769      0.7780      0.6691      0.4466      0.6929

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5698      0.5588     0.0681  19
max valid BA                0.6034      0.5959     0.0771  19
best valid F1               0.5482      0.5283     0.1112  19
test BA                     0.5463      0.5231     0.0670  19
test F1                     0.3704      0.4138     0.2193  19
test sensitivity            0.4157      0.3529     0.3220  19
test specificity            0.6769      0.7872     0.3190  19
test precision              0.4962      0.4844     0.1209  16
test loss                   0.7633      0.6970     0.1341  19
FPR (FP/(FP+TN))            0.3231      0.2128     0.3190  19
FNR (FN/(FN+TP))            0.5843      0.6471     0.3220  19

=== abs(sensitivity-specificity) gap: mean=0.5845 median=0.6984 n=19 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5468      0.5367     0.0345  3
  max valid BA                0.5830      0.5909     0.0394  3
  best valid F1               0.6731      0.6848     0.0354  3
  test BA                     0.5133      0.5044     0.0160  3
  test F1                     0.4766      0.6093     0.2810  3
  test sensitivity            0.5622      0.6866     0.4243  3
  test specificity            0.4645      0.3770     0.4168  3
  test precision              0.5396      0.5455     0.0120  3
  test loss                   0.7780      0.6936     0.1493  3
  FPR (FP/(FP+TN))            0.5355      0.6230     0.4168  3
  FNR (FN/(FN+TP))            0.4378      0.3134     0.4243  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5577      0.5192     0.0838  3
  max valid BA                0.6026      0.6154     0.0777  3
  best valid F1               0.4969      0.4615     0.1675  3
  test BA                     0.6000      0.5600     0.1249  3
  test F1                     0.3587      0.3125     0.3839  3
  test sensitivity            0.3467      0.2000     0.4388  3
  test specificity            0.8533      0.9200     0.1890  3
  test precision              0.7071      0.7071     0.0101  2
  test loss                   0.6785      0.6937     0.0283  3
  FPR (FP/(FP+TN))            0.1467      0.0800     0.1890  3
  FNR (FN/(FN+TP))            0.6533      0.8000     0.4388  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6745      0.6729     0.0517  3
  max valid BA                0.7196      0.7371     0.0396  3
  best valid F1               0.6362      0.6557     0.0436  3
  test BA                     0.5786      0.5675     0.0618  3
  test F1                     0.3927      0.3902     0.1515  3
  test sensitivity            0.3913      0.3478     0.2421  3
  test specificity            0.7660      0.7872     0.1185  3
  test precision              0.4377      0.4444     0.0349  3
  test loss                   0.7086      0.6970     0.0610  3
  FPR (FP/(FP+TN))            0.2340      0.2128     0.1185  3
  FNR (FN/(FN+TP))            0.6087      0.6522     0.2421  3

groups_LBP_BPI_CETP (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5922      0.5922     0.0577  2
  max valid BA                0.6540      0.6540     0.0298  2
  best valid F1               0.5379      0.5379     0.0386  2
  test BA                     0.5992      0.5992     0.0474  2
  test F1                     0.3879      0.3879     0.1585  2
  test sensitivity            0.3261      0.3261     0.2152  2
  test specificity            0.8723      0.8723     0.1204  2
  test precision              0.5952      0.5952     0.1010  2
  test loss                   0.7830      0.7830     0.0814  2
  FPR (FP/(FP+TN))            0.1277      0.1277     0.1204  2
  FNR (FN/(FN+TP))            0.6739      0.6739     0.2152  2

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5278      0.5000     0.0593  3
  max valid BA                0.5370      0.5158     0.0516  3
  best valid F1               0.5249      0.5181     0.0765  3
  test BA                     0.5104      0.5090     0.0112  3
  test F1                     0.2827      0.4160     0.2449  3
  test sensitivity            0.2718      0.4000     0.2355  3
  test specificity            0.7491      0.6292     0.2174  3
  test precision              0.4417      0.4417     0.0118  2
  test loss                   0.9385      0.9494     0.2452  3
  FPR (FP/(FP+TN))            0.2509      0.3708     0.2174  3
  FNR (FN/(FN+TP))            0.7282      0.6000     0.2355  3

groups_lipocalin (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0000  2
  max valid BA                0.5035      0.5035     0.0049  2
  best valid F1               0.4005      0.4005     0.1407  2
  test BA                     0.5000      0.5000     0.0000  2
  test F1                     0.2500      0.2500     0.3536  2
  test sensitivity            0.5000      0.5000     0.7071  2
  test specificity            0.5000      0.5000     0.7071  2
  test precision              0.3333      0.3333     0.0000  1
  test loss                   0.7054      0.7054     0.0262  2
  FPR (FP/(FP+TN))            0.5000      0.5000     0.7071  2
  FNR (FN/(FN+TP))            0.5000      0.5000     0.7071  2

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5735      0.5735     0.0147  3
  max valid BA                0.6078      0.5882     0.0340  3
  best valid F1               0.5152      0.5172     0.0143  3
  test BA                     0.5245      0.5294     0.0663  3
  test F1                     0.4097      0.4138     0.0441  3
  test sensitivity            0.5098      0.3529     0.2717  3
  test specificity            0.5392      0.7059     0.3950  3
  test precision              0.3954      0.3750     0.0961  3
  test loss                   0.7383      0.7547     0.0696  3
  FPR (FP/(FP+TN))            0.4608      0.2941     0.3950  3
  FNR (FN/(FN+TP))            0.4902      0.6471     0.2717  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.476    0.442     4.000              0.347         0.420   5.000               0.480          0.395
GLTP                     0.595         0.484    0.493     2.000              0.488         0.513   3.000               0.494          0.503
IP_trans                 0.727         0.727    0.574     3.000              0.720         0.583   2.667               0.664          0.457
LBP_BPI_CETP             0.721         0.811    0.600     2.000              0.811         0.607   1.667               0.792          0.574
START                    0.574         0.487    0.515     3.000              0.460         0.462   4.000               0.519          0.501
lipocalin                0.558         0.299    0.256     5.000              0.215         0.223   2.000               0.679          0.463
scp2                     0.632         0.441    0.474     2.667              0.538         0.522   2.667               0.621          0.537

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.532               0.488                  0.036                     0.176
net_AUC           0.479               0.515                  0.083                     0.113

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.471                  0.044                     0.205
net_AUC_prot           0.476               0.491                  0.059                     0.129

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.607               0.581                  0.084                     0.115
net_AUC_lipid           0.490               0.477                  0.121                     0.058

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.532  0.498      0.511     0.472
10     0.532  0.562      0.511     0.536
49     0.532  0.502      0.511     0.467
51     0.532  0.478      0.511     0.463
120    0.532  0.479      0.511     0.476

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.622         0.655      0.033          0.654              0.686           0.033
10        0.622         0.645      0.022          0.654              0.678           0.024
49        0.622         0.654      0.031          0.654              0.698           0.044
51        0.622         0.648      0.025          0.654              0.691           0.037
120       0.622         0.666      0.044          0.654              0.696           0.043

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.476  0.442      0.347     0.420     0.524         0.633      0.109          0.589              0.692           0.103
GLTP          0.484  0.493      0.488     0.513     0.520         0.552      0.033          0.547              0.577           0.030
IP_trans      0.727  0.574      0.720     0.583     0.727         0.745      0.019          0.730              0.755           0.025
LBP_BPI_CETP  0.811  0.600      0.811     0.607     0.811         0.816      0.006          0.815              0.823           0.008
START         0.487  0.515      0.460     0.462     0.513         0.580      0.067          0.561              0.649           0.089
lipocalin     0.299  0.256      0.215     0.223     0.701         0.710      0.009          0.698              0.704           0.006
scp2          0.441  0.474      0.538     0.522     0.562         0.625      0.063          0.634              0.672           0.038

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.532               0.488                  0.036                     0.176
net               0.479               0.515                  0.083                     0.113
fit_chem          0.622               0.590                  0.035                     0.121
fit_chem_net      0.666               0.653                  0.035                     0.095
increment         0.044               0.042                  0.026                     0.038

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.471                  0.044                     0.205
net_prot               0.476               0.491                  0.059                     0.129
fit_chem_prot          0.654               0.659                  0.037                     0.099
fit_chem_net_prot      0.696               0.684                  0.031                     0.078
increment_prot         0.043               0.030                  0.021                     0.038
```
