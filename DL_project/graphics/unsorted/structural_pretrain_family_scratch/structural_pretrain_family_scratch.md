# structural_pretrain_family_scratch

## Summary (analysis/summarize_label.py)

```
Summary: 'structural_pretrain_family_scratch'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.8895      0.7678      0.9355      0.8408      0.9396      0.8679
groups_GLTP            5      0.9667      0.8868      0.9545      0.9247      0.9667      1.0000
groups_IP_trans        5      0.9600      0.5018      0.8433      0.6747      1.0000      0.7568
groups_LBP_BPI_CETP    5      0.8000      0.8175      0.8311      0.8491      1.0000      0.9306
groups_ML              5      0.6000      0.6000      0.0000      1.0000      0.0000      1.0000
groups_OSBP            5      0.2500      0.8000         n/a         n/a         n/a         n/a
groups_START           5      0.8503      0.8994      0.9540      0.8526      1.0000      0.9188
groups_lipocalin       5      0.9214      0.9090      0.9588      0.8662      0.9429      0.9201
groups_scp2            5      0.9600      0.6943      0.9272      0.6434      0.9500      0.8033
ALL                   45      0.8123      0.7641      0.8895      0.8127      0.9443      0.8886

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.8981      0.9286     0.1051  36
max valid BA                0.9164      0.9444     0.0980  36
best valid F1               0.7607      0.8844     0.3287  42
test BA                     0.7855      0.8042     0.1648  44
test AUC                    0.8824      0.9613     0.2200  44
test AUC in-protein         0.9025      0.9684     0.1502  30
  (proteins averaged)       0.9778      1.0000     0.8115  45
test AUC in-protein (pairs)      0.8807      0.9615     0.2285  42
  (proteins contributing)      2.1111      2.0000     1.2472  45
test F1                     0.6720      0.7303     0.2895  44
test sensitivity            0.8123      1.0000     0.3189  44
test specificity            0.7641      0.8571     0.2674  45
test precision              0.6783      0.6667     0.2055  39
test loss                   0.4762      0.4760     0.2559  45
FPR (FP/(FP+TN))            0.2359      0.1429     0.2674  45
FNR (FN/(FN+TP))            0.1877      0.0000     0.3189  44

=== abs(sensitivity-specificity) gap: mean=0.3333 median=0.1429 n=44 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8910      0.8638     0.0660  5
  max valid BA                0.9038      0.8638     0.0721  5
  best valid F1               0.8664      0.8333     0.0929  5
  test BA                     0.8287      0.8365     0.0555  5
  test AUC                    0.8932      0.8782     0.0309  5
  test AUC in-protein         0.9346      0.9500     0.0623  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.9274      0.9070     0.0415  5
    (proteins contributing)      4.0000      4.0000     0.7071  5
  test F1                     0.7610      0.7692     0.0551  5
  test sensitivity            0.8895      0.9091     0.0867  5
  test specificity            0.7678      0.7500     0.0297  5
  test precision              0.6655      0.6667     0.0361  5
  test loss                   0.4378      0.4238     0.0782  5
  FPR (FP/(FP+TN))            0.2322      0.2500     0.0297  5
  FNR (FN/(FN+TP))            0.1105      0.0909     0.0867  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9833      1.0000     0.0373  5
  max valid BA                0.9833      1.0000     0.0373  5
  best valid F1               0.9818      1.0000     0.0407  5
  test BA                     0.9267      0.9545     0.1130  5
  test AUC                    0.9773      1.0000     0.0363  5
  test AUC in-protein         0.9780      1.0000     0.0306  5
    (proteins averaged)       1.4000      1.0000     0.5477  5
  test AUC in-protein (pairs)      0.9738      1.0000     0.0380  5
    (proteins contributing)      1.6000      2.0000     0.5477  5
  test F1                     0.8921      0.8889     0.1185  5
  test sensitivity            0.9667      1.0000     0.0745  5
  test specificity            0.8868      0.9091     0.1540  5
  test precision              0.8350      0.8000     0.1636  5
  test loss                   0.3982      0.2180     0.4926  5
  FPR (FP/(FP+TN))            0.1132      0.0909     0.1540  5
  FNR (FN/(FN+TP))            0.0333      0.0000     0.0745  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8177      0.8125     0.0441  5
  max valid BA                0.8784      0.8750     0.0732  5
  best valid F1               0.7714      0.8000     0.0990  5
  test BA                     0.7309      0.7273     0.0575  5
  test AUC                    0.8452      0.8286     0.1397  5
  test AUC in-protein         0.7238      0.7333     0.2398  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.8337      0.8462     0.1462  5
    (proteins contributing)      2.0000      2.0000     0.7071  5
  test F1                     0.5788      0.6000     0.1308  5
  test sensitivity            0.9600      1.0000     0.0894  5
  test specificity            0.5018      0.4545     0.1628  5
  test precision              0.4357      0.4286     0.1601  5
  test loss                   0.6472      0.6127     0.1561  5
  FPR (FP/(FP+TN))            0.4982      0.5455     0.1628  5
  FNR (FN/(FN+TP))            0.0400      0.0000     0.0894  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9653      0.9444     0.0318  5
  max valid BA                0.9653      0.9444     0.0318  5
  best valid F1               0.9206      0.8889     0.0736  5
  test BA                     0.8088      0.8333     0.1353  5
  test AUC                    0.8401      0.9630     0.2084  5
  test AUC in-protein         0.8333      0.8333     0.2041  5
    (proteins averaged)       1.0000      1.0000     0.0000  5
  test AUC in-protein (pairs)      0.8208      0.9167     0.2203  5
    (proteins contributing)      1.8000      2.0000     0.4472  5
  test F1                     0.6809      0.6667     0.2087  5
  test sensitivity            0.8000      1.0000     0.2739  5
  test specificity            0.8175      0.8571     0.0909  5
  test precision              0.6167      0.6667     0.2007  5
  test loss                   0.4338      0.5752     0.2544  5
  FPR (FP/(FP+TN))            0.1825      0.1429     0.0909  5
  FNR (FN/(FN+TP))            0.2000      0.0000     0.2739  5

groups_ML (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5000      0.5000     0.0000  1
  max valid BA                0.5000      0.5000     0.0000  1
  best valid F1               0.0000      0.0000     0.0000  4
  test BA                     0.6000      0.5000     0.2236  5
  test AUC                    0.6000      1.0000     0.5477  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.6000      1.0000     0.5477  5
    (proteins contributing)      1.0000      1.0000     0.0000  5
  test F1                     0.4667      0.6667     0.4472  5
  test sensitivity            0.6000      1.0000     0.5477  5
  test specificity            0.6000      1.0000     0.5477  5
  test precision              0.6667      0.5000     0.2887  3
  test loss                   0.6938      0.6942     0.0023  5
  FPR (FP/(FP+TN))            0.4000      0.0000     0.5477  5
  FNR (FN/(FN+TP))            0.4000      0.0000     0.5477  5

groups_OSBP (n=5):
  metric                        mean      median        std  n
  best valid F1               0.3333      0.0000     0.5774  3
  test BA                     0.5000      0.5000     0.0000  4
  test AUC                    1.0000      1.0000     0.0000  4
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      1.0000      1.0000     0.0000  2
    (proteins contributing)      0.4000      0.0000     0.5477  5
  test F1                     0.1667      0.0000     0.3333  4
  test sensitivity            0.2500      0.0000     0.5000  4
  test specificity            0.8000      1.0000     0.4472  5
  test precision              0.5000      0.5000     0.0000  1
  test loss                   0.6899      0.6922     0.0056  5
  FPR (FP/(FP+TN))            0.2000      0.0000     0.4472  5
  FNR (FN/(FN+TP))            0.7500      1.0000     0.5000  4

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9505      0.9545     0.0293  5
  max valid BA                0.9594      0.9773     0.0254  5
  best valid F1               0.9298      0.9524     0.0385  5
  test BA                     0.8749      0.8656     0.0765  5
  test AUC                    0.9662      0.9763     0.0367  5
  test AUC in-protein         0.9500      0.9636     0.0522  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.9371      0.9626     0.0784  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.8374      0.8182     0.0893  5
  test sensitivity            0.8503      0.8182     0.0881  5
  test specificity            0.8994      0.9130     0.0796  5
  test precision              0.8273      0.8182     0.1024  5
  test loss                   0.2085      0.1891     0.1110  5
  FPR (FP/(FP+TN))            0.1006      0.0870     0.0796  5
  FNR (FN/(FN+TP))            0.1497      0.1818     0.0881  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8816      0.9286     0.1153  5
  max valid BA                0.9315      0.9545     0.0704  5
  best valid F1               0.9085      0.9231     0.0852  5
  test BA                     0.9152      0.9545     0.0669  5
  test AUC                    0.9584      0.9596     0.0302  5
  test AUC in-protein         0.9000      1.0000     0.1732  3
    (proteins averaged)       1.0000      1.0000     1.0000  5
  test AUC in-protein (pairs)      0.9396      1.0000     0.1001  5
    (proteins contributing)      3.6000      4.0000     0.8944  5
  test F1                     0.8655      0.9231     0.1164  5
  test sensitivity            0.9214      1.0000     0.1141  5
  test specificity            0.9090      0.9231     0.0244  5
  test precision              0.8179      0.8571     0.1230  5
  test loss                   0.2635      0.1826     0.1558  5
  FPR (FP/(FP+TN))            0.0910      0.0769     0.0244  5
  FNR (FN/(FN+TP))            0.0786      0.0000     0.1141  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8767      0.8750     0.0836  5
  max valid BA                0.8767      0.8750     0.0836  5
  best valid F1               0.8111      0.7500     0.1323  5
  test BA                     0.8271      0.8000     0.0682  5
  test AUC                    0.8851      0.8800     0.0888  5
  test AUC in-protein         1.0000      1.0000     0.0000  3
    (proteins averaged)       0.6000      1.0000     0.5477  5
  test AUC in-protein (pairs)      0.9657      1.0000     0.0480  5
    (proteins contributing)      1.6000      2.0000     0.5477  5
  test F1                     0.6981      0.8000     0.2168  5
  test sensitivity            0.9600      1.0000     0.0894  5
  test specificity            0.6943      0.7143     0.1455  5
  test precision              0.5929      0.7143     0.2476  5
  test loss                   0.5133      0.4625     0.1836  5
  FPR (FP/(FP+TN))            0.3057      0.2857     0.1455  5
  FNR (FN/(FN+TP))            0.0400      0.0000     0.0894  5
```

