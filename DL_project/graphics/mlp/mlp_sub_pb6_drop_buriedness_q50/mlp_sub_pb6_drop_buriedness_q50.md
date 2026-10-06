# mlp_sub_pb6_drop_buriedness_q50

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_drop_buriedness_q50'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.5879      0.4244      0.4405      0.6322      0.4727      0.5750
groups_FA                                    5      0.2417      0.8595      0.5689      0.7221      0.2083      0.9056
groups_LPC+LPE+LPG                           5      0.4625      0.6839      0.6399      0.6971      0.6875      0.6867
groups_PA                                    5      0.4769      0.9385      0.4931      0.7046      0.5846      0.8308
groups_PC                                    5      0.5725      0.5046      0.6096      0.4443      0.5927      0.5228
groups_PE                                    5      0.9100      0.5950      0.7671      0.5695      0.8900      0.6075
groups_PG                                    5      0.6070      0.8283      0.6798      0.6656      0.6429      0.7735
groups_PI                                    5      0.2250      0.6875      0.4269      0.6701      0.4250      0.7125
ALL                                         40      0.5104      0.6902      0.5782      0.6382      0.5630      0.7018

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6190      0.5936     0.1049  40
max valid BA                0.6324      0.6235     0.1045  40
best valid F1               0.5575      0.5714     0.1236  40
test BA                     0.6003      0.5768     0.1331  40
test AUC                    0.5972      0.5495     0.1944  40
test AUC in-protein         0.6019      0.5741     0.2292  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.5487      0.5436     0.2296  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.4469      0.5010     0.2433  40
test sensitivity            0.5104      0.5192     0.3355  40
test specificity            0.6902      0.8178     0.3317  40
test precision              0.5297      0.5577     0.2263  36
test loss                   0.6539      0.6759     0.0951  40
FPR (FP/(FP+TN))            0.3098      0.1822     0.3317  40
FNR (FN/(FN+TP))            0.4896      0.4808     0.3355  40

