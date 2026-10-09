# Указатель документов `files/`

> **Правило сопровождения.** Новый документ кладётся в подпапку по типу и добавляется
> сюда строкой. Заголовок в таблице — первая строка `#` самого документа, дата —
> последнее содержательное изменение. Что действует сейчас —
> [CURRENT_STATE.md](CURRENT_STATE.md).

| подпапка | что там |
|---|---|
| [history/](history/) | история архитектур и метрик: что меняли, что сработало, что нет — **начинать отсюда** |
| [reference/](reference/) | как устроены данные, разрезы, признаки и модули |
| [results/](results/) | разборы законченных прогонов и измерений: числа, таблицы, выводы |
| [proposals/](proposals/) | открытые предложения: что попробовать дальше |
| [literature/](literature/) | обзоры литературы и исходные статьи/таблицы данных |
| [report/](report/) | статья (TeX), отчёт, презентация, заявка на вычислительные ресурсы |

## history/

| документ | дата | о чём |
|---|---|---|
| [baselines_and_metrics.md](history/baselines_and_metrics.md) | 2026-10-06 | История эталонов и метрик: с чем сравнивают модель и по какому числу |
| [descriptor_models.md](history/descriptor_models.md) | 2026-10-06 | История дескрипторных моделей: `descriptors_*`, `descriptors_head`, `descriptor_mlp` |
| [geometric_edge.md](history/geometric_edge.md) | 2026-10-09 | История графовой модели: от attention-модели (`bbp`) до GE на `species15` |

## reference/

| документ | дата | о чём |
|---|---|---|
| [data_source.md](reference/data_source.md) | 2026-09-28 | Источник данных о взаимодействиях LTP-липид |
| [deepclip_architecture.md](reference/deepclip_architecture.md) | 2026-10-06 | DeepCLIP в проекте: устройство и что показали прогоны |
| [descriptor_catalog.md](reference/descriptor_catalog.md) | 2026-10-09 | Каталог дескрипторов: что есть, как считается, что про них известно |
| [double_cold_split.md](reference/double_cold_split.md) | 2026-08-29 | Как составляется двусторонний холодный сплит |
| [feature_mapping_mlp_descriptors.md](reference/feature_mapping_mlp_descriptors.md) | 2026-10-09 | Feature mapping: 17 дескрипторов `mlp_sub_pb6` / `descriptors_head_..._protbind6` |
| [lipid_class_ether_variant.md](reference/lipid_class_ether_variant.md) | 2026-09-28 | Вариант классификации с отдельным -O классом, и аудит на ошибки типа CL |
| [lipid_species_coldsplit.md](reference/lipid_species_coldsplit.md) | 2026-09-28 | Сплит по конкретному липиду: флаг `--lipid_species_coldsplit`, приоритет балансировок и планки |
| [local_cpu_layout.md](reference/local_cpu_layout.md) | 2026-08-29 | Локальный запуск: как раздаются ядра и память |
| [marginals_and_cold_split.md](reference/marginals_and_cold_split.md) | 2026-08-29 | Маргиналы, холодный сплит и точка отсчёта |
| [pocket_lipid_compatibility.md](reference/pocket_lipid_compatibility.md) | 2026-08-29 | Признак пары: карман против цепи |
| [pocket_shape_descriptors.md](reference/pocket_shape_descriptors.md) | 2026-10-09 | Дескрипторы формы кармана |
| [protein_edge_mlp_vs_attention.md](reference/protein_edge_mlp_vs_attention.md) | 2026-09-03 | `--protein_edge_mlp` vs `--protein_edge_attention`: как учитывается геометрия белка |

## results/

