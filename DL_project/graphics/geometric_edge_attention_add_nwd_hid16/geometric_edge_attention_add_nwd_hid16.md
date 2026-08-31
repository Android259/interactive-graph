# geometric_edge_attention_add_nwd_hid16

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention_add_nwd_hid16'
rows: 21

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.9353      0.0820      0.7467      0.4573      0.9104      0.1398
groups_GLTP            3      0.6933      0.3467      0.6608      0.4317      0.7051      0.3718
groups_IP_trans        3      0.6232      0.6241      0.7567      0.6152      0.6944      0.6809
groups_LBP_BPI_CETP    3      0.6812      0.4539      0.7526      0.5421      0.6667      0.4539
groups_START           3      0.9333      0.1461      0.8020      0.5904      0.9375      0.1498
groups_lipocalin       3      0.7870      0.3380      0.5576      0.4944      0.8519      0.3241
groups_scp2            3      0.6471      0.6569      0.6789      0.4330      0.7255      0.7255
ALL                   21      0.7572      0.3782      0.7079      0.5092      0.7845      0.4065

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5955      0.5655     0.0861  21
max valid BA                0.6550      0.6346     0.0960  21
best valid F1               0.6536      0.6667     0.0527  21
test BA                     0.5677      0.5596     0.0749  21
test F1                     0.5468      0.5882     0.1141  21
test sensitivity            0.7572      0.8507     0.2672  21
test specificity            0.3782      0.3191     0.3403  21
test precision              0.4887      0.4724     0.1467  21
test loss                   0.6932      0.6870     0.0865  21
FPR (FP/(FP+TN))            0.6218      0.6809     0.3403  21
FNR (FN/(FN+TP))            0.2428      0.1493     0.2672  21

=== abs(sensitivity-specificity) gap: mean=0.6085 median=0.6984 n=21 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5251      0.5242     0.0024  3
  max valid BA                0.5874      0.5843     0.0233  3
  best valid F1               0.7020      0.7053     0.0067  3
  test BA                     0.5086      0.5082     0.0507  3
  test F1                     0.6746      0.6907     0.0393  3
  test sensitivity            0.9353      0.9552     0.0766  3
  test specificity            0.0820      0.0656     0.0751  3
  test precision              0.5280      0.5276     0.0283  3
  test loss                   0.6834      0.6863     0.0056  3
  FPR (FP/(FP+TN))            0.9180      0.9344     0.0751  3
  FNR (FN/(FN+TP))            0.0647      0.0448     0.0766  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5385      0.5385     0.0385  3
  max valid BA                0.5577      0.5385     0.0693  3
  best valid F1               0.6786      0.6757     0.0136  3
  test BA                     0.5200      0.5000     0.0721  3
  test F1                     0.5399      0.6197     0.1804  3
  test sensitivity            0.6933      0.8800     0.4314  3
  test specificity            0.3467      0.0400     0.5662  3
  test precision              0.6594      0.5000     0.2952  3
  test loss                   0.7066      0.7035     0.0299  3
  FPR (FP/(FP+TN))            0.6533      0.9600     0.5662  3
  FNR (FN/(FN+TP))            0.3067      0.1200     0.4314  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6876      0.6702     0.0734  3
  max valid BA                0.7434      0.7677     0.0525  3
  best valid F1               0.6677      0.6897     0.0527  3
  test BA                     0.6237      0.6596     0.0882  3
  test F1                     0.4749      0.5897     0.2014  3
  test sensitivity            0.6232      0.6957     0.4178  3
  test specificity            0.6241      0.6809     0.2809  3
  test precision              0.4448      0.4182     0.0625  3
  test loss                   0.6433      0.6478     0.0550  3
  FPR (FP/(FP+TN))            0.3759      0.3191     0.2809  3
  FNR (FN/(FN+TP))            0.3768      0.3043     0.4178  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5603      0.5567     0.0621  3
  max valid BA                0.6766      0.7176     0.0988  3
  best valid F1               0.6083      0.6190     0.0643  3
  test BA                     0.5675      0.5606     0.0713  3
  test F1                     0.4834      0.4848     0.0121  3
  test sensitivity            0.6812      0.6957     0.3263  3
  test specificity            0.4539      0.4255     0.4687  3
  test precision              0.4760      0.3721     0.2187  3
  test loss                   0.7236      0.7305     0.1277  3
  FPR (FP/(FP+TN))            0.5461      0.5745     0.4687  3
  FNR (FN/(FN+TP))            0.3188      0.3043     0.3263  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5437      0.5486     0.0247  3
  max valid BA                0.5595      0.5714     0.0224  3
  best valid F1               0.6110      0.6095     0.0053  3
  test BA                     0.5397      0.5225     0.0397  3
  test F1                     0.6018      0.6047     0.0247  3
  test sensitivity            0.9333      0.9231     0.0622  3
  test specificity            0.1461      0.1461     0.1011  3
  test precision              0.4448      0.4333     0.0241  3
  test loss                   0.7863      0.6962     0.1595  3
  FPR (FP/(FP+TN))            0.8539      0.8539     0.1011  3
  FNR (FN/(FN+TP))            0.0667      0.0769     0.0622  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5880      0.6181     0.0582  3
  max valid BA                0.7153      0.7222     0.0870  3
  best valid F1               0.6437      0.6429     0.0912  3
  test BA                     0.5625      0.5139     0.0903  3
  test F1                     0.5031      0.5035     0.0853  3
  test sensitivity            0.7870      0.8333     0.2395  3
  test specificity            0.3380      0.5000     0.2807  3
  test precision              0.3788      0.3455     0.0657  3
  test loss                   0.6862      0.6961     0.0197  3
  FPR (FP/(FP+TN))            0.6620      0.5000     0.2807  3
  FNR (FN/(FN+TP))            0.2130      0.1667     0.2395  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7255      0.7500     0.0557  3
  max valid BA                0.7451      0.7500     0.0370  3
  best valid F1               0.6639      0.6667     0.0376  3
  test BA                     0.6520      0.6471     0.0225  3
  test F1                     0.5502      0.5405     0.0416  3
  test sensitivity            0.6471      0.5882     0.1556  3
  test specificity            0.6569      0.7059     0.1114  3
  test precision              0.4889      0.5000     0.0192  3
  test loss                   0.6230      0.6296     0.0519  3
  FPR (FP/(FP+TN))            0.3431      0.2941     0.1114  3
  FNR (FN/(FN+TP))            0.3529      0.4118     0.1556  3
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.626         0.476    0.397     4.000              0.347         0.377   5.000               0.480          0.439
GLTP                     0.595         0.484    0.443     2.000              0.488         0.472   3.000               0.494          0.532
IP_trans                 0.727         0.727    0.478     3.000              0.720         0.467   2.667               0.664          0.506
LBP_BPI_CETP             0.721         0.811    0.582     2.000              0.811         0.654   1.667               0.792          0.658
START                    0.574         0.487    0.534     3.000              0.460         0.487   4.000               0.519          0.522
lipocalin                0.558         0.299    0.317     5.000              0.215         0.251   2.000               0.679          0.439
scp2                     0.632         0.441    0.582     2.667              0.538         0.525   2.667               0.621          0.510

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.532               0.488                  0.036                     0.176
net_AUC           0.476               0.488                  0.106                     0.099