## AUC vs chemistry null model, same rows (analysis/solo_family_report.py)

Not analysis/full_label_report.py: its null model reconstructs an EXCLUDED-family split, the opposite of --family_only (restricts to one family, splits randomly inside it) -- see this function's own docstring.

```
fam           seed  rows  pos seen_in_train  net_AUC net_AUC_pairs proteins  null_AUC null_AUC_pairs
CRAL-TRIO        0    36   11         0.690    0.924         0.894      3.0     0.902          0.941
CRAL-TRIO        1    37   13         0.680    0.878         0.990      4.0     0.929          1.000
CRAL-TRIO        2    36   13         0.810    0.873         0.897      4.0     0.799          0.839
CRAL-TRIO        3    38   13         0.820    0.929         0.949      5.0     0.874          0.943
CRAL-TRIO        4    37   13         0.840    0.862         0.907      4.0     0.902          0.983
GLTP             0    14    4         0.290    1.000         1.000      2.0     1.000          1.000
GLTP             1    14    3         0.140    1.000         1.000      1.0     0.939          1.000
GLTP             2    14    6         0.290    0.917         0.917      2.0     0.958          0.958
GLTP             3    14    3         0.360    0.970         0.952      1.0     0.970          0.952
GLTP             4    14    5         0.570    1.000         1.000      2.0     0.956          1.000
IP_trans         0    13    3         0.230    1.000         1.000      1.0     0.983          0.967
IP_trans         1    14    3         0.210    0.818         0.833      2.0     0.848          0.833
IP_trans         2    12    5         0.330    0.829         0.889      2.0     0.643          0.944
IP_trans         3    13    2         0.230    0.636         0.600      2.0     0.818          0.700
IP_trans         4    12    5         0.250    0.943         0.846      3.0     0.671          0.885
LBP_BPI_CETP     0    12    3         0.420    0.963         0.917      2.0     0.870          0.792
LBP_BPI_CETP     1    12    3         0.420    1.000         1.000      2.0     0.852          0.933
LBP_BPI_CETP     2    12    5         0.500    1.000         1.000      2.0     0.971          0.944
LBP_BPI_CETP     3    12    2         0.170    0.550         0.500      1.0     0.850          0.917
LBP_BPI_CETP     4    12    4         0.420    0.688         0.688      2.0     0.781          0.750
ML               0     2    1         0.000    1.000         1.000      1.0     1.000          1.000
ML               1     2    1         0.000    0.000         0.000      1.0     0.500          0.500
ML               2     2    1         0.000    1.000         1.000      1.0     1.000          1.000
ML               3     2    1         0.000    1.000         1.000      1.0     0.000          0.000
ML               4     2    1         0.000    0.000         0.000      1.0     0.000          0.000
OSBP             0     2    1         0.500    1.000         1.000      1.0     1.000          1.000
OSBP             1     2    1         0.000    1.000         1.000      1.0     1.000          1.000
OSBP             2     1    0           nan      nan           nan      0.0       nan            nan
OSBP             3     2    1         0.000    1.000           nan      0.0     0.000            nan
OSBP             4     2    1         0.000    1.000           nan      0.0     0.000            nan
START            0    34   11         0.710    1.000         1.000      3.0     0.866          0.817
START            1    34   13         0.710    0.985         0.963      3.0     1.000          1.000
START            2    34   13         0.680    0.905         0.800      3.0     0.908          0.836
START            3    34   11         0.820    0.964         0.963      3.0     0.980          0.981
START            4    34   11         0.590    0.976         0.960      3.0     0.875          0.827
lipocalin        0    20    7         0.550    0.989         0.929      4.0     0.879          1.000
lipocalin        1    20    7         0.550    0.923         1.000      4.0     0.819          0.889
lipocalin        2    20    9         0.600    0.960         1.000      4.0     0.899          0.900
lipocalin        3    19    4         0.530    0.933         0.769      2.0     0.733          0.692
lipocalin        4    19    6         0.630    0.987         1.000      4.0     0.923          0.929
scp2             0     9    2         0.110    0.929         1.000      2.0     0.643          0.667
scp2             1    10    5         0.000    0.880         0.900      2.0     0.600          0.700
scp2             2    10    3         0.100    0.857         1.000      1.0     0.952          1.000
scp2             3    10    5         0.400    0.760         0.929      2.0     0.960          0.929
scp2             4     9    1         0.330    1.000         1.000      1.0     0.500          0.500
```
