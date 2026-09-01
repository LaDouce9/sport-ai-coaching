# Bonnes pratiques — développement assisté par IA

**« Vibe engineering »** : une méthodologie éprouvée par la pratique, générale et
transférable. Générer vite avec l'IA, vérifier avec la rigueur d'ingénierie avant de
livrer.

`Agent de référence : Junie` · `Document vivant` · `Socle des supports de formation`

> **STATUT DU DOCUMENT**
>
> Document de référence personnel et vivant. Il n'est pas destiné à être distribué tel
> quel aux équipes : il sert de socle de connaissance pour produire ensuite des
> supports de formation ciblés. On y garde volontairement la profondeur, les nuances et
> les hypothèses non tranchées — à condition qu'elles soient balisées (voir
> conventions).

## Note de lecture & conventions

**Cadre général d'abord.** Le corps du document décrit ce qui fonctionne quel que soit
l'agent de codage. Les spécificités d'un outil (commande, fichier, mécanisme
propriétaire) sont isolées dans des encarts, jamais fondues dans le texte.

**Agent de référence : Junie (JetBrains)** — l'agent que les équipes utiliseront. Les
mécanismes propres à d'autres outils (notamment Claude Code) sont signalés comme tels,
pour ne pas les prendre pour des pratiques universelles. Les exemples de code sont en
Python par lisibilité ; tout se transpose à PHP.

**Deux mots de vocabulaire :** un **artefact** est un fichier durable produit et
réutilisé dans le flux (spec, plan, `AGENTS.md`, tests, doc) ; `AGENTS.md` désigne le
fichier de directives du projet (§1.1), un standard réellement lu par plusieurs agents.

**Les encarts, utilisés partout :**

> **▶ CÔTÉ JUNIE**
>
> Comment la pratique se décline avec l'agent de référence.

> **⚙ SPÉCIFIQUE CLAUDE CODE**
>
> Mécanisme propre à Claude Code — à transposer, pas à recopier.

> **⚠ À VÉRIFIER / RÉSERVE**
>
> Affirmation plausible mais non confirmée, ou détail qui a pu évoluer.

> **🔒 SÉCURITÉ**
>
> Point de vigilance sécurité ou confidentialité.

> **📎 Ancrage projet (sport-coaching-ai)**
>
> Le journal de bord de ce projet (incidents datés, fiche des pratiques
> appliquées/écartées) vit séparément dans [`docs/JOURNAL.md`](JOURNAL.md), pas dans ce
> document — cf. §0 : « une pratique observée qui ne généralise pas en bonne pratique
> reste dans le journal du projet, pas ici ».

---

# PARTIE 0 — Cadre et principes

## 0.1 — « Vibe coding » vs développement assisté

Le « vibe coding », c'est décrire son intention en langage naturel et laisser l'IA
générer le code. La nuance qui change tout : *si vous relisez, testez et savez
expliquer le code produit, ce n'est plus du « vibe coding », c'est du développement
assisté*. L'IA tape vite ; l'ingénieur reste responsable de l'intention et de la
vérification.

La règle d'or tient en deux mots : **« Vibe & Verify »**. Générer vite avec l'IA,
vérifier avec la rigueur d'ingénierie (revue, tests, analyse statique) avant de livrer.
Le cycle de base : **décrire l'intention → l'IA génère → vérifier & itérer** (lire le
diff, tester, corriger, recommencer).

## 0.2 — Pourquoi un cadre est nécessaire

La vitesse est réelle, mais sans garde-fous elle se paie en dette technique et en
failles de sécurité : une part significative du code généré sans vérification contient
des vulnérabilités, et la sur-confiance (« Accept All » sans relire) augmente le taux
de défauts — sur les tâches complexes, des développeurs expérimentés peuvent même
*perdre* du temps s'ils délèguent sans méthode.

> **⚠ À VÉRIFIER / RÉSERVE**
>
> Les chiffres précis qui circulent (pourcentages de vulnérabilités, gains/pertes de
> vitesse) viennent de sources hétérogènes et datées. À resourcer avant de les citer.
> Le *sens* (vitesse réelle mais dette/sécurité sans vérification) est solide ; les
> nombres exacts, non.

À retenir : la bonne pratique est hybride — l'IA pour générer vite, l'ingénierie
(revue, tests, sécurité) pour livrer sûr.

## 0.3 — Le modèle des 4 cadences

Plutôt qu'une suite d'étapes numérotées, on raisonne par **cadence** — à quelle
fréquence et à quelle portée chaque pratique intervient. Une bonne partie n'est **pas**
séquentielle.

| Cadence | Fréquence / portée | Ce qu'on y trouve | Partie |
|---|---|---|---|
| Socle projet | Une fois par projet, évolue lentement | `AGENTS.md`, spec, skills, permissions, arborescence | 1 |
| Boucle par feature | Répétée à chaque unité de travail | Cadrage → spec → plan → implémentation → revue | 2 |
| Disciplines transversales | Toujours actives | Bien prompter, hygiène tokens, pilotage de l'effort, sécurité | 3–5, A |
| Passage à l'échelle | Quand la pratique est mûre | Parallélisation (worktrees) | 6 |

« Faut-il faire le spec avant `AGENTS.md` ? » est un faux problème de séquence.
`AGENTS.md` est un artefact *projet* persistant qui préexiste au travail ; le spec est
*par feature*, recréé à chaque cycle. L'ordre réel : **un `AGENTS.md` minimal d'abord,
puis pour chaque feature un spec**, `AGENTS.md` se densifiant au fil des corrections.
Le seul vrai séquencement du document est la **boucle par feature** (Partie 2).

