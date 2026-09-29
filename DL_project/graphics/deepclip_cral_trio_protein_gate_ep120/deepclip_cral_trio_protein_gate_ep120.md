# deepclip_cral_trio_protein_gate_ep120

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'deepclip_cral_trio_protein_gate_ep120'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_cral-trio    5      0.8252      0.6361      0.8279      0.6519      0.9051      0.7622
ALL                 5      0.8252      0.6361      0.8279      0.6519      0.9051      0.7622

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8265      0.8397     0.0480  5
max valid BA                0.8337      0.8397     0.0409  5
best valid F1               0.7704      0.7857     0.0383  5
test BA                     0.7306      0.7291     0.0441  5
test AUC                    0.7800      0.7860     0.0172  5
test AUC in-protein         0.8835      0.9028     0.0296  5
  (proteins averaged)       2.0000      2.0000     0.0000  5
test AUC in-protein (pairs)      0.8618      0.8621     0.0216  5
  (proteins contributing)      4.0000      4.0000     0.7071  5
test F1                     0.6549      0.6286     0.0476  5
test sensitivity            0.8252      0.8462     0.0335  5
test specificity            0.6361      0.6400     0.0753  5
test precision              0.5447      0.5263     0.0609  5
test loss                   0.5872      0.5662     0.0687  5
FPR (FP/(FP+TN))            0.3639      0.3600     0.0753  5
FNR (FN/(FN+TP))            0.1748      0.1538     0.0335  5

=== abs(sensitivity-specificity) gap: mean=0.1891 median=0.1782 n=5 ===
sensitivity std across seeds (by group): mean=0.0335 median=0.0335 n=1
specificity std across seeds (by group): mean=0.0753 median=0.0753 n=1

=== By group ===
groups_cral-trio (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8265      0.8397     0.0480  5
  max valid BA                0.8337      0.8397     0.0409  5
  best valid F1               0.7704      0.7857     0.0383  5
  test BA                     0.7306      0.7291     0.0441  5
  test AUC                    0.7800      0.7860     0.0172  5
  test AUC in-protein         0.8835      0.9028     0.0296  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.8618      0.8621     0.0216  5
    (proteins contributing)      4.0000      4.0000     0.7071  5
  test F1                     0.6549      0.6286     0.0476  5
  test sensitivity            0.8252      0.8462     0.0335  5
  test specificity            0.6361      0.6400     0.0753  5
  test precision              0.5447      0.5263     0.0609  5
  test loss                   0.5872      0.5662     0.0687  5
  FPR (FP/(FP+TN))            0.3639      0.3600     0.0753  5
  FNR (FN/(FN+TP))            0.1748      0.1538     0.0335  5
```

## AUC vs chemistry null model, in-sample increment

Failed: cral-trio/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label deepclip_cral_trio_protein_gate_ep120 --seeds=0,1,2,3,4`
