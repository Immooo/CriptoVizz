# Préparation à la soutenance Crypto Viz

Échéance : jeudi 10 septembre 2026 après-midi  
Durée maximale : 30 minutes  
Cible : 20 à 24 minutes, démonstration comprise

## Méthode de travail

La préparation repose d'abord sur la récupération active : fermer les notes,
dessiner, expliquer, puis vérifier. Les tests de mémoire améliorent la rétention
différée davantage que la simple relecture dans les expériences de Roediger et
Karpicke. La pratique espacée bénéficie d'une large synthèse quantitative et le
sommeil participe à la consolidation de la mémoire.

Règle pour chaque bloc : 5 minutes de lecture au maximum, restitution sans notes,
correction ciblée, puis nouvelle restitution dans un contexte différent.

Sources :

- [Roediger et Karpicke, 2006 - testing effect](https://doi.org/10.1111/j.1467-9280.2006.01693.x)
- [Cepeda et al., 2006 - distributed practice](https://pubmed.ncbi.nlm.nih.gov/16719566/)
- [Dunlosky et al., 2013 - learning techniques](https://www.psychologicalscience.org/journals/pspi/1529100612453266/)
- [Rasch et Born, 2013 - sleep and memory](https://pmc.ncbi.nlm.nih.gov/articles/PMC3768102/)

## Architecture réelle en une phrase

Deux flux RSS sont lus chaque minute par un producteur Python. Les articles
normalisés passent par `raw_news`, sont enrichis en continu par le service
Analytics, passent par `enriched_news`, puis un worker les déduplique, les stocke
et met à jour des agrégats horaires dans MySQL. Grafana relit ces données toutes
les 30 secondes.

```text
CoinDesk + Cointelegraph
        ↓ JSON brut normalisé
Scraper Python
        ↓ raw_news
RabbitMQ
        ↓
Analytics Builder
        ↓ enriched_news, JSON enrichi
RabbitMQ
        ↓
Storage Worker
        ↓ INSERT idempotent + agrégations incrémentales
MySQL
        ↓ requêtes temporelles
Grafana
```

## Les 15 notions à maîtriser

### Niveau 1 - indispensable

1. **Pipeline de données** : chaîne de composants qui transporte et transforme
   les événements. Ici, chaque article suit le parcours RSS vers Grafana.
2. **Producteur et consommateur** : le scraper produit, Analytics consomme puis
   reproduit, Storage consomme. Ce découplage évite les appels directs entre services.
3. **RabbitMQ et queues** : broker qui tamponne les événements dans `raw_news` et
   `enriched_news`, avec leurs DLQ associées. L'exchange utilisé est l'exchange
   direct par défaut.
4. **ACK** : confirmation envoyée après réussite. Avant l'ACK, un crash peut provoquer
   une nouvelle livraison. Le système vise donc une livraison au moins une fois.
5. **Idempotence et déduplication** : SHA-256 de l'URL comme `article_id`, clé primaire
   et `INSERT ... ON DUPLICATE KEY UPDATE`. Rejouer un article ne crée pas une seconde ligne ni un second agrégat.
6. **Analytics Builder** : score lexical entre -1 et 1, label de sentiment et thèmes.
   Méthode rapide et explicable, mais limitée face au sarcasme et au contexte.
7. **Agrégations temporelles** : compteurs horaires mis à jour lors de chaque nouvel
   article. Grafana interroge de petites tables plutôt que recalculer tout l'historique.
8. **Grafana** : datasource et dashboard provisionnés depuis Git, filtre temporel,
   filtre par thème et rafraîchissement toutes les 30 secondes.

### Niveau 2 - important

9. **Persistance RabbitMQ** : queues durables et messages persistants réduisent le
   risque de perte lors d'un redémarrage, sans constituer seuls une garantie absolue.
10. **Back-pressure** : la queue absorbe un écart temporaire de débit et `basic_qos`
    limite à 50 les messages non acquittés par worker.
11. **Scaling horizontal** : plusieurs replicas Analytics peuvent partager `raw_news`.
    RabbitMQ répartit les messages entre consommateurs concurrents.
12. **MySQL et indexes** : clé primaire pour la déduplication, indexes temporels et par
    source pour accélérer les requêtes usuelles. MySQL convient au volume de la démo.
13. **Docker Compose** : décrit services, variables, dépendances, réseaux et volumes.
    Chaque composant reste isolé et reproductible.
14. **Healthchecks, reconnexion et panne** : Compose attend MySQL et RabbitMQ. Les
    workers retentent leurs connexions. Un échec transitoire provoque un NACK avec
    requeue ; un message invalide est conservé dans une dead-letter queue.

### Niveau 3 - bonus

15. **Throughput, latency et Big Data** : throughput = articles traités par unité de
    temps. Latency = délai collecte-stockage. La démo a un petit volume, mais applique
    streaming, découplage, back-pressure, traitement incrémental et observabilité.

## Limites à reconnaître

- RabbitMQ et MySQL sont chacun un point de défaillance unique dans Compose.
- Le sentiment lexical ne comprend pas le contexte complexe.
- Deux sources RSS donnent peu de variété et un volume de démonstration.
- Les dead-letter queues conservent les messages invalides, mais leur rejeu reste
  une opération manuelle et il n'existe pas de réplication multi-nœuds.
- `restart` améliore la reprise, mais ne remplace pas une orchestration haute disponibilité.
- La mesure de latence commence à `collected_at`, pas à la publication chez l'éditeur.

Formulation crédible : « Le volume de la démonstration est volontairement limité.
L'architecture reprend toutefois des principes de pipelines Big Data et prépare une
montée en charge mesurable. »

Preuve de scaling horizontal : `docker compose up --build --scale analytics=3`
lance trois consommateurs concurrents sur `raw_news`. RabbitMQ distribue les
messages entre eux et le prefetch évite qu'un seul worker réserve tout le backlog.

## Planning du lundi 7 au jeudi 10 septembre

### Lundi - architecture et parcours des données

| Durée | Objectif | Méthode et exercice | Production sans notes |
|---|---|---|---|
| 09:00-09:45 | Vue globale | Dessin de mémoire, puis comparaison au code | Architecture complète en 90 s |
| 10:00-10:45 | Scraper et messages | Expliquer un JSON brut, retrouver chaque champ | Parcours RSS vers `raw_news` |
| 11:00-11:45 | RabbitMQ | Questions ACK, durable, persistant, panne | Expliquer un crash avant/après ACK |
| 14:00-14:45 | Analytics | Prédire thème et sentiment de 5 titres | Entrée, calcul, sortie enrichie |
| 15:00-15:45 | Storage et MySQL | Refaire le schéma sur papier | Déduplication et agrégation |
| 16:00-16:30 | Rappel espacé | 15 questions mélangées | 12 réponses correctes minimum |

### Mardi - composants et décisions

| Durée | Objectif | Méthode et exercice | Production sans notes |
|---|---|---|---|
| 09:00-09:30 | Réactivation lundi | Page blanche, aucune lecture préalable | Schéma et 8 notions |
| 09:45-10:30 | Docker Compose | Associer services, réseaux, volumes, healthchecks | Expliquer le démarrage |
| 10:45-11:30 | Fiabilité | Simuler cinq pannes | Réaction et perte possible |
| 14:00-14:45 | Choix techniques | RabbitMQ/Kafka, MySQL/MongoDB | Réponses de 30 s |
| 15:00-15:45 | Code réel | Retrouver les lignes qui prouvent chaque choix | 10 preuves code-config |
| 16:00-16:45 | Interleaving | Questions mélangées architecture et panne | 80 % sans notes |

### Mercredi - Big Data et répétition

| Durée | Objectif | Méthode et exercice | Production sans notes |
|---|---|---|---|
| 09:00-09:30 | Réactivation | Dessin et explication chronométrée | Architecture en 2 min |
| 09:45-10:30 | 4V et scalabilité | Relier chaque notion à une preuve | Discours Big Data honnête |
| 10:45-11:30 | Questions difficiles | Jury sceptique, réponses de 20-40 s | 10 réponses solides |
| 14:00-14:45 | PowerPoint | Présentation slides 1 à 8 | Moins de 13 min |
| 15:00-15:45 | Démo et incidents | Démo réelle, puis scénario sans réseau | Démo et plan B en 4 min |
| 16:00-16:45 | Simulation complète | Soutenance sans interruption ni notes | 20-24 min |
| 17:00-17:20 | Correction | Reprendre seulement les points faibles | 3 corrections reformulées |

### Jeudi matin - consolidation

| Durée | Objectif | Méthode et exercice | Production sans notes |
|---|---|---|---|
| 09:00-09:25 | Rappel léger | Architecture et 10 mots-clés | Schéma exact |
| 09:40-10:25 | Dernière simulation | Présentation complète chronométrée | Moins de 24 min |
| 10:40-11:10 | Questions faibles | Rappel espacé ciblé | Réponses courtes et exactes |
| 11:15-11:35 | Vérification technique | Script de démo et plan B | Checklist validée |

### Trente minutes avant

Respirer, boire, vérifier l'écran et ouvrir les onglets. Relire seulement : chaîne
du pipeline, trois choix techniques, trois limites, phrase Big Data et conclusion.
Aucun nouveau concept.

## Storyboard et chronométrage

| # | Slide | Durée | Idée principale | Transition |
|---|---|---:|---|---|
| 1 | Crypto Viz | 0:40 | Le projet et sa mission | Partir du besoin métier |
| 2 | Problème | 1:20 | Transformer un flux continu en indicateurs | Traduire en objectifs |
| 3 | Objectifs | 1:10 | Collecter, analyser, visualiser | Montrer la chaîne complète |
| 4 | Architecture | 2:00 | Parcours et découplage | Entrer par la source |
| 5 | Ingestion | 1:30 | Normalisation et production continue | Pourquoi intercaler un broker |
| 6 | RabbitMQ | 2:00 | Files, ACK et back-pressure | Consommer le flux brut |
| 7 | Analytics | 1:40 | Enrichissement explicable | Rendre les résultats persistants |
| 8 | MySQL | 1:50 | Déduplication et agrégations | Exploiter les tables |
| 9 | Grafana | 1:30 | Vue dynamique et temporelle | Mesurer le pipeline lui-même |
| 10 | Big Data | 2:00 | Principes crédibles et limite de volume | Examiner la robustesse |
| 11 | Résilience | 1:40 | Reprise, SPOF et limites | Passer aux preuves visibles |
| 12 | Démonstration | 3:30 | Services, données, dashboard | Tirer le bilan |
| 13 | Évolutions | 1:20 | Priorités réalistes de montée en charge | Conclure sur la valeur |
| 14 | Conclusion | 0:50 | Pipeline utile, mesurable et extensible | Questions du jury |

Total cible : environ 23 minutes.

Version d'urgence 15 minutes : slide 1 en 20 s, fusion orale des slides 2-3,
architecture en 90 s, slides 5-8 en 4 min, slide 9 en 45 s, slide 10 en 90 s,
sauter la slide 11, démo limitée au dashboard pendant 2 min, slide 13 en 30 s et
conclusion en 30 s.

## Démonstration en 3 à 5 minutes

1. `docker compose ps` : montrer neuf conteneurs actifs pour sept services, dont trois replicas Analytics.
2. RabbitMQ Management : montrer `raw_news`, `enriched_news`, leurs deux DLQ et leurs consumers.
3. MySQL : montrer le nombre d'articles, les sources et `pipeline_hourly`.
4. Grafana : changer la période, le thème et commenter débit puis latence.

Plan B : conserver des captures du dashboard et la sortie de trois commandes. Si
Internet tombe, expliquer que les articles déjà stockés restent consultables. Si un
service tombe, montrer sa responsabilité sur le diagramme, expliquer la reconnexion
et préciser honnêtement ce que le système ne garantit pas.

## Banque de 45 questions du jury

1. Quel problème résout Crypto Viz ?
2. Décris le parcours complet d'un article.
3. Qu'est-ce qu'un producteur ?
4. Qu'est-ce qu'un consommateur ?
5. Pourquoi utiliser RabbitMQ ?
6. Quelles queues existent ?
7. Utilisez-vous un exchange ?
8. Qu'est-ce qu'un ACK ?
9. Pourquoi `auto_ack=False` ?
10. Une queue durable suffit-elle à éviter toute perte ?
11. À quoi sert un message persistant ?
12. Que se passe-t-il si Analytics crash avant l'ACK ?
13. Et après publication mais avant l'ACK ?
14. Peut-on traiter un article deux fois ?
15. Comment la déduplication fonctionne-t-elle ?
16. Pourquoi le SHA-256 de l'URL ?
17. Qu'est-ce que l'idempotence ?
18. Où se situe le back-pressure ?
19. À quoi sert `prefetch_count` ?
20. Comment scaler Analytics ?
21. Pourquoi RabbitMQ plutôt que Kafka ?
22. À partir de quel besoin Kafka deviendrait pertinent ?
23. Comment calculez-vous le sentiment ?
24. Quelle est la limite de cette méthode ?
25. Comment détectez-vous les thèmes ?
26. Pourquoi produire un second message ?
27. Pourquoi MySQL ?
28. Pourquoi pas MongoDB ?
29. Quels indexes avez-vous créés ?
30. Pourquoi précalculer des agrégations horaires ?
31. Comment évitez-vous de doubler les agrégats ?
32. Que se passe-t-il si MySQL tombe ?
33. Qu'est-ce que le throughput ?
34. Qu'est-ce que la latency ?
35. D'où part votre mesure de latence ?
36. Pourquoi Grafana ?
37. Qu'est-ce que le provisioning ?
38. Pourquoi un rafraîchissement de 30 secondes ?
39. Pourquoi Docker Compose ?
40. À quoi servent les réseaux Docker ?
41. À quoi servent les volumes ?
42. Que garantissent les healthchecks ?
43. Quels sont les points uniques de défaillance ?
44. Le projet est-il vraiment Big Data ?
45. Que changer pour dix millions d'articles par jour ?

Réponses pivots, 20 à 40 secondes :

- **RabbitMQ ou Kafka** : RabbitMQ répond bien à notre besoin de distribution de
  tâches, d'ACK et de files simples. Kafka serait préférable pour un journal durable,
  rejouable, distribué et à très haut débit. Pour deux RSS, Kafka alourdirait la démo.
- **Crash après INSERT avant ACK** : RabbitMQ peut redélivrer le message. La clé
  primaire et `INSERT ... ON DUPLICATE KEY UPDATE` rendent le stockage idempotent, donc les agrégats ne
  sont pas incrémentés deux fois.
- **Projet Big Data** : le dataset de démonstration reste petit. L'orientation Big
  Data vient de l'ingestion continue, du découplage, de la gestion de pression, du
  traitement incrémental, du scaling des workers et de l'observabilité.
- **Dix millions par jour** : partitionnement du flux, Kafka ou RabbitMQ en cluster,
  workers orchestrés, stockage distribué ou analytique en colonnes, DLQ, métriques
  centralisées et tests de charge avant tout choix définitif.

## Fiches finales

### Architecture

`RSS > scraper > raw_news > analytics > enriched_news > storage > MySQL > Grafana`
JSON, queues durables, ACK après succès, identifiant déterministe, agrégats horaires.

### RabbitMQ

Broker, découplage, tampon, durable queue, persistent message, manual ACK,
NACK/requeue, prefetch 50, consommateurs concurrents, livraison au moins une fois.
Le prefetch limite à 50 les messages livrés mais non acquittés par consumer : ce
n'est ni 50 ACK, ni la capacité globale du broker, ni un gain automatique de débit.
Une DLQ met en quarantaine les messages invalides ou en erreur permanente ; elle
n'est pas une sauvegarde générale et exige diagnostic puis rejeu contrôlé.

### Docker

7 services, 9 conteneurs avec trois replicas Analytics, 2 réseaux, 3 volumes nommés, `depends_on`,
healthchecks MySQL/RabbitMQ, variables `.env`, restart policies. Compose facilite
le déploiement et la reprise, mais ne garantit pas la haute disponibilité.

### MySQL et Grafana

`news_articles`, `analytics_hourly`, `pipeline_hourly`. PK SHA-256, indexes temps et
source. Grafana provisionné, 6 panneaux, filtre période/thème, refresh 30 s.

### Big Data

Velocity : continu. Variety : deux sources. Volume : faible en démo. Veracity :
normalisation et déduplication. Streaming, back-pressure, incrémental, throughput,
latency, scalabilité horizontale. Ne pas exagérer le volume.

### Questions pièges

Durable ≠ zéro perte. ACK ≠ exactement une fois. Docker Compose ≠ haute disponibilité.
Deux RSS ≠ variété massive. Sentiment lexical ≠ compréhension linguistique.
RabbitMQ seul ≠ architecture distribuée hautement disponible.

### Déroulement PowerPoint

Besoin, objectifs, architecture, ingestion, RabbitMQ, analytics, stockage, Grafana,
Big Data, résilience, démo, évolutions, conclusion. Regarder le jury, pas l'écran.

### Démonstration

Services, queues, données, dashboard. Garder captures et sorties de commandes.
Toujours expliquer ce que l'échec démontre sur le rôle du composant.

### Trente minutes avant

Pipeline. ACK. Idempotence. Agrégats. Back-pressure. Throughput/latency. Trois limites.
Phrase Big Data honnête. Conclusion. Respirer. Aucun nouvel apprentissage.

## Première séance active

Ferme maintenant ce document et réponds sans regarder :

**Un article vient d'être publié par CoinDesk. Explique tout son parcours jusqu'au
dashboard Grafana, en indiquant les deux formats de message, les deux ACK possibles,
le mécanisme anti-doublon et ce qui se passe si Storage crash après l'INSERT mais
avant l'ACK.**

## Diagnostic après la séance du 09/09/2026, 14 h 45–16 h 13

Deux blocs ont été travaillés : architecture/RabbitMQ/fiabilité, puis Big Data,
scalabilité et limites. Les bonnes réponses obtenues une seule fois restent à
confirmer par rappel différé le 10 septembre.

### Plutôt solides, à confirmer demain

- rôle de RabbitMQ, découplage et attente pendant une indisponibilité d'Analytics ;
- queue durable, message persistent, ACK manuel et erreur temporaire/permanente ;
- scaling horizontal d'Analytics et absence de `container_name` fixe ;
- 4V expliqués honnêtement, RabbitMQ face à Kafka et limites du scaling isolé ;
- sentiment lexical, ses avantages et ses limites ;
- intérêt conjoint du throughput et de la latency.

### Priorités de rappel différé

1. DLQ et distinction erreur temporaire/permanente.
2. `prefetch_count=50`, back-pressure et absence de gain automatique de throughput.
3. Publication dans `enriched_news` puis crash avant ACK : redelivery et doublon possible.
4. Idempotence : SHA-256 de l'URL, clé primaire, `INSERT ... ON DUPLICATE KEY UPDATE` et agrégats conditionnels.
5. Throughput, latency entre `collected_at` et stockage, backlog et recherche du vrai goulot.
6. SPOF : RabbitMQ mono-nœud, MySQL mono-nœud et machine Docker locale.
7. Panne MySQL : échec d'écriture, absence d'ACK, NACK/requeue, reconnexion et backlog.
8. MySQL face à MongoDB : structure, unicité, agrégations temporelles et SQL pour Grafana.
9. Parcours complet avec `raw_news`, `enriched_news` et le terme message JSON.

### Suite du 09/09/2026

Après une vraie pause : simulation PowerPoint slide par slide et chronométrée,
correction de trois erreurs maximum, démo réelle plus tard, puis jury mixte en
soirée. Ne pas ajouter une nouvelle séance théorique complète.
