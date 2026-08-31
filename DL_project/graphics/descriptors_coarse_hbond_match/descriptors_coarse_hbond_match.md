# descriptors_coarse_hbond_match

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_coarse_hbond_match'
rows: 11

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       2      0.4030      0.7377      0.5229      0.5994      0.4179      0.7419
groups_GLTP            3      0.6533      0.3733      0.5861      0.5543      0.7179      0.4487
groups_IP_trans        1      0.4783      0.8085      0.4656      0.6074      0.4583      0.6809
groups_LBP_BPI_CETP    1      0.8696      0.8085      0.6005      0.5979      0.8750      0.7872
groups_START           2      0.2077      0.8258      0.4966      0.6092      0.2031      0.8371
groups_lipocalin       1      0.5833      0.5278      0.6514      0.5061      0.7222      0.5556
groups_scp2            1      0.1765      0.6471      0.5398      0.6043      0.3529      0.9118
ALL                   11      0.4808      0.6399      0.5504      0.5814      0.5277      0.6763

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6020      0.5962     0.0878  11
max valid BA                0.6278      0.5962     0.0954  11
best valid F1               0.5950      0.5882     0.1353  11
test BA                     0.5604      0.5376     0.1088  11
test F1                     0.4671      0.4815     0.1713  11
test sensitivity            0.4808      0.4179     0.2586  11
test specificity            0.6399      0.7213     0.2347  11
test precision              0.5110      0.5294     0.1379  11
test loss                   0.6875      0.6928     0.0313  11
FPR (FP/(FP+TN))            0.3601      0.2787     0.2347  11
FNR (FN/(FN+TP))            0.5192      0.5821     0.2586  11

=== abs(sensitivity-specificity) gap: mean=0.3912 median=0.3600 n=11 ===

=== By group ===
groups_CRAL-TRIO (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5799      0.5799     0.0448  2
  max valid BA                0.6223      0.6223     0.0836  2
  best valid F1               0.6552      0.6552     0.0878  2
  test BA                     0.5703      0.5703     0.0010  2
  test F1                     0.4907      0.4907     0.0131  2
  test sensitivity            0.4030      0.4030     0.0211  2
  test specificity            0.7377      0.7377     0.0232  2
  test precision              0.6282      0.6282     0.0084  2
  test loss                   0.6917      0.6917     0.0014  2
  FPR (FP/(FP+TN))            0.2623      0.2623     0.0232  2
  FNR (FN/(FN+TP))            0.5970      0.5970     0.0211  2

groups_GLTP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5833      0.5962     0.0222  3
  max valid BA                0.6346      0.5962     0.1018  3
  best valid F1               0.6917      0.6933     0.1027  3
  test BA                     0.5133      0.5200     0.0115  3
  test F1                     0.5540      0.5763     0.1159  3
  test sensitivity            0.6533      0.6800     0.2810  3
  test specificity            0.3733      0.3200     0.2838  3
  test precision              0.5135      0.5111     0.0149  3
  test loss                   0.7034      0.7011     0.0229  3
  FPR (FP/(FP+TN))            0.6267      0.6800     0.2838  3
  FNR (FN/(FN+TP))            0.3467      0.3200     0.2810  3

groups_IP_trans (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5696      0.5696     0.0000  1
  max valid BA                0.5696      0.5696     0.0000  1
  best valid F1               0.4938      0.4938     0.0000  1
  test BA                     0.6434      0.6434     0.0000  1
  test F1                     0.5116      0.5116     0.0000  1
  test sensitivity            0.4783      0.4783     0.0000  1
  test specificity            0.8085      0.8085     0.0000  1
  test precision              0.5500      0.5500     0.0000  1
  test loss                   0.6808      0.6808     0.0000  1
  FPR (FP/(FP+TN))            0.1915      0.1915     0.0000  1
  FNR (FN/(FN+TP))            0.5217      0.5217     0.0000  1

groups_LBP_BPI_CETP (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8311      0.8311     0.0000  1
  max valid BA                0.8311      0.8311     0.0000  1
  best valid F1               0.7636      0.7636     0.0000  1
  test BA                     0.8390      0.8390     0.0000  1
  test F1                     0.7692      0.7692     0.0000  1
  test sensitivity            0.8696      0.8696     0.0000  1
  test specificity            0.8085      0.8085     0.0000  1
  test precision              0.6897      0.6897     0.0000  1
  test loss                   0.6010      0.6010     0.0000  1
  FPR (FP/(FP+TN))            0.1915      0.1915     0.0000  1
  FNR (FN/(FN+TP))            0.1304      0.1304     0.0000  1

groups_START (n=2):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5201      0.5201     0.0526  2
  max valid BA                0.5359      0.5359     0.0304  2
  best valid F1               0.4361      0.4361     0.1061  2
  test BA                     0.5168      0.5168     0.0295  2
  test F1                     0.2823      0.2823     0.0543  2
  test sensitivity            0.2077      0.2077     0.0761  2
  test specificity            0.8258      0.8258     0.1351  2
  test precision              0.5014      0.5014     0.1228  2
  test loss                   0.6963      0.6963     0.0083  2
  FPR (FP/(FP+TN))            0.1742      0.1742     0.1351  2
  FNR (FN/(FN+TP))            0.7923      0.7923     0.0761  2

groups_lipocalin (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6389      0.6389     0.0000  1
  max valid BA                0.6528      0.6528     0.0000  1
  best valid F1               0.5684      0.5684     0.0000  1
  test BA                     0.5556      0.5556     0.0000  1
  test F1                     0.4615      0.4615     0.0000  1
  test sensitivity            0.5833      0.5833     0.0000  1
  test specificity            0.5278      0.5278     0.0000  1
  test precision              0.3818      0.3818     0.0000  1
  test loss                   0.6928      0.6928     0.0000  1
  FPR (FP/(FP+TN))            0.4722      0.4722     0.0000  1
  FNR (FN/(FN+TP))            0.4167      0.4167     0.0000  1

groups_scp2 (n=1):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6324      0.6324     0.0000  1
  max valid BA                0.6324      0.6324     0.0000  1
  best valid F1               0.4615      0.4615     0.0000  1
  test BA                     0.4118      0.4118     0.0000  1
  test F1                     0.1875      0.1875     0.0000  1
  test sensitivity            0.1765      0.1765     0.0000  1
  test specificity            0.6471      0.6471     0.0000  1
  test precision              0.2000      0.2000     0.0000  1
  test loss                   0.7010      0.7010     0.0000  1
  FPR (FP/(FP+TN))            0.3529      0.3529     0.0000  1
  FNR (FN/(FN+TP))            0.8235      0.8235     0.0000  1
```

## AUC vs chemistry null model, in-sample increment

