import pandas as pd


def generate_signal(df):
    """
    Generate a Gold BUY or SELL signal from completed market candles.

    Expected columns:
        close
        high
        low
        ema_50
        rsi_14
        atr_14
        1h_close
        1h_ema_200
        4h_close
        4h_ema_200
        1h_structure
    """

    if len(df) < 2:
        return None

    current = df.iloc[-1]
    previous = df.iloc[-2]

    # --------------------------------------------------------
    # 4H TREND
    # --------------------------------------------------------

    bullish_4h = current["4h_close"] > current["4h_ema_200"]
    bearish_4h = current["4h_close"] < current["4h_ema_200"]

    # --------------------------------------------------------
    # 1H TREND
    # --------------------------------------------------------

    bullish_1h = current["1h_close"] > current["1h_ema_200"]
    bearish_1h = current["1h_close"] < current["1h_ema_200"]

    # --------------------------------------------------------
    # 1H STRUCTURE
    # --------------------------------------------------------

    bullish_structure = current["1h_structure"] == "BULLISH"
    bearish_structure = current["1h_structure"] == "BEARISH"

    # --------------------------------------------------------
    # 15M MOMENTUM
    # --------------------------------------------------------

    bullish_momentum = (
        current["close"] > current["ema_50"]
        and current["rsi_14"] > 50
    )

    bearish_momentum = (
        current["close"] < current["ema_50"]
        and current["rsi_14"] < 50
    )

    # --------------------------------------------------------
    # 15M BREAKOUT
    # --------------------------------------------------------

    bullish_breakout = current["close"] > previous["high"]
    bearish_breakout = current["close"] < previous["low"]

    # --------------------------------------------------------
    # BUY SETUP
    # --------------------------------------------------------

    buy_setup = (
        bullish_4h
        and bullish_1h
        and bullish_structure
        and bullish_momentum
        and bullish_breakout
    )

    # --------------------------------------------------------
    # SELL SETUP
    # --------------------------------------------------------

    sell_setup = (
        bearish_4h
        and bearish_1h
        and bearish_structure
        and bearish_momentum
        and bearish_breakout
    )

    # --------------------------------------------------------
    # CREATE SIGNAL
    # --------------------------------------------------------

    if buy_setup:
        entry = current["close"]
        risk = 1.5 * current["atr_14"]

        return {
            "direction": "BUY",
            "entry": entry,
            "sl": entry - risk,
            "tp1": entry + risk,
            "tp2": entry + (2 * risk),
            "tp3": entry + (3 * risk),
            "time": current.name,
        }

    if sell_setup:
        entry = current["close"]
        risk = 1.5 * current["atr_14"]

        return {
            "direction": "SELL",
            "entry": entry,
            "sl": entry + risk,
            "tp1": entry - risk,
            "tp2": entry - (2 * risk),
            "tp3": entry - (3 * risk),
            "time": current.name,
        }

    return None
