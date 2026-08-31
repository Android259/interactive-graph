# geometric_edge_mlp_add_nwd

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_add_nwd'
rows: 18

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       2      0.4254      0.6721      0.6986      0.2918      0.4254      0.6452
groups_GLTP            2      0.5600      0.5600      0.6454      0.4129      0.6731      0.4808
groups_IP_trans        3      0.3768      0.6312      0.5601      0.5634      0.4444      0.6383
groups_LBP_BPI_CETP    3      0.4493      0.5177      0.7569      0.2960      0.5694      0.4823
groups_START           3      0.6667      0.5243      0.8521      0.1962      0.6250      0.4719
groups_lipocalin       3      0.8704      0.4537      0.4057      0.5892      0.8426      0.4630
groups_scp2            2      0.5882      0.6324      0.5140      0.5495      0.7353      0.6471
ALL                   18      0.5687      0.5617      0.6356      0.4135      0.6173      0.5396

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5760      0.5574     0.0731  18
max valid BA                0.6016      0.5921     0.0855  18
best valid F1               0.6010      0.6121     0.0762  18
test BA                     0.5652      0.5409     0.0934  18
test F1                     0.4335      0.5000     0.2390  18
test sensitivity            0.5687      0.5902     0.3760  18
test specificity            0.5617      0.5906     0.3377  18
test precision              0.4151      0.4463     0.2000  18
test loss                   0.7888      0.6861     0.4498  18
FPR (FP/(FP+TN))            0.4383      0.4094     0.3377  18
FNR (FN/(FN+TP))            0.4313      0.4098     0.3760  18

=== abs(sensitivity-specificity) gap: mean=0.5863 median=0.5298 n=18 ===

