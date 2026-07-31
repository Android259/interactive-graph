# Standard configuration timestamps

Source: `metrics_summary.csv`

Standard configuration filter:

- `single_gat_layer = 1.0`
- `class_weights = 1.0`
- `transformer_conv` empty
- `gine_conv` empty
- `lipid_fragments_treatment = 0`
- `protein_pooling = 1`
- `lr = 0.0001`
- `weight_decay = 0.00001`
- `hiddim = 64.0`
- `ep = 150.0`
- `batch = 16.0`
- `grab_loss = 0.0`

Rows in table: 48.
Unique `exclusion_set + seed` after latest-timestamp deduplication: 43.
Expected complete grid: 45.

Missing group-seed runs after deduplication:

- `groups_CRAL-TRIO`, seed `0`
- `groups_CRAL-TRIO`, seed `2`

Duplicate group-seed entries in the raw table:

- `groups_CRAL-TRIO`, seed `4`
- `groups_START`, seed `0`
- `groups_START`, seed `2`
- `groups_START`, seed `4`
- `groups_lipocalin`, seed `0`

## Raw table rows

| datetime | exclusion_set | seed | run_status |
|---|---|---:|---|
| 2026-06-30 00:32:25 | groups_CRAL-TRIO | 1 | complete |
| 2026-06-29 20:07:56 | groups_CRAL-TRIO | 3 | complete |
| 2026-06-29 20:15:24 | groups_CRAL-TRIO | 4 | complete |
| 2026-06-30 00:40:14 | groups_CRAL-TRIO | 4 | complete |
| 2026-06-29 21:12:32 | groups_GLTP | 0 | complete |
| 2026-06-29 21:14:00 | groups_GLTP | 1 | complete |
| 2026-06-29 21:14:00 | groups_GLTP | 2 | complete |
| 2026-06-29 21:14:00 | groups_GLTP | 3 | complete |
| 2026-06-29 21:14:00 | groups_GLTP | 4 | complete |
| 2026-06-29 21:18:30 | groups_IP_trans | 0 | complete |
| 2026-06-29 21:24:43 | groups_IP_trans | 1 | complete |
| 2026-06-29 21:25:11 | groups_IP_trans | 2 | complete |
| 2026-06-29 21:44:34 | groups_IP_trans | 3 | complete |
| 2026-06-29 21:59:56 | groups_IP_trans | 4 | complete |
| 2026-06-29 22:52:57 | groups_LBP_BPI_CETP | 0 | complete |
| 2026-06-29 22:54:04 | groups_LBP_BPI_CETP | 1 | complete |
| 2026-06-29 22:55:43 | groups_LBP_BPI_CETP | 2 | complete |
| 2026-06-29 22:55:46 | groups_LBP_BPI_CETP | 3 | complete |
| 2026-06-29 22:56:24 | groups_LBP_BPI_CETP | 4 | complete |
| 2026-06-29 23:09:58 | groups_ML | 0 | complete |
| 2026-06-29 23:15:35 | groups_ML | 1 | complete |
| 2026-06-29 23:16:54 | groups_ML | 2 | complete |
| 2026-06-29 23:21:16 | groups_ML | 3 | complete |
| 2026-06-29 23:34:04 | groups_ML | 4 | complete |
| 2026-06-30 00:18:07 | groups_OSBP | 0 | complete |
| 2026-06-30 00:20:54 | groups_OSBP | 1 | complete |
| 2026-06-30 00:23:12 | groups_OSBP | 2 | complete |
| 2026-06-30 00:26:08 | groups_OSBP | 3 | complete |
| 2026-06-30 00:26:47 | groups_OSBP | 4 | complete |
| 2026-06-29 20:39:00 | groups_START | 0 | complete |
| 2026-06-30 00:46:57 | groups_START | 0 | complete |
| 2026-06-29 20:51:26 | groups_START | 1 | complete |
| 2026-06-29 20:57:49 | groups_START | 2 | complete |
| 2026-06-30 00:56:39 | groups_START | 2 | complete |
| 2026-06-29 20:59:58 | groups_START | 3 | complete |
| 2026-06-29 21:12:11 | groups_START | 4 | complete |
| 2026-06-30 01:21:18 | groups_START | 4 | complete |
| 2026-06-29 21:12:11 | groups_lipocalin | 0 | complete |
| 2026-06-30 01:25:16 | groups_lipocalin | 0 | complete |
| 2026-06-29 21:12:11 | groups_lipocalin | 1 | complete |
| 2026-06-29 21:12:32 | groups_lipocalin | 2 | complete |
| 2026-06-29 21:12:32 | groups_lipocalin | 3 | complete |
| 2026-06-29 21:12:32 | groups_lipocalin | 4 | complete |
| 2026-06-29 22:58:04 | groups_scp2 | 0 | complete |
| 2026-06-29 23:03:21 | groups_scp2 | 1 | complete |
| 2026-06-29 23:04:09 | groups_scp2 | 2 | complete |
| 2026-06-29 23:08:14 | groups_scp2 | 3 | complete |
| 2026-06-29 23:10:01 | groups_scp2 | 4 | complete |