---

# PARTIE 1 — Le socle projet (les artefacts de contexte)

Le socle donne à l'agent le *contexte stable* du projet. On le pose tôt, en version
minimale, et on le laisse grandir par sédimentation. Principe : **on ne pré-écrit pas
toutes les règles hypothétiques ; on ajoute ce que l'expérience a montré nécessaire.**

> **📎 VOCABULAIRE**
>
> Le fichier de directives central est appelé fichier de directives, harnais,
> constitution, guidelines… Ici on l'appelle `AGENTS.md`. On réserve le mot « socle »
> (ou « harnais ») à l'*ensemble* de la couche de contexte — `AGENTS.md` + docs
> référencées + skills/règles + permissions.

## 1.1 — `AGENTS.md` : la « constitution » du projet

Le fichier que l'agent lit en priorité : description, stack, gestionnaire de paquets,
commandes de test/lint, conventions, interdits. C'est un **standard de fichier ouvert,
lu par plusieurs agents**.

| Outil | Fichier de directives | Portée |
|---|---|---|
| Junie | `.junie/AGENTS.md` ou `AGENTS.md` racine ; `.junie/guidelines.md` = legacy | Projet + `~/.junie/AGENTS.md` global |
| Claude Code | `CLAUDE.md` (importe `AGENTS.md` via `@AGENTS.md`) | Projet + global `~/.claude/` |
| Standard | `AGENTS.md` | Projet — lisible par de nombreux agents |

> **▶ CÔTÉ JUNIE**
>
> Junie lit `AGENTS.md` nativement. Emplacement primaire `.junie/AGENTS.md`, mais un
> `AGENTS.md` racine fonctionne aussi (combiné le cas échéant à `.junie/playbook.md`
> et aux règles `.junie/rules/*.md`). Le format `.junie/guidelines.md` est *legacy*.
> Il existe un `~/.junie/AGENTS.md` global.

> **⚙ SPÉCIFIQUE CLAUDE CODE**
>
> Claude Code lit `CLAUDE.md` et ne lit pas `AGENTS.md` par défaut ; le pattern est de
> garder un `AGENTS.md` canonique et de l'importer depuis `CLAUDE.md` (`@AGENTS.md`) —
> le repo reste compréhensible par n'importe quel agent.

Deux règles de discipline : (1) **commencer minimal** (contexte, commandes, 2–3
conventions clés) ; (2) **ajouter une règle seulement après répétition** — quand on a
dû corriger la même chose deux fois (exception : un incident grave justifie une règle
dès la première fois).

```
# AGENTS.md — MaListe
## Contexte
Appli web de listes de tâches. Python (FastAPI) + SQLite. Une seule page, pas de comptes.
## Commandes
Lancer : make dev · Tests : make test · Lint : make lint
## Règles
Dates : toujours en ISO 8601, jamais de format local en base.
Un test par nouvelle fonction dans src/services/.
## Ne pas faire
Ne pas ajouter de librairie sans demander.
Ne pas toucher à src/legacy/ (gelé).
```

**Divulgation progressive.** Une règle trop spécifique à un sous-domaine ne va **pas**
dans `AGENTS.md` : elle part dans un fichier dédié (`docs/PARSING.md`) référencé depuis
`AGENTS.md`.

> **▶ CÔTÉ JUNIE**
>
> La divulgation progressive se fait en éclatant les règles dans plusieurs
> `.junie/rules/*.md` (il n'y a **pas** de syntaxe d'import `@fichier` comme chez
> Claude Code).

> **⚠ UN DOC RÉFÉRENCÉ N'EST PAS UN « SKILL »**
>
> Même objectif (ne pas tout charger), déclenchement différent : un doc référencé est
> chargé parce qu'un fichier le *pointe* ; un skill (§1.3) est chargé parce que l'agent
> *décide* de le charger d'après sa `description`. Le doc référencé = divulgation
> progressive *manuelle* ; le skill = version *automatique*.

## 1.2 — Le spec : contrat fonctionnel d'une unité de travail

Un spec décrit **ce que** le système doit faire pour *une* feature : comportement,
données et unités, cas limites, et ce qui est **hors scope**. Jamais le détail
d'implémentation — celui-ci relève d'un *plan* séparé (le *comment*).

**Trois principes** (spec-driven ; outillage de référence : *spec-kit*, Annexe C) :

1. **Un spec par feature**, pas un spec unique pour tout le produit (sinon il perd
   l'avantage : rester assez léger pour tenir dans le contexte).
2. **Séparer le spec (le quoi) du plan (le comment)** — deux artefacts, deux
   granularités.
3. **Un dossier numéroté par feature** (`specs/<N>-<nom-feature>/spec.md`). Le travail
   en cours vit dans le dossier le plus récent ; les specs terminées restent
   archivées, pas supprimées.

```
# spec — Export CSV des congés d'un collaborateur
## Objectif
Exposer un endpoint qui exporte les congés d'un collaborateur au format CSV.
## Comportement
GET /exports/conges/{id} → CSV (UTF-8, séparateur ';'), colonnes : date, type, statut.
Droits : le collaborateur concerné + le rôle RH. Pagination : 1000 lignes max.
## Cas limites
- Droits refusés → 403. - Aucun congé → CSV en-têtes seules. - Caractères spéciaux échappés.
## Hors scope
Pas d'export multi-collaborateurs. Pas de format Excel natif.
```

> **💡 IDÉE : UN SKILL « RÉDACTION DE SPEC »**
>
> Le gabarit de spec de l'équipe est un candidat idéal à un skill (§1.3). Encore
> mieux : un skill « spec en inspecteur » qui *challenge* les hypothèses et pose des
> questions avant de rédiger (prolongement du cadrage Q&A, §2.1).

## 1.3 — Les connaissances réutilisables (Agent Skills)

Un **Skill** encapsule une connaissance/convention réutilisable que l'agent charge *à
la demande*. Mécanisme : un `SKILL.md` (en-tête `name` + `description`, puis corps).
**Seuls `name` et `description` sont chargés en permanence** ; le corps est chargé si
l'agent juge la tâche pertinente. La `description` joue un rôle de **règle de
routage** — d'où l'importance de la soigner.

**Un skill est un dossier, pas qu'un fichier.** Autour du `SKILL.md`, il peut embarquer
des **fichiers de référence** (chargés à la demande), des **scripts exécutables** et
des **gabarits / checklists** — le `SKILL.md` les pointe, et l'agent ne les lit (ou ne
les exécute) que si la tâche le justifie. C'est une seconde divulgation progressive, à
l'intérieur du skill : le `SKILL.md` reste léger, une doc massive ne coûte des tokens
que quand elle sert.

