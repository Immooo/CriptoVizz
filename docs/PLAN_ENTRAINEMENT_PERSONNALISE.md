# Plan d'entraînement personnalisé — Soutenance Crypto Viz

Dernière mise à jour : 9 septembre 2026 à 16 h 13  
Prochaine étape : simulation PowerPoint après une vraie pause  
Soutenance : jeudi 10 septembre 2026 vers 16 h–17 h  
Durée maximale : 30 minutes  
Objectif oral : 20 à 24 minutes de présentation, démonstration comprise, puis questions

Ce document est à la fois un programme de travail, une banque de questions et un
journal de progression. Il doit être mis à jour après chaque séance afin que Git
conserve l'historique réel de la préparation.

---

## 1. Diagnostic de départ

### Échelle de suivi

| Statut | Signification | Critère concret |
|---|---|---|
| ⬜ Pas vu | Notion non travaillée | Impossible de commencer une réponse |
| 🟡 Vu | Notion reconnue | Réponse possible avec les notes |
| 🟠 En cours | Compréhension présente mais imprécise | Réponse sans notes, avec erreurs ou hésitations |
| 🟢 Acquis | Réponse autonome et exacte | 30 à 60 secondes, sans erreur importante |
| 🔵 Solide | Réponse précise sous relance du jury | Exemple, limite et justification inclus |
| 🔴 À revoir | Erreur importante détectée | Révision ciblée prioritaire |

### Évaluation issue du premier entraînement oral

| Compétence | Statut | Ce qui est déjà maîtrisé | Ce qu'il faut corriger |
|---|---:|---|---|
| Présentation fonctionnelle du projet | 🟠 | RSS, sentiment, topics et Grafana sont cités | Ajouter RabbitMQ et MySQL, commencer par le besoin et supprimer les répétitions |
| Parcours complet d'un article | 🟠 | Ordre général, Analytics, Storage et deux queues compris | Dire message JSON, citer les queues `_v3` et éviter les hésitations |
| Utilité de RabbitMQ | 🟢 | Découplage, durable, persistent, ACK/NACK compris | Distinguer indisponibilité du broker et reprise des messages déjà acceptés |
| Positionnement Big Data | 🟠 | Pipeline, streaming et analyse identifiés | Ne pas prétendre que le volume local est massif ; utiliser les V avec honnêteté |
| Montée en charge | 🔴 | Scaling horizontal d'Analytics compris | Revoir prefetch, back-pressure et identifier les goulots par la mesure |
| Expression orale | 🟠 | Raisonnement spontané et vocabulaire technique présent | Structurer en idée → preuve projet → limite, réduire « en gros » et « du coup » |

### Tes points forts actuels

- Tu comprends la chaîne métier et technique dans son ensemble.
- Tu connais déjà les notions RabbitMQ les plus importantes : producteur,
  consumer, queue durable, message persistant, ACK, NACK et prefetch.
- Tu reconnais honnêtement que le projet est une démonstration locale.
- Tu sais expliquer avec tes mots, ce qui est une excellente base pour progresser.

### Tes priorités avant la soutenance — mise à jour après la séance de 14 h 45

1. Distinguer précisément prefetch, back-pressure, throughput et latency.
2. Maîtriser DLQ, redelivery après publication et idempotence concrète.
3. Expliquer les SPOF, la panne MySQL et pourquoi Compose n'est pas de la HA.
4. Rendre le parcours exact avec `raw_news`, `enriched_news` et des messages JSON.
5. Justifier MySQL face à MongoDB sans caricaturer NoSQL.
6. Répondre en 30 à 45 secondes, après une courte réflexion, sans « en gros » ni « du coup ».

---

## 2. Méthode d'apprentissage choisie

### Principe central : produire avant de relire

Pour cette soutenance, connaître une phrase quand elle est sous les yeux ne suffit
pas. Il faut pouvoir la reconstruire sous stress, répondre à une reformulation et
faire le lien avec le code. Chaque séance commence donc avec les notes fermées.

Cycle recommandé pour une notion :

1. **Question sans notes — 3 minutes** : répondre à voix haute.
2. **Contrôle — 5 minutes** : vérifier dans ce guide, le code ou le PowerPoint.
3. **Correction — 5 minutes** : écrire uniquement les erreurs importantes.
4. **Nouvelle réponse — 3 minutes** : reformuler sans réciter mot pour mot.
5. **Relance — 4 minutes** : répondre à « pourquoi ? », « limite ? » ou « panne ? ».
6. **Rappel différé** : refaire la question après au moins un autre bloc, puis le lendemain.

La relecture ne doit pas dépasser environ 20 % du temps total. Le reste doit être
consacré à parler, dessiner, démontrer, répondre et corriger.

### Format de travail : 45 minutes + 10 minutes

Un bloc standard dure 45 minutes :

- 0–5 min : rappel de la séance précédente, notes fermées ;
- 5–20 min : questions ciblées ;
- 20–32 min : explication au tableau ou devant le PowerPoint ;
- 32–40 min : question piège ou scénario de panne ;
- 40–45 min : notation, correction et choix de la prochaine priorité.

