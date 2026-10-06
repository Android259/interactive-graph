# bbp_pcs_rand_fa_nps3mlp_dpt01_wd0001_gm_plm64_hid64

## Summary (analysis/summarize_label.py)

```
Summary: 'bbp_pcs_rand_fa_nps3mlp_dpt01_wd0001_gm_plm64_hid64'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.5253      0.6024      0.8286      0.7154      0.5707      0.6085
groups_GLTP            5      0.0387      0.6710      0.9399      0.8483      0.0839      0.6968
groups_IP_trans        5      0.6621      0.6379      0.7635      0.6543      0.7241      0.6655
groups_LBP_BPI_CETP    5      0.7481      0.7245      0.8602      0.7487      0.7385      0.7849
groups_START           5      0.3867      0.6640      0.9248      0.8477      0.4507      0.6893
groups_lipocalin       5      0.4140      0.6805      0.9009      0.8104      0.4727      0.6690
groups_scp2            5      0.4286      0.8140      0.9410      0.8574      0.4091      0.8326
ALL                   35      0.4576      0.6849      0.8799      0.7832      0.4928      0.7066

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5997      0.6122     0.1265  35
max valid BA                0.6673      0.7029     0.1312  35
best valid F1               0.5587      0.6245     0.1896  35
test BA                     0.5713      0.5731     0.1356  35
test F1                     0.4157      0.4138     0.2093  35
test sensitivity            0.4576      0.4933     0.2648  35
test specificity            0.6849      0.6909     0.1033  35
test precision              0.3962      0.4277     0.1829  35
test loss                   1.2989      0.8969     1.1453  35
FPR (FP/(FP+TN))            0.3151      0.3091     0.1033  35
FNR (FN/(FN+TP))            0.5424      0.5067     0.2648  35

=== abs(sensitivity-specificity) gap: mean=0.3093 median=0.2800 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5896      0.5592     0.1039  5
  max valid BA                0.6593      0.6360     0.0622  5
  best valid F1               0.5732      0.5681     0.0710  5
  test BA                     0.5639      0.6196     0.1276  5
  test F1                     0.4334      0.5029     0.1821  5
  test sensitivity            0.5253      0.5301     0.2844  5
  test specificity            0.6024      0.6182     0.1077  5
  test precision              0.3805      0.4277     0.1297  5
  test loss                   0.6888      0.6338     0.1303  5
  FPR (FP/(FP+TN))            0.3976      0.3818     0.1077  5
  FNR (FN/(FN+TP))            0.4747      0.4699     0.2844  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.3903      0.4032     0.0583  5
  max valid BA                0.4177      0.4113     0.0508  5
  best valid F1               0.1573      0.1515     0.0381  5
  test BA                     0.3548      0.3629     0.0431  5
  test F1                     0.0458      0.0392     0.0404  5
  test sensitivity            0.0387      0.0323     0.0353  5
  test specificity            0.6710      0.6774     0.0709  5
  test precision              0.0571      0.0500     0.0478  5
  test loss                   3.7024      3.2662     1.3119  5
  FPR (FP/(FP+TN))            0.3290      0.3226     0.0709  5
  FNR (FN/(FN+TP))            0.9613      0.9677     0.0353  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6948      0.6897     0.0290  5
  max valid BA                0.7052      0.7241     0.0342  5
  best valid F1               0.6208      0.6389     0.0307  5
  test BA                     0.6500      0.6552     0.0283  5
  test F1                     0.5561      0.5538     0.0202  5
  test sensitivity            0.6621      0.6207     0.1046  5
  test specificity            0.6379      0.6897     0.1483  5
  test precision              0.4939      0.5000     0.0771  5
  test loss                   0.7910      0.6696     0.2173  5
  FPR (FP/(FP+TN))            0.3621      0.3103     0.1483  5
  FNR (FN/(FN+TP))            0.3379      0.3793     0.1046  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7617      0.7536     0.0160  5
  max valid BA                0.8230      0.8284     0.0450  5
  best valid F1               0.7583      0.7692     0.0586  5
  test BA                     0.7363      0.7103     0.0516  5
  test F1                     0.6537      0.6230     0.0611  5
  test sensitivity            0.7481      0.7407     0.0884  5
  test specificity            0.7245      0.7170     0.0688  5
  test precision              0.5841      0.5750     0.0642  5
  test loss                   0.6490      0.7060     0.1457  5
  FPR (FP/(FP+TN))            0.2755      0.2830     0.0688  5
  FNR (FN/(FN+TP))            0.2519      0.2593     0.0884  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5700      0.5700     0.0709  5
  max valid BA                0.6100      0.6067     0.0749  5
  best valid F1               0.5173      0.5056     0.0808  5
  test BA                     0.5253      0.5133     0.0739  5
  test F1                     0.3698      0.3613     0.1144  5
  test sensitivity            0.3867      0.3733     0.1417  5
  test specificity            0.6640      0.6533     0.0767  5
  test precision              0.3599      0.3500     0.0945  5
  test loss                   1.2182      1.2376     0.3253  5
  FPR (FP/(FP+TN))            0.3360      0.3467     0.0767  5
  FNR (FN/(FN+TP))            0.6133      0.6267     0.1417  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5708      0.5892     0.1011  5
  max valid BA                0.7225      0.7260     0.0685  5
  best valid F1               0.6323      0.6383     0.0917  5
  test BA                     0.5472      0.5076     0.1238  5
  test F1                     0.3915      0.3333     0.1654  5
  test sensitivity            0.4140      0.3256     0.2196  5
  test specificity            0.6805      0.7011     0.0470  5
  test precision              0.3763      0.3415     0.1272  5
  test loss                   1.1509      0.9741     0.5899  5
  FPR (FP/(FP+TN))            0.3195      0.2989     0.0470  5
  FNR (FN/(FN+TP))            0.5860      0.6744     0.2196  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6208      0.6126     0.0605  5
  max valid BA                0.7334      0.7484     0.0548  5
  best valid F1               0.6516      0.6667     0.0627  5
  test BA                     0.6213      0.5731     0.0834  5
  test F1                     0.4597      0.4000     0.1430  5
  test sensitivity            0.4286      0.3810     0.1844  5
  test specificity            0.8140      0.8372     0.0658  5
  test precision              0.5219      0.5000     0.0896  5
  test loss                   0.8916      1.0110     0.3294  5
  FPR (FP/(FP+TN))            0.1860      0.1628     0.0658  5
  FNR (FN/(FN+TP))            0.5714      0.6190     0.1844  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label bbp_pcs_rand_fa_nps3mlp_dpt01_wd0001_gm_plm64_hid64 --seeds=0,1,2,3,4`
