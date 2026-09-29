# deepclip_start_protein_gate_ep120

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'deepclip_start_protein_gate_ep120'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group           n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_start    5      0.7231      0.8075      0.5801      0.7208      0.6820      0.7659
ALL             5      0.7231      0.8075      0.5801      0.7208      0.6820      0.7659

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6982      0.7042     0.0612  5
max valid BA                0.7239      0.7042     0.0422  5
best valid F1               0.6323      0.6207     0.0791  5
test BA                     0.7653      0.7727     0.0418  5
test AUC                    0.8543      0.8775     0.0665  5
test AUC in-protein         0.8674      0.8750     0.0444  5
  (proteins averaged)       2.0000      2.0000     0.0000  5
test AUC in-protein (pairs)      0.8348      0.8131     0.0631  5
  (proteins contributing)      3.0000      3.0000     0.0000  5
test F1                     0.6971      0.6957     0.0497  5
test sensitivity            0.7231      0.7273     0.1347  5
test specificity            0.8075      0.7826     0.1177  5
test precision              0.7097      0.6667     0.1650  5
test loss                   0.4777      0.4913     0.0650  5
FPR (FP/(FP+TN))            0.1925      0.2174     0.1177  5
FNR (FN/(FN+TP))            0.2769      0.2727     0.1347  5

=== abs(sensitivity-specificity) gap: mean=0.1679 median=0.0988 n=5 ===
sensitivity std across seeds (by group): mean=0.1347 median=0.1347 n=1
specificity std across seeds (by group): mean=0.1177 median=0.1177 n=1

=== By group ===
groups_start (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6982      0.7042     0.0612  5
  max valid BA                0.7239      0.7042     0.0422  5
  best valid F1               0.6323      0.6207     0.0791  5
  test BA                     0.7653      0.7727     0.0418  5
  test AUC                    0.8543      0.8775     0.0665  5
  test AUC in-protein         0.8674      0.8750     0.0444  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.8348      0.8131     0.0631  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.6971      0.6957     0.0497  5
  test sensitivity            0.7231      0.7273     0.1347  5
  test specificity            0.8075      0.7826     0.1177  5
  test precision              0.7097      0.6667     0.1650  5
  test loss                   0.4777      0.4913     0.0650  5
  FPR (FP/(FP+TN))            0.1925      0.2174     0.1177  5
  FNR (FN/(FN+TP))            0.2769      0.2727     0.1347  5
```

## AUC vs chemistry null model, in-sample increment

Failed: start/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label deepclip_start_protein_gate_ep120 --seeds=0,1,2,3,4`
