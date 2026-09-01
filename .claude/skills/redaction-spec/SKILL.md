---
name: redaction-spec
description: >
  Rédiger le spec (contrat fonctionnel) d'UNE feature — le QUOI, jamais le COMMENT.
  Utiliser dès qu'on démarre une nouvelle feature ou qu'on formalise un besoin avant
  d'implémenter. Commence toujours par poser des questions de clarification.
---

# Rédaction de spec (mode « inspecteur »)

Un spec décrit **ce que** le système doit faire pour UNE feature — jamais le détail
d'implémentation (ça, c'est le plan). But : un contrat clair, assez léger pour tenir
dans le contexte, qui remonte fidèlement l'intention.

## Étape 1 — Cadrage : poser les questions AVANT de rédiger

Ne pas rédiger sur une intention devinée. D'abord **poser les questions qui lèvent les
ambiguïtés**, puis attendre les réponses. Itérer jusqu'à épuisement des questions
bloquantes. Balayer au minimum :

- **Objectif & valeur** — à quoi ça sert, pour qui ?
- **Entrées / sorties** — quelles données en entrée, quel résultat, quel format, et
  **avec quelles unités** ?
- **Cas limites** — données manquantes/partielles, valeurs aberrantes, cas vide.
- **Hors-scope** — qu'est-ce qu'on ne fait PAS dans cette feature ?
- **Dépendances externes** — API/format tiers (Strava, Coros, FIT/TCX) ? Si oui, le
  **schéma est présumé inconnu tant qu'il n'est pas vérifié** (cf. AGENTS.md) : le
  noter comme point à vérifier, ne rien figer dessus.
- **Definition of done** — à quoi reconnaît-on que c'est fini (tests, sortie observée) ?

## Étape 2 — Rédiger la spec

Déterminer d'abord le numéro de la feature : dernier dossier `specs/<N>-.../` existant
+ 1, **zero-paddé sur 3 chiffres** (ex. après `specs/001-.../`, la suivante est
`specs/002-<nom-court>/`, pas `specs/2-.../`). Créer `specs/<N>-<nom-court>/spec.md`.

Suivre la structure de `templates/spec-template.md`. Remplir chaque section ; laisser
`(à vérifier)` ce qui n'est pas confirmé plutôt que de l'inventer.

## Règles d'or

- **Le QUOI, pas le COMMENT** : comportement observable, pas d'algorithme ni de choix
  technique (ça va dans le plan).
- **Un spec par feature**, dans `specs/<N>-<nom-court>/spec.md` (dossier numéroté,
  zero-paddé sur 3 chiffres).
- **Unités explicites** partout où il y a une grandeur physiologique.
- **Cas limites et hors-scope obligatoires** — une spec sans eux est incomplète.
- Ne jamais présumer une structure de données externe non vérifiée.
- **Aucune référence au code** : jamais de chemin de fichier, nom de
  fonction/module, ou section de notebook dans le spec — même si le comportement
  existe déjà quelque part, il se décrit en termes fonctionnels/observables, jamais
  par une citation du code qui l'implémente.
