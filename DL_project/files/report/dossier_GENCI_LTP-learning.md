# Demande d'attribution de ressources de calculs

> Formulaire de description **scientifique et technique** de la demande (AR / AS / AD).
> Document limité à 15 pages, confidentiel et dédié à l'expertise.

## 1. Description du projet

### 1.1 Informations générales

- **Titre du projet :** LTP-learning
- **Responsable scientifique :** [Prénom Nom]

### 1.2 Résumé

Ce projet développe un modèle d'apprentissage profond multimodal pour prédire les interactions
entre protéines de transfert de lipides (Lipid Transfer Proteins, LTP) et lipides. Les LTP capturent et
transportent des lipides spécifiques entre les membranes cellulaires via une poche hydrophobe ;
comprendre leur spécificité de reconnaissance est un enjeu de biologie membranaire et, pour
plusieurs familles, de santé (allergénicité, signalisation lipidique).

Chaque poche protéique est représentée par un graphe issu de la structure 3D, dont les nœuds
sont enrichis par les plongements d'un modèle de langage protéique (ESM3, 1536 dimensions) et
traités par des réseaux de neurones sur graphes (GNN de type GATv2). Chaque lipide est encodé via un modèle
de langage chimique (MoLFormer, 768 dimensions) ou, en variante, via un graphe moléculaire annoté par RDKit. Un
module d'attention croisée bidirectionnelle fait communiquer les deux modalités avant une prédiction binaire
d'interaction.

Les données expérimentales ne fournissent que des interactions confirmées ; l'entraînement
conserve les 756 positifs et n'échantillonne qu'environ 5,6 % des 10 262 paires non étiquetées
comme négatifs (≈ 575, ré-échantillonnés par graine), formant un ensemble de travail quasi
équilibré d'environ 1 300 paires ; la nature positive/non-étiquetée et le déséquilibre résiduel sont
traités par une famille de pertes (apprentissage Positive-Unlabeled, pondération de classes,
perte focale, ajustement de logits, régularisation par graphe de similarité GRAB). Les
ressources demandées servent à entraîner et comparer systématiquement ces architectures —
variantes d'encodeurs, stratégies de fusion, schémas de découpage (généralisation à des
protéines ou lipides non vus) et fonctions de perte — au moyen d'un grand nombre d'expériences
GPU, afin de produire un prédicteur précis et interprétable de la spécificité LTP–lipide.

## 2. Présentation scientifique détaillée

### Objectifs visés grâce aux ressources demandées

1. Disposant d'un ensemble de configurations de modèles d'un prédicteur LTP–lipide
   potentiellement prometteuses, **identifier l'architecture** du prédicteur présentant la plus
   grande capacité de généralisation. Le résultat satisfaisant est supposé au niveau de
   prédiction correcte approximativement de 70–75 % (la BA — *balanced accuracy* — moyenne de
   la meilleure architecture actuelle est d'environ 60 % : sur l'ensemble des campagnes menées,
   la BA de test moyennée sur les familles et les graines est de ≈ 0,595, la meilleure
   configuration atteignant ≈ 0,63–0,65 en moyenne et ≈ 0,70 en BA de validation).

2. **Évaluer la généralisation** à des protéines non vues (validation croisée par exclusion de
   famille sur 9 familles) et, en variante, à des lipides non vus.

Ces objectifs sont atteints par une campagne de comparaison systématique de configurations,
chacune évaluée par validation croisée répétée sur plusieurs graines.

### Contexte biologique et données

Les LTP regroupent plusieurs familles structuralement distinctes liant un lipide dans une cavité
hydrophobe. Le jeu de données couvre **9 familles** et **35 protéines LTP humaines** (identifiants
UniProt entre parenthèses), sélectionnées à partir de l'annotation de famille et de domaine
UniProt/PROSITE, avec des structures expérimentales sans mutation (PDB) ou, à défaut, des
modèles AlphaFold (AFDB) :

