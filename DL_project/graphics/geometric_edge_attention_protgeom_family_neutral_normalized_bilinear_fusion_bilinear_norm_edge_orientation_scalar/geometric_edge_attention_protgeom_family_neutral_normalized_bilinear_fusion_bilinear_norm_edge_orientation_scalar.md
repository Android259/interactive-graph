# geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_edge_orientation_scalar

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_edge_orientation_scalar'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.3284      0.7803      0.6840      0.7020      0.3672      0.7645
groups_GLTP            5      0.2480      0.6640      0.6133      0.6270      0.3385      0.7462
groups_IP_trans        5      0.4000      0.8298      0.6534      0.6675      0.4333      0.7957
groups_LBP_BPI_CETP    5      0.3565      0.8553      0.7840      0.6325      0.4500      0.8085
groups_START           5      0.2462      0.7663      0.7549      0.5956      0.2812      0.8247
groups_lipocalin       5      0.2000      0.8361      0.7517      0.6242      0.2722      0.8306
groups_scp2            5      0.3294      0.7941      0.6744      0.6166      0.3765      0.8471
ALL                   35      0.3012      0.7894      0.7023      0.6379      0.3598      0.8025

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5812      0.5599     0.0688  35
max valid BA                0.6203      0.6029     0.0676  35
best valid F1               0.5535      0.5833     0.1198  35
test BA                     0.5453      0.5347     0.0740  35
test F1                     0.3297      0.3158     0.1913  35
test sensitivity            0.3012      0.2609     0.2238  35
test specificity            0.7894      0.8235     0.1809  35
test precision              0.5034      0.5000     0.1458  32
test loss                   0.7249      0.6817     0.1531  35
FPR (FP/(FP+TN))            0.2106      0.1765     0.1809  35
FNR (FN/(FN+TP))            0.6988      0.7391     0.2238  35

=== abs(sensitivity-specificity) gap: mean=0.5471 median=0.5556 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5658      0.5599     0.0437  5
  max valid BA                0.6052      0.6004     0.0340  5
  best valid F1               0.6754      0.6961     0.0540  5
  test BA                     0.5543      0.5747     0.0384  5
  test F1                     0.3543      0.4286     0.2784  5
  test sensitivity            0.3284      0.3134     0.3180  5
  test specificity            0.7803      0.8361     0.2609  5
  test precision              0.6832      0.6616     0.1087  4
  test loss                   0.7188      0.7160     0.0371  5
  FPR (FP/(FP+TN))            0.2197      0.1639     0.2609  5
  FNR (FN/(FN+TP))            0.6716      0.6866     0.3180  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5423      0.5577     0.0567  5
  max valid BA                0.5654      0.5769     0.0172  5
  best valid F1               0.5150      0.5231     0.1134  5
  test BA                     0.4560      0.4400     0.0590  5
  test F1                     0.2990      0.3000     0.1428  5
  test sensitivity            0.2480      0.2400     0.1481  5
  test specificity            0.6640      0.6400     0.0780  5
  test precision              0.3987      0.3889     0.1048  5
  test loss                   0.7452      0.7432     0.0313  5
  FPR (FP/(FP+TN))            0.3360      0.3600     0.0780  5
  FNR (FN/(FN+TP))            0.7520      0.7600     0.1481  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6145      0.6520     0.0671  5
  max valid BA                0.6885      0.6853     0.0431  5
  best valid F1               0.5994      0.5833     0.0477  5
  test BA                     0.6149      0.5893     0.0757  5
  test F1                     0.4437      0.4286     0.1372  5
  test sensitivity            0.4000      0.3913     0.1750  5
  test specificity            0.8298      0.8085     0.0542  5
  test precision              0.5281      0.5556     0.0897  5
  test loss                   0.6283      0.6292     0.0177  5
  FPR (FP/(FP+TN))            0.1702      0.1915     0.0542  5
  FNR (FN/(FN+TP))            0.6000      0.6087     0.1750  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6293      0.6410     0.0631  5
  max valid BA                0.6666      0.6729     0.0811  5
  best valid F1               0.5231      0.5902     0.1863  5
  test BA                     0.6059      0.5661     0.0812  5
  test F1                     0.4236      0.4000     0.1388  5
  test sensitivity            0.3565      0.3913     0.1549  5
  test specificity            0.8553      0.9149     0.1711  5
  test precision              0.6180      0.6667     0.1798  5
  test loss                   0.7290      0.5899     0.2033  5
  FPR (FP/(FP+TN))            0.1447      0.0851     0.1711  5
  FNR (FN/(FN+TP))            0.6435      0.6087     0.1549  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5530      0.5073     0.0821  5
  max valid BA                0.6070      0.5701     0.0738  5
  best valid F1               0.6120      0.6011     0.0496  5
  test BA                     0.5062      0.5000     0.0572  5
  test F1                     0.2278      0.1860     0.2348  5
  test sensitivity            0.2462      0.1231     0.3647  5
  test specificity            0.7663      0.8539     0.2774  5
  test precision              0.3978      0.4301     0.1229  4
  test loss                   0.8970      0.7079     0.3063  5
  FPR (FP/(FP+TN))            0.2337      0.1461     0.2774  5
  FNR (FN/(FN+TP))            0.7538      0.8769     0.3647  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5514      0.5486     0.0349  5
  max valid BA                0.5625      0.5556     0.0431  5
  best valid F1               0.4198      0.3898     0.0936  5
  test BA                     0.5181      0.5139     0.0126  5
  test F1                     0.2177      0.2692     0.1592  5
  test sensitivity            0.2000      0.1944     0.1948  5
  test specificity            0.8361      0.8750     0.1888  5
  test precision              0.4350      0.4375     0.0676  5
  test loss                   0.6973      0.6766     0.0751  5
  FPR (FP/(FP+TN))            0.1639      0.1250     0.1888  5
  FNR (FN/(FN+TP))            0.8000      0.8056     0.1948  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6118      0.5735     0.0945  5
  max valid BA                0.6471      0.6176     0.0615  5
  best valid F1               0.5300      0.4848     0.0798  5
  test BA                     0.5618      0.5588     0.0446  5
  test F1                     0.3418      0.4138     0.1916  5
  test sensitivity            0.3294      0.3529     0.1977  5
  test specificity            0.7941      0.8235     0.1690  5
  test precision              0.4717      0.4559     0.1003  4
  test loss                   0.6590      0.6577     0.0153  5
  FPR (FP/(FP+TN))            0.2059      0.1765     0.1690  5
  FNR (FN/(FN+TP))            0.6706      0.6471     0.1977  5
```

## AUC vs chemistry null model, in-sample increment