=== By group ===
groups_CRAL-TRIO (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5353      0.5353     0.0393  2
  max valid BA                0.5564      0.5564     0.0692  2
  best valid F1               0.6837      0.6837     0.0000  2
  test BA                     0.5488      0.5488     0.0805  2
  test F1                     0.3497      0.3497     0.4945  2
  test sensitivity            0.4254      0.4254     0.6016  2
  test specificity            0.6721      0.6721     0.4405  2
  test precision              0.2969      0.2969     0.4198  2
  test loss                   0.6919      0.6919     0.0153  2
  FPR (FP/(FP+TN))            0.3279      0.3279     0.4405  2
  FNR (FN/(FN+TP))            0.5746      0.5746     0.6016  2

groups_GLTP (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5769      0.5769     0.0272  2
  max valid BA                0.6154      0.6154     0.0272  2
  best valid F1               0.6913      0.6913     0.0100  2
  test BA                     0.5600      0.5600     0.1697  2
  test F1                     0.5025      0.5025     0.3385  2
  test sensitivity            0.5600      0.5600     0.5091  2
  test specificity            0.5600      0.5600     0.1697  2
  test precision              0.5031      0.5031     0.1676  2
  test loss                   0.6933      0.6933     0.0010  2
  FPR (FP/(FP+TN))            0.4400      0.4400     0.1697  2
  FNR (FN/(FN+TP))            0.4400      0.4400     0.5091  2

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5414      0.5208     0.0447  3
  max valid BA                0.5533      0.5465     0.0364  3
  best valid F1               0.5127      0.5053     0.0128  3
  test BA                     0.5040      0.5106     0.0127  3
  test F1                     0.2312      0.1935     0.2521  3
  test sensitivity            0.3768      0.1304     0.5436  3
  test specificity            0.6312      0.8936     0.5299  3
  test precision              0.2361      0.3333     0.2055  3
  test loss                   0.6805      0.6781     0.0208  3
  FPR (FP/(FP+TN))            0.3688      0.1064     0.5299  3
  FNR (FN/(FN+TP))            0.6232      0.8696     0.5436  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5259      0.5204     0.0290  3
  max valid BA                0.5618      0.5780     0.0555  3
  best valid F1               0.5243      0.5106     0.0284  3
  test BA                     0.4835      0.5000     0.0386  3
  test F1                     0.2849      0.2800     0.2074  3
  test sensitivity            0.4493      0.3043     0.4945  3
  test specificity            0.5177      0.5745     0.4918  3
  test precision              0.3626      0.3286     0.1239  3
  test loss                   1.3190      0.6858     1.1008  3
  FPR (FP/(FP+TN))            0.4823      0.4255     0.4918  3
  FNR (FN/(FN+TP))            0.5507      0.6957     0.4945  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5485      0.5402     0.0190  3
  max valid BA                0.5571      0.5402     0.0300  3
  best valid F1               0.6047      0.6095     0.0131  3
  test BA                     0.5955      0.5880     0.0302  3
  test F1                     0.5702      0.5600     0.0363  3
  test sensitivity            0.6667      0.5692     0.1960  3
  test specificity            0.5243      0.6067     0.2465  3
  test precision              0.5204      0.5139     0.0599  3
  test loss                   0.6830      0.6864     0.0087  3
  FPR (FP/(FP+TN))            0.4757      0.3933     0.2465  3
  FNR (FN/(FN+TP))            0.3333      0.4308     0.1960  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6528      0.7083     0.1211  3
  max valid BA                0.6759      0.7500     0.1405  3
  best valid F1               0.6204      0.6667     0.0987  3
  test BA                     0.6620      0.7153     0.1431  3
  test F1                     0.6119      0.6372     0.1016  3
  test sensitivity            0.8704      1.0000     0.2245  3
  test specificity            0.4537      0.4306     0.4657  3
  test precision              0.5386      0.4675     0.2485  3
  test loss                   0.6820      0.6822     0.0158  3
  FPR (FP/(FP+TN))            0.5463      0.5694     0.4657  3
  FNR (FN/(FN+TP))            0.1296      0.0000     0.2245  3

groups_scp2 (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6691      0.6691     0.0312  2
  max valid BA                0.7206      0.7206     0.0416  2
  best valid F1               0.6410      0.6410     0.0363  2
  test BA                     0.6103      0.6103     0.0104  2
  test F1                     0.5020      0.5020     0.0444  2
  test sensitivity            0.5882      0.5882     0.1664  2
  test specificity            0.6324      0.6324     0.1456  2
  test precision              0.4496      0.4496     0.0297  2
  test loss                   0.6670      0.6670     0.0284  2
  FPR (FP/(FP+TN))            0.3676      0.3676     0.1456  2
  FNR (FN/(FN+TP))            0.4118      0.4118     0.1664  2
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.476    0.446     4.000              0.347         0.478   5.000               0.480          0.451
GLTP                     0.595         0.484    0.592     2.000              0.488         0.599   3.000               0.494          0.637
IP_trans                 0.727         0.727    0.518     3.000              0.720         0.578   2.667               0.664          0.464
LBP_BPI_CETP             0.721         0.811    0.521     2.000              0.811         0.545   1.667               0.792          0.531
START                    0.574         0.487    0.552     3.000              0.460         0.523   4.000               0.519          0.428
lipocalin                0.558         0.299    0.527     5.000              0.215         0.641   2.000               0.679          0.497
scp2                     0.632         0.441    0.726     2.667              0.538         0.592   2.667               0.621          0.576

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.532               0.488                  0.036                     0.176
net_AUC           0.555               0.538                  0.147                     0.087

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.471                  0.044                     0.205
net_AUC_prot           0.565               0.581                  0.191                     0.054

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.607               0.581                  0.084                     0.115
net_AUC_lipid           0.512               0.485                  0.111                     0.075

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.532  0.522      0.511     0.499
10     0.532  0.582      0.511     0.615
49     0.532  0.550      0.511     0.570
51     0.532  0.544      0.511     0.572
120    0.532  0.555      0.511     0.565

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.622         0.661      0.038          0.654              0.701           0.047
10        0.622         0.671      0.049          0.654              0.709           0.056
49        0.622         0.667      0.045          0.654              0.706           0.052
51        0.622         0.661      0.039          0.654              0.702           0.048
120       0.622         0.685      0.063          0.654              0.713           0.059

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.476  0.446      0.347     0.478     0.524         0.553      0.029          0.589              0.598           0.009
GLTP          0.484  0.592      0.488     0.599     0.520         0.618      0.099          0.547              0.605           0.057
IP_trans      0.727  0.518      0.720     0.578     0.727         0.756      0.029          0.730              0.769           0.038
LBP_BPI_CETP  0.811  0.521      0.811     0.545     0.811         0.804     -0.007          0.815              0.807          -0.008
START         0.487  0.552      0.460     0.523     0.513         0.580      0.067          0.561              0.638           0.077
lipocalin     0.299  0.527      0.215     0.641     0.701         0.746      0.046          0.698              0.811           0.113
scp2          0.441  0.726      0.538     0.592     0.562         0.738      0.177          0.634              0.764           0.129

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.532               0.488                  0.036                     0.176
net               0.555               0.538                  0.147                     0.087
fit_chem          0.622               0.590                  0.035                     0.121
fit_chem_net      0.685               0.725                  0.056                     0.099
increment         0.063               0.045                  0.052                     0.060

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.471                  0.044                     0.205
net_prot               0.565               0.581                  0.191                     0.054
fit_chem_prot          0.654               0.659                  0.037                     0.099
fit_chem_net_prot      0.713               0.754                  0.045                     0.096
increment_prot         0.059               0.059                  0.049                     0.051
```
