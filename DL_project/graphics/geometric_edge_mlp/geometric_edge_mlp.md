# geometric_edge_mlp

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp'
rows: 31

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       4      0.5746      0.4959      0.4529      0.5602      0.5410      0.5282
groups_GLTP            5      0.6320      0.3040      0.6680      0.3201      0.7231      0.3923
groups_IP_trans        5      0.8174      0.2681      0.7300      0.2937      0.8083      0.2809
groups_LBP_BPI_CETP    4      0.4565      0.6436      0.5664      0.4333      0.4583      0.6223
groups_START           5      0.8462      0.2382      0.5536      0.4464      0.8281      0.2652
groups_lipocalin       3      0.6667      0.3333      0.6972      0.3073      0.6667      0.3333
groups_scp2            5      0.6353      0.5176      0.5978      0.4159      0.6118      0.4882
ALL                   31      0.6703      0.3935      0.6102      0.3960      0.6727      0.4108

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5418      0.5106     0.0537  31
max valid BA                0.5617      0.5735     0.0597  31
best valid F1               0.5830      0.5899     0.0749  31
test BA                     0.5319      0.5000     0.0808  31
test F1                     0.4532      0.4946     0.2151  31
test sensitivity            0.6703      0.8769     0.3913  31
test specificity            0.3935      0.3200     0.4064  31
test precision              0.4639      0.4410     0.1569  28
test loss                   0.7102      0.6931     0.0354  31
FPR (FP/(FP+TN))            0.6065      0.6800     0.4064  31
FNR (FN/(FN+TP))            0.3297      0.1231     0.3913  31

=== abs(sensitivity-specificity) gap: mean=0.7493 median=1.0000 n=31 ===

=== By group ===
groups_CRAL-TRIO (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5346      0.5246     0.0432  4
  max valid BA                0.5524      0.5447     0.0619  4
  best valid F1               0.6940      0.6856     0.0183  4
  test BA                     0.5353      0.5291     0.0420  4
  test F1                     0.4575      0.5601     0.3298  4
  test sensitivity            0.5746      0.6493     0.4993  4
  test specificity            0.4959      0.4918     0.5034  4
  test precision              0.5927      0.5546     0.0942  3
  test loss                   0.6930      0.6930     0.0005  4
  FPR (FP/(FP+TN))            0.5041      0.5082     0.5034  4
  FNR (FN/(FN+TP))            0.4254      0.3507     0.4993  4

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5577      0.5577     0.0638  5
  max valid BA                0.5692      0.5769     0.0617  5
  best valid F1               0.6667      0.6667     0.0000  5
  test BA                     0.4680      0.5000     0.0701  5
  test F1                     0.5116      0.4615     0.1453  5
  test sensitivity            0.6320      0.4800     0.3434  5
  test specificity            0.3040      0.3200     0.3318  5
  test precision              0.4796      0.5000     0.0787  5
  test loss                   0.6970      0.6931     0.0085  5
  FPR (FP/(FP+TN))            0.6960      0.6800     0.3318  5
  FNR (FN/(FN+TP))            0.3680      0.5200     0.3434  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5446      0.5106     0.0781  5
  max valid BA                0.5535      0.5106     0.0785  5
  best valid F1               0.5345      0.5106     0.0434  5
  test BA                     0.5427      0.5000     0.0731  5
  test F1                     0.4732      0.4946     0.1080  5
  test sensitivity            0.8174      1.0000     0.3401  5
  test specificity            0.2681      0.0000     0.3939  5
  test precision              0.3769      0.3286     0.0663  5
  test loss                   0.7173      0.6932     0.0412  5
  FPR (FP/(FP+TN))            0.7319      1.0000     0.3939  5
  FNR (FN/(FN+TP))            0.1826      0.0000     0.3401  5

groups_LBP_BPI_CETP (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5403      0.5155     0.0617  4
  max valid BA                0.6033      0.6144     0.0775  4
  best valid F1               0.5453      0.5416     0.0373  4
  test BA                     0.5501      0.5109     0.0863  4
  test F1                     0.2920      0.2890     0.2937  4
  test sensitivity            0.4565      0.4130     0.5101  4
  test specificity            0.6436      0.7872     0.4737  4
  test precision              0.6008      0.4737     0.3533  3
  test loss                   0.7179      0.6927     0.0521  4
  FPR (FP/(FP+TN))            0.3564      0.2128     0.4737  4
  FNR (FN/(FN+TP))            0.5435      0.5870     0.5101  4

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5466      0.5445     0.0480  5
  max valid BA                0.5649      0.5820     0.0429  5
  best valid F1               0.6097      0.5899     0.0277  5
  test BA                     0.5422      0.5000     0.0701  5
  test F1                     0.5703      0.5936     0.1148  5
  test sensitivity            0.8462      1.0000     0.2803  5
  test specificity            0.2382      0.2360     0.2529  5
  test precision              0.4445      0.4221     0.0475  5
  test loss                   0.7076      0.6932     0.0314  5
  FPR (FP/(FP+TN))            0.7618      0.7640     0.2529  5
  FNR (FN/(FN+TP))            0.1538      0.0000     0.2803  5

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0000  3
  max valid BA                0.5000      0.5000     0.0000  3
  best valid F1               0.5000      0.5000     0.0000  3
  test BA                     0.5000      0.5000     0.0000  3
  test F1                     0.3333      0.5000     0.2887  3
  test sensitivity            0.6667      1.0000     0.5774  3
  test specificity            0.3333      0.0000     0.5774  3
  test precision              0.3333      0.3333     0.0000  2
  test loss                   0.7369      0.7203     0.0604  3
  FPR (FP/(FP+TN))            0.6667      1.0000     0.5774  3
  FNR (FN/(FN+TP))            0.3333      0.0000     0.5774  3

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5441     0.0556  5
  max valid BA                0.5706      0.5735     0.0514  5
  best valid F1               0.5119      0.5000     0.0165  5
  test BA                     0.5765      0.5000     0.1337  5
  test F1                     0.4548      0.5000     0.2335  5
  test sensitivity            0.6353      0.7059     0.4041  5
  test specificity            0.5176      0.7353     0.4791  5
  test precision              0.4475      0.3333     0.2022  5
  test loss                   0.7108      0.6931     0.0397  5
  FPR (FP/(FP+TN))            0.4824      0.2647     0.4791  5
  FNR (FN/(FN+TP))            0.3647      0.2941     0.4041  5
```

## AUC vs chemistry null model, in-sample increment

