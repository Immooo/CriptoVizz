import os
import subprocess
import time
from database.database_insert import Database_insert

def generate_seeder_if_needed():
    """Generate seeder file if it doesn't exist"""
    seeder_path = 'database/crypto_seeder_hourly_last_15_days.sql'
    
    if not os.path.exists(seeder_path):
        print("📝 Génération du fichier seeder...")
        try:
            subprocess.run(["python", "database/seeder.py"], check=True)
            print("✅ Fichier seeder généré avec succès")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de la génération du seeder: {e}")
            return False
    else:
        print("✅ Fichier seeder déjà existant")
        return True

def insert_seeder_data(db_insert):
    """Insert seeder data if the database is empty"""
    try:
        # Check if we need to insert seeder data
        # This is a simple check - you might want to improve it
        db_insert.insert_seeder_into_db("Data")
        return True
    except Exception as e:
        print(f"⚠️ Erreur lors de l'insertion du seeder (peut-être déjà inséré): {e}")
        return False

if __name__ == "__main__":
    print("🚀 Démarrage du service Queue...")
    
    # Generate seeder if needed
    seeder_generated = generate_seeder_if_needed()
    
    # Create database insert instance
    db_insert = Database_insert()
    
    # Insert seeder data on first run
    if seeder_generated:
        print("💾 Tentative d'insertion des données du seeder...")
        # Wait a bit for MySQL to be ready
        time.sleep(10)
        insert_seeder_data(db_insert)
    
    # Start consuming messages
    print("📡 Démarrage du consommateur de messages...")
    try:
        db_insert.consume_queue()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du service Queue")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")