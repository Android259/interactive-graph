# structural_pretrain_family_unfrozen_protunion14

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'structural_pretrain_family_unfrozen_protunion14'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.8713      0.8102      0.9441      0.8514      0.9088      0.8923
groups_GLTP            5      0.9667      0.9318      0.9550      0.9733      1.0000      1.0000
groups_IP_trans        5      0.8133      0.7592      0.8705      0.7900      1.0000      0.9118
groups_LBP_BPI_CETP    5      0.8000      0.8511      0.7158      0.8623      1.0000      0.9556
groups_START           5      0.8965      0.9176      0.9448      0.8465      1.0000      0.9272
groups_lipocalin       5      0.9214      0.8929      0.9102      0.8780      0.9143      0.9089
groups_scp2            5      0.9200      0.7743      0.8430      0.7392      0.9500      0.8033
ALL                   35      0.8842      0.8482      0.8834      0.8487      0.9676      0.9142

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.9206      0.9375     0.0829  35
max valid BA                0.9409      0.9643     0.0672  35
best valid F1               0.9042      0.9231     0.0969  35
test BA                     0.8662      0.8874     0.1068  35
test AUC                    0.9086      0.9446     0.1085  35
test AUC in-protein         0.9148      0.9745     0.1440  30
  (proteins averaged)       1.2571      1.0000     0.7005  35
test AUC in-protein (pairs)      0.9141      0.9604     0.1251  35
  (proteins contributing)      2.5143      2.0000     1.0947  35
test F1                     0.7828      0.8571     0.1866  35
test sensitivity            0.8842      1.0000     0.1646  35
test specificity            0.8482      0.8571     0.1335  35
test precision              0.7418      0.7647     0.2225  35
test loss                   0.4130      0.3800     0.3173  35
FPR (FP/(FP+TN))            0.1518      0.1429     0.1335  35
FNR (FN/(FN+TP))            0.1158      0.0000     0.1646  35

