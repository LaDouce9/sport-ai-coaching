# Journal de bord — sport-coaching-ai

> Log projet-spécifique : pratiques essayées, incidents rencontrés, verdicts tirés du
> réel. Une pratique observée ici qui se généralise en bonne pratique transférable migre
> vers `docs/METHODOLOGIE.md` ; une pratique qui reste propre à ce projet reste ici. À
> tenir à jour au fil de l'eau, pas seulement au moment des incidents.

---

## 1. Fiche des pratiques

### 1.1 Pratiques appliquées dans ce projet

| Pratique | Source | Retour d'expérience |
|---|---|---|
| Prompting structuré (contexte, non-objectifs, granularité) | Ajout | *à compléter* |
| Cadrage par Q&A avant SPEC.md | Ajout | *à compléter* |
| SPEC.md comme contrat fonctionnel évolutif | Fiche initiale | *à compléter* |
| Harness (CLAUDE.md) construit progressivement, règles ajoutées après répétition | Fiche initiale (ajusté) | *à compléter* |
| Divulgation progressive (docs/ spécifiques référencés) | Fiche initiale | *à compléter* |
| TDD ciblé sur modules critiques uniquement | Fiche initiale (ajusté — pas dogmatique) | *à compléter* |
| Tests sur données réelles anonymisées en plus des mocks | Ajout | *à compléter* |
| Explore/Edit via Plan Mode | Fiche initiale | *à compléter* |
| Diffs petits et revuables | Ajout | *à compléter* |
| Suite de non-régression sur métriques calculées (valeurs de référence figées) | Ajout | *à compléter* |
| Routage par niveau d'effort (pragmatique, pas Spark) | Fiche initiale (simplifié) | *à compléter* |
| Secrets en `.env`, permissions Claude Code restreintes | Fiche initiale (simplifié) | *à compléter* |
| Graphify + Agent Skills via MCP (prise en main) | Fiche initiale + demande explicite | Installé en avance sur l'étape 7 (voir §2) — vérifié réel via web (package `graphifyy`, PyPI + GitHub, non fabriqué contrairement à d'autres éléments de la fiche source) |
| Journal de bord coût/bénéfice par pratique | Ajout | *à compléter* |
| AGENTS.md canonique + CLAUDE.md en import (`@AGENTS.md`) | Demande explicite | Claude Code ne lit pas AGENTS.md nativement (vérifié) ; le symlink/import est le pattern officiellement supporté — repo compréhensible par n'importe quel agent sans rien casser côté Claude Code |
| Règle explicite de non-présomption sur données externes (APIs Strava/Coros) dans AGENTS.md | Ajout, suite retour Gemini + incident réel | Ajoutée après un seul incident (schéma Strava halluciné, 25/08) au lieu des deux répétitions habituelles — dérogation assumée et documentée dans AGENTS.md, vu la gravité (pan fonctionnel manquant) ; *impact réel à confirmer au prochain Plan Mode touchant une API externe* |
| Revue de code après un premier passage sur données réelles (skill `/code-review`) | Ajout | A trouvé un vrai bug de correction (watermark de reprise incrémentale) que ni les tests unitaires ni le Plan Mode initial n'avaient attrapé — complémentaire, pas redondant avec ces deux disciplines |

### 1.2 Pratiques connues, non appliquées ici (bon à savoir)

| Pratique | Pourquoi elle existe | Pourquoi pas ici |
|---|---|---|
| Formats colonnaires Parquet/ORC + partitionnement | Nécessaire à très gros volume (data engineering) | Quelques centaines/milliers d'activités : un SQLite/Postgres suffit, plus simple à déboguer avec l'IA |
| NUMA-aware dual-socket, isolation façon CERN | Calcul HPC multi-tenant à très grande échelle | Projet solo, une seule charge de travail à la fois |
| Kueue (gestion de quotas Kubernetes) | Fair-sharing de ressources entre équipes/jobs | Pas de cluster, pas de contention de ressources à gérer |
| ContainerSSH + OIDC/OAuth2/Kerberos pour l'accès aux sessions | Accès sécurisé multi-utilisateurs à des environnements de calcul partagés | Un seul utilisateur, poste local : la protection `.env` + permissions Claude Code suffit |
| Chiffres de benchmark non sourcés (ex : "MAE de 22.7") | — | Chiffre sans unité ni source dans le document d'origine, vraisemblablement fabriqué — on définira nos propres seuils empiriquement |
| Budget strict de "150-200 instructions" pour CLAUDE.md | Éviter la dilution des règles | Le principe (rester concis) est valide, le chiffre précis est non vérifié — pas de règle numérique dure |
| Vision via AST / graphes de dépendance systématiques | Utile sur de très grosses bases de code | Base de code d'un mini-projet : à réévaluer si Graphify s'avère utile même à cette échelle (question ouverte, pas tranchée) |