## Latest rows after group-seed deduplication

| datetime | exclusion_set | seed | run_status |
|---|---|---:|---|
| 2026-06-30 00:32:25 | groups_CRAL-TRIO | 1 | complete |
| 2026-06-29 20:07:56 | groups_CRAL-TRIO | 3 | complete |
| 2026-06-30 00:40:14 | groups_CRAL-TRIO | 4 | complete |
| 2026-06-29 21:12:32 | groups_GLTP | 0 | complete |
| 2026-06-29 21:14:00 | groups_GLTP | 1 | complete |
| 2026-06-29 21:14:00 | groups_GLTP | 2 | complete |
| 2026-06-29 21:14:00 | groups_GLTP | 3 | complete |
| 2026-06-29 21:14:00 | groups_GLTP | 4 | complete |
| 2026-06-29 21:18:30 | groups_IP_trans | 0 | complete |
| 2026-06-29 21:24:43 | groups_IP_trans | 1 | complete |
| 2026-06-29 21:25:11 | groups_IP_trans | 2 | complete |
| 2026-06-29 21:44:34 | groups_IP_trans | 3 | complete |
| 2026-06-29 21:59:56 | groups_IP_trans | 4 | complete |
| 2026-06-29 22:52:57 | groups_LBP_BPI_CETP | 0 | complete |
| 2026-06-29 22:54:04 | groups_LBP_BPI_CETP | 1 | complete |
| 2026-06-29 22:55:43 | groups_LBP_BPI_CETP | 2 | complete |
| 2026-06-29 22:55:46 | groups_LBP_BPI_CETP | 3 | complete |
| 2026-06-29 22:56:24 | groups_LBP_BPI_CETP | 4 | complete |
| 2026-06-29 23:09:58 | groups_ML | 0 | complete |
| 2026-06-29 23:15:35 | groups_ML | 1 | complete |
| 2026-06-29 23:16:54 | groups_ML | 2 | complete |
| 2026-06-29 23:21:16 | groups_ML | 3 | complete |
| 2026-06-29 23:34:04 | groups_ML | 4 | complete |
| 2026-06-30 00:18:07 | groups_OSBP | 0 | complete |
| 2026-06-30 00:20:54 | groups_OSBP | 1 | complete |
| 2026-06-30 00:23:12 | groups_OSBP | 2 | complete |
| 2026-06-30 00:26:08 | groups_OSBP | 3 | complete |
| 2026-06-30 00:26:47 | groups_OSBP | 4 | complete |
| 2026-06-30 00:46:57 | groups_START | 0 | complete |
| 2026-06-29 20:51:26 | groups_START | 1 | complete |
| 2026-06-30 00:56:39 | groups_START | 2 | complete |
| 2026-06-29 20:59:58 | groups_START | 3 | complete |
| 2026-06-30 01:21:18 | groups_START | 4 | complete |
| 2026-06-30 01:25:16 | groups_lipocalin | 0 | complete |
| 2026-06-29 21:12:11 | groups_lipocalin | 1 | complete |
| 2026-06-29 21:12:32 | groups_lipocalin | 2 | complete |
| 2026-06-29 21:12:32 | groups_lipocalin | 3 | complete |
| 2026-06-29 21:12:32 | groups_lipocalin | 4 | complete |
| 2026-06-29 22:58:04 | groups_scp2 | 0 | complete |
| 2026-06-29 23:03:21 | groups_scp2 | 1 | complete |
| 2026-06-29 23:04:09 | groups_scp2 | 2 | complete |
| 2026-06-29 23:08:14 | groups_scp2 | 3 | complete |
| 2026-06-29 23:10:01 | groups_scp2 | 4 | complete |
