# sport-coaching-ai

Projet d'apprentissage : coaching sportif personnel croisant les données Strava et
Coros, utilisé comme terrain de pratique pour une méthodologie de développement assisté
par IA. La démarche méthodologique compte plus que l'application elle-même — voir
[docs/METHODOLOGIE.md](docs/METHODOLOGIE.md).

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows (git bash)
pip install -r requirements.txt
```

## Structure

```
src/sport_coaching/
├── ingestion/   # clients API Strava/Coros
├── parsing/     # fichiers FIT/TCX
└── metrics/     # calculs physiologiques (VO2max, TSS, zones FC)
notebooks/       # exploration
tests/           # pytest
data/            # exports locaux, non versionné
docs/            # SPEC.md, METHODOLOGIE.md
```

## État

Configuration de base en place. Étape suivante : cadrage du besoin par Q&A avant
rédaction de `docs/SPEC.md` (voir méthodologie, étape 0).