- **CRAL-TRIO / SEC14 (9) :** ATCAY (Q86WG3), BNIPL (Q7Z465), RLBP1 (P12271), SEC14L2 (O76054),
  SEC14L4 (Q9UDX3), SEC14L5 (O43304), SEC14L6 (B5MCN3), TTPA (P49638), TTPAL (Q9BTX7).
- **START (3) :** STARD2 (Q9UKL6), STARD10 (Q9Y365), STARD11/CERT (Q9Y5P4).
- **Lipocalines / iLBP (10) :** CRABP2 (P29373), FABP1 (P07148), FABP5 (Q01469), FABP7 (O15540),
  LCN1 (P31025), LCN15 (Q6UWW0), PMP2 (P02689), RBP1 (P09455), RBP4 (P02753), RBP5 (P82980).
- **GLTP (2) :** GLTP (Q9NZD2), GLTPD1 (Q5TA50).
- **PITP / IP_trans (3) :** PITPNA (Q00169), PITPNB (P48739), PITPNC1 (Q9UKF7).
- **LBP-BPI-CETP (2) :** BPI (P17213), BPIFB2 (Q8N4F0).
- **SCP2 (3) :** HSDL2 (Q6YN16), SCP2 (P22307), SCP2D1 (Q9UJQ7).
- **ML / GM2A (1) :** GM2A (P17900).
- **OSBP (2) :** OSBPL5 (Q9H0X9), OSBPL9 (Q96SU4).

Ces familles ont été retenues parce qu'elles constituent des replis de transport lipidique
structuralement distincts et non homologues, ce qui permet de tester la généralisation d'un
repli à l'autre (validation croisée par exclusion de famille). [À COMPLÉTER : justification
biologique précise, protéine par protéine, du choix de chaque LTP et de son cargo lipidique
attendu.]

Le jeu comprend **284 lipides distincts** (271 SMILES globaux distincts) et **11 018 paires
(protéine, lipide) dont 756 positives** (10 262 paires non étiquetées).

**Groupes et sous-groupes de lipides.** Les lipides couvrent 34 classes réparties en grands
groupes chimiques (nomenclature LIPID MAPS) :

- **Glycérophospholipides :** PC, PC-O, PE, PE-O, PS, PI, PG, PGP, PA, BMP, PG/BMP, CL
  (cardiolipine), et les lyso-formes LPC, LPE, LPE-O, LPG.
- **Sphingolipides :** céramides (dCer, d\*Cer, tCer, DHCer, DHOH\*Cer), hexosyl- et
  dihexosylcéramides (t\*HexCer, d\*HexCer, t\*Hex2Cer), sulfatide (d\*SHexCer), sphingomyélines
  (d\*SM, t\*SM, DHSM) et céramide-phosphate (d\*CerP). Les préfixes `d`/`DH`/`t`/`t*` codent la
  nature du squelette sphingoïde (di-/trihydroxylé, saturé ou insaturé) et déterminent la règle
  de stéréochimie de la double liaison C4/C5.
- **Glycérolipides neutres :** DAG, TAG.
- **Acyls gras et dérivés :** FA (acide gras), FAL (alcool/aldéhyde gras), VA (vitamine A / rétinol).

La classe de chaque lipide et les propriétés de stéréochimie (cis pour l'insaturation des chaînes
acyles ; trans pour la double liaison sphingoïde C4/C5 des formes `d`) sont dérivées par un jeu de
règles appliquées au SMILES (voir `preprocessing/lipid_identity_smiles_rules.md`).

Les interactions positives proviennent de criblages expérimentaux systématiques des complexes
LTP–lipide (Titeca *et al.*, 2023). Le jeu total de 11 018 paires criblées se répartit en
**6 201 paires criblées *in vitro*** et **4 817 paires criblées *in cellulo*** ; parmi elles, les
**756 interactions positives** se décomposent en **494 positives *in vitro*** et **262 positives
*in cellulo***. Les structures sont issues de la PDB et de modèles AlphaFold, les lipides de
LIPID MAPS (requêtes REST à partir de la description tête polaire + chaîne issue de la
spectrométrie de masse).

