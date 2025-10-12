#!/usr/bin/env python3
"""
Screener Pipeline Step 02: Get Company Overview from Alpha Vantage
Fetches company overview data, SMA (50-day), and RSI (14-day) for all tickers in screener.json
API Documentation:
  - Company Overview: https://www.alphavantage.co/documentation/#company-overview
  - SMA: https://www.alphavantage.co/documentation/#sma
  - RSI: https://www.alphavantage.co/documentation/#rsi
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

def get_company_overview(ticker, api_key):
    """
    Fetch company overview from Alpha Vantage API

    Args:
        ticker: Stock symbol
        api_key: Alpha Vantage API key

    Returns:
        dict: Company overview data
    """
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "OVERVIEW",
        "symbol": ticker,
        "apikey": api_key
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()

    data = response.json()

    # Check for API errors
    if "Error Message" in data:
        raise ValueError(f"API Error for {ticker}: {data['Error Message']}")

    if "Note" in data:
        raise ValueError(f"API Rate Limit: {data['Note']}")

    return data

def get_sma(ticker, api_key, interval="daily", time_period=50, series_type="close"):
    """
    Fetch Simple Moving Average (SMA) from Alpha Vantage API

    Args:
        ticker: Stock symbol
        api_key: Alpha Vantage API key
        interval: Time interval (daily, weekly, monthly)
        time_period: Number of data points for SMA calculation
        series_type: Price type (close, open, high, low)

    Returns:
        dict: SMA data with latest value
    """
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "SMA",
        "symbol": ticker,
        "interval": interval,
        "time_period": time_period,
        "series_type": series_type,
        "apikey": api_key
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()

    data = response.json()

    # Check for API errors
    if "Error Message" in data:
        raise ValueError(f"API Error for {ticker}: {data['Error Message']}")

    if "Note" in data:
        raise ValueError(f"API Rate Limit: {data['Note']}")

    # Extract the most recent SMA value
    if "Technical Analysis: SMA" in data:
        technical_data = data["Technical Analysis: SMA"]
        if technical_data:
            latest_date = list(technical_data.keys())[0]
            return {
                "latest_date": latest_date,
                "value": technical_data[latest_date]["SMA"],
                "time_period": time_period
            }

    return None

def get_rsi(ticker, api_key, interval="daily", time_period=14, series_type="close"):
    """
    Fetch Relative Strength Index (RSI) from Alpha Vantage API

    Args:
        ticker: Stock symbol
        api_key: Alpha Vantage API key
        interval: Time interval (daily, weekly, monthly)
        time_period: Number of data points for RSI calculation
        series_type: Price type (close, open, high, low)

    Returns:
        dict: RSI data with latest value
    """
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "RSI",
        "symbol": ticker,
        "interval": interval,
        "time_period": time_period,
        "series_type": series_type,
        "apikey": api_key
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()

    data = response.json()

    # Check for API errors
    if "Error Message" in data:
        raise ValueError(f"API Error for {ticker}: {data['Error Message']}")

    if "Note" in data:
        raise ValueError(f"API Rate Limit: {data['Note']}")

    # Extract the most recent RSI value
    if "Technical Analysis: RSI" in data:
        technical_data = data["Technical Analysis: RSI"]
        if technical_data:
            latest_date = list(technical_data.keys())[0]
            return {
                "latest_date": latest_date,
                "value": technical_data[latest_date]["RSI"],
                "time_period": time_period
            }

    return None

def main():
    print("="*60)
    print("SCREENER STEP 02: Get Company Overview (Alpha Vantage)")
    print("="*60)

    try:
        # Get API key from environment
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        if not api_key:
            raise ValueError("ALPHAVANTAGE_API_KEY not found in .env file")

        # Load tickers from screener config
        tickers = load_tickers()
        print(f"\n📊 Loading overview data for {len(tickers)} tickers...")

        # Fetch overview data for each ticker
        overview_data = {}
        for i, ticker in enumerate(tickers, 1):
            print(f"  [{i}/{len(tickers)}] Fetching {ticker}...")

            try:
                # Fetch company overview
                print(f"    - Overview...", end=" ")
                data = get_company_overview(ticker, api_key)
                print("✓")
                time.sleep(12)  # Rate limit: ~5 calls per minute

                # Fetch SMA (50-day)
                print(f"    - SMA...", end=" ")
                sma_data = get_sma(ticker, api_key, interval="daily", time_period=50)
                data["technical_indicators"] = {"SMA_50": sma_data}
                print("✓")
                time.sleep(12)

                # Fetch RSI (14-day)
                print(f"    - RSI...", end=" ")
                rsi_data = get_rsi(ticker, api_key, interval="daily", time_period=14)
                data["technical_indicators"]["RSI_14"] = rsi_data
                print("✓")

                overview_data[ticker] = data

                # Alpha Vantage free tier: 5 API calls/minute, 500/day
                # Add delay to respect rate limits
                if i < len(tickers):
                    time.sleep(12)  # ~5 calls per minute

            except Exception as e:
                print(f"✗ ({e})")
                overview_data[ticker] = {"error": str(e)}

        # Save to overview.json
        output = {
            "timestamp": datetime.now().isoformat(),
            "count": len(tickers),
            "data": overview_data
        }

        with open("data/overview.json", "w") as f:
            json.dump(output, f, indent=2)

        # Summary
        successful = sum(1 for v in overview_data.values() if "error" not in v)
        print(f"\n✓ Completed: {successful}/{len(tickers)} successful")
        print(f"  Saved to: data/overview.json")
        print("\nStep 02 complete")

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        exit(1)

if __name__ == "__main__":
    main()
