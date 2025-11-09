#!/usr/bin/env python3
"""
Screener Pipeline Step 02c: Daily Quote Data

This step fetches real-time/latest quote data from Alpha Vantage API:
- Current price, open, high, low, volume
- Previous close and price change
- Latest trading day information

Uses the GLOBAL_QUOTE endpoint for each ticker in screener.json.
"""
import json
import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_tickers():
    """Load tickers from screener.json"""
    with open("data/screener.json", "r") as f:
        config = json.load(f)
    return config["tickers"]


def fetch_global_quote(ticker, api_key):
    """
    Fetch latest quote data from Alpha Vantage API

    Args:
        ticker: Stock symbol
        api_key: Alpha Vantage API key

    Returns:
        dict: Global quote data
    """
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": ticker,
        "apikey": api_key
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()

    # Error handling
    if "Error Message" in data:
        raise ValueError(f"API Error: {data['Error Message']}")
    if "Note" in data:
        raise ValueError(f"API Rate Limit: {data['Note']}")
    if not data or "Global Quote" not in data:
        raise ValueError("Empty or invalid response from API")

    # Extract the Global Quote object
    quote = data.get("Global Quote", {})

    # Check if quote is empty (invalid ticker)
    if not quote:
        raise ValueError("No quote data available for this ticker")

    return quote


def main():
    print("="*60)
    print("SCREENER STEP 02c: Daily Quote Data")
    print("="*60)

    try:
        # Get API key
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        if not api_key:
            raise ValueError("ALPHAVANTAGE_API_KEY not found in .env file")

        # Load tickers
        tickers = load_tickers()
        print(f"\n📊 Fetching latest quotes for {len(tickers)} tickers...")
        print(f"   (Real-time price, volume, and trading data)\n")

        # Fetch quote for each ticker
        results = {}
        for i, ticker in enumerate(tickers, 1):
            print(f"  [{i}/{len(tickers)}] {ticker}...", end=" ")

            try:
                quote = fetch_global_quote(ticker, api_key)

                # Store the quote data
                results[ticker] = {
                    "symbol": quote.get("01. symbol", ticker),
                    "price": quote.get("05. price", "N/A"),
                    "open": quote.get("02. open", "N/A"),
                    "high": quote.get("03. high", "N/A"),
                    "low": quote.get("04. low", "N/A"),
                    "volume": quote.get("06. volume", "N/A"),
                    "latest_trading_day": quote.get("07. latest trading day", "N/A"),
                    "previous_close": quote.get("08. previous close", "N/A"),
                    "change": quote.get("09. change", "N/A"),
                    "change_percent": quote.get("10. change percent", "N/A"),
                    "timestamp": datetime.now().isoformat()
                }

                # Display key metrics
                price = quote.get("05. price", "N/A")
                change_pct = quote.get("10. change percent", "N/A")
                print(f"✓ (Price: ${price}, Change: {change_pct})")

                # Rate limiting: Alpha Vantage free tier = 5 calls/min
                # Sleep 12 seconds between calls (~5 calls/min)
                if i < len(tickers):
                    time.sleep(12)

            except Exception as e:
                results[ticker] = {"error": str(e)}
                print(f"✗ ({e})")

                # Still apply rate limiting even on errors
                if i < len(tickers):
                    time.sleep(12)

        # Save output
        output_file = "data/daily_data.json"
        output = {
            "timestamp": datetime.now().isoformat(),
            "count": len(tickers),
            "data": results
        }

        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)

        # Summary
        successful = sum(1 for v in results.values() if "error" not in v)
        print(f"\n✓ Completed: {successful}/{len(tickers)} quotes retrieved")
        print(f"  Saved to: {output_file}")
        print("\nStep 02c complete")

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        exit(1)


if __name__ == "__main__":
    main()