Puis prendre **10 minutes de vraie pause** : se lever, boire, marcher, regarder au
loin. Éviter une vidéo ou un réseau social qui rendrait le retour plus difficile.
Après trois blocs, prendre 25 à 30 minutes de pause.

Le ratio 45/10 n'est pas une loi scientifique : c'est un cadre pratique adapté à
un entraînement oral et technique. Si l'attention chute avant 45 minutes, passer à
25/5 ; si une simulation complète est en cours, aller jusqu'au bout sans la couper.

### Réponse orale en quatre mouvements

Pour presque toutes les questions du jury :

1. **Définition** : une phrase simple.
2. **Application** : « Dans Crypto Viz… ».
3. **Justification** : pourquoi ce choix est utile.
4. **Limite** : ce que le choix ne garantit pas.

Exemple :

> Le prefetch limite le nombre de messages non acquittés livrés à un consumer.
> Dans Crypto Viz, il vaut 50 sur Analytics et Storage. Il évite qu'un seul worker
> réserve tout le backlog et contribue à la back-pressure. Il ne rend toutefois pas
> le traitement plus rapide à lui seul : pour augmenter le débit, il faut aussi
> ajouter des consumers et vérifier la capacité de MySQL.

### Répétition espacée à très court délai

Comme la soutenance est demain, utiliser cet espacement :

- **R0** : réponse initiale ;
- **R1** : 20 à 40 minutes plus tard ;
- **R2** : en fin de soirée ;
- **R3** : jeudi matin ;
- **R4** : rappel léger 30 à 60 minutes avant la soutenance.

Une question passe à 🟢 seulement après deux réponses correctes sans notes, dont
une différée. Elle passe à 🔵 si tu réponds aussi à une relance imprévue.

### Sommeil et charge de travail

Arrêter l'apprentissage lourd suffisamment tôt pour préserver une nuit normale.
Le dernier bloc du soir sert à rappeler, pas à découvrir. Jeudi matin, corriger
trois faiblesses maximum : accumuler de nouvelles notions juste avant l'oral risque
d'augmenter la confusion et le stress.

### Fondements utilisés

- La pratique de tests et le rappel actif sont mieux étayés que la simple relecture.
- Répartir les rappels dans le temps améliore généralement la rétention à long terme.
- Le feedback après une tentative permet de corriger précisément les erreurs.
- Le sommeil après l'apprentissage participe à la récupération et à la consolidation.
- Pour l'oral, la compétence évaluée doit être répétée dans des conditions proches :
  debout, chronométré, avec slides, démonstration et interruptions.

Sources principales :

