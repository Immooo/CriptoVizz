from .database_connection import Database_connection
from datetime import datetime, timedelta


class Database_clean:
    def __init__(self):
            self.db_connection = Database_connection()
    def database_clean(self):
        try:
            conn = self.db_connection.connection()

            # Créer un objet de curseur
            cursor = conn.cursor()

            # Calculer la date limite (48 heures avant la date actuelle)
            date_limite = datetime.now() - timedelta(hours=48)

            # Récupérer le numéro de minute actuel
            minute_actuelle = datetime.now().minute

            # Utiliser le modulo pour déterminer si le jeu de données doit être supprimé
            if minute_actuelle % 2 == 0:
                # Requête SQL pour supprimer les données obsolètes
                sql = "DELETE FROM crypto WHERE cryptoDatetime < %s"
                cursor.execute(sql, (date_limite,))

                # Valider la transaction
                conn.commit()

                print("Données obsolètes supprimées avec succès.")
            else:
                print("Aucune suppression effectuée pour cette minute.")

        except Exception as e:
            print(f"Erreur MySQL : {e}")

        finally:
            cursor.close()
            conn.close()
