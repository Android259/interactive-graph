# mlp_sub_pb6_hid64_wd003

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_hid64_wd003'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.6848      0.2000      0.7500      0.6043      0.7636      0.2750
groups_FA                                    5      0.3500      0.7784      0.7164      0.6984      0.3167      0.8056
groups_LPC+LPE+LPG                           5      0.4875      0.8774      0.8189      0.6946      0.5750      0.7933
groups_PA                                    5      0.5538      0.8462      0.6263      0.7225      0.5231      0.9385
groups_PC                                    5      0.2917      0.6579      0.5990      0.7269      0.2972      0.6670
groups_PE                                    5      0.8700      0.7600      0.8007      0.7923      0.9200      0.7825
groups_PG                                    5      0.7053      0.8248      0.8468      0.8076      0.7143      0.8071
groups_PI                                    5      0.3500      0.4500      0.7673      0.4165      0.6250      0.4750
groups_PS+PGP+DAG+TAG                        5      0.5333      0.5333      0.6334      0.6625      0.4250      0.5750
ALL                                         45      0.5363      0.6587      0.7288      0.6806      0.5733      0.6799

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6151      0.5833     0.1341  45
max valid BA                0.6266      0.5833     0.1329  45
best valid F1               0.5367      0.5686     0.1754  45
test BA                     0.5975      0.5771     0.1506  45
test AUC                    0.5762      0.5588     0.2183  45
test AUC in-protein         0.6252      0.6637     0.2459  32
  (proteins averaged)       3.0000      2.0000     3.5162  45
test AUC in-protein (pairs)      0.5790      0.5833     0.2386  45
  (proteins contributing)      5.4444      3.0000     4.0819  45
test F1                     0.4826      0.5263     0.2091  45
test sensitivity            0.5363      0.5556     0.2829  45
test specificity            0.6587      0.7838     0.3111  45
test precision              0.5249      0.5167     0.2129  44
test loss                   0.6678      0.6890     0.1501  45
FPR (FP/(FP+TN))            0.3413      0.2162     0.3111  45
FNR (FN/(FN+TP))            0.4637      0.4444     0.2829  45

