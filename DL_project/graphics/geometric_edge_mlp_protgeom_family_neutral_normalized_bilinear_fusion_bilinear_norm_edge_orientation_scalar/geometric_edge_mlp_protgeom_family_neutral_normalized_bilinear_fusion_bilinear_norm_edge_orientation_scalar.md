# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_edge_orientation_scalar

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_edge_orientation_scalar'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.2328      0.8328      0.5777      0.7323      0.2119      0.8645
groups_GLTP            5      0.1520      0.7520      0.4673      0.6912      0.3077      0.7846
groups_IP_trans        5      0.4348      0.7745      0.6860      0.6521      0.4917      0.8043
groups_LBP_BPI_CETP    5      0.2348      0.9489      0.7165      0.6459      0.2500      0.9021
groups_START           5      0.3631      0.6382      0.5529      0.5836      0.3844      0.6449
groups_lipocalin       5      0.1556      0.8917      0.5333      0.6737      0.1389      0.8750
groups_scp2            5      0.5176      0.7118      0.6142      0.6755      0.4235      0.7588
ALL                   35      0.2987      0.7928      0.5925      0.6649      0.3154      0.8049

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5596      0.5385     0.0583  35
max valid BA                0.5960      0.5882     0.0770  35
best valid F1               0.5143      0.5446     0.1297  35
test BA                     0.5458      0.5417     0.0728  35
test F1                     0.3227      0.3607     0.1968  35
test sensitivity            0.2987      0.3043     0.2177  35
test specificity            0.7928      0.7978     0.1668  35
test precision              0.4756      0.4400     0.1622  31
test loss                   0.6808      0.6824     0.0571  35
FPR (FP/(FP+TN))            0.2072      0.2022     0.1668  35
FNR (FN/(FN+TP))            0.7013      0.6957     0.2177  35

=== abs(sensitivity-specificity) gap: mean=0.5292 median=0.4722 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5382      0.5292     0.0390  5
  max valid BA                0.5828      0.5916     0.0504  5
  best valid F1               0.5929      0.6707     0.1672  5
  test BA                     0.5328      0.5384     0.0391  5
  test F1                     0.2810      0.3023     0.2500  5
  test sensitivity            0.2328      0.1940     0.2361  5
  test specificity            0.8328      0.9016     0.1896  5
  test precision              0.5779      0.6136     0.1305  4
  test loss                   0.7167      0.6960     0.0352  5
  FPR (FP/(FP+TN))            0.1672      0.0984     0.1896  5
  FNR (FN/(FN+TP))            0.7672      0.8060     0.2361  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5423      0.5385     0.0285  5
  max valid BA                0.5577      0.5577     0.0360  5
  best valid F1               0.5130      0.4643     0.1212  5
  test BA                     0.4520      0.4400     0.0303  5
  test F1                     0.2001      0.2162     0.1249  5
  test sensitivity            0.1520      0.1600     0.0996  5
  test specificity            0.7520      0.6800     0.1453  5
  test precision              0.3738      0.3667     0.0482  4
  test loss                   0.7228      0.7227     0.0298  5
  FPR (FP/(FP+TN))            0.2480      0.3200     0.1453  5
  FNR (FN/(FN+TP))            0.8480      0.8400     0.0996  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6480      0.6547     0.0246  5
  max valid BA                0.6938      0.6950     0.0454  5
  best valid F1               0.5985      0.6038     0.0519  5
  test BA                     0.6046      0.6212     0.0537  5
  test F1                     0.4515      0.4615     0.0944  5
  test sensitivity            0.4348      0.3913     0.1340  5
  test specificity            0.7745      0.7447     0.0613  5
  test precision              0.4837      0.4800     0.0668  5
  test loss                   0.6402      0.6381     0.0312  5
  FPR (FP/(FP+TN))            0.2255      0.2553     0.0613  5
  FNR (FN/(FN+TP))            0.5652      0.6087     0.1340  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5761      0.5718     0.0496  5
  max valid BA                0.6765      0.6751     0.0524  5
  best valid F1               0.5734      0.5714     0.0677  5
  test BA                     0.5919      0.6092     0.0844  5
  test F1                     0.3130      0.3871     0.2364  5
  test sensitivity            0.2348      0.2609     0.2030  5
  test specificity            0.9489      0.9574     0.0356  5
  test precision              0.5645      0.7000     0.3170  5
  test loss                   0.6527      0.5964     0.1241  5
  FPR (FP/(FP+TN))            0.0511      0.0426     0.0356  5
  FNR (FN/(FN+TP))            0.7652      0.7391     0.2030  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5147      0.5113     0.0158  5
  max valid BA                0.5158      0.5113     0.0169  5
  best valid F1               0.4780      0.4892     0.0936  5
  test BA                     0.5006      0.4978     0.0485  5
  test F1                     0.3208      0.3840     0.2453  5
  test sensitivity            0.3631      0.3692     0.3173  5
  test specificity            0.6382      0.5955     0.2697  5
  test precision              0.3898      0.4103     0.1006  4
  test loss                   0.7010      0.7006     0.0127  5
  FPR (FP/(FP+TN))            0.3618      0.4045     0.2697  5
  FNR (FN/(FN+TP))            0.6369      0.6308     0.3173  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5069      0.5208     0.0337  5
  max valid BA                0.5250      0.5208     0.0382  5
  best valid F1               0.3182      0.2830     0.1072  5
  test BA                     0.5236      0.5417     0.0324  5
  test F1                     0.1978      0.1905     0.1585  5
  test sensitivity            0.1556      0.1111     0.1425  5
  test specificity            0.8917      0.9028     0.0984  5
  test precision              0.4341      0.4237     0.1823  4
  test loss                   0.6640      0.6666     0.0215  5
  FPR (FP/(FP+TN))            0.1083      0.0972     0.0984  5
  FNR (FN/(FN+TP))            0.8444      0.8889     0.1425  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5912      0.5735     0.0619  5
  max valid BA                0.6206      0.6029     0.0524  5
  best valid F1               0.5263      0.5143     0.0454  5
  test BA                     0.6147      0.6176     0.0434  5
  test F1                     0.4946      0.4848     0.0536  5
  test sensitivity            0.5176      0.4706     0.0767  5
  test specificity            0.7118      0.6765     0.0816  5
  test precision              0.4801      0.4583     0.0745  5
  test loss                   0.6681      0.6704     0.0246  5
  FPR (FP/(FP+TN))            0.2882      0.3235     0.0816  5
  FNR (FN/(FN+TP))            0.4824      0.5294     0.0767  5
```

## AUC vs chemistry null model, in-sample increment

