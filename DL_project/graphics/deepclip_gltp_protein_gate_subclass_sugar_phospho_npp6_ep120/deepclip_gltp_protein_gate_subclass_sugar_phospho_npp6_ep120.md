# deepclip_gltp_protein_gate_subclass_sugar_phospho_npp6_ep120

## Summary (analysis/summarize_label.py)

```
Summary: 'deepclip_gltp_protein_gate_subclass_sugar_phospho_npp6_ep120'
rows: 10

=== Sensitivity / specificity by group (test / train / valid) ===
group                                      n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CerP+Hex2Cer+SHexCer_groups_gltp   10      0.6714      0.6286      0.5167      0.6757      0.7000      0.7286
ALL                                       10      0.6714      0.6286      0.5167      0.6757      0.7000      0.7286

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6643      0.6786     0.1067  10
max valid BA                0.7143      0.7500     0.1260  10
best valid F1               0.7469      0.7418     0.1042  10
test BA                     0.6500      0.6071     0.1947  10
test AUC                    0.5735      0.5816     0.1982  10
test AUC in-protein         0.4000      0.5000     0.2108  10
  (proteins averaged)       1.8000      2.0000     0.4216  10
test AUC in-protein (pairs)      0.4928      0.5000     0.1989  10
  (proteins contributing)      2.0000      2.0000     0.0000  10
test F1                     0.5959      0.6275     0.3121  10
test sensitivity            0.6714      0.8571     0.3987  10
test specificity            0.6286      0.6429     0.3101  10
test precision              0.6613      0.7000     0.2287  9
test loss                   0.7153      0.6928     0.0725  10
FPR (FP/(FP+TN))            0.3714      0.3571     0.3101  10
FNR (FN/(FN+TP))            0.3286      0.1429     0.3987  10

=== abs(sensitivity-specificity) gap: mean=0.4714 median=0.4286 n=10 ===
sensitivity std across seeds (by group): mean=0.3987 median=0.3987 n=1
specificity std across seeds (by group): mean=0.3101 median=0.3101 n=1

=== By group ===
groups_CerP+Hex2Cer+SHexCer_groups_gltp (n=10):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6643      0.6786     0.1067  10
  max valid BA                0.7143      0.7500     0.1260  10
  best valid F1               0.7469      0.7418     0.1042  10
  test BA                     0.6500      0.6071     0.1947  10
  test AUC                    0.5735      0.5816     0.1982  10
  test AUC in-protein         0.4000      0.5000     0.2108  10
    (proteins averaged)       1.8000      2.0000     0.4216  10
  test AUC in-protein (pairs)      0.4928      0.5000     0.1989  10
    (proteins contributing)      2.0000      2.0000     0.0000  10
  test F1                     0.5959      0.6275     0.3121  10
  test sensitivity            0.6714      0.8571     0.3987  10
  test specificity            0.6286      0.6429     0.3101  10
  test precision              0.6613      0.7000     0.2287  9
  test loss                   0.7153      0.6928     0.0725  10
  FPR (FP/(FP+TN))            0.3714      0.3571     0.3101  10
  FNR (FN/(FN+TP))            0.3286      0.1429     0.3987  10
```

## AUC vs chemistry null model, in-sample increment

Failed: CerP+Hex2Cer+SHexCer_groups_gltp/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label deepclip_gltp_protein_gate_subclass_sugar_phospho_npp6_ep120 --seeds=0,1,2,3,4,5,6,7,8,9`
