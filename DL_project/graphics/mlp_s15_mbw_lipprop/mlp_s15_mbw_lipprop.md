# mlp_s15_mbw_lipprop

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'mlp_s15_mbw_lipprop'
rows: 5

=== Sensitivity / specificity by group (test / train / valid) ===
group               n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_species15    5      0.8020      0.7905      0.7939      0.7653      0.8760      0.8091
ALL                 5      0.8020      0.7905      0.7939      0.7653      0.8760      0.8091

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8325      0.8385     0.0507  5
max valid BA                0.8425      0.8405     0.0419  5
best valid F1               0.6494      0.6613     0.0568  5
test BA                     0.7963      0.8068     0.0563  5
test AUC                    0.8618      0.8446     0.0468  5
test AUC in-protein         0.8441      0.8288     0.0498  5
  (proteins averaged)      15.6000     15.0000     2.4083  5
test AUC in-protein (pairs)      0.8446      0.8277     0.0420  5
  (proteins contributing)     19.6000     19.0000     2.4083  5
test F1                     0.5947      0.6080     0.0814  5
test sensitivity            0.8020      0.8125     0.0818  5
test specificity            0.7905      0.8128     0.0714  5
test precision              0.4759      0.4875     0.0837  5
test loss                   0.4480      0.4539     0.0653  5
FPR (FP/(FP+TN))            0.2095      0.1872     0.0714  5
FNR (FN/(FN+TP))            0.1980      0.1875     0.0818  5

=== abs(sensitivity-specificity) gap: mean=0.0710 median=0.0394 n=5 ===
sensitivity std across seeds (by group): mean=0.0818 median=0.0818 n=1
specificity std across seeds (by group): mean=0.0714 median=0.0714 n=1

=== By group ===
groups_species15 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8325      0.8385     0.0507  5
  max valid BA                0.8425      0.8405     0.0419  5
  best valid F1               0.6494      0.6613     0.0568  5
  test BA                     0.7963      0.8068     0.0563  5
  test AUC                    0.8618      0.8446     0.0468  5
  test AUC in-protein         0.8441      0.8288     0.0498  5
    (proteins averaged)      15.6000     15.0000     2.4083  5
  test AUC in-protein (pairs)      0.8446      0.8277     0.0420  5
    (proteins contributing)     19.6000     19.0000     2.4083  5
  test F1                     0.5947      0.6080     0.0814  5
  test sensitivity            0.8020      0.8125     0.0818  5
  test specificity            0.7905      0.8128     0.0714  5
  test precision              0.4759      0.4875     0.0837  5
  test loss                   0.4480      0.4539     0.0653  5
  FPR (FP/(FP+TN))            0.2095      0.1872     0.0714  5
  FNR (FN/(FN+TP))            0.1980      0.1875     0.0818  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_s15_mbw_lipprop --seeds=0,1,2,3,4`
