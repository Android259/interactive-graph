# deepclip_start_protein_gate_positional_ep120

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'deepclip_start_protein_gate_positional_ep120'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group           n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_start    5      0.7441      0.7536      0.6695      0.6027      0.7183      0.6955
ALL             5      0.7441      0.7536      0.6695      0.6027      0.7183      0.6955

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6978      0.7042     0.0647  5
max valid BA                0.7069      0.7042     0.0583  5
best valid F1               0.6201      0.6154     0.0855  5
test BA                     0.7488      0.7747     0.0771  5
test AUC                    0.8297      0.8775     0.0909  5
test AUC in-protein         0.8679      0.8750     0.0518  5
  (proteins averaged)       2.0000      2.0000     0.0000  5
test AUC in-protein (pairs)      0.8297      0.8131     0.0833  5
  (proteins contributing)      3.0000      3.0000     0.0000  5
test F1                     0.6770      0.6923     0.0806  5
test sensitivity            0.7441      0.7273     0.1284  5
test specificity            0.7536      0.7391     0.1074  5
test precision              0.6320      0.6154     0.1015  5
test loss                   0.5447      0.5252     0.1185  5
FPR (FP/(FP+TN))            0.2464      0.2609     0.1074  5
FNR (FN/(FN+TP))            0.2559      0.2727     0.1284  5

=== abs(sensitivity-specificity) gap: mean=0.1247 median=0.0791 n=5 ===
sensitivity std across seeds (by group): mean=0.1284 median=0.1284 n=1
specificity std across seeds (by group): mean=0.1074 median=0.1074 n=1

=== By group ===
groups_start (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6978      0.7042     0.0647  5
  max valid BA                0.7069      0.7042     0.0583  5
  best valid F1               0.6201      0.6154     0.0855  5
  test BA                     0.7488      0.7747     0.0771  5
  test AUC                    0.8297      0.8775     0.0909  5
  test AUC in-protein         0.8679      0.8750     0.0518  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.8297      0.8131     0.0833  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.6770      0.6923     0.0806  5
  test sensitivity            0.7441      0.7273     0.1284  5
  test specificity            0.7536      0.7391     0.1074  5
  test precision              0.6320      0.6154     0.1015  5
  test loss                   0.5447      0.5252     0.1185  5
  FPR (FP/(FP+TN))            0.2464      0.2609     0.1074  5
  FNR (FN/(FN+TP))            0.2559      0.2727     0.1284  5
```

## AUC vs chemistry null model, in-sample increment

Failed: start/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label deepclip_start_protein_gate_positional_ep120 --seeds=0,1,2,3,4`
