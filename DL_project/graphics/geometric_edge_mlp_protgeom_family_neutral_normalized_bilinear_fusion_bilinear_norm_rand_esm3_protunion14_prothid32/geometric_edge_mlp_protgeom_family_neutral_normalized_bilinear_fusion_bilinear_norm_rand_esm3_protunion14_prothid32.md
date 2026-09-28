# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rand_esm3_protunion14_prothid32

## Summary (analysis/summarize_label.py)

```
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rand_esm3_protunion14_prothid32'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
random    5      0.8550      0.7887      0.8795      0.7908      0.8421      0.8243
ALL       5      0.8550      0.7887      0.8795      0.7908      0.8421      0.8243

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8088      0.8675     0.1388  5
max valid BA                0.8332      0.8746     0.1196  5
best valid F1               0.7542      0.8039     0.1408  5
test BA                     0.8218      0.8637     0.1039  5
test AUC                    0.8648      0.9108     0.1289  5
test AUC in-protein         0.8237      0.8950     0.1621  5
  (proteins averaged)       9.2000      9.0000     1.7889  5
test AUC in-protein (pairs)      0.8582      0.8810     0.0932  5
  (proteins contributing)     16.2000     16.0000     1.3038  5
test F1                     0.7417      0.7925     0.1223  5
test sensitivity            0.8550      0.9111     0.1330  5
test specificity            0.7887      0.8200     0.0762  5
test precision              0.6555      0.7000     0.1144  5
test loss                   0.4169      0.3703     0.1439  5
FPR (FP/(FP+TN))            0.2113      0.1800     0.0762  5
FNR (FN/(FN+TP))            0.1450      0.0889     0.1330  5

=== abs(sensitivity-specificity) gap: mean=0.0786 median=0.0761 n=5 ===
sensitivity std across seeds (by group): mean=0.1330 median=0.1330 n=1
specificity std across seeds (by group): mean=0.0762 median=0.0762 n=1

=== By group ===
random (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8088      0.8675     0.1388  5
  max valid BA                0.8332      0.8746     0.1196  5
  best valid F1               0.7542      0.8039     0.1408  5
  test BA                     0.8218      0.8637     0.1039  5
  test AUC                    0.8648      0.9108     0.1289  5
  test AUC in-protein         0.8237      0.8950     0.1621  5
    (proteins averaged)       9.2000      9.0000     1.7889  5
  test AUC in-protein (pairs)      0.8582      0.8810     0.0932  5
    (proteins contributing)     16.2000     16.0000     1.3038  5
  test F1                     0.7417      0.7925     0.1223  5
  test sensitivity            0.8550      0.9111     0.1330  5
  test specificity            0.7887      0.8200     0.0762  5
  test precision              0.6555      0.7000     0.1144  5
  test loss                   0.4169      0.3703     0.1439  5
  FPR (FP/(FP+TN))            0.2113      0.1800     0.0762  5
  FNR (FN/(FN+TP))            0.1450      0.0889     0.1330  5
```

## AUC vs chemistry null model, in-sample increment

(skipped: SKIP_AUC=1 -- rerun without it to fill this in: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_rand_esm3_protunion14_prothid32 --seeds=0,1,2,3,4`)