```
skills/mon-skill/
├─ SKILL.md      # obligatoire — name + description + corps (qui pointe les fichiers)
├─ scripts/      # helpers exécutables (ex. check.sh), lancés par l'agent
├─ templates/    # gabarits / assets
└─ checklists/   # matière de référence chargée au besoin (ex. review.md)
```

> **⚙ SPÉCIFIQUE CLAUDE CODE**
>
> « Agent Skills » (`SKILL.md`, dossiers `~/.claude/skills/` ou `.claude/skills/`). Un
> Skill est **indépendant de MCP** : aucun serveur requis.

> **▶ CÔTÉ JUNIE**
>
> Structure identique, confirmée en plugin ET en CLI (doc officielle JetBrains). Un
> skill est un dossier `.junie/skills/<nom>/` avec `SKILL.md` obligatoire, plus
> `scripts/` (que Junie **exécute**), `templates/` et `checklists/`. Divulgation
> progressive native : seuls `name` et `description` sont connus tant que la tâche ne
> rend pas le skill pertinent. Côté CLI, `skill-locations` ajoute des emplacements et
> les fonctions avancées (`/skills`, `$nom`) sont surtout CLI.

> **🔒 SÉCURITÉ**
>
> Un skill qui embarque un script s'exécute avec les droits de l'agent → il repasse
> par les permissions / l'Action Allowlist (§5.1). Un skill avec script est donc du
> **code exécutable** : à traiter comme une dépendance (source de confiance, revue).

**Cartographie des typologies de skills :**

| Typologie | But | Exemples |
|---|---|---|
| Production de code | Uniformiser le code écrit | modularité + docstrings ; style/lint maison ; gestion d'erreurs |
| Artefacts de process | Standardiser les livrables | spec « en inspecteur » ; plan ; découpage en tâches |
| Qualité & tests | Fiabiliser | plan de tests piloté par la couverture ; TDD ; correction de tests |
| Revue & sécurité | Filet de sortie | revue de code ; revue sécurité/RGPD ; anti-patterns |
| Documentation | Expliquer / tracer | doc de module ; docstrings ; changelog |
| Git & livraison | Discipliner la livraison | message de commit ; titre/description de PR ; branches |
| Domaine métier | Encapsuler le métier | règles métier ; databook ; glossaire |
| Brownfield | Rendre l'implicite explicite | extraction de conventions ; caractérisation ; carte de dépendances |

## 1.4 — Récapitulatif du socle

| Artefact | Rôle | Junie | Claude Code | Chargement |
|---|---|---|---|---|
| `AGENTS.md` | Constitution du projet | `.junie/AGENTS.md` ou racine | `CLAUDE.md` (+`@AGENTS.md`) | Toujours |
| Spec | Contrat fonctionnel par feature | `specs/<N>-.../spec.md` | idem | À l'ouverture de la feature |
| Doc / règle spécialisée | Détail d'un sous-domaine | `.junie/rules/*.md` | fichier référencé (@) | Sur référence |
| Skill | Convention réutilisable auto-routée | `skill-locations` (CLI) | `SKILL.md` | À la demande |

## 1.5 — Arborescence de repo proposée

**Version générale** (standard `AGENTS.md`, agent-agnostique) :

```
mon-projet/
├─ AGENTS.md          # fichier de directives racine (standard inter-outils)
├─ .aiignore          # fichiers interdits à l'agent (secrets, /vendor…)
├─ .env               # secrets — NON commité (.gitignore)
├─ docs/
│  ├─ ARCHITECTURE.md # carte du code (économise des tokens)
│  ├─ DATABOOK.md     # schéma de base annoté (clé en brownfield)
│  └─ <sous-domaine>.md # docs spécialisées → divulgation progressive
├─ specs/
│  ├─ 001-<feature>/  # spec.md · plan.md · tasks.md
│  └─ 002-<feature>/ …
├─ src/ …
└─ tests/ …
```

**Version Junie** (ce qui change) :

```
mon-projet/
├─ AGENTS.md              # (ou .junie/AGENTS.md) emplacement primaire lu par Junie
├─ .junie/
│  ├─ rules/              # divulgation progressive : règles éclatées
│  │  ├─ style.md · redaction-spec.md · brownfield.md
│  ├─ config.json         # settings CLI partagés (model, effort, brave, hooks)
│  └─ guidelines.md       # (legacy, seulement si existant)
├─ .aiignore              # ≈ « deny » d'accès fichiers (secrets)
├─ mcp.json               # serveurs MCP
├─ specs/… · docs/…       # conventions indépendantes de l'outil (identiques)
└─ (hors repo) ~/.junie/allowlist.json  # règles allow/ask par type d'action
```

