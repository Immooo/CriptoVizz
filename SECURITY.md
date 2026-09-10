# Sécurité

Ce dépôt cible un déploiement local. Ne pas publier ses ports directement sur Internet.
Ne jamais inclure de mots de passe, `.env`, sauvegardes ou dumps dans une issue publique.
Pour signaler une vulnérabilité, utiliser la fonction privée « Report a vulnerability »
de GitHub si elle est activée, sinon contacter le propriétaire du dépôt en privé.

Exécuter la CI et l’audit de dépendances avant mise à niveau. Un audit sans alerte
ne constitue pas une preuve d’absence de vulnérabilité. Voir
[le bilan de revue](docs/SECURITY_REVIEW.md) et [les opérations](docs/OPERATIONS.md).