*Cette section s'enrichit à chaque fois qu'on écarte une pratique en cours de route —
avec la raison, pas juste le constat.*

---

## 2. Journal de bord

*(rempli au fil des étapes avec : pratique observée, contexte, gain/coût constaté, verdict)*

### 2026-08-24 — Détour assumé : outillage avant cadrage

Installation de Graphify et bascule AGENTS.md/CLAUDE.md faites juste après la
configuration de base, donc avant le cadrage Q&A — en avance sur l'ordre habituel.
Décision explicite, pas un oubli :
- Repo quasi vide → risque faible de casser quoi que ce soit, terrain sûr pour prendre
  en main un nouvel outil.
- Objectif explicite de prise en main de Graphify, indépendant du calendrier du projet.
- Avant d'exécuter quoi que ce soit, vérification que les deux éléments cités par
  l'utilisateur étaient réels (et pas un nouvel avatar du problème de la fiche
  initiale) : Graphify existe et correspond à sa description (package `graphifyy` sur
  PyPI, dépôt GitHub actif) ; AGENTS.md n'est en revanche PAS lu nativement par Claude
  Code (vérifié par recherche web), d'où le choix du pattern import plutôt qu'un
  remplacement pur et simple.
- Point d'attention pour la suite : Graphify tourne sur un code encore vide — sa vraie
  valeur (graphe de dépendances utile) ne pourra être évaluée qu'une fois du code réel
  écrit.

### 2026-08-24 — Cadrage Q&A et rédaction du SPEC.md V1

L'utilisateur a fourni un document produit complet (4 modules : ingestion, sports sans
montre, coaching adaptatif, stratégie de course) en demandant explicitement de prioriser
plutôt que de tout spécifier. Bon test réel du cadrage par Q&A :

- Reformulation du périmètre réduit avant de poser des questions, pour valider la
  compréhension avant d'investir du temps dans le détail.
- Une des questions de cadrage (accès API Coros) a révélé un vrai risque technique non
  mentionné dans le document produit : l'API développeur officielle Coros nécessite une
  approbation "entreprise", inadaptée à un projet perso. Recherche web faite avant de
  trancher plutôt que de supposer — a permis de découvrir une alternative pertinente
  (serveur MCP Coros, self-service) et surtout un fait simplificateur décisif : Coros
  était déjà synchronisé vers Strava sur le compte réel de l'utilisateur, ce qui rend
  Strava seul suffisant pour le V1. **Sans cette vérification, le SPEC V1 aurait
  probablement embarqué une intégration Coros risquée dès le départ.**
- Gain concret : le périmètre V1 rédigé dans `SPEC.md` est net (ingestion Strava +
  module sans-montre + charge par zone, rien d'autre), alors que le document produit
  initial aurait naturellement tiré vers une spec beaucoup plus large.
- Le mapping "activité → zones corporelles par défaut" proposé par l'utilisateur pendant
  le Q&A a changé la conception du module de charge (poids par défaut + surcharge
  manuelle plutôt que saisie manuelle pure) — exemple concret où le cadrage a amélioré
  la conception, pas juste réduit le scope.

### 2026-08-25 — Schéma de données non vérifié en revue de plan

Premier passage réel en Plan Mode (ingestion Strava). Le sous-agent de planification a
produit un schéma SQLite complet (noms de colonnes, types) en le présentant avec
assurance, sans jamais consulter la vraie documentation Strava — alors même que le
`SPEC.md` demandait explicitement de vérifier ce point avant de le figer. L'utilisateur
a posé la question directement ("comment sais-tu le schéma de données ?"), à trois
reprises, avant que la vérification ne soit faite.

**Ce qui a marché :** la question a été posée en revue de plan, donc avant qu'une seule
ligne de code ne soit écrite — c'est précisément l'intérêt de la discipline Explore/Edit :
le coût de l'erreur était encore nul. Vérification faite après coup :
- L'objet "summary" (liste d'activités) et l'objet "detailed" (une activité) de l'API
  Strava n'exposent pas les mêmes champs — le schéma halluciné mélangeait les deux sans
  le savoir.
