# geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protbind6

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_attention_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protbind6'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6022      0.5166      0.9179      0.7960      0.5957      0.5748
groups_choline            5      0.4036      0.7138      0.9309      0.7353      0.5429      0.7250
groups_phosphorus_free    5      0.1677      0.8912      0.9190      0.6340      0.4933      0.8464
groups_sphingolipids      5      0.4848      0.4945      0.7989      0.6783      0.5273      0.6407
ALL                      20      0.4146      0.6540      0.8917      0.7109      0.5398      0.6968

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.5696      0.5631     0.0537  20
max valid BA                0.6183      0.5959     0.0515  20
best valid F1               0.5568      0.5500     0.0557  20
test BA                     0.5343      0.5390     0.0648  20
test AUC                    0.5512      0.5746     0.1181  20
test AUC in-protein         0.5424      0.5442     0.1316  20
  (proteins averaged)       7.9000      8.5000     3.5968  20
test AUC in-protein (pairs)      0.5374      0.5666     0.1288  20
  (proteins contributing)     11.7000     14.0000     5.3024  20
test F1                     0.3622      0.4110     0.2002  20
test sensitivity            0.4146      0.3916     0.3171  20
test specificity            0.6540      0.7017     0.2723  20
test precision              0.4414      0.4329     0.1932  20
test loss                   0.9425      0.8301     0.3135  20
FPR (FP/(FP+TN))            0.3460      0.2983     0.2723  20
FNR (FN/(FN+TP))            0.5854      0.6084     0.3171  20

=== abs(sensitivity-specificity) gap: mean=0.5242 median=0.5788 n=20 ===

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5765      0.5871     0.0210  5
  max valid BA                0.5853      0.5871     0.0233  5
  best valid F1               0.5401      0.5447     0.0161  5
  test BA                     0.5594      0.5445     0.0306  5
  test AUC                    0.5700      0.5538     0.0338  5
  test AUC in-protein         0.5468      0.5372     0.0273  5
    (proteins averaged)      12.2000     12.0000     0.4472  5
  test AUC in-protein (pairs)      0.5660      0.5631     0.0473  5
    (proteins contributing)     16.4000     17.0000     1.5166  5
  test F1                     0.4974      0.4911     0.0563  5
  test sensitivity            0.6022      0.5914     0.1872  5
  test specificity            0.5166      0.6159     0.1908  5
  test precision              0.4387      0.4314     0.0354  5
  test loss                   1.1942      1.2895     0.2662  5
  FPR (FP/(FP+TN))            0.4834      0.3841     0.1908  5
  FNR (FN/(FN+TP))            0.3978      0.4086     0.1872  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5872      0.5952     0.0557  5
  max valid BA                0.6339      0.6354     0.0402  5
  best valid F1               0.5742      0.6116     0.0726  5
  test BA                     0.5587      0.5275     0.0604  5
  test AUC                    0.6253      0.6443     0.0494  5
  test AUC in-protein         0.6693      0.6956     0.0622  5
    (proteins averaged)       9.8000     10.0000     0.4472  5
  test AUC in-protein (pairs)      0.6144      0.6330     0.0558  5
    (proteins contributing)     14.8000     15.0000     0.4472  5
  test F1                     0.3845      0.3858     0.2319  5
  test sensitivity            0.4036      0.3423     0.2867  5
  test specificity            0.7138      0.7126     0.1856  5
  test precision              0.5786      0.4780     0.2392  5
  test loss                   0.7984      0.8104     0.0978  5
  FPR (FP/(FP+TN))            0.2862      0.2874     0.1856  5
  FNR (FN/(FN+TP))            0.5964      0.6577     0.2867  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5692      0.5321     0.0898  5
  max valid BA                0.6699      0.6720     0.0619  5
  best valid F1               0.5755      0.5417     0.0690  5
  test BA                     0.5295      0.5308     0.0810  5
  test AUC                    0.5769      0.6203     0.1677  5
  test AUC in-protein         0.5373      0.5512     0.1820  5
    (proteins averaged)       6.6000      7.0000     1.1402  5
  test AUC in-protein (pairs)      0.5472      0.5786     0.2102  5
    (proteins contributing)     12.2000     13.0000     2.1679  5
  test F1                     0.2201      0.1667     0.1996  5
  test sensitivity            0.1677      0.0968     0.1787  5
  test specificity            0.8912      0.8596     0.0600  5
  test precision              0.4151      0.4667     0.2484  5
  test loss                   0.8036      0.8294     0.1453  5
  FPR (FP/(FP+TN))            0.1088      0.1404     0.0600  5
  FNR (FN/(FN+TP))            0.8323      0.9032     0.1787  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5456      0.5429     0.0306  5
  max valid BA                0.5840      0.5884     0.0127  5
  best valid F1               0.5374      0.5500     0.0531  5
  test BA                     0.4897      0.5000     0.0691  5
  test AUC                    0.4327      0.4309     0.0942  5
  test AUC in-protein         0.4164      0.4113     0.0672  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4219      0.4231     0.0638  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.3468      0.3396     0.2113  5
  test sensitivity            0.4848      0.2727     0.4495  5
  test specificity            0.4945      0.6909     0.3843  5
  test precision              0.3332      0.3750     0.1343  5
  test loss                   0.9736      0.7172     0.4848  5
  FPR (FP/(FP+TN))            0.5055      0.3091     0.3843  5
  FNR (FN/(FN+TP))            0.5152      0.7273     0.4495  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.547      11.6              0.530         0.471     5.4               0.501          0.615              0.501         0.549
