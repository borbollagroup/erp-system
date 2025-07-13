from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
from facturador.models import ExchangeRate, ExchangeRate.BankRate
from django.utils import timezone

class Command(BaseCommand):
    help = "Fetches and updates the latest USD to MXN exchange rates from El Dolar website."

    def handle(self, *args, **kwargs):
        # URL of the page to scrape
        url = "https://www.eldolar.info/en/mexico/dia/hoy"

        # Send a GET request to the page
        response = requests.get(url)
        response.raise_for_status()

        # Parse the page content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extracting data
        data = {}
        average_rate_section = soup.find('h1')
        average_rate = average_rate_section.find_all('span', class_='xTimes')
        data['average_rate'] = {
            'dollar_to_peso': average_rate[1].text.strip(),
            'percentage_change': soup.find('p', class_='change').text.strip()
        }

        # Extract the buy/sell rates
        exchange_rate_section = soup.find('div', class_='exchangeRate')
        buy_rate = exchange_rate_section.find('p', title="Buying one you pay").find('span', class_='xTimes').text
        sell_rate = exchange_rate_section.find('p', title="Selling one you get").find('span', class_='xTimes').text
        data['buy_rate'] = buy_rate
        data['sell_rate'] = sell_rate

        # Fetch the detailed bank rates from the table
        bank_data = []
        table = soup.find('table', id='dllsTable')
        rows = table.find('tbody').find_all('tr')

        for row in rows:
            columns = row.find_all('td')
            if len(columns) == 5:
                entity = columns[0].text.strip()
                buy = columns[3].text.strip()
                sell = columns[4].text.strip() if len(columns) > 4 else "N/A"
                bank_data.append({
                    'entity': entity,
                    'buy': buy,
                    'sell': sell
                })

        data['banks'] = bank_data

        # Update or create the ExchangeRate model
        exchange_rate, created = ExchangeRate.objects.get_or_create(
            date=timezone.now().date(),
            defaults={
                'average_rate': data['average_rate']['dollar_to_peso'],
                'percentage_change': data['average_rate']['percentage_change'],
                'buy_rate': data['buy_rate'],
                'sell_rate': data['sell_rate']
            }
        )

        # Update or create BankRates
        for bank in data['banks']:
            BankRate.objects.update_or_create(
                exchange_rate=exchange_rate,
                bank_name=bank['entity'],
                defaults={
                    'buy_rate': bank['buy'],
                    'sell_rate': bank['sell']
                }
        )

        self.stdout.write(self.style.SUCCESS('Exchange rates successfully updated.'))
