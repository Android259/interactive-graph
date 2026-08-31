# descriptors_path_v2

## Summary (analysis/summarize_label.py)

```
Summary: 'descriptors_path_v2'
rows: 35

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5844      0.5588     0.0915  35
max valid BA                0.6041      0.5878     0.0953  35
best valid F1               0.5247      0.5610     0.1796  35
test BA                     0.5720      0.5347     0.1080  35
test F1                     0.4282      0.4962     0.2331  35
test sensitivity            0.5549      0.6471     0.3492  35
test specificity            0.5892      0.7059     0.3574  35
test precision              0.4858      0.4235     0.1977  30
test loss                   0.6931      0.6950     0.0124  35
test TP                    18.2286     17.0000    15.1640  35
test FP                    24.1714     14.0000    25.3046  35
test FN                    18.3429      9.0000    21.2117  35
test TN                    29.4000     25.0000    22.6705  35
FPR (FP/(FP+TN))            0.4108      0.2941     0.3574  35
FNR (FN/(FN+TP))            0.4451      0.3529     0.3492  35

=== abs(sensitivity-specificity) gap: mean=0.5696 median=0.5930 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5377      0.5196     0.0405  5
  max valid BA                0.5461      0.5370     0.0433  5
  best valid F1               0.4665      0.4522     0.2286  5
  test BA                     0.5306      0.5213     0.0483  5
  test F1                     0.3050      0.3800     0.2896  5
  test sensitivity            0.2776      0.2836     0.2763  5
  test specificity            0.7836      0.7705     0.2185  5
  test precision              0.4433      0.5593     0.2992  4
  test loss                   0.6916      0.6925     0.0045  5
  test TP                    18.6000     19.0000    18.5149  5
  test FP                    13.2000     14.0000    13.3304  5
  test FN                    48.4000     48.0000    18.5149  5
  test TN                    47.8000     47.0000    13.3304  5
  FPR (FP/(FP+TN))            0.2164      0.2295     0.2185  5
  FNR (FN/(FN+TP))            0.7224      0.7164     0.2763  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5615      0.5385     0.0737  5
  max valid BA                0.5769      0.5577     0.0827  5
  best valid F1               0.3717      0.4706     0.3519  5
  test BA                     0.5280      0.5000     0.0438  5
  test F1                     0.2203      0.2069     0.2379  5
  test sensitivity            0.1920      0.1200     0.2644  5
  test specificity            0.8640      1.0000     0.2823  5
  test precision              0.7500      0.7500     0.2500  3
  test loss                   0.6982      0.7003     0.0055  5
  test TP                     4.8000      3.0000     6.6106  5
  test FP                     3.4000      0.0000     7.0569  5
  test FN                    20.2000     22.0000     6.6106  5
  test TN                    21.6000     25.0000     7.0569  5
  FPR (FP/(FP+TN))            0.1360      0.0000     0.2823  5
  FNR (FN/(FN+TP))            0.8080      0.8800     0.2644  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5559      0.5430     0.0435  5
  max valid BA                0.6123      0.6068     0.0734  5
  best valid F1               0.5620      0.5610     0.0528  5
  test BA                     0.5268      0.5102     0.0338  5
  test F1                     0.4995      0.4944     0.0156  5
  test sensitivity            0.9217      0.9130     0.0364  5
  test specificity            0.1319      0.0851     0.0991  5
  test precision              0.3432      0.3333     0.0190  5
  test loss                   0.7013      0.7014     0.0041  5
  test TP                    21.2000     21.0000     0.8367  5
  test FP                    40.8000     43.0000     4.6583  5
  test FN                     1.8000      2.0000     0.8367  5
  test TN                     6.2000      4.0000     4.6583  5
  FPR (FP/(FP+TN))            0.8681      0.9149     0.0991  5
  FNR (FN/(FN+TP))            0.0783      0.0870     0.0364  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.7754      0.7788     0.0512  5
  max valid BA                0.7817      0.7788     0.0454  5
  best valid F1               0.7071      0.7037     0.0599  5
  test BA                     0.8124      0.8057     0.0402  5
  test F1                     0.7451      0.7391     0.0504  5
  test sensitivity            0.7652      0.7391     0.0659  5
  test specificity            0.8596      0.8723     0.0190  5
  test precision              0.7267      0.7391     0.0401  5
  test loss                   0.6719      0.6729     0.0067  5
  test TP                    17.6000     17.0000     1.5166  5
  test FP                     6.6000      6.0000     0.8944  5
  test FN                     5.4000      6.0000     1.5166  5
  test TN                    40.4000     41.0000     0.8944  5
  FPR (FP/(FP+TN))            0.1404      0.1277     0.0190  5
  FNR (FN/(FN+TP))            0.2348      0.2609     0.0659  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5073      0.5056     0.0097  5
  max valid BA                0.5073      0.5056     0.0097  5
  best valid F1               0.5561      0.5631     0.0461  5
  test BA                     0.4869      0.5000     0.0301  5
  test F1                     0.2850      0.3238     0.2779  5
  test sensitivity            0.4031      0.2615     0.4540  5
  test specificity            0.5708      0.7416     0.4831  5
  test precision              0.4100      0.4221     0.0236  3
  test loss                   0.6976      0.6942     0.0127  5
  test TP                    26.2000     17.0000    29.5076  5
  test FP                    38.2000     23.0000    42.9965  5
  test FN                    38.8000     48.0000    29.5076  5
  test TN                    50.8000     66.0000    42.9965  5
  FPR (FP/(FP+TN))            0.4292      0.2584     0.4831  5
  FNR (FN/(FN+TP))            0.5969      0.7385     0.4540  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5792      0.5694     0.0324  5
  max valid BA                0.5958      0.5694     0.0539  5
  best valid F1               0.5435      0.5344     0.0278  5
  test BA                     0.5431      0.5417     0.0211  5
  test F1                     0.5071      0.5085     0.0099  5
  test sensitivity            0.8778      0.8611     0.0847  5
  test specificity            0.2083      0.2083     0.1154  5
  test precision              0.3579      0.3529     0.0146  5
  test loss                   0.7041      0.7043     0.0080  5
  test TP                    31.6000     31.0000     3.0496  5
  test FP                    57.0000     57.0000     8.3066  5
  test FN                     4.4000      5.0000     3.0496  5
  test TN                    15.0000     15.0000     8.3066  5
  FPR (FP/(FP+TN))            0.7917      0.7917     0.1154  5
  FNR (FN/(FN+TP))            0.1222      0.1389     0.0847  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5735      0.5882     0.0294  5
  max valid BA                0.6088      0.6029     0.0397  5
  best valid F1               0.4662      0.4286     0.0784  5
  test BA                     0.5765      0.5735     0.0351  5
  test F1                     0.4352      0.4118     0.0549  5
  test sensitivity            0.4471      0.4118     0.1147  5
  test specificity            0.7059      0.7059     0.0907  5
  test precision              0.4363      0.4400     0.0498  5
  test loss                   0.6867      0.6850     0.0071  5
  test TP                     7.6000      7.0000     1.9494  5
  test FP                    10.0000     10.0000     3.0822  5
  test FN                     9.4000     10.0000     1.9494  5
  test TN                    24.0000     24.0000     3.0822  5
  FPR (FP/(FP+TN))            0.2941      0.2941     0.0907  5
  FNR (FN/(FN+TP))            0.5529      0.5882     0.1147  5
```

