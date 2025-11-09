#!/usr/bin/env python3
"""
Screener Pipeline Step 01: Check/Create Configuration
Checks for screener.json in data folder. If not found, prompts for 8 tickers.
"""
import json
import os
from datetime import datetime

def check_config():
    """Check if screener.json exists"""
    config_path = "data/screener.json"
    return os.path.exists(config_path)

def prompt_for_tickers():
    """Prompt user for up to 8 ticker symbols"""
    print("\nNo screener configuration found.")
    print("Please enter up to 8 ticker symbols (comma-separated):")
    print("Example: AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, NFLX")

    user_input = input("\nEnter tickers: ").strip()

    # Parse and clean tickers
    tickers = [t.strip().upper() for t in user_input.split(',') if t.strip()]

    # Limit to 8 tickers
    if len(tickers) > 8:
        print(f"\nWarning: You entered {len(tickers)} tickers. Using first 8.")
        tickers = tickers[:8]

    if len(tickers) == 0:
        raise ValueError("No tickers provided")

    return tickers

def create_config(tickers):
    """Create screener.json with provided tickers"""
    config = {
        "timestamp": datetime.now().isoformat(),
        "count": len(tickers),
        "tickers": tickers
    }

    with open("data/screener.json", "w") as f:
        json.dump(config, f, indent=2)

    return config

def main():
    print("="*60)
    print("SCREENER STEP 01: Check/Create Configuration")
    print("="*60)

    try:
        if check_config():
            # Config exists, load and display it
            with open("data/screener.json", "r") as f:
                config = json.load(f)
            print(f"\n✓ Configuration found: {len(config['tickers'])} tickers")
            print(f"  Tickers: {', '.join(config['tickers'])}")
        else:
            # Config doesn't exist, create it
            tickers = prompt_for_tickers()
            config = create_config(tickers)
            print(f"\n✓ Configuration created: {len(config['tickers'])} tickers")
            print(f"  Tickers: {', '.join(config['tickers'])}")

        print("\nStep 01 complete")

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        exit(1)

if __name__ == "__main__":
    main()
