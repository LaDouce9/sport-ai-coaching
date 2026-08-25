# Méthodologie de Vibe Engineering — Projet Coaching Sportif (Strava/Coros)

> Document vivant. Objectif final : une méthodologie éprouvée par la pratique, pas une
> liste théorique. Chaque pratique appliquée doit être confrontée au réel dans ce projet
> avant d'être jugée bonne ou mauvaise.
>
> Priorité explicite du projet : **comprendre la méthode et les concepts**, pas produire
> l'application la plus rapide/sécurisée/scalable. La stack technique sera choisie pour
> sa simplicité, pas pour sa robustesse en production.

---

## 0. Bien prompter : la méta-pratique transversale

Toutes les étapes ci-dessous reposent sur des allers-retours avec un LLM. La qualité de
ces échanges conditionne tout le reste — c'est la pratique la plus transversale et la plus
facile à négliger.

**Principes à appliquer tout au long du projet :**

- **Contexte avant tâche.** Dire *pourquoi* avant *quoi*. "On ajoute un parseur FIT parce
  que Coros exporte dans ce format et qu'on n'a pas encore de calcul de charge fiable"
  guide mieux que "ajoute un parseur FIT".
- **Expliciter les non-objectifs.** Dire ce qu'on ne veut PAS est aussi utile que dire ce
  qu'on veut : "pas besoin de gérer le multi-athlète", "pas besoin d'authentification
  robuste ici".
- **Un niveau de granularité à la fois.** Ne pas mélanger une question de cadrage
  ("est-ce qu'on stocke les FC brutes ou juste les zones ?") avec une demande d'implémentation
  dans le même message — ça pousse le modèle à trancher des choix de conception en
  passant, sans que ce soit visible.
- **Séparer explicitement lecture et écriture.** "Explique-moi comment X est calculé"
  vs "modifie X pour qu'il fasse Y" ne doivent jamais être ambigus dans la formulation.
- **Donner le critère de succès.** Une demande sans "definition of done" laisse le
  modèle deviner quand s'arrêter — première cause de sur-ingénierie ou de sous-livraison.
- **Corriger tout de suite, pas trois tours plus tard.** Si une réponse part dans la
  mauvaise direction, le signal est plus utile immédiatement qu'après plusieurs messages
  qui accumulent l'erreur.
- **Préférer une question ciblée à une question fourre-tout** en phase de cadrage
  ("cadrage" = ambigu, mieux vaut itérer petit), mais **grouper les demandes indépendantes**
  une fois le cadrage posé (pas besoin de dix allers-retours pour dix tâches non liées).
- **Éviter le vague évaluatif** ("améliore ça", "fais que ce soit propre") : préciser la
  dimension visée (lisibilité, perf, sécurité, cohérence avec le style existant).