Les dossiers `specs/` et `docs/` sont des conventions posées *au-dessus* de l'outil :
identiques dans les deux cas.

---

# PARTIE 2 — La boucle par feature

Le cœur séquentiel. Pour *chaque* unité de travail, on déroule une boucle à **deux
régimes** : neuf (greenfield) ou modification d'existant (brownfield) — même exigence
de vérification, chemins opposés.

## 2.1 — Le point de départ commun : le cadrage par Q&A

Avant d'écrire le moindre spec, on ne part pas d'une intention déjà figée. On donne le
besoin en une ou deux phrases, puis on demande **explicitement à l'IA de poser ses
questions de clarification**. Un humain qui rédige seul laisse des angles morts
implicites que l'IA ne peut pas deviner ; la forcer à interroger les fait remonter
*avant* qu'ils ne coûtent des itérations.

Déroulé : besoin en 1–2 phrases → *« Avant de rédiger le spec, pose-moi toutes les
questions pour lever les ambiguïtés »* → on répond, on itère jusqu'à épuisement des
questions bloquantes → seulement alors, le spec.

## 2.2 — Régime greenfield (nouvelle feature) — « spec-driven »

On part d'une spec claire et de garde-fous ; l'IA agit comme un **exécutant rapide sans
marge d'interprétation**. Idéal pour le boilerplate, l'UI, les modules bien cadrés. Le
flux : **Specify** (le quoi) → **Plan** (le comment, discipline Explore/Edit §2.5) →
**Tasks** (découpage) → **Implement** (petits diffs).

**TDD ciblé, pas dogmatique.** Écrire le test *avant* le code, mais **uniquement là où
une erreur silencieuse coûterait cher** : calculs métier sensibles, parsing de formats
externes, règles de droits. Pas de dogmatisme sur l'UI ou la plomberie.

**Variante — le test-first piloté par la couverture :** (1) concevoir d'abord le **plan
de tests** sous forme de tableau (cas nominal, limites, erreurs…), visant une cible
(~90 %), *sans* écrire le code — un artefact que l'humain valide ; (2) puis générer les
tests en cohérence. *90 % est une cible, pas un dogme* : la couverture mesure ce qui
est *exécuté*, pas *vérifié*.

> **⚠ UN TEST VERT NE GARANTIT PAS UN RÉSULTAT CORRECT**
>
> Pour tout code produisant une sortie visuelle ou un résumé (graphique, rapport,
> dashboard), un test peut valider que la fonction ne plante pas sans révéler un
> résultat absurde. Regarder le rendu final fait partie de la vérification. C'est le
> piège « **AI test theater** » : des tests verts qui ne vérifient rien de réel.

## 2.3 — Régime brownfield (modifier du legacy) — « comprendre d'abord »

Le régime le plus exigeant, et le plus fréquent sur une base ancienne. **Presque tout y
est inversé** par rapport au greenfield.

**La « Convention Inversion ».** En greenfield, l'agent *propose* les conventions. En
brownfield, il doit **se soumettre à des conventions préexistantes, implicites et non
documentées** qu'il ne peut pas deviner. Livré à lui-même, il comble les vides avec ses
conventions « modernes » — et casse la cohérence du code ancien. **Toute la méthode
consiste à rendre explicite l'implicite *avant* de laisser l'IA écrire.**

