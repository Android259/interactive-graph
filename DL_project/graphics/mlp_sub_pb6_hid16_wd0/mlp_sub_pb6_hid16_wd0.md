# mlp_sub_pb6_hid16_wd0

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_hid16_wd0'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.6303      0.3268      0.6109      0.6192      0.5697      0.4750
groups_FA                                    5      0.2833      0.7514      0.4840      0.6232      0.3833      0.7444
groups_LPC+LPE+LPG                           5      0.5625      0.7871      0.8272      0.7837      0.6125      0.7800
groups_PA                                    5      0.5538      0.9154      0.5553      0.6839      0.5385      0.9231
groups_PC                                    5      0.2697      0.7168      0.4341      0.7133      0.2679      0.7299
groups_PE                                    5      0.8850      0.7600      0.7614      0.7703      0.9100      0.7800
groups_PG                                    5      0.7088      0.7858      0.7804      0.7773      0.7071      0.7912
groups_PI                                    5      0.3500      0.6000      0.3408      0.7353      0.5750      0.5750
groups_PS+PGP+DAG+TAG                        5      0.4000      0.6667      0.4013      0.6232      0.4500      0.6125
ALL                                         45      0.5159      0.7011      0.5773      0.7033      0.5571      0.7123

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6240      0.5833     0.1248  45
max valid BA                0.6347      0.6000     0.1238  45
best valid F1               0.5313      0.5714     0.1829  45
test BA                     0.6085      0.5556     0.1367  45
test AUC                    0.5908      0.5414     0.2082  45
test AUC in-protein         0.5772      0.5637     0.2306  32
  (proteins averaged)       3.0000      2.0000     3.5162  45
test AUC in-protein (pairs)      0.5245      0.5379     0.2439  45
  (proteins contributing)      5.4444      3.0000     4.0819  45
test F1                     0.4574      0.5263     0.2493  45
test sensitivity            0.5159      0.6154     0.3213  45
test specificity            0.7011      0.8053     0.3094  45
test precision              0.5680      0.5833     0.2017  39
test loss                   0.6335      0.6728     0.1038  45
FPR (FP/(FP+TN))            0.2989      0.1947     0.3094  45
FNR (FN/(FN+TP))            0.4841      0.3846     0.3213  45