=== the same rows ranked INSIDE each protein ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.511               0.471                  0.044                     0.205
net_AUC_prot           0.462               0.446                  0.114                     0.125

=== the same rows ranked INSIDE each lipid class ===
63 lipid class blocks across 21 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.607               0.581                  0.084                     0.115
net_AUC_lipid           0.515               0.513                  0.149                     0.074

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.532  0.554      0.511     0.568
10     0.532  0.596      0.511     0.569
49     0.532  0.560      0.511     0.557
51     0.532  0.539      0.511     0.525
120    0.532  0.476      0.511     0.462

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.622         0.653      0.030          0.654              0.701           0.047
10        0.622         0.680      0.058          0.654              0.697           0.043
49        0.622         0.686      0.064          0.654              0.694           0.040
51        0.622         0.682      0.059          0.654              0.702           0.048
120       0.622         0.672      0.050          0.654              0.692           0.038

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.476  0.397      0.347     0.377     0.524         0.581      0.057          0.589              0.580          -0.009
GLTP          0.484  0.443      0.488     0.472     0.520         0.562      0.042          0.547              0.580           0.033
IP_trans      0.727  0.478      0.720     0.467     0.727         0.767      0.041          0.730              0.785           0.054
LBP_BPI_CETP  0.811  0.582      0.811     0.654     0.811         0.819      0.009          0.815              0.824           0.008
START         0.487  0.534      0.460     0.487     0.513         0.591      0.078          0.561              0.627           0.066
lipocalin     0.299  0.317      0.215     0.251     0.701         0.766      0.066          0.698              0.788           0.090
scp2          0.441  0.582      0.538     0.525     0.562         0.617      0.055          0.634              0.659           0.025

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.532               0.488                  0.036                     0.176
net               0.476               0.488                  0.106                     0.099
fit_chem          0.622               0.590                  0.035                     0.121
fit_chem_net      0.672               0.660                  0.058                     0.108
increment         0.050               0.047                  0.058                     0.022

=== the same rows ranked INSIDE each protein, epoch 120 ===
65 protein blocks across 21 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.511               0.471                  0.044                     0.205
net_prot               0.462               0.446                  0.114                     0.125
fit_chem_prot          0.654               0.659                  0.037                     0.099
fit_chem_net_prot      0.692               0.686                  0.067                     0.104
increment_prot         0.038               0.014                  0.047                     0.034
```
