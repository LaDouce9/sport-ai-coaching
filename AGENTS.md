# AGENTS.md

Fichier canonique, lu par n'importe quel agent de codage (Codex, Cursor, Gemini CLI,
Aider...). Pour Claude Code, `CLAUDE.md` l'importe via `@AGENTS.md` — voir
`docs/METHODOLOGIE.md` §1.1.

Harnais minimal — enrichi uniquement quand une règle a dû être rappelée deux fois
manuellement. Ne pas ajouter de règles hypothétiques par anticipation.

## Projet

Application de coaching sportif personnelle croisant les données Strava et Coros
(charge d'entraînement, métriques physiologiques). Objectif du projet : prendre en main
une méthodologie de développement assisté par IA — voir `docs/METHODOLOGIE.md`.

MVP actuel : ingestion via scripts/CLI + notebooks d'exploration, visualisation via une
interface Streamlit locale en lecture seule (`src/sport_coaching/app/`).

## Stack

- Python 3.13
- Gestionnaire de paquets : `uv` (`pyproject.toml` + `uv.lock`) — commandes `uv add`,
  `uv sync`, `uv run`
- Tests : pytest, commande `uv run pytest`

## Conventions

- Layout `src/sport_coaching/` avec sous-modules par responsabilité :
  `ingestion/` (clients API Strava/Coros), `parsing/` (FIT/TCX), `metrics/` (calculs
  physiologiques : VO2max, TSS, zones FC).
- Unités de référence — système métrique partout : distances en **mètres** (jamais en
  miles), fréquence cardiaque en **bpm**, allure en **min/km**, vitesse en **km/h**.
  Toute donnée externe reçue dans une autre unité est convertie explicitement, jamais
  laissée telle quelle. Voir la table unités/types de
  `specs/001-ingestion-strava-v1/spec.md` (§2) pour les subtilités réelles déjà
  observées (ex. `moving_time` vs `elapsed_time`, divergence FC calculée/Strava).

## Discipline Explore/Edit

Toute modification touchant plusieurs fichiers, ou dont l'approche d'implémentation
n'est pas déjà validée, démarre en Plan Mode avant toute édition — à l'initiative de
l'agent, pas seulement sur demande explicite. Voir `docs/METHODOLOGIE.md` (§2.5).

## Ne pas faire

- Ne pas lire ni afficher les secrets (tokens OAuth) — ils vivent dans `.env`, jamais
  commité.
- Ne pas committer dans `data/` (contient des exports personnels réels).
- Ne jamais présumer, deviner ou halluciner dans ta réponse la structure d'une réponse
  d'API externe (schéma JSON, nom de champ, type, endpoint), un format de fichier
  (FIT/TCX), ou une signature de méthode d'une bibliothèque cliente. Si ce n'est pas
  explicitement vérifié (doc officielle, réponse réelle observée, code source de la
  lib) :
  - Le dire explicitement ("non vérifié") plutôt que de le présenter avec assurance.
  - Vérifier avant de figer un plan ou d'écrire du code dessus — pas après coup.

  Exception à la règle "deux répétitions avant ajout au harnais" ci-dessus : ajoutée
  après un seul incident, jugé assez coûteux pour justifier la dérogation (schéma
  Strava halluciné en Plan Mode, pan fonctionnel entier manquant — voir
  `docs/JOURNAL.md`, entrée du 2026-08-25 « Schéma de données non vérifié en revue de
  plan » et §3 Catalogue des failles).

## Référence

- `specs/001-ingestion-strava-v1/spec.md` : contrat fonctionnel V1 (rédigé, amendé au
  fil de l'eau). Travail en cours = dossier le plus récent sous `specs/` ; les specs
  terminées y restent archivées.
- `docs/METHODOLOGIE.md` : méthodologie générale (socle, boucle par feature,
  disciplines transversales).
- `docs/JOURNAL.md` : journal de bord et incidents réels du projet.
- `.claude/skills/` : skills disponibles (ex. `messages-de-commit`, `redaction-spec`,
  `redaction-plan`).
- `.claude/commands/` : commandes slash disponibles (ex. `/nouvelle-feature`, cycle
  complet cadrage → spec → plan → implémentation).
