# SPEC.md — V1

Contrat fonctionnel. Issu de l'étape 0 (cadrage par Q&A) sur le document produit complet
fourni par l'utilisateur — voir `METHODOLOGIE.md` pour le détail de la discussion de
cadrage. Document amendé à chaque divergence constatée en cours de route.

## 1. Périmètre V1

**Objectif :** récupérer la donnée d'entraînement réelle et rendre visible la charge par
zone corporelle, sans aucune logique de recommandation. Rien d'autre.

**Dans le V1 :**
1. Ingestion des activités **Strava** (OAuth2).
2. Saisie manuelle de séances **"sans montre"** (durée, RPE global, RPE par zone
   corporelle).
3. Calcul et restitution d'une **charge par zone corporelle**, combinant activités
   Strava (via mapping activité → zones par défaut) et séances manuelles.
4. Restitution via scripts/CLI + notebooks.

**Explicitement hors V1 :**
- **Coros** — reporté en V1.1. Coros est déjà synchronisé vers Strava sur le compte de
  l'utilisateur, donc Strava seul couvre déjà l'essentiel des activités pour le V1.
  Coros sera ajouté ensuite spécifiquement pour les métriques qu'il est seul à fournir
  (EvoLab : HRV, recovery, training load) — accès probable via le serveur MCP Coros
  (self-service, pas d'approbation entreprise requise), à confirmer par un spike
  technique avant de l'intégrer au SPEC.
- Plans d'entraînement périodisés, adaptation dynamique du plan, détection de
  découplage aérobie, recommandations d'exercices.
- Stratégie de course (GPX), scraping de résultats, prédictions de chrono.
- Modélisation d'effets santé (tabac/vapotage) sur la FC.
- Segment efforts / VAM Strava.
- Toute interface web, vocale ou conversationnelle.
- Toute règle d'adaptation automatique des séances futures (dépend d'un module de plan
  qui n'existe pas en V1).

## 2. Types de données et unités

Point d'attention explicite (cf. `METHODOLOGIE.md`, risque identifié dès la fiche
initiale) : ne jamais confondre les unités suivantes lors de l'implémentation.

| Donnée | Unité | Source |
|---|---|---|
| Distance | mètres | Strava API |
| Durée | secondes — **`moving_time` et `elapsed_time` sont distincts dans l'API Strava**, choix à documenter explicitement au moment de l'implémentation | Strava API |
| Fréquence cardiaque | bpm | Strava API (`average_heartrate`, `max_heartrate`), quand le capteur était présent |
| Dénivelé positif | mètres | Strava API (`total_elevation_gain`) |
| Type d'activité | tel que renvoyé par l'API Strava (`type`/`sport_type`) — la liste exacte des valeurs possibles (ex : présence ou non d'un type "Rugby") est à vérifier contre la documentation officielle au moment de l'implémentation, pas supposée ici | Strava API |
| RPE (séance manuelle ou zone) | échelle 1–10 (Borg CR10) | Saisie utilisateur |
| Charge par zone | voir formule section 3 — **pas d'unité physiologique établie, c'est un score relatif interne au projet, pas une mesure validée scientifiquement** | Calculée |

## 3. Module "Sports sans Montre" & charge par zone corporelle

### 3.1 Zones corporelles (liste fermée)

Enum fixe, amendable si un besoin réel apparaît (pas par anticipation) :
`ischios`, `quadriceps`, `adducteurs`, `mollets`, `tendon_achille`, `genoux`,
`fessiers`, `bas_du_dos`, `haut_du_dos`, `epaules`, `avant_bras`, `mains_doigts`.

### 3.2 Mapping activité → zones par défaut

Chaque type d'activité (Strava ou saisie manuelle) a un profil par défaut de charge
relative par zone (poids de 0 à 1). Exemples de départ, à ajuster empiriquement au fil
du journal de bord — **ce ne sont pas des vérités physiologiques, ce sont des poids
heuristiques initiaux** :

| Activité | Zones fortement sollicitées (poids ~0.7–1) | Zones peu sollicitées (poids ~0–0.2) |
|---|---|---|
| Course à pied | ischios, quadriceps, mollets, tendon_achille | epaules, avant_bras, mains_doigts |
| Escalade (bloc) | avant_bras, mains_doigts, epaules, haut_du_dos | ischios, quadriceps, mollets |
| Rugby | corps entier (contacts) — pas de zone dominante unique | — |
| Vélo | quadriceps, ischios (modéré) | avant_bras, mains_doigts, epaules |

Cette table vit dans un fichier de config versionné (pas codée en dur dans la logique),
pour rester amendable sans toucher au code.

### 3.3 Calcul de la charge

Pour une séance donnée :

```
charge_zone(séance, zone) = durée_minutes(séance) × intensité(séance) × poids_zone(activité, zone)
```

- `intensité(séance)` : RPE global saisi (manuel), ou dérivé du `%FC max` moyen si
  disponible (Strava avec capteur FC) — la méthode de dérivation exacte est un détail
  d'implémentation à trancher à l'étape suivante, pas figée ici.
- Pour une séance manuelle, l'utilisateur peut **surcharger** le poids par défaut d'une
  zone spécifique avec son propre RPE de zone (ex : rugby + "adducteurs raides" → RPE
  zone adducteurs saisi explicitement plutôt que le poids par défaut du mapping).
- La charge par zone sur une période (ex : 7 jours glissants) est la somme des charges
  de zone de toutes les séances de la période.

### 3.4 Cas limites à traiter

- Activité Strava sans donnée FC (capteur absent) → pas d'intensité dérivable
  automatiquement ; comportement à définir (RPE par défaut du type d'activité, ou
  saisie manuelle demandée) — **non résolu ici, à trancher à l'implémentation**.
- Séance avec plusieurs zones surchargées à des RPE différents dans une même saisie.
- Agrégation par période : ambiguïté fuseau horaire Strava (`start_date` UTC vs
  `start_date_local`) — choisir explicitement `start_date_local` pour l'agrégation
  hebdomadaire côté utilisateur.
- Pas de déduplication activité Strava / séance manuelle : le module manuel est réservé
  aux séances *sans* capteur, donc pas de recouvrement attendu en usage normal.

## 4. Stockage

SQLite local (`data/`, non versionné — cf. `AGENTS.md`).

## 5. Definition of done V1

- [ ] Authentification OAuth2 Strava fonctionnelle, récupération des activités d'une
      période donnée en base locale.
- [ ] Saisie manuelle d'une séance (type, durée, RPE global, zones + RPE par zone en
      surcharge optionnelle) via CLI.
- [ ] Restitution (notebook ou rapport CLI) de la charge cumulée par zone corporelle sur
      une période, combinant Strava + manuel.
- [ ] Tests sur les calculs de charge (cas simples + cas limites de la section 3.4) et
      sur le parsing des réponses Strava (mocks + au moins un jeu de données réel
      anonymisé).
