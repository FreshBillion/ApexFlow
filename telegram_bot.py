import os
import requests


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_signal(signal):
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is missing.")

    if not TELEGRAM_CHAT_ID:
        raise ValueError("TELEGRAM_CHAT_ID is missing.")

    direction = signal["direction"]

    emoji = "🟢" if direction == "BUY" else "🔴"

    message = (
        f"{emoji} GOLD {direction} SIGNAL\n\n"
        f"Entry: ${signal['entry']:.2f}\n"
        f"TP1: ${signal['tp1']:.2f}\n"
        f"TP2: ${signal['tp2']:.2f}\n"
        f"TP3: ${signal['tp3']:.2f}\n"
        f"SL: ${signal['sl']:.2f}\n\n"
        f"Time: {signal['time']} UTC"
    )

    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    response = requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()