- Un endpoint entier (`/activities/{id}/streams`, séries temporelles FC/allure/altitude)
  était absent du plan — pas une erreur de détail, un pan fonctionnel manquant,
  directement lié à un besoin produit réel exprimé dès le document de cadrage initial
  (découplage aérobie, etc.) mais perdu en cours de route lors de la réduction du V1.
- Cette même vérification a aussi fait revenir sur le choix de bibliothèque
  (`requests` brut abandonné pour `stravalib`, maintenue et déjà correcte sur ce
  schéma) : l'incident a servi d'argument concret dans un arbitrage qui semblait acquis.

**Leçon :** demander "comment sais-tu ça ?" sur une affirmation technique précise
(schéma, nom de champ, signature de méthode) est une pratique de revue à elle seule,
indépendante du Plan Mode — le Plan Mode crée juste le bon moment pour la poser à
moindre coût.

### 2026-08-25 — Revue de code post-implémentation (skill `/code-review`)

Demandée après un premier sync réel réussi, sur `src/sport_coaching/ingestion` et
`tests/ingestion`. 4 findings, dont un réel bug de correction (pas un style/nit) :
le watermark de reprise incrémentale (`MAX(start_date)` en base) est recalculé après
coup, mais `get_activities()` renvoie les activités du plus récent au plus ancien —
si un sync est interrompu (rate limit, coupure réseau) après avoir committé
seulement les toutes premières (les plus récentes), le prochain sync repart déjà du
même watermark maximal et **ne récupère jamais les plus anciennes non traitées**,
silencieusement.

**Ce qui a marché :** le premier sync réel de l'utilisateur s'est déroulé sans
interruption, donc ce bug précis n'a pas corrompu les données déjà en base — mais
rien ne le garantissait, et un futur sync interrompu (quota Strava, coupure) l'aurait
fait sans avertissement. Trouvé par une revue de code post-implémentation, avant que
ça n'arrive, plutôt qu'en production.

**Correction appliquée :** tout un `sync` devient une seule transaction SQLite
(commit uniquement en fin de boucle, rollback complet sur exception) — un run
interrompu redémarre proprement au même point plutôt que de faire avancer le
watermark sur des données partielles. Un test de régression couvre explicitement ce
scénario (`test_sync_rolls_back_entirely_on_error`).

**Leçon :** une revue de code après un premier passage réel (données vraies, pas
seulement des mocks) a trouvé un bug que ni les tests unitaires ni le Plan Mode initial
n'avaient attrapé — les deux disciplines sont complémentaires, pas substituables l'une
à l'autre.

### 2026-08-25 — Audit de données + dashboard : le rendu réel comme discipline de vérification

Deux tâches enchaînées sur les vraies données (271 activités) : audit descriptif
(`notebooks/strava_data_audit.ipynb`) puis fonction de visualisation d'activité
(`sport_coaching.metrics.activity_report`).

**L'audit a de nouveau contredit une vérification pourtant faite sérieusement** : le
Plan Mode du 25/08 avait confirmé par introspection que `average_heartrate`/
`suffer_score`/`average_cadence` n'étaient PAS des champs du `SummaryActivity` de
stravalib — exact au sens strict (`model_fields` ne les liste pas), mais le JSON brut
réellement renvoyé par Strava les contient bien (champs "extra" que la lib laisse
passer sans les déclarer). Les deux vérifications n'étaient pas contradictoires, mais
l'introspection de bibliothèque et l'observation de données réelles répondent à des
questions différentes — seule la seconde est vraiment probante sur "qu'est-ce que
l'API renvoie". Schéma corrigé, colonnes ajoutées, backfill depuis `raw_json` déjà en
base (pas de nouvel appel API nécessaire).

