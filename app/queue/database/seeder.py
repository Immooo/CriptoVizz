import random
from datetime import datetime, timedelta

# Structure de base des données de cryptomonnaie
crypto_data_example = {
    "Bitcoin": {"cryptoPrice": 26891.3, "cryptoClassement": 1, "cryptoVolume": "9 B"},
    "Ethereum": {"cryptoPrice": 1550.75, "cryptoClassement": 2, "cryptoVolume": "4.83 B"},
    "Tether": {'cryptoPrice': 1.0, 'cryptoClassement': 3, 'cryptoVolume': '15.77 B'},
    "BNB": {'cryptoPrice': 206.19, 'cryptoClassement': 4, 'cryptoVolume': '288.66 M'},
    "XRP": {'cryptoPrice': 0.4832, 'cryptoClassement': 5, 'cryptoVolume': '705.12 M'},
    "USD Coin": {'cryptoPrice': 1.0, 'cryptoClassement': 6, 'cryptoVolume': '2.23 B'},
    "Solana": {'cryptoPrice': 21.53, 'cryptoClassement': 7, 'cryptoVolume': '243.24 M'},
    "Cardano": {'cryptoPrice': 0.2476, 'cryptoClassement': 8, 'cryptoVolume': '93.67 M'},
    "Dogecoin": {'cryptoPrice': 0.05866, 'cryptoClassement': 9, 'cryptoVolume': '123.47 M'},
    "TRON": {'cryptoPrice': 0.08552, 'cryptoClassement': 10, 'cryptoVolume': '135.26 M'},
    "Toncoin": {"cryptoPrice": 1.95, "cryptoClassement": 11, "cryptoVolume": "22.81 M"},
    "Dai": {"cryptoPrice": 1.0, "cryptoClassement": 12, "cryptoVolume": "91.06 M"},
    "Polygon": {"cryptoPrice": 0.5151, "cryptoClassement": 13, "cryptoVolume": "206.2 M"},
    "Polkadot": {"cryptoPrice": 3.71, "cryptoClassement": 14, "cryptoVolume": "69.53 M"},
    "Litecoin": {"cryptoPrice": 61.69, "cryptoClassement": 15, "cryptoVolume": "212.12 M"},
    "Bitcoin Cash": {"cryptoPrice": 214.25, "cryptoClassement": 16, "cryptoVolume": "131.57 M"},
    "SHIBA INU": {"cryptoPrice": 6.863e-06, "cryptoClassement": 17, "cryptoVolume": "67.17 M"},
    "Chainlink": {"cryptoPrice": 7.25, "cryptoClassement": 18, "cryptoVolume": "188.72 M"},
    "UNUS SED LEO": {"cryptoPrice": 3.71, "cryptoClassement": 19, "cryptoVolume": "571,181"},
    "TrueUSD": {"cryptoPrice": 0.9992, "cryptoClassement": 20, "cryptoVolume": "142.99 M"},
    "Avalanche": {"cryptoPrice": 9.18, "cryptoClassement": 21, "cryptoVolume": "96.5 M"},
    "Stellar": {"cryptoPrice": 0.1033, "cryptoClassement": 22, "cryptoVolume": "48.18 M"},
    "Monero": {"cryptoPrice": 152.14, "cryptoClassement": 23, "cryptoVolume": "53.55 M"},
    "OKB": {"cryptoPrice": 42.99, "cryptoClassement": 24, "cryptoVolume": "1.59 M"},
    "Cosmos": {"cryptoPrice": 6.64, "cryptoClassement": 25, "cryptoVolume": "68.59 M"},
    "Uniswap": {"cryptoPrice": 4.02, "cryptoClassement": 26, "cryptoVolume": "46.6 M"},
    "Binance USD": {"cryptoPrice": 1.0, "cryptoClassement": 27, "cryptoVolume": "434.34 M"},
    "Ethereum Classic": {"cryptoPrice": 14.86, "cryptoClassement": 28, "cryptoVolume": "58.88 M"},
    "Hedera": {"cryptoPrice": 0.04616, "cryptoClassement": 29, "cryptoVolume": "29.73 M"},
    "Filecoin": {"cryptoPrice": 3.22, "cryptoClassement": 30, "cryptoVolume": "48.52 M"},
    "Lido DAO Token": {"cryptoPrice": 1.56, "cryptoClassement": 31, "cryptoVolume": "25.84 M"},
    "Maker": {"cryptoPrice": 1392.35, "cryptoClassement": 32, "cryptoVolume": "48.84 M"},
    "Cronos": {"cryptoPrice": 0.05074, "cryptoClassement": 33, "cryptoVolume": "11.11 M"},
    "Internet Computer": {"cryptoPrice": 3.0, "cryptoClassement": 34, "cryptoVolume": "16.81 M"},
    "Wrapped Beacon ETH": {"cryptoPrice": 1577.59, "cryptoClassement": 35, "cryptoVolume": "2.02 M"},
    "VeChain": {"cryptoPrice": 0.01644, "cryptoClassement": 36, "cryptoVolume": "23.44 M"},
    "Aptos": {"cryptoPrice": 4.86, "cryptoClassement": 37, "cryptoVolume": "67.76 M"},
    "Optimism": {"cryptoPrice": 1.2, "cryptoClassement": 38, "cryptoVolume": "66.04 M"},
    "Quant": {"cryptoPrice": 85.86, "cryptoClassement": 39, "cryptoVolume": "11.34 M"},
    "Arbitrum": {"cryptoPrice": 0.8078, "cryptoClassement": 40, "cryptoVolume": "107.93 M"},
    "Mantle": {"cryptoPrice": 0.3261, "cryptoClassement": 41, "cryptoVolume": "30.68 M"},
    "Wrapped EOS": {"cryptoPrice": 0.8901, "cryptoClassement": 42, "cryptoVolume": "_A"},
    "NEAR Protocol": {"cryptoPrice": 1.01, "cryptoClassement": 43, "cryptoVolume": "43.21 M"},
    "Aave": {"cryptoPrice": 63.78, "cryptoClassement": 44, "cryptoVolume": "54.8 M"},
    "Kaspa": {"cryptoPrice": 0.04279, "cryptoClassement": 45, "cryptoVolume": "10.73 M"},
    "Trexcoin": {"cryptoPrice": 0.8535, "cryptoClassement": 46, "cryptoVolume": "186,725"},
    "UnlimitedIP": {"cryptoPrice": 0.5108, "cryptoClassement": 47, "cryptoVolume": "158,292"},
    "Algorand": {"cryptoPrice": 0.09521, "cryptoClassement": 48, "cryptoVolume": "18.43 M"},
    "The Graph": {"cryptoPrice": 0.08065, "cryptoClassement": 49, "cryptoVolume": "15.51 M"},
    "USDD": {"cryptoPrice": 0.9995, "cryptoClassement": 50, "cryptoVolume": "17.88 M"}
    # Ajoutez d'autres cryptomonnaies si nécessaire
}

