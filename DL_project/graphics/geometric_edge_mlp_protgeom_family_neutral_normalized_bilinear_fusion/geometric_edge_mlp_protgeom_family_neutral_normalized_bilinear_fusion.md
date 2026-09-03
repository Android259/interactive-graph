# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.7224      0.4066      0.5914      0.4798      0.7134      0.4161
groups_GLTP            5      0.6320      0.3280      0.5243      0.5433      0.6846      0.4231
groups_IP_trans        5      0.5739      0.5745      0.4826      0.5716      0.6333      0.5617
groups_LBP_BPI_CETP    5      0.5652      0.7064      0.6196      0.4812      0.6000      0.7447
groups_START           5      0.5262      0.4562      0.5549      0.4976      0.5500      0.5011
groups_lipocalin       5      0.7278      0.5472      0.5309      0.5306      0.7111      0.5750
groups_scp2            5      0.7529      0.3765      0.5966      0.4804      0.8118      0.4529
ALL                   35      0.6429      0.4850      0.5572      0.5121      0.6720      0.5250

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6007      0.5769     0.0683  35
max valid BA                0.6557      0.6731     0.0716  35
best valid F1               0.6387      0.6304     0.0531  35
test BA                     0.5640      0.5555     0.0837  35
test F1                     0.5034      0.5373     0.1537  35
test sensitivity            0.6429      0.6716     0.2777  35
test specificity            0.4850      0.5278     0.2998  35
test precision              0.4780      0.4615     0.1274  35
test loss                   7.0065      0.8879    17.5462  35
FPR (FP/(FP+TN))            0.5150      0.4722     0.2998  35
FNR (FN/(FN+TP))            0.3571      0.3284     0.2777  35

=== abs(sensitivity-specificity) gap: mean=0.4603 median=0.4093 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5648      0.5497     0.0311  5
  max valid BA                0.5989      0.5929     0.0251  5
  best valid F1               0.7029      0.7016     0.0140  5
  test BA                     0.5645      0.5645     0.0818  5
  test F1                     0.6354      0.6667     0.0662  5
  test sensitivity            0.7224      0.7164     0.1560  5
  test specificity            0.4066      0.4590     0.2419  5
  test precision              0.5821      0.5932     0.0722  5
  test loss                   3.1419      0.7615     5.2686  5
  FPR (FP/(FP+TN))            0.5934      0.5410     0.2419  5
  FNR (FN/(FN+TP))            0.2776      0.2836     0.1560  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5538      0.5577     0.0316  5
  max valid BA                0.6308      0.6346     0.0798  5
  best valid F1               0.6930      0.6849     0.0272  5
  test BA                     0.4800      0.4800     0.0548  5
  test F1                     0.5151      0.5926     0.1773  5
  test sensitivity            0.6320      0.6400     0.3217  5
  test specificity            0.3280      0.4400     0.2958  5
  test precision              0.4666      0.4815     0.0812  5
  test loss                   1.1406      0.7252     0.7731  5
  FPR (FP/(FP+TN))            0.6720      0.5600     0.2958  5
  FNR (FN/(FN+TP))            0.3680      0.3600     0.3217  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5975      0.5984     0.0664  5
  max valid BA                0.6938      0.7048     0.0240  5
  best valid F1               0.6110      0.6182     0.0304  5
  test BA                     0.5742      0.5578     0.0594  5
  test F1                     0.4267      0.4561     0.1660  5
  test sensitivity            0.5739      0.5652     0.3470  5
  test specificity            0.5745      0.5745     0.3220  5
  test precision              0.4542      0.4000     0.1273  5
  test loss                   9.2940      0.9117    17.3980  5
  FPR (FP/(FP+TN))            0.4255      0.4255     0.3220  5
  FNR (FN/(FN+TP))            0.4261      0.4348     0.3470  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6723      0.6760     0.0325  5
  max valid BA                0.7368      0.7371     0.0373  5
  best valid F1               0.6506      0.6552     0.0500  5
  test BA                     0.6358      0.6383     0.0568  5
  test F1                     0.5053      0.5366     0.1171  5
  test sensitivity            0.5652      0.4783     0.2884  5
  test specificity            0.7064      0.8511     0.2788  5
  test precision              0.5458      0.5000     0.1565  5
  test loss                  25.5356      0.7021    40.2066  5
  FPR (FP/(FP+TN))            0.2936      0.1489     0.2788  5
  FNR (FN/(FN+TP))            0.4348      0.5217     0.2884  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5256      0.5257     0.0135  5
  max valid BA                0.5741      0.5753     0.0397  5
  best valid F1               0.6067      0.6038     0.0092  5
  test BA                     0.4912      0.5132     0.0496  5
  test F1                     0.3817      0.5402     0.2492  5
  test sensitivity            0.5262      0.7231     0.4301  5
  test specificity            0.4562      0.3034     0.3915  5
  test precision              0.4254      0.4312     0.1749  5
  test loss                   3.7365      1.3807     5.1408  5
  FPR (FP/(FP+TN))            0.5438      0.6966     0.3915  5
  FNR (FN/(FN+TP))            0.4738      0.2769     0.4301  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6583      0.6667     0.0752  5
  max valid BA                0.6847      0.6875     0.0595  5
  best valid F1               0.6056      0.6061     0.0491  5
  test BA                     0.6375      0.6528     0.0869  5
  test F1                     0.5609      0.5373     0.0703  5
  test sensitivity            0.7278      0.6944     0.1694  5
  test specificity            0.5472      0.5278     0.2986  5
  test precision              0.4874      0.4412     0.1285  5
  test loss                   4.9409      0.8879     9.1932  5
  FPR (FP/(FP+TN))            0.4528      0.4722     0.2986  5
  FNR (FN/(FN+TP))            0.2722      0.3056     0.1694  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6324      0.6471     0.0560  5
  max valid BA                0.6706      0.7059     0.0710  5
  best valid F1               0.6010      0.6190     0.0518  5
  test BA                     0.5647      0.5441     0.0663  5
  test F1                     0.4988      0.5231     0.0684  5
  test sensitivity            0.7529      0.7059     0.2177  5
  test specificity            0.3765      0.5000     0.2525  5
  test precision              0.3847      0.3542     0.0621  5
  test loss                   1.2561      0.8093     0.9542  5
  FPR (FP/(FP+TN))            0.6235      0.5000     0.2525  5
  FNR (FN/(FN+TP))            0.2471      0.2941     0.2177  5
```

## AUC vs chemistry null model, in-sample increment

