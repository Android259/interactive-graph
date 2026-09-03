# geometric_edge_mlp_protgeom8_normalized_rankprot

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom8_normalized_rankprot'
rows: 34

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4478      0.5803      0.6577      0.4695      0.4299      0.5742
groups_GLTP            5      0.5440      0.4960      0.6105      0.5426      0.6462      0.5923
groups_IP_trans        5      0.6696      0.5404      0.5609      0.5680      0.6833      0.6043
groups_LBP_BPI_CETP    5      0.6000      0.4809      0.5840      0.5157      0.6000      0.4851
groups_START           5      0.7631      0.2831      0.6164      0.4526      0.7719      0.2787
groups_lipocalin       5      0.5500      0.5889      0.5358      0.5673      0.5222      0.6556
groups_scp2            4      0.5588      0.5000      0.7220      0.4849      0.6324      0.5441
ALL                   34      0.5914      0.4955      0.6093      0.5152      0.6117      0.5331

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5736      0.5370     0.0793  34
max valid BA                0.6044      0.6043     0.0771  34
best valid F1               0.5927      0.5900     0.0869  34
test BA                     0.5435      0.5164     0.0739  34
test F1                     0.4325      0.4946     0.1993  34
test sensitivity            0.5914      0.6872     0.3780  34
test specificity            0.4955      0.4700     0.3798  34
test precision              0.4856      0.4835     0.1683  33
test loss                   0.7104      0.6717     0.1775  34
FPR (FP/(FP+TN))            0.5045      0.5300     0.3798  34
FNR (FN/(FN+TP))            0.4086      0.3128     0.3780  34

=== abs(sensitivity-specificity) gap: mean=0.6820 median=0.7381 n=34 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5020      0.5000     0.0163  5
  max valid BA                0.5455      0.5394     0.0412  5
  best valid F1               0.6906      0.6842     0.0094  5
  test BA                     0.5140      0.5000     0.0236  5
  test F1                     0.3609      0.1892     0.2992  5
  test sensitivity            0.4478      0.1045     0.5044  5
  test specificity            0.5803      0.9180     0.5307  5
  test precision              0.6694      0.5234     0.2223  5
  test loss                   0.7621      0.7063     0.1884  5
  FPR (FP/(FP+TN))            0.4197      0.0820     0.5307  5
  FNR (FN/(FN+TP))            0.5522      0.8955     0.5044  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6192      0.5962     0.0875  5
  max valid BA                0.6269      0.6154     0.0845  5
  best valid F1               0.6957      0.6667     0.0553  5
  test BA                     0.5200      0.4800     0.0883  5
  test F1                     0.4964      0.5667     0.1763  5
  test sensitivity            0.5440      0.6800     0.3028  5
  test specificity            0.4960      0.3600     0.3413  5
  test precision              0.5725      0.4878     0.2525  5
  test loss                   0.7546      0.7010     0.2368  5
  FPR (FP/(FP+TN))            0.5040      0.6400     0.3413  5
  FNR (FN/(FN+TP))            0.4560      0.3200     0.3028  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6438      0.6742     0.0896  5
  max valid BA                0.6603      0.6848     0.0955  5
  best valid F1               0.5890      0.5882     0.0612  5
  test BA                     0.6050      0.6448     0.0866  5
  test F1                     0.4965      0.5385     0.1284  5
  test sensitivity            0.6696      0.6087     0.3084  5
  test specificity            0.5404      0.6809     0.3339  5
  test precision              0.4362      0.4468     0.0821  5
  test loss                   0.6393      0.6213     0.1022  5
  FPR (FP/(FP+TN))            0.4596      0.3191     0.3339  5
  FNR (FN/(FN+TP))            0.3304      0.3913     0.3084  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5426      0.5204     0.0731  5
  max valid BA                0.5804      0.5922     0.0791  5
  best valid F1               0.5173      0.5053     0.0466  5
  test BA                     0.5404      0.5111     0.0724  5
  test F1                     0.3611      0.4946     0.2300  5
  test sensitivity            0.6000      0.8696     0.4913  5
  test specificity            0.4809      0.4681     0.4842  5
  test precision              0.4203      0.4444     0.0868  5
  test loss                   0.6968      0.6529     0.0926  5
  FPR (FP/(FP+TN))            0.5191      0.5319     0.4842  5
  FNR (FN/(FN+TP))            0.4000      0.1304     0.4913  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5253      0.5029     0.0409  5
  max valid BA                0.5519      0.5531     0.0426  5
  best valid F1               0.5591      0.5899     0.0894  5
  test BA                     0.5231      0.5092     0.0315  5
  test F1                     0.5175      0.5936     0.1552  5
  test sensitivity            0.7631      0.9846     0.3674  5
  test specificity            0.2831      0.0337     0.4035  5
  test precision              0.4620      0.4267     0.0584  5
  test loss                   0.8494      0.7360     0.2858  5
  FPR (FP/(FP+TN))            0.7169      0.9663     0.4035  5
  FNR (FN/(FN+TP))            0.2369      0.0154     0.3674  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5972      0.6042     0.0762  5
  max valid BA                0.6306      0.6597     0.0750  5
  best valid F1               0.5389      0.5397     0.0733  5
  test BA                     0.5694      0.5486     0.0948  5
  test F1                     0.3823      0.4425     0.2521  5
  test sensitivity            0.5500      0.6944     0.4327  5
  test specificity            0.5889      0.5833     0.3644  5
  test precision              0.4280      0.4395     0.0907  4
  test loss                   0.6585      0.6645     0.0786  5
  FPR (FP/(FP+TN))            0.4111      0.4167     0.3644  5
  FNR (FN/(FN+TP))            0.4500      0.3056     0.4327  5

groups_scp2 (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5882      0.5809     0.0624  4
  max valid BA                0.6434      0.6397     0.0515  4
  best valid F1               0.5496      0.5406     0.0306  4
  test BA                     0.5294      0.5368     0.0890  4
  test F1                     0.4078      0.4145     0.1377  4
  test sensitivity            0.5588      0.5000     0.3610  4
  test specificity            0.5000      0.4412     0.3085  4
  test precision              0.3776      0.3598     0.1355  4
  test loss                   0.5874      0.5944     0.0929  4
  FPR (FP/(FP+TN))            0.5000      0.5588     0.3085  4
  FNR (FN/(FN+TP))            0.4412      0.5000     0.3610  4
```

## AUC vs chemistry null model, in-sample increment

