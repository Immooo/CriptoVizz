# Crypto Viz - Rapport d'architecture et de choix techniques

## 1. Objectif du projet

Crypto Viz transforme en continu des actualités issues de flux RSS consacrés aux
cryptomonnaies en indicateurs lisibles. L'application collecte les articles, les
normalise, calcule un sentiment et des thèmes, conserve les résultats, puis expose
leur évolution temporelle dans Grafana.

Le projet répond aux trois fonctions demandées :

1. un scraper en ligne collecte continuellement les actualités ;
2. un composant Analytics consomme les données, les enrichit et republie le résultat ;
3. un viewer dynamique affiche les analyses et permet de choisir une période.

Le déploiement cible est local et reproductible avec Docker Compose. Le volume de
la démonstration reste modeste ; le projet illustre surtout les principes d'un
pipeline de données en continu.

## 2. Architecture générale

```text
CoinDesk + Cointelegraph
          |
          v
Scraper Python -- JSON brut --> RabbitMQ / RAW_NEWS_QUEUE
                                      |
                                      v
                              Analytics Builder
                                      |
                              JSON enrichi
                                      v
                         RabbitMQ / ANALYTICS_QUEUE
                                      |
                                      v
                              Storage Worker
                                      |
                     articles + agrégats horaires
                                      v
                                    MySQL
                                      |
                                      v
                                   Grafana
```

Les noms physiques des files sont configurables. Avec le fichier
`.env.example`, `RAW_NEWS_QUEUE` vaut `raw_news` et `ANALYTICS_QUEUE` vaut
`enriched_news`.

### 2.1 Scraper

Le scraper interroge les flux RSS toutes les 60 secondes par défaut. Il retient
les champs utiles, limite leur taille et convertit les dates en UTC. L'identifiant
d'un article est le SHA-256 de son URL. Il publie ensuite un message JSON persistant
dans la file brute.

Exemple de message brut :

```json
{
  "article_id": "sha256-de-url",
  "source": "CoinDesk",
  "title": "Titre de l'article",
  "summary": "Résumé RSS",
  "url": "https://...",
  "published_at": "2026-09-09T12:00:00+00:00",
  "collected_at": "2026-09-09T12:03:00+00:00"
}
```

### 2.2 Analytics Builder

Analytics est à la fois consommateur et producteur. Il consomme la file brute,
calcule un score lexical compris entre -1 et 1, attribue un label positif, neutre
ou négatif, puis détecte un ou plusieurs thèmes. Il publie le message enrichi dans
la seconde file avant d'acquitter le message brut.

Ce traitement est volontairement simple, rapide et explicable. Il ne comprend pas
finement la négation, le contexte ou le sarcasme et ne doit pas être présenté comme
un modèle d'intelligence artificielle validé scientifiquement.

### 2.3 Storage Worker et MySQL

Storage consomme les messages enrichis et effectue, dans une même transaction :

- l'insertion de l'article dans `news_articles` ;
- la mise à jour des agrégats de contenu dans `analytics_hourly` ;
- la mise à jour des mesures du pipeline dans `pipeline_hourly`.

La clé primaire `article_id` et `INSERT IGNORE` rendent l'écriture idempotente :
une redelivery d'un article déjà présent ne modifie pas une seconde fois les
agrégats. Les tendances de contenu sont regroupées selon `published_at`. Les
mesures d'ingestion sont regroupées selon `collected_at`, afin qu'un article ancien
collecté aujourd'hui soit bien compté dans l'activité d'aujourd'hui.

### 2.4 Viewer Grafana

Grafana interroge MySQL directement. La datasource et le dashboard sont
provisionnés depuis les fichiers Git, ce qui rend la visualisation reproductible.
Le dashboard se rafraîchit toutes les 30 secondes et propose un filtre temporel et
un filtre par thème.

Les panneaux montrent :

- le volume par thème ;
- le sentiment moyen au fil du temps ;
- la distribution des labels de sentiment ;
- les derniers articles analysés ;
- le débit d'ingestion par source ;
- la latence moyenne du pipeline par source.

La distribution du sentiment est calculée depuis `news_articles`. Chaque article
est ainsi compté une seule fois lorsque tous les thèmes sont sélectionnés. Le débit
d'ingestion utilise `collected_at` et représente donc l'heure d'entrée dans le
pipeline, pas l'heure de publication chez l'éditeur.

## 3. Choix techniques

### RabbitMQ

