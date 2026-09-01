# sport-coaching-ai

Projet d'apprentissage : coaching sportif personnel croisant les données Strava et
Coros, utilisé comme terrain de pratique pour une méthodologie de développement assisté
par IA. La démarche méthodologique compte plus que l'application elle-même — voir
[docs/METHODOLOGIE.md](docs/METHODOLOGIE.md).

## Setup

```bash
uv sync
```

## Setup Strava

1. Créer une app sur [strava.com/settings/api](https://www.strava.com/settings/api)
   (Authorization Callback Domain : `localhost`).
2. Copier `.env.example` en `.env`, renseigner `STRAVA_CLIENT_ID`/`STRAVA_CLIENT_SECRET`.
3. Autorisation initiale (une fois) :
   ```bash
   uv run python -m sport_coaching.ingestion.cli authorize
   ```
   Ouvre une URL à autoriser dans le navigateur. Après autorisation, Strava redirige
   vers `http://localhost` — **la page échoue à charger, c'est normal** (aucun serveur
   n'écoute sur `localhost`, exprès, pour rester simple). Ce qui compte, c'est l'URL
   dans la barre d'adresse à ce moment-là, du style :
   ```
   http://localhost/?state=&code=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX&scope=read,activity:read_all
   ```
   Copier uniquement la valeur entre `code=` et le `&` suivant, et la coller quand le
   terminal la demande. Remplit `STRAVA_REFRESH_TOKEN` dans `.env`.
4. Synchronisation des activités :
   ```bash
   uv run python -m sport_coaching.ingestion.cli sync           # incrémental
   uv run python -m sport_coaching.ingestion.cli sync --full    # historique complet
   ```

## Visualiser les activités

```bash
uv run streamlit run src/sport_coaching/app/streamlit_app.py
```

Nécessite une synchronisation Strava préalable (voir ci-dessus) — la page prévient si
`data/sport_coaching.sqlite3` est absent. Aucun secret Strava requis pour cette
commande : lecture seule de la base déjà synchronisée.

## Structure

```
src/sport_coaching/
├── ingestion/   # clients API Strava/Coros
├── parsing/     # fichiers FIT/TCX
├── metrics/     # calculs physiologiques (VO2max, TSS, zones FC)
└── app/         # interface Streamlit (visualisation)
notebooks/       # exploration
tests/           # pytest (uv run pytest)
data/            # exports locaux + sport_coaching.sqlite3, non versionné
docs/            # METHODOLOGIE.md, JOURNAL.md
specs/           # spec.md/plan.md par feature (001-ingestion-strava-v1/, ...)
```

## État

Ingestion Strava (activités + streams) implémentée — voir
`specs/001-ingestion-strava-v1/spec.md` pour le périmètre V1 complet et sa Definition
of Done. Premier jet de visualisation des activités livré (Streamlit, voir
`specs/002-visualisation-activites-streamlit/spec.md`). Prochaine étape : module de
saisie manuelle "sports sans montre" et calcul de charge par zone corporelle.