# Fonction pour générer un changement de prix réaliste
def generate_price_change_5_percent(current_price):
    change_percent = random.uniform(-5, 5)
    return current_price * (1 + change_percent / 100), change_percent

# Définition de la plage de temps pour les 15 derniers jours
end_date = datetime.now()
start_date = end_date - timedelta(days=15)
interval_hourly = timedelta(hours=1)

# Génération des données pour des intervalles horaires sur les 15 derniers jours
seeder_data_hourly = []
current_date = start_date
while current_date <= end_date:
    for crypto, values in crypto_data_example.items():
        new_price, change_percent = generate_price_change_5_percent(values['cryptoPrice'])
        seeder_data_hourly.append({
            "cryptoName": crypto,
            "cryptoPrice": new_price,
            "cryptoChange": change_percent,
            "cryptoDateTime": current_date.strftime("%Y-%m-%d %H:%M:%S"),
            "cryptoClassement": values['cryptoClassement'],
            "cryptoVolume": values['cryptoVolume']
        })
    current_date += interval_hourly

# Écriture des données dans un fichier SQL
output_file_path_hourly = 'database/crypto_seeder_hourly_last_15_days.sql'

with open(output_file_path_hourly, 'w') as file:
    # Instruction INSERT INTO unique
    file.write("INSERT INTO crypto.crypto (cryptoName, cryptoPrice, cryptoDatetime, cryptoClassement, cryptoVolume, cryptoChange) VALUES\n")

    # Ajout de toutes les valeurs
    values = []
    for entry in seeder_data_hourly:
        value = "('{}',{:.2f},'{}',{},'{}',{:.2f})".format(
            entry['cryptoName'],
            entry['cryptoPrice'],
            entry['cryptoDateTime'],
            entry['cryptoClassement'],
            entry['cryptoVolume'],
            entry['cryptoChange']
        )
        values.append(value)

    # Combinaison des valeurs et ajout d'un point-virgule à la fin
    file.write(",\n".join(values) + ";")
