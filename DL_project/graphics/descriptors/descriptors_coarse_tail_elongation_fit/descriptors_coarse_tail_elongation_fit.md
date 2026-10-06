# descriptors_coarse_tail_elongation_fit

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_coarse_tail_elongation_fit'
rows: 9

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO    1      0.2388      0.7705      0.4686      0.6902      0.4179      0.8065
groups_GLTP         1      0.4400      0.4400      0.6743      0.3678      0.5769      0.5000
groups_IP_trans     2      0.8043      0.4681      0.6625      0.4676      0.8125      0.5000
groups_START        1      0.1385      0.9663      0.0478      0.9249      0.0781      0.9551
groups_lipocalin    2      0.4306      0.8194      0.5703      0.6009      0.3333      0.7569
groups_scp2         2      0.5000      0.5000      0.5710      0.4661      0.5588      0.6912
ALL                 9      0.4763      0.6391      0.5331      0.5614      0.4980      0.6842

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5911      0.5625     0.0711  9
max valid BA                0.6111      0.6042     0.0667  9
best valid F1               0.5229      0.5714     0.1542  9
test BA                     0.5577      0.5726     0.0956  9
test F1                     0.4204      0.4400     0.1411  9
test sensitivity            0.4763      0.4400     0.2715  9
test specificity            0.6391      0.6170     0.2266  9
test precision              0.4938      0.5000     0.1588  9
test loss                   0.6912      0.6920     0.0145  9
FPR (FP/(FP+TN))            0.3609      0.3830     0.2266  9
FNR (FN/(FN+TP))            0.5237      0.5600     0.2715  9

=== abs(sensitivity-specificity) gap: mean=0.3645 median=0.2353 n=9 ===

