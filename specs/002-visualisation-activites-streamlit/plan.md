# plan — Visualisation Streamlit des activités (spec : specs/002-visualisation-activites-streamlit/spec.md)

## Vérifications préalables (dans le code réel)

- Connexion réutilisable à la DB ? → oui, `storage.connect(db_path: Path) ->
  sqlite3.Connection` dans `src/sport_coaching/ingestion/storage.py` ; ne prend pas
  en charge le chemin lui-même, c'est à l'appelant de le fournir.
- Résolution actuelle du chemin de la DB ? → `config.load_strava_config().db_path`
  (via `SPORT_COACHING_DB_PATH` ou un défaut `data/sport_coaching.sqlite3`), mais
  cette fonction lève une `KeyError` si `STRAVA_CLIENT_ID`/`STRAVA_CLIENT_SECRET` sont
  absents du `.env` — inadapté pour une app en lecture seule. Décision : ajouter une
  fonction étroite `resolve_db_path()` dédiée, qui ne dépend pas des secrets Strava.
- La carte détail voulue existe-t-elle déjà ? → oui, une fonction déjà présente dans
  `src/sport_coaching/metrics/activity_report.py` produit exactement les indicateurs
  et graphiques décrits dans le spec (distance, durée, allure, D+, FC moy/max,
  cadence, indice d'effort ; graphiques allure/FC/altitude/allure-par-km), à partir
  d'une connexion et d'un id d'activité, et retourne une figure affichable telle
  quelle — pas de nouvelle logique de calcul à écrire.
- Pattern existant de test touchant la DB ? → oui, dans
  `tests/metrics/test_activity_report.py` : DB temporaire via
  `storage.connect(tmp_path / "test.sqlite3")` + `storage.init_db(conn)`, données
  insérées via `storage.upsert_activity(...)` avec une fixture `_activity(**overrides)`
  — directement réutilisable pour tester le listing/filtre.
- Convention d'ajout de dépendance ? → `pyproject.toml` n'a qu'une liste plate
  `[project.dependencies]` (pas de groupe `optional-dependencies`) ; Streamlit y va
  directement via `uv add streamlit`.
- Scaffolding UI existant ? → aucun (`app/`, `ui/`, `streamlit` : zéro résultat dans
  tout le repo) — module entièrement nouveau.

## Approche

Nouveau sous-module `src/sport_coaching/app/`, séparant la couche données
(listing/filtre d'activités, testable sans Streamlit) de la couche UI (rendu
Streamlit). Aucune nouvelle logique de calcul : la carte détail réutilise
intégralement le code déjà présent dans `metrics/activity_report.py`.

## Fichiers touchés

- `src/sport_coaching/app/__init__.py` — nouveau, vide (package marker, cohérent avec
  `ingestion/`, `metrics/`, `parsing/`).
- `src/sport_coaching/app/queries.py` — nouveau : fonction de listing des activités
  (colonnes utiles à l'affichage liste) + fonction de récupération des types
  d'activité distincts (pour le filtre), à partir d'une connexion déjà ouverte.
- `src/sport_coaching/app/streamlit_app.py` — nouveau : point d'entrée Streamlit,
  liste + filtre par type (via `queries.py`), gestion du clic sur une activité,
  affichage de la carte détail.
- `src/sport_coaching/ingestion/config.py` — modifié : ajout de
  `resolve_db_path() -> Path`, qui isole la résolution du chemin (env var / défaut)
  sans dépendre des secrets Strava ; `load_strava_config()` peut être réécrite pour
  l'appeler en interne, pour ne pas dupliquer la logique.
- `src/sport_coaching/ingestion/storage.py` — réutilisé sans changement (`connect`).
- `src/sport_coaching/metrics/activity_report.py` — réutilisé sans changement (la
  fonction de rendu de la carte détail).
- `pyproject.toml` — modifié : ajout de `streamlit` dans `[project.dependencies]`.
- `tests/app/test_queries.py` — nouveau : tests de `queries.py`, pattern DB temporaire
  déjà établi dans le projet.
- `README.md` — modifié : ajout de la commande de lancement de l'app dans la section
  État.

## Étapes (petits diffs)

1. Ajouter `streamlit` à `pyproject.toml` (`uv add streamlit`), vérifier `uv sync`.
2. Ajouter `config.resolve_db_path()` (extraction depuis la logique déjà présente
   dans `load_strava_config()`, sans rien changer côté ingestion existante) + test.
3. Créer `app/__init__.py` + `app/queries.py` (listing, filtre par type) + ses tests.
4. Créer `app/streamlit_app.py` (liste, filtre, clic → carte détail via
   `activity_report`).
5. Vérification manuelle sur la vraie base (271 activités), y compris sur une
   activité sans FC/cadence/watts (cas limite du spec).
6. Mettre à jour le README (commande de lancement).

## Décisions à trancher

Aucune restante — les deux points ouverts (résolution du chemin DB, emplacement du
code) ont été tranchés avec l'utilisateur avant validation de ce plan :
- Résolution du chemin DB : nouvelle fonction étroite `resolve_db_path()`.
- Emplacement : sous-module `app/` avec deux fichiers (`queries.py` + `streamlit_app.py`).

## Plan de tests

- `app/queries.py` : tests unitaires (liste complète, filtre sur un type présent,
  filtre sur un type absent → liste vide), sur le pattern DB temporaire déjà établi.
- `config.resolve_db_path()` : test que la résolution fonctionne sans variables
  Strava dans l'environnement (le point même de son existence).
- `app/streamlit_app.py` : pas de test automatisé du rendu (aucun framework de test
  Streamlit en place, hors scope pour ce premier jet) — vérification manuelle sur la
  vraie base, en particulier le cas limite FC/cadence/watts manquants, conformément à
  la règle « un test vert ne garantit pas un résultat correct ».

## Definition of done (technique)

- `uv run pytest` reste vert, y compris les nouveaux tests.
- `streamlit run src/sport_coaching/app/streamlit_app.py` se lance sans erreur sur la
  vraie base.
- Vérification manuelle : liste affichée, filtre par type fonctionne, clic sur une
  activité affiche la carte détail sans planter, y compris pour une activité sans FC.
- Couvre la Definition of done fonctionnelle de `specs/002-.../spec.md`.
