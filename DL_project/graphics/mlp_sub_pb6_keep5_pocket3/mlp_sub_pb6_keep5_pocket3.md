# mlp_sub_pb6_keep5_pocket3

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_keep5_pocket3'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.6667      0.3220      0.4989      0.5951      0.6727      0.3850
groups_FA                                    5      0.4917      0.7676      0.4973      0.6697      0.3833      0.7944
groups_LPC+LPE+LPG                           5      0.8000      0.6710      0.6339      0.6218      0.9500      0.5200
groups_PA                                    5      0.6308      0.9385      0.6020      0.6137      0.6000      0.9462
groups_PC                                    5      0.3560      0.6975      0.4683      0.6659      0.3046      0.7584
groups_PE                                    5      0.9200      0.7625      0.6199      0.6154      0.9150      0.7525
groups_PG                                    5      0.7754      0.7186      0.6069      0.6224      0.7679      0.7027
groups_PI                                    5      0.4000      0.6250      0.5751      0.6070      0.5500      0.7000
ALL                                         40      0.6301      0.6878      0.5628      0.6264      0.6429      0.6949

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6621      0.6747     0.1228  40
max valid BA                0.6689      0.6833     0.1220  40
best valid F1               0.5817      0.6280     0.1610  40
test BA                     0.6589      0.6643     0.1413  40
test AUC                    0.6271      0.6428     0.1967  40
test AUC in-protein         0.4889      0.5000     0.0423  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.4863      0.5000     0.0454  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.5494      0.5868     0.2214  40
test sensitivity            0.6301      0.6721     0.2957  40
test specificity            0.6878      0.7404     0.2637  40
test precision              0.5574      0.5759     0.1711  38
test loss                   0.6627      0.6804     0.0461  40
FPR (FP/(FP+TN))            0.3122      0.2596     0.2637  40
FNR (FN/(FN+TP))            0.3699      0.3279     0.2957  40

