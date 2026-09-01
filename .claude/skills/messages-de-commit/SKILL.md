---
name: messages-de-commit
description: Format des messages de commit de ce projet. Utiliser quand on rédige un commit.
---

# Messages de commit

Convention calée sur les commits déjà écrits dans ce repo (`git log --oneline`), qui
suivent le style **Chris Beams** ("How to Write a Git Commit Message", la règle
50/72) — pas *Conventional Commits*. C'est un choix délibéré, pas un oubli : voir
« Pourquoi pas Conventional Commits » ci-dessous.

## Format

Sujet à l'**impératif**, **capitalisé**, **sans point final**. Cible ~50 caractères,
limite dure 72. **Pas de préfixe `type(scope):`**.

Si un corps est nécessaire : une ligne vide après le sujet, puis un corps qui explique
le **pourquoi** (le diff montre déjà le *quoi*), enveloppé à ~72 caractères.

## Exemples

Tirés tels quels de l'historique du projet :

✓ `Fix incremental-sync watermark data-loss bug found in code review`
✓ `Draft SPEC.md V1: Strava-only ingestion, manual sessions, body-zone load`
✓ `Document Explore/Edit ecosystem comparison and codify the rule`
✓ `Add reusable activity-analysis dashboard (Strava-app-style summary)`

✗ `Fix: install project as an editable package so python -m works outside pytest` —
seul commit du repo à utiliser un `:` après le type ; incohérent avec tous les autres,
à éviter.
✗ `update` — pas informatif, ne dit pas quoi ni pourquoi.
✗ `Fixed the bug.` — pas à l'impératif (« Fixed »), point final.

## Règles

- Un commit = un changement logique ; pas de commit fourre-tout.
- Impératif : « Add », « Fix », « Document », « Implement » — jamais « Added »,
  « Fixes », « Adding ».
- Pas de point final sur le sujet.
- Le corps (s'il existe) explique une décision ou un compromis non évident depuis le
  diff seul — pas une paraphrase du diff.

## Pourquoi pas Conventional Commits

*Conventional Commits* (`type(scope): description`) est un standard répandu, mais il
ne correspond pas à l'usage réel de ce projet : aucun des 12 commits existants n'utilise
ce préfixe. L'introduire maintenant casserait la cohérence de l'historique sans gain
réel ici (pas de changelog généré automatiquement, pas de semantic-release). Si ce
besoin apparaît plus tard, ce skill sera mis à jour en conséquence — pas avant.
