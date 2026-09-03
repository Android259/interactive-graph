# geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rim_ev28'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4090      0.7475      0.7097      0.6853      0.3910      0.7581
groups_GLTP            5      0.2480      0.7120      0.5923      0.6594      0.3462      0.7538
groups_IP_trans        5      0.3913      0.8085      0.7317      0.6912      0.4917      0.7957
groups_LBP_BPI_CETP    5      0.2783      0.7915      0.7536      0.6719      0.4167      0.7830
groups_START           5      0.2923      0.7685      0.7140      0.6710      0.2687      0.7775
groups_lipocalin       5      0.3833      0.7889      0.6391      0.6474      0.4278      0.7861
groups_scp2            5      0.3176      0.7824      0.6512      0.7161      0.3647      0.8647
ALL                   35      0.3314      0.7713      0.6845      0.6775      0.3867      0.7884

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5876      0.5891     0.0637  35
max valid BA                0.6339      0.6346     0.0724  35
best valid F1               0.5519      0.5714     0.1284  35
test BA                     0.5514      0.5441     0.0768  35
test F1                     0.3647      0.3396     0.1699  35
test sensitivity            0.3314      0.2800     0.1956  35
test specificity            0.7713      0.7778     0.1321  35
test precision              0.5063      0.5000     0.1760  35
test loss                   0.7754      0.6895     0.2459  35
FPR (FP/(FP+TN))            0.2287      0.2222     0.1321  35
FNR (FN/(FN+TP))            0.6686      0.7200     0.1956  35

=== abs(sensitivity-specificity) gap: mean=0.4464 median=0.4392 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5746      0.5769     0.0376  5
  max valid BA                0.6312      0.6241     0.0472  5
  best valid F1               0.6759      0.6706     0.0394  5
  test BA                     0.5782      0.5831     0.0416  5
  test F1                     0.4542      0.5424     0.2341  5
  test sensitivity            0.4090      0.4776     0.2474  5
  test specificity            0.7475      0.6885     0.1760  5
  test precision              0.7159      0.6389     0.1637  5
  test loss                   0.7199      0.6895     0.0506  5
  FPR (FP/(FP+TN))            0.2525      0.3115     0.1760  5
  FNR (FN/(FN+TP))            0.5910      0.5224     0.2474  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5577     0.0322  5
  max valid BA                0.5885      0.5769     0.0349  5
  best valid F1               0.5411      0.5283     0.0835  5
  test BA                     0.4800      0.4800     0.0632  5
  test F1                     0.3089      0.3000     0.1448  5
  test sensitivity            0.2480      0.2400     0.1481  5
  test specificity            0.7120      0.6800     0.0867  5
  test precision              0.4422      0.4286     0.1190  5
  test loss                   0.7462      0.7622     0.0332  5
  FPR (FP/(FP+TN))            0.2880      0.3200     0.0867  5
  FNR (FN/(FN+TP))            0.7520      0.7600     0.1481  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6437      0.6529     0.0344  5
  max valid BA                0.6897      0.6862     0.0608  5
  best valid F1               0.5922      0.5714     0.0749  5
  test BA                     0.5999      0.5999     0.0735  5
  test F1                     0.4095      0.4390     0.1598  5
  test sensitivity            0.3913      0.3913     0.2280  5
  test specificity            0.8085      0.7872     0.1146  5
  test precision              0.5733      0.5000     0.2510  5
  test loss                   0.8970      0.6594     0.5634  5
  FPR (FP/(FP+TN))            0.1915      0.2128     0.1146  5
  FNR (FN/(FN+TP))            0.6087      0.6087     0.2280  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5998      0.5891     0.0673  5
  max valid BA                0.6243      0.6006     0.0806  5
  best valid F1               0.4732      0.5000     0.1900  5
  test BA                     0.5349      0.5005     0.1043  5
  test F1                     0.2871      0.3200     0.2242  5
  test sensitivity            0.2783      0.3478     0.2292  5
  test specificity            0.7915      0.8723     0.2026  5
  test precision              0.4228      0.3333     0.1684  5
  test loss                   0.9049      0.9061     0.2950  5
  FPR (FP/(FP+TN))            0.2085      0.1277     0.2026  5
  FNR (FN/(FN+TP))            0.7217      0.6522     0.2292  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5231      0.5097     0.0949  5
  max valid BA                0.5890      0.5951     0.0926  5
  best valid F1               0.4872      0.6036     0.1867  5
  test BA                     0.5304      0.5022     0.0896  5
  test F1                     0.3347      0.2936     0.1888  5
  test sensitivity            0.2923      0.2462     0.2224  5
  test specificity            0.7685      0.7079     0.1001  5
  test precision              0.4509      0.4255     0.1244  5
  test loss                   0.7990      0.7321     0.1565  5
  FPR (FP/(FP+TN))            0.2315      0.2921     0.1001  5
  FNR (FN/(FN+TP))            0.7077      0.7538     0.2224  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6069      0.6389     0.0588  5
  max valid BA                0.6764      0.6597     0.0993  5
  best valid F1               0.5863      0.5806     0.1072  5
  test BA                     0.5861      0.5694     0.0814  5
  test F1                     0.4148      0.3571     0.1409  5
  test sensitivity            0.3833      0.2778     0.1717  5
  test specificity            0.7889      0.8194     0.1151  5
  test precision              0.4800      0.4200     0.1395  5
  test loss                   0.6622      0.6806     0.0477  5
  FPR (FP/(FP+TN))            0.2111      0.1806     0.1151  5
  FNR (FN/(FN+TP))            0.6167      0.7222     0.1717  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6147      0.6029     0.0351  5
  max valid BA                0.6382      0.6471     0.0339  5
  best valid F1               0.5073      0.5455     0.0725  5
  test BA                     0.5500      0.5588     0.0305  5
  test F1                     0.3439      0.3333     0.0972  5
  test sensitivity            0.3176      0.2353     0.1695  5
  test specificity            0.7824      0.8235     0.1565  5
  test precision              0.4590      0.4091     0.1193  5
  test loss                   0.6985      0.6732     0.1035  5
  FPR (FP/(FP+TN))            0.2176      0.1765     0.1565  5
  FNR (FN/(FN+TP))            0.6824      0.7647     0.1695  5
```

## AUC vs chemistry null model, in-sample increment