| документ | дата | о чём |
|---|---|---|
| [compat_input_audit.md](results/compat_input_audit.md) | 2026-08-29 | Признак совместимости: чей это прирост |
| [cron.md](results/cron.md) | 2026-10-09 | Kron-RLS: полное резюме (диагноз нейросетевой части, результаты Kron-RLS) |
| [dcs_bilinear_norm_family_comparison.md](results/dcs_bilinear_norm_family_comparison.md) | 2026-09-13 | geometric_edge, double_coldsplit: вся линия `_bilinear_norm*` (2026-09-13) |
| [dcs_descriptors_head_family_comparison.md](results/dcs_descriptors_head_family_comparison.md) | 2026-10-09 | descriptors_head (одноветочная архитектура), double_coldsplit: вся линия (2026-09-13) |
| [dcs_lcs_final_baseline_decision.md](results/dcs_lcs_final_baseline_decision.md) | 2026-10-09 | DCS/LCS baseline decision for geometric_edge and descriptors (2026-09-12) |
| [descriptor_mlp_recheck_and_tuning.md](results/descriptor_mlp_recheck_and_tuning.md) | 2026-09-30 | `--descriptor_mlp`: re-check of the MLP-vs-head claim, and why it still trails the joint bar |
| [descriptors_baseline_leak_confirmed.md](results/descriptors_baseline_leak_confirmed.md) | 2026-10-09 | Дескрипторный baseline (architecture 2): утечка подтверждена, честной замены не существует |
| [descriptors_head_bottleneck.md](results/descriptors_head_bottleneck.md) | 2026-09-29 | Голова `NamedDescriptorHead` — узкое место, а не дескрипторы и не сплит |
| [edge_geometry_pruning_rbf6_orient_raw3.md](results/edge_geometry_pruning_rbf6_orient_raw3.md) | 2026-10-09 | Обрезка геометрии рёбер (`edge_rbf6` / `edge_orientation_scalar` / `edge_raw3`) против бейзлайна |
| [fig3_lipid_subclass_coldsplit_results.md](results/fig3_lipid_subclass_coldsplit_results.md) | 2026-09-19 | Figure-3 lipid-subclass cold split (Kron-RLS, `--excluded_lipid_groups`) — первый прогон |
| [four_families_audit.md](results/four_families_audit.md) | 2026-10-09 | Аудит активных семейств архитектур: descriptors_*, geometric_edge_*, bbp_dcs_rand_smd_fa_nps_* |
| [ge_s15_ablation.md](results/ge_s15_ablation.md) | 2026-10-06 | Абляция входов `ge_s15_prothid32_hid64_noreg` (geometric_edge, species15) |
| [ge_s15_architecture_sweep_results.md](results/ge_s15_architecture_sweep_results.md) | 2026-10-06 | `ge_*` на `groups_species15`: 29 вариантов против базы `ge_s15_prothid32_hid64_noreg` |
| [geometric_edge_descriptors_baseline_selection_results.md](results/geometric_edge_descriptors_baseline_selection_results.md) | 2026-09-12 | Разбор 33 прогонов (2026-09-11): что из предложений подтвердилось для geometric_edge и descriptors |
| [geometric_edge_recent_proposals_vs_runs.md](results/geometric_edge_recent_proposals_vs_runs.md) | 2026-09-07 | geometric_edge*/thematical_paths: последние предложения vs фактически прогнанные варианты |
| [keep5_all6_network_knn_kronrls_subclass.md](results/keep5_all6_network_knn_kronrls_subclass.md) | 2026-10-06 | keep5 и all6 на lipid_subclass: нейросеть, k-ближайших соседей, Kron-RLS |
| [kronrls_false_negative_candidates.md](results/kronrls_false_negative_candidates.md) | 2026-09-03 | Kron-RLS: поиск кандидатов в false negative по сходству |
| [lbp_bpi_cetp_family_identifiability.md](results/lbp_bpi_cetp_family_identifiability.md) | 2026-09-30 | Почему на DCS работает именно LBP_BPI_CETP: какие каналы вообще выдают эту семью |
| [lcs_descriptors_and_protgeom8_baseline_results.md](results/lcs_descriptors_and_protgeom8_baseline_results.md) | 2026-09-12 | 8 новых `--lipid_coldsplit` конфигов: `descriptors_head` впервые под lcs, `protgeom8`/`protfull` поверх текущего лучшего baseline |
| [lcs_descriptors_head_family_comparison.md](results/lcs_descriptors_head_family_comparison.md) | 2026-09-13 | descriptors_head (одноветочная архитектура), lipid_coldsplit: вся линия (2026-09-13) |
| [lcs_geometric_edge_best_candidate_recheck.md](results/lcs_geometric_edge_best_candidate_recheck.md) | 2026-09-12 | Пересмотр "лучшего lcs-кандидата" для geometric_edge: advprot vs liphid32 vs остальные |
| [lcs_protbind6_family_comparison.md](results/lcs_protbind6_family_comparison.md) | 2026-09-13 | geometric_edge, lipid_coldsplit: protbind6/protgeom8/protunion14 family comparison (2026-09-13) |
| [lipid_coldsplit_architecture_direction.md](results/lipid_coldsplit_architecture_direction.md) | 2026-10-09 | Липидный колдсплит: что показали прогоны и куда тюнить архитектуру |
| [lipid_species_coldsplit_composition.md](results/lipid_species_coldsplit_composition.md) | 2026-09-30 | Что реально держит `--lipid_species_coldsplit=0.15` в valid/test: подкласс за подклассом |
| [lipid_species_coldsplit_tanimoto_isolation.md](results/lipid_species_coldsplit_tanimoto_isolation.md) | 2026-10-06 | `--lipid_species_coldsplit=0.15`: блок дизъюнктен по структурам, но НЕ изолирован по Tanimoto |
| [lipid_subclass_split_and_cron_features.md](results/lipid_subclass_split_and_cron_features.md) | 2026-09-22 | Сплит по подклассу липида, признаки из химии кармана и справка по DeepCLIP |
| [mlp_all70_subclass_ablation.md](results/mlp_all70_subclass_ablation.md) | 2026-10-06 | Абляция входов `mlp_sub_pb6_all70` (70 дескрипторов, `lipid_subclass`) и кандидаты в набор из 5 |
| [mlp_baseline_lcs_dcs.md](results/mlp_baseline_lcs_dcs.md) | 2026-09-30 | MLP-baseline (`--descriptors_head`) на двух осях: lipid_coldsplit и double_coldsplit |
| [mlp_s15_ablation_70_inputs.md](results/mlp_s15_ablation_70_inputs.md) | 2026-10-06 | Абляция входов mlp s15 (`mlp_s15_nomb_hid64`, 70 дескрипторов) и кандидаты в набор из 5 |
| [mlp_s15_architecture_sweep.md](results/mlp_s15_architecture_sweep.md) | 2026-09-30 | Архитектурная сетка на `mlp_s15_nomb_hid64`: длина обучения, ширина, глубина, дропаут |
| [mlp_s15_pu_loss_first_measurement.md](results/mlp_s15_pu_loss_first_measurement.md) | 2026-09-30 | PU-loss на MLP-линии species15: первое измерение, и баг, найденный по пути |
| [mlp_vs_head_subclass_and_feature_ablation.md](results/mlp_vs_head_subclass_and_feature_ablation.md) | 2026-10-06 | mlp против descriptors_head на lipid_subclass: архитектура, регуляризация, абляция признаков |
| [molformer_expressivity_probe.md](results/molformer_expressivity_probe.md) | 2026-09-22 | Выразительность MolFormer: можно ли вынуть класс липида из того вектора, который получает сеть |
| [nonneural_lipid_coldsplit_baselines.md](results/nonneural_lipid_coldsplit_baselines.md) | 2026-09-18 | Ненейронные baseline'ы на --lipid_coldsplit: Kron-RLS vs HistGradientBoosting |
| [pocket_shape_metric_comparison.md](results/pocket_shape_metric_comparison.md) | 2026-09-14 | Две формулы длины оси кармана: percentile span против √λ |
| [report_pocket_lipid_interaction.md](results/report_pocket_lipid_interaction.md) | 2026-08-29 | Pocket–Lipid Interaction |
| [reuter_fig3a_dataset_consistency.md](results/reuter_fig3a_dataset_consistency.md) | 2026-10-06 | Reuter et al. Figure 3a vs. this project's interaction table |
| [rotate_train_negatives_first_results.md](results/rotate_train_negatives_first_results.md) | 2026-10-09 | --rotate_train_negatives: первые четыре прогона против своих бейзлайнов |
| [signal_state.md](results/signal_state.md) | 2026-10-09 | Что модель выучивает и чего не выучивает |
| [split_similarity_four_baselines_and_deepclip.md](results/split_similarity_four_baselines_and_deepclip.md) | 2026-10-09 | Метрика против похожести отложенного блока: четыре базлайна и лучший DeepCLIP |
| [split_similarity_vs_metric.md](results/split_similarity_vs_metric.md) | 2026-10-09 | Сходство отложенного блока с трейном против test BA / test F1 (2026-09-16) |
| [thematical_paths_summary.md](results/thematical_paths_summary.md) | 2026-10-06 | `--thematical_paths`: идея и почему не получилось (линия закрыта) |

