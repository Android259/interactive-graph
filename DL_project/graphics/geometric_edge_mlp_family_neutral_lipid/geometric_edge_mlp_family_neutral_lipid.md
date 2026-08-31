# geometric_edge_mlp_family_neutral_lipid

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_family_neutral_lipid'
rows: 21

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.5075      0.6721      0.6924      0.5821      0.4876      0.7151
groups_GLTP            3      0.6800      0.2800      0.7624      0.5928      0.6154      0.4615
groups_IP_trans        3      0.2899      0.8298      0.7144      0.5629      0.3333      0.9007
groups_LBP_BPI_CETP    3      0.3188      0.7730      0.6718      0.5060      0.4306      0.7943
groups_START           3      0.6103      0.5243      0.7247      0.5415      0.5677      0.5431
groups_lipocalin       3      0.4537      0.7454      0.7431      0.4546      0.4815      0.7500
groups_scp2            3      0.3725      0.7059      0.6158      0.6473      0.5490      0.7843
ALL                   21      0.4618      0.6472      0.7035      0.5553      0.4950      0.7070

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6010      0.6017     0.0627  21
max valid BA                0.6440      0.6509     0.0681  21
best valid F1               0.6128      0.6071     0.0702  21
test BA                     0.5545      0.5387     0.0679  21
test F1                     0.4115      0.4932     0.2209  21
test sensitivity            0.4618      0.4627     0.3030  21
test specificity            0.6472      0.6885     0.2692  21
test precision              0.4578      0.4783     0.1428  19
test loss                   0.7688      0.7217     0.1585  21
FPR (FP/(FP+TN))            0.3528      0.3115     0.2692  21
FNR (FN/(FN+TP))            0.5382      0.5373     0.3030  21

=== abs(sensitivity-specificity) gap: mean=0.4626 median=0.3611 n=21 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6013      0.6017     0.0131  3
  max valid BA                0.6283      0.6459     0.0350  3
  best valid F1               0.7067      0.7143     0.0138  3
  test BA                     0.5898      0.5681     0.0455  3
  test F1                     0.5596      0.5210     0.0702  3
  test sensitivity            0.5075      0.4627     0.0908  3
  test specificity            0.6721      0.6721     0.0164  3
  test precision              0.6268      0.6122     0.0400  3
  test loss                   0.7918      0.7320     0.1526  3
  FPR (FP/(FP+TN))            0.3279      0.3279     0.0164  3
  FNR (FN/(FN+TP))            0.4925      0.5373     0.0908  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5385      0.5385     0.0192  3
  max valid BA                0.5577      0.5577     0.0192  3
  best valid F1               0.6228      0.6667     0.0836  3
  test BA                     0.4800      0.4800     0.0200  3
  test F1                     0.5504      0.5263     0.1062  3
  test sensitivity            0.6800      0.6000     0.2884  3
  test specificity            0.2800      0.3200     0.2623  3
  test precision              0.4823      0.4783     0.0160  3
  test loss                   0.7298      0.7217     0.0162  3
  FPR (FP/(FP+TN))            0.7200      0.6800     0.2623  3
  FNR (FN/(FN+TP))            0.3200      0.4000     0.2884  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6170      0.6126     0.0361  3
  max valid BA                0.6680      0.6551     0.0421  3
  best valid F1               0.5712      0.5676     0.0603  3
  test BA                     0.5598      0.5675     0.0775  3
  test F1                     0.3003      0.3902     0.2669  3
  test sensitivity            0.2899      0.3478     0.2657  3
  test specificity            0.8298      0.7872     0.1126  3
  test precision              0.3148      0.4444     0.2740  3
  test loss                   0.6313      0.6393     0.0542  3
  FPR (FP/(FP+TN))            0.1702      0.2128     0.1126  3
  FNR (FN/(FN+TP))            0.7101      0.6522     0.2657  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6124      0.6210     0.0881  3
  max valid BA                0.6893      0.6959     0.0119  3
  best valid F1               0.5879      0.5909     0.0098  3
  test BA                     0.5459      0.5162     0.0560  3
  test F1                     0.3146      0.4138     0.2040  3
  test sensitivity            0.3188      0.3913     0.2472  3
  test specificity            0.7730      0.8298     0.2391  3
  test precision              0.4574      0.5000     0.1003  3
  test loss                   0.8295      0.7844     0.1997  3
  FPR (FP/(FP+TN))            0.2270      0.1702     0.2391  3
  FNR (FN/(FN+TP))            0.6812      0.6087     0.2472  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5554      0.5686     0.0501  3
  max valid BA                0.5744      0.5686     0.0240  3
  best valid F1               0.6066      0.6071     0.0137  3
  test BA                     0.5673      0.5387     0.0853  3
  test F1                     0.4238      0.6049     0.3684  3
  test sensitivity            0.6103      0.8769     0.5299  3
  test specificity            0.5243      0.4494     0.4430  3
  test precision              0.4903      0.4903     0.0671  2
  test loss                   0.8250      0.7048     0.2452  3
  FPR (FP/(FP+TN))            0.4757      0.5506     0.4430  3
  FNR (FN/(FN+TP))            0.3897      0.1231     0.5299  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6157      0.6458     0.1040  3
  max valid BA                0.6597      0.6667     0.0593  3
  best valid F1               0.5638      0.5926     0.0797  3
  test BA                     0.5995      0.6181     0.0917  3
  test F1                     0.3650      0.4932     0.3208  3
  test sensitivity            0.4537      0.5000     0.4324  3
  test specificity            0.7454      0.7361     0.2501  3
  test precision              0.4746      0.4746     0.0168  2
  test loss                   0.8473      0.7267     0.2556  3
  FPR (FP/(FP+TN))            0.2546      0.2639     0.2501  3
  FNR (FN/(FN+TP))            0.5463      0.5000     0.4324  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6667      0.6618     0.0085  3
  max valid BA                0.7304      0.7353     0.0663  3
  best valid F1               0.6310      0.6522     0.1035  3
  test BA                     0.5392      0.5147     0.0695  3
  test F1                     0.3669      0.3784     0.1392  3
  test sensitivity            0.3725      0.4118     0.1797  3
  test specificity            0.7059      0.7059     0.0882  3
  test precision              0.3746      0.3500     0.0894  3
  test loss                   0.7271      0.7236     0.0770  3
  FPR (FP/(FP+TN))            0.2941      0.2941     0.0882  3
  FNR (FN/(FN+TP))            0.6275      0.5882     0.1797  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.476    0.600     4.000              0.347         0.544   5.000               0.480          0.563
