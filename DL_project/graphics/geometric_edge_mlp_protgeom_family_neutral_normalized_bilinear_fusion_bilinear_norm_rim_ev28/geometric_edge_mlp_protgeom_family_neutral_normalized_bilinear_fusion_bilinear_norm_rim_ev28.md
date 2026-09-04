# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4269      0.6820      0.6914      0.7104      0.4537      0.6581
groups_GLTP            5      0.3040      0.6400      0.5629      0.5897      0.4231      0.6538
groups_IP_trans        5      0.3043      0.8426      0.6485      0.6628      0.4167      0.8681
groups_LBP_BPI_CETP    5      0.1913      0.9106      0.7438      0.6389      0.2833      0.8511
groups_START           5      0.4185      0.5551      0.6020      0.5164      0.4375      0.5685
groups_lipocalin       5      0.2444      0.7722      0.5768      0.6639      0.3778      0.7806
groups_scp2            5      0.2824      0.8647      0.6396      0.6946      0.3412      0.8824
ALL                   35      0.3103      0.7524      0.6379      0.6395      0.3905      0.7518

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5720      0.5577     0.0688  35
max valid BA                0.6072      0.5981     0.0797  35
best valid F1               0.5379      0.5600     0.1427  35
test BA                     0.5314      0.5222     0.0631  35
test F1                     0.3077      0.3333     0.2098  35
test sensitivity            0.3103      0.2537     0.3000  35
test specificity            0.7524      0.8085     0.2698  35
test precision              0.4322      0.4615     0.1532  33
test loss                   0.6987      0.6878     0.1199  35
FPR (FP/(FP+TN))            0.2476      0.1915     0.2698  35
FNR (FN/(FN+TP))            0.6897      0.7463     0.3000  35

=== abs(sensitivity-specificity) gap: mean=0.6509 median=0.7200 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5559      0.5593     0.0459  5
  max valid BA                0.5947      0.5981     0.0449  5
  best valid F1               0.6802      0.6957     0.0483  5
  test BA                     0.5544      0.5487     0.0221  5
  test F1                     0.4664      0.4381     0.1387  5
  test sensitivity            0.4269      0.3433     0.2731  5
  test specificity            0.6820      0.7869     0.2355  5
  test precision              0.6037      0.6053     0.0246  5
  test loss                   0.6986      0.6969     0.0209  5
  FPR (FP/(FP+TN))            0.3180      0.2131     0.2355  5
  FNR (FN/(FN+TP))            0.5731      0.6567     0.2731  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5385      0.5577     0.0272  5
  max valid BA                0.5538      0.5577     0.0316  5
  best valid F1               0.5773      0.6269     0.1327  5
  test BA                     0.4720      0.4800     0.0303  5
  test F1                     0.2927      0.1935     0.2134  5
  test sensitivity            0.3040      0.1200     0.3716  5
  test specificity            0.6400      0.8000     0.3476  5
  test precision              0.4229      0.4286     0.0884  5
  test loss                   0.7156      0.7242     0.0212  5
  FPR (FP/(FP+TN))            0.3600      0.2000     0.3476  5
  FNR (FN/(FN+TP))            0.6960      0.8800     0.3716  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6424      0.6649     0.0509  5
  max valid BA                0.7145      0.7367     0.0521  5
  best valid F1               0.6195      0.6545     0.0750  5
  test BA                     0.5735      0.5782     0.0368  5
  test F1                     0.3682      0.3889     0.0868  5
  test sensitivity            0.3043      0.3043     0.0972  5
  test specificity            0.8426      0.8511     0.0323  5
  test precision              0.4794      0.4706     0.0557  5
  test loss                   0.6253      0.6219     0.0133  5
  FPR (FP/(FP+TN))            0.1574      0.1489     0.0323  5
  FNR (FN/(FN+TP))            0.6957      0.6957     0.0972  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5672      0.5612     0.0409  5
  max valid BA                0.6131      0.6037     0.0417  5
  best valid F1               0.4466      0.5053     0.1191  5
  test BA                     0.5510      0.5222     0.0805  5
  test F1                     0.2160      0.1481     0.2301  5
  test sensitivity            0.1913      0.0870     0.2655  5
  test specificity            0.9106      0.9574     0.1057  5
  test precision              0.3881      0.5000     0.2353  5
  test loss                   0.8025      0.6412     0.3034  5
  FPR (FP/(FP+TN))            0.0894      0.0426     0.1057  5
  FNR (FN/(FN+TP))            0.8087      0.9130     0.2655  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5030      0.5000     0.0056  5
  max valid BA                0.5110      0.5044     0.0133  5
  best valid F1               0.4410      0.3594     0.1364  5
  test BA                     0.4868      0.5000     0.0277  5
  test F1                     0.2661      0.1136     0.3019  5
  test sensitivity            0.4185      0.0769     0.5316  5
  test specificity            0.5551      0.7978     0.5127  5
  test precision              0.3487      0.3777     0.0970  4
  test loss                   0.7055      0.7000     0.0188  5
  FPR (FP/(FP+TN))            0.4449      0.2022     0.5127  5
  FNR (FN/(FN+TP))            0.5815      0.9231     0.5316  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5792      0.5278     0.0993  5
  max valid BA                0.6042      0.6250     0.0943  5
  best valid F1               0.4368      0.5000     0.1989  5
  test BA                     0.5083      0.5000     0.0705  5
  test F1                     0.2194      0.0870     0.2308  5
  test sensitivity            0.2444      0.0556     0.2909  5
  test specificity            0.7722      0.7778     0.1804  5
  test precision              0.2812      0.2977     0.1498  4
  test loss                   0.6954      0.6938     0.0669  5
  FPR (FP/(FP+TN))            0.2278      0.2222     0.1804  5
  FNR (FN/(FN+TP))            0.7556      0.9444     0.2909  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6176      0.6324     0.0819  5
  max valid BA                0.6588      0.6618     0.0661  5
  best valid F1               0.5641      0.5484     0.0617  5
  test BA                     0.5735      0.6029     0.0757  5
  test F1                     0.3249      0.4000     0.2130  5
  test sensitivity            0.2824      0.2941     0.2217  5
  test specificity            0.8647      0.9118     0.0795  5
  test precision              0.4542      0.5294     0.1560  5
  test loss                   0.6480      0.6516     0.0186  5
  FPR (FP/(FP+TN))            0.1353      0.0882     0.0795  5
  FNR (FN/(FN+TP))            0.7176      0.7059     0.2217  5
```

## AUC vs chemistry null model, in-sample increment

(skipped: SKIP_AUC=1 -- rerun without it to fill this in: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28 --seeds=0,1,2,3,4`)