=== abs(sensitivity-specificity) gap: mean=0.4865 median=0.4231 n=45 ===
sensitivity std across seeds (by group): mean=0.2318 median=0.2232 n=9
specificity std across seeds (by group): mean=0.2470 median=0.2616 n=9

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4927      0.5000     0.0186  5
  max valid BA                0.5223      0.5125     0.0367  5
  best valid F1               0.5483      0.5833     0.0868  5
  test BA                     0.4786      0.5000     0.0572  5
  test AUC                    0.3690      0.4095     0.1235  5
  test AUC in-protein         0.5223      0.5649     0.2202  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4776      0.4891     0.2376  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4414      0.5263     0.2551  5
  test sensitivity            0.6303      0.7576     0.3835  5
  test specificity            0.3268      0.2439     0.3897  5
  test precision              0.4272      0.4276     0.0431  4
  test loss                   0.7313      0.7149     0.0444  5
  FPR (FP/(FP+TN))            0.6732      0.7561     0.3897  5
  FNR (FN/(FN+TP))            0.3697      0.2424     0.3835  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5514      0.5486     0.0441  5
  max valid BA                0.5639      0.5625     0.0446  5
  best valid F1               0.4138      0.4138     0.1860  5
  test BA                     0.5173      0.5152     0.0670  5
  test AUC                    0.4570      0.4932     0.0818  5
  test AUC in-protein         0.4167      0.3500     0.2963  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.3976      0.4167     0.1763  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3000      0.3529     0.1828  5
  test sensitivity            0.2833      0.2500     0.2232  5
  test specificity            0.7514      0.8919     0.2616  5
  test precision              0.4909      0.5027     0.1730  4
  test loss                   0.7050      0.6948     0.0371  5
  FPR (FP/(FP+TN))            0.2486      0.1081     0.2616  5
  FNR (FN/(FN+TP))            0.7167      0.7500     0.2232  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6804      0.6646     0.0780  5
  max valid BA                0.6963      0.7104     0.0711  5
  best valid F1               0.6069      0.6250     0.0917  5
  test BA                     0.6748      0.6704     0.0743  5
  test AUC                    0.7764      0.7712     0.0964  5
  test AUC in-protein         0.8947      0.8866     0.0805  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.7666      0.7857     0.1097  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5761      0.5517     0.0852  5
  test sensitivity            0.5625      0.6250     0.0884  5
  test specificity            0.7871      0.8387     0.1685  5
  test precision              0.6209      0.6154     0.1616  5
  test loss                   0.5831      0.6085     0.1386  5
  FPR (FP/(FP+TN))            0.2129      0.1613     0.1685  5
  FNR (FN/(FN+TP))            0.4375      0.3750     0.0884  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7192      0.7115     0.0292  5
  max valid BA                0.7308      0.7115     0.0385  5
  best valid F1               0.6334      0.6087     0.0595  5
  test BA                     0.7346      0.7500     0.0583  5
  test AUC                    0.6947      0.7130     0.0919  5
  test AUC in-protein         0.5292      0.4583     0.3400  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.6168      0.5333     0.2792  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6453      0.6667     0.0882  5
  test sensitivity            0.5538      0.5385     0.0644  5
  test specificity            0.9154      0.9615     0.0688  5
  test precision              0.7806      0.8750     0.1451  5
  test loss                   0.6090      0.6334     0.0655  5
  FPR (FP/(FP+TN))            0.0846      0.0385     0.0688  5
  FNR (FN/(FN+TP))            0.4462      0.4615     0.0644  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4979      0.5000     0.0221  5
  max valid BA                0.4989      0.5000     0.0213  5
  best valid F1               0.3300      0.2549     0.1693  5
  test BA                     0.4932      0.5000     0.0249  5
  test AUC                    0.4252      0.4097     0.0971  5
  test AUC in-protein         0.4829      0.5097     0.1314  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4728      0.4692     0.0799  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.2091      0.1781     0.1951  5
  test sensitivity            0.2697      0.1193     0.3985  5
  test specificity            0.7168      0.8782     0.3900  5
  test precision              0.3490      0.3559     0.0651  4
  test loss                   0.6923      0.6936     0.0218  5
  FPR (FP/(FP+TN))            0.2832      0.1218     0.3900  5
  FNR (FN/(FN+TP))            0.7303      0.8807     0.3985  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8375      0.8375     0.0400  5
  max valid BA                0.8450      0.8500     0.0343  5
  best valid F1               0.7746      0.7789     0.0397  5
  test BA                     0.8225      0.8313     0.0392  5
  test AUC                    0.9009      0.9025     0.0447  5
  test AUC in-protein         0.7141      0.7000     0.1073  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7391      0.7059     0.0613  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7484      0.7600     0.0445  5
  test sensitivity            0.8850      0.9000     0.0742  5
  test specificity            0.7600      0.7750     0.0526  5
  test precision              0.6507      0.6333     0.0473  5
  test loss                   0.4435      0.4511     0.0498  5
  FPR (FP/(FP+TN))            0.2400      0.2250     0.0526  5
  FNR (FN/(FN+TP))            0.1150      0.1000     0.0742  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7429      0.7374     0.0139  5
  max valid BA                0.7491      0.7463     0.0125  5
  best valid F1               0.6642      0.6607     0.0157  5
  test BA                     0.7473      0.7535     0.0373  5
  test AUC                    0.8020      0.8195     0.0341  5
  test AUC in-protein         0.5025      0.5167     0.0587  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.5063      0.4965     0.0396  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.6645      0.6723     0.0465  5
  test sensitivity            0.7088      0.7018     0.0520  5
  test specificity            0.7858      0.8053     0.0333  5
  test precision              0.6261      0.6452     0.0467  5
  test loss                   0.5599      0.5621     0.0432  5
  FPR (FP/(FP+TN))            0.2142      0.1947     0.0333  5
  FNR (FN/(FN+TP))            0.2912      0.2982     0.0520  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5625      0.5312     0.0733  5
  max valid BA                0.5750      0.5938     0.0719  5
  best valid F1               0.4110      0.5517     0.2165  5
  test BA                     0.4750      0.4688     0.0261  5
  test AUC                    0.4031      0.4219     0.0951  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.3533      0.5000     0.3280  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.2357      0.3333     0.2183  5
  test sensitivity            0.3500      0.3750     0.3469  5
  test specificity            0.6000      0.5625     0.3968  5
  test precision              0.3042      0.3000     0.0072  3
  test loss                   0.6896      0.6893     0.0230  5
  FPR (FP/(FP+TN))            0.4000      0.4375     0.3968  5
  FNR (FN/(FN+TP))            0.6500      0.6250     0.3469  5

groups_PS+PGP+DAG+TAG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5312      0.5312     0.0312  5
  max valid BA                0.5312      0.5312     0.0312  5
  best valid F1               0.3997      0.3636     0.1110  5
  test BA                     0.5333      0.5333     0.0236  5
  test AUC                    0.4889      0.5259     0.0886  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.3900      0.6000     0.3612  5
    (proteins contributing)      2.6000      3.0000     0.8944  5
  test F1                     0.2962      0.2000     0.2380  5
  test sensitivity            0.4000      0.1111     0.4554  5
  test specificity            0.6667      1.0000     0.4619  5
  test precision              0.6950      0.6957     0.3521  4
  test loss                   0.6876      0.6886     0.0133  5
  FPR (FP/(FP+TN))            0.3333      0.0000     0.4619  5
  FNR (FN/(FN+TP))            0.6000      0.8889     0.4554  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_hid16_wd0 --seeds=0,1,2,3,4`