GLTP                     0.595         0.484    0.498     2.000              0.488         0.513   3.000               0.494          0.518
IP_trans                 0.727         0.727    0.698     3.000              0.720         0.744   2.667               0.664          0.569
LBP_BPI_CETP             0.721         0.811    0.745     2.000              0.811         0.744   1.667               0.792          0.616
START                    0.574         0.487    0.520     3.000              0.460         0.531   4.000               0.519          0.600
lipocalin                0.558         0.299    0.487     5.000              0.215         0.469   2.000               0.679          0.609
scp2                     0.632         0.441    0.739     2.667              0.538         0.601   2.667               0.621          0.614

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.532               0.488                  0.036                     0.176
net_AUC           0.612               0.600                  0.064                     0.114

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.471                  0.044                     0.205
net_AUC_prot           0.592               0.546                  0.053                     0.111

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.607               0.581                  0.084                     0.115
net_AUC_lipid           0.584               0.558                  0.113                     0.036

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.532  0.528      0.511     0.517
10     0.532  0.538      0.511     0.523
49     0.532  0.581      0.511     0.561
51     0.532  0.584      0.511     0.570
120    0.532  0.612      0.511     0.592

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.622         0.665      0.043          0.654              0.692           0.038
10        0.622         0.664      0.041          0.654              0.684           0.031
49        0.622         0.653      0.031          0.654              0.684           0.030
51        0.622         0.667      0.044          0.654              0.691           0.037
120       0.622         0.677      0.054          0.654              0.696           0.043

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.476  0.600      0.347     0.544     0.524         0.579      0.055          0.589              0.628           0.039
GLTP          0.484  0.498      0.488     0.513     0.520         0.546      0.027          0.547              0.550           0.003
IP_trans      0.727  0.698      0.720     0.744     0.727         0.764      0.037          0.730              0.772           0.042
LBP_BPI_CETP  0.811  0.745      0.811     0.744     0.811         0.830      0.019          0.815              0.835           0.020
START         0.487  0.520      0.460     0.531     0.513         0.547      0.034          0.561              0.582           0.021
lipocalin     0.299  0.487      0.215     0.469     0.701         0.734      0.034          0.698              0.747           0.048
scp2          0.441  0.739      0.538     0.601     0.562         0.736      0.174          0.634              0.758           0.124

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.532               0.488                  0.036                     0.176
net               0.612               0.600                  0.064                     0.114
fit_chem          0.622               0.590                  0.035                     0.121
fit_chem_net      0.677               0.694                  0.046                     0.116
increment         0.054               0.047                  0.043                     0.054

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.471                  0.044                     0.205
net_prot               0.592               0.546                  0.053                     0.111
fit_chem_prot          0.654               0.659                  0.037                     0.099
fit_chem_net_prot      0.696               0.695                  0.047                     0.108
increment_prot         0.043               0.027                  0.040                     0.039
```