- [Dunlosky et al. — Improving Students' Learning With Effective Learning Techniques](https://journals.sagepub.com/doi/10.1177/1529100612453266)
- [Roediger et Karpicke — Test-Enhanced Learning](https://doi.org/10.1111/j.1467-9280.2006.01693.x)
- [Cepeda et al. — Distributed Practice in Verbal Recall Tasks](https://pubmed.ncbi.nlm.nih.gov/16719566/)
- [PubMed — Contributions of post-learning REM and NREM sleep to memory retrieval](https://pubmed.ncbi.nlm.nih.gov/33588273/)
- [Systematic review — Sleep and Learning](https://pmc.ncbi.nlm.nih.gov/articles/PMC11511274/)

---

## 3. Planning réel du 9 septembre 14 h 30 au 10 septembre 17 h

Ce planning part de la situation réelle : reprise entre 14 h 30 et 15 h aujourd'hui,
puis soutenance demain vers 16 h–17 h. Il ne faut pas tenter de travailler toutes
les 60 questions avec la même intensité. La priorité est : fondamentaux exacts,
faiblesses actuelles, présentation complète, démo, puis questions difficiles.

Si tu reprends à 15 h, décale simplement les horaires de 30 minutes. Ne supprime
pas les pauses et ne décale pas la fin de soirée au-delà d'environ 22 h 15.

### Mercredi 9 septembre après-midi — construire la solidité

| Heure si départ 14 h 30 | Durée | Travail exact | Résultat obligatoire |
|---|---:|---|---|
| 14:30–14:45 | 15 min | Installation, eau, téléphone éloigné, ouvrir PowerPoint et guide | Poste prêt, aucune révision passive |
| 14:45–16:13 | 88 min | **Séance orale réalisée** : architecture/RabbitMQ/fiabilité, puis Big Data/scalabilité/limites | Diagnostic mis à jour dans la section 11 |
| 16:13–17:00 env. | 45 min env. | Vraie pause, collation et repos vocal | Couper réellement avec la théorie |
| Après la pause | 45 min | **Simulation PowerPoint n°1**, slide par slide, debout et chronométrée | Noter durée et trois erreurs maximum |
| 18:25–19:10 | 45 min | Grande pause et repas | Couper réellement avec le projet |
| Après la simulation | 30 min | Corriger uniquement les trois erreurs de la simulation | Chaque passage faible refait deux fois |
| 19:40–19:50 | 10 min | Pause | — |
| Plus tard | 45 min | **Démo réelle + plan B** : services, RabbitMQ, Grafana, captures | Démo entre 3 et 5 min sans improvisation |
| 20:35–20:45 | 10 min | Pause | — |
| En soirée | 40 min | **Jury mixte** : 10 questions, avec rappel ciblé des notions rouges | Au moins 7 réponses notées 2 ou 3 |
| 21:25–21:40 | 15 min | Journal : scores, statuts et trois points faibles de demain | Suivi rempli dans la section 11 |
| 21:40–22:00 | 20 min max | Rappel léger : pipeline, ACK, Big Data, conclusion | Arrêt de l'apprentissage lourd |
| Après 22:00 | — | Préparer vêtements/matériel, détente et sommeil normal | Pas de nouveau concept |

### Règle de décision mercredi soir

- Si la simulation dépasse 25 minutes : raccourcir les explications, sans parler
  plus vite, et identifier deux slides à condenser.
- Si le pipeline contient une erreur : refaire immédiatement le dessin et la réponse.
- Si une question niveau 3 bloque : apprendre une réponse pivot, puis la reformuler.
- Si la fatigue devient forte : supprimer le bloc de 21 h 40, jamais le sommeil.
- Une seule simulation complète aujourd'hui suffit ; répéter cinq fois un oral fatigué
  risque surtout d'automatiser les tics de langage.

### Jeudi 10 septembre matin — rappel espacé et deuxième simulation

L'heure de lever peut varier. Conserver l'ordre et les pauses plutôt que de suivre
les horaires à la minute.

| Heure indicative | Durée | Travail exact | Résultat obligatoire |
|---|---:|---|---|
| 09:30–09:55 | 25 min | Page blanche : pipeline, queues v3, DLQ, tables, 4V et trois limites | Rappel sans notes |
| 09:55–10:10 | 15 min | Vérification et correction ciblée | Seulement les oublis réels |
| 10:10–10:20 | 10 min | Pause | — |
| 10:20–11:05 | 45 min | **Simulation PowerPoint n°2** avec démo ou démo simulée | Oral stable en 20–24 min |
| 11:05–11:20 | 15 min | Pause et repos vocal | — |
| 11:20–11:50 | 30 min | Corriger les trois faiblesses observées | Réponse correcte deux fois |
| 11:50–12:20 | 30 min | Questions 23, 27, 41, 46, 48, 51 et 52 | Scénarios de panne et scale maîtrisés |
| À partir de 12:20 | — | Déjeuner et vraie coupure | Ne pas saturer avant 16 h–17 h |

### Jeudi après-midi — rester chaud sans se fatiguer

| Heure indicative | Durée | Travail exact | But |
|---|---:|---|---|
| 13:45–14:10 | 25 min | 8 questions mélangées, réponses courtes | Réactivation, pas apprentissage |
| 14:10–14:25 | 15 min | Vérification technique : PowerPoint, chargeur, Docker, captures | Sécuriser la démonstration |
| 14:25–15:00 | 35 min | Pause, marche, eau | Récupérer |
| Vers 15:00 | 15 min | Première phrase, architecture 90 s, conclusion | Installer la fluidité |
| Ensuite | — | Stop révision jusqu'à l'installation | Préserver attention et voix |

Si le passage est confirmé à 17 h plutôt qu'à 16 h, ajouter vers 15 h 45 un seul
rappel de 10 minutes sur les trois questions encore orange. Ne pas refaire tout le
PowerPoint et ne pas ajouter une heure de révision.

### Entre 30 et 60 minutes avant le passage

- Ne plus faire de simulation complète.
- Relire seulement la fiche d'urgence de la section 10 pendant cinq minutes.
- Dire une fois la première phrase, le pipeline et la conclusion.
- Vérifier l'affichage, le PowerPoint, Grafana, RabbitMQ et les captures de secours.
- Aller aux toilettes, boire quelques gorgées et ralentir volontairement le débit.
- Si une notion ne revient plus, noter trois mots-clés et arrêter : ne pas relire tout
  le document sous stress.

### Stratégie pendant la soutenance

- Parler environ 10 % plus lentement que dans une conversation normale.
- Après une question, prendre deux secondes avant de commencer.
- Si la question est floue : « Si je comprends bien, vous me demandez… ».
- Si tu ne connais pas la réponse : dire ce que le système garantit réellement,
  reconnaître la limite, puis proposer comment tu la vérifierais.
- Pour une question technique : définition → application Crypto Viz → intérêt → limite.
- Pour une interruption pendant la démo : revenir au diagramme et poursuivre avec le
  plan B au lieu de déboguer longtemps devant le jury.

---

## 4. Vérité technique du projet à mémoriser

### Architecture actuelle

```text
CoinDesk + Cointelegraph
        ↓ lecture RSS périodique
Scraper Python — producteur
        ↓ raw_news
RabbitMQ — queue durable + messages persistants
        ↓ consommation avec ACK manuel
Analytics — consumer puis producteur
        ↓ sentiment + topics
        ↓ enriched_news
RabbitMQ
        ↓ consommation avec ACK manuel
Storage Worker
        ↓ INSERT idempotent + agrégations horaires
MySQL
        ↓ requêtes SQL directes
Grafana — 6 panneaux et rafraîchissement 30 s
```

Les messages invalides peuvent être dirigés vers `raw_news.dlq` et
`enriched_news.dlq`. Le service `clean` applique une rétention de 30 jours par
défaut aux données brutes. Les agrégats permettent de conserver les tendances.

### Les phrases à ne pas dire

| Formulation imprécise | Formulation correcte |
|---|---|
| « Le scraper récupère des cryptomonnaies » | « Le scraper récupère des articles sur les cryptomonnaies » |
| « Grafana passe par une API » | « Grafana interroge directement MySQL avec des requêtes SQL » |
| « Le prefetch envoie 50 messages après traitement » | « Il limite à 50 les messages livrés mais pas encore acquittés par consumer » |
| « Les messages restent en mémoire » | « Les messages persistants sont écrits durablement par RabbitMQ » |
| « RabbitMQ garantit qu'on ne perd jamais rien » | « Durable + persistent réduisent le risque ; ce n'est pas une garantie absolue » |
| « ACK garantit exactement une fois » | « Le système vise au moins une fois ; l'idempotence absorbe les redéliveries » |
| « C'est Big Data car il y a RabbitMQ » | « Le volume de démo est faible, mais l'architecture applique plusieurs patterns Big Data » |

### Technologies et responsabilités

| Élément | Responsabilité | Preuve ou configuration |
|---|---|---|
| Scraper | Collecter, normaliser et publier | Deux RSS, intervalle configurable |
| `raw_news` | Transporter les événements bruts | Queue durable, DLQ associée |
| Analytics | Enrichir sentiment et topics | Consumer concurrent, `prefetch_count=50` |
| `enriched_news` | Transporter les événements enrichis | Queue durable, DLQ associée |
| Storage | Dédupliquer, stocker et agréger | ACK après transaction réussie |
| MySQL | Articles et tables analytiques | `news_articles`, `analytics_hourly`, `pipeline_hourly` |
| Grafana | Exploration et observabilité | Volume, sentiment, articles, débit, latence |
| Clean | Rétention des articles bruts | `RETENTION_DAYS=30` par défaut |
| Docker Compose | Reproductibilité locale | Services, réseaux, volumes, healthchecks |

---

## 5. Questions niveau 1 — fondamentales

Objectif : réponse claire en 20 à 40 secondes. Une erreur ici est prioritaire.

| # | Question | Éléments indispensables | Statut | R0 | R1 | R2/R3 |
|---:|---|---|:---:|:---:|:---:|:---:|
| 1 | Quel problème résout Crypto Viz ? | Veille continue, synthèse des actualités, tendances | 🟠 | ✓ | ⬜ | ⬜ |
| 2 | Présente le projet en une minute. | Besoin, pipeline, résultat, valeur | 🟠 | ✓ | ⬜ | ⬜ |
| 3 | Décris le parcours complet d'un article. | RSS → scraper → deux queues → Analytics → Storage → MySQL → Grafana | 🟠 | ✓ | ⬜ | ⬜ |
| 4 | Qu'est-ce qu'un producteur ? | Crée et publie un message | 🟢 | ✓ | ✓ | ⬜ |
| 5 | Qu'est-ce qu'un consumer ? | Reçoit, traite, confirme ou rejette | 🟢 | ✓ | ✓ | ⬜ |
| 6 | Quels sont les producteurs et consumers ici ? | Scraper, Analytics double rôle, Storage | 🟠 | ✓ | ⬜ | ⬜ |
| 7 | Pourquoi RabbitMQ ? | Découplage, tampon, fiabilité, rythmes différents | 🟢 | ✓ | ✓ | ⬜ |
| 8 | Quelles queues existent ? | `raw_news`, `enriched_news`, deux `.dlq` | 🟠 | ✓ | ⬜ | ⬜ |
| 9 | Que produit Analytics ? | Score, label de sentiment, liste de topics | 🟢 | ✓ | ⬜ | ⬜ |
| 10 | Pourquoi MySQL ? | Structure, contraintes, requêtes SQL, volume de démo | 🟠 | ✓ | ⬜ | ⬜ |
| 11 | Que contient `news_articles` ? | Articles enrichis et dédupliqués | 🟡 | ⬜ | ⬜ | ⬜ |
| 12 | À quoi servent les agrégats horaires ? | Éviter de rescanner les articles, requêtes Grafana rapides | 🟡 | ⬜ | ⬜ | ⬜ |
| 13 | Que montre Grafana ? | Volume, sentiment, articles, throughput, latency | 🟢 | ✓ | ⬜ | ⬜ |
| 14 | Grafana utilise-t-il une API applicative ? | Non, datasource MySQL et SQL direct | 🔴 | ✗ | ⬜ | ⬜ |
| 15 | Pourquoi Docker Compose ? | Lancement reproductible, isolation, réseaux, volumes, sans HA | 🟠 | ✓ | ⬜ | ⬜ |

#### Réponses pivots niveau 1

**Présentation en une minute**

> Crypto Viz est une application de veille sur l'actualité crypto. Elle collecte
> en continu des articles depuis plusieurs flux RSS, les transporte de manière
> asynchrone avec RabbitMQ, puis enrichit chaque article avec un sentiment et des
> thèmes. Les articles dédupliqués et les agrégats horaires sont stockés dans MySQL.
> Grafana permet ensuite de suivre les tendances, le débit et la latence du pipeline.

**Parcours d'un article**

> Le scraper lit un flux RSS, normalise l'article et le publie dans `raw_news`.
> Analytics consomme ce message, calcule le sentiment et les topics, publie le JSON
> enrichi dans `enriched_news`, puis acquitte le message brut. Storage consomme
> le message enrichi, effectue une transaction idempotente dans MySQL et envoie son
> ACK après réussite. Grafana interroge ensuite MySQL directement.

---

## 6. Questions niveau 2 — techniques attendues

Objectif : réponse de 30 à 60 secondes avec application au projet.

| # | Question | Point de contrôle | Statut |
|---:|---|---|:---:|
| 16 | Quelle différence entre queue durable et message persistant ? | Déclaration de la queue vs propriété du message | 🟠 |
| 17 | Qu'est-ce qu'un ACK ? | Confirmation après succès | 🟢 |
| 18 | Pourquoi `auto_ack=False` ? | Éviter de perdre un traitement si le worker crash | 🟠 |
| 19 | Que fait un NACK avec `requeue=True` ? | Remise en file pour erreur transitoire | 🟢 |
| 20 | Quand utiliser une DLQ ? | Message invalide/permanent, diagnostic et rejeu contrôlé | 🔴 |
| 21 | Une queue durable suffit-elle ? | Non, message persistent nécessaire, garanties limitées | 🟠 |
| 22 | Que se passe-t-il si Analytics crash avant l'ACK ? | Redelivery probable | 🟠 |
| 23 | Que se passe-t-il après publication enrichie mais avant ACK brut ? | Doublon possible en aval | 🟠 |
| 24 | Pourquoi viser une livraison au moins une fois ? | Fiabilité avec redelivery possible | 🟡 |
| 25 | Comment absorber les doublons ? | ID déterministe, PK, `INSERT ... ON DUPLICATE KEY UPDATE`, transaction | 🟠 |
| 26 | Qu'est-ce que l'idempotence ? | Même opération répétée, même état final | 🟠 |
| 27 | À quoi sert `prefetch_count=50` ? | Messages non acquittés max par consumer | 🔴 |
| 28 | Qu'est-ce que la back-pressure ? | Adapter/limiter la charge quand aval plus lent | 🔴 |
| 29 | Comment scaler Analytics ? | Plusieurs replicas consommateurs concurrents | 🟠 |
| 30 | Quelle commande démontre ce scaling ? | `docker compose up --build --scale analytics=3` | 🟡 |
| 31 | Pourquoi Analytics n'a-t-il pas de `container_name` fixe ? | Permettre plusieurs replicas Compose | 🟠 |
| 32 | Pourquoi précalculer `analytics_hourly` ? | Lecture rapide, coût déplacé vers ingestion | 🟡 |
| 33 | Que mesure `pipeline_hourly` ? | Volume, somme/max de latence par heure/source | 🟡 |
| 34 | Différence throughput/latency ? | Débit par temps vs délai d'un événement | 🔴 |
| 35 | D'où part la mesure de latence ? | `collected_at`, pas publication éditeur ni simple latence réseau | 🔴 |
| 36 | Comment fonctionne le sentiment ? | Comptage lexical normalisé, score [-1,1], label | 🟠 |
| 37 | Limites du sentiment lexical ? | Contexte, négation, sarcasme, vocabulaire | 🟢 |
| 38 | Comment sont détectés les topics ? | Mots-clés, plusieurs topics possibles, `other` | 🟠 |
| 39 | Pourquoi des volumes Docker ? | Persistance MySQL, RabbitMQ et Grafana | 🟡 |
| 40 | Que garantit un healthcheck ? | État testé/démarrage ordonné, pas haute disponibilité | 🟠 |

#### Réponses pivots niveau 2

**Durable, persistent et ACK**

> `durable=True` demande à RabbitMQ de recréer la queue après son redémarrage.
> Le mode de livraison persistant concerne chaque message et demande son stockage
> durable. L'ACK manuel indique seulement que le consumer a terminé. Il faut combiner
> ces mécanismes, mais ils ne constituent pas à eux seuls une garantie de zéro perte.

**Idempotence après une redelivery**

> L'ACK peut être perdu après l'écriture MySQL, donc RabbitMQ peut redélivrer le
> message. L'identifiant de l'article est déterministe, basé sur son URL. La clé
> primaire et `INSERT ... ON DUPLICATE KEY UPDATE` empêchent une seconde insertion ; les agrégats ne sont
> mis à jour que lorsqu'un nouvel article a réellement été inséré.

**Prefetch et scaling**

> Le prefetch fixe le nombre de messages non acquittés que RabbitMQ peut livrer à
> chaque consumer. La valeur 50 protège contre une réservation excessive du backlog.
> Pour augmenter le débit, on peut démarrer plusieurs instances Analytics ; RabbitMQ
> distribue alors les messages entre consommateurs concurrents.

---

## 7. Questions niveau 3 — jury exigeant et questions pièges

Objectif : raisonner honnêtement, annoncer les compromis et ne pas inventer.

| # | Question | Angle de réponse attendu | Statut |
|---:|---|---|:---:|
| 41 | Le projet est-il vraiment Big Data ? | Petit volume réel, patterns Big Data et trajectoire de scale | 🟠 |
| 42 | Quels V sont présents ? | Velocity, Variety limitée, Veracity, Volume faible | 🟠 |
| 43 | Pourquoi RabbitMQ plutôt que Kafka ? | Work queues/ACK simples ; Kafka pour log distribué et replay massif | 🟠 |
| 44 | À partir de quand choisir Kafka ? | Très haut débit, rétention longue, replay, plusieurs groupes | 🟡 |
| 45 | Pourquoi MySQL plutôt qu'une base NoSQL ? | Données structurées, contraintes, SQL/Grafana ; compromis de scale | 🟠 |
| 46 | Que changer pour 10 millions d'articles/jour ? | Partitionnement, cluster, workers, stockage analytique, tests de charge | 🟠 |
| 47 | Quels composants peuvent saturer à ×100 ? | Mesurer backlog/throughput/latency ; Analytics, RabbitMQ, Storage, MySQL, Grafana | 🔴 |
| 48 | Le prefetch augmente-t-il automatiquement le débit ? | Non, fenêtre de travail ; dépend du traitement et des ressources | 🔴 |
| 49 | Peut-on scaler Storage comme Analytics ? | Oui en théorie, mais contention MySQL à mesurer | 🟡 |
| 50 | Quels sont les SPOF actuels ? | RabbitMQ et MySQL mono-nœuds, machine Docker | 🔴 |
| 51 | Que se passe-t-il si RabbitMQ est indisponible ? | Publications impossibles ; reconnexion ; messages déjà persistés conservés selon garanties | 🟠 |
| 52 | Que se passe-t-il si MySQL tombe ? | Storage échoue, NACK/requeue, backlog augmente | 🟠 |
| 53 | Une DLQ règle-t-elle automatiquement l'erreur ? | Non, conservation ; diagnostic et rejeu restent nécessaires | 🟡 |
| 54 | Comment surveiller la qualité du sentiment ? | Jeu annoté, précision/rappel/F1, suivi de dérive | ⬜ |
| 55 | Comment éviter une croissance infinie des données ? | Rétention brute, agrégats, archivage éventuel | 🟡 |
| 56 | Pourquoi deux réseaux Docker ? | Limiter les connexions entre domaines RabbitMQ/MySQL | 🟡 |
| 57 | Les secrets sont-ils sécurisés ? | `.env` local non versionné ; suffisant démo, secret manager en prod | 🟡 |
| 58 | Comment tester la résilience ? | Arrêt worker/broker/DB, redelivery, doublons, backlog, DLQ | 🟡 |
| 59 | Pourquoi le dashboard n'est-il pas du temps réel strict ? | Polling RSS + pipeline + refresh 30 s : quasi temps réel | 🟡 |
| 60 | Quelle amélioration apporte le plus de valeur ? | Choisir selon objectif : NLP, sources, HA ou stockage analytique | 🟠 |

#### Réponses pivots niveau 3

**Le projet est-il vraiment Big Data ?**

> Le dataset de démonstration reste volontairement petit, donc je ne revendique pas
> un volume massif en local. En revanche, le système applique des patterns utiles au
> Big Data : ingestion continue, pipeline asynchrone, back-pressure, traitement
> incrémental, workers scalables et observabilité du débit et de la latence. Pour un
> volume industriel, il faudrait également distribuer RabbitMQ et le stockage.

**Charge multipliée par 100**

> Je commencerais par mesurer le backlog, le débit et la latence afin d'identifier le
> vrai goulot. Analytics peut être répliqué horizontalement. Storage peut aussi avoir
> plusieurs consumers, mais MySQL risque alors de devenir la limite ; j'optimiserais
> les index, les transactions et les écritures par lot. À une échelle beaucoup plus
> grande, j'évaluerais un broker clusterisé et un stockage analytique partitionné.

**RabbitMQ contre Kafka**

> RabbitMQ correspond au besoin actuel de files de travail, d'ACK individuels et de
> routage simple. Kafka devient plus pertinent quand on veut conserver longtemps un
> journal distribué, rejouer l'historique ou servir plusieurs groupes indépendants à
> très haut débit. Pour deux flux RSS locaux, Kafka ajouterait une complexité peu utile.

---

## 8. Exercices pratiques et simulations

### Exercice A — dessin de mémoire, 5 minutes

Dessiner tous les composants, puis ajouter :

- les deux noms de queues en version `v3` ;
- les endroits où un ACK est envoyé ;
- les deux DLQ ;
- les trois tables MySQL ;
- les limites de prefetch ;
- le service de nettoyage ;
- le sens des requêtes Grafana.

Barème : 1 point par élément, objectif 12/14 ou plus.

### Exercice B — parcours d'un message, 90 secondes

Choisir un article fictif CoinDesk et expliquer : normalisation, publication,
enrichissement, seconde publication, transaction, déduplication et affichage.
Recommencer avec une interruption : « Analytics vient de crasher, que se passe-t-il ? »

### Exercice C — jury contradicteur, 10 minutes

Répondre successivement :

1. « Deux RSS, ce n'est absolument pas du Big Data. »
2. « Durable veut dire qu'aucun message ne peut être perdu, non ? »
3. « Pourquoi ne pas supprimer RabbitMQ et écrire directement en base ? »
4. « Votre sentiment par mots-clés n'est pas de l'intelligence artificielle. »
5. « Trois replicas Analytics ne rendent pas tout le système scalable. »

Réponse attendue : reconnaître la part vraie, défendre le choix dans le périmètre,
puis annoncer clairement la limite et l'évolution possible.

### Exercice D — démonstration nominale, 3 à 5 minutes

1. Montrer `docker compose ps`.
2. Montrer dans RabbitMQ les queues `raw_news` et `enriched_news`.
3. Montrer les consumers et expliquer le prefetch.
4. Montrer dans Grafana la période, le filtre topic et les six panneaux.
5. Commenter un résultat réel, pas seulement l'interface.

### Exercice E — démonstration dégradée

Faire une simulation sans Internet ou sans dashboard. Utiliser les captures du
PowerPoint et continuer l'explication. L'objectif n'est pas de réparer en direct,
mais de préserver le fil de la soutenance et d'expliquer le rôle du composant en panne.

### Exercice F — simulation complète

- Debout et chronométré.
- PowerPoint en plein écran.
- Aucune note pendant les cinq premières minutes.
- Une interruption volontaire sur RabbitMQ.
- Démo limitée à cinq minutes.
- Cinq questions aléatoires à la fin.
- Enregistrement audio ou vidéo si possible.

Après la simulation, ne noter que : une force, trois erreurs prioritaires et une
habitude orale à corriger. Refaire uniquement les trois passages faibles.

---

## 9. Barème d'auto-évaluation

### Note par réponse

| Score | Critère |
|---:|---|
| 0 | Pas de réponse ou contresens |
| 1 | Idée générale, mais erreur technique importante |
| 2 | Réponse correcte, mais sans preuve projet ou avec hésitations |
| 3 | Réponse exacte, structurée, liée au projet et avec une limite |

### Seuils de préparation

- Niveau 1 : au moins 13 questions sur 15 avec un score ≥ 2.
- Niveau 2 : au moins 20 questions sur 25 avec un score ≥ 2.
- Niveau 3 : au moins 12 questions sur 20 avec un score ≥ 2.
- Aucune question marquée 🔴 le jeudi midi.
- Présentation comprise entre 20 et 24 minutes deux fois de suite.
- Démo principale en moins de 5 minutes.

### Tableau de progression global

| Domaine | Score initial /3 | Dernier score /3 | Cible | Prochaine action |
|---|---:|---:|---:|---|
| Pitch et valeur | 1.5 | 2.2 | 2.5 | Ajouter RabbitMQ et MySQL sans allonger le pitch |
| Architecture | 2.0 | 2.1 | 3.0 | Parcours fluide avec queues v3 et messages JSON |
| RabbitMQ | 2.3 | 1.9 | 3.0 | DLQ, back-pressure, prefetch et publication avant ACK |
| MySQL/idempotence | 1.5 | 1.8 | 2.5 | Citer SHA-256, PK, `INSERT ... ON DUPLICATE KEY UPDATE` et condition sur les agrégats |
| Analytics | 1.8 | 2.5 | 2.5 | Confirmer par rappel différé la méthode et ses limites |
| Big Data | 1.5 | 2.3 | 2.5 | Conserver la réponse honnête et mesurer avant de nommer un goulot |
| Scalabilité | 1.5 | 2.0 | 2.5 | Distinguer prefetch, débit et ajout de replicas |
| Grafana/observabilité | 1.8 | 1.8 | 2.5 | Réapprendre throughput et latency collecte-stockage |
| Démo |  |  | 2.5 | Faire une démo nominale et une dégradée |
| Expression orale | 1.7 | 1.8 | 2.5 | Pause de 1–2 s, réponses courtes, supprimer « en gros » et « du coup » |

---

## 10. Fiche d'urgence à relire avant l'oral

### Pipeline

`RSS → scraper → raw_news → Analytics → enriched_news → Storage → MySQL → Grafana`

### Trois décisions fortes

1. RabbitMQ découple les rythmes et permet ACK, redelivery et back-pressure.
2. L'identifiant déterministe et la transaction MySQL rendent le stockage idempotent.
3. Les agrégats horaires évitent de recalculer tout l'historique pour Grafana.

### Trois limites honnêtes

1. Volume et variété limités dans la démonstration locale.
2. RabbitMQ et MySQL restent des points uniques de défaillance.
3. Le sentiment lexical comprend mal le contexte, la négation et le sarcasme.

### Big Data en une phrase

> Le volume local est faible, mais l'architecture applique ingestion continue,
> découplage asynchrone, back-pressure, traitement incrémental, scaling horizontal
> d'Analytics et observabilité ; une échelle industrielle exigerait aussi un broker
> et un stockage distribués.

### Fiabilité en une phrase

> Les queues durables, messages persistants et ACK manuels limitent les pertes et
> permettent la redelivery ; comme celle-ci peut créer des doublons, le stockage est
> idempotent grâce à l'identifiant déterministe et à la contrainte MySQL.

### Première phrase

> Crypto Viz transforme un flux continu et dispersé d'actualités crypto en indicateurs
> compréhensibles sur les thèmes, le sentiment et le fonctionnement du pipeline.

### Conclusion

> Le projet démontre une chaîne complète, observable et évolutive, de l'ingestion à
> la visualisation. Sa valeur est de rendre les tendances de l'actualité crypto
> rapidement lisibles, tout en assumant clairement les limites du prototype local.

---

## 11. Journal de suivi versionné

Copier une ligne après chaque bloc. Conserver les anciennes lignes : elles forment
l'historique Git de la préparation.

| Date/heure | Durée | Travail effectué | Questions réussies | Questions à revoir | Statut suivant | Commit |
|---|---:|---|---|---|---|---|
| 09/09/2026 | 5 réponses | Diagnostic général initial | RabbitMQ, pipeline global | précision, Big Data, prefetch, scale | En cours | Création du plan |
| 09/09/2026 14:45–16:13 | 88 min | Bloc 1 architecture/RabbitMQ/fiabilité ; bloc 2 Big Data/scalabilité/limites | découplage, durable/persistent/ACK, erreur temporaire/permanente, scaling Analytics, 4V, RabbitMQ/Kafka, sentiment | DLQ, back-pressure, prefetch, redelivery/idempotence, goulots, throughput/latency, SPOF, panne MySQL, HA Compose, MySQL/MongoDB | Pause puis simulation PowerPoint ; rappel différé ciblé demain | À compléter par le commit de séance |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |

### Historique des simulations

| Date/heure | Durée présentation | Démo | Questions / score | Trois erreurs | Action corrective |
|---|---:|---:|---:|---|---|
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

### Liste personnelle des erreurs à ne plus reproduire

- [x] Ne pas dire que le scraper récupère des cryptomonnaies.
- [x] Ne pas ajouter une API entre MySQL et Grafana.
- [ ] Définir parfaitement `prefetch_count`.
- [ ] Distinguer queue durable, message persistant et ACK.
- [ ] Défendre le Big Data sans prétendre avoir un volume massif.
- [ ] Citer au moins quatre goulots possibles en cas de charge ×100.
- [ ] Dire exactement `raw_news` et `enriched_news`, comme dans `.env.example` et RabbitMQ.
- [ ] Parler de messages JSON, jamais de « fichiers » dans RabbitMQ.
- [ ] Dire que `prefetch_count=50` limite 50 messages livrés non acquittés par consumer, pas 50 ACK.
- [ ] Ne pas présenter le prefetch comme la capacité globale de RabbitMQ ni comme une hausse automatique du débit.
- [ ] Définir la DLQ comme une quarantaine pour erreurs permanentes, pas comme une sauvegarde générale en cas de panne.
- [ ] Ne jamais dire que Docker Compose garantit la haute disponibilité ou que `restart` suffit.
- [ ] Définir la latency comme le délai entre `collected_at` et le stockage, pas comme une simple latence réseau.
- [ ] Citer RabbitMQ mono-nœud, MySQL mono-nœud et la machine Docker locale comme SPOF.
- [ ] Présenter une limite dans chaque réponse difficile.

### Prochaine séance après la pause

1. Faire une simulation PowerPoint slide par slide, debout et chronométrée.
2. Noter trois erreurs maximum et corriger uniquement ces trois passages.
3. Faire la démo réelle plus tard, avec son plan B.
4. En soirée, faire un jury mixte incluant les notions rouges.
5. Demain matin, vérifier par rappel différé : DLQ, prefetch, back-pressure,
   throughput/latency, SPOF, panne MySQL et parcours avec les queues `_v3`.
6. Ne pas ajouter une nouvelle séance théorique complète ce soir.
