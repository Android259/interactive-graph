# geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28_lipid_class

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28_lipid_class'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.1254      0.9311      0.7869      0.8121      0.0896      0.9581
groups_GLTP            5      0.1600      0.8560      0.8016      0.8429      0.2462      0.9154
groups_IP_trans        5      0.2870      0.8723      0.8334      0.7922      0.3917      0.9021
groups_LBP_BPI_CETP    5      0.0522      0.9404      0.7882      0.7164      0.1417      0.9404
groups_START           5      0.4154      0.5843      0.9007      0.6592      0.4469      0.5888
groups_lipocalin       5      0.4778      0.7611      0.7305      0.7802      0.4667      0.7556
groups_scp2            5      0.3529      0.8529      0.6989      0.7746      0.3765      0.8235
ALL                   35      0.2672      0.8283      0.7915      0.7682      0.3084      0.8406

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5745      0.5710     0.0676  35
max valid BA                0.6077      0.6029     0.0642  35
best valid F1               0.5015      0.5210     0.1070  35
test BA                     0.5478      0.5222     0.0767  35
test F1                     0.2938      0.3107     0.2024  35
test sensitivity            0.2672      0.2174     0.2493  35
test specificity            0.8283      0.8824     0.2020  35
test precision              0.4891      0.5000     0.2222  33
test loss                   0.8914      0.7623     0.3324  35
FPR (FP/(FP+TN))            0.1717      0.1176     0.2020  35
FNR (FN/(FN+TP))            0.7328      0.7826     0.2493  35

=== abs(sensitivity-specificity) gap: mean=0.6499 median=0.6540 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5238      0.5137     0.0285  5
  max valid BA                0.5543      0.5473     0.0396  5
  best valid F1               0.5094      0.5915     0.1744  5
  test BA                     0.5283      0.5000     0.0577  5
  test F1                     0.1753      0.0811     0.2226  5
  test sensitivity            0.1254      0.0448     0.1796  5
  test specificity            0.9311      0.9344     0.0680  5
  test precision              0.5448      0.5604     0.1936  4
  test loss                   0.9133      0.8899     0.1958  5
  FPR (FP/(FP+TN))            0.0689      0.0656     0.0680  5
  FNR (FN/(FN+TP))            0.8746      0.9552     0.1796  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5808      0.5962     0.0644  5
  max valid BA                0.5962      0.5962     0.0720  5
  best valid F1               0.4514      0.4186     0.1254  5
  test BA                     0.5080      0.4800     0.1035  5
  test F1                     0.2373      0.1667     0.1810  5
  test sensitivity            0.1600      0.1200     0.1265  5
  test specificity            0.8560      0.8800     0.1220  5
  test precision              0.5012      0.4000     0.2913  5
  test loss                   1.2178      1.1416     0.3278  5
  FPR (FP/(FP+TN))            0.1440      0.1200     0.1220  5
  FNR (FN/(FN+TP))            0.8400      0.8800     0.1265  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6469      0.6458     0.0157  5
  max valid BA                0.6510      0.6560     0.0179  5
  best valid F1               0.5061      0.5143     0.0648  5
  test BA                     0.5796      0.5879     0.0458  5
  test F1                     0.3261      0.3448     0.1532  5
  test sensitivity            0.2870      0.2174     0.2620  5
  test specificity            0.8723      0.9362     0.1933  5
  test precision              0.6538      0.6000     0.2583  5
  test loss                   1.0991      0.9709     0.6029  5
  FPR (FP/(FP+TN))            0.1277      0.0638     0.1933  5
  FNR (FN/(FN+TP))            0.7130      0.7826     0.2620  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5410      0.5408     0.0390  5
  max valid BA                0.6025      0.6037     0.0655  5
  best valid F1               0.4459      0.3830     0.1156  5
  test BA                     0.4963      0.5009     0.0282  5
  test F1                     0.0868      0.1379     0.0794  5
  test sensitivity            0.0522      0.0870     0.0476  5
  test specificity            0.9404      0.9574     0.0233  5
  test precision              0.2667      0.3333     0.2528  5
  test loss                   0.7348      0.6687     0.1154  5
  FPR (FP/(FP+TN))            0.0596      0.0426     0.0233  5
  FNR (FN/(FN+TP))            0.9478      0.9130     0.0476  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5178      0.5000     0.0493  5
  max valid BA                0.5762      0.5763     0.0465  5
  best valid F1               0.5552      0.5732     0.0590  5
  test BA                     0.4998      0.5000     0.0427  5
  test F1                     0.3492      0.3704     0.2228  5
  test sensitivity            0.4154      0.3846     0.3691  5
  test specificity            0.5843      0.6742     0.3738  5
  test precision              0.4251      0.4216     0.0585  4
  test loss                   0.8956      0.8938     0.1993  5
  FPR (FP/(FP+TN))            0.4157      0.3258     0.3738  5
  FNR (FN/(FN+TP))            0.5846      0.6154     0.3691  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6111      0.5694     0.1079  5
  max valid BA                0.6444      0.6181     0.1027  5
  best valid F1               0.5519      0.5227     0.1159  5
  test BA                     0.6194      0.6042     0.1019  5
  test F1                     0.4561      0.5333     0.2206  5
  test sensitivity            0.4778      0.5833     0.2787  5
  test specificity            0.7611      0.8333     0.1859  5
  test precision              0.4788      0.5417     0.1904  5
  test loss                   0.6543      0.6455     0.0700  5
  FPR (FP/(FP+TN))            0.2389      0.1667     0.1859  5
  FNR (FN/(FN+TP))            0.5222      0.4167     0.2787  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6000      0.6029     0.0192  5
  max valid BA                0.6294      0.6029     0.0366  5
  best valid F1               0.4905      0.4737     0.0525  5
  test BA                     0.6029      0.6029     0.0275  5
  test F1                     0.4260      0.4286     0.0530  5
  test sensitivity            0.3529      0.3529     0.0720  5
  test specificity            0.8529      0.8529     0.0465  5
  test precision              0.5517      0.5455     0.0662  5
  test loss                   0.7251      0.6354     0.2205  5
  FPR (FP/(FP+TN))            0.1471      0.1471     0.0465  5
  FNR (FN/(FN+TP))            0.6471      0.6471     0.0720  5
```

## AUC vs chemistry null model, in-sample increment

(skipped: SKIP_AUC=1 -- rerun without it to fill this in: `python3 analysis/full_label_report.py --label geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28_lipid_class --seeds=0,1,2,3,4`)
