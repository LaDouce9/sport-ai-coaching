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

### Étape 5 — Routage par niveau d'effort selon la tâche

Pas de "modèle Driver/Executor" façon Spark, mais une règle pragmatique : les tâches de
raisonnement (choix d'architecture, cadrage) méritent un effort de réflexion plus élevé
que les tâches mécaniques (renommage, nettoyage). À observer concrètement plutôt qu'à
théoriser à l'avance.

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
