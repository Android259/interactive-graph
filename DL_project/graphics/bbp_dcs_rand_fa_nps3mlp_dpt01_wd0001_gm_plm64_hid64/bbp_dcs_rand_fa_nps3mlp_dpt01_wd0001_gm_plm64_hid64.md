# bbp_dcs_rand_fa_nps3mlp_dpt01_wd0001_gm_plm64_hid64

## Summary (analysis/summarize_label.py)

```
Summary: 'bbp_dcs_rand_fa_nps3mlp_dpt01_wd0001_gm_plm64_hid64'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.6567      0.4033      0.8766      0.8017      0.7284      0.4516
groups_GLTP            5      0.2160      0.7920      0.6606      0.6664      0.2692      0.8308
groups_IP_trans        5      0.4957      0.7489      0.7862      0.7231      0.5333      0.7915
groups_LBP_BPI_CETP    5      0.3913      0.8681      0.8366      0.7740      0.4500      0.8638
groups_START           5      0.5846      0.5101      0.9338      0.8328      0.6094      0.5685
groups_lipocalin       5      0.1389      0.8250      0.7939      0.6960      0.1556      0.8250
groups_scp2            5      0.4824      0.6118      0.8688      0.8213      0.5882      0.6588
ALL                   35      0.4236      0.6799      0.8224      0.7593      0.4763      0.7129

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5946      0.5962     0.0772  35
max valid BA                0.6297      0.6324     0.0774  35
best valid F1               0.5519      0.5909     0.1393  35
test BA                     0.5518      0.5546     0.0840  35
test F1                     0.4081      0.4242     0.1849  35
test sensitivity            0.4236      0.4000     0.2575  35
test specificity            0.6799      0.6806     0.2206  35
test precision              0.4857      0.4613     0.1676  34
test loss                   1.0611      0.8357     0.6940  35
FPR (FP/(FP+TN))            0.3201      0.3194     0.2206  35
FNR (FN/(FN+TP))            0.5764      0.6000     0.2575  35

=== abs(sensitivity-specificity) gap: mean=0.4390 median=0.3824 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5900      0.6080     0.0779  5
  max valid BA                0.6259      0.6270     0.0403  5
  best valid F1               0.7166      0.7081     0.0274  5
  test BA                     0.5300      0.5729     0.0756  5
  test F1                     0.5850      0.6581     0.1264  5
  test sensitivity            0.6567      0.7313     0.2025  5
  test specificity            0.4033      0.3934     0.1241  5
  test precision              0.5390      0.5700     0.0646  5
  test loss                   0.7929      0.8432     0.0808  5
  FPR (FP/(FP+TN))            0.5967      0.6066     0.1241  5
  FNR (FN/(FN+TP))            0.3433      0.2687     0.2025  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5577     0.0399  5
  max valid BA                0.5577      0.5577     0.0408  5
  best valid F1               0.4643      0.4800     0.0863  5
  test BA                     0.5040      0.4600     0.1135  5
  test F1                     0.2851      0.3000     0.2051  5
  test sensitivity            0.2160      0.2400     0.1486  5
  test specificity            0.7920      0.7600     0.2028  5
  test precision              0.5472      0.4000     0.3019  4
  test loss                   0.9096      0.7642     0.3324  5
  FPR (FP/(FP+TN))            0.2080      0.2400     0.2028  5
  FNR (FN/(FN+TP))            0.7840      0.7600     0.1486  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6624      0.6964     0.0643  5
  max valid BA                0.6937      0.7163     0.0533  5
  best valid F1               0.6035      0.6275     0.0555  5
  test BA                     0.6223      0.6031     0.0728  5
  test F1                     0.4495      0.5161     0.1768  5
  test sensitivity            0.4957      0.5652     0.3144  5
  test specificity            0.7489      0.8298     0.2146  5
  test precision              0.5511      0.5000     0.1344  5
  test loss                   0.6842      0.6772     0.0767  5
  FPR (FP/(FP+TN))            0.2511      0.1702     0.2146  5
  FNR (FN/(FN+TP))            0.5043      0.4348     0.3144  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6569      0.6449     0.0385  5
  max valid BA                0.7090      0.7070     0.0164  5
  best valid F1               0.6094      0.6000     0.0264  5
  test BA                     0.6297      0.6203     0.0718  5
  test F1                     0.4479      0.4242     0.1480  5
  test sensitivity            0.3913      0.3043     0.2062  5
  test specificity            0.8681      0.8936     0.1150  5
  test precision              0.6383      0.6818     0.1330  5
  test loss                   1.0102      0.8357     0.4315  5
  FPR (FP/(FP+TN))            0.1319      0.1064     0.1150  5
  FNR (FN/(FN+TP))            0.6087      0.6957     0.2062  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5890      0.5937     0.0750  5
  max valid BA                0.6299      0.5959     0.0695  5
  best valid F1               0.6070      0.5848     0.0688  5
  test BA                     0.5474      0.5312     0.0577  5
  test F1                     0.5104      0.5153     0.0935  5
  test sensitivity            0.5846      0.6154     0.1699  5
  test specificity            0.5101      0.5393     0.1275  5
  test precision              0.4632      0.4533     0.0570  5
  test loss                   1.2346      1.0100     0.5030  5
  FPR (FP/(FP+TN))            0.4899      0.4607     0.1275  5
  FNR (FN/(FN+TP))            0.4154      0.3846     0.1699  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4903      0.5000     0.0280  5
  max valid BA                0.5181      0.5069     0.0404  5
  best valid F1               0.2918      0.2712     0.0838  5
  test BA                     0.4819      0.4861     0.0335  5
  test F1                     0.1753      0.1600     0.0935  5
  test sensitivity            0.1389      0.1111     0.0921  5
  test specificity            0.8250      0.8333     0.1014  5
  test precision              0.2923      0.2857     0.1025  5
  test loss                   1.7421      0.9449     1.5821  5
  FPR (FP/(FP+TN))            0.1750      0.1667     0.1014  5
  FNR (FN/(FN+TP))            0.8611      0.8889     0.0921  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6235      0.6324     0.0566  5
  max valid BA                0.6735      0.6765     0.0242  5
  best valid F1               0.5708      0.5714     0.0367  5
  test BA                     0.5471      0.5441     0.0554  5
  test F1                     0.4038      0.4516     0.1378  5
  test sensitivity            0.4824      0.5294     0.2331  5
  test specificity            0.6118      0.5588     0.2042  5
  test precision              0.3812      0.3636     0.0830  5
  test loss                   1.0542      1.0071     0.3343  5
  FPR (FP/(FP+TN))            0.3882      0.4412     0.2042  5
  FNR (FN/(FN+TP))            0.5176      0.4706     0.2331  5
```

## AUC vs chemistry null model, in-sample increment

Failed: no checkpoints scored -- rerun for the full output: `python3 analysis/full_label_report.py --label bbp_dcs_rand_fa_nps3mlp_dpt01_wd0001_gm_plm64_hid64 --seeds=0,1,2,3,4`
