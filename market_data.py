import requests
import pandas as pd

from config import (
    TWELVE_DATA_API_KEY,
    SYMBOL,
    BASE_INTERVAL,
    REQUEST_TIMEOUT,
)


# ============================================================
# DOWNLOAD XAU/USD 15M DATA
# ============================================================

def download_market_data(outputsize=5000):
    if not TWELVE_DATA_API_KEY:
        raise ValueError("Twelve Data API key is missing.")

    url = "https://api.twelvedata.com/time_series"

    params = {
        "symbol": SYMBOL,
        "interval": BASE_INTERVAL,
        "outputsize": outputsize,
        "apikey": TWELVE_DATA_API_KEY,
    }

    response = requests.get(
        url,
        params=params,
        timeout=REQUEST_TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    if data.get("status") == "error":
        raise RuntimeError(
            f"Twelve Data error: {data.get('message', 'Unknown error')}"
        )

    if "values" not in data:
        raise RuntimeError("No market data returned.")

    df = pd.DataFrame(data["values"])

    df["datetime"] = pd.to_datetime(df["datetime"])

    for column in ["open", "high", "low", "close"]:
        df[column] = pd.to_numeric(df[column])

    df = (
        df.sort_values("datetime")
        .drop_duplicates("datetime")
        .reset_index(drop=True)
    )

    df = df.set_index("datetime")

    return df


# ============================================================
# REMOVE INCOMPLETE CANDLE
# ============================================================

def remove_incomplete_candle(df):
    if len(df) < 2:
        return df

    return df.iloc[:-1].copy()


# ============================================================
# RESAMPLE HIGHER TIMEFRAMES
# ============================================================

def resample_timeframe(df, timeframe):
    result = df.resample(timeframe).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
    })

    result = result.dropna()

    return result


# ============================================================
# EMA
# ============================================================

def add_ema(df, period):
    df = df.copy()

    df[f"ema_{period}"] = (
        df["close"]
        .ewm(span=period, adjust=False)
        .mean()
    )

    return df


# ============================================================
# RSI
# ============================================================

def add_rsi(df, period=14):
    df = df.copy()

    change = df["close"].diff()

    gain = change.clip(lower=0)
    loss = -change.clip(upper=0)

    average_gain = gain.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    average_loss = loss.ewm(
        alpha=1 / period,
        adjust=False
    ).mean()

    rs = average_gain / average_loss

    df[f"rsi_{period}"] = 100 - (
        100 / (1 + rs)
    )

    return df


# ============================================================
# ATR
# ============================================================

