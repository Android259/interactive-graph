# descriptors_no_extent_coarse_add_lipprop_family_neutral

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_no_extent_coarse_add_lipprop_family_neutral'
rows: 8

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_LBP_BPI_CETP    3      0.4638      0.7376      0.8325      0.7809      0.5972      0.7305
groups_START           5      0.7138      0.2989      0.7365      0.6532      0.7406      0.3573
ALL                    8      0.6201      0.4634      0.7725      0.7011      0.6868      0.4973

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5920      0.5492     0.0861  8
max valid BA                0.6472      0.6120     0.0955  8
best valid F1               0.6307      0.6200     0.0672  8
test BA                     0.5417      0.5344     0.0710  8
test F1                     0.5089      0.5119     0.0569  8
test sensitivity            0.6201      0.5923     0.1571  8
test specificity            0.4634      0.4157     0.2625  8
test precision              0.4523      0.4465     0.0805  8
test loss                   0.8808      0.8432     0.2068  8
FPR (FP/(FP+TN))            0.5366      0.5843     0.2625  8
FNR (FN/(FN+TP))            0.3799      0.4077     0.1571  8

=== abs(sensitivity-specificity) gap: mean=0.3620 median=0.3837 n=8 ===

=== By group ===
groups_LBP_BPI_CETP (n=3):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6639      0.7247     0.1081  3
  max valid BA                0.7368      0.7691     0.1044  3
  best valid F1               0.6739      0.6939     0.0976  3
  test BA                     0.6007      0.6323     0.0744  3
  test F1                     0.4705      0.4878     0.0637  3
  test sensitivity            0.4638      0.4783     0.0251  3
  test specificity            0.7376      0.8298     0.1597  3
  test precision              0.4928      0.5556     0.1296  3
  test loss                   0.9598      1.0289     0.3259  3
  FPR (FP/(FP+TN))            0.2624      0.1702     0.1597  3
  FNR (FN/(FN+TP))            0.5362      0.5217     0.0251  3

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5490      0.5320     0.0306  5
  max valid BA                0.5935      0.5839     0.0298  5
  best valid F1               0.6048      0.6186     0.0299  5
  test BA                     0.5064      0.5334     0.0434  5
  test F1                     0.5319      0.5368     0.0433  5
  test sensitivity            0.7138      0.7692     0.1165  5
  test specificity            0.2989      0.2584     0.1326  5
  test precision              0.4280      0.4426     0.0312  5
  test loss                   0.8333      0.8325     0.1194  5
  FPR (FP/(FP+TN))            0.7011      0.7416     0.1326  5
  FNR (FN/(FN+TP))            0.2862      0.2308     0.1165  5
```

## AUC vs chemistry null model, in-sample increment

### features = tanimoto (full molecular structure)

Failed: CRAL-TRIO/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label descriptors_no_extent_coarse_add_lipprop_family_neutral --seeds=0,1,2,3,4 --features=tanimoto --features-label=tanimoto`
