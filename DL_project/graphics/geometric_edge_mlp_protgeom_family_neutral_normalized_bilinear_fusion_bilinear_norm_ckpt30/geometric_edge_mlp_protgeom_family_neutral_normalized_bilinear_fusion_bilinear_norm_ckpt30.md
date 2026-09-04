# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_ckpt30

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_ckpt30'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4448      0.6525      0.7149      0.6343      0.4537      0.6452
groups_GLTP            5      0.1840      0.8960      0.7401      0.6907      0.2308      0.9154
groups_IP_trans        5      0.4000      0.8255      0.7229      0.6262      0.4167      0.8426
groups_LBP_BPI_CETP    5      0.3043      0.9277      0.7041      0.6410      0.3667      0.8553
groups_START           5      0.1600      0.8067      0.6512      0.6007      0.1750      0.8562
groups_lipocalin       5      0.1500      0.8528      0.6648      0.7141      0.1667      0.8667
groups_scp2            5      0.3059      0.8294      0.7135      0.6387      0.3647      0.8294
ALL                   35      0.2784      0.8272      0.7016      0.6494      0.3106      0.8301

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5898      0.5769     0.0637  35
max valid BA                0.6163      0.6029     0.0745  35
best valid F1               0.5263      0.5600     0.1462  35
test BA                     0.5528      0.5342     0.0840  35
test F1                     0.3141      0.3377     0.2078  35
test sensitivity            0.2784      0.2353     0.2383  35
test specificity            0.8272      0.8723     0.2048  35
test precision              0.5273      0.5088     0.2393  32
test loss                   0.8155      0.6915     0.3774  35
FPR (FP/(FP+TN))            0.1728      0.1277     0.2048  35
FNR (FN/(FN+TP))            0.7216      0.7647     0.2383  35

=== abs(sensitivity-specificity) gap: mean=0.6318 median=0.6800 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5820      0.5802     0.0271  5
  max valid BA                0.6048      0.5995     0.0146  5
  best valid F1               0.6537      0.6707     0.0649  5
  test BA                     0.5486      0.5411     0.0452  5
  test F1                     0.4674      0.4299     0.1591  5
  test sensitivity            0.4448      0.3433     0.2850  5
  test specificity            0.6525      0.7213     0.3275  5
  test precision              0.6233      0.6441     0.0756  5
  test loss                   0.7008      0.6927     0.0227  5
  FPR (FP/(FP+TN))            0.3475      0.2787     0.3275  5
  FNR (FN/(FN+TP))            0.5552      0.6567     0.2850  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5923      0.5769     0.0685  5
  max valid BA                0.6231      0.5769     0.0727  5
  best valid F1               0.5746      0.5946     0.1193  5
  test BA                     0.5400      0.5200     0.0894  5
  test F1                     0.2831      0.2222     0.1433  5
  test sensitivity            0.1840      0.1600     0.0963  5
  test specificity            0.8960      0.9200     0.1081  5
  test precision              0.6442      0.6000     0.2794  5
  test loss                   0.8641      0.8775     0.0910  5
  FPR (FP/(FP+TN))            0.1040      0.0800     0.1081  5
  FNR (FN/(FN+TP))            0.8160      0.8400     0.0963  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6589      0.6857     0.0535  5
  max valid BA                0.6855      0.7052     0.0409  5
  best valid F1               0.5897      0.6182     0.0442  5
  test BA                     0.6128      0.6207     0.0519  5
  test F1                     0.4476      0.4444     0.1031  5
  test sensitivity            0.4000      0.3913     0.1282  5
  test specificity            0.8255      0.8298     0.0551  5
  test precision              0.5264      0.5000     0.0818  5
  test loss                   0.7219      0.6249     0.2266  5
  FPR (FP/(FP+TN))            0.1745      0.1702     0.0551  5
  FNR (FN/(FN+TP))            0.6000      0.6087     0.1282  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6232      0.6627     0.0812  5
  max valid BA                0.6341      0.6848     0.0802  5
  best valid F1               0.4979      0.5882     0.1628  5
  test BA                     0.6160      0.5874     0.1247  5
  test F1                     0.3463      0.3333     0.3113  5
  test sensitivity            0.3043      0.2174     0.3090  5
  test specificity            0.9277      0.9574     0.0613  5
  test precision              0.5190      0.6667     0.3032  5
  test loss                   0.9134      0.6533     0.6027  5
  FPR (FP/(FP+TN))            0.0723      0.0426     0.0613  5
  FNR (FN/(FN+TP))            0.6957      0.7826     0.3090  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5451      0.5278     0.0622  5
  max valid BA                0.5640      0.5356     0.0966  5
  best valid F1               0.4403      0.3780     0.2066  5
  test BA                     0.4834      0.4950     0.0647  5
  test F1                     0.1693      0.0822     0.1731  5
  test sensitivity            0.1600      0.0462     0.2273  5
  test specificity            0.8067      0.9438     0.3235  5
  test precision              0.4576      0.3606     0.3106  4
  test loss                   1.1004      0.6927     0.7742  5
  FPR (FP/(FP+TN))            0.1933      0.0562     0.3235  5
  FNR (FN/(FN+TP))            0.8400      0.9538     0.2273  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5361      0.5278     0.0292  5
  max valid BA                0.5556      0.5486     0.0431  5
  best valid F1               0.3798      0.4409     0.1314  5
  test BA                     0.5014      0.4861     0.0604  5
  test F1                     0.1744      0.0816     0.1848  5
  test sensitivity            0.1500      0.0556     0.1696  5
  test specificity            0.8528      0.9028     0.1459  5
  test precision              0.3018      0.2355     0.2229  4
  test loss                   0.7229      0.7004     0.0701  5
  FPR (FP/(FP+TN))            0.1472      0.0972     0.1459  5
  FNR (FN/(FN+TP))            0.8500      0.9444     0.1696  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5912      0.5882     0.0366  5
  max valid BA                0.6471      0.6176     0.0812  5
  best valid F1               0.5478      0.5217     0.0944  5
  test BA                     0.5676      0.5735     0.0671  5
  test F1                     0.3107      0.3704     0.2118  5
  test sensitivity            0.3059      0.2353     0.3096  5
  test specificity            0.8294      0.8529     0.2165  5
  test precision              0.5677      0.4688     0.2963  4
  test loss                   0.6853      0.6438     0.0859  5
  FPR (FP/(FP+TN))            0.1706      0.1471     0.2165  5
  FNR (FN/(FN+TP))            0.6941      0.7647     0.3096  5
```

## AUC vs chemistry null model, in-sample increment

(skipped: SKIP_AUC=1 -- rerun without it to fill this in: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_ckpt30 --seeds=0,1,2,3,4`)
