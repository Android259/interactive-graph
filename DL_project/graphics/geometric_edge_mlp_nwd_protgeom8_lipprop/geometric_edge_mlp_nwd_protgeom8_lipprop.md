# geometric_edge_mlp_nwd_protgeom8_lipprop

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_nwd_protgeom8_lipprop'
rows: 19

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.9104      0.1093      0.5543      0.5005      0.9403      0.1344
groups_GLTP            2      0.8200      0.1800      0.6576      0.5009      0.8269      0.2500
groups_IP_trans        3      0.4783      0.6596      0.6556      0.5725      0.6250      0.6383
groups_LBP_BPI_CETP    3      0.2899      0.8511      0.6985      0.5133      0.3194      0.8085
groups_START           3      0.8769      0.2921      0.6928      0.5518      0.8542      0.3184
groups_lipocalin       3      0.7685      0.5324      0.5953      0.4134      0.7778      0.5139
groups_scp2            2      0.3235      0.8235      0.7011      0.5559      0.4706      0.8676
ALL                   19      0.6452      0.4916      0.6477      0.5141      0.6918      0.4987

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5953      0.5735     0.0805  19
max valid BA                0.6331      0.6321     0.0739  19
best valid F1               0.6184      0.6170     0.0865  19
test BA                     0.5684      0.5538     0.0834  19
test F1                     0.5005      0.5856     0.2091  19
test sensitivity            0.6452      0.7826     0.3300  19
test specificity            0.4916      0.5506     0.3637  19
test precision              0.5161      0.5000     0.1229  18
test loss                   0.7131      0.6937     0.1000  19
FPR (FP/(FP+TN))            0.5084      0.4494     0.3637  19
FNR (FN/(FN+TP))            0.3548      0.2174     0.3300  19

=== abs(sensitivity-specificity) gap: mean=0.6015 median=0.6000 n=19 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5374      0.5254     0.0218  3
  max valid BA                0.5519      0.5329     0.0396  3
  best valid F1               0.7036      0.6947     0.0189  3
  test BA                     0.5099      0.5164     0.0203  3
  test F1                     0.6667      0.6915     0.0453  3
  test sensitivity            0.9104      0.9701     0.1301  3
  test specificity            0.1093      0.0820     0.0932  3
  test precision              0.5280      0.5317     0.0115  3
  test loss                   0.7255      0.7363     0.0322  3
  FPR (FP/(FP+TN))            0.8907      0.9180     0.0932  3
  FNR (FN/(FN+TP))            0.0896      0.0299     0.1301  3

