# geometric_edge_attention

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5612      0.4262      0.4897      0.5115      0.5821      0.4226
groups_GLTP            5      0.4960      0.5440      0.5401      0.4608      0.5308      0.4923
groups_IP_trans        5      0.6000      0.4766      0.4639      0.5303      0.6000      0.4298
groups_LBP_BPI_CETP    5      0.7130      0.3064      0.5830      0.4075      0.7583      0.3404
groups_START           5      0.2462      0.7596      0.4184      0.6102      0.2500      0.7955
groups_lipocalin       5      0.3278      0.6556      0.4122      0.6061      0.3778      0.6639
groups_scp2            5      0.4588      0.5824      0.4890      0.5110      0.5176      0.6176
ALL                   35      0.4861      0.5358      0.4852      0.5196      0.5167      0.5374

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5271      0.5000     0.0490  35
max valid BA                0.5288      0.5000     0.0491  35
best valid F1               0.5708      0.5106     0.0769  35
test BA                     0.5110      0.5000     0.0445  35
test F1                     0.3205      0.3922     0.2613  35
test sensitivity            0.4861      0.4118     0.4445  35
test specificity            0.5358      0.6806     0.4438  35
test precision              0.4556      0.3862     0.1922  24
test loss                   0.6946      0.6931     0.0064  35
FPR (FP/(FP+TN))            0.4642      0.3194     0.4438  35
FNR (FN/(FN+TP))            0.5139      0.5882     0.4445  35

=== abs(sensitivity-specificity) gap: mean=0.8258 median=1.0000 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5023      0.5000     0.0052  5
  max valid BA                0.5023      0.5000     0.0052  5
  best valid F1               0.6837      0.6837     0.0000  5
  test BA                     0.4937      0.5000     0.0141  5
  test F1                     0.3990      0.6207     0.3653  5
  test sensitivity            0.5612      0.8060     0.5184  5
  test specificity            0.4262      0.1311     0.5265  5
  test precision              0.5172      0.5234     0.0108  3
  test loss                   0.6936      0.6933     0.0015  5
  FPR (FP/(FP+TN))            0.5738      0.8689     0.5265  5
  FNR (FN/(FN+TP))            0.4388      0.1940     0.5184  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5115      0.5000     0.0258  5
  max valid BA                0.5115      0.5000     0.0258  5
  best valid F1               0.6667      0.6667     0.0000  5
  test BA                     0.5200      0.5000     0.0447  5
  test F1                     0.3758      0.5455     0.3466  5
  test sensitivity            0.4960      0.4800     0.5001  5
  test specificity            0.5440      0.7200     0.5096  5
  test precision              0.5439      0.5000     0.0760  3
  test loss                   0.6934      0.6932     0.0005  5
  FPR (FP/(FP+TN))            0.4560      0.2800     0.5096  5
  FNR (FN/(FN+TP))            0.5040      0.5200     0.5001  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5149      0.5000     0.0333  5
  max valid BA                0.5170      0.5000     0.0324  5
  best valid F1               0.5144      0.5053     0.0175  5
  test BA                     0.5383      0.5000     0.0856  5
  test F1                     0.3205      0.4946     0.2966  5
  test sensitivity            0.6000      1.0000     0.5477  5
  test specificity            0.4766      0.3830     0.5027  5
  test precision              0.3665      0.3286     0.0657  3
  test loss                   0.6964      0.6931     0.0110  5
  FPR (FP/(FP+TN))            0.5234      0.6170     0.5027  5
  FNR (FN/(FN+TP))            0.4000      0.0000     0.5477  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5494      0.5000     0.1046  5
  max valid BA                0.5494      0.5000     0.1046  5
  best valid F1               0.5363      0.5053     0.0665  5
  test BA                     0.5097      0.5000     0.0283  5
  test F1                     0.3879      0.4835     0.2171  5
  test sensitivity            0.7130      0.9565     0.4311  5
  test specificity            0.3064      0.0213     0.4449  5
  test precision              0.3398      0.3286     0.0259  4
  test loss                   0.6975      0.6936     0.0092  5
  FPR (FP/(FP+TN))            0.6936      0.9787     0.4449  5
  FNR (FN/(FN+TP))            0.2870      0.0435     0.4311  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5228      0.5169     0.0302  5
  max valid BA                0.5326      0.5234     0.0329  5
  best valid F1               0.5921      0.5899     0.0036  5
  test BA                     0.5029      0.5000     0.0109  5
  test F1                     0.1848      0.0597     0.2560  5
  test sensitivity            0.2462      0.0308     0.4295  5
  test specificity            0.7596      1.0000     0.4234  5
  test precision              0.6072      0.4276     0.3406  3
  test loss                   0.6925      0.6931     0.0011  5
  FPR (FP/(FP+TN))            0.2404      0.0000     0.4234  5
  FNR (FN/(FN+TP))            0.7538      0.9692     0.4295  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5208      0.5069     0.0295  5
  max valid BA                0.5208      0.5069     0.0295  5
  best valid F1               0.5007      0.5000     0.0016  5
  test BA                     0.4917      0.5000     0.0151  5
  test F1                     0.2245      0.2899     0.2201  5
  test sensitivity            0.3278      0.2778     0.4094  5
  test specificity            0.6556      0.6806     0.4046  5
  test precision              0.3139      0.3030     0.0195  3
  test loss                   0.6916      0.6931     0.0026  5
  FPR (FP/(FP+TN))            0.3444      0.3194     0.4046  5
  FNR (FN/(FN+TP))            0.6722      0.7222     0.4094  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5676      0.5735     0.0436  5
  max valid BA                0.5676      0.5735     0.0436  5
  best valid F1               0.5016      0.5000     0.0035  5
  test BA                     0.5206      0.5147     0.0638  5
  test F1                     0.3511      0.3922     0.1574  5
  test sensitivity            0.4588      0.4118     0.3612  5
  test specificity            0.5824      0.7941     0.4182  5
  test precision              0.5059      0.3636     0.2916  5
  test loss                   0.6973      0.6930     0.0096  5
  FPR (FP/(FP+TN))            0.4176      0.2059     0.4182  5
  FNR (FN/(FN+TP))            0.5412      0.5882     0.3612  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.630         0.484    0.500       4.0              0.369         0.500     5.0               0.458          0.500
