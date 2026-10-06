# thematical_paths_geom_chem_orthogonal_init_no_volume

## Summary (analysis/summarize_label.py)

```
Summary: 'thematical_paths_geom_chem_orthogonal_init_no_volume'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6328      0.4557      0.7286      0.5159      0.6358      0.5097
groups_GLTP            5      0.4000      0.6560      0.6914      0.4925      0.4385      0.7154
groups_IP_trans        5      0.4609      0.5362      0.6105      0.5711      0.5000      0.5787
groups_LBP_BPI_CETP    5      0.6435      0.5489      0.6861      0.6472      0.6833      0.5489
groups_START           5      0.4431      0.6315      0.7031      0.6092      0.5062      0.6292
groups_lipocalin       5      0.5722      0.5167      0.7425      0.5480      0.5722      0.5389
groups_scp2            5      0.3882      0.8118      0.6619      0.6677      0.4471      0.8588
ALL                   35      0.5058      0.5938      0.6892      0.5788      0.5404      0.6257

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5831      0.5804     0.0732  35
max valid BA                0.6103      0.6089     0.0821  35
best valid F1               0.5923      0.6026     0.0807  35
test BA                     0.5498      0.5315     0.0687  35
test F1                     0.4239      0.4783     0.1967  35
test sensitivity            0.5058      0.5077     0.3105  35
test specificity            0.5938      0.6809     0.3171  35
test precision              0.4685      0.5000     0.1218  31
test loss                   0.7347      0.6931     0.1052  35
FPR (FP/(FP+TN))            0.4062      0.3191     0.3171  35
FNR (FN/(FN+TP))            0.4942      0.4923     0.3105  35

=== abs(sensitivity-specificity) gap: mean=0.4965 median=0.4000 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5727      0.5804     0.0598  5
  max valid BA                0.5943      0.6089     0.0625  5
  best valid F1               0.6823      0.6848     0.0336  5
  test BA                     0.5443      0.5383     0.0446  5
  test F1                     0.5644      0.6173     0.1370  5
  test sensitivity            0.6328      0.7463     0.3049  5
  test specificity            0.4557      0.4262     0.3532  5
  test precision              0.5929      0.5778     0.0879  5
  test loss                   0.7777      0.6931     0.1808  5
  FPR (FP/(FP+TN))            0.5443      0.5738     0.3532  5
  FNR (FN/(FN+TP))            0.3672      0.2537     0.3049  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5769      0.5000     0.1062  5
  max valid BA                0.6115      0.5192     0.1498  5
  best valid F1               0.6950      0.6667     0.0634  5
  test BA                     0.5280      0.5000     0.0438  5
  test F1                     0.3273      0.3030     0.3336  5
  test sensitivity            0.4000      0.2000     0.4690  5
  test specificity            0.6560      0.8800     0.4424  5
  test precision              0.5655      0.5714     0.0627  3
  test loss                   0.7724      0.6932     0.1665  5
  FPR (FP/(FP+TN))            0.3440      0.1200     0.4424  5
  FNR (FN/(FN+TP))            0.6000      0.8000     0.4690  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5394      0.5319     0.0386  5
  max valid BA                0.5568      0.5452     0.0322  5
  best valid F1               0.5085      0.5217     0.0319  5
  test BA                     0.4985      0.5000     0.0305  5
  test F1                     0.2853      0.2326     0.2151  5
  test sensitivity            0.4609      0.2174     0.4789  5
  test specificity            0.5362      0.6809     0.4572  5
  test precision              0.3243      0.3362     0.0532  4
  test loss                   0.7350      0.6936     0.0937  5
  FPR (FP/(FP+TN))            0.4638      0.3191     0.4572  5
  FNR (FN/(FN+TP))            0.5391      0.7826     0.4789  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6161      0.6321     0.0595  5
  max valid BA                0.6436      0.6742     0.0820  5
  best valid F1               0.5653      0.5769     0.0601  5
  test BA                     0.5962      0.6332     0.0942  5
  test F1                     0.5001      0.5106     0.0967  5
  test sensitivity            0.6435      0.6957     0.2268  5
  test specificity            0.5489      0.6809     0.3092  5
  test precision              0.4335      0.4848     0.0927  5
  test loss                   0.6813      0.6895     0.0165  5
  FPR (FP/(FP+TN))            0.4511      0.3191     0.3092  5
  FNR (FN/(FN+TP))            0.3565      0.3043     0.2268  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5677      0.5507     0.0475  5
  max valid BA                0.5912      0.5732     0.0420  5
  best valid F1               0.5821      0.6026     0.0581  5
  test BA                     0.5373      0.5427     0.0666  5
  test F1                     0.4474      0.4583     0.1139  5
  test sensitivity            0.4431      0.5077     0.1433  5
  test specificity            0.6315      0.6854     0.1012  5
  test precision              0.4623      0.4815     0.0922  5
  test loss                   0.7515      0.6933     0.0881  5
  FPR (FP/(FP+TN))            0.3685      0.3146     0.1012  5
  FNR (FN/(FN+TP))            0.5569      0.4923     0.1433  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5556      0.5278     0.0673  5
  max valid BA                0.6069      0.6181     0.0514  5
  best valid F1               0.5228      0.5319     0.0196  5
  test BA                     0.5444      0.5000     0.0811  5
  test F1                     0.4451      0.4478     0.0881  5
  test sensitivity            0.5722      0.5000     0.2535  5
  test specificity            0.5167      0.5694     0.3108  5
  test precision              0.3942      0.3333     0.1028  5
  test loss                   0.7196      0.6931     0.0549  5
  FPR (FP/(FP+TN))            0.4833      0.4306     0.3108  5
  FNR (FN/(FN+TP))            0.4278      0.5000     0.2535  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6529      0.6765     0.0874  5
  max valid BA                0.6676      0.7059     0.0945  5
  best valid F1               0.5903      0.6154     0.0516  5
  test BA                     0.6000      0.6324     0.0738  5
  test F1                     0.3977      0.5143     0.2298  5
  test sensitivity            0.3882      0.4118     0.2301  5
  test specificity            0.8118      0.7353     0.1373  5
  test precision              0.5288      0.5132     0.1287  4
  test loss                   0.7058      0.6900     0.0666  5
  FPR (FP/(FP+TN))            0.1882      0.2647     0.1373  5
  FNR (FN/(FN+TP))            0.6118      0.5882     0.2301  5
```

## AUC vs chemistry null model, in-sample increment

