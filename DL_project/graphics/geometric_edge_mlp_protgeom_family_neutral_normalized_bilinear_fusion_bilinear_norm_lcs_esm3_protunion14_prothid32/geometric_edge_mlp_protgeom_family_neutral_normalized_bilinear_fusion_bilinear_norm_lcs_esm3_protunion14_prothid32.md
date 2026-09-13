# geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protunion14_prothid32

## Summary (analysis/summarize_label.py)

```
conda is not available in this environment.
Could not activate Kalinin_project_LP (create it with: source /home/andrei/DL_project_5/DL_project/scripts/tools/enter_project_env.sh); using current python3: /usr/bin/python3
Summary: 'geometric_edge_mlp_protgeom_family_neutral_normalized_bilinear_fusion_bilinear_norm_lcs_esm3_protunion14_prothid32'
rows: 20

=== Sensitivity / specificity by group (test / train / valid) ===
group                     n   test_sens   test_spec  train_sens  train_spec  valid_sens  valid_spec
groups_anionic            5      0.6366      0.5152      0.9433      0.8694      0.6409      0.5351
groups_choline            5      0.4090      0.8048      0.8774      0.7353      0.5571      0.7321
groups_phosphorus_free    5      0.4516      0.8070      0.9208      0.8000      0.5533      0.7929
groups_sphingolipids      5      0.3091      0.6727      0.7511      0.6889      0.4485      0.7630
ALL                      20      0.4516      0.6999      0.8731      0.7734      0.5500      0.7058

=== Overall ===
metric                        mean      median        std  n
checkpoint valid BA         0.6032      0.5940     0.0629  20
max valid BA                0.6279      0.6183     0.0607  20
best valid F1               0.5531      0.5619     0.0739  20
test BA                     0.5758      0.5618     0.0863  20
test AUC                    0.5954      0.6151     0.1217  20
test AUC in-protein         0.6002      0.5921     0.1222  20
  (proteins averaged)       7.9000      8.5000     3.5968  20
test AUC in-protein (pairs)      0.6053      0.6158     0.1231  20
  (proteins contributing)     11.7000     14.0000     5.3024  20
test F1                     0.4314      0.4817     0.1817  20
test sensitivity            0.4516      0.4355     0.2435  20
test specificity            0.6999      0.7054     0.1837  20
test precision              0.4895      0.4624     0.1464  19
test loss                   1.0015      0.8368     0.3616  20
FPR (FP/(FP+TN))            0.3001      0.2946     0.1837  20
FNR (FN/(FN+TP))            0.5484      0.5645     0.2435  20

=== abs(sensitivity-specificity) gap: mean=0.3797 median=0.3362 n=20 ===
sensitivity std across seeds (by group): mean=0.2193 median=0.2127 n=4
specificity std across seeds (by group): mean=0.1345 median=0.1063 n=4

=== By group ===
groups_anionic (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5718      0.5676     0.0368  5
  max valid BA                0.5880      0.5891     0.0271  5
  best valid F1               0.5454      0.5540     0.0264  5
  test BA                     0.5759      0.5755     0.0443  5
  test AUC                    0.5828      0.5754     0.0341  5
  test AUC in-protein         0.5631      0.5794     0.0258  5
    (proteins averaged)      12.2000     12.0000     0.4472  5
  test AUC in-protein (pairs)      0.5715      0.5732     0.0098  5
    (proteins contributing)     16.4000     17.0000     1.5166  5
  test F1                     0.5207      0.5244     0.0676  5
  test sensitivity            0.6366      0.6559     0.1344  5
  test specificity            0.5152      0.5166     0.0825  5
  test precision              0.4452      0.4470     0.0343  5
  test loss                   1.3665      1.3645     0.1035  5
  FPR (FP/(FP+TN))            0.4848      0.4834     0.0825  5
  FNR (FN/(FN+TP))            0.3634      0.3441     0.1344  5

groups_choline (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5932      0.5848     0.0460  5
  max valid BA                0.6446      0.6473     0.0312  5
  best valid F1               0.5725      0.5992     0.0522  5
  test BA                     0.6069      0.6537     0.0731  5
  test AUC                    0.6662      0.6616     0.0766  5
  test AUC in-protein         0.7076      0.7197     0.0207  5
    (proteins averaged)       9.8000     10.0000     0.4472  5
  test AUC in-protein (pairs)      0.6849      0.6881     0.0384  5
    (proteins contributing)     14.8000     15.0000     0.4472  5
  test F1                     0.4646      0.5233     0.1531  5
  test sensitivity            0.4090      0.4054     0.1807  5
  test specificity            0.8048      0.8802     0.1156  5
  test precision              0.5842      0.5581     0.1384  5
  test loss                   0.8153      0.7297     0.2354  5
  FPR (FP/(FP+TN))            0.1952      0.1198     0.1156  5
  FNR (FN/(FN+TP))            0.5910      0.5946     0.1807  5

groups_phosphorus_free (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.6606      0.6863     0.0712  5
  max valid BA                0.6731      0.6863     0.0781  5
  best valid F1               0.5642      0.5818     0.1162  5
  test BA                     0.6293      0.5971     0.1015  5
  test AUC                    0.6845      0.6587     0.0672  5
  test AUC in-protein         0.6729      0.6177     0.1300  5
    (proteins averaged)       6.6000      7.0000     1.1402  5
  test AUC in-protein (pairs)      0.7136      0.7071     0.0808  5
    (proteins contributing)     12.2000     13.0000     2.1679  5
  test F1                     0.4736      0.4444     0.1733  5
  test sensitivity            0.4516      0.4194     0.2446  5
  test specificity            0.8070      0.7895     0.0969  5
  test precision              0.5749      0.5385     0.1141  5
  test loss                   0.7824      0.7620     0.1662  5
  FPR (FP/(FP+TN))            0.1930      0.2105     0.0969  5
  FNR (FN/(FN+TP))            0.5484      0.5806     0.2446  5

groups_sphingolipids (n=5):
  metric                        mean      median        std  n
  checkpoint valid BA         0.5874      0.5707     0.0667  5
  max valid BA                0.6057      0.5800     0.0645  5
  best valid F1               0.5300      0.5500     0.0875  5
  test BA                     0.4909      0.5000     0.0631  5
  test AUC                    0.4482      0.4755     0.1240  5
  test AUC in-protein         0.4574      0.4421     0.0685  5
    (proteins averaged)       3.0000      3.0000     0.0000  5
  test AUC in-protein (pairs)      0.4511      0.4298     0.1004  5
    (proteins contributing)      3.4000      3.0000     0.5477  5
  test F1                     0.2669      0.2182     0.2266  5
  test sensitivity            0.3091      0.1818     0.3174  5
  test specificity            0.6727      0.7091     0.2429  5
  test precision              0.3196      0.3380     0.1240  4
  test loss                   1.0418      0.6968     0.5052  5
  FPR (FP/(FP+TN))            0.3273      0.2909     0.2429  5
  FNR (FN/(FN+TP))            0.6909      0.8182     0.3174  5
```

