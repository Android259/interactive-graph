# mlp_sub_pb6_drop_chain

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_drop_chain'
rows: 40

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.7030      0.3902      0.6151      0.4386      0.6424      0.3900
groups_FA                                    5      0.3250      0.8054      0.4440      0.8157      0.2250      0.9278
groups_LPC+LPE+LPG                           5      0.6125      0.6839      0.6475      0.7673      0.6875      0.6800
groups_PA                                    5      0.5692      0.8769      0.5434      0.7016      0.5846      0.9385
groups_PC                                    5      0.5761      0.4091      0.6870      0.3859      0.6092      0.4173
groups_PE                                    5      0.8700      0.7675      0.7206      0.7244      0.9150      0.7650
groups_PG                                    5      0.5649      0.8301      0.6015      0.7342      0.5821      0.7929
groups_PI                                    5      0.3500      0.6750      0.5641      0.5739      0.6250      0.6250
ALL                                         40      0.5714      0.6798      0.6029      0.6427      0.6089      0.6921

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6380      0.6278     0.1187  40
max valid BA                0.6505      0.6340     0.1229  40
best valid F1               0.5864      0.5732     0.1379  40
test BA                     0.6256      0.6382     0.1243  40
test AUC                    0.6257      0.6593     0.1956  40
test AUC in-protein         0.6360      0.6429     0.2303  32
  (proteins averaged)       3.3750      2.0000     3.5568  40
test AUC in-protein (pairs)      0.6326      0.6624     0.1882  40
  (proteins contributing)      5.8000      4.0000     4.1891  40
test F1                     0.4983      0.5637     0.2263  40
test sensitivity            0.5714      0.5972     0.3078  40
test specificity            0.6798      0.8032     0.3173  40
test precision              0.5497      0.5505     0.1900  36
test loss                   0.6481      0.6688     0.0970  40
FPR (FP/(FP+TN))            0.3202      0.1968     0.3173  40
FNR (FN/(FN+TP))            0.4286      0.4028     0.3078  40

