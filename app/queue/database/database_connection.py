import mysql.connector
import time
from dotenv import load_dotenv

class Database_connection:
    def __init__(self):
        pass

    def connection(self, max_retries=10, retry_delay=5):
        load_dotenv()
        
        for attempt in range(max_retries):
            try:
                print(f"Tentative de connexion MySQL #{attempt + 1}")
                mydb = mysql.connector.connect(
                    host="mysql",  # Docker
                    user="epitech",
                    password="epitech",
                    database="crypto",
                    port=3306,
                    connect_timeout=30
                )
                print("✅ Connexion MySQL réussie !")
                return mydb
                
            except mysql.connector.Error as e:
                print(f"❌ Erreur connexion MySQL (tentative {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ Nouvelle tentative dans {retry_delay} secondes...")
                    time.sleep(retry_delay)
                else:
                    print("🚨 Impossible de se connecter à MySQL après toutes les tentatives")
                    raise e
            except Exception as e:
                print(f"❌ Erreur inattendue: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise e