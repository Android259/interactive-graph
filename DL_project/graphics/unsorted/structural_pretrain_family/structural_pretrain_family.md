# structural_pretrain_family

## Summary (analysis/summarize_label.py)

```
Summary: 'structural_pretrain_family'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.8406      0.6444      0.9038      0.7328      0.9231      0.8436
groups_GLTP            5      0.9600      0.7941      0.9207      0.8697      0.9667      0.8867
groups_IP_trans        5      1.0000      0.5875      0.8321      0.7137      1.0000      0.6736
groups_LBP_BPI_CETP    5      0.8000      0.8148      0.8851      0.8643      1.0000      0.9556
groups_ML              5      1.0000      0.0000      1.0000      0.0000      1.0000      0.0000
groups_OSBP            5      1.0000      0.0000         n/a         n/a         n/a         n/a
groups_START           5      0.8685      0.9089      0.9541      0.8793      1.0000      0.9176
groups_lipocalin       5      0.8881      0.9531      0.9022      0.8590      0.9131      0.8955
groups_scp2            5      0.7867      0.6943      0.9297      0.7123      1.0000      0.7567
ALL                   45      0.9027      0.5997      0.9066      0.7821      0.9726      0.8235

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8886      0.9045     0.1030  36
max valid BA                0.8981      0.9129     0.1019  36
best valid F1               0.6969      0.8235     0.3456  45
test BA                     0.7580      0.7929     0.1605  44
test AUC                    0.8208      0.9095     0.2787  44
test AUC in-protein         0.8756      0.9387     0.1705  30
  (proteins averaged)       0.9778      1.0000     0.8115  45
test AUC in-protein (pairs)      0.8202      0.9083     0.2899  42
  (proteins contributing)      2.1111      2.0000     1.2472  45
test F1                     0.6998      0.6875     0.1869  45
test sensitivity            0.9027      1.0000     0.1529  44
test specificity            0.5997      0.7200     0.3533  45
test precision              0.6128      0.5789     0.2184  45
test loss                   0.4951      0.5337     0.2467  45
FPR (FP/(FP+TN))            0.4003      0.2800     0.3533  45
FNR (FN/(FN+TP))            0.0973      0.0000     0.1529  44

=== abs(sensitivity-specificity) gap: mean=0.3809 median=0.2342 n=44 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8776      0.8750     0.0992  5
  max valid BA                0.8833      0.8750     0.0982  5
  best valid F1               0.8388      0.8235     0.1214  5
  test BA                     0.7425      0.7492     0.0343  5
  test AUC                    0.7913      0.8000     0.0357  5
  test AUC in-protein         0.8859      0.8924     0.0827  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.8874      0.8706     0.0445  5
    (proteins contributing)      4.0000      4.0000     0.7071  5
  test F1                     0.6679      0.6667     0.0321  5
  test sensitivity            0.8406      0.8462     0.0125  5
  test specificity            0.6444      0.6522     0.0748  5
  test precision              0.5553      0.5625     0.0441  5
  test loss                   0.6384      0.6025     0.1021  5
  FPR (FP/(FP+TN))            0.3556      0.3478     0.0748  5
  FNR (FN/(FN+TP))            0.1594      0.1538     0.0125  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9142      0.9000     0.0533  5
  max valid BA                0.9267      0.9167     0.0418  5
  best valid F1               0.8352      0.8000     0.1260  5
  test BA                     0.8770      0.9000     0.0401  5
  test AUC                    0.9261      0.9394     0.0810  5
  test AUC in-protein         0.9530      1.0000     0.0812  5
    (proteins averaged)       1.4000      1.0000     0.5477  5
  test AUC in-protein (pairs)      0.9488      1.0000     0.0902  5
    (proteins contributing)      1.6000      2.0000     0.5477  5
  test F1                     0.7811      0.8000     0.0812  5
  test sensitivity            0.9600      1.0000     0.0894  5
  test specificity            0.7941      0.8000     0.1379  5
  test precision              0.6867      0.6667     0.1880  5
  test loss                   0.3744      0.4247     0.2016  5
  FPR (FP/(FP+TN))            0.2059      0.2000     0.1379  5
  FNR (FN/(FN+TP))            0.0400      0.0000     0.0894  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8268      0.8125     0.0583  5
  max valid BA                0.8368      0.8125     0.0670  5
  best valid F1               0.7010      0.6667     0.0984  5
  test BA                     0.7938      0.7857     0.0823  5
  test AUC                    0.8513      0.8571     0.1121  5
  test AUC in-protein         0.6405      0.6143     0.3130  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.8003      0.8462     0.1642  5
    (proteins contributing)      2.0000      2.0000     0.7071  5
  test F1                     0.6357      0.6000     0.2048  5
  test sensitivity            1.0000      1.0000     0.0000  5
  test specificity            0.5875      0.5714     0.1647  5
  test precision              0.4940      0.4286     0.2356  5
  test loss                   0.6549      0.7309     0.2892  5
  FPR (FP/(FP+TN))            0.4125      0.4286     0.1647  5
  FNR (FN/(FN+TP))            0.0000      0.0000     0.0000  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9778      1.0000     0.0304  5
  max valid BA                0.9778      1.0000     0.0304  5
  best valid F1               0.9429      1.0000     0.0782  5
  test BA                     0.8074      0.8889     0.1566  5
  test AUC                    0.8714      0.9259     0.1526  5
  test AUC in-protein         0.8500      0.8333     0.1708  5
    (proteins averaged)       1.0000      1.0000     0.0000  5
  test AUC in-protein (pairs)      0.8625      0.9167     0.1741  5
    (proteins contributing)      1.8000      2.0000     0.4472  5
  test F1                     0.6832      0.7500     0.2233  5
  test sensitivity            0.8000      1.0000     0.2739  5
  test specificity            0.8148      0.8000     0.0572  5
  test precision              0.6033      0.6000     0.1987  5
  test loss                   0.4158      0.2909     0.3120  5
  FPR (FP/(FP+TN))            0.1852      0.2000     0.0572  5
  FNR (FN/(FN+TP))            0.2000      0.0000     0.2739  5

groups_ML (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0000  1
  max valid BA                0.5000      0.5000     0.0000  1
  best valid F1               0.1333      0.0000     0.2981  5
  test BA                     0.5000      0.5000     0.0000  5
  test AUC                    0.2000      0.0000     0.4472  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.2000      0.0000     0.4472  5
    (proteins contributing)      1.0000      1.0000     0.0000  5
  test F1                     0.6667      0.6667     0.0000  5
  test sensitivity            1.0000      1.0000     0.0000  5
  test specificity            0.0000      0.0000     0.0000  5
  test precision              0.5000      0.5000     0.0000  5
  test loss                   0.6957      0.6962     0.0024  5
  FPR (FP/(FP+TN))            1.0000      1.0000     0.0000  5
  FNR (FN/(FN+TP))            0.0000      0.0000     0.0000  5

groups_OSBP (n=5):
  metric                        mean      median        std  n
  best valid F1               0.2000      0.0000     0.4472  5
  test BA                     0.5000      0.5000     0.0000  4
  test AUC                    1.0000      1.0000     0.0000  4
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      1.0000      1.0000     0.0000  2
    (proteins contributing)      0.4000      0.0000     0.5477  5
  test F1                     0.5333      0.6667     0.2981  5
  test sensitivity            1.0000      1.0000     0.0000  4
  test specificity            0.0000      0.0000     0.0000  5
  test precision              0.4000      0.5000     0.2236  5
  test loss                   0.7068      0.6927     0.0357  5
  FPR (FP/(FP+TN))            1.0000      1.0000     0.0000  5
  FNR (FN/(FN+TP))            0.0000      0.0000     0.0000  4

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9472      0.9545     0.0367  5
  max valid BA                0.9588      0.9773     0.0383  5
  best valid F1               0.9333      0.9600     0.0573  5
  test BA                     0.8887      0.8656     0.0572  5
  test AUC                    0.9744      0.9780     0.0212  5
  test AUC in-protein         0.9624      0.9675     0.0378  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.9517      0.9720     0.0571  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.8518      0.8182     0.0642  5
  test sensitivity            0.8685      0.8462     0.0892  5
  test specificity            0.9089      0.9130     0.0353  5
  test precision              0.8374      0.8333     0.0484  5
  test loss                   0.2086      0.1946     0.0702  5
  FPR (FP/(FP+TN))            0.0911      0.0870     0.0353  5
  FNR (FN/(FN+TP))            0.1315      0.1538     0.0892  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8960      0.8920     0.0496  5
  max valid BA                0.9043      0.8920     0.0418  5
  best valid F1               0.8599      0.8750     0.0541  5
  test BA                     0.9206      0.9286     0.0478  5
  test AUC                    0.9530      0.9697     0.0600  5
  test AUC in-protein         0.9000      1.0000     0.1732  3
    (proteins averaged)       1.0000      1.0000     1.0000  5
  test AUC in-protein (pairs)      0.9538      1.0000     0.1032  5
    (proteins contributing)      3.6000      4.0000     0.8944  5
  test F1                     0.8926      0.9231     0.0809  5
  test sensitivity            0.8881      0.8571     0.1096  5
  test specificity            0.9531      0.9333     0.0437  5
  test precision              0.9050      0.9000     0.1037  5
  test loss                   0.2334      0.1944     0.1319  5
  FPR (FP/(FP+TN))            0.0469      0.0667     0.0437  5
  FNR (FN/(FN+TP))            0.1119      0.1429     0.1096  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8583      0.8750     0.1143  5
  max valid BA                0.8783      0.9000     0.1102  5
  best valid F1               0.8280      0.8571     0.1326  5
  test BA                     0.7405      0.7500     0.1000  5
  test AUC                    0.8554      0.8571     0.0391  5
  test AUC in-protein         0.9167      0.9167     0.0833  3
    (proteins averaged)       0.6000      1.0000     0.5477  5
  test AUC in-protein (pairs)      0.8848      0.8571     0.0699  5
    (proteins contributing)      1.6000      2.0000     0.5477  5
  test F1                     0.5855      0.6667     0.2066  5
  test sensitivity            0.7867      0.8000     0.2724  5
  test specificity            0.6943      0.7143     0.1455  5
  test precision              0.5333      0.5000     0.2248  5
  test loss                   0.5279      0.5170     0.1851  5
  FPR (FP/(FP+TN))            0.3057      0.2857     0.1455  5
  FNR (FN/(FN+TP))            0.2133      0.2000     0.2724  5
```

