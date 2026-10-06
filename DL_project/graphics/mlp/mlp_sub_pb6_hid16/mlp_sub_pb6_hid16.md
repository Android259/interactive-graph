# mlp_sub_pb6_hid16

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_hid16'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.4424      0.4976      0.5254      0.6585      0.4970      0.5100
groups_FA                                    5      0.3917      0.7189      0.5304      0.6190      0.4417      0.7167
groups_LPC+LPE+LPG                           5      0.5125      0.8452      0.8146      0.7834      0.4750      0.8067
groups_PA                                    5      0.5538      0.8769      0.5148      0.6971      0.5385      0.9462
groups_PC                                    5      0.2679      0.7188      0.4519      0.7027      0.2862      0.7086
groups_PE                                    5      0.8850      0.7925      0.7877      0.7778      0.9000      0.8000
groups_PG                                    5      0.6982      0.7965      0.7969      0.7645      0.6929      0.7841
groups_PI                                    5      0.3000      0.6500      0.3845      0.6975      0.5500      0.5500
groups_PS+PGP+DAG+TAG                        5      0.4000      0.6533      0.3799      0.6406      0.4500      0.6250
ALL                                         45      0.4946      0.7277      0.5762      0.7046      0.5368      0.7164

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6165      0.5625     0.1234  45
max valid BA                0.6266      0.5694     0.1265  45
best valid F1               0.5266      0.5517     0.1831  45
test BA                     0.6112      0.5850     0.1355  45
test AUC                    0.5837      0.5349     0.2137  45
test AUC in-protein         0.5883      0.5338     0.2474  32
  (proteins averaged)       3.0000      2.0000     3.5162  45
test AUC in-protein (pairs)      0.5179      0.5318     0.2326  45
  (proteins contributing)      5.4444      3.0000     4.0819  45
test F1                     0.4457      0.5185     0.2574  45
test sensitivity            0.4946      0.5455     0.3303  45
test specificity            0.7277      0.8230     0.3006  45
test precision              0.5530      0.5938     0.1943  39
test loss                   0.6461      0.6812     0.1148  45
FPR (FP/(FP+TN))            0.2723      0.1770     0.3006  45
FNR (FN/(FN+TP))            0.5054      0.4545     0.3303  45

