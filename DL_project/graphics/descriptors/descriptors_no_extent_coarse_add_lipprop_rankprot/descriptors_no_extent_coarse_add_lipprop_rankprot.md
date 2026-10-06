# descriptors_no_extent_coarse_add_lipprop_rankprot

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_add_lipprop_rankprot'
rows: 19

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       4      0.6828      0.2951      0.6486      0.3534      0.7090      0.3145
groups_GLTP            3      0.8933      0.0933      0.8149      0.2367      0.8718      0.1923
groups_IP_trans        4      0.6304      0.6277      0.6632      0.3674      0.6146      0.6702
groups_LBP_BPI_CETP    1      0.5652      0.8936      0.6727      0.4149      0.7917      0.7021
groups_START           2      0.9846      0.0169      0.9079      0.1143      0.9922      0.0225
groups_lipocalin       2      0.7639      0.2917      0.8012      0.3012      0.8611      0.3333
groups_scp2            3      0.6471      0.3333      0.5950      0.4022      0.6667      0.3824
ALL                   19      0.7335      0.3411      0.7141      0.3182      0.7583      0.3725

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5662      0.5294     0.0827  19
max valid BA                0.5732      0.5294     0.0885  19
best valid F1               0.5935      0.6176     0.1101  19
test BA                     0.5373      0.5005     0.0860  19
test F1                     0.4981      0.5888     0.2217  19
test sensitivity            0.7335      0.8696     0.3513  19
test specificity            0.3411      0.1600     0.3852  19
test precision              0.4267      0.4364     0.1441  18
test loss                   0.6932      0.6924     0.0443  19
FPR (FP/(FP+TN))            0.6589      0.8400     0.3852  19
FNR (FN/(FN+TP))            0.2665      0.1304     0.3513  19

=== abs(sensitivity-specificity) gap: mean=0.7364 median=0.9355 n=19 ===

=== By group ===
groups_CRAL-TRIO (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5117      0.5081     0.0148  4
  max valid BA                0.5159      0.5133     0.0142  4
  best valid F1               0.6838      0.6854     0.0073  4
  test BA                     0.4890      0.5000     0.0226  4
  test F1                     0.4916      0.6396     0.3305  4
  test sensitivity            0.6828      0.8657     0.4698  4
  test specificity            0.2951      0.0902     0.4757  4
  test precision              0.5141      0.5234     0.0165  3
  test loss                   0.7081      0.7119     0.0238  4
  FPR (FP/(FP+TN))            0.7049      0.9098     0.4757  4
  FNR (FN/(FN+TP))            0.3172      0.1343     0.4698  4

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5321      0.5192     0.0400  3
  max valid BA                0.5321      0.5192     0.0400  3
  best valid F1               0.6593      0.6753     0.0364  3
  test BA                     0.4933      0.5000     0.0702  3
  test F1                     0.6354      0.6667     0.0713  3
  test sensitivity            0.8933      0.9600     0.1514  3
  test specificity            0.0933      0.1200     0.0833  3
  test precision              0.4944      0.5000     0.0419  3
  test loss                   0.7298      0.7275     0.0185  3
  FPR (FP/(FP+TN))            0.9067      0.8800     0.0833  3
  FNR (FN/(FN+TP))            0.1067      0.0400     0.1514  3

groups_IP_trans (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6424      0.6463     0.0694  4
  max valid BA                0.6662      0.6625     0.0583  4
  best valid F1               0.5732      0.5852     0.0764  4
  test BA                     0.6290      0.6628     0.0893  4
  test F1                     0.4605      0.5794     0.2565  4
  test sensitivity            0.6304      0.8043     0.3929  4
  test specificity            0.6277      0.5532     0.2282  4
  test precision              0.4268      0.4437     0.0678  4
  test loss                   0.6685      0.6701     0.0119  4
  FPR (FP/(FP+TN))            0.3723      0.4468     0.2282  4
  FNR (FN/(FN+TP))            0.3696      0.1957     0.3929  4

groups_LBP_BPI_CETP (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7469      0.7469     0.0000  1
  max valid BA                0.7682      0.7682     0.0000  1
  best valid F1               0.6909      0.6909     0.0000  1
  test BA                     0.7294      0.7294     0.0000  1
  test F1                     0.6341      0.6341     0.0000  1
  test sensitivity            0.5652      0.5652     0.0000  1
  test specificity            0.8936      0.8936     0.0000  1
  test precision              0.7222      0.7222     0.0000  1
  test loss                   0.5915      0.5915     0.0000  1
  FPR (FP/(FP+TN))            0.1064      0.1064     0.0000  1
  FNR (FN/(FN+TP))            0.4348      0.4348     0.0000  1

groups_START (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5073      0.5073     0.0104  2
  max valid BA                0.5079      0.5079     0.0112  2
  best valid F1               0.5926      0.5926     0.0039  2
  test BA                     0.5007      0.5007     0.0010  2
  test F1                     0.5912      0.5912     0.0034  2
  test sensitivity            0.9846      0.9846     0.0218  2
  test specificity            0.0169      0.0169     0.0238  2
  test precision              0.4224      0.4224     0.0005  2
  test loss                   0.6875      0.6875     0.0070  2
  FPR (FP/(FP+TN))            0.9831      0.9831     0.0238  2
  FNR (FN/(FN+TP))            0.0154      0.0154     0.0218  2

groups_lipocalin (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5972      0.5972     0.1375  2
  max valid BA                0.5972      0.5972     0.1375  2
  best valid F1               0.5523      0.5523     0.0740  2
  test BA                     0.5278      0.5278     0.0393  2
  test F1                     0.4735      0.4735     0.0374  2
  test sensitivity            0.7639      0.7639     0.3339  2
  test specificity            0.2917      0.2917     0.4125  2
  test precision              0.3605      0.3605     0.0385  2
  test loss                   0.6455      0.6455     0.0545  2
  FPR (FP/(FP+TN))            0.7083      0.7083     0.4125  2
  FNR (FN/(FN+TP))            0.2361      0.2361     0.3339  2

groups_scp2 (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5294      0.5294     0.0294  3
  max valid BA                0.5294      0.5294     0.0294  3
  best valid F1               0.4301      0.5152     0.1615  3
  test BA                     0.4902      0.4853     0.0225  3
  test F1                     0.3284      0.4776     0.2848  3
  test sensitivity            0.6471      0.9412     0.5611  3
  test specificity            0.3333      0.0294     0.5521  3
  test precision              0.2200      0.3200     0.1908  3
  test loss                   0.7392      0.7479     0.0200  3
  FPR (FP/(FP+TN))            0.6667      0.9706     0.5521  3
  FNR (FN/(FN+TP))            0.3529      0.0588     0.5611  3
```

## AUC vs chemistry null model, in-sample increment

### features = tanimoto (full molecular structure)

Failed: scp2/seed2: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label descriptors_no_extent_coarse_add_lipprop_rankprot --seeds=0,1,2,3,4 --features=tanimoto --features-label=tanimoto`
