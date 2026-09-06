# thematical_paths_geom_chem_single_norm

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'thematical_paths_geom_chem_single_norm'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.4627      0.5410      0.6217      0.5369      0.4716      0.5387
groups_GLTP            5      0.6000      0.4000      0.6385      0.3665      0.6000      0.4000
groups_IP_trans        5      0.6000      0.3745      0.6711      0.3355      0.6250      0.3830
groups_LBP_BPI_CETP    5      0.6000      0.4000      0.6330      0.3696      0.6000      0.4000
groups_START           5      0.6062      0.3933      0.6594      0.3321      0.6125      0.3955
groups_lipocalin       5      0.6000      0.4000      0.6587      0.3352      0.6056      0.4000
groups_scp2            5      0.6000      0.4000      0.6366      0.3692      0.6000      0.4000
ALL                   35      0.5813      0.4155      0.6456      0.3779      0.5878      0.4167

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5023      0.5000     0.0066  35
max valid BA                0.5031      0.5000     0.0103  35
best valid F1               0.4515      0.5053     0.2393  35
test BA                     0.4984      0.5000     0.0109  35
test F1                     0.3308      0.4946     0.2783  35
test sensitivity            0.5813      1.0000     0.4933  35
test specificity            0.4155      0.0000     0.4895  35
test precision              0.3793      0.3333     0.1145  23
test loss                   0.7450      0.7143     0.1278  35
FPR (FP/(FP+TN))            0.5845      1.0000     0.4895  35
FNR (FN/(FN+TP))            0.4187      0.0000     0.4933  35

=== abs(sensitivity-specificity) gap: mean=0.9771 median=1.0000 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5052      0.5000     0.0116  5
  max valid BA                0.5109      0.5000     0.0244  5
  best valid F1               0.5469      0.6837     0.3057  5
  test BA                     0.5018      0.5000     0.0041  5
  test F1                     0.3541      0.3962     0.3444  5
  test sensitivity            0.4627      0.3134     0.5069  5
  test specificity            0.5410      0.7049     0.5083  5
  test precision              0.5284      0.5234     0.0087  3
  test loss                   0.8465      0.7055     0.3230  5
  FPR (FP/(FP+TN))            0.4590      0.2951     0.5083  5
  FNR (FN/(FN+TP))            0.5373      0.6866     0.5069  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0000  5
  max valid BA                0.5000      0.5000     0.0000  5
  best valid F1               0.5333      0.6667     0.2981  5
  test BA                     0.5000      0.5000     0.0000  5
  test F1                     0.4000      0.6667     0.3651  5
  test sensitivity            0.6000      1.0000     0.5477  5
  test specificity            0.4000      0.0000     0.5477  5
  test precision              0.5000      0.5000     0.0000  3
  test loss                   0.7064      0.7049     0.0112  5
  FPR (FP/(FP+TN))            0.6000      1.0000     0.5477  5
  FNR (FN/(FN+TP))            0.4000      0.0000     0.5477  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5040      0.5000     0.0089  5
  max valid BA                0.5040      0.5000     0.0089  5
  best valid F1               0.4042      0.5053     0.2260  5
  test BA                     0.4872      0.5000     0.0285  5
  test F1                     0.2968      0.4946     0.2709  5
  test sensitivity            0.6000      1.0000     0.5477  5
  test specificity            0.3745      0.0000     0.5147  5
  test precision              0.2464      0.3286     0.1643  4
  test loss                   0.7362      0.7388     0.0661  5
  FPR (FP/(FP+TN))            0.6255      1.0000     0.5147  5
  FNR (FN/(FN+TP))            0.4000      0.0000     0.5477  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0000  5
  max valid BA                0.5000      0.5000     0.0000  5
  best valid F1               0.4042      0.5053     0.2260  5
  test BA                     0.5000      0.5000     0.0000  5
  test F1                     0.2968      0.4946     0.2709  5
  test sensitivity            0.6000      1.0000     0.5477  5
  test specificity            0.4000      0.0000     0.5477  5
  test precision              0.3286      0.3286     0.0000  3
  test loss                   0.7350      0.7386     0.0672  5
  FPR (FP/(FP+TN))            0.6000      1.0000     0.5477  5
  FNR (FN/(FN+TP))            0.4000      0.0000     0.5477  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5040      0.5000     0.0090  5
  max valid BA                0.5040      0.5000     0.0090  5
  best valid F1               0.4719      0.5899     0.2638  5
  test BA                     0.4997      0.5000     0.0007  5
  test F1                     0.3676      0.5936     0.3101  5
  test sensitivity            0.6062      1.0000     0.5394  5
  test specificity            0.3933      0.0000     0.5386  5
  test precision              0.4166      0.4221     0.0110  4
  test loss                   0.7215      0.7182     0.0361  5
  FPR (FP/(FP+TN))            0.6067      1.0000     0.5386  5
  FNR (FN/(FN+TP))            0.3938      0.0000     0.5394  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5028      0.5000     0.0062  5
  max valid BA                0.5028      0.5000     0.0062  5
  best valid F1               0.4000      0.5000     0.2236  5
  test BA                     0.5000      0.5000     0.0000  5
  test F1                     0.3000      0.5000     0.2739  5
  test sensitivity            0.6000      1.0000     0.5477  5
  test specificity            0.4000      0.0000     0.5477  5
  test precision              0.3333      0.3333     0.0000  3
  test loss                   0.7360      0.7384     0.0654  5
  FPR (FP/(FP+TN))            0.6000      1.0000     0.5477  5
  FNR (FN/(FN+TP))            0.4000      0.0000     0.5477  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0000  5
  max valid BA                0.5000      0.5000     0.0000  5
  best valid F1               0.4000      0.5000     0.2236  5
  test BA                     0.5000      0.5000     0.0000  5
  test F1                     0.3000      0.5000     0.2739  5
  test sensitivity            0.6000      1.0000     0.5477  5
  test specificity            0.4000      0.0000     0.5477  5
  test precision              0.3333      0.3333     0.0000  3
  test loss                   0.7330      0.7364     0.0638  5
  FPR (FP/(FP+TN))            0.6000      1.0000     0.5477  5
  FNR (FN/(FN+TP))            0.4000      0.0000     0.5477  5
```

## AUC vs chemistry null model, in-sample increment

(skipped: SKIP_AUC=1 -- rerun without it to fill this in: `python3 analysis/full_label_report.py --label thematical_paths_geom_chem_single_norm --seeds=0,1,2,3,4`)