## AUC vs chemistry null model, in-sample increment (analysis/full_label_report.py)

```
/home/andrei/DL_project_5/DL_project/dataloader/New_dataloader.py:152: UserWarning: The given NumPy array is not writable, and PyTorch does not support non-writable tensors. This means writing to this tensor will result in undefined behavior. You may want to copy the array to protect its data or make it writable before converting it to a tensor. This type of warning will be suppressed for the rest of this program. (Triggered internally at /pytorch/torch/csrc/utils/tensor_numpy.cpp:213.)
  self.train_orig_indexes = torch.as_tensor(self.csvtrain["pair_id"].values, dtype=torch.long)
lipid class holdout for cral-trio : 7 classes, 134 positives held out, costing train 119 positives
  Cardiolipin, Diacylglycerol, Phosphatidylglycerophosphate, Phosphatidate, Phosphatidylethanolamine, Phosphatidylglycerol, Phosphatidylinositol
train : (1044, 12)
valid : (129, 12)
test : (128, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed0_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed0_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed0_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed0_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed0_epoch120.pt
lipid class holdout for cral-trio : 7 classes, 134 positives held out, costing train 119 positives
  Cardiolipin, Diacylglycerol, Phosphatidylglycerophosphate, Phosphatidate, Phosphatidylethanolamine, Phosphatidylglycerol, Phosphatidylinositol
train : (1044, 12)
valid : (129, 12)
test : (128, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed1_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed1_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed1_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed1_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed1_epoch120.pt
lipid class holdout for cral-trio : 7 classes, 134 positives held out, costing train 119 positives
  Cardiolipin, Diacylglycerol, Phosphatidylglycerophosphate, Phosphatidate, Phosphatidylethanolamine, Phosphatidylglycerol, Phosphatidylinositol
train : (1044, 12)
valid : (129, 12)
test : (128, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed2_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed2_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed2_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed2_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed2_epoch120.pt
lipid class holdout for cral-trio : 7 classes, 134 positives held out, costing train 119 positives
  Cardiolipin, Diacylglycerol, Phosphatidylglycerophosphate, Phosphatidate, Phosphatidylethanolamine, Phosphatidylglycerol, Phosphatidylinositol
train : (1044, 12)
valid : (129, 12)
test : (128, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed3_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed3_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed3_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed3_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed3_epoch120.pt
lipid class holdout for cral-trio : 7 classes, 134 positives held out, costing train 119 positives
  Cardiolipin, Diacylglycerol, Phosphatidylglycerophosphate, Phosphatidate, Phosphatidylethanolamine, Phosphatidylglycerol, Phosphatidylinositol
train : (1044, 12)
valid : (129, 12)
test : (128, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed4_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed4_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed4_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed4_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_CRAL-TRIO/dynamics/seed4_epoch120.pt
lipid class holdout for gltp : 5 classes, 51 positives held out, costing train 1 positives
  Hexosyl ceramide, Ceramide phosphate, Sphingomyelin, Dihexosyl ceramide, Sulfohexosyl ceramide
train : (1713, 12)
valid : (52, 12)
test : (50, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed0_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed0_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed0_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed0_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed0_epoch120.pt
lipid class holdout for gltp : 5 classes, 51 positives held out, costing train 1 positives
  Hexosyl ceramide, Ceramide phosphate, Sphingomyelin, Dihexosyl ceramide, Sulfohexosyl ceramide
train : (1713, 12)
valid : (52, 12)
test : (50, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed1_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed1_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed1_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed1_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed1_epoch120.pt
lipid class holdout for gltp : 5 classes, 51 positives held out, costing train 1 positives
  Hexosyl ceramide, Ceramide phosphate, Sphingomyelin, Dihexosyl ceramide, Sulfohexosyl ceramide
train : (1713, 12)
valid : (52, 12)
test : (50, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed2_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed2_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed2_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed2_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed2_epoch120.pt
lipid class holdout for gltp : 5 classes, 51 positives held out, costing train 1 positives
  Hexosyl ceramide, Ceramide phosphate, Sphingomyelin, Dihexosyl ceramide, Sulfohexosyl ceramide
train : (1713, 12)
valid : (52, 12)
test : (50, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed3_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed3_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed3_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed3_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed3_epoch120.pt
lipid class holdout for gltp : 5 classes, 51 positives held out, costing train 1 positives
  Hexosyl ceramide, Ceramide phosphate, Sphingomyelin, Dihexosyl ceramide, Sulfohexosyl ceramide
train : (1713, 12)
valid : (52, 12)
test : (50, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed4_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed4_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed4_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed4_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_GLTP/dynamics/seed4_epoch120.pt
lipid class holdout for ip_trans : 3 classes, 47 positives held out, costing train 213 positives
  Phosphatidate, Phosphatidylinositol, Phosphatidylcholine
train : (1089, 12)
valid : (71, 12)
test : (70, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed0_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed0_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed0_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed0_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed0_epoch120.pt
lipid class holdout for ip_trans : 3 classes, 47 positives held out, costing train 213 positives
  Phosphatidate, Phosphatidylinositol, Phosphatidylcholine
train : (1089, 12)
valid : (71, 12)
test : (70, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed1_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed1_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed1_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed1_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed1_epoch120.pt
lipid class holdout for ip_trans : 3 classes, 47 positives held out, costing train 213 positives
  Phosphatidate, Phosphatidylinositol, Phosphatidylcholine
train : (1089, 12)
valid : (71, 12)
test : (70, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed2_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed2_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed2_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed2_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed2_epoch120.pt
lipid class holdout for ip_trans : 3 classes, 47 positives held out, costing train 213 positives
  Phosphatidate, Phosphatidylinositol, Phosphatidylcholine
train : (1089, 12)
valid : (71, 12)
test : (70, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed3_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed3_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed3_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed3_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed3_epoch120.pt
lipid class holdout for ip_trans : 3 classes, 47 positives held out, costing train 213 positives
  Phosphatidate, Phosphatidylinositol, Phosphatidylcholine
train : (1089, 12)
valid : (71, 12)
test : (70, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed4_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed4_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed4_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed4_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_IP_trans/dynamics/seed4_epoch120.pt
lipid class holdout for lbp_bpi_cetp : 4 classes, 47 positives held out, costing train 193 positives
  Bismonoacylglycerolphosphate, Phosphatidylserine, Phosphatidylinositol, Phosphatidylcholine
train : (1164, 12)
valid : (71, 12)
test : (70, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed0_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed0_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed0_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed0_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed0_epoch120.pt
lipid class holdout for lbp_bpi_cetp : 4 classes, 47 positives held out, costing train 193 positives
  Bismonoacylglycerolphosphate, Phosphatidylserine, Phosphatidylinositol, Phosphatidylcholine
train : (1164, 12)
valid : (71, 12)
test : (70, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed1_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed1_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed1_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed1_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed1_epoch120.pt
lipid class holdout for lbp_bpi_cetp : 4 classes, 47 positives held out, costing train 193 positives
  Bismonoacylglycerolphosphate, Phosphatidylserine, Phosphatidylinositol, Phosphatidylcholine
train : (1164, 12)
valid : (71, 12)
test : (70, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed2_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed2_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed2_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed2_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed2_epoch120.pt
lipid class holdout for lbp_bpi_cetp : 4 classes, 47 positives held out, costing train 193 positives
  Bismonoacylglycerolphosphate, Phosphatidylserine, Phosphatidylinositol, Phosphatidylcholine
train : (1164, 12)
valid : (71, 12)
test : (70, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed3_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed3_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed3_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed3_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed3_epoch120.pt
lipid class holdout for lbp_bpi_cetp : 4 classes, 47 positives held out, costing train 193 positives
  Bismonoacylglycerolphosphate, Phosphatidylserine, Phosphatidylinositol, Phosphatidylcholine
train : (1164, 12)
valid : (71, 12)
test : (70, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed4_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed4_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed4_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed4_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_LBP_BPI_CETP/dynamics/seed4_epoch120.pt
lipid class holdout for start : 4 classes, 129 positives held out, costing train 191 positives
  Ceramide, Triacylglycerol, Phosphatidylcholine, Phosphatidylethanolamine
train : (879, 12)
valid : (153, 12)
test : (154, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed0_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed0_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed0_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed0_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed0_epoch120.pt
lipid class holdout for start : 4 classes, 129 positives held out, costing train 191 positives
  Ceramide, Triacylglycerol, Phosphatidylcholine, Phosphatidylethanolamine
train : (879, 12)
valid : (153, 12)
test : (154, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed1_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed1_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed1_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed1_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed1_epoch120.pt
lipid class holdout for start : 4 classes, 129 positives held out, costing train 191 positives
  Ceramide, Triacylglycerol, Phosphatidylcholine, Phosphatidylethanolamine
train : (879, 12)
valid : (153, 12)
test : (154, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed2_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed2_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed2_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed2_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed2_epoch120.pt
lipid class holdout for start : 4 classes, 129 positives held out, costing train 191 positives
  Ceramide, Triacylglycerol, Phosphatidylcholine, Phosphatidylethanolamine
train : (879, 12)
valid : (153, 12)
test : (154, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed3_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed3_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed3_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed3_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed3_epoch120.pt
lipid class holdout for start : 4 classes, 129 positives held out, costing train 191 positives
  Ceramide, Triacylglycerol, Phosphatidylcholine, Phosphatidylethanolamine
train : (879, 12)
valid : (153, 12)
test : (154, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed4_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed4_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed4_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed4_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_START/dynamics/seed4_epoch120.pt
lipid class holdout for lipocalin : 14 classes, 72 positives held out, costing train 220 positives
  docosapentaenoate, nonadecenoate, octadecadienoate, eicosatrienoate, eicosapentaenoate, heptadecenoate, hexadecenoate, eicosatetraenoate, Retinol, octadecenoate, docosatetraenoate, Lysophosphatidylethanolamine, Lysophosphatidylglycerol, Phosphatidylcholine
train : (981, 12)
valid : (108, 12)
test : (108, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed0_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed0_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed0_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed0_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed0_epoch120.pt
lipid class holdout for lipocalin : 14 classes, 72 positives held out, costing train 220 positives
  docosapentaenoate, nonadecenoate, octadecadienoate, eicosatrienoate, eicosapentaenoate, heptadecenoate, hexadecenoate, eicosatetraenoate, Retinol, octadecenoate, docosatetraenoate, Lysophosphatidylethanolamine, Lysophosphatidylglycerol, Phosphatidylcholine
train : (981, 12)
valid : (108, 12)
test : (108, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed1_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed1_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed1_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed1_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed1_epoch120.pt
lipid class holdout for lipocalin : 14 classes, 72 positives held out, costing train 220 positives
  docosapentaenoate, nonadecenoate, octadecadienoate, eicosatrienoate, eicosapentaenoate, heptadecenoate, hexadecenoate, eicosatetraenoate, Retinol, octadecenoate, docosatetraenoate, Lysophosphatidylethanolamine, Lysophosphatidylglycerol, Phosphatidylcholine
train : (981, 12)
valid : (108, 12)
test : (108, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed2_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed2_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed2_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed2_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed2_epoch120.pt
lipid class holdout for lipocalin : 14 classes, 72 positives held out, costing train 220 positives
  docosapentaenoate, nonadecenoate, octadecadienoate, eicosatrienoate, eicosapentaenoate, heptadecenoate, hexadecenoate, eicosatetraenoate, Retinol, octadecenoate, docosatetraenoate, Lysophosphatidylethanolamine, Lysophosphatidylglycerol, Phosphatidylcholine
train : (981, 12)
valid : (108, 12)
test : (108, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed3_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed3_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed3_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed3_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed3_epoch120.pt
lipid class holdout for lipocalin : 14 classes, 72 positives held out, costing train 220 positives
  docosapentaenoate, nonadecenoate, octadecadienoate, eicosatrienoate, eicosapentaenoate, heptadecenoate, hexadecenoate, eicosatetraenoate, Retinol, octadecenoate, docosatetraenoate, Lysophosphatidylethanolamine, Lysophosphatidylglycerol, Phosphatidylcholine
train : (981, 12)
valid : (108, 12)
test : (108, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed4_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed4_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed4_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed4_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_lipocalin/dynamics/seed4_epoch120.pt
lipid class holdout for scp2 : 7 classes, 34 positives held out, costing train 126 positives
  Lysophosphatidylcholine, Lysophosphatidylglycerol, Triacylglycerol, docosatrienoate, Lysophosphatidylethanolamine, eicosatetraenoate, Phosphatidylglycerol
train : (1395, 12)
valid : (51, 12)
test : (51, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed0_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed0_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed0_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed0_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed0_epoch120.pt
lipid class holdout for scp2 : 7 classes, 34 positives held out, costing train 126 positives
  Lysophosphatidylcholine, Lysophosphatidylglycerol, Triacylglycerol, docosatrienoate, Lysophosphatidylethanolamine, eicosatetraenoate, Phosphatidylglycerol
train : (1395, 12)
valid : (51, 12)
test : (51, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed1_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed1_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed1_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed1_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed1_epoch120.pt
lipid class holdout for scp2 : 7 classes, 34 positives held out, costing train 126 positives
  Lysophosphatidylcholine, Lysophosphatidylglycerol, Triacylglycerol, docosatrienoate, Lysophosphatidylethanolamine, eicosatetraenoate, Phosphatidylglycerol
train : (1395, 12)
valid : (51, 12)
test : (51, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed2_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed2_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed2_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed2_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed2_epoch120.pt
lipid class holdout for scp2 : 7 classes, 34 positives held out, costing train 126 positives
  Lysophosphatidylcholine, Lysophosphatidylglycerol, Triacylglycerol, docosatrienoate, Lysophosphatidylethanolamine, eicosatetraenoate, Phosphatidylglycerol
train : (1395, 12)
valid : (51, 12)
test : (51, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed3_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed3_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed3_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed3_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed3_epoch120.pt
lipid class holdout for scp2 : 7 classes, 34 positives held out, costing train 126 positives
  Lysophosphatidylcholine, Lysophosphatidylglycerol, Triacylglycerol, docosatrienoate, Lysophosphatidylethanolamine, eicosatetraenoate, Phosphatidylglycerol
train : (1395, 12)
valid : (51, 12)
test : (51, 12)
lipid prior baseline valid : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
lipid prior baseline test : balanced accuracy 0.500 by lipid, 0.500 by class | 0% of rows have their lipid in train
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed4_epoch1.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed4_epoch10.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed4_epoch49.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed4_epoch51.pt
missing : /home/andrei/DL_project_5/DL_project/models/descriptors_path_v2/groups_scp2/dynamics/seed4_epoch120.pt
no checkpoints scored
(full_label_report.py exited non-zero -- most likely no --save_model_in_dynamics checkpoints saved for this label)
```
