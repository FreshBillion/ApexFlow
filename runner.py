import time
from datetime import datetime, timezone

from market_data import prepare_market_data
from signal_engine import generate_signal


CHECK_INTERVAL_SECONDS = 60


def run():
    last_signal_time = None

    print("APEXFLOW GOLD BOT STARTED")

    while True:
        try:
            data = prepare_market_data()
            signal = generate_signal(data)

            current_time = datetime.now(timezone.utc)

            if signal is None:
                print(
                    f"[{current_time:%Y-%m-%d %H:%M:%S} UTC] "
                    "NO SIGNAL"
                )

            else:
                signal_time = signal["time"]

                if signal_time != last_signal_time:
                    print(
                        f"\n[{current_time:%Y-%m-%d %H:%M:%S} UTC] "
                        f"{signal['direction']} SIGNAL"
                    )

                    print(f"Entry: {signal['entry']:.2f}")
                    print(f"SL:    {signal['sl']:.2f}")
                    print(f"TP1:   {signal['tp1']:.2f}")
                    print(f"TP2:   {signal['tp2']:.2f}")
                    print(f"TP3:   {signal['tp3']:.2f}")

                    last_signal_time = signal_time

                else:
                    print(
                        f"[{current_time:%Y-%m-%d %H:%M:%S} UTC] "
                        "Signal already processed"
                    )

        except Exception as error:
            print(f"ERROR: {error}")

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
