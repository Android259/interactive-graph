# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_node_bilinear

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_node_bilinear'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4507      0.6951      0.5097      0.6317      0.4657      0.6903
groups_GLTP            5      0.4000      0.5920      0.5979      0.4914      0.4615      0.6077
groups_IP_trans        5      0.3304      0.7191      0.4959      0.6234      0.4000      0.7447
groups_LBP_BPI_CETP    5      0.4261      0.7872      0.5057      0.5845      0.5167      0.7702
groups_START           5      0.3292      0.6787      0.4471      0.5775      0.3219      0.7056
groups_lipocalin       5      0.1722      0.8778      0.4777      0.6177      0.2500      0.8667
groups_scp2            5      0.2588      0.8000      0.5905      0.6372      0.2353      0.8882
ALL                   35      0.3382      0.7357      0.5178      0.5948      0.3787      0.7533

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5660      0.5577     0.0587  35
max valid BA                0.6172      0.6024     0.0807  35
best valid F1               0.5695      0.5745     0.1397  35
test BA                     0.5370      0.5227     0.0581  35
test F1                     0.3263      0.3469     0.2135  35
test sensitivity            0.3382      0.2500     0.2969  35
test specificity            0.7357      0.8235     0.2605  35
test precision              0.4602      0.4401     0.1856  32
test loss                   0.7486      0.6856     0.4149  35
FPR (FP/(FP+TN))            0.2643      0.1765     0.2605  35
FNR (FN/(FN+TP))            0.6618      0.7500     0.2969  35

=== abs(sensitivity-specificity) gap: mean=0.5986 median=0.6137 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5780      0.5820     0.0281  5
  max valid BA                0.6279      0.6351     0.0286  5
  best valid F1               0.7071      0.7011     0.0234  5
  test BA                     0.5729      0.5952     0.0422  5
  test F1                     0.4984      0.5185     0.1470  5
  test sensitivity            0.4507      0.4179     0.2177  5
  test specificity            0.6951      0.7705     0.1600  5
  test precision              0.6199      0.6308     0.0503  5
  test loss                   0.6858      0.6898     0.0182  5
  FPR (FP/(FP+TN))            0.3049      0.2295     0.1600  5
  FNR (FN/(FN+TP))            0.5493      0.5821     0.2177  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5346      0.5385     0.0161  5
  max valid BA                0.5462      0.5385     0.0219  5
  best valid F1               0.6225      0.6667     0.0799  5
  test BA                     0.4960      0.4800     0.0518  5
  test F1                     0.3574      0.3000     0.2727  5
  test sensitivity            0.4000      0.2400     0.3909  5
  test specificity            0.5920      0.6400     0.3242  5
  test precision              0.4372      0.4000     0.0878  5
  test loss                   0.7145      0.7186     0.0175  5
  FPR (FP/(FP+TN))            0.4080      0.3600     0.3242  5
  FNR (FN/(FN+TP))            0.6000      0.7600     0.3909  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5723      0.5824     0.0378  5
  max valid BA                0.6696      0.6197     0.0951  5
  best valid F1               0.6032      0.5542     0.0943  5
  test BA                     0.5248      0.5231     0.0541  5
  test F1                     0.2749      0.2424     0.1996  5
  test sensitivity            0.3304      0.1739     0.3944  5
  test specificity            0.7191      0.8723     0.3671  5
  test precision              0.3410      0.4000     0.2027  5
  test loss                   0.6610      0.6624     0.0384  5
  FPR (FP/(FP+TN))            0.2809      0.1277     0.3671  5
  FNR (FN/(FN+TP))            0.6696      0.8261     0.3944  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6434      0.6126     0.0788  5
  max valid BA                0.6937      0.6964     0.0756  5
  best valid F1               0.5778      0.5909     0.1382  5
  test BA                     0.6067      0.6119     0.0713  5
  test F1                     0.4027      0.4898     0.2341  5
  test sensitivity            0.4261      0.5217     0.2923  5
  test specificity            0.7872      0.7660     0.1627  5
  test precision              0.4187      0.4737     0.2440  5
  test loss                   0.6541      0.6611     0.0227  5
  FPR (FP/(FP+TN))            0.2128      0.2340     0.1627  5
  FNR (FN/(FN+TP))            0.5739      0.4783     0.2923  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5137      0.5112     0.0126  5
  max valid BA                0.5399      0.5456     0.0295  5
  best valid F1               0.4832      0.5899     0.1589  5
  test BA                     0.5039      0.5077     0.0336  5
  test F1                     0.2640      0.2824     0.2539  5
  test sensitivity            0.3292      0.1846     0.4158  5
  test specificity            0.6787      0.9101     0.4296  5
  test precision              0.6011      0.5138     0.2826  4
  test loss                   0.6931      0.6930     0.0069  5
  FPR (FP/(FP+TN))            0.3213      0.0899     0.4296  5
  FNR (FN/(FN+TP))            0.6708      0.8154     0.4158  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5583      0.5417     0.0864  5
  max valid BA                0.6222      0.6389     0.1101  5
  best valid F1               0.4771      0.5155     0.2291  5
  test BA                     0.5250      0.5000     0.0483  5
  test F1                     0.2026      0.2687     0.1925  5
  test sensitivity            0.1722      0.2222     0.1694  5
  test specificity            0.8778      0.9306     0.1408  5
  test precision              0.4524      0.4516     0.1625  3
  test loss                   1.1555      0.6685     1.1026  5
  FPR (FP/(FP+TN))            0.1222      0.0694     0.1408  5
  FNR (FN/(FN+TP))            0.8278      0.7778     0.1694  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5618      0.5588     0.0218  5
  max valid BA                0.6206      0.6029     0.0395  5
  best valid F1               0.5154      0.5263     0.0310  5
  test BA                     0.5294      0.5147     0.0345  5
  test F1                     0.2839      0.2400     0.1421  5
  test sensitivity            0.2588      0.1765     0.1841  5
  test specificity            0.8000      0.8235     0.1202  5
  test precision              0.3759      0.3750     0.0433  5
  test loss                   0.6761      0.6762     0.0095  5
  FPR (FP/(FP+TN))            0.2000      0.1765     0.1202  5
  FNR (FN/(FN+TP))            0.7412      0.8235     0.1841  5
```

## AUC vs chemistry null model, in-sample increment