=== By group ===
groups_CRAL-TRIO (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6122      0.6122     0.0000  1
  max valid BA                0.6122      0.6122     0.0000  1
  best valid F1               0.6490      0.6490     0.0000  1
  test BA                     0.5046      0.5046     0.0000  1
  test F1                     0.3299      0.3299     0.0000  1
  test sensitivity            0.2388      0.2388     0.0000  1
  test specificity            0.7705      0.7705     0.0000  1
  test precision              0.5333      0.5333     0.0000  1
  test loss                   0.6989      0.6989     0.0000  1
  FPR (FP/(FP+TN))            0.2295      0.2295     0.0000  1
  FNR (FN/(FN+TP))            0.7612      0.7612     0.0000  1

groups_GLTP (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5385      0.5385     0.0000  1
  max valid BA                0.5769      0.5769     0.0000  1
  best valid F1               0.6842      0.6842     0.0000  1
  test BA                     0.4400      0.4400     0.0000  1
  test F1                     0.4400      0.4400     0.0000  1
  test sensitivity            0.4400      0.4400     0.0000  1
  test specificity            0.4400      0.4400     0.0000  1
  test precision              0.4400      0.4400     0.0000  1
  test loss                   0.6920      0.6920     0.0000  1
  FPR (FP/(FP+TN))            0.5600      0.5600     0.0000  1
  FNR (FN/(FN+TP))            0.5600      0.5600     0.0000  1

groups_IP_trans (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6562      0.6562     0.0542  2
  max valid BA                0.6766      0.6766     0.0680  2
  best valid F1               0.6088      0.6088     0.0528  2
  test BA                     0.6362      0.6362     0.0899  2
  test F1                     0.5618      0.5618     0.0683  2
  test sensitivity            0.8043      0.8043     0.0307  2
  test specificity            0.4681      0.4681     0.2106  2
  test precision              0.4363      0.4363     0.0901  2
  test loss                   0.6914      0.6914     0.0105  2
  FPR (FP/(FP+TN))            0.5319      0.5319     0.2106  2
  FNR (FN/(FN+TP))            0.1957      0.1957     0.0307  2

groups_START (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5166      0.5166     0.0000  1
  max valid BA                0.5610      0.5610     0.0000  1
  best valid F1               0.3788      0.3788     0.0000  1
  test BA                     0.5524      0.5524     0.0000  1
  test F1                     0.2338      0.2338     0.0000  1
  test sensitivity            0.1385      0.1385     0.0000  1
  test specificity            0.9663      0.9663     0.0000  1
  test precision              0.7500      0.7500     0.0000  1
  test loss                   0.6733      0.6733     0.0000  1
  FPR (FP/(FP+TN))            0.0337      0.0337     0.0000  1
  FNR (FN/(FN+TP))            0.8615      0.8615     0.0000  1

groups_lipocalin (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5451      0.5451     0.0246  2
  max valid BA                0.5660      0.5660     0.0540  2
  best valid F1               0.3640      0.3640     0.2005  2
  test BA                     0.6250      0.6250     0.0687  2
  test F1                     0.4413      0.4413     0.1937  2
  test sensitivity            0.4306      0.4306     0.3339  2
  test specificity            0.8194      0.8194     0.1964  2
  test precision              0.6053      0.6053     0.1339  2
  test loss                   0.6877      0.6877     0.0299  2
  FPR (FP/(FP+TN))            0.1806      0.1806     0.1964  2
  FNR (FN/(FN+TP))            0.5694      0.5694     0.3339  2

groups_scp2 (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6250      0.6250     0.1144  2
  max valid BA                0.6324      0.6324     0.1040  2
  best valid F1               0.5242      0.5242     0.1386  2
  test BA                     0.5000      0.5000     0.1248  2
  test F1                     0.3869      0.3869     0.1750  2
  test sensitivity            0.5000      0.5000     0.2912  2
  test specificity            0.5000      0.5000     0.0416  2
  test precision              0.3190      0.3190     0.1145  2
  test loss                   0.6990      0.6990     0.0122  2
  FPR (FP/(FP+TN))            0.5000      0.5000     0.0416  2
  FNR (FN/(FN+TP))            0.5000      0.5000     0.2912  2
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.630         0.484    0.551       4.0              0.369         0.545     5.0               0.458          0.575
GLTP                     0.605         0.521    0.551       2.0              0.512         0.497     3.0               0.523          0.558
IP_trans                 0.722         0.680    0.633       3.0              0.677         0.643     2.4               0.590          0.641
LBP_BPI_CETP             0.719         0.798    0.713       2.0              0.798         0.710     1.6               0.784          0.668
START                    0.576         0.508    0.442       3.0              0.474         0.504     4.0               0.536          0.571
lipocalin                0.565         0.331    0.529       5.0              0.246         0.482     2.2               0.646          0.759
scp2                     0.651         0.489    0.468       2.8              0.593         0.430     2.6               0.642          0.542

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.545               0.503                  0.065                     0.151
net_AUC           0.555               0.568                  0.082                     0.093

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.524               0.493                  0.065                     0.186
net_AUC_prot           0.544               0.545                  0.096                     0.098

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.597               0.581                  0.085                     0.106
net_AUC_lipid           0.616               0.600                  0.100                     0.078

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.545  0.441      0.524     0.460
10     0.545  0.570      0.524     0.565
49     0.545  0.559      0.524     0.554
51     0.545  0.557      0.524     0.552
120    0.545  0.555      0.524     0.544

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.618         0.676      0.058          0.653              0.700           0.047
10        0.618         0.671      0.053          0.653              0.696           0.042
49        0.618         0.668      0.050          0.653              0.694           0.040
51        0.618         0.663      0.045          0.653              0.694           0.041
120       0.618         0.662      0.044          0.653              0.692           0.039

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.484  0.551      0.369     0.545     0.539         0.579      0.041          0.613              0.635           0.022
GLTP          0.521  0.551      0.512     0.497     0.543         0.625      0.082          0.565              0.633           0.068
IP_trans      0.680  0.633      0.677     0.643     0.680         0.679     -0.001          0.693              0.694           0.001
LBP_BPI_CETP  0.798  0.713      0.798     0.710     0.798         0.807      0.008          0.801              0.811           0.010
START         0.508  0.442      0.474     0.504     0.536         0.619      0.083          0.606              0.642           0.037
lipocalin     0.331  0.529      0.246     0.482     0.669         0.714      0.046          0.673              0.746           0.072
scp2          0.489  0.468      0.593     0.430     0.562         0.610      0.049          0.622              0.684           0.062

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.545               0.503                  0.065                     0.151
net               0.555               0.568                  0.082                     0.093
fit_chem          0.618               0.590                  0.052                     0.101
fit_chem_net      0.662               0.649                  0.053                     0.078
increment         0.044               0.029                  0.032                     0.032

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.524               0.493                  0.065                     0.186
net_prot               0.544               0.545                  0.096                     0.098
fit_chem_prot          0.653               0.662                  0.055                     0.078
fit_chem_net_prot      0.692               0.680                  0.052                     0.066
increment_prot         0.039               0.019                  0.035                     0.029
```