## AUC vs chemistry null model, same rows (analysis/solo_family_report.py)

Not analysis/full_label_report.py: its null model reconstructs an EXCLUDED-family split, the opposite of --family_only (restricts to one family, splits randomly inside it) -- see this function's own docstring.

```
fam           seed  rows  pos seen_in_train  net_AUC net_AUC_pairs proteins  null_AUC null_AUC_pairs
CRAL-TRIO        0    36   11         0.690    0.818         0.871      3.0     0.902          0.941
CRAL-TRIO        1    37   13         0.680    0.811         0.961      4.0     0.929          1.000
CRAL-TRIO        2    36   13         0.810    0.729         0.862      4.0     0.799          0.839
CRAL-TRIO        3    38   13         0.820    0.800         0.848      5.0     0.874          0.943
CRAL-TRIO        4    37   13         0.840    0.798         0.895      4.0     0.902          0.983
GLTP             0    14    4         0.290    1.000         1.000      2.0     1.000          1.000
GLTP             1    14    3         0.140    0.879         1.000      1.0     0.939          1.000
GLTP             2    14    6         0.290    0.812         0.792      2.0     0.958          0.958
GLTP             3    14    3         0.360    0.939         0.952      1.0     0.970          0.952
GLTP             4    14    5         0.570    1.000         1.000      2.0     0.956          1.000
IP_trans         0    13    3         0.230    1.000         1.000      1.0     0.983          0.967
IP_trans         1    14    3         0.210    0.758         0.667      2.0     0.848          0.833
IP_trans         2    12    5         0.330    0.857         0.889      2.0     0.643          0.944
IP_trans         3    13    2         0.230    0.727         0.600      2.0     0.818          0.700
IP_trans         4    12    5         0.250    0.914         0.846      3.0     0.671          0.885
LBP_BPI_CETP     0    12    3         0.420    0.926         0.917      2.0     0.870          0.792
LBP_BPI_CETP     1    12    3         0.420    1.000         1.000      2.0     0.852          0.933
LBP_BPI_CETP     2    12    5         0.500    1.000         1.000      2.0     0.971          0.944
LBP_BPI_CETP     3    12    2         0.170    0.650         0.583      1.0     0.850          0.917
LBP_BPI_CETP     4    12    4         0.420    0.781         0.812      2.0     0.781          0.750
ML               0     2    1         0.000    1.000         1.000      1.0     1.000          1.000
ML               1     2    1         0.000    0.000         0.000      1.0     0.500          0.500
ML               2     2    1         0.000    0.000         0.000      1.0     1.000          1.000
ML               3     2    1         0.000    0.000         0.000      1.0     0.000          0.000
ML               4     2    1         0.000    0.000         0.000      1.0     0.000          0.000
OSBP             0     2    1         0.500    1.000         1.000      1.0     1.000          1.000
OSBP             1     2    1         0.000    1.000         1.000      1.0     1.000          1.000
OSBP             2     1    0           nan      nan           nan      0.0       nan            nan
OSBP             3     2    1         0.000    1.000           nan      0.0     0.000            nan
OSBP             4     2    1         0.000    1.000           nan      0.0     0.000            nan
START            0    34   11         0.710    1.000         1.000      3.0     0.866          0.817
START            1    34   13         0.710    0.978         0.981      3.0     1.000          1.000
START            2    34   13         0.680    0.941         0.855      3.0     0.908          0.836
START            3    34   11         0.820    0.980         0.972      3.0     0.980          0.981
START            4    34   11         0.590    0.972         0.950      3.0     0.875          0.827
lipocalin        0    20    7         0.550    0.989         1.000      4.0     0.879          1.000
lipocalin        1    20    7         0.550    0.956         1.000      4.0     0.819          0.889
lipocalin        2    20    9         0.600    0.970         1.000      4.0     0.899          0.900
lipocalin        3    19    4         0.530    0.850         0.769      2.0     0.733          0.692
lipocalin        4    19    6         0.630    1.000         1.000      4.0     0.923          0.929
scp2             0     9    2         0.110    0.857         0.833      2.0     0.643          0.667
scp2             1    10    5         0.000    0.800         0.900      2.0     0.600          0.700
scp2             2    10    3         0.100    0.905         1.000      1.0     0.952          1.000
scp2             3    10    5         0.400    0.840         0.857      2.0     0.960          0.929
scp2             4     9    1         0.330    0.875         0.833      1.0     0.500          0.500
```
