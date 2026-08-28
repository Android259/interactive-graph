🥇 1. Контрастивный вспомогательный лосс на пулинг-эмбеддингах (ConPLex, CCL-ASPS, MulinforCPI-pretraining)
Почему: это самый прямой рычаг на обобщение к невиданным семьям. Сейчас GRAB_loss регуляризует по графу похожести только внутри train; контраст же формирует пространство, где невиданный фолд садится рядом со своими липидами.
Как: взять пулинг-векторы lip_outs, prot_outs в final_layer.py:66-67 до binar, спроецировать в общее пространство и добавить protein-anchored triplet/InfoNCE: якорь-белок, положительный липид (истинный), отрицательные (несвязываемые). Новый терм в loss.py рядом с GRAB, вес — новый флаг конфигурации.
Стоимость: средняя; ~50–100 строк, без изменения энкодеров.

🥈 2. Радикальное сокращение обучаемых параметров / «заморозить больше» (ChemGLaM, MulinforCPI)
Почему: две независимые работы делают один вывод — на малых/novel данных меньше параметров = лучше обобщение. У нас медиана 1.4M параметров на ~1300 пар leave-family-out — идеальный рецепт переобучения. ChemGLaM обучает по сути только interaction-блок.
Как (абляция, дёшево): прогнать лёгкие конфиги — double_attention=False, отключить extra hidden layer (m↓), меньший hiddim, single_gat_layer, *_disable_post_sa_mlp. Всё это уже есть как флаги в read_configuration.py. Гипотеза: лёгкий вариант побьёт тяжёлый на test-BA.
Стоимость: ноль кода — только запуск сравнения.

🥉 3. Абляция «cross-attention vs конкатенация» на разреженных данных (MulinforCPI)
Почему: MulinforCPI явно нашёл, что на sparse-данных конкатенация превзошла cross-attention (наша задача очень разреженная: 756 позитивов). Наш double_attention/cross_attention может переобучаться.
Как: флаг cross_attention уже существует в interaction_classification.py:27-37 — сравнить cross_attention=True/False × double_attention=True/False честно на leave-family-out. Если конкат не хуже — это и обобщает лучше, и дешевле.
Стоимость: ноль кода.

4. Инъекция дескрипторов класса/headgroup липида (MulinforCPI «what/where», ConPLex Morgan-fingerprints)
Почему: MulinforCPI и ConPLex показывают, что высокоуровневые substructure-дескрипторы, конкатенированные к атомному представлению, дают обобщение по химии. У нас эти признаки уже посчитаны — класс липида, headgroup, стереохимия (preprocessing/infer_real_lipid_fullidentity.py, правила из lipid_identity_smiles_rules.md). Сейчас они не подаются в модель.
Как: конкатенировать one-hot класса/headgroup + число ненасыщенностей/длину цепи к липидному вектору в lipid_encoder.py (по аналогии с nn.Embedding-lookup у MulinforCPI). Даёт модели биологический prior специфичности.
Стоимость: низкая; данные уже есть.

5. Слить два липидных пути (MoLFormer-LM ⊕ RDKit-граф) вместо «или/или» (Dual-Interaction Fusion, DCGAT)
Почему: досье подчёркивает, что стереохимия (cis/trans) — ключ к специфичности, а канонические LM-эмбеддинги её размывают; граф RDKit её кодирует явно (флаг lipid_graph_isomers, edge-фичи stereo, bond_dir). Сейчас это взаимоисключающие ветки в lipid_encoder.py:28-50. Пути комплементарны: LM — глобальная химия, граф — изомерия.
Как: посчитать обе ветки и сложить/сконкатенировать перед self-attention.
Стоимость: средняя.

6. Многоуровневое представление белка: карман-токен + глобаль-токен (ColdDTI, «Multilevel Structure»)
Почему: абляции обеих работ: уровни структуры дают наибольший прирост именно на cold-protein — наш случай. У нас уже есть pocketness-маска, но она используется лишь как bias/фильтр пулинга.
Как: добавить явные пул-токены «только карман» и «весь белок» и межуровневое внимание к липиду в final_layer.py/cross_attention.py. Переиспользует существующий pocket_mask.
Стоимость: средняя.

7. Слабый надзор карты cross-attention карманом (ChemGLaM + PLiCat Integrated Gradients)
Почему: ChemGLaM показывает интерпретируемость через карту внимания, PLiCat — что известные сайты связывания совпадают с высоко-атрибутивными остатками. У нас есть ground-truth карман — можно превратить его из bias в supervised сигнал.
Как: вернуть веса внимания из lip_cross_attention в cross_attention.py:126 и добавить вспомогательный лосс «липид→белок внимание концентрируется на pocket-остатках».
Стоимость: средняя.

8. Информативный отбор негативов вместо равномерного 5.6% (CCL-ASPS, CrossLinker)
Почему: сейчас PU-негативы сэмплируются равномерно случайно; adaptive self-paced / hard-negative даёт более информативный сигнал. У нас уже посчитаны Tanimoto-матрицы — можно сэмплировать негативы по похожести (curriculum: от лёгких к трудным).
Как: заменить равномерный сэмплинг в Dataloader.py на взвешенный по Tanimoto/близости к позитивам.
Стоимость: средняя.

Что я бы попробовал в первую очередь
№2 и №3 — бесплатно (только запуск существующих флагов): проверить гипотезу «легче = лучше обобщает» и «конкат ≥ cross-attention». Это может сразу поднять test-BA и удешевить кампанию, о которой идёт речь в досье.
№1 (контрастивный лосс) — самый вероятный рычаг для скачка 0.60 → 0.70, но требует реализации.
№4 (дескрипторы класса липида) — дёшево, данные уже есть, прямой биологический prior.
Хотите — могу оформить это как раздел в досье (там как раз стоит «À COMPLÉTER» про ссылку на cross-attention-аналог: ближайшие published — ChemGLaM и бидирекциональный CPI-cross-attention), либо детально расписать реализацию любого из пунктов (например, №1).

Sources:

ChemGLaM (J. Cheminformatics / bioRxiv)
PLiCat (PMC)
ConPLex (PMC)
MulinforCPI (Briefings in Bioinformatics)
Generalizable CPI, structure- & property-aware LM (Comms Chemistry)
ColdDTI / Attending on Multilevel Structure (arXiv)
CCL-ASPS collaborative contrastive + adaptive sampling (BMC Biology)
CrossLinker cold-start/few-shot DTI (JCIM)
Bidirectional interpretable CPI cross-attention (Comput. Biol. Med.)
iNGNN-DTI (PMC)
ML proteome-wide lipid-interacting proteins (bioRxiv)