## proposals/

| документ | дата | о чём |
|---|---|---|
| [data_proposals.md](proposals/data_proposals.md) | 2026-08-03 | Предложения по нормализации данных (бывший `data/data_proposals.md`) |
| [deepclip_proposals.md](proposals/deepclip_proposals.md) | 2026-10-06 | DeepCLIP: открытые предложения |
| [interaction_embedding_design.md](proposals/interaction_embedding_design.md) | 2026-09-11 | Эмбеддинг взаимодействия вместо попарной классификации: постановка и условия валидности |
| [species15_information_above_protein_subclass.md](proposals/species15_information_above_protein_subclass.md) | 2026-10-06 | Какую информацию добавить, чтобы подняться выше угадывания по «белок × подкласс» |
| [species15_where_to_go_next.md](proposals/species15_where_to_go_next.md) | 2026-10-09 | Куда двигать проект: диагноз по измерениям 2026-10-01 |

## literature/

| документ | дата | о чём |
|---|---|---|
| [binding_determinants_literature_and_feature_proposals.md](literature/binding_determinants_literature_and_feature_proposals.md) | 2026-09-19 | Что литература считает определяющим в связывании LTP-липид, и каких признаков нам не хватает |
| [lipid_similarity_measures.md](literature/lipid_similarity_measures.md) | 2026-09-16 | Что в липиде решает связывание, и какой мерой похожести это мерить |
| [protein_lipid_binding_family_literature.md](literature/protein_lipid_binding_family_literature.md) | 2026-09-06 | Биологически установленные детерминанты связывания липидов, по семьям |
| [Reuter.pdf](literature/Reuter.pdf) | 2026-09-18 | Reuter et al. — статья-источник таблицы взаимодействий |
| [s_MTBLS9567.txt](literature/s_MTBLS9567.txt) | 2026-08-24 | MetaboLights MTBLS9567: таблица образцов исходного эксперимента |

## report/

| документ | дата | о чём |
|---|---|---|
| [architecture_section.tex](report/architecture_section.tex) | 2026-08-24 | статья: раздел «архитектура» |
| [Background_and_Tests.pptx](report/Background_and_Tests.pptx) | 2026-06-10 | презентация: постановка и тесты |
| [data_section.tex](report/data_section.tex) | 2026-08-24 | статья: раздел «данные» |
| [dossier_GENCI_LTP-learning.md](report/dossier_GENCI_LTP-learning.md) | 2026-07-13 | Demande d'attribution de ressources de calculs |
| [explanations.md](report/explanations.md) | 2026-08-25 | Что измеряет каждый тест в results_section.tex и почему он устроен именно так |
| [Report_DL_architecture_FE-2.pdf](report/Report_DL_architecture_FE-2.pdf) | 2026-06-10 | отчёт по архитектуре (PDF, собран из `Report DL architecture FE LATEX/`) |
| [results_section.tex](report/results_section.tex) | 2026-08-25 | статья: раздел «результаты» (тесты разобраны в explanations.md) |