Les paires non positives sont obtenues en prenant le complément des paires positives : toute
paire (protéine, lipide) non observée comme transportée est traitée comme non étiquetée (et non
comme un vrai négatif), d'où le cadre Positive-Unlabeled.

La quasi-totalité des SMILES disponibles (≈ 100 % : la totalité des SMILES globaux et de
fragments distincts non triviaux portent au moins un descripteur isomérique — chiralité `@`/`@@`
ou géométrie de double liaison `/`, `\`) sont écrits sous forme isomérique ; les plongements sont
obtenus à partir de formules canoniques, avec ou sans prise en compte des propriétés isomériques
selon l'architecture (drapeaux `lipid_isomers` / `lipid_graph_isomers`, la canonicalisation
RDKit préservant alors la stéréochimie).

**Features utilisées dans le dataset.** Chaque protéine est un graphe grain-grossier au niveau
résidu (obtenu par Voronota / diagramme de Voronoï des sphères atomiques) :

- *Nœuds (résidus)* — trois descripteurs géométrico-chimiques `[N, 3]` (`residue_type`,
  `residue_sas_area` = aire de surface accessible au solvant, `residue_volume`), plus le
  plongement ESM3 `[N, 1536]` (projeté par une couche linéaire vers `plm_compression_dim`,
  activable via `plmon`).
- *Buriedness* — enfouissement moyen du résidu `residue_mean_buriedness` `[N]` (scalaire par
  résidu, activable via `buryon`).
- *Pocketness* — masque booléen de poche `[N]` : Voronota-pocket annote la poche dans la colonne
  b-factor du `.pdb` ; un résidu est « poche » dès qu'un de ses atomes non-squelette porte un score
  de poche positif. Ce masque sert de biais positionnel appris dans l'attention
  (`attention_pos_bias`) ou de filtre de pooling (`pooling_by_pockets`).
- *Arêtes* — trois descripteurs de contact de Voronoï `[E, 3]` (`distance`, `area`, `boundary`).

Chaque lipide est représenté soit par le plongement MoLFormer `[N, 768]` (voie « legacy »), soit
par un graphe moléculaire RDKit : 11 features de nœud (`atomic_num`, `formal_charge`, `degree`,
`hybridization`, `is_aromatic`, `is_in_ring`, `chiral_tag`, `chirality_possible`, `total_num_hs`,
`mass`, `gasteiger_charge`) et 6 features d'arête (`bond_type`, `is_conjugated`, `is_in_ring`,
`stereo`, `bond_dir`, `is_aromatic`).

**Métriques d'évaluation.** La métrique principale est la *balanced accuracy* (BA =
(sensibilité + spécificité) / 2), adaptée au déséquilibre résiduel des classes. Sont également
suivies l'exactitude (*accuracy*), la sensibilité (rappel), la spécificité, la précision et le
score F1. La sélection de point de contrôle s'appuie sur une moyenne glissante de la BA de
validation ; les configurations sont comparées par leur BA de test moyennée sur les familles
exclues et sur plusieurs graines, ainsi que par des indicateurs de stabilité (écart-type inter-
graines, oscillation, pente post-optimum).

**Génération des jeux d'entraînement / validation / test.** Trois schémas de découpage sont
disponibles :

- **Exclusion de famille (leave-family-out, schéma principal) :** une ou plusieurs des 9 familles
  sont retirées de l'entraînement ; validation et test proviennent des familles exclues. Avec
  l'option `test_group`, le test provient d'une famille exclue et la validation d'une (ou
  plusieurs) autre(s) famille(s) exclue(s), garantissant des familles **disjointes** entre
  sélection de modèle et évaluation.
- **Exclusion de protéine (leave-protein-out) :** via `excluded_subgroups`, pour tester la
  généralisation à des protéines non vues au sein des familles.
- **Découpage aléatoire :** 85 % / reste, utile pour des tests précoces.

Dans tous les cas, l'échantillonnage Positive-Unlabeled conserve les 756 positifs et échantillonne
≈ 5,6 % des non-étiquetées comme négatifs (≈ 575), ré-échantillonnés à chaque graine ; une
option (`balance_excluded_group_negatives`) ré-équilibre à 1:1 les négatifs de chaque famille
exclue pour éviter les ratios pos/nég aberrants dus au sous-échantillonnage global.

## 3. Présentation technique détaillée

### 3.1 Méthode numérique et implémentations

**Pile logicielle.** Le code est écrit en Python et repose sur PyTorch et PyTorch Geometric (PyG)
pour l'apprentissage et le traitement des graphes, RDKit pour la chimie-informatique (canonicalisation
SMILES, extraction des features atomiques et de liaison, charges de Gasteiger), et NumPy/pandas pour
la manipulation de données. Les plongements protéiques sont générés par ESM3 (« esm3-sm-open-v1 »)
et les plongements lipidiques par MoLFormer ; ces deux modèles pré-entraînés sont utilisés gelés,
en amont de l'entraînement, pour produire des embeddings mis en cache. Les poches sont annotées
par Voronota / voronota-js (diagramme de Voronoï des sphères atomiques) en préprocessing.

**Modèle multimodal.** Le modèle de haut niveau `InteractionClassification` compose :

1. **Encodeur protéine (`Protein_encoder`)** — deux couches de convolution sur graphe (par défaut
   GATv2, `HEADS = 8` têtes ; variantes disponibles : `TransformerConv`, `GINEConv`, connexions
   résiduelles GAT/GINE, normalisation de graphe), suivies d'une auto-attention sur les nœuds
   d'un même échantillon, puis d'un MLP. Les features de nœud combinent les trois descripteurs
   géométriques, l'enfouissement, et le plongement ESM3 projeté.
2. **Encodeur lipide (`Lipid_encoder`)** — soit une projection linéaire des tokens MoLFormer
   (768 → `hiddim`) suivie d'auto-attention, soit, en mode graphe, deux couches GATv2 sur le graphe
   moléculaire ; le graphe lipidique est fully-connected dans la voie « tokens ».
3. **Attention croisée bidirectionnelle (`CrossAttention`)** — deux blocs de type transformeur,
   chacun bâti autour d'un `torch.nn.MultiheadAttention` (`HEADS` têtes) : une voie requête-lipide /
   clé-protéine et une voie requête-protéine / clé-lipide. Chaque bloc suit le schéma classique à
   deux sous-couches : (i) attention croisée + connexion résiduelle + normalisation de couche
   (`LayerNorm`), puis (ii) réseau feed-forward position-wise (`Linear` → activation → dropout →
   `Linear`, facteur d'expansion `m`) + connexion résiduelle + seconde `LayerNorm`. Des portes
   résiduelles apprises (`attention_residual_gates`) et un biais positionnel de poche par tête
   (`prot_pos_bias_per_head`) sont optionnels. Un second bloc encodeur + attention croisée
   (`double_attention`) est disponible.
4. **Pooling de graphe puis couche finale (`Final_Layer`)** — pooling configurable
   (`add`, `max`, `mean`, `add_max`, `gem` — moyenne généralisée à exposant appris), concaténation
   des représentations protéine et lipide, puis MLP produisant des logits `[batch, 2]`.

**Contrats de tenseurs (principaux).** nœud protéine `[N, 3]` ; ESM3 `[N, 1536]` → `plm_compression_dim` ;
enfouissement `[N]` ; arête protéine `[E, 3]` ; nœud lipide legacy `[N, 768]` ; nœud lipide graphe
`[N, 11]` ; arête lipide graphe `[E, 6]` ; sortie encodeur `[N, hiddim]` (GAT : `hiddim × HEADS`
avant projection) ; sortie classifieur `[batch, 2]`.

**Masques d'attention optionnels (fréquemment utilisés).** Les nœuds de toutes les paires d'un lot
étant concaténés, l'attention est restreinte par des masques booléens de forme `[requêtes, clés]`
(la valeur `True` interdit un couple requête-clé) :

- *Masque d'échantillon* — l'auto-attention protéine et lipide ne relie que des nœuds appartenant
  au même échantillon ; l'attention croisée n'autorise que les couples lipide↔protéine issus de la
  même paire (`[N_lipid, N_protein]` pour la requête-lipide, `[N_protein, N_lipid]` pour la
  requête-protéine).
- *Masque de fragments* (`lipid_fragments_mask`, `lipid_batch`) — restreint en plus l'attention aux
  nœuds d'un même fragment lipidique ; il est combiné au masque d'échantillon et ne franchit jamais
  la frontière entre échantillons, même si des identifiants de fragment coïncident.
- *Biais positionnel de poche* (`prot_attention_pos_bias`) — ajoute un biais additif appris aux
  clés « poche » de la protéine dans l'auto-attention protéine et dans l'attention croisée
  requête-lipide (variante par tête via `prot_pos_bias_per_head`) ; il pondère les résidus de poche
  sans supprimer les nœuds hors-poche.
- *Filtrage de poche au pooling* (`prot_pooling_by_pockets`) — retire les nœuds hors-poche
  juste avant le pooling final, chaque échantillon conservant au moins un nœud de poche.

**Fonctions de perte.** Le cadre positive-unlabeled et le déséquilibre sont traités par une famille
de pertes sélectionnables :

- entropie croisée binaire (référence),
- **nnPU** (Non-negative Positive-Unlabeled, Kiryo *et al.* 2017) avec prior `pu_rho` (fixé ou
  dérivé de la fraction de positifs supposée parmi les non-étiquetés), correction non-négative
  (`pu_beta`, `pu_gamma`),
- **perte focale** (Lin *et al.* 2017, `focal_gamma`),
- **ajustement de logits** (Menon *et al.* 2020, biais de log-prior par classe, `tau`),
- **GRAB** : régularisation par graphe de similarité entre paires d'entraînement (les coefficients
  de voisinage ne proviennent que du split d'entraînement),
- pondérations d'échantillon : par classe, par Tanimoto (diversité lipidique), par groupe/classe
  de protéine.

**Optimisation et reproductibilité.** Optimiseur Adam (`lr`, `weight_decay`), 150 époques par
défaut, batch 16 ; ordonnanceurs optionnels (warm-up linéaire + cosinus, SWA). Précision mixte
automatique (AMP + GradScaler) activée uniquement sur CUDA (`type_opt`), le CPU restant valide
pour les tests. Les graines contrôlent l'échantillonnage, le découpage et l'ordre des DataLoaders
(générateurs séparés train/validation/test, `seed_worker` par worker) ; la reproductibilité CPU
est garantie, la déterminisme bit-à-bit CUDA n'est pas revendiqué.

**Validation du code.** Une suite de tests unitaires et d'intégration CPU (`tests/`) vérifie les
formes, la finitude des pertes, la rétropropagation, les gradients et le pas d'optimiseur (elle ne
prouve ni la qualité ni la performance CUDA).

**Coût mesuré (relevé dans `metrics_summary.csv`, 1 816 runs).** Le nombre de paramètres
entraînables va de ≈ 25 · 10³ (variantes légères) à ≈ 3,25 · 10⁶ (variantes lourdes), avec une
médiane de ≈ 1,4 · 10⁶ ; la configuration de référence (`no_post_sa_mlp_standard`) compte
≈ 1,01 · 10⁶ paramètres. Le temps par époque est de ≈ 77 s en médiane (min 60 s, max 292 s pour les
architectures les plus lourdes), soit une durée d'entraînement (150 époques) de ≈ 3,0 h en médiane
(min ≈ 5 min pour les runs courts, max ≈ 4,1 h). Ces mesures sont agrégées sur A100/V100 et servent
de base à l'estimation d'heures GPU ci-dessous.

### 3.2 Justification de l'usage des ressources sur la partition demandée

**Nature de la campagne.** La demande finance une campagne de comparaison systématique. L'espace
exploré comprend ≈ 49 configurations d'architecture/perte distinctes, chacune évaluée sur 10
schémas d'exclusion (les 9 familles exclues tour à tour + le découpage complet) et 5 graines, soit
de l'ordre de 2 000 runs (l'historique actuel compte ≈ 1 960 runs enregistrés). Chaque run
enchaîne entraînement (150 époques), validation et test sur ≈ 1 300 paires d'entraînement.

**Matériel demandé (NVIDIA).** Les runs s'exécutent sur un GPU unique par job (`/nodes=1/gpu=1`),
sur GPU NVIDIA A100 ou V100 (partition GPU de type Bigfoot / GRICAD). Le choix NVIDIA est imposé
par la pile logicielle : CUDA pour PyTorch/PyTorch Geometric, AMP (précision mixte), et la
génération d'embeddings ESM3/MoLFormer. Le besoin mémoire est modéré (jobs configurés pour ≥ 16 Go
de mémoire GPU libre), ce qui rend V100 (16/32 Go) et A100 adaptés ; un seul GPU par run suffit
(pas de parallélisme multi-GPU requis), l'accélération provenant du **débit expérimental** (grand
nombre de runs courts indépendants), non de la taille d'un modèle unique.

**Heures demandées et ventilation.** La demande porte sur **15 000 heures GPU sur une période de
3 semaines**. Cette enveloppe est cohérente avec le coût mesuré : à ≈ 3,0 h par run en médiane, une
campagne complète (≈ 2 000 runs = 49 configurations × 10 schémas d'exclusion × 5 graines)
représente de l'ordre de 6 000 heures GPU. Les 15 000 heures couvrent ainsi une campagne complète,
la ré-exécution des architectures les plus lourdes (jusqu'à ≈ 4,1 h/run) et une marge pour de
nouvelles variantes d'encodeurs, de pertes et de schémas de découpage, ainsi que pour la
(re)génération des plongements. Répartie sur 3 semaines, l'enveloppe correspond à ≈ 30 GPU utilisés
en moyenne simultanément, ce qui est réaliste puisque les runs sont indépendants.

**Profil de consommation.** Les jobs sont courts et indépendants (walltime de 4 h, jusqu'à 10 h pour
certains diagnostics), donc massivement parallélisables et bien adaptés à un ordonnancement par lots.
Sur les 3 semaines demandées, la consommation est prévue **régulière**, au rythme du drainage de la
file de jobs par lots.

**Courbes de scalabilité.** [À COMPLÉTER — à produire.] Une courbe de scalabilité mesure comment le
débit ou le temps par époque évolue avec les ressources allouées ; ici la parallélisation est
« embarrassingly parallel » (un GPU par run, pas de multi-GPU), donc la scalabilité pertinente est
**faible (strong scaling) au niveau de la campagne** : temps total de la campagne en fonction du
nombre de GPU utilisés en parallèle (attendu ≈ linéairement décroissant, chaque run étant
indépendant), et non une accélération intra-modèle. Pour l'obtenir : soumettre un même lot de N
runs identiques en faisant varier le nombre de GPU concurrents (p. ex. 1, 5, 10, 20, 30) et relever
le temps de complétion du lot ; comparer en complément le `training_sec_per_epoch` mesuré sur V100
et sur A100 pour une même configuration afin de quantifier le gain par génération de GPU. Ces
mesures sont directement extractibles des colonnes `training_sec_per_epoch` / `training_duration_sec`
de `metrics_summary.csv`.

### 3.3 Plan de gestion de données (DMP)

Les entrées persistantes sont de taille modérée : plongements ESM3 (≈ 47 Mo), graphes protéiques
grain-grossier (≈ 62 Mo), graphes lipidiques isomériques (≈ 17 Mo), plongements SMILES MoLFormer,
matrices de Tanimoto et tables d'interaction ; le répertoire `data/` complet est de l'ordre de
16 Go (incluant structures brutes et dérivés). Les sorties d'entraînement (métriques agrégées,
logs TensorBoard, tables de métriques `metrics_summary.csv`, checkpoints optionnels) croissent
avec le nombre de runs.

Les identifiants de paires, indices de Tanimoto et arêtes de graphe GRAB dépendent de l'ordre
original des lignes de la table d'interaction : cet ordre est préservé comme invariant du contrat
de données. Aucune donnée à caractère personnel n'est manipulée.

**Volume demandé.** Les besoins de stockage sont modestes. Le stockage **permanent** héberge le
code, les entrées persistantes (répertoire `data/` ≈ 16 Go, plongements et graphes inclus) et les
sorties agrégées (tables de métriques, logs, figures), soit une demande de l'ordre de **50 Go**
avec marge. Le stockage **scratch/travail** absorbe les logs TensorBoard et les checkpoints
optionnels produits pendant les campagnes ; chaque run ne génère que quelques Mo de métriques (la
sauvegarde de checkpoints est désactivée par défaut), une enveloppe de l'ordre de **50–100 Go** est
donc suffisante pour l'ensemble d'une campagne. Les checkpoints des modèles retenus (≈ 4–13 Mo
chacun) sont conservés sur le stockage permanent.

**Rétention.** L'ordre original des lignes de la table d'interaction (identifiants de paires,
indices de Tanimoto, arêtes GRAB) est préservé comme invariant du contrat de données. Aucune donnée
à caractère personnel n'est manipulée.

[À COMPLÉTER : politique de sauvegarde/rétention exacte imposée par le centre, et
ouverture/partage éventuel des jeux de données et des poids finaux.]

### 3.4 Bibliographie

- Titeca, K. *et al.* (2023). *A system-wide analysis of lipid transfer proteins delineates lipid
  mobility in human cells.* bioRxiv, doi:10.1101/2023.12.21.572821. — source des interactions LTP–lipide.
- Hayes, T. *et al.* (2024). *Simulating 500 million years of evolution with a language model
  (ESM3).* bioRxiv, doi:10.1101/2024.07.01.600583. — plongements protéiques.
- Ross, J. *et al.* (2022). *Large-Scale Chemical Language Representations Capture Molecular
  Structure and Properties (MoLFormer).* arXiv:2106.09553. — plongements lipidiques.
- Olechnovič, K. & Venclovas, Č. (2014). *Voronota: computing the vertices of the Voronoi diagram
  of atomic balls.* J. Comput. Chem. 35(8):672–681, doi:10.1002/jcc.23538. — annotation de poche.
- Conroy, M. J. *et al.* (2023). *LIPID MAPS: update to databases and tools for the lipidomics
  community.* Nucleic Acids Research 52(D1):D1677–D1682, doi:10.1093/nar/gkad896. — SMILES des lipides.
- Paszke, A. *et al.* (2019). *PyTorch: An Imperative Style, High-Performance Deep Learning
  Library.* arXiv:1912.01703.
- Fey, M. & Lenssen, J. E. (2019). *Fast Graph Representation Learning with PyTorch Geometric.*
  ICLR Workshop on Representation Learning on Graphs and Manifolds.
- RDKit: Open-source cheminformatics. https://www.rdkit.org
- Kiryo, R. *et al.* (2017). *Positive-Unlabeled Learning with Non-Negative Risk Estimator (nnPU).*
  NeurIPS.
- Lin, T.-Y. *et al.* (2017). *Focal Loss for Dense Object Detection.* ICCV.
- Menon, A. K. *et al.* (2020). *Long-tail learning via logit adjustment.* ICLR 2021.
- Brody, S., Alon, U. & Yahav, E. (2022). *How Attentive are Graph Attention Networks? (GATv2).* ICLR.

[À COMPLÉTER : références de la variante d'attention croisée (modèle antigène-anticorps
multimodal) et de toute méthode additionnelle effectivement retenue dans la version finale.]
