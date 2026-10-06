# structural_pretrain_family_unfrozen

## Summary (analysis/summarize_label.py)

```
Summary: 'structural_pretrain_family_unfrozen'
rows: 39

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.8867      0.7689      0.9312      0.8209      0.9242      0.8917
groups_GLTP            5      1.0000      0.8918      0.9518      0.9425      1.0000      0.9800
groups_IP_trans        5      0.9200      0.6847      0.9114      0.7433      1.0000      0.8468
groups_LBP_BPI_CETP    5      0.8000      0.8906      0.8802      0.8890      1.0000      0.9556
groups_ML              4      1.0000      0.0000      1.0000      0.0000      1.0000      0.0000
groups_START           5      0.8657      0.9072      0.9542      0.8518      1.0000      0.9184
groups_lipocalin       5      0.9167      0.8621      0.9185      0.8725      0.9429      0.9076
groups_scp2            5      0.8800      0.8129      0.9407      0.8194      1.0000      0.7883
ALL                   39      0.9063      0.7459      0.9289      0.8249      0.9815      0.8734

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.9104      0.9375     0.1020  36
max valid BA                0.9275      0.9500     0.0953  36
best valid F1               0.8230      0.8889     0.2576  39
test BA                     0.8261      0.8750     0.1452  39
test AUC                    0.9000      0.9630     0.1753  39
test AUC in-protein         0.8990      0.9739     0.1506  30
  (proteins averaged)       1.1282      1.0000     0.7671  39
test AUC in-protein (pairs)      0.8971      0.9720     0.1876  39
  (proteins contributing)      2.3590      2.0000     1.1353  39
test F1                     0.7682      0.8000     0.1561  39
test sensitivity            0.9063      1.0000     0.1464  39
test specificity            0.7459      0.8182     0.2826  39
test precision              0.6971      0.7500     0.1941  39
test loss                   0.4042      0.3227     0.2433  39
FPR (FP/(FP+TN))            0.2541      0.1818     0.2826  39
FNR (FN/(FN+TP))            0.0937      0.0000     0.1464  39

=== abs(sensitivity-specificity) gap: mean=0.2442 median=0.1429 n=39 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8842      0.8638     0.0899  5
  max valid BA                0.9079      0.8814     0.0895  5
  best valid F1               0.8784      0.8462     0.1183  5
  test BA                     0.8278      0.8194     0.0464  5
  test AUC                    0.8827      0.8982     0.0365  5
  test AUC in-protein         0.9102      0.9321     0.0592  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.9112      0.9080     0.0369  5
    (proteins contributing)      4.0000      4.0000     0.7071  5
  test F1                     0.7616      0.7692     0.0524  5
  test sensitivity            0.8867      0.9231     0.0922  5
  test specificity            0.7689      0.8000     0.0910  5
  test precision              0.6745      0.6667     0.0757  5
  test loss                   0.4818      0.4146     0.1845  5
  FPR (FP/(FP+TN))            0.2311      0.2000     0.0910  5
  FNR (FN/(FN+TP))            0.1133      0.0769     0.0922  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9900      1.0000     0.0224  5
  max valid BA                0.9900      1.0000     0.0224  5
  best valid F1               0.9778      1.0000     0.0497  5
  test BA                     0.9459      0.9545     0.0571  5
  test AUC                    0.9856      1.0000     0.0201  5
  test AUC in-protein         0.9780      1.0000     0.0306  5
    (proteins averaged)       1.4000      1.0000     0.5477  5
  test AUC in-protein (pairs)      0.9738      1.0000     0.0380  5
    (proteins contributing)      1.6000      2.0000     0.5477  5
  test F1                     0.9029      0.8571     0.0917  5
  test sensitivity            1.0000      1.0000     0.0000  5
  test specificity            0.8918      0.9091     0.1143  5
  test precision              0.8333      0.7500     0.1559  5
  test loss                   0.2699      0.1748     0.3045  5
  FPR (FP/(FP+TN))            0.1082      0.0909     0.1143  5
  FNR (FN/(FN+TP))            0.0000      0.0000     0.0000  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8943      0.9000     0.0334  5
  max valid BA                0.9234      0.9375     0.0345  5
  best valid F1               0.8260      0.8000     0.0662  5
  test BA                     0.8023      0.7286     0.1027  5
  test AUC                    0.8573      0.8286     0.1121  5
  test AUC in-protein         0.7238      0.7333     0.2398  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.8559      0.8462     0.1640  5
    (proteins contributing)      2.0000      2.0000     0.7071  5
  test F1                     0.6452      0.6667     0.2014  5
  test sensitivity            0.9200      1.0000     0.1789  5
  test specificity            0.6847      0.8000     0.2114  5
  test precision              0.5533      0.6000     0.2548  5
  test loss                   0.5411      0.6355     0.2825  5
  FPR (FP/(FP+TN))            0.3153      0.2000     0.2114  5
  FNR (FN/(FN+TP))            0.0800      0.0000     0.1789  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9653      0.9444     0.0318  5
  max valid BA                0.9778      1.0000     0.0304  5
  best valid F1               0.9429      1.0000     0.0782  5
  test BA                     0.8453      0.9444     0.1633  5
  test AUC                    0.8626      0.9630     0.1799  5
  test AUC in-protein         0.8333      0.8333     0.2041  5
    (proteins averaged)       1.0000      1.0000     0.0000  5
  test AUC in-protein (pairs)      0.8333      0.9167     0.2125  5
    (proteins contributing)      1.8000      2.0000     0.4472  5
  test F1                     0.7371      0.8571     0.2444  5
  test sensitivity            0.8000      1.0000     0.2739  5
  test specificity            0.8906      0.8889     0.0715  5
  test precision              0.7000      0.7500     0.2401  5
  test loss                   0.3726      0.2473     0.2667  5
  FPR (FP/(FP+TN))            0.1094      0.1111     0.0715  5
  FNR (FN/(FN+TP))            0.2000      0.0000     0.2739  5

groups_ML (n=4):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0000  1
  max valid BA                0.5000      0.5000     0.0000  1
  best valid F1               0.1667      0.0000     0.3333  4
  test BA                     0.5000      0.5000     0.0000  4
  test AUC                    0.7500      1.0000     0.5000  4
    (proteins averaged)       0.0000      0.0000     0.0000  4
  test AUC in-protein (pairs)      0.7500      1.0000     0.5000  4
    (proteins contributing)      1.0000      1.0000     0.0000  4
  test F1                     0.6667      0.6667     0.0000  4
  test sensitivity            1.0000      1.0000     0.0000  4
  test specificity            0.0000      0.0000     0.0000  4
  test precision              0.5000      0.5000     0.0000  4
  test loss                   0.6939      0.6931     0.0017  4
  FPR (FP/(FP+TN))            1.0000      1.0000     0.0000  4
  FNR (FN/(FN+TP))            0.0000      0.0000     0.0000  4

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9517      0.9773     0.0392  5
  max valid BA                0.9592      0.9773     0.0386  5
  best valid F1               0.9376      0.9524     0.0511  5
  test BA                     0.8865      0.9328     0.0877  5
  test AUC                    0.9599      0.9763     0.0543  5
  test AUC in-protein         0.9532      0.9750     0.0690  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.9376      0.9802     0.1028  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.8585      0.9091     0.1069  5
  test sensitivity            0.8657      0.9091     0.0682  5
  test specificity            0.9072      0.9524     0.1122  5
  test precision              0.8551      0.9091     0.1439  5
  test loss                   0.2759      0.1951     0.1728  5
  FPR (FP/(FP+TN))            0.0928      0.0476     0.1122  5
  FNR (FN/(FN+TP))            0.1343      0.0909     0.0682  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9075      0.9375     0.0933  5
  max valid BA                0.9252      0.9545     0.0639  5
  best valid F1               0.8759      0.8889     0.0678  5
  test BA                     0.8894      0.9091     0.0706  5
  test AUC                    0.9645      0.9872     0.0333  5
  test AUC in-protein         0.9000      1.0000     0.1732  3
    (proteins averaged)       1.0000      1.0000     1.0000  5
  test AUC in-protein (pairs)      0.9396      1.0000     0.1001  5
    (proteins contributing)      3.6000      4.0000     0.8944  5
  test F1                     0.8283      0.8750     0.1328  5
  test sensitivity            0.9167      1.0000     0.1179  5
  test specificity            0.8621      0.8462     0.0580  5
  test precision              0.7609      0.8182     0.1499  5
  test loss                   0.2299      0.1895     0.1003  5
  FPR (FP/(FP+TN))            0.1379      0.1538     0.0580  5
  FNR (FN/(FN+TP))            0.0833      0.0000     0.1179  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8617      0.9000     0.0999  5
  max valid BA                0.8942      0.9000     0.0801  5
  best valid F1               0.8478      0.8000     0.0987  5
  test BA                     0.8464      0.8750     0.0973  5
  test AUC                    0.9074      0.8800     0.0894  5
  test AUC in-protein         1.0000      1.0000     0.0000  3
    (proteins averaged)       0.6000      1.0000     0.5477  5
  test AUC in-protein (pairs)      0.9457      1.0000     0.0871  5
    (proteins contributing)      1.6000      2.0000     0.5477  5
  test F1                     0.7248      0.8000     0.1438  5
  test sensitivity            0.8800      1.0000     0.1789  5
  test specificity            0.8129      0.8000     0.0453  5
  test precision              0.6600      0.7500     0.1888  5
  test loss                   0.4264      0.4200     0.2167  5
  FPR (FP/(FP+TN))            0.1871      0.2000     0.0453  5
  FNR (FN/(FN+TP))            0.1200      0.0000     0.1789  5
```

