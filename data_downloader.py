import os
import requests
import pandas as pd

from config import (
    TWELVE_DATA_API_KEY,
    SYMBOL,
    BASE_INTERVAL,
    DATA_FOLDER,
    RAW_DATA_FILE,
    REQUEST_TIMEOUT,
)


def download_gold_data():
    if not TWELVE_DATA_API_KEY:
        raise ValueError("Twelve Data API key is missing.")

    url = "https://api.twelvedata.com/time_series"

    params = {
        "symbol": SYMBOL,
        "interval": BASE_INTERVAL,
        "outputsize": 5000,
        "apikey": TWELVE_DATA_API_KEY,
    }

    print("Downloading Gold market data...")

    response = requests.get(
        url,
        params=params,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    if "status" in data and data["status"] == "error":
        raise RuntimeError(
            f"Twelve Data error: {data.get('message', 'Unknown error')}"
        )

    if "values" not in data:
        raise RuntimeError("No market data was returned.")

    df = pd.DataFrame(data["values"])

    df["datetime"] = pd.to_datetime(df["datetime"])

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column])

    df = df.sort_values("datetime").reset_index(drop=True)

    os.makedirs(DATA_FOLDER, exist_ok=True)

    df.to_csv(RAW_DATA_FILE, index=False)

    print(f"Downloaded {len(df)} candles.")
    print(f"Saved to: {RAW_DATA_FILE}")


if __name__ == "__main__":
    download_gold_data()
