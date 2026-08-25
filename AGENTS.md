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
- Gestionnaire de paquets : `uv` (`pyproject.toml` + `uv.lock`) — commandes `uv add`,
  `uv sync`, `uv run`
- Tests : pytest, commande `uv run pytest`

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

## Non-présomption sur données externes (APIs Strava/Coros)

Ne jamais présumer, deviner ou halluciner dans ta réponse. Par exemple la structure d'une réponse d'API externe
(schéma JSON, nom de champ, type, endpoint), un format de fichier (FIT/TCX), ou une
signature de méthode d'une bibliothèque cliente. Si ce n'est pas explicitement vérifié
(doc officielle, réponse réelle observée, code source de la lib) :
- Le dire explicitement ("non vérifié") plutôt que de le présenter avec assurance.
- Vérifier avant de figer un plan ou d'écrire du code dessus — pas après coup.

Exception à la règle "deux répétitions avant ajout au harnais" ci-dessus : ajoutée
après un seul incident, jugé assez coûteux pour justifier la dérogation (schéma Strava
halluciné en Plan Mode, pan fonctionnel entier manquant — voir `docs/METHODOLOGIE.md`,
journal du 25/08 et §4).

## Référence

- `docs/SPEC.md` : contrat fonctionnel V1 (rédigé, amendé au fil de l'eau).
- `docs/METHODOLOGIE.md` : méthodologie et journal de bord du projet.
