# AGENTS.md

Fichier canonique, lu par n'importe quel agent de codage (Codex, Cursor, Gemini CLI,
Aider...). Pour Claude Code, `CLAUDE.md` l'importe via `@AGENTS.md` — voir
`docs/METHODOLOGIE.md` étape 2.

Harnais minimal — enrichi uniquement quand une règle a dû être rappelée deux fois
manuellement. Ne pas ajouter de règles hypothétiques par anticipation.

## Projet

Application de coaching sportif personnelle croisant les données Strava et Coros
(charge d'entraînement, métriques physiologiques). Objectif du projet : prendre en main
une méthodologie de développement assisté par IA — voir `docs/METHODOLOGIE.md`.

MVP actuel : scripts/CLI + notebooks d'exploration, pas d'interface web.

## Stack

- Python 3.13
- Gestionnaire de paquets : pip + venv (`requirements.txt`)
- Tests : pytest, commande `pytest`

## Conventions

- Layout `src/sport_coaching/` avec sous-modules par responsabilité :
  `ingestion/` (clients API Strava/Coros), `parsing/` (FIT/TCX), `metrics/` (calculs
  physiologiques : VO2max, TSS, zones FC).
- Secrets (tokens OAuth) dans `.env`, jamais lus ni affichés par l'agent.
- Pas de commit dans `data/` (contient des exports personnels réels).

## Discipline Explore/Edit

Toute modification touchant plusieurs fichiers, ou dont l'approche d'implémentation
n'est pas déjà validée, démarre en Plan Mode avant toute édition — à l'initiative de
l'agent, pas seulement sur demande explicite. Voir `docs/METHODOLOGIE.md` (étape 4).

## Référence

- `docs/SPEC.md` : contrat fonctionnel (en attente de l'étape 0 de cadrage).
- `docs/METHODOLOGIE.md` : méthodologie et journal de bord du projet.
