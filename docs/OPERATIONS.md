# Exploitation locale

## Sauvegarder avant une mise à niveau

Arrêter les producteurs/consommateurs avant la sauvegarde pour obtenir un état cohérent.
Sauvegarder MySQL, le volume Grafana et la configuration RabbitMQ. Conserver `.env` dans
un gestionnaire de secrets. Les dumps contiennent des données privées : ne pas les versionner.
Pour éviter les redirections PowerShell qui peuvent changer l’encodage, créer le dump
dans le conteneur puis le copier :

```powershell
docker stop scrap
# Arrêter aussi les instances Analytics et queue du projet via Docker Desktop.
docker exec mysql sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysqldump -uroot --single-transaction --routines --triggers "$MYSQL_DATABASE" > /tmp/cryptoviz-backup.sql'
docker cp mysql:/tmp/cryptoviz-backup.sql ./cryptoviz-backup.sql
docker stop grafana
docker cp grafana:/var/lib/grafana ./grafana-backup
```

Tester une restauration dans une pile isolée avant toute migration importante. Ne pas
réutiliser directement un volume Grafana migré avec une version plus ancienne : restaurer
la sauvegarde. Pour MySQL, importer le dump sur une base isolée avec le client MySQL.

## Mettre à niveau une installation existante

Les variables d’initialisation MySQL, RabbitMQ et Grafana ne modifient pas les comptes
déjà stockés dans leurs volumes. Ne pas supprimer les volumes pour résoudre un problème
 de mot de passe.

1. Sauvegarder comme indiqué ci-dessus. Conserver les secrets MySQL existants dans `.env`.
2. Générer deux secrets distincts avec `python -c "import secrets; print(secrets.token_hex(24))"`.
   Ajouter `GRAFANA_DB_PASSWORD` et `RABBITMQ_PASSWORD` dans `.env`, puis
   `RABBITMQ_USER=cryptoviz`. Vider l’ancien `RABBITMQ_URL` utilisant `guest`.
3. Créer le compte RabbitMQ avec `docker exec rabbitmq rabbitmqctl add_user cryptoviz <secret>`.
   S’il existe, utiliser `change_password` à la place de `add_user`. Accorder les permissions :
   `docker exec rabbitmq rabbitmqctl set_permissions -p / cryptoviz ".*" ".*" ".*"`.
   Pour l’interface de gestion : `docker exec rabbitmq rabbitmqctl set_user_tags cryptoviz management`.
4. Copier le script SQL de provisionnement :
   `docker cp script/init-grafana-user.sh mysql:/tmp/init-grafana-user.sh`.
   Exécuter `docker exec -e GRAFANA_DB_PASSWORD=<secret-hexadecimal> mysql sh /tmp/init-grafana-user.sh`.
   Le script utilise les identifiants root et le nom de base déjà présents dans le conteneur.
5. Vérifier `docker compose config --quiet`, puis `docker compose up -d --build --wait`.
6. Vérifier les logs, le dashboard et le test d’intégration décrit dans le README.
   Une fois tous les clients migrés, supprimer l’ancien compte `guest` :
   `docker exec rabbitmq rabbitmqctl delete_user guest`.

Remplacer les marqueurs `<secret>` par les valeurs locales, sans les publier. Attention
à l’historique du terminal et à la liste des processus lorsque des secrets sont fournis
sur la ligne de commande. En environnement partagé, utiliser un gestionnaire de secrets.
Le durcissement du dépôt ne met pas automatiquement à niveau une pile déjà démarrée.

## Mot de passe Grafana oublié

L’identifiant initial est `admin`. La valeur `.env` est seulement utilisée à la première
initialisation. Pour un compte existant, utiliser la CLI et saisir le nouveau mot de passe
sur l’entrée standard :

```bash
docker compose exec grafana grafana cli --homepath /usr/share/grafana admin reset-admin-password --password-from-stdin
```

Conserver ensuite le nouveau secret dans le gestionnaire de mots de passe. Ne pas activer
l’accès anonyme pour contourner un problème de connexion.

## Diagnostic

- `docker compose ps` : état des services. « Running » seul ne prouve pas le traitement.
- `docker compose logs --tail 100 scrap analytics queue clean` : collecte, reconnexions, rejets.
- RabbitMQ : surveiller les messages prêts, non acquittés et les deux `.dlq`.
- MySQL : vérifier que `pipeline_hourly` évolue sur une période récente.
- Grafana : vérifier la période, la santé de la datasource et les permissions `SELECT`.

Un message invalide est conservé en DLQ ; corriger sa cause avant un rejeu contrôlé.
Une panne SQL provoque une nouvelle livraison avec une pause de cinq secondes. Les erreurs
inattendues arrêtent le worker, que Docker redémarre. Les DLQ et agrégats n’ont pas de
rétention automatique : surveiller leur volume et définir une politique avant la production.

## Versions et exposition

Le Compose fourni utilise Grafana 13.2.1. Les images de base Python, MySQL et RabbitMQ
restent des tags de branche, donc leur contenu peut évoluer : utiliser des digests validés
pour une livraison de production, avec une politique de renouvellement de ces digests.
Revoir les [avis Grafana](https://grafana.com/security/security-advisories/) et les versions
publiées ; la CI `pip-audit` couvre les paquets Python, pas tous les paquets système des images.
