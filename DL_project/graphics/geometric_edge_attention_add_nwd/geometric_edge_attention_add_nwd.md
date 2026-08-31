# geometric_edge_attention_add_nwd

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention_add_nwd'
rows: 19

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.5672      0.5027      0.6543      0.4933      0.5572      0.5538
groups_GLTP            2      0.6200      0.5800      0.5140      0.5215      0.7308      0.5577
groups_IP_trans        3      0.8841      0.4113      0.7603      0.4633      0.9167      0.3759
groups_LBP_BPI_CETP    3      0.2464      0.8085      0.6280      0.5404      0.2778      0.7872
groups_START           3      0.5538      0.6142      0.6086      0.5643      0.5677      0.5655
groups_lipocalin       3      0.2963      0.9306      0.5525      0.6019      0.3241      0.9028
groups_scp2            2      0.7059      0.3676      0.5441      0.5134      0.7941      0.4706
ALL                   19      0.5418      0.6157      0.6172      0.5294      0.5779      0.6112

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5945      0.5652     0.0860  19
max valid BA                0.6524      0.6164     0.0835  19
best valid F1               0.6337      0.6351     0.0775  19
test BA                     0.5787      0.5800     0.0715  19
test F1                     0.4520      0.5172     0.2088  19
test sensitivity            0.5418      0.5000     0.3433  19
test specificity            0.6157      0.5957     0.3417  19
test precision              0.5396      0.5445     0.2334  18
test loss                   0.7620      0.6899     0.3458  19
FPR (FP/(FP+TN))            0.3843      0.4043     0.3417  19
FNR (FN/(FN+TP))            0.4582      0.5000     0.3433  19

=== abs(sensitivity-specificity) gap: mean=0.5890 median=0.6596 n=19 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5555      0.5571     0.0186  3
  max valid BA                0.5802      0.5762     0.0096  3
  best valid F1               0.7006      0.6989     0.0046  3
  test BA                     0.5349      0.5415     0.0115  3
  test F1                     0.4720      0.6027     0.3165  3
  test sensitivity            0.5672      0.6567     0.4691  3
  test specificity            0.5027      0.4262     0.4476  3
  test precision              0.6341      0.5570     0.1438  3
  test loss                   1.1832      0.6911     0.8648  3
  FPR (FP/(FP+TN))            0.4973      0.5738     0.4476  3
  FNR (FN/(FN+TP))            0.4328      0.3433     0.4691  3

