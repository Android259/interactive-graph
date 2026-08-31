# geometric_edge_attention_nwd_no_lipid_graphs

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention_nwd_no_lipid_graphs'
rows: 18

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       2      0.4254      0.5902      0.8943      0.3847      0.4925      0.5726
groups_GLTP            2      0.3000      0.9400      0.7688      0.6821      0.2115      0.9615
groups_IP_trans        3      0.2899      0.8014      0.8264      0.6860      0.4444      0.8298
groups_LBP_BPI_CETP    3      0.4928      0.6454      0.8823      0.4678      0.5556      0.7234
groups_START           3      0.6256      0.3558      0.9443      0.4010      0.6875      0.3708
groups_lipocalin       3      0.5833      0.5463      0.7880      0.4246      0.6019      0.5509
groups_scp2            2      0.4706      0.5588      0.6914      0.7409      0.6176      0.5735
ALL                   18      0.4648      0.6236      0.8351      0.5307      0.5284      0.6467

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5875      0.5904     0.0686  18
max valid BA                0.6159      0.5995     0.0796  18
best valid F1               0.5571      0.5866     0.0882  18
test BA                     0.5442      0.5160     0.0712  18
test F1                     0.4004      0.4073     0.1658  18
test sensitivity            0.4648      0.4348     0.3106  18
test specificity            0.6236      0.7371     0.3342  18
test precision              0.4804      0.4472     0.1507  18
test loss                   0.7377      0.6997     0.1110  18
FPR (FP/(FP+TN))            0.3764      0.2629     0.3342  18
FNR (FN/(FN+TP))            0.5352      0.5652     0.3106  18

=== abs(sensitivity-specificity) gap: mean=0.5537 median=0.5958 n=18 ===

