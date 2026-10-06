# ge_lcs_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_esm3_protunion14_prothid32_subclass

## Summary (analysis/summarize_label.py)

```
Summary: 'ge_lcs_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_esm3_protunion14_prothid32_subclass'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.2485      0.6800      0.7669      0.7028      0.4485      0.7222
groups_FA                                    5      0.4833      0.5895      0.8276      0.7428      0.6667      0.6400
groups_LPC+LPE+LPG                           5      0.6000      0.5429      0.8845      0.7995      0.6125      0.6200
groups_PA                                    5      0.6308      0.4857      0.9088      0.7752      0.6615      0.6333
groups_PC                                    5      0.4239      0.7270      0.8981      0.7147      0.5046      0.8264
groups_PE                                    5      0.6950      0.6828      0.9199      0.8005      0.8250      0.7103
groups_PG                                    5      0.6000      0.4667      0.9171      0.8202      0.6321      0.5868
groups_PI                                    5      0.2500      0.9143      0.7541      0.6780      0.3250      0.9000
groups_PS+PGP+DAG+TAG                        5      0.4889      0.7059      0.9157      0.7719      0.6500      0.6941
ALL                                         45      0.4911      0.6439      0.8658      0.7562      0.5918      0.7037

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5974      0.5795     0.0807  45
max valid BA                0.6477      0.6375     0.0728  45
best valid F1               0.6341      0.6286     0.1545  45
test BA                     0.5675      0.5610     0.0898  45
test AUC                    0.5853      0.5921     0.1232  45
test AUC in-protein         0.5267      0.5347     0.1781  39
  (proteins averaged)       3.9556      3.0000     3.1403  45
test AUC in-protein (pairs)      0.5124      0.5222     0.1399  45
  (proteins contributing)      6.9333      6.0000     3.5764  45
test F1                     0.4726      0.5051     0.2353  45
test sensitivity            0.4911      0.5088     0.2827  45
test specificity            0.6439      0.6909     0.2804  45
test precision              0.5740      0.5556     0.2046  40
test loss                   0.8634      0.7989     0.2790  45
FPR (FP/(FP+TN))            0.3561      0.3091     0.2804  45
FNR (FN/(FN+TP))            0.5089      0.4912     0.2827  45

=== abs(sensitivity-specificity) gap: mean=0.4557 median=0.3830 n=45 ===
sensitivity std across seeds (by group): mean=0.2367 median=0.1859 n=9
specificity std across seeds (by group): mean=0.2491 median=0.1917 n=9

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5513      0.5513     0.0383  5
  max valid BA                0.5854      0.5707     0.0399  5
  best valid F1               0.5075      0.5263     0.0690  5
  test BA                     0.4642      0.4727     0.0529  5
  test AUC                    0.4419      0.4496     0.0895  5
  test AUC in-protein         0.4073      0.4278     0.0521  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4600      0.4098     0.0929  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.2264      0.2069     0.1945  5
  test sensitivity            0.2485      0.1818     0.2575  5
  test specificity            0.6800      0.6909     0.2475  5
  test precision              0.2837      0.2980     0.1281  4
  test loss                   0.8975      0.7061     0.3164  5
  FPR (FP/(FP+TN))            0.3200      0.3091     0.2475  5
  FNR (FN/(FN+TP))            0.7515      0.8182     0.2575  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6125      0.6417     0.0695  5
  max valid BA                0.6533      0.6458     0.0304  5
  best valid F1               0.6764      0.7170     0.1000  5
  test BA                     0.5364      0.5000     0.1527  5
  test AUC                    0.5075      0.5044     0.1848  5
  test AUC in-protein         0.4619      0.4969     0.2421  5
    (proteins averaged)       3.0000      3.0000     1.0000  5
  test AUC in-protein (pairs)      0.4848      0.4792     0.2330  5
    (proteins contributing)      8.4000      8.0000     1.1402  5
  test F1                     0.4386      0.6441     0.3744  5
  test sensitivity            0.4833      0.7083     0.4265  5
  test specificity            0.5895      0.6842     0.3654  5
  test precision              0.5339      0.5714     0.2928  4
  test loss                   1.0254      0.7190     0.6809  5
  FPR (FP/(FP+TN))            0.4105      0.3158     0.3654  5
  FNR (FN/(FN+TP))            0.5167      0.2917     0.4265  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5862      0.6062     0.0487  5
  max valid BA                0.6162      0.6312     0.0327  5
  best valid F1               0.6209      0.6154     0.0300  5
  test BA                     0.5714      0.5610     0.0224  5
  test AUC                    0.6411      0.6369     0.0607  5
  test AUC in-protein         0.5484      0.5556     0.1199  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.5740      0.5536     0.1104  5
    (proteins contributing)      5.2000      5.0000     0.8367  5
  test F1                     0.5356      0.5641     0.0784  5
  test sensitivity            0.6000      0.6875     0.1630  5
  test specificity            0.5429      0.4762     0.1528  5
  test precision              0.5068      0.5000     0.0334  5
  test loss                   0.7590      0.7989     0.0781  5
  FPR (FP/(FP+TN))            0.4571      0.5238     0.1528  5
  FNR (FN/(FN+TP))            0.4000      0.3125     0.1630  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5000     0.0834  5
  max valid BA                0.6474      0.6667     0.0478  5
  best valid F1               0.8238      0.8125     0.0240  5
  test BA                     0.5582      0.5000     0.1005  5
  test AUC                    0.5429      0.5714     0.1542  5
  test AUC in-protein         0.4269      0.5000     0.2699  5
    (proteins averaged)       1.6000      2.0000     0.5477  5
  test AUC in-protein (pairs)      0.3776      0.3889     0.1743  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5758      0.7500     0.3359  5
  test sensitivity            0.6308      0.8462     0.4262  5
  test specificity            0.4857      0.4286     0.5010  5
  test precision              0.7537      0.6917     0.1700  4
  test loss                   0.6906      0.6964     0.0301  5
  FPR (FP/(FP+TN))            0.5143      0.5714     0.5010  5
  FNR (FN/(FN+TP))            0.3692      0.1538     0.4262  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6015      0.5795     0.0428  5
  max valid BA                0.6655      0.6638     0.0514  5
  best valid F1               0.6124      0.5801     0.0560  5
  test BA                     0.5754      0.5746     0.0350  5
  test AUC                    0.6073      0.6040     0.0307  5
  test AUC in-protein         0.5666      0.5535     0.0720  5
    (proteins averaged)       9.4000      9.0000     0.5477  5
  test AUC in-protein (pairs)      0.5443      0.5304     0.0670  5
    (proteins contributing)     13.6000     14.0000     1.1402  5
  test F1                     0.4519      0.4946     0.0944  5
  test sensitivity            0.4239      0.4220     0.1638  5
  test specificity            0.7270      0.7547     0.1850  5
  test precision              0.5400      0.5618     0.0659  5
  test loss                   0.8683      0.8993     0.0615  5
  FPR (FP/(FP+TN))            0.2730      0.2453     0.1850  5
  FNR (FN/(FN+TP))            0.5761      0.5780     0.1638  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7352      0.7685     0.1096  5
  max valid BA                0.7677      0.7935     0.0789  5
  best valid F1               0.8161      0.8148     0.0515  5
  test BA                     0.6889      0.6918     0.0596  5
  test AUC                    0.7228      0.7207     0.0452  5
  test AUC in-protein         0.6072      0.5706     0.1552  5
    (proteins averaged)       5.2000      5.0000     0.4472  5
  test AUC in-protein (pairs)      0.5951      0.6117     0.0925  5
    (proteins contributing)      8.0000      8.0000     1.2247  5
  test F1                     0.7215      0.7273     0.0460  5
  test sensitivity            0.6950      0.6750     0.0779  5
  test specificity            0.6828      0.7586     0.1409  5
  test precision              0.7579      0.7812     0.0667  5
  test loss                   0.6938      0.7108     0.0677  5
  FPR (FP/(FP+TN))            0.3172      0.2414     0.1409  5
  FNR (FN/(FN+TP))            0.3050      0.3250     0.0779  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5667      0.5634     0.0398  5
  max valid BA                0.6095      0.6170     0.0276  5
  best valid F1               0.5955      0.6107     0.0544  5
  test BA                     0.5333      0.5333     0.0300  5
  test AUC                    0.5513      0.5489     0.0511  5
  test AUC in-protein         0.5347      0.5347     0.0334  5
    (proteins averaged)       8.8000      9.0000     0.4472  5
  test AUC in-protein (pairs)      0.5163      0.5222     0.0338  5
    (proteins contributing)     11.2000     11.0000     0.8367  5
  test F1                     0.5151      0.5043     0.0534  5
  test sensitivity            0.6000      0.5088     0.1643  5
  test specificity            0.4667      0.4800     0.1784  5
  test precision              0.4651      0.4578     0.0352  5
  test loss                   0.9633      1.0420     0.1660  5
  FPR (FP/(FP+TN))            0.5333      0.5200     0.1784  5
  FNR (FN/(FN+TP))            0.4000      0.4912     0.1643  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5625      0.5625     0.0442  5
  max valid BA                0.6125      0.6250     0.0927  5
  best valid F1               0.4838      0.6250     0.2974  5
  test BA                     0.5821      0.5982     0.0817  5
  test AUC                    0.6607      0.7321     0.1211  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.5095      0.3750     0.2043  5
    (proteins contributing)      3.6000      3.0000     0.8944  5
  test F1                     0.3141      0.4000     0.2979  5
  test sensitivity            0.2500      0.2500     0.2652  5
  test specificity            0.9143      1.0000     0.1917  5
  test precision              0.8750      1.0000     0.2165  3
  test loss                   0.9346      0.8494     0.3051  5
  FPR (FP/(FP+TN))            0.0857      0.0000     0.1917  5
  FNR (FN/(FN+TP))            0.7500      0.7500     0.2652  5

groups_PS+PGP+DAG+TAG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6103      0.6360     0.0773  5
  max valid BA                0.6721      0.6912     0.0745  5
  best valid F1               0.5708      0.5714     0.0672  5
  test BA                     0.5974      0.6078     0.0600  5
  test AUC                    0.5922      0.6013     0.0697  5
  test AUC in-protein         0.6937      0.6625     0.2536  4
    (proteins averaged)       1.6000      2.0000     1.1402  5
  test AUC in-protein (pairs)      0.5499      0.5357     0.1023  5
    (proteins contributing)      5.6000      6.0000     0.5477  5
  test F1                     0.4746      0.4615     0.0495  5
  test sensitivity            0.4889      0.4444     0.1859  5
  test specificity            0.7059      0.7647     0.2790  5
  test precision              0.5400      0.5556     0.1526  5
  test loss                   0.9384      0.9269     0.0988  5
  FPR (FP/(FP+TN))            0.2941      0.2353     0.2790  5
  FNR (FN/(FN+TP))            0.5111      0.5556     0.1859  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label ge_lcs_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_esm3_protunion14_prothid32_subclass --seeds=0,1,2,3,4`
