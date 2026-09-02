# descriptors_pair_only_rankprot

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_pair_only_rankprot'
rows: 34

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6896      0.2951      0.6669      0.3576      0.7134      0.3065
groups_GLTP            5      0.6480      0.4240      0.5254      0.5289      0.6154      0.4769
groups_IP_trans        5      0.4696      0.5830      0.4601      0.5826      0.4750      0.6085
groups_LBP_BPI_CETP    5      0.5043      0.4979      0.4469      0.6090      0.5250      0.5404
groups_START           5      0.3262      0.6809      0.4423      0.5997      0.3563      0.7011
groups_lipocalin       5      0.5556      0.4278      0.5817      0.4422      0.5556      0.4278
groups_scp2            4      0.4118      0.6397      0.5823      0.5156      0.3824      0.6618
ALL                   34      0.5180      0.5030      0.5278      0.5195      0.5215      0.5280

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5248      0.5122     0.0488  34
max valid BA                0.5403      0.5203     0.0558  34
best valid F1               0.4630      0.5189     0.2110  34
test BA                     0.5105      0.5000     0.0354  34
test F1                     0.3557      0.4632     0.2538  34
test sensitivity            0.5180      0.6252     0.4229  34
test specificity            0.5030      0.4468     0.4229  34
test precision              0.4089      0.3905     0.1335  26
test loss                   0.6907      0.6976     0.0606  34
FPR (FP/(FP+TN))            0.4970      0.5532     0.4229  34
FNR (FN/(FN+TP))            0.4820      0.3748     0.4229  34

=== abs(sensitivity-specificity) gap: mean=0.7881 median=0.9648 n=34 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5097      0.5000     0.0154  5
  max valid BA                0.5163      0.5081     0.0212  5
  best valid F1               0.5757      0.6837     0.2094  5
  test BA                     0.4923      0.5000     0.0229  5
  test F1                     0.5136      0.6391     0.2922  5
  test sensitivity            0.6896      0.8060     0.4135  5
  test specificity            0.2951      0.2131     0.4120  5
  test precision              0.5162      0.5234     0.0186  4
  test loss                   0.7339      0.7197     0.0369  5
  FPR (FP/(FP+TN))            0.7049      0.7869     0.4120  5
  FNR (FN/(FN+TP))            0.3104      0.1940     0.4135  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5462      0.5192     0.0823  5
  max valid BA                0.5615      0.5192     0.0786  5
  best valid F1               0.6215      0.6667     0.1567  5
  test BA                     0.5360      0.5000     0.0498  5
  test F1                     0.4925      0.6667     0.2952  5
  test sensitivity            0.6480      0.9200     0.4608  5
  test specificity            0.4240      0.2800     0.4704  5
  test precision              0.5569      0.5305     0.0786  4
  test loss                   0.6523      0.6700     0.0683  5
  FPR (FP/(FP+TN))            0.5760      0.7200     0.4704  5
  FNR (FN/(FN+TP))            0.3520      0.0800     0.4608  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5418      0.5213     0.0631  5
  max valid BA                0.5736      0.5213     0.0917  5
  best valid F1               0.4032      0.5161     0.2471  5
  test BA                     0.5263      0.5106     0.0386  5
  test F1                     0.2928      0.4638     0.2677  5
  test sensitivity            0.4696      0.6522     0.4491  5
  test specificity            0.5830      0.5319     0.4228  5
  test precision              0.3622      0.3478     0.0381  3
  test loss                   0.6655      0.6809     0.0336  5
  FPR (FP/(FP+TN))            0.4170      0.4681     0.4228  5
  FNR (FN/(FN+TP))            0.5304      0.3478     0.4491  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5327      0.5204     0.0407  5
  max valid BA                0.5497      0.5310     0.0560  5
  best valid F1               0.3764      0.5053     0.2169  5
  test BA                     0.5011      0.5000     0.0350  5
  test F1                     0.2814      0.4000     0.2604  5
  test sensitivity            0.5043      0.6087     0.4828  5
  test specificity            0.4979      0.2979     0.4706  5
  test precision              0.3275      0.3286     0.0290  3
  test loss                   0.6968      0.7008     0.0379  5
  FPR (FP/(FP+TN))            0.5021      0.7021     0.4706  5
  FNR (FN/(FN+TP))            0.4957      0.3913     0.4828  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5287      0.5112     0.0417  5
  max valid BA                0.5389      0.5263     0.0389  5
  best valid F1               0.4969      0.5899     0.1955  5
  test BA                     0.5035      0.5000     0.0391  5
  test F1                     0.2772      0.1860     0.2458  5
  test sensitivity            0.3262      0.1231     0.4021  5
  test specificity            0.6809      0.8202     0.3776  5
  test precision              0.3974      0.4038     0.0986  4
  test loss                   0.7392      0.7180     0.0681  5
  FPR (FP/(FP+TN))            0.3191      0.1798     0.3776  5
  FNR (FN/(FN+TP))            0.6738      0.8769     0.4021  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4917      0.5000     0.0456  5
  max valid BA                0.5014      0.5000     0.0271  5
  best valid F1               0.3362      0.4672     0.2303  5
  test BA                     0.4917      0.5000     0.0151  5
  test F1                     0.2903      0.4627     0.2654  5
  test sensitivity            0.5556      0.8611     0.5096  5
  test specificity            0.4278      0.0833     0.5170  5
  test precision              0.2457      0.3248     0.1640  4
  test loss                   0.6775      0.6715     0.0333  5
  FPR (FP/(FP+TN))            0.5722      0.9167     0.5170  5
  FNR (FN/(FN+TP))            0.4444      0.1389     0.5096  5

groups_scp2 (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5221      0.5147     0.0255  4
  max valid BA                0.5404      0.5515     0.0278  4
  best valid F1               0.4233      0.4873     0.1425  4
  test BA                     0.5257      0.5221     0.0251  4
  test F1                     0.3387      0.2910     0.1080  4
  test sensitivity            0.4118      0.2353     0.3931  4
  test specificity            0.6397      0.8088     0.4312  4
  test precision              0.4242      0.3818     0.1203  4
  test loss                   0.6642      0.6986     0.0974  4
  FPR (FP/(FP+TN))            0.3603      0.1912     0.4312  4
  FNR (FN/(FN+TP))            0.5882      0.7647     0.3931  4
```

## AUC vs chemistry null model, in-sample increment

Failed: scp2/seed2: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label descriptors_pair_only_rankprot --seeds=0,1,2,3,4`
