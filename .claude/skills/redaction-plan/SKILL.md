---
name: redaction-plan
description: >
  Concevoir le plan d'implémentation (le COMMENT) d'une feature déjà spécifiée.
  Utiliser après validation du spec, en Plan Mode (lecture seule), avant d'écrire du code.
---

# Rédaction du plan (Plan Mode — lecture seule)

Le plan décrit **comment** implémenter le spec. Aucun code écrit à ce stade.
But : un plan **ancré dans le code réel**, pas dans des hypothèses.

## Méthode

1. **Explorer d'abord.** Lire le code concerné pour répondre soi-même aux questions
   **factuelles** (emplacement d'un fichier, signature d'une fonction, schéma d'une
   table, ce que retourne/réutilise l'existant). **Chercher, ne pas deviner — ni
   demander ce que le code contient.**
2. **Vérifier ce dont dépend le plan.** Tout point non confirmé est marqué `(à vérifier)`
   et levé **avant** de figer le plan (règle « non-présomption », cf. `AGENTS.md`).
3. **Réutiliser l'existant.** Identifier ce qui existe déjà ; ne pas réinventer.
4. **Ne demander que les *décisions*, jamais les *faits*.** Si un choix t'appartient
   (deux emplacements, deux approches), **proposer une option argumentée** et demander.
5. **Écrire le plan** dans `specs/<N>-<feature>/plan.md`, selon `templates/plan-template.md`.

## Règles d'or

- **Le COMMENT, pas le code.**
- **Petits diffs** : découper en étapes, 1 intention = 1 diff.
- **Plan de tests ciblé** sur le code sensible.
- Le plan est un **artefact durable**, pas seulement une approbation en fil.
