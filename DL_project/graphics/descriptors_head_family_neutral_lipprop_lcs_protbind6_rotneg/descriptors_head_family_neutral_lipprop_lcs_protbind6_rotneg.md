# descriptors_head_family_neutral_lipprop_lcs_protbind6_rotneg

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'descriptors_head_family_neutral_lipprop_lcs_protbind6_rotneg'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.9419      0.1760      0.8201      0.2891      0.8387      0.2989
groups_choline            5      0.6847      0.3663      0.5713      0.4637      0.6857      0.3683
groups_phosphorus_free    5      0.9419      0.0653      0.8747      0.1670      0.9267      0.1102
groups_sphingolipids      5      0.8424      0.2732      0.6701      0.3224      0.8727      0.2350
ALL                      20      0.8527      0.2202      0.7340      0.3105      0.8310      0.2531

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5370      0.5175     0.0502  20
max valid BA                0.5420      0.5233     0.0526  20
best valid F1               0.5624      0.5523     0.0458  20
test BA                     0.5365      0.5115     0.0550  20
test AUC                    0.5245      0.5087     0.1334  20
test AUC in-protein         0.5136      0.4966     0.1723  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5048      0.5184     0.1393  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.5318      0.5266     0.0868  20
test sensitivity            0.8527      0.9946     0.2525  20
test specificity            0.2202      0.0656     0.3114  20
test precision              0.4361      0.3900     0.1447  20
test loss                   1.1050      1.1749     0.3242  20
FPR (FP/(FP+TN))            0.7798      0.9344     0.3114  20
FNR (FN/(FN+TP))            0.1473      0.0054     0.2525  20

=== abs(sensitivity-specificity) gap: mean=0.7926 median=0.9290 n=20 ===
sensitivity std across seeds (by group): mean=0.2139 median=0.2116 n=4
specificity std across seeds (by group): mean=0.2825 median=0.3052 n=4

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5520      0.5345     0.0528  5
  max valid BA                0.5688      0.5620     0.0577  5
  best valid F1               0.5358      0.5225     0.0285  5
  test BA                     0.5589      0.5383     0.0668  5
  test AUC                    0.5967      0.6731     0.1457  5
  test AUC in-protein         0.5222      0.5156     0.0565  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.5142      0.5178     0.0541  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.5326      0.5239     0.0346  5
  test sensitivity            0.9419      0.9892     0.0876  5
  test specificity            0.1760      0.0765     0.2200  5
  test precision              0.3762      0.3550     0.0546  5
  test loss                   1.1809      1.2260     0.2598  5
  FPR (FP/(FP+TN))            0.8240      0.9235     0.2200  5
  FNR (FN/(FN+TP))            0.0581      0.0108     0.0876  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5260      0.5108     0.0299  5
  max valid BA                0.5270      0.5108     0.0289  5
  best valid F1               0.5248      0.5271     0.0073  5
  test BA                     0.5255      0.5346     0.0243  5
  test AUC                    0.5655      0.5111     0.0882  5
  test AUC in-protein         0.5092      0.4570     0.1703  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.5077      0.4405     0.1326  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.4558      0.5060     0.0942  5
  test sensitivity            0.6847      0.7568     0.3458  5
  test specificity            0.3663      0.3218     0.3904  5
  test precision              0.4010      0.3801     0.0696  5
  test loss                   1.0755      0.7941     0.5123  5
  FPR (FP/(FP+TN))            0.6337      0.6782     0.3904  5
  FNR (FN/(FN+TP))            0.3153      0.2432     0.3458  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5160      0.5102     0.0193  5
  max valid BA                0.5184      0.5160     0.0198  5
  best valid F1               0.5577      0.5556     0.0079  5
  test BA                     0.5036      0.5000     0.0075  5
  test AUC                    0.4009      0.4164     0.0602  5
  test AUC in-protein         0.5089      0.4000     0.3238  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.4235      0.4091     0.1929  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.5501      0.5586     0.0172  5
  test sensitivity            0.9419      1.0000     0.0866  5
  test specificity            0.0653      0.0204     0.0834  5
  test precision              0.3893      0.3875     0.0040  5
  test loss                   1.0949      1.1148     0.2371  5
  FPR (FP/(FP+TN))            0.9347      0.9796     0.0834  5
  FNR (FN/(FN+TP))            0.0581      0.0000     0.0866  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5539      0.5000     0.0809  5
  max valid BA                0.5539      0.5000     0.0809  5
  best valid F1               0.6314      0.6226     0.0197  5
  test BA                     0.5578      0.5000     0.0808  5
  test AUC                    0.5351      0.5432     0.1550  5
  test AUC in-protein         0.5140      0.4836     0.0622  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.5739      0.6313     0.1418  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5888      0.6168     0.1171  5
  test sensitivity            0.8424      1.0000     0.3357  5
  test specificity            0.2732      0.0000     0.4361  5
  test precision              0.5779      0.4459     0.2404  5
  test loss                   1.0687      1.2730     0.3208  5
  FPR (FP/(FP+TN))            0.7268      1.0000     0.4361  5
  FNR (FN/(FN+TP))            0.1576      0.0000     0.3357  5
```

## AUC vs chemistry null model, in-sample increment