RabbitMQ correspond au besoin d'une file de travail avec consommateurs concurrents,
ACK individuels et routage des messages invalides. Il découple le rythme du scraper,
d'Analytics et de Storage. Une file absorbe temporairement un écart de débit entre
producteurs et consommateurs.

Les files sont durables, les messages sont persistants et les ACK sont manuels.
`prefetch_count` limite le nombre de messages non acquittés réservés par chaque
worker. Ces mécanismes permettent une livraison au moins une fois ; ils ne
garantissent pas une exécution exactement une fois.

Kafka serait plus adapté à un journal distribué conservé longtemps, rejouable par
plusieurs groupes indépendants et soumis à un débit très élevé. Pour deux flux RSS
et un déploiement local, RabbitMQ offre un compromis plus simple et cohérent.

### MySQL

MySQL fournit transactions, contraintes et index, qui sont utiles pour garantir
l'idempotence et servir les requêtes Grafana. Les agrégats horaires évitent de
recalculer tout l'historique pour chaque affichage. Pour un volume industriel, il
faudrait mesurer les limites d'écriture puis envisager partitionnement, écriture
par lots ou stockage analytique distribué.

### Grafana

Grafana fournit rapidement des séries temporelles, des filtres et un rafraîchissement
automatique. Son provisioning versionne le dashboard et la datasource avec le code.
Il répond donc directement au besoin de viewer dynamique sans imposer le développement
d'une interface web spécifique.

### Docker Compose

Docker Compose décrit sept services : MySQL, RabbitMQ, Scraper, Analytics, Storage,
Clean et Grafana. Les images, variables d'environnement, volumes, réseaux,
dépendances et healthchecks sont déclaratifs. Analytics peut être lancé avec trois
réplicas pour montrer le principe des consommateurs concurrents.

## 4. Fiabilité et comportement en cas de panne

- Analytics acquitte un message brut seulement après la publication de sa version
  enrichie.
- Storage acquitte un message seulement après la transaction MySQL.
- Une erreur temporaire provoque un NACK avec remise en file.
- Un message invalide est rejeté vers une dead-letter queue.
- Les volumes Docker conservent les données de MySQL, RabbitMQ et Grafana.
- La clé primaire évite le double comptage après une redelivery côté Storage.

Les limites sont connues : RabbitMQ et MySQL sont des points uniques de défaillance
dans ce déploiement, les retries ne sont pas bornés, et la persistance locale ne
remplace pas une architecture répliquée.

## 5. Scalabilité et positionnement Big Data

La démonstration ne possède pas un volume massif. Son intérêt Big Data vient des
principes mis en œuvre : ingestion continue, événements asynchrones, découplage,
back-pressure, traitement incrémental, agrégats temporels, mesure du débit et
possibilité de multiplier les workers Analytics.

Le passage à plusieurs millions d'articles par jour demanderait d'abord un test de
charge pour identifier le goulot. Les évolutions probables seraient un broker
clusterisé et partitionné, des workers orchestrés, des écritures par lots, un
stockage analytique partitionné et une observabilité centralisée.

## 6. Déploiement et démonstration

```bash
cp .env.example .env
docker compose up --build
```

Grafana est disponible sur `http://localhost:3000` et l'interface RabbitMQ sur
`http://localhost:15672`.

Pour démontrer trois consommateurs Analytics concurrents :

```bash
docker compose up --build --scale analytics=3
```

Une démonstration courte doit montrer l'état des conteneurs, les deux files
principales, les deux DLQ et leurs consommateurs, quelques lignes MySQL, puis le dashboard avec un changement
de période. Le commentaire doit porter sur un résultat visible : nombre d'articles,
thème dominant, sentiment ou activité d'ingestion.

## 7. Limites et améliorations prioritaires

1. Évaluer le score de sentiment sur un jeu d'articles annotés.
2. Étendre les tests d'intégration aux pannes et aux reconnexions des services.
3. Borner les retries et ajouter un délai progressif avant la DLQ.
4. Conserver les identifiants de déduplication au-delà du nettoyage des articles.
5. Mesurer le débit avec un et trois workers avant d'affirmer un gain de performance.
6. Ajouter des sources et des tests de qualité de données.

## 8. Conclusion

Crypto Viz livre une chaîne complète et exécutable, de la collecte à la
visualisation. Son architecture respecte le paradigme producteur/consommateur et
intègre plusieurs mécanismes de fiabilité utiles. Le projet doit être présenté
comme un prototype de pipeline de données en continu : il démontre une architecture
extensible, tout en assumant un volume local et une analyse lexicale limités.