=== abs(sensitivity-specificity) gap: mean=0.4670 median=0.3462 n=40 ===
sensitivity std across seeds (by group): mean=0.2363 median=0.2294 n=8
specificity std across seeds (by group): mean=0.2360 median=0.2308 n=8

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5162      0.5000     0.0298  5
  max valid BA                0.5162      0.5000     0.0298  5
  best valid F1               0.5858      0.6226     0.0617  5
  test BA                     0.5466      0.5000     0.1043  5
  test AUC                    0.5135      0.4627     0.2213  5
  test AUC in-protein         0.5801      0.5110     0.2198  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.6022      0.6639     0.2757  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.5009      0.6168     0.2804  5
  test sensitivity            0.7030      1.0000     0.4456  5
  test specificity            0.3902      0.0000     0.5346  5
  test precision              0.5581      0.4459     0.2244  4
  test loss                   0.7083      0.6992     0.0296  5
  FPR (FP/(FP+TN))            0.6098      1.0000     0.5346  5
  FNR (FN/(FN+TP))            0.2970      0.0000     0.4456  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5625      0.5625     0.0390  5
  max valid BA                0.5764      0.5625     0.0566  5
  best valid F1               0.5276      0.5750     0.1641  5
  test BA                     0.5652      0.5574     0.0553  5
  test AUC                    0.4552      0.4133     0.1334  5
  test AUC in-protein         0.9167      0.9167     0.0962  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.7981      0.7500     0.0906  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3407      0.3429     0.2164  5
  test sensitivity            0.3250      0.2500     0.3096  5
  test specificity            0.8054      0.9189     0.3036  5
  test precision              0.6212      0.5852     0.1964  4
  test loss                   0.7252      0.6895     0.0726  5
  FPR (FP/(FP+TN))            0.1946      0.0811     0.3036  5
  FNR (FN/(FN+TP))            0.6750      0.7500     0.3096  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6479      0.6333     0.0923  5
  max valid BA                0.6837      0.6646     0.0774  5
  best valid F1               0.5967      0.5625     0.0933  5
  test BA                     0.6482      0.6502     0.0376  5
  test AUC                    0.7058      0.6996     0.0553  5
  test AUC in-protein         0.7322      0.8056     0.1689  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.6272      0.6364     0.1289  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.5496      0.5641     0.0410  5
  test sensitivity            0.6125      0.6250     0.1492  5
  test specificity            0.6839      0.7419     0.1914  5
  test precision              0.5290      0.5385     0.0967  5
  test loss                   0.6316      0.6408     0.0765  5
  FPR (FP/(FP+TN))            0.3161      0.2581     0.1914  5
  FNR (FN/(FN+TP))            0.3875      0.3750     0.1492  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7346      0.7500     0.0832  5
  max valid BA                0.7615      0.7500     0.0752  5
  best valid F1               0.6731      0.6667     0.1004  5
  test BA                     0.7231      0.7115     0.0501  5
  test AUC                    0.7722      0.7929     0.0912  5
  test AUC in-protein         0.4506      0.3429     0.3213  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.5361      0.5556     0.2591  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.6300      0.6087     0.0709  5
  test sensitivity            0.5692      0.5385     0.0421  5
  test specificity            0.8769      0.8846     0.0688  5
  test precision              0.7109      0.7000     0.1244  5
  test loss                   0.6412      0.6387     0.0171  5
  FPR (FP/(FP+TN))            0.1231      0.1154     0.0688  5
  FNR (FN/(FN+TP))            0.4308      0.4615     0.0421  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5132      0.5000     0.0219  5
  max valid BA                0.5132      0.5000     0.0219  5
  best valid F1               0.4310      0.4966     0.1273  5
  test BA                     0.4926      0.5000     0.0576  5
  test AUC                    0.4344      0.4534     0.1043  5
  test AUC in-protein         0.5158      0.6032     0.2302  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.5177      0.6160     0.1586  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.3513      0.5101     0.2415  5
  test sensitivity            0.5761      0.6972     0.4637  5
  test specificity            0.4091      0.4264     0.4267  5
  test precision              0.3313      0.3562     0.0834  4
  test loss                   0.7309      0.7403     0.0597  5
  FPR (FP/(FP+TN))            0.5909      0.5736     0.4267  5
  FNR (FN/(FN+TP))            0.4239      0.3028     0.4637  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.8337      0.8250     0.0285  5
  max valid BA                0.8400      0.8438     0.0278  5
  best valid F1               0.7700      0.7647     0.0344  5
  test BA                     0.8187      0.8375     0.0637  5
  test AUC                    0.8929      0.8994     0.0417  5
  test AUC in-protein         0.7773      0.7819     0.0819  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.7556      0.7662     0.0873  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.7447      0.7727     0.0725  5
  test sensitivity            0.8700      0.8500     0.0991  5
  test specificity            0.7675      0.7750     0.0497  5
  test precision              0.6525      0.6842     0.0640  5
  test loss                   0.4730      0.4637     0.0447  5
  FPR (FP/(FP+TN))            0.2325      0.2250     0.0497  5
  FNR (FN/(FN+TP))            0.1300      0.1500     0.0991  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6705      0.6613     0.0408  5
  max valid BA                0.6875      0.6836     0.0535  5
  best valid F1               0.5834      0.5660     0.0678  5
  test BA                     0.6975      0.7055     0.0461  5
  test AUC                    0.7595      0.7441     0.0520  5
  test AUC in-protein         0.5177      0.5377     0.1015  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.5172      0.5479     0.0759  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.5946      0.6038     0.0621  5
  test sensitivity            0.5649      0.5614     0.0574  5
  test specificity            0.8301      0.8407     0.0431  5
  test precision              0.6290      0.6531     0.0753  5
  test loss                   0.5738      0.5748     0.0615  5
  FPR (FP/(FP+TN))            0.1699      0.1593     0.0431  5
  FNR (FN/(FN+TP))            0.4351      0.4386     0.0574  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6250      0.6250     0.1013  5
  max valid BA                0.6250      0.6250     0.1013  5
  best valid F1               0.5238      0.5455     0.1513  5
  test BA                     0.5125      0.5000     0.0844  5
  test AUC                    0.4719      0.4453     0.0759  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.7067      0.6667     0.1817  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.2743      0.3810     0.2582  5
  test sensitivity            0.3500      0.5000     0.3236  5
  test specificity            0.6750      0.6875     0.2703  5
  test precision              0.2853      0.3205     0.2084  4
  test loss                   0.7011      0.6964     0.0234  5
  FPR (FP/(FP+TN))            0.3250      0.3125     0.2703  5
  FNR (FN/(FN+TP))            0.6500      0.5000     0.3236  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_drop_chain --seeds=0,1,2,3,4`
