import requests
from bs4 import BeautifulSoup

# URL of the page to scrape
url = "https://www.eldolar.info/en/mexico/dia/hoy"

# Send a GET request to the page
response = requests.get(url)
response.raise_for_status()  # Raise an exception if there's an error

# Parse the page content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Extracting the relevant data from the page
data = {}

# Fetch the average rate
average_rate_section = soup.find('h1')
average_rate = average_rate_section.find_all('span', class_='xTimes')
data['average_rate'] = {
    'dollar_to_peso': average_rate[1].text.strip(),
    'percentage_change': soup.find('p', class_='change').text.strip()
}

# Fetch the buy/sell rates
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

# Print the result as JSON
import json
print(json.dumps(data, indent=4))
