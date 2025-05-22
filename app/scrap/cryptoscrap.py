from bs4 import BeautifulSoup
import requests
from datetime import datetime

class Cryptoscrap:
    def __init__(self):
        pass

    def cryptoscrapfct(self):
        # datetime object containing current date and time
        now = datetime.now()
        # Webstie crypto
        res = requests.get('https://crypto.com/price')

        soup = BeautifulSoup(res.text, 'lxml')
        cryptos = soup.find_all('tr', class_='css-1cxc880')
        table = []
        data_dict = {}
        for crypto in cryptos:
            crypto_name = crypto.find('p', class_='chakra-text css-rkws3').text
            crypto_price = crypto.find('p', class_='chakra-text css-5a8n3t').text[1:]
            crypto_price = crypto_price.replace(",", "")
            crypto_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
            crypto_classement = crypto.find('td', class_='css-w6jew4').text
            crypto_volume = crypto.find('td', class_='css-15lyn3l').text[1:]
            if crypto_volume == "_A":
                crypto_volume = None
            crypto_change = crypto.find('td', class_='css-vtw5vj').text[:-1]
            if crypto_change.startswith("+"):
                crypto_change = crypto_change[1:]
            if crypto_name or crypto_price or crypto_datetime or crypto_classement or crypto_change is not None:
                data_dict = {
                    'cryptoName': crypto_name,
                    'cryptoPrice': crypto_price,
                    'cryptoDatetime': crypto_datetime,
                    'cryptoClassement': crypto_classement,
                    'cryptovolume': crypto_volume,
                    'cryptochange': crypto_change
                }
                table.append(data_dict)
        return table

