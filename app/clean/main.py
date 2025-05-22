import time
from database.database_clean import Database_clean

if __name__ == "__main__":
    starttime = time.monotonic()
    db_clean = Database_clean()  # Créer une instance en dehors de la boucle

    while True:
        try:
            db_clean.database_clean()
        except Exception as e:
            print(f"Error in main loop: {e}")
        time.sleep(500.0 - ((time.monotonic() - starttime) % 500.0))