## AUC vs chemistry null model, same rows (analysis/solo_family_report.py)

Not analysis/full_label_report.py: its null model reconstructs an EXCLUDED-family split, the opposite of --family_only (restricts to one family, splits randomly inside it) -- see this function's own docstring.

```
fam           seed  rows  pos seen_in_train  net_AUC net_AUC_pairs proteins  null_AUC null_AUC_pairs
CRAL-TRIO        0    36   11         0.690    0.898         0.871      3.0     0.902          0.941
CRAL-TRIO        1    37   13         0.680    0.853         0.971      4.0     0.929          1.000
CRAL-TRIO        2    36   13         0.810    0.903         0.908      4.0     0.799          0.839
CRAL-TRIO        3    38   13         0.820    0.923         0.911      5.0     0.874          0.943
CRAL-TRIO        4    37   13         0.840    0.837         0.895      4.0     0.902          0.983
GLTP             0    14    4         0.290    1.000         1.000      2.0     1.000          1.000
GLTP             1    14    3         0.140    1.000         1.000      1.0     0.939          1.000
GLTP             2    14    6         0.290    0.958         0.917      2.0     0.958          0.958
GLTP             3    14    3         0.360    0.970         0.952      1.0     0.970          0.952
GLTP             4    14    5         0.570    1.000         1.000      2.0     0.956          1.000
IP_trans         0    13    3         0.230    1.000         1.000      1.0     0.983          0.967
IP_trans         1    14    3         0.210    0.788         0.833      2.0     0.848          0.833
IP_trans         2    12    5         0.330    0.829         1.000      2.0     0.643          0.944
IP_trans         3    13    2         0.230    0.727         0.600      2.0     0.818          0.700
IP_trans         4    12    5         0.250    0.943         0.846      3.0     0.671          0.885
LBP_BPI_CETP     0    12    3         0.420    0.963         0.917      2.0     0.870          0.792
LBP_BPI_CETP     1    12    3         0.420    1.000         1.000      2.0     0.852          0.933
LBP_BPI_CETP     2    12    5         0.500    1.000         1.000      2.0     0.971          0.944
LBP_BPI_CETP     3    12    2         0.170    0.600         0.500      1.0     0.850          0.917
LBP_BPI_CETP     4    12    4         0.420    0.750         0.750      2.0     0.781          0.750
ML               0     2    1         0.000    1.000         1.000      1.0     1.000          1.000
ML               1     2    1         0.000    1.000         1.000      1.0     0.500          0.500
ML               2     2    1         0.000    0.000         0.000      1.0     1.000          1.000
ML               3     2    1         0.000    1.000         1.000      1.0     0.000          0.000
START            0    34   11         0.710    1.000         1.000      3.0     0.866          0.817
START            1    34   13         0.710    0.974         0.972      3.0     1.000          1.000
START            2    34   13         0.680    0.864         0.755      3.0     0.908          0.836
START            3    34   11         0.820    0.984         0.981      3.0     0.980          0.981
START            4    34   11         0.590    0.976         0.980      3.0     0.875          0.827
lipocalin        0    20    7         0.550    0.989         0.929      4.0     0.879          1.000
lipocalin        1    20    7         0.550    0.923         1.000      4.0     0.819          0.889
lipocalin        2    20    9         0.600    0.990         1.000      4.0     0.899          0.900
lipocalin        3    19    4         0.530    0.933         0.769      2.0     0.733          0.692
lipocalin        4    19    6         0.630    0.987         1.000      4.0     0.923          0.929
scp2             0     9    2         0.110    1.000         1.000      2.0     0.643          0.667
scp2             1    10    5         0.000    0.800         0.800      2.0     0.600          0.700
scp2             2    10    3         0.100    0.857         1.000      1.0     0.952          1.000
scp2             3    10    5         0.400    0.880         0.929      2.0     0.960          0.929
scp2             4     9    1         0.330    1.000         1.000      1.0     0.500          0.500
```
