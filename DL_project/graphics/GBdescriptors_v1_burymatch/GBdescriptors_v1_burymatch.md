# GBdescriptors_v1_burymatch

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'GBdescriptors_v1_burymatch'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5731      0.4328      0.4634      0.5455      0.5731      0.4387
groups_GLTP            5      0.6080      0.6000      0.6245      0.4968      0.6154      0.6846
groups_IP_trans        5      0.5391      0.5404      0.5807      0.5107      0.5833      0.5489
groups_LBP_BPI_CETP    5      0.5565      0.7064      0.3892      0.6974      0.5083      0.7149
groups_ML              5      0.3200      0.6800      0.4357      0.6961      0.5200      0.7400
groups_OSBP            5      0.4667      0.4667      0.6863      0.4113      0.8667      0.5000
groups_START           5      0.4523      0.5438      0.5754      0.5000      0.5000      0.6000
groups_lipocalin       5      0.7722      0.2778      0.6783      0.3606      0.7889      0.3056
groups_scp2            5      0.6118      0.5118      0.5157      0.6222      0.6471      0.6059
ALL                   45      0.5444      0.5288      0.5499      0.5379      0.6225      0.5710

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5967      0.6000     0.0911  45
max valid BA                0.6300      0.6299     0.1006  45
best valid F1               0.5834      0.5714     0.1176  45
test BA                     0.5366      0.5000     0.1053  45
test F1                     0.3970      0.4762     0.2424  45
test sensitivity            0.5444      0.6800     0.3854  45
test specificity            0.5288      0.5000     0.3243  45
test precision              0.4052      0.3964     0.1814  40
test loss                   0.8493      0.7070     0.3851  45
FPR (FP/(FP+TN))            0.4712      0.5000     0.3243  45
FNR (FN/(FN+TP))            0.4556      0.3200     0.3854  45

=== abs(sensitivity-specificity) gap: mean=0.5973 median=0.6471 n=45 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5059      0.5000     0.0088  5
  max valid BA                0.5139      0.5101     0.0153  5
  best valid F1               0.5459      0.6772     0.2147  5
  test BA                     0.5030      0.5000     0.0094  5
  test F1                     0.4070      0.6667     0.3716  5
  test sensitivity            0.5731      0.9254     0.5239  5
  test specificity            0.4328      0.0984     0.5190  5
  test precision              0.5261      0.5234     0.0068  3
  test loss                   1.3239      1.2399     0.6086  5
  FPR (FP/(FP+TN))            0.5672      0.9016     0.5190  5
  FNR (FN/(FN+TP))            0.4269      0.0746     0.5239  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6500      0.6154     0.0479  5
  max valid BA                0.7154      0.7308     0.0658  5
  best valid F1               0.6881      0.7317     0.1575  5
  test BA                     0.6040      0.6200     0.0590  5
  test F1                     0.5709      0.6415     0.1624  5
  test sensitivity            0.6080      0.6800     0.3155  5
  test specificity            0.6000      0.5600     0.2757  5
  test precision              0.6557      0.6000     0.1971  5
  test loss                   0.7069      0.6899     0.0493  5
  FPR (FP/(FP+TN))            0.4000      0.4400     0.2757  5
  FNR (FN/(FN+TP))            0.3920      0.3200     0.3155  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5661      0.5660     0.0675  5
  max valid BA                0.6069      0.6299     0.0849  5
  best valid F1               0.5430      0.5588     0.0474  5
  test BA                     0.5398      0.5453     0.0401  5
  test F1                     0.3639      0.4928     0.2170  5
  test sensitivity            0.5391      0.6957     0.4016  5
  test specificity            0.5404      0.4894     0.3919  5
  test precision              0.3817      0.3848     0.0428  4
  test loss                   0.8250      0.7119     0.2260  5
  FPR (FP/(FP+TN))            0.4596      0.5106     0.3919  5
  FNR (FN/(FN+TP))            0.4609      0.3043     0.4016  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6116      0.5864     0.1114  5
  max valid BA                0.6664      0.6609     0.0803  5
  best valid F1               0.6008      0.6000     0.0686  5
  test BA                     0.6315      0.6166     0.1336  5
  test F1                     0.3975      0.5570     0.3325  5
  test sensitivity            0.5565      0.7826     0.4952  5
  test specificity            0.7064      0.6596     0.2980  5
  test precision              0.4958      0.5147     0.0730  4
  test loss                   0.7166      0.6852     0.0874  5
  FPR (FP/(FP+TN))            0.2936      0.3404     0.2980  5
  FNR (FN/(FN+TP))            0.4435      0.2174     0.4952  5