=== abs(sensitivity-specificity) gap: mean=0.5066 median=0.4335 n=45 ===
sensitivity std across seeds (by group): mean=0.2432 median=0.2275 n=9
specificity std across seeds (by group): mean=0.2473 median=0.2467 n=9

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5005      0.5000     0.0232  5
  max valid BA                0.5035      0.5000     0.0193  5
  best valid F1               0.5671      0.5800     0.0519  5
  test BA                     0.4700      0.5000     0.0582  5
  test AUC                    0.3935      0.3740     0.1942  5
  test AUC in-protein         0.4606      0.5000     0.1715  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4589      0.4022     0.2058  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.3138      0.4286     0.2946  5
  test sensitivity            0.4424      0.5455     0.4368  5
  test specificity            0.4976      0.2683     0.4671  5
  test precision              0.4094      0.4231     0.0510  3
  test loss                   0.7314      0.6986     0.0801  5
  FPR (FP/(FP+TN))            0.5024      0.7317     0.4671  5
  FNR (FN/(FN+TP))            0.5576      0.4545     0.4368  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5653      0.5625     0.0446  5
  max valid BA                0.5792      0.5694     0.0512  5
  best valid F1               0.4671      0.4528     0.1499  5
  test BA                     0.5553      0.5850     0.0669  5
  test AUC                    0.4482      0.4088     0.0903  5
  test AUC in-protein         0.5000      0.5000     0.3662  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.3264      0.3636     0.1083  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.4103      0.3750     0.0988  5
  test sensitivity            0.3917      0.3333     0.2275  5
  test specificity            0.7189      0.8378     0.2467  5
  test precision              0.5388      0.5714     0.1618  5
  test loss                   0.7540      0.6954     0.1094  5
  FPR (FP/(FP+TN))            0.2811      0.1622     0.2467  5
  FNR (FN/(FN+TP))            0.6083      0.6667     0.2275  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6250      0.6521     0.0854  5
  max valid BA                0.6408      0.6667     0.0945  5
  best valid F1               0.5348      0.5517     0.1008  5
  test BA                     0.6788      0.7006     0.0482  5
  test AUC                    0.7054      0.6825     0.1301  5
  test AUC in-protein         0.8728      0.8438     0.0873  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.7104      0.6786     0.1362  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5651      0.6000     0.0693  5
  test sensitivity            0.5125      0.5000     0.0815  5
  test specificity            0.8452      0.8387     0.0620  5
  test precision              0.6408      0.6364     0.1066  5
  test loss                   0.6053      0.6266     0.1177  5
  FPR (FP/(FP+TN))            0.1548      0.1613     0.0620  5
  FNR (FN/(FN+TP))            0.4875      0.5000     0.0815  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7231      0.7500     0.0554  5
  max valid BA                0.7423      0.7500     0.0520  5
  best valid F1               0.6524      0.6667     0.0809  5
  test BA                     0.7154      0.7115     0.0439  5
  test AUC                    0.7503      0.7130     0.0709  5
  test AUC in-protein         0.5250      0.4500     0.3403  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.6349      0.5333     0.2529  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6166      0.6087     0.0663  5
  test sensitivity            0.5538      0.5385     0.0644  5
  test specificity            0.8769      0.8846     0.0688  5
  test precision              0.7075      0.7000     0.1211  5
  test loss                   0.6404      0.6452     0.0401  5
  FPR (FP/(FP+TN))            0.1231      0.1154     0.0688  5
  FNR (FN/(FN+TP))            0.4462      0.4615     0.0644  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4950      0.5000     0.0165  5
  max valid BA                0.4974      0.5048     0.0170  5
  best valid F1               0.3241      0.2212     0.1744  5
  test BA                     0.4933      0.5000     0.0209  5
  test AUC                    0.4098      0.4133     0.0474  5
  test AUC in-protein         0.4800      0.4244     0.1569  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4764      0.4622     0.0902  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.2012      0.1277     0.1996  5
  test sensitivity            0.2679      0.0826     0.4144  5
  test specificity            0.7188      0.8832     0.4053  5
  test precision              0.3483      0.3207     0.0895  4
  test loss                   0.6900      0.6877     0.0121  5
  FPR (FP/(FP+TN))            0.2812      0.1168     0.4053  5
  FNR (FN/(FN+TP))            0.7321      0.9174     0.4144  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8425      0.8375     0.0341  5
  max valid BA                0.8500      0.8438     0.0261  5
  best valid F1               0.7824      0.7816     0.0290  5
  test BA                     0.8387      0.8375     0.0399  5
  test AUC                    0.9046      0.8881     0.0340  5
  test AUC in-protein         0.7916      0.8492     0.1790  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7962      0.8052     0.1104  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7695      0.7692     0.0460  5
  test sensitivity            0.8850      0.8750     0.0627  5
  test specificity            0.7925      0.8000     0.0360  5
  test precision              0.6816      0.6863     0.0441  5
  test loss                   0.4399      0.4407     0.0390  5
  FPR (FP/(FP+TN))            0.2075      0.2000     0.0360  5
  FNR (FN/(FN+TP))            0.1150      0.1250     0.0627  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7287      0.7196     0.0246  5
  max valid BA                0.7385      0.7418     0.0269  5
  best valid F1               0.6518      0.6545     0.0337  5
  test BA                     0.7474      0.7492     0.0289  5
  test AUC                    0.7915      0.7990     0.0428  5
  test AUC in-protein         0.5146      0.5328     0.0955  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4979      0.5174     0.0690  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6652      0.6667     0.0361  5
  test sensitivity            0.6982      0.7018     0.0260  5
  test specificity            0.7965      0.8142     0.0434  5
  test precision              0.6365      0.6500     0.0518  5
  test loss                   0.5511      0.5625     0.0596  5
  FPR (FP/(FP+TN))            0.2035      0.1858     0.0434  5
  FNR (FN/(FN+TP))            0.3018      0.2982     0.0260  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5375      0.5312     0.0513  5
  max valid BA                0.5500      0.5312     0.0648  5
  best valid F1               0.3913      0.5161     0.2052  5
  test BA                     0.4750      0.5000     0.0342  5
  test AUC                    0.3578      0.3906     0.0813  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.4200      0.5000     0.2662  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.1773      0.0000     0.2428  5
  test sensitivity            0.3000      0.0000     0.4202  5
  test specificity            0.6500      0.8750     0.4455  5
  test precision              0.2126      0.3043     0.1847  3
  test loss                   0.7159      0.7045     0.0693  5
  FPR (FP/(FP+TN))            0.3500      0.1250     0.4455  5
  FNR (FN/(FN+TP))            0.7000      1.0000     0.4202  5

groups_PS+PGP+DAG+TAG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5312      0.5312     0.0221  5
  max valid BA                0.5375      0.5312     0.0261  5
  best valid F1               0.3680      0.3000     0.1383  5
  test BA                     0.5267      0.5222     0.0202  5
  test AUC                    0.4919      0.5111     0.0788  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.3400      0.5000     0.3130  5
    (proteins contributing)      2.6000      3.0000     0.8944  5
  test F1                     0.2926      0.2000     0.2400  5
  test sensitivity            0.4000      0.1111     0.4554  5
  test specificity            0.6533      0.9333     0.4507  5
  test precision              0.5700      0.4457     0.2913  4
  test loss                   0.6871      0.6895     0.0133  5
  FPR (FP/(FP+TN))            0.3467      0.0667     0.4507  5
  FNR (FN/(FN+TP))            0.6000      0.8889     0.4554  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_hid16 --seeds=0,1,2,3,4`