## AUC vs chemistry null model, in-sample increment

```
########## split = valid ##########

--- null model (null_model.py), features = lipid4 (chain,hbond,heavy,unsaturation), epoch 120 ---
=== mean over seeds ===
                 sim_to_train_pos  null_AUC_k15  net_AUC  proteins  null_AUC_prot_k15  net_AUC_prot  lipids  null_AUC_lipid_k15  net_AUC_lipid  null_AUC_pair_k15  net_AUC_pair
fam                                                                                                                                                                            
anionic                     0.631         0.495    0.550      11.6              0.530         0.474     5.4               0.501          0.614              0.501         0.555
choline                     0.687         0.646    0.497       9.4              0.696         0.590     1.8               0.565          0.315              0.622         0.498
phosphorus_free             0.396         0.499    0.636       1.2              0.739         0.644     5.4               0.514          0.744              0.484         0.625
sphingolipids               0.599         0.543    0.457       1.6              0.496         0.380     3.2               0.537          0.477              0.490         0.454

=== mean AUC (files/signal_state.md 6.4: fam column in the raw table/cache carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_k15      0.546               0.519                  0.038                     0.070
net_AUC           0.535               0.535                  0.078                     0.078

=== the same rows ranked INSIDE each protein ===
119 protein blocks across 20 family-seed splits carry a usable ranking (median 6 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_prot_k15      0.608               0.565                  0.040                     0.120
net_AUC_prot           0.522               0.511                  0.099                     0.119

=== the same rows ranked INSIDE each lipid class ===
79 lipid class blocks across 20 family-seed splits carry a usable ranking (median 4 lipid class groups per split)
                    all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_lipid_k15      0.529               0.506                  0.073                     0.028
net_AUC_lipid           0.537               0.539                  0.109                     0.184

=== the same rows ranked INSIDE each protein AND inside each lipid class jointly (per_pair_auc) ===
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
null_AUC_pair_k15      0.526               0.517                  0.031                     0.066
net_AUC_pair           0.533               0.532                  0.096                     0.074

--- increment over chemistry (interaction_increment.py) ---
=== valid block, k=15, null-model entity = FullIdentityOfLipid ===

1. Each score on its own, mean over family+seed, by epoch
        chem    net  chem_prot  net_prot
epoch                                   
1      0.516  0.504      0.501     0.488
10     0.516  0.455      0.501     0.463
49     0.516  0.553      0.501     0.531
51     0.516  0.561      0.501     0.537
120    0.516  0.535      0.501     0.522

2. Increment of the network over chemistry (in-sample fit = UPPER BOUND), mean over family+seed, by epoch
       fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
epoch                                                                                     
1         0.628         0.649      0.022          0.708              0.717           0.009
10        0.628         0.649      0.021          0.708              0.718           0.010
49        0.628         0.650      0.022          0.708              0.716           0.009
51        0.628         0.649      0.021          0.708              0.721           0.013
120       0.628         0.652      0.025          0.708              0.720           0.012

3. mean over seeds, epoch 120
                  chem    net  chem_prot  net_prot  fit_chem  fit_chem_net  increment  fit_chem_prot  fit_chem_net_prot  increment_prot
fam                                                                                                                                    
anionic          0.585  0.550      0.566     0.474     0.585         0.598      0.013          0.657              0.670           0.013
choline          0.671  0.497      0.671     0.590     0.671         0.676      0.005          0.767              0.776           0.009
phosphorus_free  0.289  0.636      0.289     0.644     0.711         0.718      0.007          0.772              0.772           0.000
sphingolipids    0.521  0.457      0.480     0.380     0.544         0.618      0.074          0.635              0.662           0.027

=== mean AUC + increment, epoch 120 (files/signal_state.md 6.4: fam column in the raw table carries the WORKING-three/other-four split) ===
              all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem              0.516               0.553                  0.041                     0.164
net               0.535               0.535                  0.078                     0.078
fit_chem          0.628               0.637                  0.034                     0.077
fit_chem_net      0.652               0.647                  0.033                     0.055
increment         0.025               0.007                  0.020                     0.033

=== the same rows ranked INSIDE each protein, epoch 120 ===
158 protein blocks across 20 family-seed splits carry a usable ranking (median 8 protein groups per split)
                   all seven  all seven (median)  all seven (std seeds)  all seven (std families)
chem_prot              0.501               0.527                  0.043                     0.162
net_prot               0.522               0.511                  0.099                     0.119
fit_chem_prot          0.708               0.701                  0.042                     0.072
fit_chem_net_prot      0.720               0.710                  0.038                     0.062
increment_prot         0.012               0.010                  0.020                     0.011
```
