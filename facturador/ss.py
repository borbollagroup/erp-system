import requests
response = requests.get("https://mx.dolarapi.com/v1/cotizaciones/usd")
print(response.json())