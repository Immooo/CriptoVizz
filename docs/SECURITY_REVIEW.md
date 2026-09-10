# Revue de sécurité et de robustesse — 10 septembre 2026

## Périmètre

Revue des services Python, du Compose, du SQL, du provisioning Grafana, des tests,
de la documentation et de la présence de `.env` dans l’historique Git. L’objectif est
un projet local maintenable. Ce travail n’est ni un pentest externe, ni une certification
« sans faille », ni un audit exhaustif de tout l’historique et des paquets système.

## Constats et corrections

| Priorité | Constat | Correction / statut |
| --- | --- | --- |
| Haute | Ancien `.env` publié dans le commit initial `362fb86f` | Plus suivi aujourd’hui ; mots de passe historiques différents des valeurs locales actuelles. Remplacer ces anciens secrets partout où ils auraient été réutilisés. Historique conservé. |
| Haute | Ports MySQL, RabbitMQ et Grafana ouverts sur toutes les interfaces | Publication limitée à `127.0.0.1`. |
| Haute | Grafana accédait à MySQL avec le compte d’écriture | Compte `grafana_reader` limité à `SELECT`, script pour volumes neufs et migration documentée. |
| Haute | Mots de passe d’exemple et compte RabbitMQ `guest` | Génération de secrets aléatoires, compte broker dédié, secrets requis par Compose. Les comptes existants nécessitent une migration. |
| Haute | Grafana 12.1.0 ancien et concerné par des avis de sécurité | Passage à 13.2.1 ; mise à jour des dépendances Python et audit. |
| Moyenne | Messages sans contrat strict et erreurs permanentes rejouées en boucle | Validation des champs, tailles, dates, thèmes et scores ; erreurs de données vers DLQ, pause sur panne SQL. |
| Moyenne | `INSERT IGNORE` pouvait masquer des erreurs SQL autres que les doublons | Upsert sans modification de la clé pour les doublons ; validation avant SQL. |
| Moyenne | Rejeu d’un article ancien après purge : agrégats comptés deux fois | Refus des articles hors rétention avant l’écriture. |
| Moyenne | Collecte RSS sans limite de réponse ni timeout | Timeout socket 15 s, réponse 2 Mio maximum, HTTP(S) uniquement, y compris redirections. |
| Moyenne | Workers root, écriture libre, logs sans rotation | UID 10001, filesystem en lecture seule, `/tmp` éphémère, suppression des capabilities, rotation des logs. |
| Moyenne | Publication sans détection des messages non routables | `mandatory=True` et confirmations ; ack après succès uniquement. |
| Faible | Test DLQ acquittait puis republiait les messages étrangers | Messages étrangers maintenus non acquittés puis remis en file. |
| Maintenabilité | Topologie RabbitMQ dupliquée, peu de garde-fous | Module commun pour connexion/topologie, contrat de message et configuration ; Ruff, tests et CI. |

Le schéma SQL canonique utilisé par Storage réside dans `app/common/schema.sql`.
Le script d’initialisation historique est conservé ; un test impose leur égalité.

## Vérifications

- 14 tests unitaires : analyse, normalisation, contrat, rétention, limites RSS et redirections.
- Ruff : lint et formatage.
- Bandit : aucune alerte détectée dans les services Python après correction.
- `pip-audit` : aucune vulnérabilité connue signalée pour les dépendances applicatives résolues à cette date.
- Pile Docker isolée construite et démarrée : test de déduplication, parcours complet
  `raw_news -> analytics -> enriched_news -> MySQL` et routage des deux DLQ réussis.
- Grafana 13.2.1 : `/api/health` et santé de la datasource OK ; `SHOW GRANTS`
  confirme uniquement `SELECT` sur la base pour `grafana_reader`.
- Protections effectives vérifiées : UID 10001, rootfs en lecture seule, capabilities supprimées.
- Collecte réelle : 55 articles publiés lors d’un cycle de test.
- `.env` exclu de Git et du contexte Docker ; inspection ciblée de son historique.

La CI reprend lint, formatage, Bandit, tests unitaires, `pip-audit` et intégration
Docker. Les résultats locaux ne prouvent pas à eux seuls le succès futur de GitHub Actions.

## Limites restantes

- La pile déjà démarrée n’est pas migrée par un changement des fichiers : suivre
  [OPERATIONS.md](OPERATIONS.md), sauvegarder puis remplacer les comptes par défaut.
- Pas de TLS entre services, de haute disponibilité, de quotas de queues ni de politique
  automatique de rétention des DLQ/agrégats. Aucun test de charge à grande échelle.
- Le compte RabbitMQ initial possède les droits administrateur ; séparer les comptes
  opérateur et workers et leurs vhosts/permissions pour la production.
- Le compte SQL applicatif reste partagé entre stockage et nettoyage, avec les droits
  nécessaires à la création du schéma. Une production doit séparer ces responsabilités.
- Les secrets locaux sont visibles à l’administrateur Docker. Utiliser un gestionnaire
  de secrets dans un environnement partagé. Ne jamais partager `.env` ni les dumps.
- Les URL RSS sont une configuration d’opérateur de confiance ; ce mécanisme n’est pas
  un service d’URL arbitraires ouvert au public. Le timeout est un timeout socket, pas
  une échéance globale de tout le cycle ; beaucoup de flux ralentissent le polling.
- Les tags des images système ne sont pas tous figés par digest ; l’audit Python ne
  remplace pas un scanner CVE des images OS. Aucune absence de CVE OS n’est revendiquée.
- Un article expiré est ignoré même lors d’un premier import historique. L’URL est la
  clé d’identité : deux articles distincts partageant une URL seront dédupliqués.

## Sources

- [Avis de sécurité Grafana](https://grafana.com/security/security-advisories/).
- [Avis concernant les permissions de dashboards](https://grafana.com/security/security-advisories/cve-2026-21721/).
- [Versions officielles Grafana](https://github.com/grafana/grafana/releases).
- [MySQL Connector/Python](https://pypi.org/project/mysql-connector-python/).
