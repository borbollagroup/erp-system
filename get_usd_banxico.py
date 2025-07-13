import requests
import csv
from datetime import datetime
import os
import django

# Set up Django environment for database access
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'borbolla_webpage.settings')  # Replace 'your_project' with your Django project name
django.setup()

# Import the ExchangeRate model
from facturador.models import ExchangeRate  # Replace 'your_app' with your Django app name

# Your Banxico API key
BANXICO_API_KEY = 'f1542325a55e88fe5f781f14bec53702ea41ba049c3b19df6500a0805015d62d'

# Fetches USD to MXN exchange rate from Banxico API
def get_usd_price():
    api_url = f'https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718/datos/oportuno?token={BANXICO_API_KEY}'
    response = requests.get(api_url, headers={'Bmx-Token': BANXICO_API_KEY})
    content = response.json()

    # Extract the USD price from the API response
    usd_price = extract_usd_price(content)
    return usd_price

# Extracts the USD price from the API response object
def extract_usd_price(obj):
    if obj and 'bmx' in obj and 'series' in obj['bmx'] and obj['bmx']['series'] and 'datos' in obj['bmx']['series'][0] and obj['bmx']['series'][0]['datos']:
        # Return both the date and price for logging in database and CSV
        date = obj['bmx']['series'][0]['datos'][0]['fecha']
        rate = obj['bmx']['series'][0]['datos'][0]['dato']
        return date, rate
    else:
        raise ValueError("USD price not found in the response object.")

# Logs the exchange rate with current datetime into a CSV file
def log_to_csv(date, rate):
    filename = 'usd_mxn_exchange_rate.csv'
    
    # Current datetime for logging
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Open or create the CSV file
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # If the file is new, write the header
        if file.tell() == 0:
            writer.writerow(["Timestamp", "Date", "USD to MXN Exchange Rate"])
        
        # Write the data (datetime, API date, and exchange rate)
        writer.writerow([now, date, rate])

# Saves the exchange rate data to the database
def save_to_db(date, rate):
    # Convert rate to Decimal for saving in the model
    rate_decimal = round(float(rate), 4)
    
    # Create and save the ExchangeRate record
    ExchangeRate.objects.create(date=date, usd_to_mxn_rate=rate_decimal)
    print(f"Saved exchange rate: {rate} on {date} to database")

# Calls the data-fetching function, logs to CSV, and saves to database
def update_banxico():
    date, rate = get_usd_price()
    log_to_csv(date, rate)
    save_to_db(date, rate)
    print(f"Logged and saved exchange rate: {rate} on {date}")

# Run the update function
if __name__ == "__main__":
    update_banxico()
