# geometric_edge_attention

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention'
rows: 33

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5612      0.4262      0.4897      0.5115      0.5821      0.4226
groups_GLTP            4      0.3700      0.6800      0.4483      0.5477      0.4135      0.6154
groups_IP_trans        4      0.7500      0.3457      0.5455      0.4439      0.7500      0.2872
groups_LBP_BPI_CETP    5      0.7130      0.3064      0.5830      0.4075      0.7583      0.3404
groups_START           5      0.2462      0.7596      0.4184      0.6102      0.2500      0.7955
groups_lipocalin       5      0.3278      0.6556      0.4122      0.6061      0.3778      0.6639
groups_scp2            5      0.4588      0.5824      0.4890      0.5110      0.5176      0.6176
ALL                   33      0.4853      0.5380      0.4829      0.5212      0.5177      0.5397

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5287      0.5000     0.0500  33
max valid BA                0.5305      0.5056     0.0500  33
best valid F1               0.5698      0.5106     0.0766  33
test BA                     0.5116      0.5000     0.0458  33
test F1                     0.3197      0.3922     0.2561  33
test sensitivity            0.4853      0.4118     0.4407  33
test specificity            0.5380      0.6806     0.4399  33
test precision              0.4537      0.3784     0.1962  23
test loss                   0.6949      0.6931     0.0065  33
FPR (FP/(FP+TN))            0.4620      0.3194     0.4399  33
FNR (FN/(FN+TP))            0.5147      0.5882     0.4407  33

=== abs(sensitivity-specificity) gap: mean=0.8153 median=1.0000 n=33 ===

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

groups_GLTP (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5144      0.5000     0.0288  4
  max valid BA                0.5144      0.5000     0.0288  4
  best valid F1               0.6667      0.6667     0.0000  4
  test BA                     0.5250      0.5000     0.0500  4
  test F1                     0.3030      0.2727     0.3534  4
  test sensitivity            0.3700      0.2400     0.4771  4
  test specificity            0.6800      0.8600     0.4722  4
  test precision              0.5658      0.5658     0.0930  2
  test loss                   0.6935      0.6934     0.0005  4
  FPR (FP/(FP+TN))            0.3200      0.1400     0.4722  4
  FNR (FN/(FN+TP))            0.6300      0.7600     0.4771  4

groups_IP_trans (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5186      0.5000     0.0372  4
  max valid BA                0.5213      0.5053     0.0358  4
  best valid F1               0.5167      0.5080     0.0194  4
  test BA                     0.5479      0.5000     0.0957  4
  test F1                     0.4006      0.4946     0.2729  4
  test sensitivity            0.7500      1.0000     0.5000  4
  test specificity            0.3457      0.1915     0.4721  4
  test precision              0.3665      0.3286     0.0657  3
  test loss                   0.6987      0.6947     0.0113  4
  FPR (FP/(FP+TN))            0.6543      0.8085     0.4721  4
  FNR (FN/(FN+TP))            0.2500      0.0000     0.5000  4

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

