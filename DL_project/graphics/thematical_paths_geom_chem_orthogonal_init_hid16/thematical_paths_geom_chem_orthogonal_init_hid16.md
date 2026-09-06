# thematical_paths_geom_chem_orthogonal_init_hid16

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'thematical_paths_geom_chem_orthogonal_init_hid16'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.2000      0.8689      0.7337      0.8775      0.2209      0.8613
groups_GLTP            5      0.4880      0.7920      0.8462      0.7921      0.5923      0.7462
groups_IP_trans        5      0.3739      0.6936      0.8336      0.8160      0.4500      0.6936
groups_LBP_BPI_CETP    5      0.3478      0.9021      0.9191      0.8459      0.4167      0.8936
groups_START           5      0.2062      0.8270      0.4805      0.8686      0.2000      0.8539
groups_lipocalin       5      0.4722      0.7111      0.8740      0.8116      0.4889      0.7694
groups_scp2            5      0.2824      0.7882      0.7905      0.7671      0.3412      0.8294
ALL                   35      0.3386      0.7976      0.7825      0.8255      0.3871      0.8068

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5972      0.5962     0.0740  35
max valid BA                0.6506      0.6445     0.0832  35
best valid F1               0.5702      0.5778     0.1170  35
test BA                     0.5681      0.5550     0.0816  35
test F1                     0.3634      0.3939     0.2088  35
test sensitivity            0.3386      0.3333     0.2331  35
test specificity            0.7976      0.8511     0.1808  35
test precision              0.5124      0.5116     0.2265  33
test loss                   0.8208      0.7229     0.2567  35
FPR (FP/(FP+TN))            0.2024      0.1489     0.1808  35
FNR (FN/(FN+TP))            0.6614      0.6667     0.2331  35

=== abs(sensitivity-specificity) gap: mean=0.5263 median=0.5139 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5411      0.5089     0.0530  5
  max valid BA                0.5700      0.5791     0.0634  5
  best valid F1               0.4912      0.4404     0.1460  5
  test BA                     0.5344      0.5382     0.0619  5
  test F1                     0.2620      0.3297     0.2506  5
  test sensitivity            0.2000      0.2239     0.1990  5
  test specificity            0.8689      0.8525     0.0875  5
  test precision              0.4934      0.6458     0.3298  4
  test loss                   1.1479      0.9492     0.4399  5
  FPR (FP/(FP+TN))            0.1311      0.1475     0.0875  5
  FNR (FN/(FN+TP))            0.8000      0.7761     0.1990  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6654      0.6346     0.0727  5
  max valid BA                0.7538      0.7308     0.0750  5
  best valid F1               0.7379      0.7541     0.1089  5
  test BA                     0.6400      0.6200     0.0800  5
  test F1                     0.5495      0.5366     0.1778  5
  test sensitivity            0.4880      0.4400     0.2252  5
  test specificity            0.7920      0.8000     0.1927  5
  test precision              0.7611      0.6875     0.1646  5
  test loss                   0.7832      0.7885     0.1847  5
  FPR (FP/(FP+TN))            0.2080      0.2000     0.1927  5
  FNR (FN/(FN+TP))            0.5120      0.5600     0.2252  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5718      0.5824     0.0330  5
  max valid BA                0.6628      0.6520     0.0396  5
  best valid F1               0.5581      0.5667     0.0527  5
  test BA                     0.5338      0.5504     0.0639  5
  test F1                     0.3216      0.3939     0.1989  5
  test sensitivity            0.3739      0.3913     0.2958  5
  test specificity            0.6936      0.8511     0.3056  5
  test precision              0.3596      0.3617     0.2338  5
  test loss                   0.8421      0.7620     0.2432  5
  FPR (FP/(FP+TN))            0.3064      0.1489     0.3056  5
  FNR (FN/(FN+TP))            0.6261      0.6087     0.2958  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6551      0.6964     0.0918  5
  max valid BA                0.6863      0.6964     0.0810  5
  best valid F1               0.5684      0.5909     0.1372  5
  test BA                     0.6250      0.6637     0.0818  5
  test F1                     0.4270      0.5143     0.1827  5
  test sensitivity            0.3478      0.3913     0.1895  5
  test specificity            0.9021      0.9149     0.0387  5
  test precision              0.6091      0.6111     0.1110  5
  test loss                   0.7006      0.7338     0.1846  5
  FPR (FP/(FP+TN))            0.0979      0.0851     0.0387  5
  FNR (FN/(FN+TP))            0.6522      0.6087     0.1895  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5270      0.5119     0.0273  5
  max valid BA                0.5559      0.5690     0.0296  5
  best valid F1               0.5299      0.5644     0.0823  5
  test BA                     0.5166      0.5021     0.0342  5
  test F1                     0.2218      0.1839     0.2229  5
  test sensitivity            0.2062      0.1231     0.2541  5
  test specificity            0.8270      0.8652     0.2286  5
  test precision              0.4770      0.4722     0.0993  4
  test loss                   0.7425      0.6963     0.0727  5
  FPR (FP/(FP+TN))            0.1730      0.1348     0.2286  5
  FNR (FN/(FN+TP))            0.7938      0.8769     0.2541  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6347      0.6458     0.0638  5
  max valid BA                0.6722      0.6667     0.0550  5
  best valid F1               0.5678      0.5600     0.0625  5
  test BA                     0.5917      0.6319     0.0780  5
  test F1                     0.4520      0.4800     0.1134  5
  test sensitivity            0.4722      0.4444     0.1944  5
  test specificity            0.7111      0.7083     0.1730  5
  test precision              0.4992      0.4407     0.2123  5
  test loss                   0.8351      0.7205     0.2267  5
  FPR (FP/(FP+TN))            0.2889      0.2917     0.1730  5
  FNR (FN/(FN+TP))            0.5278      0.5556     0.1944  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5853      0.6029     0.0351  5
  max valid BA                0.6529      0.6324     0.0460  5
  best valid F1               0.5383      0.5238     0.0671  5
  test BA                     0.5353      0.5147     0.0979  5
  test F1                     0.3100      0.2857     0.1967  5
  test sensitivity            0.2824      0.2353     0.2096  5
  test specificity            0.7882      0.7941     0.1089  5
  test precision              0.3768      0.3636     0.1986  5
  test loss                   0.6941      0.6909     0.0189  5
  FPR (FP/(FP+TN))            0.2118      0.2059     0.1089  5
  FNR (FN/(FN+TP))            0.7176      0.7647     0.2096  5
```

## AUC vs chemistry null model, in-sample increment

(skipped: SKIP_AUC=1 -- rerun without it to fill this in: `python3 analysis/full_label_report.py --label thematical_paths_geom_chem_orthogonal_init_hid16 --seeds=0,1,2,3,4`)
