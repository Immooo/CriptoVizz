from bs4 import BeautifulSoup
import requests
from datetime import datetime

class Cryptoscrap:
    def __init__(self):
        pass

    def cryptoscrapfct(self):
        # datetime object containing current date and time
        now = datetime.now()
        
        try:
            # Website crypto
            res = requests.get('https://crypto.com/price', timeout=10)
            res.raise_for_status()  # Raise exception for bad status codes
        except requests.RequestException as e:
            print(f"❌ Error fetching crypto prices: {e}")
            return []

        soup = BeautifulSoup(res.text, 'lxml')
        cryptos = soup.find_all('tr', class_='css-1cxc880')
        table = []
        
        for crypto in cryptos:
            try:
                crypto_name = crypto.find('p', class_='chakra-text css-rkws3').text
                crypto_price = crypto.find('p', class_='chakra-text css-5a8n3t').text[1:]
                crypto_price = crypto_price.replace(",", "")
                crypto_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
                crypto_classement = crypto.find('td', class_='css-w6jew4').text
                crypto_volume = crypto.find('td', class_='css-15lyn3l').text[1:]
                
                # Handle special cases for volume
                if crypto_volume == "_A" or crypto_volume == "":
                    crypto_volume = "0"
                    
                crypto_change_elem = crypto.find('td', class_='css-vtw5vj')
                crypto_change = "0"  # Default value
                
                if crypto_change_elem and crypto_change_elem.text:
                    crypto_change = crypto_change_elem.text.rstrip('%')
                    if crypto_change.startswith("+"):
                        crypto_change = crypto_change[1:]
                
                # Validate data before adding
                if crypto_name and crypto_price and crypto_classement:
                    data_dict = {
                        'cryptoName': crypto_name[:50],  # Truncate to 50 chars max
                        'cryptoPrice': crypto_price,
                        'cryptoDatetime': crypto_datetime,
                        'cryptoClassement': crypto_classement,
                        'cryptoVolume': crypto_volume,  # Fixed: capital V
                        'cryptoChange': crypto_change    # Fixed: capital C
                    }
                    table.append(data_dict)
                    
            except AttributeError as e:
                print(f"⚠️ Error parsing crypto data: {e}")
                continue
                
        return table