=== abs(sensitivity-specificity) gap: mean=0.5221 median=0.4303 n=40 ===
sensitivity std across seeds (by group): mean=0.2480 median=0.1993 n=8
specificity std across seeds (by group): mean=0.2719 median=0.2846 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5184      0.5000     0.0412  5
  max valid BA                0.5239      0.5000     0.0401  5
  best valid F1               0.5818      0.6226     0.0731  5
  test BA                     0.5061      0.5000     0.0137  5
  test AUC                    0.4135      0.4213     0.0369  5
  test AUC in-protein         0.3346      0.4042     0.1877  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.2733      0.3098     0.1455  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3707      0.6168     0.3384  5
  test sensitivity            0.5879      0.9394     0.5372  5
  test specificity            0.4244      0.1220     0.5278  5
  test precision              0.4515      0.4459     0.0097  3
  test loss                   0.7130      0.6957     0.0303  5
  FPR (FP/(FP+TN))            0.5756      0.8780     0.5278  5
  FNR (FN/(FN+TP))            0.4121      0.0606     0.5372  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5458      0.5486     0.0223  5
  max valid BA                0.5569      0.5486     0.0238  5
  best valid F1               0.4539      0.4935     0.1298  5
  test BA                     0.5506      0.5771     0.0936  5
  test AUC                    0.4354      0.3806     0.1410  5
  test AUC in-protein         0.7333      0.7333     0.0770  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.5649      0.5455     0.1125  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3332      0.3226     0.1023  5
  test sensitivity            0.2417      0.2500     0.0801  5
  test specificity            0.8595      0.9459     0.1943  5
  test precision              0.6303      0.7143     0.2382  5
  test loss                   0.7279      0.7058     0.0818  5
  FPR (FP/(FP+TN))            0.1405      0.0541     0.1943  5
  FNR (FN/(FN+TP))            0.7583      0.7500     0.0801  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6412      0.6542     0.0758  5
  max valid BA                0.6871      0.6854     0.0497  5
  best valid F1               0.5990      0.6000     0.0611  5
  test BA                     0.5732      0.6240     0.1269  5
  test AUC                    0.6679      0.7077     0.1606  5
  test AUC in-protein         0.8096      0.8067     0.0563  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.6584      0.7059     0.1576  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.4517      0.4348     0.1300  5
  test sensitivity            0.4625      0.5000     0.1569  5
  test specificity            0.6839      0.6774     0.2331  5
  test precision              0.4937      0.5238     0.2058  5
  test loss                   0.6355      0.6478     0.1039  5
  FPR (FP/(FP+TN))            0.3161      0.3226     0.2331  5
  FNR (FN/(FN+TP))            0.5375      0.5000     0.1569  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7077      0.7115     0.0370  5
  max valid BA                0.7077      0.7115     0.0370  5
  best valid F1               0.5991      0.6000     0.0629  5
  test BA                     0.7077      0.7500     0.1057  5
  test AUC                    0.6938      0.7811     0.2518  5
  test AUC in-protein         0.7542      0.7583     0.2417  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.7293      0.7000     0.1792  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.5804      0.6667     0.2067  5
  test sensitivity            0.4769      0.5385     0.1915  5
  test specificity            0.9385      0.9615     0.0344  5
  test precision              0.7639      0.8750     0.1751  5
  test loss                   0.5989      0.5762     0.0643  5
  FPR (FP/(FP+TN))            0.0615      0.0385     0.0344  5
  FNR (FN/(FN+TP))            0.5231      0.4615     0.1915  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5464      0.5419     0.0453  5
  max valid BA                0.5578      0.5419     0.0612  5
  best valid F1               0.4768      0.5253     0.1294  5
  test BA                     0.5385      0.5271     0.0435  5
  test AUC                    0.5098      0.5524     0.1037  5
  test AUC in-protein         0.4991      0.5166     0.2002  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4763      0.5431     0.1754  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3916      0.5020     0.2303  5
  test sensitivity            0.5725      0.5688     0.4181  5
  test specificity            0.5046      0.6142     0.3985  5
  test precision              0.3198      0.3958     0.1818  5
  test loss                   0.7125      0.6918     0.0619  5
  FPR (FP/(FP+TN))            0.4954      0.3858     0.3985  5
  FNR (FN/(FN+TP))            0.4275      0.4312     0.4181  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7425      0.7875     0.1390  5
  max valid BA                0.7488      0.8000     0.1423  5
  best valid F1               0.6896      0.7234     0.1120  5
  test BA                     0.7525      0.8187     0.1427  5
  test AUC                    0.8232      0.8941     0.1556  5
  test AUC in-protein         0.6978      0.7494     0.2412  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.6811      0.7013     0.2198  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.6916      0.7429     0.1095  5
  test sensitivity            0.9100      0.9250     0.0822  5
  test specificity            0.5950      0.7375     0.3362  5
  test precision              0.5762      0.6111     0.1401  5
  test loss                   0.5682      0.5182     0.1448  5
  FPR (FP/(FP+TN))            0.4050      0.2625     0.3362  5
  FNR (FN/(FN+TP))            0.0900      0.0750     0.0822  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6875      0.6976     0.0892  5
  max valid BA                0.7082      0.6976     0.0605  5
  best valid F1               0.6139      0.6016     0.0750  5
  test BA                     0.7177      0.7401     0.0774  5
  test AUC                    0.7602      0.7841     0.0617  5
  test AUC in-protein         0.4833      0.4995     0.0887  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4796      0.5000     0.0690  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6060      0.6562     0.1379  5
  test sensitivity            0.6070      0.7193     0.2071  5
  test specificity            0.8283      0.8230     0.0704  5
  test precision              0.6463      0.6721     0.0501  5
  test loss                   0.5893      0.5813     0.0676  5
  FPR (FP/(FP+TN))            0.1717      0.1770     0.0704  5
  FNR (FN/(FN+TP))            0.3930      0.2807     0.2071  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5625      0.5938     0.0585  5
  max valid BA                0.5687      0.5938     0.0640  5
  best valid F1               0.4462      0.5000     0.1279  5
  test BA                     0.4562      0.4375     0.0419  5
  test AUC                    0.4734      0.4766     0.0238  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.5267      0.5000     0.3919  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.1497      0.0000     0.2051  5
  test sensitivity            0.2250      0.0000     0.3112  5
  test specificity            0.6875      0.8750     0.3802  5
  test precision              0.1878      0.2778     0.1627  3
  test loss                   0.6857      0.6940     0.0291  5
  FPR (FP/(FP+TN))            0.3125      0.1250     0.3802  5
  FNR (FN/(FN+TP))            0.7750      1.0000     0.3112  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_drop_buriedness_q50 --seeds=0,1,2,3,4`
