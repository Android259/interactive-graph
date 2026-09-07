# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_cross_forced

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_cross_forced'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4657      0.7115      0.6583      0.6893      0.4597      0.6935
groups_GLTP            5      0.2240      0.7280      0.6757      0.6499      0.3692      0.7769
groups_IP_trans        5      0.3043      0.8383      0.7372      0.6160      0.4083      0.8468
groups_LBP_BPI_CETP    5      0.3565      0.8128      0.7247      0.6384      0.4667      0.8000
groups_START           5      0.1385      0.8360      0.7706      0.6488      0.1750      0.8539
groups_lipocalin       5      0.4556      0.7472      0.7064      0.5171      0.3889      0.7611
groups_scp2            5      0.2353      0.9176      0.6525      0.7308      0.2824      0.8941
ALL                   35      0.3114      0.7988      0.7036      0.6415      0.3643      0.8038

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5850      0.5769     0.0547  35
max valid BA                0.6099      0.6144     0.0593  35
best valid F1               0.5272      0.5417     0.1072  35
test BA                     0.5551      0.5545     0.0865  35
test F1                     0.3541      0.3243     0.1817  35
test sensitivity            0.3114      0.2609     0.2059  35
test specificity            0.7988      0.8000     0.1163  35
test precision              0.5057      0.4815     0.2064  35
test loss                   0.7270      0.6871     0.1587  35
FPR (FP/(FP+TN))            0.2012      0.2000     0.1163  35
FNR (FN/(FN+TP))            0.6886      0.7391     0.2059  35

=== abs(sensitivity-specificity) gap: mean=0.4986 median=0.5200 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5766      0.5695     0.0347  5
  max valid BA                0.6240      0.6273     0.0401  5
  best valid F1               0.6670      0.7018     0.0594  5
  test BA                     0.5886      0.5629     0.0948  5
  test F1                     0.5216      0.5179     0.1633  5
  test sensitivity            0.4657      0.4328     0.2075  5
  test specificity            0.7115      0.7377     0.0631  5
  test precision              0.6212      0.6190     0.0849  5
  test loss                   0.6769      0.6843     0.0408  5
  FPR (FP/(FP+TN))            0.2885      0.2623     0.0631  5
  FNR (FN/(FN+TP))            0.5343      0.5672     0.2075  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5731      0.5577     0.0370  5
  max valid BA                0.5769      0.5577     0.0385  5
  best valid F1               0.5415      0.5263     0.0695  5
  test BA                     0.4760      0.4400     0.0817  5
  test F1                     0.2914      0.2222     0.1437  5
  test sensitivity            0.2240      0.1600     0.1284  5
  test specificity            0.7280      0.7200     0.0716  5
  test precision              0.4319      0.3750     0.1449  5
  test loss                   0.7963      0.7920     0.0571  5
  FPR (FP/(FP+TN))            0.2720      0.2800     0.0716  5
  FNR (FN/(FN+TP))            0.7760      0.8400     0.1284  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6233      0.6210     0.0569  5
  max valid BA                0.6611      0.6445     0.0387  5
  best valid F1               0.5502      0.5484     0.0670  5
  test BA                     0.5713      0.5453     0.0655  5
  test F1                     0.3592      0.3243     0.1250  5
  test sensitivity            0.3043      0.2609     0.1537  5
  test specificity            0.8383      0.8298     0.0715  5
  test precision              0.4828      0.4545     0.0953  5
  test loss                   0.6794      0.6282     0.1197  5
  FPR (FP/(FP+TN))            0.1617      0.1702     0.0715  5
  FNR (FN/(FN+TP))            0.6957      0.7391     0.1537  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6333      0.6445     0.0359  5
  max valid BA                0.6377      0.6445     0.0414  5
  best valid F1               0.4992      0.5397     0.1062  5
  test BA                     0.5846      0.6129     0.0976  5
  test F1                     0.3688      0.4737     0.2424  5
  test sensitivity            0.3565      0.3913     0.2524  5
  test specificity            0.8128      0.8511     0.1289  5
  test precision              0.4000      0.4375     0.2606  5
  test loss                   0.7022      0.6862     0.1154  5
  FPR (FP/(FP+TN))            0.1872      0.1489     0.1289  5
  FNR (FN/(FN+TP))            0.6435      0.6087     0.2524  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5145      0.5263     0.0275  5
  max valid BA                0.5416      0.5400     0.0487  5
  best valid F1               0.4599      0.5426     0.1201  5
  test BA                     0.4872      0.4894     0.0441  5
  test F1                     0.1902      0.1500     0.1015  5
  test sensitivity            0.1385      0.0923     0.1020  5
  test specificity            0.8360      0.8989     0.1436  5
  test precision              0.4103      0.3636     0.1800  5
  test loss                   0.9236      0.7918     0.3255  5
  FPR (FP/(FP+TN))            0.1640      0.1011     0.1436  5
  FNR (FN/(FN+TP))            0.8615      0.9077     0.1020  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5861      0.5833     0.0653  5
  max valid BA                0.6014      0.5833     0.0779  5
  best valid F1               0.4770      0.4848     0.1199  5
  test BA                     0.6014      0.6319     0.1069  5
  test F1                     0.4402      0.5250     0.2095  5
  test sensitivity            0.4556      0.5000     0.2505  5
  test specificity            0.7472      0.7778     0.1003  5
  test precision              0.4460      0.4815     0.1989  5
  test loss                   0.6710      0.6733     0.0281  5
  FPR (FP/(FP+TN))            0.2528      0.2222     0.1003  5
  FNR (FN/(FN+TP))            0.5444      0.5000     0.2505  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5882      0.6029     0.0453  5
  max valid BA                0.6265      0.6471     0.0556  5
  best valid F1               0.4958      0.5366     0.0915  5
  test BA                     0.5765      0.5588     0.0319  5
  test F1                     0.3072      0.2105     0.1376  5
  test sensitivity            0.2353      0.1176     0.1664  5
  test specificity            0.9176      0.9706     0.1128  5
  test precision              0.7475      0.6667     0.2411  5
  test loss                   0.6401      0.6337     0.0190  5
  FPR (FP/(FP+TN))            0.0824      0.0294     0.1128  5
  FNR (FN/(FN+TP))            0.7647      0.8824     0.1664  5
```

## AUC vs chemistry null model, in-sample increment

