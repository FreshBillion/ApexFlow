from market_data import prepare_market_data
from signal_engine import generate_signal


def main():
    print("=" * 60)
    print("APEXFLOW GOLD BOT")
    print("=" * 60)

    print("\nLoading latest Gold market data...")

    data = prepare_market_data()

    signal = generate_signal(data)

    print("\n" + "=" * 60)
    print("SIGNAL RESULT")
    print("=" * 60)

    if signal is None:
        print("NO SIGNAL")
        print("The current market does not meet all strategy conditions.")

    else:
        print(f"Direction : {signal['direction']}")
        print(f"Entry     : {signal['entry']:.2f}")
        print(f"SL        : {signal['sl']:.2f}")
        print(f"TP1       : {signal['tp1']:.2f}")
        print(f"TP2       : {signal['tp2']:.2f}")
        print(f"TP3       : {signal['tp3']:.2f}")
        print(f"Time      : {signal['time']}")

    print("=" * 60)


if __name__ == "__main__":
    main()