groups_GLTP (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5385      0.5385     0.0272  2
  max valid BA                0.6731      0.6731     0.0000  2
  best valid F1               0.7365      0.7365     0.0090  2
  test BA                     0.5000      0.5000     0.0000  2
  test F1                     0.6211      0.6211     0.0081  2
  test sensitivity            0.8200      0.8200     0.0283  2
  test specificity            0.1800      0.1800     0.0283  2
  test precision              0.5000      0.5000     0.0000  2
  test loss                   0.6896      0.6896     0.0061  2
  FPR (FP/(FP+TN))            0.8200      0.8200     0.0283  2
  FNR (FN/(FN+TP))            0.1800      0.1800     0.0283  2

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6316      0.6290     0.0400  3
  max valid BA                0.6587      0.6507     0.0314  3
  best valid F1               0.5844      0.5797     0.0289  3
  test BA                     0.5689      0.5615     0.0191  3
  test F1                     0.3976      0.4706     0.1526  3
  test sensitivity            0.4783      0.5217     0.3283  3
  test specificity            0.6596      0.6596     0.3191  3
  test precision              0.5153      0.4286     0.2055  3
  test loss                   0.6738      0.6643     0.0173  3
  FPR (FP/(FP+TN))            0.3404      0.3404     0.3191  3
  FNR (FN/(FN+TP))            0.5217      0.4783     0.3283  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5640      0.5310     0.0854  3
  max valid BA                0.5980      0.5988     0.0634  3
  best valid F1               0.5360      0.5231     0.0503  3
  test BA                     0.5705      0.5111     0.1126  3
  test F1                     0.2310      0.0800     0.3332  3
  test sensitivity            0.2899      0.0435     0.4649  3
  test specificity            0.8511      0.9787     0.2398  3
  test precision              0.4936      0.4936     0.0091  2
  test loss                   0.8043      0.6694     0.2391  3
  FPR (FP/(FP+TN))            0.1489      0.0213     0.2398  3
  FNR (FN/(FN+TP))            0.7101      0.9565     0.4649  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5863      0.6112     0.0455  3
  max valid BA                0.6245      0.6112     0.0501  3
  best valid F1               0.6209      0.6170     0.0110  3
  test BA                     0.5845      0.5538     0.0946  3
  test F1                     0.6201      0.5953     0.0515  3
  test sensitivity            0.8769      0.8308     0.0936  3
  test specificity            0.2921      0.2921     0.2584  3
  test precision              0.4860      0.4569     0.0781  3
  test loss                   0.7125      0.7109     0.0044  3
  FPR (FP/(FP+TN))            0.7079      0.7079     0.2584  3
  FNR (FN/(FN+TP))            0.1231      0.1692     0.0936  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6458      0.7014     0.1275  3
  max valid BA                0.6620      0.7222     0.1165  3
  best valid F1               0.5995      0.6353     0.0775  3
  test BA                     0.6505      0.6736     0.1403  3
  test F1                     0.5968      0.5843     0.1072  3
  test sensitivity            0.7685      0.7222     0.1850  3
  test specificity            0.5324      0.6250     0.4653  3
  test precision              0.5567      0.4906     0.2627  3
  test loss                   0.6653      0.6906     0.0962  3
  FPR (FP/(FP+TN))            0.4676      0.3750     0.4653  3
  FNR (FN/(FN+TP))            0.2315      0.2778     0.1850  3

groups_scp2 (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6691      0.6691     0.1352  2
  max valid BA                0.6985      0.6985     0.1144  2
  best valid F1               0.5717      0.5717     0.1898  2
  test BA                     0.5735      0.5735     0.0208  2
  test F1                     0.3649      0.3649     0.1304  2
  test sensitivity            0.3235      0.3235     0.2080  2
  test specificity            0.8235      0.8235     0.1664  2
  test precision              0.5222      0.5222     0.1100  2
  test loss                   0.7132      0.7132     0.0808  2
  FPR (FP/(FP+TN))            0.1765      0.1765     0.1664  2
  FNR (FN/(FN+TP))            0.6765      0.6765     0.2080  2
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.476    0.489     4.000              0.347         0.486   5.000               0.480          0.550
GLTP                     0.595         0.484    0.442     2.000              0.488         0.496   3.000               0.494          0.510
IP_trans                 0.727         0.727    0.605     3.000              0.720         0.644   2.667               0.664          0.626
LBP_BPI_CETP             0.721         0.811    0.576     2.000              0.811         0.578   1.667               0.792          0.607
START                    0.574         0.487    0.580     3.000              0.460         0.559   4.000               0.519          0.564
lipocalin                0.558         0.299    0.570     5.000              0.215         0.558   2.000               0.679          0.497
scp2                     0.632         0.441    0.701     2.667              0.538         0.625   2.667               0.621          0.583

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.532               0.488                  0.036                     0.176
net_AUC           0.566               0.582                  0.087                     0.083

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.471                  0.044                     0.205
net_AUC_prot           0.564               0.576                  0.101                     0.059

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.607               0.581                  0.084                     0.115
net_AUC_lipid           0.562               0.561                  0.097                     0.048

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.532  0.451      0.511     0.468
10     0.532  0.511      0.511     0.488
49     0.532  0.546      0.511     0.506
51     0.532  0.553      0.511     0.531
120    0.532  0.566      0.511     0.564

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.622         0.670      0.047          0.654              0.692           0.039
10        0.622         0.664      0.041          0.654              0.694           0.040
49        0.622         0.664      0.042          0.654              0.694           0.040
51        0.622         0.670      0.048          0.654              0.692           0.039
120       0.622         0.674      0.052          0.654              0.704           0.050

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.476  0.489      0.347     0.486     0.524         0.584      0.060          0.589              0.630           0.041
GLTP          0.484  0.442      0.488     0.496     0.520         0.586      0.066          0.547              0.628           0.081
IP_trans      0.727  0.605      0.720     0.644     0.727         0.745      0.019          0.730              0.765           0.035
LBP_BPI_CETP  0.811  0.576      0.811     0.578     0.811         0.815      0.005          0.815              0.823           0.008
START         0.487  0.580      0.460     0.559     0.513         0.596      0.083          0.561              0.615           0.054
lipocalin     0.299  0.570      0.215     0.558     0.701         0.739      0.038          0.698              0.761           0.062
scp2          0.441  0.701      0.538     0.625     0.562         0.656      0.094          0.634              0.706           0.072

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.532               0.488                  0.036                     0.176
net               0.566               0.582                  0.087                     0.083
fit_chem          0.622               0.590                  0.035                     0.121
fit_chem_net      0.674               0.670                  0.044                     0.093
increment         0.052               0.023                  0.044                     0.033

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.471                  0.044                     0.205
net_prot               0.564               0.576                  0.101                     0.059
fit_chem_prot          0.654               0.659                  0.037                     0.099
fit_chem_net_prot      0.704               0.729                  0.044                     0.082
increment_prot         0.050               0.037                  0.036                     0.025
```
