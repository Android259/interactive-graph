# thematical_paths_geom_chem_orthogonal_init_bn_scale

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'thematical_paths_geom_chem_orthogonal_init_bn_scale'
rows: 35

=== Sensitivity / specificity by group (test / train / valid) ===
group                  n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_CRAL-TRIO       5      0.2119      0.8623      0.7503      0.8274      0.2687      0.8806
groups_GLTP            5      0.5600      0.7680      0.8732      0.7753      0.5769      0.7077
groups_IP_trans        5      0.4087      0.5660      0.8501      0.6937      0.5167      0.6213
groups_LBP_BPI_CETP    5      0.1913      0.9064      0.8887      0.8088      0.2917      0.8809
groups_START           5      0.5292      0.5618      0.7952      0.7352      0.5094      0.6180
groups_lipocalin       5      0.4611      0.5694      0.7291      0.6401      0.4778      0.5944
groups_scp2            5      0.4353      0.7176      0.6508      0.7189      0.5294      0.6882
ALL                   35      0.3997      0.7074      0.7910      0.7428      0.4529      0.7130

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5830      0.5694     0.0802  35
max valid BA                0.6183      0.6124     0.0814  35
best valid F1               0.5499      0.5385     0.1168  35
test BA                     0.5535      0.5441     0.0940  35
test F1                     0.3830      0.3636     0.1985  35
test sensitivity            0.3997      0.3134     0.2742  35
test specificity            0.7074      0.8000     0.2638  35
test precision              0.5184      0.4580     0.1913  32
test loss                   0.8015      0.7253     0.2006  35
FPR (FP/(FP+TN))            0.2926      0.2000     0.2638  35
FNR (FN/(FN+TP))            0.6003      0.6866     0.2742  35

=== abs(sensitivity-specificity) gap: mean=0.5150 median=0.5476 n=35 ===

=== By group ===
groups_CRAL-TRIO (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5747      0.6122     0.0558  5
  max valid BA                0.6130      0.6384     0.0513  5
  best valid F1               0.6291      0.6509     0.0598  5
  test BA                     0.5371      0.5218     0.0345  5
  test F1                     0.2862      0.3226     0.2014  5
  test sensitivity            0.2119      0.2239     0.1653  5
  test specificity            0.8623      0.8197     0.1015  5
  test precision              0.6252      0.6364     0.0329  4
  test loss                   1.0121      1.0469     0.1995  5
  FPR (FP/(FP+TN))            0.1377      0.1803     0.1015  5
  FNR (FN/(FN+TP))            0.7881      0.7761     0.1653  5

groups_GLTP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6423      0.5962     0.1462  5
  max valid BA                0.7038      0.6731     0.1251  5
  best valid F1               0.6762      0.6415     0.1430  5
  test BA                     0.6640      0.7000     0.1513  5
  test F1                     0.6086      0.6667     0.2056  5
  test sensitivity            0.5600      0.6000     0.2417  5
  test specificity            0.7680      0.8000     0.2047  5
  test precision              0.7264      0.7500     0.1951  5
  test loss                   0.7258      0.6316     0.2615  5
  FPR (FP/(FP+TN))            0.2320      0.2000     0.2047  5
  FNR (FN/(FN+TP))            0.4400      0.4000     0.2417  5

groups_IP_trans (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5690      0.5616     0.0646  5
  max valid BA                0.6265      0.6454     0.0698  5
  best valid F1               0.5288      0.5161     0.0633  5
  test BA                     0.4873      0.5347     0.1074  5
  test F1                     0.3558      0.3529     0.0722  5
  test sensitivity            0.4087      0.3913     0.1525  5
  test specificity            0.5660      0.5957     0.2970  5
  test precision              0.3662      0.4000     0.1301  5
  test loss                   0.7973      0.6976     0.2394  5
  FPR (FP/(FP+TN))            0.4340      0.4043     0.2970  5
  FNR (FN/(FN+TP))            0.5913      0.6087     0.1525  5

groups_LBP_BPI_CETP (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5863      0.6037     0.0484  5
  max valid BA                0.6254      0.6250     0.0588  5
  best valid F1               0.4855      0.5172     0.1058  5
  test BA                     0.5488      0.5560     0.0364  5
  test F1                     0.2663      0.3226     0.1141  5
  test sensitivity            0.1913      0.2174     0.0902  5
  test specificity            0.9064      0.9149     0.0683  5
  test precision              0.6040      0.6000     0.2504  5
  test loss                   0.7823      0.8022     0.1253  5
  FPR (FP/(FP+TN))            0.0936      0.0851     0.0683  5
  FNR (FN/(FN+TP))            0.8087      0.7826     0.0902  5

groups_START (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5637      0.5531     0.0522  5
  max valid BA                0.5906      0.5973     0.0459  5
  best valid F1               0.5105      0.5775     0.1497  5
  test BA                     0.5455      0.5086     0.0862  5
  test F1                     0.4602      0.4663     0.1793  5
  test sensitivity            0.5292      0.5846     0.3135  5
  test specificity            0.5618      0.5955     0.2515  5
  test precision              0.4619      0.4412     0.0713  5
  test loss                   0.8381      0.8118     0.1616  5
  FPR (FP/(FP+TN))            0.4382      0.4045     0.2515  5
  FNR (FN/(FN+TP))            0.4708      0.4154     0.3135  5

groups_lipocalin (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5361      0.5278     0.0388  5
  max valid BA                0.5514      0.5417     0.0416  5
  best valid F1               0.4688      0.5000     0.0695  5
  test BA                     0.5153      0.5000     0.0586  5
  test F1                     0.3182      0.2857     0.2187  5
  test sensitivity            0.4611      0.2778     0.4220  5
  test specificity            0.5694      0.6667     0.3778  5
  test precision              0.3374      0.3205     0.0538  4
  test loss                   0.8132      0.7313     0.1708  5
  FPR (FP/(FP+TN))            0.4306      0.3333     0.3778  5
  FNR (FN/(FN+TP))            0.5389      0.7222     0.4220  5

groups_scp2 (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6088      0.6029     0.1033  5
  max valid BA                0.6176      0.6029     0.0997  5
  best valid F1               0.5501      0.5385     0.0756  5
  test BA                     0.5765      0.5735     0.0610  5
  test F1                     0.3858      0.4865     0.2186  5
  test sensitivity            0.4353      0.4118     0.2959  5
  test specificity            0.7176      0.7353     0.2849  5
  test precision              0.4866      0.4437     0.1478  4
  test loss                   0.6419      0.6894     0.0937  5
  FPR (FP/(FP+TN))            0.2824      0.2647     0.2849  5
  FNR (FN/(FN+TP))            0.5647      0.5882     0.2959  5
```

## AUC vs chemistry null model, in-sample increment

(skipped: SKIP_AUC=1 -- rerun without it to fill this in: `python3 analysis/full_label_report.py --label thematical_paths_geom_chem_orthogonal_init_bn_scale --seeds=0,1,2,3,4`)
