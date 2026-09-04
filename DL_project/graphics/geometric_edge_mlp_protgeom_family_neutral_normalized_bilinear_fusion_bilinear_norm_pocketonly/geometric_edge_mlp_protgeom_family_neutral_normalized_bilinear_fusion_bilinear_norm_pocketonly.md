# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_pocketonly

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_pocketonly'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.3552      0.7574      0.6617      0.7245      0.3821      0.7581
groups_GLTP            5      0.4000      0.6880      0.7016      0.5413      0.4538      0.7154
groups_IP_trans        5      0.4000      0.7787      0.7300      0.6548      0.4500      0.8170
groups_LBP_BPI_CETP    5      0.2609      0.9447      0.7026      0.6180      0.3417      0.9106
groups_START           5      0.3631      0.6562      0.7904      0.5621      0.3812      0.6787
groups_lipocalin       5      0.1889      0.8667      0.6153      0.7098      0.2722      0.8667
groups_scp2            5      0.4824      0.6471      0.7475      0.6413      0.5059      0.6941
ALL                   35      0.3501      0.7627      0.7070      0.6360      0.3981      0.7772

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5877      0.5851     0.0638  35
max valid BA                0.6321      0.6286     0.0678  35
best valid F1               0.5432      0.5882     0.1356  35
test BA                     0.5564      0.5588     0.0785  35
test F1                     0.3649      0.3889     0.1965  35
test sensitivity            0.3501      0.3043     0.2529  35
test specificity            0.7627      0.8033     0.2243  35
test precision              0.5099      0.5000     0.2260  34
test loss                   0.7124      0.6930     0.1038  35
FPR (FP/(FP+TN))            0.2373      0.1967     0.2243  35
FNR (FN/(FN+TP))            0.6499      0.6957     0.2529  35

=== abs(sensitivity-specificity) gap: mean=0.5432 median=0.5346 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5701      0.5471     0.0419  5
  max valid BA                0.6163      0.6158     0.0478  5
  best valid F1               0.6581      0.6837     0.0728  5
  test BA                     0.5563      0.5630     0.0220  5
  test F1                     0.4398      0.4660     0.1006  5
  test sensitivity            0.3552      0.3582     0.1311  5
  test specificity            0.7574      0.8033     0.1084  5
  test precision              0.6194      0.6087     0.0315  5
  test loss                   0.7028      0.7077     0.0170  5
  FPR (FP/(FP+TN))            0.2426      0.1967     0.1084  5
  FNR (FN/(FN+TP))            0.6448      0.6418     0.1311  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5846      0.5769     0.0800  5
  max valid BA                0.6462      0.6731     0.0661  5
  best valid F1               0.5927      0.5946     0.1019  5
  test BA                     0.5440      0.5000     0.1236  5
  test F1                     0.4219      0.3871     0.2101  5
  test sensitivity            0.4000      0.2400     0.3544  5
  test specificity            0.6880      0.7600     0.4103  5
  test precision              0.6467      0.5000     0.3280  5
  test loss                   0.7622      0.7300     0.0762  5
  FPR (FP/(FP+TN))            0.3120      0.2400     0.4103  5
  FNR (FN/(FN+TP))            0.6000      0.7600     0.3544  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6335      0.6445     0.0390  5
  max valid BA                0.6974      0.7150     0.0507  5
  best valid F1               0.6085      0.6296     0.0585  5
  test BA                     0.5894      0.5883     0.0667  5
  test F1                     0.4211      0.3889     0.1126  5
  test sensitivity            0.4000      0.3043     0.1638  5
  test specificity            0.7787      0.7447     0.0683  5
  test precision              0.4662      0.4783     0.0792  5
  test loss                   0.6755      0.6300     0.1130  5
  FPR (FP/(FP+TN))            0.2213      0.2553     0.0683  5
  FNR (FN/(FN+TP))            0.6000      0.6957     0.1638  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6262      0.6232     0.0772  5
  max valid BA                0.6623      0.6760     0.0690  5
  best valid F1               0.5188      0.5556     0.1758  5
  test BA                     0.6028      0.6096     0.0975  5
  test F1                     0.3287      0.4118     0.2737  5
  test sensitivity            0.2609      0.3043     0.2381  5
  test specificity            0.9447      0.9574     0.0512  5
  test precision              0.6278      0.6842     0.3782  5
  test loss                   0.6416      0.6470     0.0625  5
  FPR (FP/(FP+TN))            0.0553      0.0426     0.0512  5
  FNR (FN/(FN+TP))            0.7391      0.6957     0.2381  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5300      0.5244     0.0451  5
  max valid BA                0.5733      0.5819     0.0561  5
  best valid F1               0.5061      0.5829     0.1371  5
  test BA                     0.5096      0.5062     0.0928  5
  test F1                     0.3223      0.2923     0.2630  5
  test sensitivity            0.3631      0.2923     0.3489  5
  test specificity            0.6562      0.5506     0.2496  5
  test precision              0.3907      0.4952     0.1608  5
  test loss                   0.8263      0.8091     0.1699  5
  FPR (FP/(FP+TN))            0.3438      0.4494     0.2496  5
  FNR (FN/(FN+TP))            0.6369      0.7077     0.3489  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5694      0.5625     0.0703  5
  max valid BA                0.5847      0.5625     0.0774  5
  best valid F1               0.3883      0.3448     0.1605  5
  test BA                     0.5278      0.5069     0.0646  5
  test F1                     0.2039      0.0976     0.2229  5
  test sensitivity            0.1889      0.0556     0.2269  5
  test specificity            0.8667      0.9167     0.1334  5
  test precision              0.3583      0.3806     0.1607  4
  test loss                   0.6725      0.6699     0.0756  5
  FPR (FP/(FP+TN))            0.1333      0.0833     0.1334  5
  FNR (FN/(FN+TP))            0.8111      0.9444     0.2269  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6000      0.6029     0.0481  5
  max valid BA                0.6441      0.6324     0.0408  5
  best valid F1               0.5301      0.5333     0.0634  5
  test BA                     0.5647      0.5735     0.0424  5
  test F1                     0.4167      0.4444     0.1133  5
  test sensitivity            0.4824      0.3529     0.2708  5
  test specificity            0.6471      0.7941     0.2589  5
  test precision              0.4296      0.3784     0.1060  5
  test loss                   0.7058      0.6613     0.0694  5
  FPR (FP/(FP+TN))            0.3529      0.2059     0.2589  5
  FNR (FN/(FN+TP))            0.5176      0.6471     0.2708  5
```

## AUC vs chemistry null model, in-sample increment

(skipped: SKIP_AUC=1 -- rerun without it to fill this in: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_pocketonly --seeds=0,1,2,3,4`)
