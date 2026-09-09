# Démonstration Crypto Viz - 4 minutes

## Avant de commencer

Depuis la racine du projet :

```powershell
docker compose up -d --scale analytics=3
./script/demo-check.ps1
```

Ouvrir avant le passage :

- le PowerPoint `output/presentation/crypto-viz-soutenance-p1-final.pptx` ;
- Grafana sur `http://localhost:3000/d/crypto-news-analytics/crypto-news-analytics` ;
- RabbitMQ sur `http://localhost:15672` ;
- un terminal placé à la racine du projet.

## Déroulement chronométré

### 0:00 à 0:40 - Services

Lancer `docker compose ps` ou montrer la première partie de `demo-check.ps1`.

Phrase à dire :

> Sept services composent l'application. Analytics possède trois replicas, ce qui
> donne neuf conteneurs actifs. MySQL et RabbitMQ sont déclarés sains.

Ne pas énumérer toutes les colonnes. Montrer simplement les services actifs et les
trois lignes Analytics.

### 0:40 à 1:30 - RabbitMQ

Montrer les quatre queues : `raw_news`, `enriched_news`, `raw_news.dlq` et
`enriched_news.dlq`. Montrer les trois consumers de `raw_news` et le consumer de
`enriched_news`.

Phrase à dire :

> Le scraper produit dans raw_news. Trois workers Analytics se partagent cette
> queue, enrichissent les messages et produisent dans enriched_news. Storage
> acquitte après la transaction MySQL. Les messages invalides rejoignent les DLQ.

Une queue vide est un bon résultat : les consommateurs suivent le débit. Elle ne
prouve cependant pas à elle seule la performance maximale du pipeline.

### 1:30 à 2:20 - Données

Utiliser les compteurs affichés par `demo-check.ps1`.

Phrase à dire :

> L'identifiant SHA-256 de l'URL devient la clé primaire. Une redelivery retrouve
> donc l'article existant et n'incrémente pas une seconde fois les agrégats. Les
> compteurs de sentiment affichés ici proviennent des articles uniques.

### 2:20 à 3:40 - Grafana

Afficher le dashboard, changer la période, puis commenter deux panneaux :

1. la distribution du sentiment ou le volume par thème ;
2. le débit d'ingestion par source.

Phrase à dire :

> Les tendances éditoriales suivent published_at. Le débit d'ingestion suit
> collected_at, l'heure d'entrée dans notre pipeline. Le dashboard se rafraîchit
> toutes les 30 secondes.

Éviter de commenter tous les panneaux. Lire un résultat réel et expliquer sa
signification.

### 3:40 à 4:00 - Conclusion

> La démonstration prouve une chaîne continue, découplée et observable. Le volume
> local reste limité ; le test de charge déterminera le prochain goulot avant tout
> changement d'architecture.

## Plan de secours

- Si Internet ne fournit aucun nouvel article, utiliser les données déjà stockées.
- Si RabbitMQ Management ne s'ouvre pas, montrer la capture de la slide 12 et la
  sortie de `demo-check.ps1`.
- Si Grafana ne s'ouvre pas, rester sur la slide 9 et expliquer les six panneaux.
- Si Docker est indisponible, poursuivre avec les slides 4, 11 et 12 sans tenter une
  réparation en direct.

Le plan de secours doit conserver l'explication du parcours des données. Une panne
pendant la démonstration ne justifie pas de modifier le code devant le jury.

## Vérification de l'idempotence et des DLQ

À exécuter avant la soutenance, pas pendant les quatre minutes de démonstration :

```powershell
docker compose cp tests/integration_pipeline.py queue:/tmp/integration_pipeline.py
docker compose exec -T queue python /tmp/integration_pipeline.py
```

Le test ajoute puis retire un article synthétique. Il vérifie qu'une seconde
livraison ne double ni l'article ni les agrégats. Il envoie ensuite un message JSON
invalide dans chaque queue principale et vérifie son arrivée dans la DLQ associée.
