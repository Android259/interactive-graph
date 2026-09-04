# geometric_edge_mlp_protgeom_family_neutral_dro_wd01

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_dro_wd01'
rows: 21

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       3      0.9104      0.2131      0.4819      0.5567      0.9154      0.2097
groups_GLTP            3      0.5067      0.4933      0.7268      0.5012      0.5769      0.5897
groups_IP_trans        3      0.6812      0.5887      0.4555      0.6814      0.6944      0.5887
groups_LBP_BPI_CETP    3      0.3913      0.8014      0.6280      0.6834      0.5000      0.8085
groups_START           3      0.2821      0.7640      0.6985      0.5865      0.3698      0.7004
groups_lipocalin       3      0.5093      0.5741      0.7044      0.5479      0.4722      0.5926
groups_scp2            3      0.3529      0.8039      0.6853      0.5111      0.3529      0.8039
ALL                   21      0.5191      0.6055      0.6258      0.5812      0.5545      0.6134

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5839      0.5882     0.0670  21
max valid BA                0.6674      0.6597     0.0638  21
best valid F1               0.6373      0.6400     0.0630  21
test BA                     0.5623      0.5569     0.0630  21
test F1                     0.4412      0.5000     0.2174  21
test sensitivity            0.5191      0.5385     0.3095  21
test specificity            0.6055      0.6471     0.2843  21
test precision              0.4488      0.4719     0.1452  20
test loss                   0.7335      0.6996     0.1233  21
FPR (FP/(FP+TN))            0.3945      0.3529     0.2843  21
FNR (FN/(FN+TP))            0.4809      0.4615     0.3095  21

=== abs(sensitivity-specificity) gap: mean=0.4860 median=0.4942 n=21 ===

=== By group ===
groups_CRAL-TRIO (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5626      0.5589     0.0311  3
  max valid BA                0.5931      0.5726     0.0478  3
  best valid F1               0.7038      0.7033     0.0126  3
  test BA                     0.5618      0.5588     0.0336  3
  test F1                     0.6932      0.6988     0.0169  3
  test sensitivity            0.9104      0.8955     0.0538  3
  test specificity            0.2131      0.1639     0.0997  3
  test precision              0.5607      0.5556     0.0231  3
  test loss                   0.7200      0.7333     0.0273  3
  FPR (FP/(FP+TN))            0.7869      0.8361     0.0997  3
  FNR (FN/(FN+TP))            0.0896      0.1045     0.0538  3

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5833      0.5769     0.0484  3
  max valid BA                0.6859      0.7308     0.0949  3
  best valid F1               0.7088      0.6765     0.0567  3
  test BA                     0.5000      0.4800     0.0529  3
  test F1                     0.4009      0.5263     0.3552  3
  test sensitivity            0.5067      0.6000     0.4670  3
  test specificity            0.4933      0.3200     0.4086  3
  test precision              0.3345      0.4688     0.2916  3
  test loss                   0.7498      0.7326     0.0542  3
  FPR (FP/(FP+TN))            0.5067      0.6800     0.4086  3
  FNR (FN/(FN+TP))            0.4933      0.4000     0.4670  3

groups_IP_trans (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6415      0.6308     0.0259  3
  max valid BA                0.6701      0.6844     0.0345  3
  best valid F1               0.5896      0.6027     0.0365  3
  test BA                     0.6349      0.6226     0.0497  3
  test F1                     0.5370      0.5079     0.0574  3
  test sensitivity            0.6812      0.6957     0.1527  3
  test specificity            0.5887      0.5532     0.1210  3
  test precision              0.4517      0.4750     0.0448  3
  test loss                   0.7091      0.6756     0.1396  3
  FPR (FP/(FP+TN))            0.4113      0.4468     0.1210  3
  FNR (FN/(FN+TP))            0.3188      0.3043     0.1527  3

groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6543      0.6853     0.0632  3
  max valid BA                0.6919      0.7269     0.0794  3
  best valid F1               0.6076      0.6400     0.0803  3
  test BA                     0.5964      0.5569     0.0688  3
  test F1                     0.4327      0.3810     0.1092  3
  test sensitivity            0.3913      0.3478     0.1150  3
  test specificity            0.8014      0.8085     0.0325  3
  test precision              0.4862      0.4375     0.0989  3
  test loss                   0.9236      0.9554     0.2284  3
  FPR (FP/(FP+TN))            0.1986      0.1915     0.0325  3
  FNR (FN/(FN+TP))            0.6087      0.6522     0.1150  3

groups_START (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5351      0.5180     0.0623  3
  max valid BA                0.6317      0.6269     0.0254  3
  best valid F1               0.6204      0.6214     0.0301  3
  test BA                     0.5230      0.5394     0.0329  3
  test F1                     0.2992      0.3689     0.2433  3
  test sensitivity            0.2821      0.2923     0.2617  3
  test specificity            0.7640      0.7865     0.2032  3
  test precision              0.3889      0.4667     0.1644  3
  test loss                   0.6889      0.6897     0.0640  3
  FPR (FP/(FP+TN))            0.2360      0.2135     0.2032  3
  FNR (FN/(FN+TP))            0.7179      0.7077     0.2617  3

groups_lipocalin (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5324      0.5694     0.0828  3
  max valid BA                0.6736      0.6597     0.0434  3
  best valid F1               0.5913      0.5766     0.0440  3
  test BA                     0.5417      0.5486     0.0250  3
  test F1                     0.3911      0.4667     0.1420  3
  test sensitivity            0.5093      0.5833     0.3395  3
  test specificity            0.5741      0.5417     0.3691  3
  test precision              0.4517      0.3889     0.1520  3
  test loss                   0.6920      0.6996     0.0287  3
  FPR (FP/(FP+TN))            0.4259      0.4583     0.3691  3
  FNR (FN/(FN+TP))            0.4907      0.4167     0.3395  3

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5784      0.5882     0.0740  3
  max valid BA                0.7255      0.7206     0.0516  3
  best valid F1               0.6398      0.6286     0.0554  3
  test BA                     0.5784      0.5588     0.0899  3
  test F1                     0.3346      0.4324     0.2980  3
  test sensitivity            0.3529      0.4706     0.3113  3
  test specificity            0.8039      0.7647     0.1797  3
  test precision              0.4778      0.4778     0.1100  2
  test loss                   0.6513      0.6481     0.0155  3
  FPR (FP/(FP+TN))            0.1961      0.2353     0.1797  3
  FNR (FN/(FN+TP))            0.6471      0.5294     0.3113  3
```

## AUC vs chemistry null model, in-sample increment

(skipped: SKIP_AUC=1 -- rerun without it to fill this in: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_dro_wd01 --seeds=0,1,2,3,4`)
