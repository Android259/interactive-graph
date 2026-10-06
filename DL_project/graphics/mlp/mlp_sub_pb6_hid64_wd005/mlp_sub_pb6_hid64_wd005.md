# mlp_sub_pb6_hid64_wd005

## Summary (analysis/summarize_label.py)

```
Summary: 'mlp_sub_pb6_hid64_wd005'
rows: 45

=== Sensitivity / specificity by group (test / train / valid) ===
group                                        n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM    5      0.7333      0.2829      0.6863      0.4578      0.6970      0.3650
groups_FA                                    5      0.5083      0.5081      0.6829      0.4713      0.5167      0.5556
groups_LPC+LPE+LPG                           5      0.6625      0.4065      0.5721      0.5987      0.7125      0.5200
groups_PA                                    5      0.7692      0.5385      0.6086      0.4857      0.7077      0.6231
groups_PC                                    5      0.4495      0.5330      0.5668      0.5411      0.4312      0.5401
groups_PE                                    5      0.8050      0.4275      0.5801      0.5295      0.7800      0.4450
groups_PG                                    5      0.8561      0.3876      0.6342      0.4776      0.7607      0.4478
groups_PI                                    5      0.6000      0.2500      0.6534      0.4835      0.6750      0.4875
groups_PS+PGP+DAG+TAG                        5      0.5778      0.5200      0.6292      0.4965      0.5500      0.5625
ALL                                         45      0.6624      0.4282      0.6237      0.5046      0.6479      0.5052

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5571      0.5341     0.0722  45
max valid BA                0.5765      0.5750     0.0732  45
best valid F1               0.5372      0.5500     0.0794  45
test BA                     0.5453      0.5188     0.1059  45
test AUC                    0.5256      0.5292     0.1714  45
test AUC in-protein         0.5863      0.5826     0.2061  32
  (proteins averaged)       3.0000      2.0000     3.5162  45
test AUC in-protein (pairs)      0.5580      0.6000     0.2354  45
  (proteins contributing)      5.4444      3.0000     4.0819  45
test F1                     0.4513      0.5158     0.2019  45
test sensitivity            0.6624      0.7544     0.3598  45
test specificity            0.4282      0.2375     0.3971  45
test precision              0.4385      0.3810     0.1682  41
test loss                   0.6939      0.6935     0.0099  45
FPR (FP/(FP+TN))            0.5718      0.7625     0.3971  45
FNR (FN/(FN+TP))            0.3376      0.2456     0.3598  45

=== abs(sensitivity-specificity) gap: mean=0.6798 median=0.7692 n=45 ===
sensitivity std across seeds (by group): mean=0.3506 median=0.4217 n=9
specificity std across seeds (by group): mean=0.4222 median=0.4167 n=9

=== By group ===
groups_Cer+CerP+HexCer+Hex2Cer+SHexCer+SM (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5010      0.5000     0.0224  5
  max valid BA                0.5310      0.5000     0.0426  5
  best valid F1               0.6154      0.6226     0.0161  5
  test BA                     0.5081      0.5000     0.0330  5
  test AUC                    0.4596      0.4642     0.1045  5
  test AUC in-protein         0.5336      0.5003     0.0623  5
    (proteins averaged)       2.0000      2.0000     0.0000  5
  test AUC in-protein (pairs)      0.4949      0.4620     0.1591  5
    (proteins contributing)      2.0000      2.0000     0.0000  5
  test F1                     0.4829      0.6168     0.2718  5
  test sensitivity            0.7333      0.9091     0.4217  5
  test specificity            0.2829      0.1951     0.4141  5
  test precision              0.4517      0.4459     0.0226  4
  test loss                   0.6999      0.6988     0.0053  5
  FPR (FP/(FP+TN))            0.7171      0.8049     0.4141  5
  FNR (FN/(FN+TP))            0.2667      0.0909     0.4217  5

groups_FA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5347      0.5139     0.0556  5
  max valid BA                0.5361      0.5139     0.0545  5
  best valid F1               0.5714      0.5714     0.0000  5
  test BA                     0.5082      0.5000     0.0358  5
  test AUC                    0.4172      0.4302     0.1002  5
  test AUC in-protein         0.6500      0.8000     0.3226  4
    (proteins averaged)       0.8000      1.0000     0.4472  5
  test AUC in-protein (pairs)      0.5942      0.7143     0.2559  5
    (proteins contributing)      4.0000      4.0000     1.8708  5
  test F1                     0.3675      0.3902     0.2341  5
  test sensitivity            0.5083      0.3333     0.4314  5
  test specificity            0.5081      0.6216     0.4167  5
  test precision              0.4031      0.4043     0.0567  4
  test loss                   0.6945      0.6944     0.0037  5
  FPR (FP/(FP+TN))            0.4919      0.3784     0.4167  5
  FNR (FN/(FN+TP))            0.4917      0.6667     0.4314  5

groups_LPC+LPE+LPG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5650      0.5500     0.0505  5
  max valid BA                0.6162      0.6271     0.0562  5
  best valid F1               0.5562      0.5500     0.0463  5
  test BA                     0.5345      0.5323     0.0786  5
  test AUC                    0.5869      0.6210     0.1427  5
  test AUC in-protein         0.6179      0.6539     0.2098  4
    (proteins averaged)       1.6000      2.0000     0.8944  5
  test AUC in-protein (pairs)      0.5227      0.4333     0.2545  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.4581      0.4878     0.0837  5
  test sensitivity            0.6625      0.6250     0.3295  5
  test specificity            0.4065      0.4839     0.3922  5
  test precision              0.4404      0.3556     0.2244  5
  test loss                   0.6894      0.6935     0.0089  5
  FPR (FP/(FP+TN))            0.5935      0.5161     0.3922  5
  FNR (FN/(FN+TP))            0.3375      0.3750     0.3295  5

groups_PA (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6654      0.6923     0.0586  5
  max valid BA                0.6654      0.6923     0.0586  5
  best valid F1               0.5813      0.5778     0.0282  5
  test BA                     0.6538      0.6154     0.1008  5
  test AUC                    0.6852      0.6953     0.0733  5
  test AUC in-protein         0.6292      0.6583     0.3902  4
    (proteins averaged)       1.0000      1.0000     0.7071  5
  test AUC in-protein (pairs)      0.6616      0.7778     0.3121  5
    (proteins contributing)      2.8000      3.0000     1.0954  5
  test F1                     0.5889      0.5652     0.0982  5
  test sensitivity            0.7692      0.6154     0.2107  5
  test specificity            0.5385      0.5000     0.3598  5
  test precision              0.5404      0.3939     0.2307  5
  test loss                   0.6872      0.6916     0.0068  5
  FPR (FP/(FP+TN))            0.4615      0.5000     0.3598  5
  FNR (FN/(FN+TP))            0.2308      0.3846     0.2107  5

groups_PC (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.4852      0.4949     0.0235  5
  max valid BA                0.4856      0.4949     0.0227  5
  best valid F1               0.3859      0.4023     0.1434  5
  test BA                     0.4913      0.4985     0.0251  5
  test AUC                    0.3704      0.3694     0.0270  5
  test AUC in-protein         0.4549      0.3638     0.1689  5
    (proteins averaged)      10.8000     11.0000     0.8367  5
  test AUC in-protein (pairs)      0.4661      0.4576     0.1178  5
    (proteins contributing)     13.6000     13.0000     1.3416  5
  test F1                     0.2840      0.2077     0.2276  5
  test sensitivity            0.4495      0.1743     0.4971  5
  test specificity            0.5330      0.7208     0.4826  5
  test precision              0.3389      0.3541     0.0500  5
  test loss                   0.7027      0.7051     0.0157  5
  FPR (FP/(FP+TN))            0.4670      0.2792     0.4826  5
  FNR (FN/(FN+TP))            0.5505      0.8257     0.4971  5

groups_PE (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5925      0.5687     0.0935  5
  max valid BA                0.6125      0.5750     0.0849  5
  best valid F1               0.5520      0.5379     0.0404  5
  test BA                     0.6162      0.5563     0.1266  5
  test AUC                    0.7076      0.6866     0.0555  5
  test AUC in-protein         0.6876      0.6354     0.1476  5
    (proteins averaged)       4.2000      4.0000     0.4472  5
  test AUC in-protein (pairs)      0.6972      0.6528     0.1275  5
    (proteins contributing)      8.6000      9.0000     1.6733  5
  test F1                     0.5736      0.5147     0.0899  5
  test sensitivity            0.8050      0.8750     0.2168  5
  test specificity            0.4275      0.2375     0.4692  5
  test precision              0.5340      0.3646     0.2609  5
  test loss                   0.6893      0.6920     0.0084  5
  FPR (FP/(FP+TN))            0.5725      0.7625     0.4692  5
  FNR (FN/(FN+TP))            0.1950      0.1250     0.2168  5

groups_PG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5822      0.5526     0.0662  5
  max valid BA                0.6043      0.6017     0.0737  5
  best valid F1               0.5341      0.5275     0.0276  5
  test BA                     0.6219      0.5668     0.1144  5
  test AUC                    0.7210      0.7174     0.0375  5
  test AUC in-protein         0.5585      0.5881     0.0625  5
    (proteins averaged)       6.6000      6.0000     1.5166  5
  test AUC in-protein (pairs)      0.5353      0.5395     0.0558  5
    (proteins contributing)      9.4000     10.0000     2.4083  5
  test F1                     0.5754      0.5258     0.0797  5
  test sensitivity            0.8561      0.8947     0.1610  5
  test specificity            0.3876      0.2389     0.3811  5
  test precision              0.4663      0.3723     0.1516  5
  test loss                   0.6884      0.6915     0.0090  5
  FPR (FP/(FP+TN))            0.6124      0.7611     0.3811  5
  FNR (FN/(FN+TP))            0.1439      0.1053     0.1610  5

groups_PI (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5375      0.5000     0.0559  5
  max valid BA                0.5813      0.5938     0.0523  5
  best valid F1               0.5314      0.5455     0.0292  5
  test BA                     0.4250      0.5000     0.1355  5
  test AUC                    0.3281      0.3125     0.1317  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.5600      0.6667     0.3394  5
    (proteins contributing)      2.6000      3.0000     0.5477  5
  test F1                     0.3190      0.4286     0.2250  5
  test sensitivity            0.6000      0.7500     0.4541  5
  test specificity            0.2500      0.1250     0.4239  5
  test precision              0.2729      0.3167     0.0999  4
  test loss                   0.6962      0.6952     0.0107  5
  FPR (FP/(FP+TN))            0.7500      0.8750     0.4239  5
  FNR (FN/(FN+TP))            0.4000      0.2500     0.4541  5

groups_PS+PGP+DAG+TAG (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5500      0.5625     0.0474  5
  max valid BA                0.5563      0.5625     0.0407  5
  best valid F1               0.5067      0.5000     0.0149  5
  test BA                     0.5489      0.5333     0.0536  5
  test AUC                    0.4548      0.4444     0.1512  5
    (proteins averaged)       0.0000      0.0000     0.0000  5
  test AUC in-protein (pairs)      0.4900      0.6000     0.3814  5
    (proteins contributing)      2.6000      3.0000     0.8944  5
  test F1                     0.4126      0.5263     0.2364  5
  test sensitivity            0.5778      0.5556     0.4332  5
  test specificity            0.5200      0.6667     0.4604  5
  test precision              0.4666      0.4457     0.1048  4
  test loss                   0.6976      0.6931     0.0089  5
  FPR (FP/(FP+TN))            0.4800      0.3333     0.4604  5
  FNR (FN/(FN+TP))            0.4222      0.4444     0.4332  5
```

## AUC vs chemistry null model, in-sample increment

Failed: PC/seed0: split reproduced here does not match the scored rows -- rerun for the full output: `python3 analysis/full_label_report.py --label mlp_sub_pb6_hid64_wd005 --seeds=0,1,2,3,4`
