# Тот же ..._lcs_esm3_balanced_lipid_classes_advprot, но БЕЗ --balanced_lipid_classes:
# отрицательные набираются протеин-сбалансированно, как на всей линии до 2026-09-08.
#
# Что проверяет. Стоит ли весь adv/rank-слой на бейзлайне, который сам ниже предыдущего.
# --balanced_lipid_classes вошёл в бейзлайн по пулированной BA (+0.0625 пулом, +0.187 на
# sphingolipids при 5.7s), то есть по величине, которую потом показали как белковую
# маргиналь. Разложение 2x2 через analysis/cross_sampler_eval.py (веса одного лейбла на
# строках другого, эпоха 120) даёт на внутрибелковой парной метрике:
#
#   эффект ОБУЧЕНИЯ, anionic+choline, парно по (набор, сид):
#       на строках без флага   -0.068 +- 0.037 (1.8s)
#       на строках с флагом    -0.070 +- 0.037 (1.9s)
#   эффект БЛОКА (те же веса, разные строки):
#       anionic -0.073 +- 0.009 (7.8s), choline +0.008 (0.3s)
#
# Знак и величина воспроизводятся на ДВУХ независимых наборах оценочных строк, то есть это
# свойство обученной модели, а не разметки блока
# (files/geometric_edge_and_solo_next_architecture.md 8.6).
#
# Почему нужен именно этот прогон. Всё разложение выше сделано на бейзлайне БЕЗ
# адверсария. Дельты advprot/rankprot/rank+adv отсчитаны от точки с флагом, и если знак
# верен, они частично есть возврат к тому, что уже было. Один флаг разделяет эти две
# возможности.
#
# Оговорка. 1.9s вопрос не закрывает, и на phosphorus_free/sphingolipids знак
# противоположный (8 и 2 белковых блока — нечитаемо). Прогон нужен ровно потому, что
# нынешних данных на вывод не хватает.
#
# Ожидание, записанное ДО прогона: на anionic и choline этот конфиг будет ВЫШЕ
# ..._balanced_lipid_classes_advprot примерно на те же 0.05-0.07. Если окажется ниже или
# вровень — эффект был свойством бейзлайна без адверсария и на adv-базе не переносится.
#
# Читать по AUC_within_protein_pairs на anionic и choline (RULE в
# files/lipid_coldsplit_architecture_direction.md). ВНИМАНИЕ: оценочные строки у этого
# лейбла ДРУГИЕ (белковых блоков 16.4/14.8/12.2/3.4 против 14.6/14.0/7.8/2.0), поэтому с
# лейблами, где флаг стоит, его числа сравнимы только через cross_sampler_eval.

--ep=120
--fast_attention
--hiddim=8
--dropout=0.1
--weight_decay=0.01
--pool_type="add"
--bilinear_fusion
--bilinear_pooled_norm
--protein_descriptors=pocket_volume_per_sasa,pocket_elongation,pocket_flatness,buriedness_q50,apolar_sasa_share,aromatic_share,hydropathy_rim
--protein_edge_mlp
--save_model_in_dynamics
--save_model
--balanced_batches
--balanced_proteins
--lipid_coldsplit
--adversarial_grl
--no_adv_lipid