groups_GLTP (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6442      0.6442     0.1224  2
  max valid BA                0.6923      0.6923     0.0544  2
  best valid F1               0.6969      0.6969     0.0180  2
  test BA                     0.6000      0.6000     0.0283  2
  test F1                     0.5457      0.5457     0.2242  2
  test sensitivity            0.6200      0.6200     0.5374  2
  test specificity            0.5800      0.5800     0.5940  2
  test precision              0.7717      0.7717     0.3228  2
  test loss                   0.6858      0.6858     0.0084  2
  FPR (FP/(FP+TN))            0.4200      0.4200     0.5940  2
  FNR (FN/(FN+TP))            0.3800      0.3800     0.5374  2

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6463      0.6170     0.0990  3
  max valid BA                0.6968      0.7566     0.1036  3
  best valid F1               0.6334      0.6774     0.0762  3
  test BA                     0.6477      0.6674     0.0366  3
  test F1                     0.5730      0.5763     0.0261  3
  test sensitivity            0.8841      0.9130     0.1328  3
  test specificity            0.4113      0.3404     0.1611  3
  test precision              0.4290      0.4259     0.0418  3
  test loss                   0.6939      0.6901     0.0067  3
  FPR (FP/(FP+TN))            0.5887      0.6596     0.1611  3
  FNR (FN/(FN+TP))            0.1159      0.0870     0.1328  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5325      0.5363     0.0308  3
  max valid BA                0.5773      0.5816     0.0284  3
  best valid F1               0.5184      0.5106     0.0183  3
  test BA                     0.5274      0.5000     0.0830  3
  test F1                     0.2593      0.3333     0.2313  3
  test sensitivity            0.2464      0.3478     0.2145  3
  test specificity            0.8085      0.8936     0.2454  3
  test precision              0.4529      0.4529     0.2299  2
  test loss                   0.6848      0.6572     0.0846  3
  FPR (FP/(FP+TN))            0.1915      0.1064     0.2454  3
  FNR (FN/(FN+TP))            0.7536      0.6522     0.2145  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5666      0.5700     0.0156  3
  max valid BA                0.6187      0.6164     0.0396  3
  best valid F1               0.6195      0.6243     0.0186  3
  test BA                     0.5840      0.6128     0.0595  3
  test F1                     0.5111      0.5172     0.0764  3
  test sensitivity            0.5538      0.4615     0.3179  3
  test specificity            0.6142      0.7640     0.4355  3
  test precision              0.6150      0.5882     0.1991  3
  test loss                   0.6953      0.6987     0.0090  3
  FPR (FP/(FP+TN))            0.3858      0.2360     0.4355  3
  FNR (FN/(FN+TP))            0.4462      0.5385     0.3179  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6134      0.5764     0.1493  3
  max valid BA                0.7315      0.7917     0.1165  3
  best valid F1               0.6707      0.7246     0.1162  3
  test BA                     0.6134      0.6667     0.1235  3
  test F1                     0.3696      0.5185     0.3220  3
  test sensitivity            0.2963      0.3889     0.2625  3
  test specificity            0.9306      0.9444     0.0241  3
  test precision              0.4993      0.7200     0.4333  3
  test loss                   0.6499      0.6595     0.0394  3
  FPR (FP/(FP+TN))            0.0694      0.0556     0.0241  3
  FNR (FN/(FN+TP))            0.7037      0.6111     0.2625  3

groups_scp2 (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6324      0.6324     0.1248  2
  max valid BA                0.6985      0.6985     0.0312  2
  best valid F1               0.6097      0.6097     0.0266  2
  test BA                     0.5368      0.5368     0.0312  2
  test F1                     0.4709      0.4709     0.0296  2
  test sensitivity            0.7059      0.7059     0.2496  2
  test specificity            0.3676      0.3676     0.3120  2
  test precision              0.3661      0.3661     0.0356  2
  test loss                   0.6924      0.6924     0.0512  2
  FPR (FP/(FP+TN))            0.6324      0.6324     0.3120  2
  FNR (FN/(FN+TP))            0.2941      0.2941     0.2496  2
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.476    0.482     4.000              0.347         0.475   5.000               0.480          0.430
GLTP                     0.595         0.484    0.505     2.000              0.488         0.516   3.000               0.494          0.551
IP_trans                 0.727         0.727    0.590     3.000              0.720         0.570   2.667               0.664          0.659
LBP_BPI_CETP             0.721         0.811    0.412     2.000              0.811         0.398   1.667               0.792          0.511
START                    0.574         0.487    0.609     3.000              0.460         0.572   4.000               0.519          0.539
lipocalin                0.558         0.299    0.352     5.000              0.215         0.297   2.000               0.679          0.455
scp2                     0.632         0.441    0.687     2.667              0.538         0.643   2.667               0.621          0.641

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.532               0.488                  0.036                     0.176
net_AUC           0.520               0.557                  0.099                     0.117

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.471                  0.044                     0.205
net_AUC_prot           0.496               0.532                  0.119                     0.118

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.607               0.581                  0.084                     0.115
net_AUC_lipid           0.541               0.532                  0.126                     0.086

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.532  0.458      0.511     0.455
10     0.532  0.488      0.511     0.491
49     0.532  0.474      0.511     0.479
51     0.532  0.489      0.511     0.487
120    0.532  0.520      0.511     0.496

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.622         0.655      0.033          0.654              0.699           0.045
10        0.622         0.674      0.052          0.654              0.704           0.050
49        0.622         0.662      0.039          0.654              0.691           0.038
51        0.622         0.667      0.045          0.654              0.714           0.060
120       0.622         0.681      0.059          0.654              0.705           0.051

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.476  0.482      0.347     0.475     0.524         0.533      0.009          0.589              0.588          -0.001
GLTP          0.484  0.505      0.488     0.516     0.520         0.588      0.068          0.547              0.611           0.064
IP_trans      0.727  0.590      0.720     0.570     0.727         0.760      0.034          0.730              0.770           0.040
LBP_BPI_CETP  0.811  0.412      0.811     0.398     0.811         0.809     -0.002          0.815              0.817           0.002
START         0.487  0.609      0.460     0.572     0.513         0.632      0.119          0.561              0.655           0.094
lipocalin     0.299  0.352      0.215     0.297     0.701         0.739      0.039          0.698              0.750           0.052
scp2          0.441  0.687      0.538     0.643     0.562         0.706      0.144          0.634              0.742           0.108

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.532               0.488                  0.036                     0.176
net               0.520               0.557                  0.099                     0.117
fit_chem          0.622               0.590                  0.035                     0.121
fit_chem_net      0.681               0.665                  0.046                     0.100
increment         0.059               0.039                  0.043                     0.055

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.471                  0.044                     0.205
net_prot               0.496               0.532                  0.119                     0.118
fit_chem_prot          0.654               0.659                  0.037                     0.099
fit_chem_net_prot      0.705               0.709                  0.056                     0.087
increment_prot         0.051               0.039                  0.051                     0.042
```