Les risques spécifiques : l'agent (1) hallucine une convention moderne ; (2)
« améliore » du code qui avait une raison non évidente (*Chesterton's fence*) ; (3)
réécrit au lieu de patcher (effet « second système ») ; (4) travaille à l'aveugle sur
des dépendances hors contexte ; (5) modifie silencieusement une règle métier implicite ;
(6) se trompe sur le schéma de base → corruption de données.

Le « **dossier de reprise** » d'une zone legacy (pendant brownfield de la spec) — ciblé
sur la zone, jamais tout le legacy d'un coup :

1. **Cartographier la zone** — exploration en lecture seule : qui appelle ce code,
   qu'appelle-t-il, quelles données. Produire une carte de dépendances.
2. **Documenter l'existant** (IA rédige, humain valide contre le métier) — c'est là que
   l'IA excelle le plus.
3. **Extraire et expliciter les conventions implicites** → les écrire dans
   `AGENTS.md` / `.junie/rules/`. C'est l'acte qui renverse la Convention Inversion.
4. **Databook / schéma de base annoté** : tables, relations, sens métier des colonnes,
   valeurs magiques, dénormalisations. L'IA génère depuis le DDL, l'humain annote.
5. **Characterization tests / golden master AVANT tout changement.** Règle d'or :
   « pas de characterization tests → pas de refacto IA ».
6. **Contraintes de version explicites** dans `AGENTS.md` (ex. « PHP 5.6, pas de
   syntaxe PHP 8 »).
7. **Interdire toute nouvelle dépendance / pattern** sans validation.
8. **Chesterton's fence** : ne rien supprimer dont on ne comprend pas la raison.
9. **Micro-pas + strangler fig + rollback prêt** ; 1 changement = 1 intention ; **ne
   JAMAIS réécrire de zéro**.

> **💡 L'IDÉE-FORCE EN FORMATION**
>
> En brownfield, le gros du travail IA est **en amont** (cartographier, documenter,
> expliciter, poser le filet de tests) ; la génération de code ne vient qu'après, très
> encadrée. C'est l'inverse de l'intuition « l'IA va vite réécrire le vieux code ».

## 2.4 — Greenfield vs brownfield, en un tableau

| | Greenfield (neuf) | Brownfield (legacy) |
|---|---|---|
| Logique | Spec-driven : spécifier puis générer | Comprendre d'abord, puis modifier |
| Rôle de l'agent | Propose les conventions | Se soumet (Convention Inversion) |
| Point de départ | Spec claire + garde-fous | Dossier de reprise : carte + doc + conventions |
| Filet de test | Test-first sur modules sensibles | Characterization tests avant refacto |
| Où est l'effort IA | Sur la génération de code | En amont (comprendre, documenter, filet) |
| Progression | Petits diffs, une intention | Micro-pas, strangler fig, jamais de big-bang |
| Interdit clé | Générer sans definition of done | Réécrire de zéro (second système) |

## 2.5 — La discipline Explore/Edit (« Plan mode »)

Toute tâche touchant plusieurs fichiers passe par une **phase d'exploration en lecture
seule avant l'édition**. Le mécanisme fiable n'est pas une phrase de consigne mais une
**contrainte imposée par l'outil** : forcer le démarrage en lecture seule/plan. **Une
règle appliquée vaut mieux qu'une règle demandée.**

> **⚙ SPÉCIFIQUE CLAUDE CODE**
>
> On force ce comportement via `defaultMode: "plan"` dans `permissions` de
> `settings.json` : chaque session démarre en lecture seule, la sortie se fait par
> validation du plan.

> **▶ CÔTÉ JUNIE ⚠ (À TESTER)**
>
> Pas d'équivalent documenté d'un « mode plan forcé » par configuration. Le garde-fou
> apparenté est double : la séparation **Ask mode** (planifier, aucune édition) /
> **Code mode** (agent complet), et l'**Action Allowlist** qui, hors « brave mode »,
> exige une confirmation par défaut (voir §5.1).

| Outil | Mécanisme plan / édition |
|---|---|
| Junie | Séparation native Ask mode / Code mode ; le plan se valide avant exécution |
| Claude Code | Plan mode dans la même conversation ; forçable via `settings.json` |
| Cursor | Pas de bascule native ; explorer dans un thread, ouvrir un thread neuf nourri du plan |
| Google Antigravity | Fichiers de règles ; pas de mode plan/édition natif documenté |

La discipline symétrique, **côté sortie**, est la **revue de code** (§2.6) : le plan
réduit les erreurs de *conception* ; la revue attrape des bugs d'*exécution*.
Complémentaires, pas substituables.

## 2.6 — La revue de code (discipline de sortie)

Après un premier passage — idéalement sur données réelles — une revue dédiée attrape
des bugs que ni les tests ni le plan n'avaient exposés. Outillée (skill/commande) ou
manuelle, elle est **complémentaire**, jamais redondante.

> **RAPPEL TRANSVERSAL**
>
> « **1 PR = 1 intention** ». Petites tâches, petits diffs : une fonction, un fichier,
> une frontière à la fois. Jamais « Accept All » à l'aveugle ; commit + test après
> chaque changement. Le gros diff fourre-tout est une PR que personne ne comprend.

---

# PARTIE 3 — Piloter l'effort et les modèles

Toutes les tâches ne méritent pas le même « effort » de raisonnement. Les tâches de
**raisonnement** (architecture, cadrage) méritent un effort élevé ; les tâches
**mécaniques** (renommage, nettoyage) non. Deux réalités à ne pas confondre : le
**routage automatique** (l'outil choisit) et la **discipline manuelle** (vous
ajustez).

| Outil | Routage / sélection du modèle |
|---|---|
| Cursor | Routage automatique réel : un routeur classe chaque requête et choisit frontier vs économique |
| Junie | Partiellement automatique : auto-sélection + effort ajustable |
| Claude Code | Aucun routage auto : modèle/effort explicites ; un sous-agent peut recevoir un modèle différent |
| Google Antigravity | Manuel : sélection du modèle et du niveau d'effort (Low/Medium/High) |

> **⚙ SPÉCIFIQUE CLAUDE CODE**
>
> Commandes concrètes (`/model`, `/effort`, `--model`, `--effort`). Ce qui est
> portable, c'est le **principe** (« adapter l'effort à la tâche »), pas la commande.

> **▶ CÔTÉ JUNIE**
>
> Le modèle et l'effort se posent dans `config.json` (`model`, `effort`,
> `provider`/`byok`). L'auto-sélection couvre déjà une partie du « routage par effort ».

> **⚠ À VÉRIFIER / RÉSERVE**
>
> **Piste : modèle capable pour le plan, modèle léger pour l'exécution.** Séduisant,
> mais (1) le comportement d'un changement de modèle en cours de session n'est pas
> garanti, et (2) un modèle léger peut introduire des bugs subtils : **l'économie ne se
> substitue jamais à la vérification.**

---

# PARTIE 4 — Économie de tokens

Contre-intuitif mais central : **un contexte ciblé coûte moins cher ET produit un
meilleur code**. Quelques milliers de tokens *utiles* battent des dizaines de milliers
de tokens *vagues*.

## 4.1 — Pourquoi le contexte « lean » gagne sur les deux tableaux

Un contexte trop chargé **dilue l'attention** (le *context rot*), **noie les
directives** dans le bruit, et **coûte plus de tokens** à chaque tour (tout l'historique
est retraité). Réduire le contexte = gagner en coût *et* en qualité.

## 4.2 — Les leviers