- **Donner explicitement le périmètre** ("ne touche pas au parseur Strava", "reste dans
  `src/coros/`") quand une tâche pourrait déborder.

Cette section sera enrichie avec des exemples concrets tirés du projet au fil de l'eau
(bons et mauvais prompts observés).

---

## 1. Méthodologie étape par étape

L'ordre proposé suit une logique de dépendances : chaque étape s'appuie sur un artefact
produit par la précédente.

### Étape 0 — Cadrage par Q&A avec le LLM

Avant d'écrire le moindre `SPEC.md`, on ne part pas d'une spec déjà figée dans notre
tête : on fait rédiger une première version du besoin, puis on demande explicitement au
LLM de **poser des questions de clarification** avant de proposer un contrat fonctionnel.

Pourquoi cet ordre et pas l'inverse (nous écrivons la spec seuls) : un humain qui rédige
seul a tendance à laisser des angles morts implicites ("évidemment on garde l'historique
complet") que le LLM ne peut pas deviner. Le forcer à interroger fait remonter ces angles
morts avant qu'ils ne coûtent des itérations de code.

Déroulé concret :
1. On donne un besoin en une ou deux phrases (ex : "appli qui croise Strava et Coros pour
   proposer un feedback de charge d'entraînement").
2. On demande explicitement : *"Avant de rédiger le SPEC.md, pose-moi toutes les
   questions nécessaires pour lever les ambiguïtés."*
3. On répond, on itère jusqu'à ce que le LLM n'ait plus de question bloquante.
4. Seulement à ce stade, rédaction du `SPEC.md`.

### Étape 1 — Rédaction du SPEC.md

Contrat fonctionnel, pas technique : ce que le système fait, les types de données
manipulés (et leurs unités — watts vs watts/kg, allure vs vitesse), les cas limites
connus, ce qui est explicitement hors scope. Le `SPEC.md` est relu et amendé à chaque
divergence constatée en cours de route (pas figé une fois pour toutes).

### Étape 2 — Constitution du Harness (CLAUDE.md)

Contrairement à une approche "on écrit toutes les conventions d'un coup avant de coder",
on constitue le harness **progressivement** :
- Un `CLAUDE.md` minimal dès le départ (description du projet, gestionnaire de paquets,
  commande de test/lint) — pas une liste exhaustive de règles hypothétiques.
- Une règle n'est ajoutée au harness qu'après avoir été **répétée deux fois** en
  correction manuelle (signal que ce n'est pas un cas isolé).
- Les règles trop spécifiques à un sous-domaine (ex : conventions de parsing FIT)
  partent dans un fichier dédié (`docs/PARSING.md`) référencé depuis `CLAUDE.md`, plutôt
  que de tout centraliser — cf. divulgation progressive.

### Étape 3 — TDD augmenté par l'IA sur les modules critiques

Test-first uniquement là où une erreur silencieuse coûterait cher à détecter : calculs
physiologiques (zones FC, charge d'entraînement, VO2max), parsing de formats externes
(FIT/TCX). Pas de dogmatisme TDD sur le reste (UI, plomberie) — l'objectif ici est
d'observer où le test-first apporte réellement de la valeur, pas de l'appliquer partout
par principe.

### Étape 4 — Discipline Explore/Edit (Plan Mode)

Toute tâche touchant plusieurs fichiers passe par une phase d'exploration en lecture
seule (Plan Mode) avant l'édition. Toute tâche mono-fichier bien définie peut s'en
passer — l'objectif est d'observer le point de bascule où le plan devient rentable.

Ce n'est pas une bascule manuelle entre deux conversations séparées : c'est un mode qui
change d'état **au sein de la même conversation**, initié à l'origine par l'agent
lui-même sur les tâches non triviales — pas seulement sur demande explicite de
l'utilisateur.

**Comparaison écosystème :**

| Outil | Mécanisme | Source |
|---|---|---|
| Claude Code | Plan Mode : bascule dans la même conversation (lecture seule → plan → validation → édition) | Comportement observé dans ce projet |
| JetBrains Junie | Plan Mode natif (`Shift+Tab`, `/plan`, `Ctrl+P` pour la vue dédiée) ; séparation *Ask Mode* (planifier/discuter, aucune édition) / *Code Mode* (agent complet, édite et teste) | [Junie — Plan mode](https://junie.jetbrains.com/docs/junie-cli-plan-mode.html), [Junie — Ask vs Code mode](https://youtrack.jetbrains.com/articles/SUPPORT-A-1832/What-is-the-difference-between-ask-and-code-modes-in-Junie) |
| Cursor | Pas de bascule native — pratique communautaire : explorer dans un thread, puis ouvrir un **nouveau** thread vierge nourri uniquement du plan/spec, pour repartir sur un contexte propre | Pratique d'usage rapportée, non une spec produit |
| Google Antigravity | Fichiers de règles `.agents/rules` (projet, valeur par défaut) ou `~/.gemini/AGENTS.md` (global) ; `GEMINI.md` prioritaire sur `AGENTS.md` en cas de conflit ; limite de 12 000 caractères par fichier | [Antigravity — Rules](https://antigravity.google/docs/rules-workflows/) |

### Étape 5 — Routage par niveau d'effort selon la tâche

Pas de "modèle Driver/Executor" façon Spark, mais une règle pragmatique : les tâches de
raisonnement (choix d'architecture, cadrage) méritent un effort de réflexion plus élevé
que les tâches mécaniques (renommage, nettoyage). À observer concrètement plutôt qu'à
théoriser à l'avance.

Vérifié le 25/08 (voir journal) : Claude Code ne fait **aucun routage automatique** par
complexité de tâche — le principe ci-dessus est donc une discipline manuelle à appliquer
soi-même, pas un comportement natif de l'outil. Seule nuance : quand l'agent principal
délègue à un subagent (tool Agent), il peut choisir explicitement un modèle différent
pour ce subagent — décision de l'IA au moment de l'orchestration, mais toujours
explicite/paramétrée, pas un routage caché du système.

**Comparaison écosystème :**

| Outil | Mécanisme | Source |
|---|---|---|
| Claude Code | Aucun routage automatique par complexité — choix du modèle (`/model`, `--model`, `settings.json`) et de l'effort (`/effort`, `--effort`) toujours explicites ; `/fast` est un toggle manuel (bascule vers Opus) | [Model config](https://code.claude.com/docs/en/model-config.md), [Fast mode](https://code.claude.com/docs/en/fast-mode.md), [Sub-agents](https://code.claude.com/docs/en/sub-agents.md) |
| Cursor | Routage automatique réel : le "Cursor Router" (classifieur "Compass") score chaque requête (0 à 1) sur sa complexité et choisit seul entre un modèle frontier ou économique | [Model routing](https://cursor.com/guides/model-routing) |
| JetBrains Junie | Partiellement automatique : mode "auto-selection" + bascule automatique vers un modèle allégé (Claude Haiku / Gemini Flash) pour les tâches internes ; effort ajustable manuellement via `/effort` | [Model selection](https://junie.jetbrains.com/docs/junie-cli-model-selection.html) |
| Google Antigravity | Manuel : sélection du modèle et du niveau d'effort (Low/Medium/High) via dropdown ou `/effort` — aucun routage automatique constaté dans la documentation | [Models](https://antigravity.google/docs/models/) |

Conséquence pour le harnais : le principe reste dans `AGENTS.md` (portable, énoncé comme
intention plutôt que comme mécanisme), mais les commandes concrètes (`/model`, `/effort`)
n'y ont pas leur place — elles n'existent que côté Claude Code, et seraient même sans
objet pour un utilisateur Cursor (déjà automatique chez eux).

### Étape 6 — Sécurité proportionnée

Pas d'infrastructure de sandboxing façon cluster de calcul. Juste : secrets OAuth
Strava/Coros dans `.env` non commité, jamais lus ni affichés par l'agent, permissions
Claude Code configurées pour refuser explicitement l'accès à `.env`.

### Étape 7 — Outils de context engineering (expérimentation encadrée)

C'est ici qu'on teste **Graphify** et des **Agent Skills via MCP** pour les calculs
répétitifs (VO2max, seuils, lissage HRV) — en prise en main volontaire, avec un objectif
explicite : voir si ça change réellement la qualité des réponses de l'IA sur ce projet,
ou si c'est de l'outillage superflu à cette échelle. Résultat à consigner dans le journal
de bord, pas présupposé.

---

## 2. Fiche des pratiques

### 2.1 Pratiques appliquées dans ce projet

| Pratique | Source | Retour d'expérience |
|---|---|---|
| Prompting structuré (contexte, non-objectifs, granularité) | Ajout | *à compléter* |
| Cadrage par Q&A avant SPEC.md | Ajout | *à compléter* |
| SPEC.md comme contrat fonctionnel évolutif | Fiche initiale | *à compléter* |
| Harness (CLAUDE.md) construit progressivement, règles ajoutées après répétition | Fiche initiale (ajusté) | *à compléter* |
| Divulgation progressive (docs/ spécifiques référencés) | Fiche initiale | *à compléter* |
| TDD ciblé sur modules critiques uniquement | Fiche initiale (ajusté — pas dogmatique) | *à compléter* |
| Tests sur données réelles anonymisées en plus des mocks | Ajout | *à compléter* |
| Explore/Edit via Plan Mode | Fiche initiale | *à compléter* |
| Diffs petits et revuables | Ajout | *à compléter* |
| Suite de non-régression sur métriques calculées (valeurs de référence figées) | Ajout | *à compléter* |
| Routage par niveau d'effort (pragmatique, pas Spark) | Fiche initiale (simplifié) | *à compléter* |
| Secrets en `.env`, permissions Claude Code restreintes | Fiche initiale (simplifié) | *à compléter* |
| Graphify + Agent Skills via MCP (prise en main) | Fiche initiale + demande explicite | Installé en avance sur l'étape 7 (voir journal) — vérifié réel via web (package `graphifyy`, PyPI + GitHub, non fabriqué contrairement à d'autres éléments de la fiche source) |
| Journal de bord coût/bénéfice par pratique | Ajout | *à compléter* |
| AGENTS.md canonique + CLAUDE.md en import (`@AGENTS.md`) | Demande explicite | Claude Code ne lit pas AGENTS.md nativement (vérifié) ; le symlink/import est le pattern officiellement supporté — repo compréhensible par n'importe quel agent sans rien casser côté Claude Code |
| Règle explicite de non-présomption sur données externes (APIs Strava/Coros) dans AGENTS.md | Ajout, suite retour Gemini + incident réel | Ajoutée après un seul incident (schéma Strava halluciné, 25/08) au lieu des deux répétitions habituelles — dérogation assumée et documentée dans AGENTS.md, vu la gravité (pan fonctionnel manquant) ; *impact réel à confirmer au prochain Plan Mode touchant une API externe* |

### 2.2 Pratiques connues, non appliquées ici (bon à savoir)

| Pratique | Pourquoi elle existe | Pourquoi pas ici |
|---|---|---|
| Formats colonnaires Parquet/ORC + partitionnement | Nécessaire à très gros volume (data engineering) | Quelques centaines/milliers d'activités : un SQLite/Postgres suffit, plus simple à déboguer avec l'IA |
| NUMA-aware dual-socket, isolation façon CERN | Calcul HPC multi-tenant à très grande échelle | Projet solo, une seule charge de travail à la fois |
| Kueue (gestion de quotas Kubernetes) | Fair-sharing de ressources entre équipes/jobs | Pas de cluster, pas de contention de ressources à gérer |
| ContainerSSH + OIDC/OAuth2/Kerberos pour l'accès aux sessions | Accès sécurisé multi-utilisateurs à des environnements de calcul partagés | Un seul utilisateur, poste local : la protection `.env` + permissions Claude Code suffit |
| Chiffres de benchmark non sourcés (ex : "MAE de 22.7") | — | Chiffre sans unité ni source dans le document d'origine, vraisemblablement fabriqué — on définira nos propres seuils empiriquement |
| Budget strict de "150-200 instructions" pour CLAUDE.md | Éviter la dilution des règles | Le principe (rester concis) est valide, le chiffre précis est non vérifié — pas de règle numérique dure |
| Vision via AST / graphes de dépendance systématiques | Utile sur de très grosses bases de code | Base de code d'un mini-projet : à réévaluer si Graphify s'avère utile même à cette échelle (question ouverte, pas tranchée) |

*Cette section s'enrichit à chaque fois qu'on écarte une pratique en cours de route —
avec la raison, pas juste le constat.*

---

## 3. Journal de bord

*(rempli au fil des étapes avec : pratique observée, contexte, gain/coût constaté, verdict)*

### 2026-08-24 — Détour assumé : outillage avant cadrage

Installation de Graphify et bascule AGENTS.md/CLAUDE.md faites juste après la
configuration de base, donc avant l'étape 0 (cadrage Q&A) — en avance sur l'ordre
défini en section 1. Décision explicite, pas un oubli :
- Repo quasi vide → risque faible de casser quoi que ce soit, terrain sûr pour prendre
  en main un nouvel outil.
- Objectif explicite de prise en main de Graphify, indépendant du calendrier du projet.
- Avant d'exécuter quoi que ce soit, vérification que les deux éléments cités par
  l'utilisateur étaient réels (et pas un nouvel avatar du problème de la fiche
  initiale) : Graphify existe et correspond à sa description (package `graphifyy` sur
  PyPI, dépôt GitHub actif) ; AGENTS.md n'est en revanche PAS lu nativement par Claude
  Code (vérifié par recherche web), d'où le choix du pattern import plutôt qu'un
  remplacement pur et simple.
- Point d'attention pour la suite : Graphify tourne sur un code encore vide — sa vraie
  valeur (graphe de dépendances utile) ne pourra être évaluée qu'une fois du code réel
  écrit. À réévaluer après l'étape 3 ou 4.

### 2026-08-24 — Étape 0 (cadrage Q&A) et étape 1 (SPEC.md V1)

L'utilisateur a fourni un document produit complet (4 modules : ingestion, sports sans
montre, coaching adaptatif, stratégie de course) en demandant explicitement de prioriser
plutôt que de tout spécifier. Bon test réel de l'étape 0 :

- Reformulation du périmètre réduit avant de poser des questions, pour valider la
  compréhension avant d'investir du temps dans le détail.
- Une des questions de cadrage (accès API Coros) a révélé un vrai risque technique non
  mentionné dans le document produit : l'API développeur officielle Coros nécessite une
  approbation "entreprise", inadaptée à un projet perso. Recherche web faite avant de
  trancher plutôt que de supposer — a permis de découvrir une alternative pertinente
  (serveur MCP Coros, self-service) et surtout un fait simplificateur décisif : Coros
  était déjà synchronisé vers Strava sur le compte réel de l'utilisateur, ce qui rend
  Strava seul suffisant pour le V1. **Sans cette vérification, le SPEC V1 aurait
  probablement embarqué une intégration Coros risquée dès le départ.**
- Gain concret de l'étape 0 : le périmètre V1 rédigé dans `SPEC.md` est net (ingestion
  Strava + module sans-montre + charge par zone, rien d'autre), alors que le document
  produit initial aurait naturellement tiré vers une spec beaucoup plus large.
- Le mapping "activité → zones corporelles par défaut" proposé par l'utilisateur pendant
  le Q&A a changé la conception du module de charge (poids par défaut + surcharge
  manuelle plutôt que saisie manuelle pure) — exemple concret où le cadrage a amélioré
  la conception, pas juste réduit le scope.

### 2026-08-25 — Schéma de données non vérifié en revue de plan

Premier passage réel en Plan Mode (ingestion Strava). Le sous-agent de planification a
produit un schéma SQLite complet (noms de colonnes, types) en le présentant avec
assurance, sans jamais consulter la vraie documentation Strava — alors même que le
`SPEC.md` demandait explicitement de vérifier ce point avant de le figer. L'utilisateur
a posé la question directement ("comment sais-tu le schéma de données ?"), à trois
reprises, avant que la vérification ne soit faite.

**Ce qui a marché :** la question a été posée en revue de plan, donc avant qu'une seule
ligne de code ne soit écrite — c'est précisément l'intérêt de la discipline Explore/Edit
(étape 4) : le coût de l'erreur était encore nul. Vérification faite après coup :
- L'objet "summary" (liste d'activités) et l'objet "detailed" (une activité) de l'API
  Strava n'exposent pas les mêmes champs — le schéma halluciné mélangeait les deux sans
  le savoir.
- Un endpoint entier (`/activities/{id}/streams`, séries temporelles FC/allure/altitude)
  était absent du plan — pas une erreur de détail, un pan fonctionnel manquant,
  directement lié à un besoin produit réel exprimé dès le document de cadrage initial
  (découplage aérobie, etc.) mais perdu en cours de route lors de la réduction du V1.
- Cette même vérification a aussi fait revenir sur le choix de bibliothèque
  (`requests` brut abandonné pour `stravalib`, maintenue et déjà correcte sur ce
  schéma) : l'incident a servi d'argument concret dans un arbitrage qui semblait acquis.

**Leçon pour le document final :** demander "comment sais-tu ça ?" sur une affirmation
technique précise (schéma, nom de champ, signature de méthode) est une pratique de
revue à elle seule, indépendante du Plan Mode — le Plan Mode crée juste le bon moment
pour la poser à moindre coût.

### 2026-08-25 — Retour Gemini sur AGENTS.md : un LLM tiers reproduit le même biais

Demande d'avis externe (Gemini) sur deux idées d'ajout à `AGENTS.md` : un persona
("tu es un expert...") et une règle de non-présomption sur les schémas d'API externes.
Réponse de Gemini pertinente sur le fond (voir fiche §4), mais elle cite comme fait
établi un seuil de "150 à 200 instructions" pour la taille d'un fichier de règles —
exactement le même chiffre que ce document avait déjà flaggé comme non sourcé et
vraisemblablement fabriqué en §2.2, sans que Gemini ne le sache. Confirmation en
conditions réelles que la discipline "vérifier avant de croire" (cf. incident du
25/08 ci-dessus) doit s'appliquer à l'avis d'un LLM tiers sur notre méthodologie,
pas seulement au code produit par l'agent principal du projet.

---

## 4. Catalogue des failles rencontrées

Vue transverse, organisée par catégorie plutôt que par date : chaque ligne renvoie à
l'entrée complète du journal (§3) au lieu de répéter le récit. Une catégorie sans
exemple reste listée tant qu'elle reste pertinente pour le projet, marquée comme telle
plutôt que supprimée — l'absence de cas est une information utile, pas un vide à
combler artificiellement.

| # | Catégorie | Exemple concret | Référence | Leçon retenue |
|---|---|---|---|---|
| 1 | Donnée non sourcée / fabriquée | Chiffre de benchmark ("MAE de 22.7") sans unité ni source dans le document produit initial ayant servi de base à la fiche de pratiques | §2.2 — 24/08 | Ne jamais reprendre un chiffre sans savoir d'où il vient ; définir ses propres seuils empiriquement plutôt que d'hériter d'une valeur non vérifiable |
| 2 | Donnée non sourcée / fabriquée | Seuil "150-200 instructions" pour la taille d'un fichier de règles, repris tel quel par Gemini en conseil sur `AGENTS.md`, sans source citée | §3 — 25/08, "Retour Gemini sur AGENTS.md" | La vérification s'applique à toute source d'affirmation technique, y compris l'avis d'un LLM tiers sur notre propre méthodologie |
| 3 | Absence de vérification avant affirmation technique | Schéma SQLite complet (colonnes, types) halluciné en Plan Mode pour l'ingestion Strava : mélange des objets `summary`/`detailed`, endpoint `/activities/{id}/streams` absent du plan | §3 — 25/08, "Schéma de données non vérifié en revue de plan" | Poser "comment sais-tu ça ?" sur toute affirmation de schéma/API/signature avant qu'elle soit figée — coût nul si posé en Plan Mode, avant la moindre ligne de code |
| 4 | Complexification inutile d'une tâche (sur-ingénierie, robustesse non demandée) | Aucun cas observé à ce jour | — | Catégorie connue mais pas encore rencontrée dans ce projet — à surveiller notamment lors des tâches plus larges (étapes 3-4, TDD et Plan Mode répétés) |

*Table mise à jour à chaque nouvelle entrée de journal qui révèle une faille — pas
seulement les incidents "négatifs" : une vérification qui a empêché une faille reste
dans le journal (§3) mais n'entre ici que si la faille a réellement eu lieu.*