def add_atr(df, period=14):
    df = df.copy()

    previous_close = df["close"].shift(1)

    true_range = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - previous_close).abs(),
            (df["low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    df[f"atr_{period}"] = (
        true_range
        .ewm(alpha=1 / period, adjust=False)
        .mean()
    )

    return df


# ============================================================
# 1H MARKET STRUCTURE
# ============================================================

def add_market_structure(df):
    df = df.copy()

    df["swing_high"] = False
    df["swing_low"] = False

    left = 2
    right = 2

    for i in range(left, len(df) - right):
        high = df["high"].iloc[i]
        low = df["low"].iloc[i]

        left_highs = df["high"].iloc[i-left:i]
        right_highs = df["high"].iloc[i+1:i+right+1]

        left_lows = df["low"].iloc[i-left:i]
        right_lows = df["low"].iloc[i+1:i+right+1]

        if high > left_highs.max() and high > right_highs.max():
            df.iloc[i, df.columns.get_loc("swing_high")] = True

        if low < left_lows.min() and low < right_lows.min():
            df.iloc[i, df.columns.get_loc("swing_low")] = True

    structure = None

    last_swing_high = None
    previous_swing_high = None

    last_swing_low = None
    previous_swing_low = None

    structures = []

    for i in range(len(df)):

        if df["swing_high"].iloc[i]:
            previous_swing_high = last_swing_high
            last_swing_high = df["high"].iloc[i]

        if df["swing_low"].iloc[i]:
            previous_swing_low = last_swing_low
            last_swing_low = df["low"].iloc[i]

        if (
            last_swing_high is not None
            and previous_swing_high is not None
            and last_swing_low is not None
            and previous_swing_low is not None
        ):
            if (
                last_swing_high > previous_swing_high
                and last_swing_low > previous_swing_low
            ):
                structure = "BULLISH"

            elif (
                last_swing_high < previous_swing_high
                and last_swing_low < previous_swing_low
            ):
                structure = "BEARISH"

        structures.append(structure)

    df["structure"] = structures

    return df


# ============================================================
# PREPARE ALL MARKET DATA
# ============================================================

def prepare_market_data():
    # Download 15M data
    df_15m = download_market_data()

    # Remove newest incomplete candle
    df_15m = remove_incomplete_candle(df_15m)

    # Create higher timeframes
    df_1h = resample_timeframe(df_15m, "1h")
    df_4h = resample_timeframe(df_15m, "4h")

    # Remove incomplete higher-timeframe candles
    df_1h = remove_incomplete_candle(df_1h)
    df_4h = remove_incomplete_candle(df_4h)

    # --------------------------------------------------------
    # 15M INDICATORS
    # --------------------------------------------------------

    df_15m = add_ema(df_15m, 20)
    df_15m = add_ema(df_15m, 50)
    df_15m = add_ema(df_15m, 200)
    df_15m = add_rsi(df_15m, 14)
    df_15m = add_atr(df_15m, 14)

    # --------------------------------------------------------
    # 1H INDICATORS + STRUCTURE
    # --------------------------------------------------------

    df_1h = add_ema(df_1h, 200)
    df_1h = add_market_structure(df_1h)

    # --------------------------------------------------------
    # 4H INDICATORS
    # --------------------------------------------------------

    df_4h = add_ema(df_4h, 200)

    # --------------------------------------------------------
    # PREVENT LOOK-AHEAD
    # --------------------------------------------------------

    df_1h = df_1h.copy()
    df_4h = df_4h.copy()

    df_1h.index = df_1h.index + pd.Timedelta(hours=1)
    df_4h.index = df_4h.index + pd.Timedelta(hours=4)

    # --------------------------------------------------------
    # MERGE HIGHER TIMEFRAMES INTO 15M DATA
    # --------------------------------------------------------

    df_15m = pd.merge_asof(
        df_15m.sort_index(),
        df_1h[
            [
                "close",
                "ema_200",
                "structure",
            ]
        ].rename(
            columns={
                "close": "1h_close",
                "ema_200": "1h_ema_200",
                "structure": "1h_structure",
            }
        ),
        left_index=True,
        right_index=True,
        direction="backward",
    )

    df_15m = pd.merge_asof(
        df_15m.sort_index(),
        df_4h[
            [
                "close",
                "ema_200",
            ]
        ].rename(
            columns={
                "close": "4h_close",
                "ema_200": "4h_ema_200",
            }
        ),
        left_index=True,
        right_index=True,
        direction="backward",
    )

    # --------------------------------------------------------
    # REMOVE ROWS WITHOUT COMPLETE INDICATOR DATA
    # --------------------------------------------------------

    required_columns = [
        "close",
        "ema_50",
        "rsi_14",
        "atr_14",
        "1h_close",
        "1h_ema_200",
        "1h_structure",
        "4h_close",
        "4h_ema_200",
    ]

    df_15m = df_15m.dropna(
        subset=required_columns
    )

    return df_15m


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    data = prepare_market_data()

    print("=" * 60)
    print("APEXFLOW GOLD MARKET DATA")
    print("=" * 60)

    print(f"15M candles prepared: {len(data)}")

    print(
        f"Latest candle: "
        f"{data.index[-1]}"
    )

    print(
        f"Latest Gold price: "
        f"{data['close'].iloc[-1]:.2f}"
    )

    print(
        f"Latest 1H structure: "
        f"{data['1h_structure'].iloc[-1]}"
    )

    print(
        f"Latest 4H trend: "
        f"{'BULLISH' if data['4h_close'].iloc[-1] > data['4h_ema_200'].iloc[-1] else 'BEARISH'}"
    )

    print("=" * 60)