| Levier | Principe |
|---|---|
| Hygiène de contexte | Conversation neuve en changeant de sujet ; compacter quand la limite approche |
| Contexte ciblé | Donner les 2–3 bons fichiers, pas tout le dépôt |
| Carte du code | Un `ARCHITECTURE.md` évite de lire 25 fichiers pour en comprendre 3 |
| Cache de prompt | Mettre le stable en premier (instructions, schémas) |
| Router les modèles | Léger pour le simple, gros pour le complexe |
| Plan puis exécution | Raisonner une fois en mode plan, exécuter ensuite |
| Batch / non interactif | Traitements en lot |
| Outils MCP sobres | Renvoyer des champs minimaux |

## 4.3 — Hygiène de contexte : mécanismes

> **⚙ SPÉCIFIQUE CLAUDE CODE**
>
> `/clear` (conversation neuve, garde la mémoire projet) en changeant de tâche ;
> `/compact` (compresse l'historique) quand la limite approche ; `/btw` (question
> annexe hors historique).

> **▶ CÔTÉ JUNIE**
>
> Réflexe équivalent : ouvrir une **nouvelle conversation/tâche** en changeant de sujet
> plutôt que d'accumuler un fil interminable (le 10ᵉ message coûte ~10× le premier).
> ⚠ Un équivalent « compact » côté Junie est à confirmer.

---

# PARTIE 5 — Sécurité et garde-fous proportionnés

Principe : une sécurité **proportionnée au risque réel**, appliquée par des
**mécanismes** (pas seulement des recommandations dans un fichier).

## 5.1 — Secrets et permissions

