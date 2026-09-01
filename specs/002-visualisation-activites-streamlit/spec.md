# spec — Visualisation des activités (interface Streamlit)

## Objectif
Premier jet minimal d'une interface Streamlit locale, une seule page, pour parcourir
facilement les activités déjà synchronisées en base — sans logique de recommandation
ni saisie, juste de la visualisation.

## Comportement attendu
- Entrée : les activités déjà synchronisées et stockées localement (271 activités
  actuellement, 10 types distincts : Run, Ride, Hike, Swim, Workout, Walk, TrailRun,
  AlpineSki, Snowboard, Rowing).
- Sortie :
  - Une **vue liste** à la maille activité (nom, date, type, distance, durée...),
    filtrable par type au clic.
  - Un **clic sur une activité** ouvre une **carte détail** avec :
    - Indicateurs clés : distance, durée, allure moyenne, dénivelé positif,
      fréquence cardiaque moyenne, fréquence cardiaque max, cadence moyenne, indice
      d'effort relatif.
    - Graphiques : allure en fonction de la distance, fréquence cardiaque en
      fonction de la distance, profil d'altitude, allure par kilomètre.
- Règles : unités conformes à `AGENTS.md` (mètres, bpm, min/km, km/h).

## Cas limites
- Si la fréquence cardiaque n'est pas disponible pour une activité (~28 % de
  couverture sur les 271 activités actuelles), le graphique correspondant affiche un
  message clair plutôt que d'être vide ou erroné.
- Idem si la cadence ou la puissance ne sont pas disponibles pour l'activité (~49 %
  / ~35 % de couverture).
- Aucune activité pour un type filtré → liste vide, pas d'erreur.
- Base de données vide ou absente → message clair plutôt qu'un plantage silencieux
  (comportement précis à trancher à l'implémentation).

## Hors-scope
- Sessions manuelles ("sports sans montre") — le module n'existe pas encore.
- Filtres autres que par type d'activité (période, recherche texte...) — itération
  suivante.
- Toute modification de données (pas d'édition/suppression depuis l'UI).
- Déploiement — usage local uniquement pour ce premier jet.

## Dépendances externes
- Nouvelle dépendance externe : Streamlit (bibliothèque d'interface web Python),
  absente du projet aujourd'hui.
- Aucune dépendance API externe nouvelle — les données proviennent uniquement de
  l'ingestion Strava déjà en place.

## Definition of done
- La page se lance et affiche la liste des activités sans planter.
- Le filtre par type d'activité fonctionne.
- Cliquer sur une activité affiche sa carte détail (indicateurs + graphiques) sans
  planter, y compris pour une activité sans donnée de fréquence cardiaque, de
  cadence ou de puissance.