groups_ML (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6300      0.6500     0.0837  5
  max valid BA                0.6300      0.6500     0.0837  5
  best valid F1               0.5506      0.5556     0.0483  5
  test BA                     0.5000      0.5000     0.0612  5
  test F1                     0.2278      0.2500     0.2360  5
  test sensitivity            0.3200      0.2000     0.4147  5
  test specificity            0.6800      0.8000     0.3271  5
  test precision              0.2509      0.3095     0.1721  4
  test loss                   0.7932      0.7231     0.1885  5
  FPR (FP/(FP+TN))            0.3200      0.2000     0.3271  5
  FNR (FN/(FN+TP))            0.6800      0.8000     0.4147  5

groups_OSBP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6833      0.7500     0.1087  5
  max valid BA                0.7167      0.7500     0.1394  5
  best valid F1               0.6633      0.6667     0.1193  5
  test BA                     0.4667      0.4167     0.1728  5
  test F1                     0.2905      0.2857     0.2976  5
  test sensitivity            0.4667      0.3333     0.5055  5
  test specificity            0.4667      0.5000     0.2739  5
  test precision              0.2167      0.2500     0.2173  5
  test loss                   1.0687      0.7011     0.8280  5
  FPR (FP/(FP+TN))            0.5333      0.5000     0.2739  5
  FNR (FN/(FN+TP))            0.5333      0.6667     0.5055  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5472     0.0377  5
  max valid BA                0.5616      0.5534     0.0296  5
  best valid F1               0.5404      0.5385     0.0658  5
  test BA                     0.4981      0.4822     0.0952  5
  test F1                     0.3969      0.4000     0.1866  5
  test sensitivity            0.4523      0.3692     0.2968  5
  test specificity            0.5438      0.4831     0.3032  5
  test precision              0.4187      0.4113     0.1205  5
  test loss                   0.7067      0.7029     0.0236  5
  FPR (FP/(FP+TN))            0.4562      0.5169     0.3032  5
  FNR (FN/(FN+TP))            0.5477      0.6308     0.2968  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5472      0.5208     0.1172  5
  max valid BA                0.5972      0.6181     0.1106  5
  best valid F1               0.5294      0.5400     0.1132  5
  test BA                     0.5250      0.5000     0.1480  5
  test F1                     0.4657      0.5000     0.1704  5
  test sensitivity            0.7722      0.8333     0.3206  5
  test specificity            0.2778      0.3333     0.1981  5
  test precision              0.3379      0.3333     0.1164  5
  test loss                   0.8100      0.7641     0.1595  5
  FPR (FP/(FP+TN))            0.7222      0.6667     0.1981  5
  FNR (FN/(FN+TP))            0.2278      0.1667     0.3206  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6265      0.6029     0.0710  5
  max valid BA                0.6618      0.6324     0.0864  5
  best valid F1               0.5890      0.5641     0.0851  5
  test BA                     0.5618      0.5588     0.0731  5
  test F1                     0.4532      0.4762     0.1303  5
  test sensitivity            0.6118      0.5882     0.2778  5
  test specificity            0.5118      0.5294     0.2931  5
  test precision              0.3941      0.3846     0.0805  5
  test loss                   0.6927      0.6998     0.0211  5
  FPR (FP/(FP+TN))            0.4882      0.4706     0.2931  5
  FNR (FN/(FN+TP))            0.3882      0.4118     0.2778  5
```

## AUC vs chemistry null model, in-sample increment

### features = tanimoto (full molecular structure)

```
########## split = valid ##########

--- null model (null_model.py), features = tanimoto (tanimoto), epoch 120 ---
=== mean over seeds ===
              sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid
fam                                                                                                                                        
CRAL-TRIO                0.802         0.474    0.461       4.0              0.497         0.473     5.0               0.529          0.436
GLTP                     0.615         0.539    0.523       2.0              0.501         0.495     3.0               0.502          0.576
IP_trans                 0.809         0.680    0.468       3.0              0.696         0.512     2.4               0.535          0.397
LBP_BPI_CETP             0.809         0.677    0.548       2.0              0.692         0.576     1.6               0.662          0.533
START                    0.789         0.497    0.456       3.0              0.498         0.515     4.0               0.533          0.460
lipocalin                0.832         0.487    0.388       5.0              0.462         0.254     2.2               0.698          0.346
scp2                     0.834         0.621    0.619       2.8              0.519         0.537     2.6               0.604          0.613

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.568               0.564                  0.075                     0.090
net_AUC           0.495               0.484                  0.103                     0.075

=== the same rows ranked INSIDE each protein ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.552               0.529                  0.068                     0.098
net_AUC_prot           0.480               0.499                  0.106                     0.105

=== the same rows ranked INSIDE each lipid class ===
104 lipid class blocks across 35 family-seed splits carry a usable ranking (median 3 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15       0.58               0.546                  0.070                     0.075
net_AUC_lipid            0.48               0.465                  0.112                     0.097

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.568  0.482      0.552     0.481
10     0.568  0.500      0.552     0.508
49     0.568  0.504      0.552     0.497
51     0.568  0.507      0.552     0.501
120    0.568  0.495      0.552     0.480

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.594         0.665      0.071          0.654              0.715           0.060
10        0.594         0.658      0.064          0.654              0.697           0.042
49        0.594         0.655      0.061          0.654              0.721           0.067
51        0.594         0.657      0.063          0.654              0.721           0.067
120       0.594         0.642      0.048          0.654              0.694           0.040

3. mean over seeds, epoch 120
               chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                 
CRAL-TRIO     0.474  0.461      0.497     0.473     0.547         0.580      0.032          0.641              0.671           0.030
GLTP          0.539  0.523      0.501     0.495     0.542         0.594      0.052          0.596              0.641           0.046
IP_trans      0.680  0.468      0.696     0.512     0.680         0.697      0.017          0.712              0.729           0.017
LBP_BPI_CETP  0.677  0.548      0.692     0.576     0.677         0.726      0.049          0.714              0.753           0.039
START         0.497  0.456      0.498     0.515     0.527         0.595      0.067          0.611              0.645           0.034
lipocalin     0.487  0.388      0.462     0.254     0.563         0.624      0.061          0.617              0.707           0.091
scp2          0.621  0.619      0.519     0.537     0.621         0.681      0.060          0.689              0.712           0.023

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.568               0.564                  0.075                     0.090
net               0.495               0.484                  0.103                     0.075
fit_chem          0.594               0.578                  0.068                     0.065
fit_chem_net      0.642               0.618                  0.068                     0.058
increment         0.048               0.034                  0.065                     0.018

=== the same rows ranked INSIDE each protein, epoch 120 ===
109 protein blocks across 35 family-seed splits carry a usable ranking (median 3 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.552               0.529                  0.068                     0.098
net_prot               0.480               0.499                  0.106                     0.105
fit_chem_prot          0.654               0.661                  0.043                     0.050
fit_chem_net_prot      0.694               0.686                  0.052                     0.043
increment_prot         0.040               0.025                  0.044                     0.024

wrote : /tmp/tmp.XdW9yoZurb
```

### features = the label's own --good_descriptors/--bad_descriptors

Failed: FileNotFoundError: [Errno 2] No such file or directory: '/home/andrei/DL_project_5/DL_project/analysis/.null_model_cache.json.tmp' -> '/home/andrei/DL_project_5/DL_project/analysis/.null_model_cache.json' -- rerun for the full output: `python3 analysis/full_label_report.py --label GBdescriptors_v1_burymatch --seeds=0,1,2,3,4 --scores=<checkpoint_scores.py output>`
