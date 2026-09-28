# deepclip_gltp_protein_gate_subclass_sugar_phospho_ep120

## Summary (analysis/summarize_label.py)

```
Summary: 'deepclip_gltp_protein_gate_subclass_sugar_phospho_ep120'
rows: 11

=== Sensitivity / specificity by group (test / train / valid) ===
group                                      n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CerP+Hex2Cer+SHexCer_groups_gltp   11      0.6364      0.5909      0.5417      0.6686      0.6883      0.7273
ALL                                       11      0.6364      0.5909      0.5417      0.6686      0.6883      0.7273

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6407      0.6310     0.1260  11
max valid BA                0.7078      0.7143     0.1307  11
best valid F1               0.7537      0.7778     0.1107  11
test BA                     0.6136      0.5833     0.1637  11
test AUC                    0.5108      0.5000     0.2503  11
test AUC in-protein         0.3636      0.5000     0.3931  11
  (proteins averaged)       1.3636      1.0000     0.5045  11
test AUC in-protein (pairs)      0.4394      0.4444     0.2806  11
  (proteins contributing)      1.9091      2.0000     0.3015  11
test F1                     0.5645      0.7000     0.3123  11
test sensitivity            0.6364      0.8571     0.4158  11
test specificity            0.5909      0.5000     0.3445  11
test precision              0.6691      0.6515     0.1962  10
test loss                   0.6951      0.6928     0.0068  11
FPR (FP/(FP+TN))            0.4091      0.5000     0.3445  11
FNR (FN/(FN+TP))            0.3636      0.1429     0.4158  11

=== abs(sensitivity-specificity) gap: mean=0.5649 median=0.6667 n=11 ===
sensitivity std across seeds (by group): mean=0.4158 median=0.4158 n=1
specificity std across seeds (by group): mean=0.3445 median=0.3445 n=1

=== By group ===
groups_CerP+Hex2Cer+SHexCer_groups_gltp (n=11):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6407      0.6310     0.1260  11
  max valid BA                0.7078      0.7143     0.1307  11
  best valid F1               0.7537      0.7778     0.1107  11
  test BA                     0.6136      0.5833     0.1637  11
  test AUC                    0.5108      0.5000     0.2503  11
  test AUC in-protein         0.3636      0.5000     0.3931  11
    (proteins averaged)       1.3636      1.0000     0.5045  11
  test AUC in-protein (pairs)      0.4394      0.4444     0.2806  11
    (proteins contributing)      1.9091      2.0000     0.3015  11
  test F1                     0.5645      0.7000     0.3123  11
  test sensitivity            0.6364      0.8571     0.4158  11
  test specificity            0.5909      0.5000     0.3445  11
  test precision              0.6691      0.6515     0.1962  10
  test loss                   0.6951      0.6928     0.0068  11
  FPR (FP/(FP+TN))            0.4091      0.5000     0.3445  11
  FNR (FN/(FN+TP))            0.3636      0.1429     0.4158  11
```

## AUC vs chemistry null model, in-sample increment

Failed: CerP+Hex2Cer+SHexCer_groups_gltp/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label deepclip_gltp_protein_gate_subclass_sugar_phospho_ep120 --seeds=0,1,2,3,4,5,6,7,8,9`
