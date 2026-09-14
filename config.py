import os
from dotenv import load_dotenv

load_dotenv()

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

SYMBOL = "XAU/USD"
BASE_INTERVAL = "15min"

DATA_FOLDER = "data"
RAW_DATA_FILE = f"{DATA_FOLDER}/xauusd_15m.csv"

REQUEST_TIMEOUT = 30