choline                     0.687         0.646    0.543       9.4              0.696         0.622     1.8               0.565          0.531              0.622         0.549
phosphorus_free             0.396         0.499    0.584       1.2              0.739         0.610     5.4               0.514          0.650              0.484         0.633
sphingolipids               0.599         0.543    0.383       1.6              0.496         0.299     3.2               0.537          0.399              0.490         0.380

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                      0.07
net_AUC           0.514               0.532                  0.080                      0.09

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.500               0.516                  0.103                     0.151

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.549               0.560                  0.131                     0.112

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.528               0.550                  0.067                     0.106

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.516  0.491      0.501     0.471
10     0.516  0.489      0.501     0.502
49     0.516  0.513      0.501     0.495
51     0.516  0.523      0.501     0.502
120    0.516  0.514      0.501     0.500

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.644      0.016          0.708              0.717           0.010
10        0.628         0.657      0.030          0.708              0.730           0.023
49        0.628         0.671      0.043          0.708              0.746           0.038
51        0.628         0.671      0.043          0.708              0.746           0.039
120       0.628         0.672      0.044          0.708              0.738           0.030

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.585  0.547      0.566     0.471     0.585         0.606      0.021          0.657              0.665           0.008
choline          0.671  0.543      0.671     0.622     0.671         0.681      0.010          0.767              0.773           0.006
phosphorus_free  0.289  0.584      0.289     0.610     0.711         0.742      0.030          0.772              0.782           0.010
sphingolipids    0.521  0.383      0.480     0.299     0.544         0.658      0.114          0.635              0.731           0.097

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.516               0.553                  0.041                     0.164
net               0.514               0.532                  0.080                     0.090
fit_chem          0.628               0.637                  0.034                     0.077
fit_chem_net      0.672               0.676                  0.043                     0.056
increment         0.044               0.020                  0.033                     0.048

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.501               0.527                  0.043                     0.162
net_prot               0.500               0.516                  0.103                     0.151
fit_chem_prot          0.708               0.701                  0.042                     0.072
fit_chem_net_prot      0.738               0.744                  0.047                     0.053
increment_prot         0.030               0.007                  0.040                     0.044
```
