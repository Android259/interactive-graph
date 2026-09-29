# deepclip_start_protein_gate_signed_ep120

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'deepclip_start_protein_gate_signed_ep120'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group           n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_start    5      0.8112      0.7371      0.7735      0.6523      0.7824      0.6488
ALL             5      0.8112      0.7371      0.7735      0.6523      0.7824      0.6488

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.7115      0.7250     0.0654  5
max valid BA                0.7156      0.7348     0.0671  5
best valid F1               0.6334      0.6667     0.0953  5
test BA                     0.7741      0.7787     0.0478  5
test AUC                    0.8391      0.8814     0.0723  5
test AUC in-protein         0.8700      0.8875     0.0677  5
  (proteins averaged)       2.0000      2.0000     0.0000  5
test AUC in-protein (pairs)      0.8296      0.8174     0.0918  5
  (proteins contributing)      3.0000      3.0000     0.0000  5
test F1                     0.7046      0.6923     0.0563  5
test sensitivity            0.8112      0.8182     0.0732  5
test specificity            0.7371      0.7391     0.0579  5
test precision              0.6237      0.6000     0.0527  5
test loss                   0.5057      0.5092     0.0732  5
FPR (FP/(FP+TN))            0.2629      0.2609     0.0579  5
FNR (FN/(FN+TP))            0.1888      0.1818     0.0732  5

=== abs(sensitivity-specificity) gap: mean=0.0820 median=0.0791 n=5 ===
sensitivity std across seeds (by group): mean=0.0732 median=0.0732 n=1
specificity std across seeds (by group): mean=0.0579 median=0.0579 n=1

=== By group ===
groups_start (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7115      0.7250     0.0654  5
  max valid BA                0.7156      0.7348     0.0671  5
  best valid F1               0.6334      0.6667     0.0953  5
  test BA                     0.7741      0.7787     0.0478  5
  test AUC                    0.8391      0.8814     0.0723  5
  test AUC in-protein         0.8700      0.8875     0.0677  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.8296      0.8174     0.0918  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.7046      0.6923     0.0563  5
  test sensitivity            0.8112      0.8182     0.0732  5
  test specificity            0.7371      0.7391     0.0579  5
  test precision              0.6237      0.6000     0.0527  5
  test loss                   0.5057      0.5092     0.0732  5
  FPR (FP/(FP+TN))            0.2629      0.2609     0.0579  5
  FNR (FN/(FN+TP))            0.1888      0.1818     0.0732  5
```

## AUC vs chemistry null model, in-sample increment

Failed: start/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label deepclip_start_protein_gate_signed_ep120 --seeds=0,1,2,3,4`