GLTP                     0.605         0.521    0.500       2.0              0.512         0.500     3.0               0.523          0.500
IP_trans                 0.722         0.680    0.500       3.0              0.677         0.500     2.4               0.590          0.500
LBP_BPI_CETP             0.719         0.798    0.500       2.0              0.798         0.500     1.6               0.784          0.500
START                    0.576         0.508    0.492       3.0              0.474         0.506     4.0               0.536          0.505
lipocalin                0.565         0.331    0.500       5.0              0.246         0.500     2.2               0.646          0.500
scp2                     0.651         0.489    0.500       2.8              0.593         0.500     2.6               0.642          0.500

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.545               0.503                  0.065                     0.151
net_AUC           0.499               0.500                  0.003                     0.003

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.524               0.493                  0.065                     0.186
net_AUC_prot           0.501               0.500                  0.002                     0.002

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.597               0.581                  0.085                     0.106
net_AUC_lipid           0.501               0.500                  0.002                     0.002

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.495      0.524     0.467
10     0.545  0.492      0.524     0.460
49     0.545  0.480      0.524     0.454
51     0.545  0.486      0.524     0.454
120    0.545  0.499      0.524     0.501

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.618         0.646      0.028          0.653              0.681           0.027
10        0.618         0.646      0.028          0.653              0.679           0.026
49        0.618         0.652      0.034          0.653              0.686           0.033
51        0.618         0.649      0.031          0.653              0.677           0.023
120       0.618         0.620      0.002          0.653              0.655           0.001

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.484  0.500      0.369     0.500     0.539         0.539      0.000          0.613              0.613           0.000
GLTP          0.521  0.500      0.512     0.500     0.543         0.543      0.000          0.565              0.565           0.000
IP_trans      0.680  0.500      0.677     0.500     0.680         0.680      0.000          0.693              0.693           0.000
LBP_BPI_CETP  0.798  0.500      0.798     0.500     0.798         0.798      0.000          0.801              0.801           0.000
START         0.508  0.492      0.474     0.506     0.536         0.548      0.012          0.606              0.615           0.009
lipocalin     0.331  0.500      0.246     0.500     0.669         0.669      0.000          0.673              0.673           0.000
scp2          0.489  0.500      0.593     0.500     0.562         0.562      0.000          0.622              0.622           0.000

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.545               0.503                  0.065                     0.151
net               0.499               0.500                  0.003                     0.003
fit_chem          0.618               0.590                  0.052                     0.101
fit_chem_net      0.620               0.590                  0.052                     0.099
increment         0.002               0.000                  0.004                     0.004

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.524               0.493                  0.065                     0.186
net_prot               0.501               0.500                  0.002                     0.002
fit_chem_prot          0.653               0.662                  0.055                     0.078
fit_chem_net_prot      0.655               0.662                  0.054                     0.077
increment_prot         0.001               0.000                  0.003                     0.004
```
