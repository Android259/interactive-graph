# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_headchain

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_headchain'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6409      0.3574      0.6643      0.5558      0.6645      0.4022
groups_choline            5      0.6775      0.4564      0.4813      0.5849      0.6696      0.5604
groups_phosphorus_free    5      0.1355      0.8000      0.6129      0.5310      0.4067      0.7429
groups_sphingolipids      5      0.4000      0.5610      0.5320      0.6009      0.4667      0.6800
ALL                      20      0.4635      0.5437      0.5726      0.5682      0.5519      0.5964

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5443      0.5337     0.0421  20
max valid BA                0.5741      0.5612     0.0483  20
best valid F1               0.5633      0.5505     0.0458  20
test BA                     0.5036      0.4943     0.0520  20
test AUC                    0.5152      0.4975     0.0705  20
test AUC in-protein         0.6155      0.5740     0.1407  20
  (proteins averaged)       6.6000      6.5000     4.8818  20
test AUC in-protein (pairs)      0.5365      0.5601     0.1247  20
  (proteins contributing)      9.6000     11.0000     5.4618  20
test F1                     0.3529      0.3905     0.1888  20
test sensitivity            0.4635      0.3636     0.3341  20
test specificity            0.5437      0.6066     0.3063  20
test precision              0.3440      0.3546     0.1082  19
test loss                   0.6953      0.6939     0.0129  20
FPR (FP/(FP+TN))            0.4563      0.3934     0.3063  20
FNR (FN/(FN+TP))            0.5365      0.6364     0.3341  20

=== abs(sensitivity-specificity) gap: mean=0.5285 median=0.4548 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5166      0.5167     0.0179  5
  max valid BA                0.5334      0.5368     0.0128  5
  best valid F1               0.5107      0.5098     0.0050  5
  test BA                     0.4991      0.4898     0.0168  5
  test AUC                    0.5011      0.5019     0.0163  5
  test AUC in-protein         0.4932      0.5089     0.0400  5
    (proteins averaged)      11.6000     11.0000     0.8944  5
  test AUC in-protein (pairs)      0.4877      0.4899     0.0509  5
    (proteins contributing)     14.6000     15.0000     1.8166  5
  test F1                     0.4294      0.4630     0.0645  5
  test sensitivity            0.6409      0.7204     0.2359  5
  test specificity            0.3574      0.3060     0.2432  5
  test precision              0.3367      0.3320     0.0160  5
  test loss                   0.7035      0.7066     0.0174  5
  FPR (FP/(FP+TN))            0.6426      0.6940     0.2432  5
  FNR (FN/(FN+TP))            0.3591      0.2796     0.2359  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5689      0.5676     0.0489  5
  max valid BA                0.6150      0.6096     0.0429  5
  best valid F1               0.5552      0.5429     0.0256  5
  test BA                     0.5670      0.5712     0.0631  5
  test AUC                    0.6170      0.6256     0.0281  5
  test AUC in-protein         0.6650      0.6940     0.0523  5
    (proteins averaged)      11.0000     11.0000     1.0000  5
  test AUC in-protein (pairs)      0.6322      0.6522     0.0595  5
    (proteins contributing)     14.0000     13.0000     1.4142  5
  test F1                     0.4898      0.5236     0.1164  5
  test sensitivity            0.6775      0.7117     0.2836  5
  test specificity            0.4564      0.4505     0.2915  5
  test precision              0.4111      0.4072     0.0530  5
  test loss                   0.6903      0.6925     0.0094  5
  FPR (FP/(FP+TN))            0.5436      0.5495     0.2915  5
  FNR (FN/(FN+TP))            0.3225      0.2883     0.2836  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5488      0.5167     0.0540  5
  max valid BA                0.5748      0.5878     0.0527  5
  best valid F1               0.5625      0.5505     0.0292  5
  test BA                     0.4677      0.4651     0.0302  5
  test AUC                    0.4645      0.4694     0.0277  5
  test AUC in-protein         0.7867      0.8000     0.1366  5
    (proteins averaged)       1.8000      2.0000     0.8367  5
  test AUC in-protein (pairs)      0.5556      0.5938     0.1387  5
    (proteins contributing)      7.8000      9.0000     2.1679  5
  test F1                     0.1386      0.0541     0.1666  5
  test sensitivity            0.1355      0.0323     0.1728  5
  test specificity            0.8000      0.8980     0.2270  5
  test precision              0.2014      0.2361     0.1528  4
  test loss                   0.6867      0.6847     0.0093  5
  FPR (FP/(FP+TN))            0.2000      0.1020     0.2270  5
  FNR (FN/(FN+TP))            0.8645      0.9677     0.1728  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5428      0.5356     0.0326  5
  max valid BA                0.5733      0.5629     0.0460  5
  best valid F1               0.6249      0.6226     0.0126  5
  test BA                     0.4805      0.4815     0.0193  5
  test AUC                    0.4783      0.4486     0.0606  5
  test AUC in-protein         0.5170      0.5020     0.0234  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4707      0.4927     0.1678  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3539      0.3810     0.1886  5
  test sensitivity            0.4000      0.3636     0.3582  5
  test specificity            0.5610      0.6341     0.3384  5
  test precision              0.3984      0.4000     0.0488  5
  test loss                   0.7005      0.6951     0.0085  5
  FPR (FP/(FP+TN))            0.4390      0.3659     0.3384  5
  FNR (FN/(FN+TP))            0.6000      0.6364     0.3582  5
```

## AUC vs chemistry null model, in-sample increment

Failed: sphingolipids/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_balanced_lipid_classes_advprot_headchain --seeds=0,1,2,3,4`