=== abs(sensitivity-specificity) gap: mean=0.4155 median=0.3730 n=45 ===
sensitivity std across seeds (by group): mean=0.2010 median=0.2054 n=9
specificity std across seeds (by group): mean=0.1985 median=0.1676 n=9

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4785      0.4841     0.0221  5
  max valid BA                0.5193      0.5038     0.0254  5
  best valid F1               0.5870      0.5825     0.0312  5
  test BA                     0.4424      0.4224     0.0510  5
  test AUC                    0.4037      0.3814     0.1070  5
  test AUC in-protein         0.4422      0.4560     0.1186  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.3744      0.3547     0.1264  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4984      0.5208     0.1013  5
  test sensitivity            0.6848      0.7576     0.2430  5
  test specificity            0.2000      0.1951     0.1676  5
  test precision              0.4000      0.3968     0.0442  5
  test loss                   0.7905      0.8279     0.0768  5
  FPR (FP/(FP+TN))            0.8000      0.8049     0.1676  5
  FNR (FN/(FN+TP))            0.3152      0.2424     0.2430  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5569      0.5556     0.0158  5
  max valid BA                0.5611      0.5556     0.0180  5
  best valid F1               0.4464      0.4211     0.0963  5
  test BA                     0.5642      0.5704     0.0593  5
  test AUC                    0.4115      0.3919     0.1260  5
  test AUC in-protein         0.6500      0.8000     0.3226  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.4052      0.4545     0.1498  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3959      0.3226     0.1126  5
  test sensitivity            0.3500      0.2500     0.2054  5
  test specificity            0.7784      0.7838     0.2157  5
  test precision              0.5758      0.4474     0.2158  5
  test loss                   0.7948      0.7477     0.1042  5
  FPR (FP/(FP+TN))            0.2216      0.2162     0.2157  5
  FNR (FN/(FN+TP))            0.6500      0.7500     0.2054  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6650      0.6667     0.0549  5
  max valid BA                0.6842      0.6979     0.0567  5
  best valid F1               0.5705      0.6000     0.1137  5
  test BA                     0.6825      0.7016     0.0583  5
  test AUC                    0.7252      0.7258     0.0884  5
  test AUC in-protein         0.8385      0.8542     0.0805  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.7198      0.7333     0.0548  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5625      0.5926     0.0982  5
  test sensitivity            0.4875      0.5000     0.1027  5
  test specificity            0.8774      0.9032     0.0620  5
  test precision              0.6792      0.6923     0.1073  5
  test loss                   0.5752      0.6040     0.0837  5
  FPR (FP/(FP+TN))            0.1226      0.0968     0.0620  5
  FNR (FN/(FN+TP))            0.5125      0.5000     0.1027  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7269      0.7500     0.0498  5
  max valid BA                0.7308      0.7500     0.0451  5
  best valid F1               0.6358      0.6667     0.0724  5
  test BA                     0.7000      0.7115     0.0421  5
  test AUC                    0.7047      0.7041     0.0366  5
  test AUC in-protein         0.5792      0.6583     0.4685  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.6901      0.7778     0.2730  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.5991      0.6087     0.0500  5
  test sensitivity            0.5538      0.5385     0.0644  5
  test specificity            0.8462      0.8846     0.1216  5
  test precision              0.6822      0.7000     0.1511  5
  test loss                   0.6153      0.6081     0.0395  5
  FPR (FP/(FP+TN))            0.1538      0.1154     0.1216  5
  FNR (FN/(FN+TP))            0.4462      0.4615     0.0644  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4791      0.4772     0.0329  5
  max valid BA                0.4821      0.4772     0.0289  5
  best valid F1               0.3648      0.3938     0.1416  5
  test BA                     0.4748      0.4859     0.0287  5
  test AUC                    0.3691      0.3683     0.0223  5
  test AUC in-protein         0.5286      0.5522     0.1860  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4924      0.5518     0.1286  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.2321      0.2105     0.1706  5
  test sensitivity            0.2917      0.1835     0.3802  5
  test specificity            0.6579      0.7208     0.3616  5
  test precision              0.2980      0.2857     0.0461  5
  test loss                   0.7752      0.7053     0.1528  5
  FPR (FP/(FP+TN))            0.3421      0.2792     0.3616  5
  FNR (FN/(FN+TP))            0.7083      0.8165     0.3802  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8400      0.8313     0.0374  5
  max valid BA                0.8512      0.8375     0.0311  5
  best valid F1               0.7827      0.7660     0.0372  5
  test BA                     0.8150      0.8187     0.0379  5
  test AUC                    0.9088      0.9012     0.0342  5
  test AUC in-protein         0.7679      0.7964     0.1958  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7852      0.8052     0.1248  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7397      0.7473     0.0421  5
  test sensitivity            0.8700      0.8750     0.0779  5
  test specificity            0.7600      0.7750     0.0335  5
  test precision              0.6449      0.6441     0.0324  5
  test loss                   0.4479      0.4563     0.0331  5
  FPR (FP/(FP+TN))            0.2400      0.2250     0.0335  5
  FNR (FN/(FN+TP))            0.1300      0.1250     0.0779  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7518      0.7510     0.0085  5
  max valid BA                0.7607      0.7600     0.0115  5
  best valid F1               0.6794      0.6772     0.0151  5
  test BA                     0.7650      0.7712     0.0219  5
  test AUC                    0.8122      0.8123     0.0327  5
  test AUC in-protein         0.6087      0.5602     0.0810  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.5941      0.5532     0.0790  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6869      0.6949     0.0281  5
  test sensitivity            0.7053      0.7193     0.0380  5
  test specificity            0.8248      0.8230     0.0131  5
  test precision              0.6699      0.6721     0.0231  5
  test loss                   0.5113      0.5097     0.0370  5
  FPR (FP/(FP+TN))            0.1752      0.1770     0.0131  5
  FNR (FN/(FN+TP))            0.2947      0.2807     0.0380  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5375      0.5625     0.0513  5
  max valid BA                0.5500      0.5625     0.0568  5
  best valid F1               0.3869      0.5333     0.2392  5
  test BA                     0.4000      0.4375     0.1069  5
  test AUC                    0.3500      0.3594     0.1370  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.3600      0.5000     0.3507  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.2033      0.1739     0.2113  5
  test sensitivity            0.3500      0.2500     0.3791  5
  test specificity            0.4500      0.1875     0.4494  5
  test precision              0.1798      0.2095     0.1416  4
  test loss                   0.7203      0.7158     0.0350  5
  FPR (FP/(FP+TN))            0.5500      0.8125     0.4494  5
  FNR (FN/(FN+TP))            0.6500      0.7500     0.3791  5

groups_PS+PGP+DAG+TAG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0797  5
  max valid BA                0.5000      0.5000     0.0797  5
  best valid F1               0.3767      0.3636     0.0772  5
  test BA                     0.5333      0.5444     0.0588  5
  test AUC                    0.5007      0.5259     0.1180  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.7900      0.7500     0.2012  5
    (proteins contributing)      2.6000      3.0000     0.8944  5
  test F1                     0.4258      0.4762     0.1414  5
  test sensitivity            0.5333      0.5556     0.3182  5
  test specificity            0.5333      0.5333     0.3621  5
  test precision              0.5250      0.4167     0.2726  5
  test loss                   0.7798      0.7050     0.1328  5
  FPR (FP/(FP+TN))            0.4667      0.4667     0.3621  5
  FNR (FN/(FN+TP))            0.4667      0.4444     0.3182  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_hid64_wd003 --seeds=0,1,2,3,4`