=== abs(sensitivity-specificity) gap: mean=0.1477 median=0.1000 n=35 ===
sensitivity std across seeds (by group): mean=0.1513 median=0.1141 n=7
specificity std across seeds (by group): mean=0.1153 median=0.1090 n=7

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8967      0.8638     0.0698  5
  max valid BA                0.9005      0.8638     0.0746  5
  best valid F1               0.8649      0.8333     0.0910  5
  test BA                     0.8408      0.8365     0.0528  5
  test AUC                    0.8928      0.8963     0.0466  5
  test AUC in-protein         0.9323      0.9333     0.0515  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.9368      0.9412     0.0373  5
    (proteins contributing)      4.0000      4.0000     0.7071  5
  test F1                     0.7762      0.7742     0.0614  5
  test sensitivity            0.8713      0.9231     0.1191  5
  test specificity            0.8102      0.8000     0.0461  5
  test precision              0.7060      0.7059     0.0522  5
  test loss                   0.4573      0.4124     0.1602  5
  FPR (FP/(FP+TN))            0.1898      0.2000     0.0461  5
  FNR (FN/(FN+TP))            0.1287      0.0769     0.1191  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9900      1.0000     0.0224  5
  max valid BA                1.0000      1.0000     0.0000  5
  best valid F1               1.0000      1.0000     0.0000  5
  test BA                     0.9492      1.0000     0.0903  5
  test AUC                    0.9856      1.0000     0.0201  5
  test AUC in-protein         0.9780      1.0000     0.0306  5
    (proteins averaged)       1.4000      1.0000     0.5477  5
  test AUC in-protein (pairs)      0.9738      1.0000     0.0380  5
    (proteins contributing)      1.6000      2.0000     0.5477  5
  test F1                     0.9253      1.0000     0.1069  5
  test sensitivity            0.9667      1.0000     0.0745  5
  test specificity            0.9318      1.0000     0.1090  5
  test precision              0.8929      1.0000     0.1473  5
  test loss                   0.2743      0.0897     0.3179  5
  FPR (FP/(FP+TN))            0.0682      0.0000     0.1090  5
  FNR (FN/(FN+TP))            0.0333      0.0000     0.0745  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9043      0.9000     0.0225  5
  max valid BA                0.9559      0.9545     0.0512  5
  best valid F1               0.9029      0.8571     0.0917  5
  test BA                     0.7863      0.7273     0.1444  5
  test AUC                    0.8523      0.8485     0.1200  5
  test AUC in-protein         0.7655      0.8167     0.2410  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.8503      0.8889     0.1508  5
    (proteins contributing)      2.0000      2.0000     0.7071  5
  test F1                     0.6332      0.5000     0.2325  5
  test sensitivity            0.8133      1.0000     0.2724  5
  test specificity            0.7592      0.8571     0.1822  5
  test precision              0.5800      0.6667     0.2459  5
  test loss                   0.6850      0.5622     0.6006  5
  FPR (FP/(FP+TN))            0.2408      0.1429     0.1822  5
  FNR (FN/(FN+TP))            0.1867      0.0000     0.2724  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9778      1.0000     0.0304  5
  max valid BA                0.9778      1.0000     0.0304  5
  best valid F1               0.9429      1.0000     0.0782  5
  test BA                     0.8256      0.8333     0.1591  5
  test AUC                    0.8450      1.0000     0.2124  5
  test AUC in-protein         0.8667      1.0000     0.2173  5
    (proteins averaged)       1.0000      1.0000     0.0000  5
  test AUC in-protein (pairs)      0.8250      1.0000     0.2437  5
    (proteins contributing)      1.8000      2.0000     0.4472  5
  test F1                     0.7048      0.6667     0.2506  5
  test sensitivity            0.8000      1.0000     0.2739  5
  test specificity            0.8511      0.8889     0.1602  5
  test precision              0.7000      0.7500     0.3260  5
  test loss                   0.4072      0.3818     0.2635  5
  FPR (FP/(FP+TN))            0.1489      0.1111     0.1602  5
  FNR (FN/(FN+TP))            0.2000      0.0000     0.2739  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.9426      0.9545     0.0333  5
  max valid BA                0.9636      0.9773     0.0306  5
  best valid F1               0.9451      0.9600     0.0422  5
  test BA                     0.9071      0.8874     0.0555  5
  test AUC                    0.9686      0.9802     0.0408  5
  test AUC in-protein         0.9594      0.9740     0.0485  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.9464      0.9720     0.0731  5
    (proteins contributing)      3.0000      3.0000     0.0000  5
  test F1                     0.8750      0.8571     0.0646  5
  test sensitivity            0.8965      0.8462     0.0952  5
  test specificity            0.9176      0.9130     0.0414  5
  test precision              0.8574      0.8667     0.0550  5
  test loss                   0.2952      0.2396     0.2294  5
  FPR (FP/(FP+TN))            0.0824      0.0870     0.0414  5
  FNR (FN/(FN+TP))            0.1035      0.1538     0.0952  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8914      0.9286     0.0886  5
  max valid BA                0.9116      0.9545     0.0782  5
  best valid F1               0.8627      0.8889     0.0862  5
  test BA                     0.9071      0.9091     0.0856  5
  test AUC                    0.9528      0.9744     0.0575  5
  test AUC in-protein         0.9000      1.0000     0.1732  3
    (proteins averaged)       1.0000      1.0000     1.0000  5
  test AUC in-protein (pairs)      0.9538      1.0000     0.1032  5
    (proteins contributing)      3.6000      4.0000     0.8944  5
  test F1                     0.8560      0.9000     0.1522  5
  test sensitivity            0.9214      1.0000     0.1141  5
  test specificity            0.8929      0.9231     0.0829  5
  test precision              0.8065      0.8571     0.1848  5
  test loss                   0.2424      0.1838     0.1532  5
  FPR (FP/(FP+TN))            0.1071      0.0769     0.0829  5
  FNR (FN/(FN+TP))            0.0786      0.0000     0.1141  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8417      0.8750     0.1484  5
  max valid BA                0.8767      0.8750     0.0836  5
  best valid F1               0.8111      0.7500     0.1323  5
  test BA                     0.8471      0.8571     0.0728  5
  test AUC                    0.8629      0.8571     0.0818  5
  test AUC in-protein         1.0000      1.0000     0.0000  3
    (proteins averaged)       0.6000      1.0000     0.5477  5
  test AUC in-protein (pairs)      0.9124      0.9286     0.0929  5
    (proteins contributing)      1.6000      2.0000     0.5477  5
  test F1                     0.7092      0.8000     0.2267  5
  test sensitivity            0.9200      1.0000     0.1095  5
  test specificity            0.7743      0.8000     0.1853  5
  test precision              0.6500      0.7500     0.3082  5
  test loss                   0.5295      0.5126     0.1822  5
  FPR (FP/(FP+TN))            0.2257      0.2000     0.1853  5
  FNR (FN/(FN+TP))            0.0800      0.0000     0.1095  5
```

## AUC vs chemistry null model, in-sample increment

Failed: ValueError: Unknown parameter: --family_only -- rerun for the full output: `python3 analysis/full_label_report.py --label structural_pretrain_family_unfrozen_protunion14 --seeds=0,1,2,3,4`
