import requests

from config import TWELVE_DATA_API_KEY


url = "https://api.twelvedata.com/time_series"

params = {
    "symbol": "XAU/USD",
    "interval": "15min",
    "outputsize": 5,
    "apikey": TWELVE_DATA_API_KEY,
}


response = requests.get(url, params=params, timeout=30)

print("HTTP status:", response.status_code)
print(response.json())