=== By group ===
groups_CRAL-TRIO (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5326      0.5326     0.0130  2
  max valid BA                0.5549      0.5549     0.0130  2
  best valid F1               0.6307      0.6307     0.0761  2
  test BA                     0.5078      0.5078     0.0060  2
  test F1                     0.3889      0.3889     0.3296  2
  test sensitivity            0.4254      0.4254     0.4749  2
  test specificity            0.5902      0.5902     0.4869  2
  test precision              0.5629      0.5629     0.0525  2
  test loss                   0.6932      0.6932     0.0001  2
  FPR (FP/(FP+TN))            0.4098      0.4098     0.4869  2
  FNR (FN/(FN+TP))            0.5746      0.5746     0.4749  2

groups_GLTP (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5865      0.5865     0.0136  2
  max valid BA                0.5865      0.5865     0.0136  2
  best valid F1               0.3800      0.3800     0.0545  2
  test BA                     0.6200      0.6200     0.1414  2
  test F1                     0.4158      0.4158     0.3052  2
  test sensitivity            0.3000      0.3000     0.2546  2
  test specificity            0.9400      0.9400     0.0283  2
  test precision              0.7615      0.7615     0.2284  2
  test loss                   0.8910      0.8910     0.1856  2
  FPR (FP/(FP+TN))            0.0600      0.0600     0.0283  2
  FNR (FN/(FN+TP))            0.7000      0.7000     0.2546  2

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6371      0.6126     0.0508  3
  max valid BA                0.7058      0.7154     0.0178  3
  best valid F1               0.6141      0.6275     0.0267  3
  test BA                     0.5456      0.5569     0.0502  3
  test F1                     0.3304      0.3810     0.1309  3
  test sensitivity            0.2899      0.3478     0.1398  3
  test specificity            0.8014      0.7872     0.0443  3
  test precision              0.3982      0.4211     0.0891  3
  test loss                   0.7395      0.6542     0.1699  3
  FPR (FP/(FP+TN))            0.1986      0.2128     0.0443  3
  FNR (FN/(FN+TP))            0.7101      0.6522     0.1398  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6395      0.6108     0.0660  3
  max valid BA                0.6656      0.6605     0.0470  3
  best valid F1               0.5821      0.5946     0.0584  3
  test BA                     0.5691      0.5555     0.0822  3
  test F1                     0.4201      0.3860     0.1374  3
  test sensitivity            0.4928      0.4783     0.2829  3
  test specificity            0.6454      0.5319     0.2152  3
  test precision              0.4245      0.4500     0.0910  3
  test loss                   0.6848      0.6911     0.0518  3
  FPR (FP/(FP+TN))            0.3546      0.4681     0.2152  3
  FNR (FN/(FN+TP))            0.5072      0.5217     0.2829  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5291      0.5312     0.0282  3
  max valid BA                0.5503      0.5712     0.0438  3
  best valid F1               0.5677      0.5899     0.0383  3
  test BA                     0.4907      0.4895     0.0087  3
  test F1                     0.4756      0.4636     0.1124  3
  test sensitivity            0.6256      0.5385     0.3393  3
  test specificity            0.3558      0.4270     0.3261  3
  test precision              0.4122      0.4074     0.0086  3
  test loss                   0.7992      0.7786     0.1115  3
  FPR (FP/(FP+TN))            0.6442      0.5730     0.3261  3
  FNR (FN/(FN+TP))            0.3744      0.4615     0.3393  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5764      0.5069     0.1263  3
  max valid BA                0.5764      0.5069     0.1263  3
  best valid F1               0.5217      0.5000     0.1045  3
  test BA                     0.5648      0.5208     0.0948  3
  test F1                     0.4176      0.5000     0.2110  3
  test sensitivity            0.5833      0.6389     0.4470  3
  test specificity            0.5463      0.7083     0.4860  3
  test precision              0.4335      0.4444     0.0952  3
  test loss                   0.6749      0.6853     0.0360  3
  FPR (FP/(FP+TN))            0.4537      0.2917     0.4860  3
  FNR (FN/(FN+TP))            0.4167      0.3611     0.4470  3

groups_scp2 (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5956      0.5956     0.0104  2
  max valid BA                0.6544      0.6544     0.0728  2
  best valid F1               0.5750      0.5750     0.0249  2
  test BA                     0.5147      0.5147     0.0416  2
  test F1                     0.3333      0.3333     0.1886  2
  test sensitivity            0.4706      0.4706     0.4991  2
  test specificity            0.5588      0.5588     0.5823  2
  test precision              0.4961      0.4961     0.2412  2
  test loss                   0.7078      0.7078     0.0111  2
  FPR (FP/(FP+TN))            0.4412      0.4412     0.5823  2
  FNR (FN/(FN+TP))            0.5294      0.5294     0.4991  2
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.476    0.474     4.000              0.347         0.451   5.000               0.480          0.407
GLTP                     0.595         0.484    0.420     2.000              0.488         0.435   3.000               0.494          0.548
IP_trans                 0.727         0.727    0.572     3.000              0.720         0.605   2.667               0.664          0.578
LBP_BPI_CETP             0.721         0.811    0.556     2.000              0.811         0.519   1.667               0.792          0.513
START                    0.574         0.487    0.528     3.000              0.460         0.482   4.000               0.519          0.602
lipocalin                0.558         0.299    0.329     5.000              0.215         0.286   2.000               0.679          0.597
scp2                     0.632         0.441    0.527     2.667              0.538         0.625   2.667               0.621          0.528

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.532               0.488                  0.036                     0.176
net_AUC           0.486               0.476                  0.094                     0.086

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.471                  0.044                     0.205
net_AUC_prot           0.486               0.498                  0.115                     0.114

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.607               0.581                  0.084                     0.115
net_AUC_lipid           0.539               0.533                  0.100                     0.067

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.532  0.536      0.511     0.502
10     0.532  0.563      0.511     0.537
49     0.532  0.506      0.511     0.499
51     0.532  0.510      0.511     0.501
120    0.532  0.486      0.511     0.486

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.622         0.651      0.029          0.654              0.680           0.027
10        0.622         0.645      0.023          0.654              0.679           0.026
49        0.622         0.660      0.038          0.654              0.680           0.026
51        0.622         0.658      0.035          0.654              0.679           0.025
120       0.622         0.655      0.033          0.654              0.681           0.027

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.476  0.474      0.347     0.451     0.524         0.534      0.010          0.589              0.602           0.013
GLTP          0.484  0.420      0.488     0.435     0.520         0.611      0.092          0.547              0.652           0.105
IP_trans      0.727  0.572      0.720     0.605     0.727         0.730      0.004          0.730              0.736           0.006
LBP_BPI_CETP  0.811  0.556      0.811     0.519     0.811         0.814      0.004          0.815              0.820           0.005
START         0.487  0.528      0.460     0.482     0.513         0.499     -0.014          0.561              0.561          -0.000
lipocalin     0.299  0.329      0.215     0.286     0.701         0.716      0.016          0.698              0.709           0.011
scp2          0.441  0.527      0.538     0.625     0.562         0.680      0.119          0.634              0.685           0.051

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.532               0.488                  0.036                     0.176
net               0.486               0.476                  0.094                     0.086
fit_chem          0.622               0.590                  0.035                     0.121
fit_chem_net      0.655               0.643                  0.059                     0.113
increment         0.033               0.015                  0.041                     0.051

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.471                  0.044                     0.205
net_prot               0.486               0.498                  0.115                     0.114
fit_chem_prot          0.654               0.659                  0.037                     0.099
fit_chem_net_prot      0.681               0.686                  0.053                     0.086
increment_prot         0.027               0.011                  0.026                     0.038
```
