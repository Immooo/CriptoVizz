from .database_connection import Database_connection
from datetime import datetime, timedelta, timezone
import time

class Database_clean:
    def __init__(self, retention_hours=720):
        self.db_connection = Database_connection()
        self.retention_hours = retention_hours
        
    def database_clean(self):
        """Clean old data from the database"""
        conn = None
        cursor = None
        
        try:
            # Establish connection
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    conn = self.db_connection.connection()
                    cursor = conn.cursor()
                    break
                except Exception as e:
                    retry_count += 1
                    print(f"❌ Tentative de connexion MySQL #{retry_count}: {e}")
                    if retry_count < max_retries:
                        time.sleep(5)
                    else:
                        raise Exception("Impossible de se connecter à MySQL")
            
            # Calculate cutoff date
            date_limite = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=self.retention_hours)
            
            # Count and delete old source articles. Hourly analytics are retained.
            count_sql = "SELECT COUNT(*) FROM news_articles WHERE published_at < %s"
            cursor.execute(count_sql, (date_limite,))
            count_to_delete = cursor.fetchone()[0]
            
            if count_to_delete > 0:
                # Delete old records
                delete_sql = "DELETE FROM news_articles WHERE published_at < %s"
                cursor.execute(delete_sql, (date_limite,))
                
                # Commit the transaction
                conn.commit()
                
                print(f"✅ {count_to_delete} enregistrements obsolètes supprimés (plus de {self.retention_hours} heures)")
                
                # Optional: Optimize table after deletion
                if count_to_delete > 1000:  # Only optimize if we deleted many records
                    cursor.execute("OPTIMIZE TABLE news_articles")
                    print("✅ Table optimisée après suppression")
            else:
                print(f"ℹ️ Aucun enregistrement à supprimer (tous datent de moins de {self.retention_hours} heures)")
            
            # Print database statistics
            cursor.execute("SELECT COUNT(*), MIN(published_at), MAX(published_at) FROM news_articles")
            stats = cursor.fetchone()
            if stats[0] > 0:
                print(f"📊 Statistiques: {stats[0]} enregistrements, du {stats[1]} au {stats[2]}")
            
        except Exception as e:
            print(f"❌ Erreur lors du nettoyage de la base de données: {e}")
            if conn:
                conn.rollback()
                
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    def get_database_size(self):
        """Get the size of the crypto table"""
        conn = None
        cursor = None
        
        try:
            conn = self.db_connection.connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    table_name,
                    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb,
                    table_rows
                FROM information_schema.tables
                WHERE table_schema = DATABASE() AND table_name = 'news_articles'
            """)
            
            result = cursor.fetchone()
            if result:
                print(f"📈 Taille de la table: {result[1]} MB, {result[2]} lignes")
                
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de la taille: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
