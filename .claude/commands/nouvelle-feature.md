---
description: Démarre le cycle complet d'une nouvelle feature (cadrage Q&A → spec → plan → implémentation → rappel de revue)
argument-hint: <description du sujet en 1-2 phrases>
---

Nouvelle feature : $ARGUMENTS

Suis ce cycle dans l'ordre, sans sauter d'étape ni les fusionner.

## 1. Cadrage par Q&A

Applique le skill `redaction-spec` : reformule le besoin en 1–2 phrases pour valider la
compréhension, puis pose explicitement toutes les questions de clarification
nécessaires **avant** d'écrire quoi que ce soit (périmètre, cas limites, ce qui est
hors scope). Itère jusqu'à épuisement des questions bloquantes.

## 2. Rédaction du spec

Détermine le numéro de la feature (dernier dossier `specs/<N>-.../` existant + 1,
zero-paddé sur 3 chiffres) et crée `specs/<N>-<nom-court-feature>/spec.md` suivant le
gabarit du skill `redaction-spec`. Le spec décrit le **quoi**, jamais le **comment**.

**Arrête-toi ici et attends la validation explicite du spec par l'utilisateur avant de
continuer** — ne pas enchaîner sur le plan sans confirmation.

## 3. Plan d'implémentation

Une fois le spec validé, applique le skill `redaction-plan`, en Plan Mode (discipline
Explore/Edit, cf. `AGENTS.md`) : explore le code réel pour vérifier toi-même les faits
nécessaires (jamais deviner, jamais demander à l'utilisateur ce qui est vérifiable
dans le code), ne pose de question que sur de vraies décisions d'implémentation, puis
conçois l'approche. Une fois le plan approuvé par l'utilisateur, écris-le aussi dans
`specs/<N>-<nom-court-feature>/plan.md` suivant le gabarit du skill — artefact
durable, pas seulement l'approbation interactive — avant de commencer à coder.

## 4. Implémentation

Implémente en petits diffs, un changement = une intention, en suivant le plan validé.
Teste après chaque changement significatif plutôt qu'en un seul gros diff.

## 5. Fin de cycle

Une fois l'implémentation terminée et testée, rappelle explicitement à l'utilisateur de
lancer `/code-review` avant de considérer la feature terminée — ne le lance jamais
automatiquement, laisse l'utilisateur choisir le moment (ex. après avoir testé
manuellement sur des données réelles).
