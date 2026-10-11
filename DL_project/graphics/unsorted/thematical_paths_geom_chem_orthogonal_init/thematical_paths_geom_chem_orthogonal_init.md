# thematical_paths_geom_chem_orthogonal_init

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'thematical_paths_geom_chem_orthogonal_init'
rows: 33

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       4      0.2463      0.8279      0.6571      0.7878      0.3246      0.8105
groups_GLTP            5      0.6000      0.7440      0.8637      0.7800      0.7154      0.7000
groups_IP_trans        5      0.5652      0.5574      0.7311      0.6917      0.5750      0.5957
groups_LBP_BPI_CETP    5      0.2261      0.8170      0.8619      0.7943      0.3667      0.8681
groups_START           5      0.3446      0.7596      0.4833      0.7812      0.3187      0.7685
groups_lipocalin       4      0.5694      0.5486      0.6781      0.5638      0.5278      0.5347
groups_scp2            5      0.5647      0.5588      0.8778      0.6228      0.6353      0.5941
ALL                   33      0.4475      0.6876      0.7403      0.7199      0.4989      0.6974

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5982      0.5769     0.0961  33
max valid BA                0.6222      0.5972     0.0979  33
best valid F1               0.5582      0.5366     0.1214  33
test BA                     0.5675      0.5294     0.0986  33
test F1                     0.3912      0.4167     0.2342  33
test sensitivity            0.4475      0.4706     0.3335  33
test specificity            0.6876      0.7541     0.2927  33
test precision              0.4857      0.4483     0.1635  29
test loss                   0.7270      0.6982     0.1143  33
FPR (FP/(FP+TN))            0.3124      0.2459     0.2927  33
FNR (FN/(FN+TP))            0.5525      0.5294     0.3335  33

=== abs(sensitivity-specificity) gap: mean=0.5353 median=0.5004 n=33 ===

=== By group ===
groups_CRAL-TRIO (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5676      0.5659     0.0566  4
  max valid BA                0.5832      0.5846     0.0475  4
  best valid F1               0.5684      0.6265     0.1275  4
  test BA                     0.5371      0.5262     0.0449  4
  test F1                     0.3041      0.3146     0.2412  4
  test sensitivity            0.2463      0.2164     0.2301  4
  test specificity            0.8279      0.8361     0.1620  4
  test precision              0.6214      0.6271     0.0875  3
  test loss                   0.8132      0.7922     0.1428  4
  FPR (FP/(FP+TN))            0.1721      0.1639     0.1620  4
  FNR (FN/(FN+TP))            0.7537      0.7836     0.2301  4

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7077      0.6923     0.1504  5
  max valid BA                0.7346      0.7308     0.1389  5
  best valid F1               0.7300      0.6923     0.1326  5
  test BA                     0.6720      0.7000     0.1836  5
  test F1                     0.6398      0.6818     0.2127  5
  test sensitivity            0.6000      0.6000     0.2173  5
  test specificity            0.7440      0.7600     0.2202  5
  test precision              0.7038      0.7083     0.2069  5
  test loss                   0.6710      0.6335     0.2035  5
  FPR (FP/(FP+TN))            0.2560      0.2400     0.2202  5
  FNR (FN/(FN+TP))            0.4000      0.4000     0.2173  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5854      0.6277     0.0791  5
  max valid BA                0.6016      0.6348     0.0833  5
  best valid F1               0.5215      0.5053     0.0656  5
  test BA                     0.5613      0.5241     0.0764  5
  test F1                     0.3799      0.4946     0.2369  5
  test sensitivity            0.5652      0.5652     0.4445  5
  test specificity            0.5574      0.6596     0.3927  5
  test precision              0.3944      0.4005     0.0536  4
  test loss                   0.7672      0.7316     0.1089  5
  FPR (FP/(FP+TN))            0.4426      0.3404     0.3927  5
  FNR (FN/(FN+TP))            0.4348      0.4348     0.4445  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6174      0.6033     0.0677  5
  max valid BA                0.6528      0.6653     0.0730  5
  best valid F1               0.5281      0.5366     0.1101  5
  test BA                     0.5216      0.5116     0.0391  5
  test F1                     0.2652      0.2162     0.1203  5
  test sensitivity            0.2261      0.1739     0.1422  5
  test specificity            0.8170      0.8298     0.0935  5
  test precision              0.3705      0.4000     0.0761  5
  test loss                   0.7300      0.7084     0.0678  5
  FPR (FP/(FP+TN))            0.1830      0.1702     0.0935  5
  FNR (FN/(FN+TP))            0.7739      0.8261     0.1422  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5436      0.5257     0.0499  5
  max valid BA                0.5722      0.5404     0.0713  5
  best valid F1               0.5036      0.4571     0.1280  5
  test BA                     0.5521      0.5000     0.0795  5
  test F1                     0.3151      0.3048     0.3032  5
  test sensitivity            0.3446      0.2462     0.3690  5
  test specificity            0.7596      0.7303     0.2351  5
  test precision              0.4561      0.4549     0.1106  4
  test loss                   0.6794      0.6851     0.0198  5
  FPR (FP/(FP+TN))            0.2404      0.2697     0.2351  5
  FNR (FN/(FN+TP))            0.6554      0.7538     0.3690  5

groups_lipocalin (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5312      0.5312     0.0361  4
  max valid BA                0.5503      0.5521     0.0505  4
  best valid F1               0.4901      0.5000     0.0402  4
  test BA                     0.5590      0.5174     0.0963  4
  test F1                     0.3829      0.4573     0.2684  4
  test sensitivity            0.5694      0.6389     0.4377  4
  test specificity            0.5486      0.5972     0.4121  4
  test precision              0.4010      0.3696     0.0877  3
  test loss                   0.7283      0.7026     0.0820  4
  FPR (FP/(FP+TN))            0.4514      0.4028     0.4121  4
  FNR (FN/(FN+TP))            0.4306      0.3611     0.4377  4

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6147      0.6029     0.0972  5
  max valid BA                0.6382      0.6618     0.0934  5
  best valid F1               0.5540      0.5185     0.0764  5
  test BA                     0.5618      0.5294     0.0644  5
  test F1                     0.4325      0.4815     0.1381  5
  test sensitivity            0.5647      0.4706     0.3343  5
  test specificity            0.5588      0.7059     0.3990  5
  test precision              0.4489      0.4444     0.1153  5
  test loss                   0.7177      0.7276     0.0984  5
  FPR (FP/(FP+TN))            0.4412      0.2941     0.3990  5
  FNR (FN/(FN+TP))            0.4353      0.5294     0.3343  5
```

## AUC vs chemistry null model, in-sample increment

