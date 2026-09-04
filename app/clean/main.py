import time
import os
from datetime import datetime
from database.database_clean import Database_clean

if __name__ == "__main__":
    # Configuration
    CLEANUP_INTERVAL_MINUTES = 60  # Run cleanup every hour
    RETENTION_HOURS = int(os.getenv("RETENTION_DAYS", "30")) * 24
    
    db_clean = Database_clean(retention_hours=RETENTION_HOURS)
    
    print(f"🧹 Service de nettoyage démarré")
    print(f"⚙️ Configuration: nettoyage toutes les {CLEANUP_INTERVAL_MINUTES} minutes")
    print(f"⚙️ Rétention des données: {RETENTION_HOURS} heures")
    
    while True:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n🕐 Début du nettoyage à {current_time}")
            
            # Perform cleanup
            db_clean.database_clean()
            
            # Get database size info
            db_clean.get_database_size()
            
            # Wait for next cleanup cycle
            print(f"💤 Prochain nettoyage dans {CLEANUP_INTERVAL_MINUTES} minutes")
            time.sleep(CLEANUP_INTERVAL_MINUTES * 60)
            
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du service de nettoyage")
            break
        except Exception as e:
            print(f"❌ Erreur dans la boucle principale: {e}")
            # Wait a bit before retrying
            time.sleep(60)