=== abs(sensitivity-specificity) gap: mean=0.3725 median=0.3201 n=40 ===
sensitivity std across seeds (by group): mean=0.2090 median=0.2185 n=8
specificity std across seeds (by group): mean=0.1761 median=0.1466 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5289      0.5125     0.0559  5
  max valid BA                0.5289      0.5125     0.0559  5
  best valid F1               0.5776      0.6000     0.0751  5
  test BA                     0.4943      0.5000     0.0285  5
  test AUC                    0.4588      0.4390     0.0845  5
  test AUC in-protein         0.5000      0.5000     0.0000  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.5000      0.5000     0.0000  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4607      0.5684     0.2593  5
  test sensitivity            0.6667      0.7576     0.3857  5
  test specificity            0.3220      0.1463     0.3908  5
  test precision              0.4418      0.4438     0.0202  4
  test loss                   0.7008      0.7002     0.0102  5
  FPR (FP/(FP+TN))            0.6780      0.8537     0.3908  5
  FNR (FN/(FN+TP))            0.3333      0.2424     0.3857  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5750      0.5417     0.0772  5
  max valid BA                0.5889      0.5417     0.0899  5
  best valid F1               0.4449      0.3390     0.1883  5
  test BA                     0.6296      0.6408     0.0608  5
  test AUC                    0.5669      0.5321     0.1449  5
  test AUC in-protein         0.5000      0.5000     0.0000  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.4909      0.5000     0.0203  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.5309      0.5385     0.0778  5
  test sensitivity            0.4917      0.5000     0.0950  5
  test specificity            0.7676      0.7838     0.1057  5
  test precision              0.5918      0.6364     0.1108  5
  test loss                   0.6793      0.6792     0.0126  5
  FPR (FP/(FP+TN))            0.2324      0.2162     0.1057  5
  FNR (FN/(FN+TP))            0.5083      0.5000     0.0950  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7146      0.7375     0.0888  5
  max valid BA                0.7350      0.7375     0.0562  5
  best valid F1               0.6707      0.6667     0.0504  5
  test BA                     0.7355      0.7440     0.0970  5
  test AUC                    0.6901      0.7016     0.1683  5
  test AUC in-protein         0.4688      0.5000     0.0625  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.4824      0.5000     0.0395  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.6491      0.6667     0.1238  5
  test sensitivity            0.8000      0.8750     0.2396  5
  test specificity            0.6710      0.6774     0.2096  5
  test precision              0.5863      0.5833     0.1118  5
  test loss                   0.6670      0.6832     0.0535  5
  FPR (FP/(FP+TN))            0.3290      0.3226     0.2096  5
  FNR (FN/(FN+TP))            0.2000      0.1250     0.2396  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7731      0.7692     0.0567  5
  max valid BA                0.7731      0.7692     0.0567  5
  best valid F1               0.6954      0.6957     0.0778  5
  test BA                     0.7846      0.7500     0.1157  5
  test AUC                    0.7754      0.7515     0.1292  5
  test AUC in-protein         0.4479      0.5000     0.1042  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.4222      0.5000     0.1083  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.7074      0.6667     0.1546  5
  test sensitivity            0.6308      0.5385     0.2135  5
  test specificity            0.9385      0.9615     0.0344  5
  test precision              0.8285      0.8750     0.0981  5
  test loss                   0.6371      0.6452     0.0367  5
  FPR (FP/(FP+TN))            0.0615      0.0385     0.0344  5
  FNR (FN/(FN+TP))            0.3692      0.4615     0.2135  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5239      0.5079     0.0364  5
  max valid BA                0.5315      0.5233     0.0385  5
  best valid F1               0.3650      0.2868     0.1344  5
  test BA                     0.5267      0.5152     0.0399  5
  test AUC                    0.3948      0.3622     0.1189  5
  test AUC in-protein         0.5002      0.5000     0.0005  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.5001      0.5000     0.0002  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.2652      0.2692     0.2556  5
  test sensitivity            0.3560      0.1927     0.4295  5
  test specificity            0.6975      0.8680     0.4040  5
  test precision              0.3650      0.4051     0.1171  4
  test loss                   0.6968      0.6924     0.0145  5
  FPR (FP/(FP+TN))            0.3025      0.1320     0.4040  5
  FNR (FN/(FN+TP))            0.6440      0.8073     0.4295  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8300      0.8313     0.0329  5
  max valid BA                0.8337      0.8438     0.0341  5
  best valid F1               0.7600      0.7742     0.0375  5
  test BA                     0.8412      0.8438     0.0267  5
  test AUC                    0.8845      0.9022     0.0355  5
  test AUC in-protein         0.5000      0.5000     0.0000  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.5000      0.5000     0.0000  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7688      0.7619     0.0324  5
  test sensitivity            0.9200      0.9250     0.0512  5
  test specificity            0.7625      0.7750     0.0523  5
  test precision              0.6623      0.6604     0.0450  5
  test loss                   0.6049      0.6323     0.0664  5
  FPR (FP/(FP+TN))            0.2375      0.2250     0.0523  5
  FNR (FN/(FN+TP))            0.0800      0.0750     0.0512  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7264      0.7112     0.0449  5
  max valid BA                0.7353      0.7335     0.0441  5
  best valid F1               0.6497      0.6466     0.0489  5
  test BA                     0.7470      0.7575     0.0208  5
  test AUC                    0.7641      0.7567     0.0360  5
  test AUC in-protein         0.4956      0.5000     0.0099  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.4944      0.5000     0.0124  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6647      0.6765     0.0238  5
  test sensitivity            0.7754      0.7895     0.0337  5
  test specificity            0.7186      0.7257     0.0246  5
  test precision              0.5820      0.5823     0.0234  5
  test loss                   0.6345      0.6266     0.0335  5
  FPR (FP/(FP+TN))            0.2814      0.2743     0.0246  5
  FNR (FN/(FN+TP))            0.2246      0.2105     0.0337  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6250      0.6562     0.0765  5
  max valid BA                0.6250      0.6562     0.0765  5
  best valid F1               0.4899      0.5333     0.1301  5
  test BA                     0.5125      0.5000     0.0523  5
  test AUC                    0.4820      0.4531     0.1229  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.5000      0.5000     0.0000  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.3485      0.3333     0.1278  5
  test sensitivity            0.4000      0.3750     0.2236  5
  test specificity            0.6250      0.5625     0.1875  5
  test precision              0.3400      0.3333     0.0693  5
  test loss                   0.6812      0.6896     0.0217  5
  FPR (FP/(FP+TN))            0.3750      0.4375     0.1875  5
  FNR (FN/(FN+TP))            0.6000      0.6250     0.2236  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_keep5_pocket3 --seeds=0,1,2,3,4`