Les secrets (jetons, clés d'API) vivent dans un fichier non commité (type `.env`),
jamais lus ni affichés par l'agent. Cette interdiction doit être **appliquée**, pas
seulement recommandée.

> **⚙ SPÉCIFIQUE CLAUDE CODE**
>
> Section `permissions` de `settings.json` avec `allow` / `ask` / `deny` : lecture et
> tests pré-approuvés (`allow`) ; actions modifiant les dépendances en confirmation
> (`ask`) ; lecture des secrets et commandes destructrices en refus (`deny`). Extrait
> en Annexe B.5.

> **▶ CÔTÉ JUNIE ⚠ (À TESTER)**
>
> Correspondance partielle via l'**Action Allowlist**. Côté CLI : `~/.junie/config.json`
> et `.junie/config.json` (réglages), et `~/.junie/allowlist.json` (règles par type
> d'action : `fileEditing`, `executables`, `mcpTools`, `readOutsideProject`,
> `readSecretFile`) avec niveaux `allow`/`ask`. Côté IDE : allowlist en UI ;
> `.aiignore` bloque l'accès à des fichiers.

| Claude Code | Junie CLI | Junie IDE |
|---|---|---|
| `allow` | `allow` | règle « auto-approve » |
| `ask` | `ask` (défaut hors brave) | confirmation par défaut |
| `deny` | pas de `deny` natif — approximé par `readSecretFile: ask`, `.aiignore` | `.aiignore` (fichiers) |
| `defaultMode: plan` | pas d'équivalent documenté | pas d'équivalent documenté |
| `hooks` | champ `hooks` de `config.json` | — |

> **🔒 POINT CLÉ POUR LA FORMATION**
>
> Junie n'a pas de liste `deny` native. La protection des secrets passe par
> `.aiignore` (et/ou `readSecretFile: ask`), pas par un refus de lecture ; le « jamais
> ça » se reconstitue par des allowlists restrictives + les protections de branche/CI.

## 5.2 — Hooks (automatisation événementielle)

Les **hooks** décident **ce qui se passe automatiquement autour** d'une action
(reformater après édition, lancer les tests, bloquer une commande par un pattern).
Deux règles : ne pas dupliquer un outillage existant juste pour avoir un hook ; écrire
les diagnostics sur `stderr` pour que l'agent voie *pourquoi* une action a été bloquée.

> **🔒 LIMITE IMPORTANTE (TOUS OUTILS)**
>
> Ces garde-fous locaux sont une discipline de *confort en session*. Ils ne
> remplacent **pas** la CI, la protection de branche ou les contrôles
> d'infrastructure — la couche d'application qui fait foi.

## 5.3 — Confiance dans le contenu externe (injection de prompt indirecte)

Dès qu'un agent lit un contenu **qu'il n'a pas produit** — réponse d'API, page web,
sortie d'un serveur MCP tiers — il doit être traité comme **non fiable par défaut**,
comme une entrée utilisateur non validée.

> **🔒 LE « LETHAL TRIFECTA »**
>
> Le risque (décrit par Simon Willison) apparaît quand trois conditions se
> combinent : accès à des **données privées** + exposition à du **contenu non
> fiable** + capacité à **communiquer vers l'extérieur**. Un serveur MCP tiers se
> scrute avec la même rigueur qu'une dépendance externe.

## 5.4 — Revue humaine sur le sensible

Sur l'authentification, le paiement, les données personnelles (RGPD), le chiffrement :
**expertise humaine obligatoire**, jamais d'écriture automatique. C'est le miroir
sécurité de la revue de code (§2.6).

## 5.5 — Les pièges à garder en tête

- **Sécurité en angle mort** — secrets en clair, clés exposées, injections.
- **« AI test theater »** — des tests verts qui ne vérifient rien (§2.2).
- **Dette & archi emmêlée** — plusieurs libs pour la même tâche, styles incohérents,
  code plausible mais faux.
- **Sur-confiance** — « Accept All » sans relire ; on perd la capacité à déboguer son
  propre code.
- **Le big-bang** — tout nettoyer en un gros diff.
- **L'agent sans garde-fou** — un agent qui ignore un « code freeze » ou touche à la
  prod.

---

# PARTIE 6 — Passage à l'échelle : parallélisation

Au-delà d'une tâche à la fois : les *git worktrees* permettent de checkouter plusieurs
branches du même dépôt dans des dossiers séparés, chacun avec sa session d'agent, sans
se marcher dessus.

**Le vrai piège n'est pas technique, il est organisationnel.** Des agents parallèles
qui éditent la même zone ou partent d'hypothèses incompatibles cassent le dépôt aussi
vite qu'ils accélèrent. Ça ne marche que si **chaque tâche est scopée et indépendante
avant** de lancer le parallélisme (un spec par feature, une tâche par worktree), avec
tests et vérifications avant fusion.

**Au-delà d'un certain nombre de worktrees, le goulot devient la revue humaine, pas
l'agent.** C'est la vraie limite d'échelle : la vérification humaine reste le facteur
limitant.

> **▶ CÔTÉ JUNIE**
>
> La parallélisation par worktrees est une pratique **niveau git**, indépendante de
> l'agent : plusieurs checkouts, une session Junie par dossier.

> **⚠ À VÉRIFIER / RÉSERVE**
>
> Les ordres de grandeur (« 4–8 worktrees par développeur ») sont des retours d'usage
> rapportés, pas une mesure.

---

# ANNEXE A — Bien prompter (discipline transversale)

*En annexe car elle fait l'objet d'un support dédié. Rappel des principes qui
traversent tout le document.*

## A.1 — La règle d'or : être clair et précis

Un prompt ambigu produit une réponse ambiguë. Donner détails et contexte : « Qui était
président du Mexique en 2021 ? » plutôt que « Qui était président ? ».

## A.2 — Construire un prompt : combiner des briques

Un prompt structuré combine : **Rôle · Contexte · Objectif · Résultat attendu ·
Contrainte · Format**. Les **délimiteurs** encadrent les données (`<email>` …
`</email>`) pour que le modèle ne confonde pas consigne et contenu. Préférer **les
instructions aux contraintes** (« Sois clair » plutôt que « Ne sois pas ambigu »).

## A.3 — Principes spécifiques au développement assisté

- **Contexte avant tâche** — dire *pourquoi* avant *quoi*.
- **Expliciter les non-objectifs** — « Pas besoin de gérer le multi-utilisateur ici ».
- **Un niveau de granularité à la fois** — ne pas mélanger cadrage et implémentation.
- **Séparer lecture et écriture** — « explique-moi » vs « modifie » jamais ambigus.
- **Donner le critère de succès** (definition of done) — sans lui, sur-ingénierie ou
  sous-livraison.
- **Corriger tout de suite**, pas trois tours plus tard.
- **Éviter le vague évaluatif** (« améliore ça ») : préciser la dimension (lisibilité,
  perf, sécurité).
- **Donner le périmètre** (« ne touche pas au module X »).

## A.4 — Techniques avancées (rappel)

- **Zero-shot** — aucune démonstration.
- **One-shot / few-shot** — un ou plusieurs exemples pour suggérer un pattern.
- **Step-back** — considérer d'abord une question générale, puis la tâche spécifique.
- **Chain-of-Thought (CoT)** — demander des étapes de raisonnement intermédiaires.

---

# ANNEXE B — Bibliothèque d'exemples complets

*Exemples génériques illustrant le format attendu — à adapter, pas à recopier tels
quels.*

## B.1 — `AGENTS.md` complet

```
# AGENTS.md — MaListe
## Contexte
Appli web de listes de tâches. Python 3.12 (FastAPI) + SQLite.
Une seule page, pas de comptes utilisateurs pour l'instant.
## Commandes
Lancer : make dev · Tests : make test · Lint : make lint
## Règles
Fonctions courtes, typées. Pas d'état global.
Dates : toujours ISO 8601, jamais de format local en base.
Un test par nouvelle fonction dans src/services/.
Erreurs : lever des exceptions typées, jamais renvoyer None en cas d'échec.
## Ne pas faire
Ne pas ajouter de librairie sans demander.
Ne pas toucher à src/legacy/ (gelée). Ne pas lire ni afficher .env.
## Docs spécialisées (chargées à la demande)
Parsing des imports : voir docs/PARSING.md · Conventions d'API : voir docs/API.md
```

## B.2 — Skill complet (`SKILL.md`)

```
---
name: messages-de-commit
description: Format des messages de commit et titres de PR de l'équipe.
  Utiliser quand on rédige un commit, une pull request, ou une note de version.
---
# Messages de commit
## Format
`type(portée): description à l'impératif`
Types autorisés : feat, fix, docs, refactor, test, chore
## Exemples
✓ feat(taches): ajouter le filtre par date
✗ update — trop vague     ✗ « J'ai corrigé le bug » — pas à l'impératif
## Règles
- Titre : 72 caractères max, pas de point final.
- Si le commit corrige un ticket, ajouter Refs #123 en pied.
- Un commit = un changement logique.
```

## B.3 — Spec complet

```
# spec — Export CSV des congés d'un collaborateur
## Objectif
Permettre à un collaborateur (et au rôle RH) d'exporter ses congés au format CSV.
## Comportement attendu
Endpoint : GET /exports/conges/{id}     Sortie : CSV, UTF-8, séparateur ';'
Colonnes : date (ISO 8601), type, statut
Droits   : le collaborateur {id} lui-même OU un utilisateur du rôle RH
Volume   : pagination 1000 lignes par page
## Cas limites
- Appelant non autorisé → 403
- Collaborateur sans aucun congé → CSV avec la ligne d'en-têtes seule
- Valeurs contenant ';' ou saut de ligne → échappement CSV correct
- {id} inexistant → 404
## Hors scope
- Export multi-collaborateurs - Format Excel natif (.xlsx) - Filtres par période
```

## B.4 — Plan de tests piloté par la couverture (gabarit tableau)

Étape 1 de la variante §2.2 : produire ce tableau AVANT d'écrire les tests, puis le
valider.

| # | Cas | Type | Entrée | Sortie attendue | Priorité |
|---|---|---|---|---|---|
| 1 | Nominal | fonctionnel | congés valides | CSV complet, colonnes correctes | haute |
| 2 | Droits refusés | sécurité | appelant tiers | 403 | haute |
| 3 | Sans congé | limite | id valide, 0 congé | CSV en-têtes seules | moyenne |
| 4 | Caractères spéciaux | robustesse | valeur avec `;` | champ échappé | moyenne |
| 5 | Id inexistant | erreur | id inconnu | 404 | moyenne |

## B.5 — Extrait de permissions (Claude Code)

> **⚙ SPÉCIFIQUE CLAUDE CODE**
>
> Illustre le principe « la restriction est appliquée par un mécanisme ». À transposer
> conceptuellement pour Junie (§5.1), pas à recopier.

```jsonc
{
  "permissions": {
    "defaultMode": "plan",              // lecture seule par défaut au démarrage
    "allow": [
      "Read", "Glob", "Grep",
      "Bash(npm run test:*)", "Bash(npm run lint:*)",
      "Bash(git status)", "Bash(git diff:*)", "Bash(git log:*)"
    ],
    "ask": [ "Bash(git push:*)", "Bash(npm install:*)" ],
    "deny": [
      "Read(.env*)", "Read(secrets/**)",
      "Bash(rm -rf:*)", "Bash(git push --force:*)",
      "Bash(git reset --hard:*)", "Bash(curl:* | sh)"
    ]
  }
}
```

---

# ANNEXE C — Fiche outillage : spec-kit

**Ce que c'est.** Un outil en ligne de commande (CLI Python) publié par l'organisation
**GitHub officielle** (`github/spec-kit`), sous licence MIT, très adopté. Il outille la
méthode « spec-driven » : scaffolding, fichiers de workflow, intégration avec de
nombreux agents.

**Ce n'est pas** une extension d'IDE. On l'installe via `uv` / `uvx`, puis des
commandes comme `specify init` génèrent le flux `specify → plan → tasks → implement`.

**À retenir :** la convention `SPEC.md` (un spec par feature, dossiers numérotés,
séparation spec/plan) s'adopte **sans installer aucun outil**. spec-kit n'est qu'une
implémentation de référence qui automatise cette convention.

> **🔒 SÉCURITÉ**
>
> Cœur = dépôt officiel GitHub (confiance haute). Deux réserves : (1) c'est un CLI qui
> **exécute du code et télécharge des ressources** ; (2) le dépôt indique, pour ses
> presets communautaires, « Review source code before installation ». Donc : cœur
> officiel = OK ; presets tiers = à réviser. **Adopter la convention ne nécessite
> aucune installation.**

> **⚠ À VÉRIFIER / RÉSERVE**
>
> Noms exacts des commandes, arborescence et liste des agents compatibles (dont Junie)
> à revérifier sur le dépôt avant support.

---

# ANNEXE D — Glossaire

- **Artefact** — fichier durable produit et réutilisé dans le flux (spec, plan,
  `AGENTS.md`, tests, doc).
- **Vibe coding** — décrire une intention et laisser l'IA générer ; devient «
  développement assisté » dès qu'on relit, teste et sait expliquer.
- **Socle / harnais** — l'ensemble des artefacts de contexte stables (`AGENTS.md`,
  docs, skills, permissions).
- **`AGENTS.md`** — fichier de directives lu en priorité ; standard inter-outils.
- **Spec** — contrat fonctionnel d'*une* feature (le quoi), distinct du **plan** (le
  comment).
- **Skill** — connaissance/convention réutilisable chargée à la demande (`SKILL.md`),
  routée par sa `description`.
- **MCP** — protocole permettant à un agent de dialoguer avec des serveurs/outils
  externes. Indépendant des skills.
- **TDD** — écrire le test avant le code, puis coder juste ce qu'il faut pour le faire
  passer.
- **Plan mode / Explore-Edit** — phase d'exploration en lecture seule imposée avant
  l'édition.
- **Convention Inversion** — en brownfield, l'agent se soumet aux conventions
  existantes au lieu de proposer les siennes.
- **Characterization tests** — tests qui figent le comportement *actuel* d'un code
  legacy avant tout refacto.
- **Databook** — documentation annotée du schéma de base (tables, relations, sens
  métier, valeurs magiques).
- **Strangler fig** — migration progressive qui remplace l'ancien par du neuf sans
  big-bang.
- **Chesterton's fence** — ne pas retirer ce dont on ne comprend pas la raison d'être.
- **Context rot** — dilution de l'attention du modèle quand le contexte est trop
  chargé.
- **Lethal trifecta** — données privées + contenu non fiable + capacité
  d'exfiltration.
- **Worktree** — checkout d'une branche git dans un dossier séparé, pour paralléliser
  des sessions.
- **AI test theater** — des tests générés qui passent au vert sans rien vérifier de
  réel.
- **Brave mode (Junie)** — mode d'auto-approbation qui lève la confirmation des
  actions sensibles.

---

*Document de travail — à enrichir au fil de la pratique. Les encarts « À vérifier »
signalent ce qui doit être confirmé avant de nourrir un support de formation. Agent de
référence : Junie (JetBrains).*
