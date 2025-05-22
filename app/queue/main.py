import time
import subprocess
from database.database_insert import Database_insert

seederGenerator = False

if not seederGenerator:
    subprocess.run(["python", "database/seeder.py"]) # Lancer le script de création du seeder
    ligne_executee = True

if __name__ == "__main__":
    db_insert = Database_insert()  # Créer une instance en dehors de la boucle

    while True:
        try:
            db_insert.consume_queue()
            db_insert.insert_seeder_into_db(message="Data") # Insérer les données du seeder dans la BDD
        except Exception as e:
            print(f"Error in main loop: {e}")
