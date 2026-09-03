# geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.2716      0.8230      0.6309      0.6937      0.3045      0.8161
groups_GLTP            5      0.3360      0.5840      0.6123      0.5615      0.4462      0.6308
groups_IP_trans        5      0.4174      0.7532      0.6667      0.6251      0.5333      0.7574
groups_LBP_BPI_CETP    5      0.3217      0.8553      0.7206      0.6446      0.4083      0.8085
groups_START           5      0.3415      0.6404      0.6812      0.6239      0.3406      0.6697
groups_lipocalin       5      0.5222      0.5861      0.7486      0.5183      0.5389      0.6111
groups_scp2            5      0.4118      0.7353      0.7006      0.6303      0.4353      0.8059
ALL                   35      0.3746      0.7110      0.6801      0.6139      0.4296      0.7285

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5790      0.5824     0.0648  35
max valid BA                0.6041      0.6029     0.0656  35
best valid F1               0.5339      0.5588     0.1224  35
test BA                     0.5428      0.5338     0.0725  35
test F1                     0.3567      0.3590     0.1884  35
test sensitivity            0.3746      0.3913     0.2785  35
test specificity            0.7110      0.7541     0.2754  35
test precision              0.4811      0.4545     0.1617  33
test loss                   0.6993      0.6823     0.1092  35
FPR (FP/(FP+TN))            0.2890      0.2459     0.2754  35
FNR (FN/(FN+TP))            0.6254      0.6087     0.2785  35

=== abs(sensitivity-specificity) gap: mean=0.5179 median=0.5023 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5603      0.5835     0.0472  5
  max valid BA                0.5940      0.5991     0.0476  5
  best valid F1               0.6416      0.6923     0.0902  5
  test BA                     0.5473      0.5038     0.0682  5
  test F1                     0.3290      0.3265     0.2585  5
  test sensitivity            0.2716      0.2388     0.2394  5
  test specificity            0.8230      0.8197     0.1459  5
  test precision              0.6056      0.5811     0.1016  4
  test loss                   0.7022      0.7109     0.0293  5
  FPR (FP/(FP+TN))            0.1770      0.1803     0.1459  5
  FNR (FN/(FN+TP))            0.7284      0.7612     0.2394  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5385      0.5385     0.0304  5
  max valid BA                0.5538      0.5577     0.0316  5
  best valid F1               0.5699      0.5660     0.0975  5
  test BA                     0.4600      0.4600     0.0316  5
  test F1                     0.3059      0.2927     0.2373  5
  test sensitivity            0.3360      0.2400     0.3843  5
  test specificity            0.5840      0.6400     0.3551  5
  test precision              0.3383      0.4000     0.1949  5
  test loss                   0.7274      0.7222     0.0311  5
  FPR (FP/(FP+TN))            0.4160      0.3600     0.3551  5
  FNR (FN/(FN+TP))            0.6640      0.7600     0.3843  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6454      0.6516     0.0597  5
  max valid BA                0.6734      0.6857     0.0625  5
  best valid F1               0.5777      0.6000     0.0763  5
  test BA                     0.5853      0.5694     0.0614  5
  test F1                     0.4112      0.4528     0.1381  5
  test sensitivity            0.4174      0.5217     0.2099  5
  test specificity            0.7532      0.7234     0.1246  5
  test precision              0.4527      0.4444     0.0508  5
  test loss                   0.6654      0.6651     0.0309  5
  FPR (FP/(FP+TN))            0.2468      0.2766     0.1246  5
  FNR (FN/(FN+TP))            0.5826      0.4783     0.2099  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6084      0.5829     0.0634  5
  max valid BA                0.6258      0.6334     0.0655  5
  best valid F1               0.4522      0.5588     0.1768  5
  test BA                     0.5885      0.6133     0.0674  5
  test F1                     0.3489      0.4865     0.2161  5
  test sensitivity            0.3217      0.3913     0.2546  5
  test specificity            0.8553      0.8936     0.1630  5
  test precision              0.5393      0.5000     0.0914  5
  test loss                   0.6309      0.6258     0.0431  5
  FPR (FP/(FP+TN))            0.1447      0.1064     0.1630  5
  FNR (FN/(FN+TP))            0.6783      0.6087     0.2546  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5051      0.5000     0.0305  5
  max valid BA                0.5274      0.5066     0.0354  5
  best valid F1               0.4487      0.5409     0.1764  5
  test BA                     0.4910      0.5000     0.0662  5
  test F1                     0.2884      0.2619     0.2133  5
  test sensitivity            0.3415      0.1692     0.3927  5
  test specificity            0.6404      0.9101     0.4370  5
  test precision              0.4745      0.5005     0.1343  4
  test loss                   0.8336      0.7143     0.2411  5
  FPR (FP/(FP+TN))            0.3596      0.0899     0.4370  5
  FNR (FN/(FN+TP))            0.6585      0.8308     0.3927  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5750      0.5903     0.0532  5
  max valid BA                0.6014      0.6042     0.0457  5
  best valid F1               0.5156      0.5227     0.0397  5
  test BA                     0.5542      0.5208     0.0721  5
  test F1                     0.3979      0.4783     0.2003  5
  test sensitivity            0.5222      0.5000     0.3477  5
  test specificity            0.5861      0.5694     0.3793  5
  test precision              0.4402      0.3929     0.1196  5
  test loss                   0.6855      0.6918     0.0579  5
  FPR (FP/(FP+TN))            0.4139      0.4306     0.3793  5
  FNR (FN/(FN+TP))            0.4778      0.5000     0.3477  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6206      0.5882     0.0554  5
  max valid BA                0.6529      0.6471     0.0397  5
  best valid F1               0.5317      0.5405     0.0605  5
  test BA                     0.5735      0.5882     0.0540  5
  test F1                     0.4155      0.4571     0.0830  5
  test sensitivity            0.4118      0.4706     0.1380  5
  test specificity            0.7353      0.7059     0.1728  5
  test precision              0.5410      0.4444     0.2679  5
  test loss                   0.6502      0.6522     0.0324  5
  FPR (FP/(FP+TN))            0.2647      0.2941     0.1728  5
  FNR (FN/(FN+TP))            0.5882      0.5294     0.1380  5
```

## AUC vs chemistry null model, in-sample increment