**Le dashboard a révélé deux bugs qu'aucun test ni aucune relecture de code n'aurait
attrapés — seul le fait de regarder l'image rendue les a montrés :**
1. Cadence de course affichée deux fois trop faible (l'API Strava compte par jambe,
   l'appli affiche le total) — vérifié après coup contre la communauté développeurs
   Strava, corrigé avec un multiplicateur explicite et testé.
2. Un arrêt réel pendant une sortie (feu rouge, pause) faisait exploser l'allure d'un
   seul kilomètre à l'écran (~250 min/km), écrasant visuellement tous les autres
   splits — invisible dans les données brutes ou un test unitaire construit à la main,
   flagrant sur le graphique. Corrigé en excluant le temps non-`moving` du calcul.

**Leçon :** pour du code qui produit une sortie visuelle ou un résumé de données, "les
tests passent" ne suffit pas à conclure que c'est correct — regarder le rendu final
fait partie de la boucle de vérification, au même titre que les tests. Un test peut
valider qu'une fonction ne plante pas sans jamais révéler qu'elle produit un résultat
absurde.

### 2026-08-25 — Retour Gemini sur AGENTS.md : un LLM tiers reproduit le même biais

Demande d'avis externe (Gemini) sur deux idées d'ajout à `AGENTS.md` : un persona
("tu es un expert...") et une règle de non-présomption sur les schémas d'API externes.
Réponse de Gemini pertinente sur le fond, mais elle cite comme fait établi un seuil de
"150 à 200 instructions" pour la taille d'un fichier de règles — exactement le même
chiffre que ce journal avait déjà flaggé comme non sourcé et vraisemblablement fabriqué
(§1.2), sans que Gemini ne le sache. Confirmation en conditions réelles que la
discipline "vérifier avant de croire" (cf. incident du 25/08 ci-dessus) doit
s'appliquer à l'avis d'un LLM tiers sur notre méthodologie, pas seulement au code
produit par l'agent principal du projet.

### 2026-09-01 — Test du skill redaction-spec : le spec citait du code

Premier test réel du skill `redaction-spec` sur la feature "Visualisation Streamlit
des activités" (`specs/002-.../spec.md`). Le cadrage Q&A a bien fonctionné et a fait
remonter une information utile via exploration du code (une fonction existante,
`plot_activity_dashboard`, couvrait déjà exactement le besoin décrit) — mais cette
information a été reportée telle quelle dans le spec final : nom de fonction, chemin
de module, référence à une section de notebook. Repéré par l'utilisateur en
relecture : ça viole directement la règle du skill lui-même (« le QUOI, pas le
COMMENT »).

**Correction :** spec réécrit en termes purement fonctionnels (indicateurs et
graphiques énumérés sans citer de code), et une règle explicite ajoutée au skill
(« Aucune référence au code ») pour éviter la récidive.

**Leçon :** vérifier un fait par exploration du code (bonne pratique, évite de
halluciner) et le reporter tel quel dans un artefact censé être agnostique du code
(mauvaise pratique si mal filtré) sont deux étapes distinctes — la vérification
informe la rédaction, elle ne doit pas être recopiée dedans.

### 2026-09-01 — Bug de threading Streamlit/sqlite3 : la vérification "ça marche" ne suffisait pas

Implémentation de la feature "Visualisation Streamlit des activités"
(`specs/002-.../plan.md`) : connexion SQLite mise en cache via `@st.cache_resource`
dans `app/streamlit_app.py`. Vérification faite après implémentation : lancement réel
de l'app (`streamlit run`, HTTP 200 sans erreur) + exercice direct de la logique
métier (`queries.py`, `plot_activity_dashboard`) en Python nu contre la vraie base
(271 activités), y compris le cas limite "activité sans FC" — tout au vert.

**Ce qui a été raté :** aucune de ces vérifications ne déclenchait de *rerun*
Streamlit (l'exécution qui suit un changement de sélection dans un widget). En
changeant d'activité dans l'UI réelle, l'utilisateur a immédiatement obtenu
`sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in
that same thread` — Streamlit exécute les reruns sur des threads potentiellement
différents, et la connexion mise en cache avait été créée dans le thread du premier
run.

**Correction :** suppression du `@st.cache_resource` sur la connexion — une
connexion SQLite locale est bon marché à rouvrir à chaque rerun, ce qui élimine
structurellement toute réutilisation inter-thread. Un test de non-régression a été
ajouté via `streamlit.testing.v1.AppTest` (API officielle Streamlit, incluse avec le
package, aucune dépendance supplémentaire) qui simule réellement plusieurs reruns
successifs (changement de filtre puis changements d'activité répétés) — ce test
aurait attrapé le bug avant livraison.

**Outillage constaté :** `chromium-cli` / Playwright (recommandés par le skill `run`
pour piloter une app web avec captures d'écran réelles) ne sont pas installés dans
cet environnement — `AppTest` est le meilleur substitut disponible : il exécute le
vrai script Streamlit et ses reruns, mais sans rendu visuel réel (pas de capture
d'écran, pas de vérification humaine du rendu).

**Leçon :** pour une app interactive (pas juste un script), "la logique métier
fonctionne en Python nu" et "le serveur répond" ne suffisent pas à vérifier "l'app
fonctionne" — il faut exercer le cycle d'interaction réel (ici : les reruns
Streamlit déclenchés par les widgets), pas seulement son point d'entrée. Complète la
règle déjà connue du projet ("un test vert ne garantit pas un résultat correct") avec
un cas concret : ici, ni un test unitaire ni même un lancement serveur réussi
n'auraient suffi sans simuler l'interaction elle-même.

---

## 3. Catalogue des failles rencontrées

Vue transverse, organisée par catégorie plutôt que par date : chaque ligne renvoie à
l'entrée complète du journal (§2) au lieu de répéter le récit. Une catégorie sans
exemple reste listée tant qu'elle reste pertinente pour le projet, marquée comme telle
plutôt que supprimée — l'absence de cas est une information utile, pas un vide à
combler artificiellement.

| # | Catégorie | Exemple concret | Référence | Leçon retenue |
|---|---|---|---|---|
| 1 | Donnée non sourcée / fabriquée | Chiffre de benchmark ("MAE de 22.7") sans unité ni source dans le document produit initial ayant servi de base à la fiche de pratiques | §1.2 — 24/08 | Ne jamais reprendre un chiffre sans savoir d'où il vient ; définir ses propres seuils empiriquement plutôt que d'hériter d'une valeur non vérifiable |
| 2 | Donnée non sourcée / fabriquée | Seuil "150-200 instructions" pour la taille d'un fichier de règles, repris tel quel par Gemini en conseil sur `AGENTS.md`, sans source citée | §2 — 25/08, "Retour Gemini sur AGENTS.md" | La vérification s'applique à toute source d'affirmation technique, y compris l'avis d'un LLM tiers sur notre propre méthodologie |
| 3 | Absence de vérification avant affirmation technique | Schéma SQLite complet (colonnes, types) halluciné en Plan Mode pour l'ingestion Strava : mélange des objets `summary`/`detailed`, endpoint `/activities/{id}/streams` absent du plan | §2 — 25/08, "Schéma de données non vérifié en revue de plan" | Poser "comment sais-tu ça ?" sur toute affirmation de schéma/API/signature avant qu'elle soit figée — coût nul si posé en Plan Mode, avant la moindre ligne de code |
| 4 | Complexification inutile d'une tâche (sur-ingénierie, robustesse non demandée) | Aucun cas observé à ce jour | — | Catégorie connue mais pas encore rencontrée dans ce projet — à surveiller notamment lors des tâches plus larges à venir |
| 5 | Bug invisible aux tests, visible seulement au rendu réel | Cadence de course affichée 2x trop faible (unité API vs appli) ; un arrêt réel gonflant l'allure d'un split à ~250 min/km, écrasant tout le graphique | §2 — 25/08, "Audit de données + dashboard" | Pour du code produisant une sortie visuelle/un résumé, regarder le rendu final fait partie de la vérification — un test qui ne plante pas n'exclut pas un résultat absurde |
| 6 | Vérification qui ne reproduit pas le cycle d'exécution réel de l'app (interactions, reruns, threading) | `sqlite3.ProgrammingError` au changement d'activité dans l'app Streamlit — connexion mise en cache réutilisée sur un thread différent ; ni le lancement serveur (HTTP 200) ni les tests unitaires de la logique en Python nu ne déclenchaient de rerun | §2 — 01/09, "Bug de threading Streamlit/sqlite3" | Pour une app interactive, vérifier que le serveur démarre et que la logique fonctionne isolément ne suffit pas — il faut simuler l'interaction elle-même (ex. `streamlit.testing.v1.AppTest`) |

*Table mise à jour à chaque nouvelle entrée de journal qui révèle une faille — pas
seulement les incidents "négatifs" : une vérification qui a empêché une faille reste
dans le journal (§2) mais n'entre ici que si la faille a réellement eu lieu.*
