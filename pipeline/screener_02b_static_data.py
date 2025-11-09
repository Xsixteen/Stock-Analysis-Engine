#!/usr/bin/env python3
"""
Screener Pipeline Step 02b: Company Static Data (Financial Statements)

This step fetches fundamental financial data from Alpha Vantage API:
- Income Statement
- Balance Sheet
- Cash Flow Statement

Only runs if data/static_data.json is not present.
Pulls data for tickers listed in screener.json.
Stores only the last 2 years of annual and quarterly reports.
"""
import json
import os
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_tickers():
    """Load tickers from screener.json"""
    with open("data/screener.json", "r") as f:
        config = json.load(f)
    return config["tickers"]


def filter_last_two_years(financial_data):
    """
    Filter financial statement data to only include last 2 years

    Args:
        financial_data: Raw financial statement data from Alpha Vantage

    Returns:
        dict: Filtered data with only last 2 years of reports
    """
    if "error" in financial_data:
        return financial_data

    # Calculate cutoff date (2 years ago from today)
    cutoff_date = datetime.now() - timedelta(days=730)  # 2 years = 730 days
    cutoff_str = cutoff_date.strftime("%Y-%m-%d")

    filtered_data = {}

    # Copy metadata fields
    for key in ["symbol", "annualReports", "quarterlyReports"]:
        if key not in financial_data:
            continue

        if key in ["annualReports", "quarterlyReports"]:
            # Filter reports by date
            reports = financial_data[key]
            filtered_reports = [
                report for report in reports
                if "fiscalDateEnding" in report and report["fiscalDateEnding"] >= cutoff_str
            ]
            filtered_data[key] = filtered_reports
        else:
            # Copy as-is
            filtered_data[key] = financial_data[key]

    return filtered_data


def fetch_financial_statement(ticker, function, api_key):
    """
    Fetch a financial statement from Alpha Vantage API

    Args:
        ticker: Stock symbol
        function: API function (INCOME_STATEMENT, BALANCE_SHEET, CASH_FLOW)
        api_key: Alpha Vantage API key

    Returns:
        dict: Financial statement data
    """
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": function,
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
    if not data:
        raise ValueError("Empty response from API")

    return data


def fetch_ticker_data(ticker, api_key):
    """
    Fetch all financial statements for a ticker

    Args:
        ticker: Stock symbol
        api_key: Alpha Vantage API key

    Returns:
        dict: All financial data for the ticker
    """
    result = {
        "ticker": ticker,
        "timestamp": datetime.now().isoformat()
    }

    # API functions to fetch
    functions = {
        "income_statement": "INCOME_STATEMENT",
        "balance_sheet": "BALANCE_SHEET",
        "cash_flow": "CASH_FLOW"
    }

    for data_type, function in functions.items():
        try:
            print(f"    • {data_type.replace('_', ' ').title()}...", end=" ")
            data = fetch_financial_statement(ticker, function, api_key)

            # Filter to only keep last 2 years of data
            filtered_data = filter_last_two_years(data)
            result[data_type] = filtered_data

            print("✓")

            # Rate limiting: Alpha Vantage free tier = 5 calls/min
            # Sleep 12 seconds between calls (~5 calls/min)
            time.sleep(12)

        except Exception as e:
            result[data_type] = {"error": str(e)}
            print(f"✗ ({e})")

    return result


def main():
    print("="*60)
    print("SCREENER STEP 02b: Company Static Data")
    print("="*60)

    # Check if static_data.json already exists
    output_file = "data/static_data.json"
    if os.path.exists(output_file):
        print(f"\n✓ {output_file} already exists - skipping this step")
        print("\nStep 02b complete (skipped)")
        return

    try:
        # Get API key
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        if not api_key:
            raise ValueError("ALPHAVANTAGE_API_KEY not found in .env file")

        # Load tickers
        tickers = load_tickers()
        print(f"\n📊 Fetching financial statements for {len(tickers)} tickers...")
        print("   (Income Statement, Balance Sheet, Cash Flow)")
        print(f"\n⏱  Estimated time: ~{len(tickers) * 36 / 60:.1f} minutes")
        print("   (3 API calls per ticker × 12 sec rate limit)\n")

        # Fetch data for each ticker
        results = {}
        for i, ticker in enumerate(tickers, 1):
            print(f"  [{i}/{len(tickers)}] {ticker}")

            ticker_data = fetch_ticker_data(ticker, api_key)
            results[ticker] = ticker_data

            # Check if all data fetched successfully
            errors = [k for k, v in ticker_data.items()
                     if isinstance(v, dict) and "error" in v]
            if errors:
                print(f"    ⚠ Some data failed: {', '.join(errors)}")
            else:
                print(f"    ✓ All data retrieved")
            print()

        # Save output
        output = {
            "timestamp": datetime.now().isoformat(),
            "count": len(tickers),
            "data": results
        }

        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)

        # Summary
        total_calls = len(tickers) * 3
        successful_tickers = sum(
            1 for ticker_data in results.values()
            if not any(isinstance(v, dict) and "error" in v
                      for k, v in ticker_data.items()
                      if k not in ["ticker", "timestamp"])
        )

        print(f"✓ Completed: {successful_tickers}/{len(tickers)} tickers fully retrieved")
        print(f"  Total API calls made: {total_calls}")
        print(f"  Saved to: {output_file}")
        print("\nStep 02b complete")

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        exit(1)


if __name__ == "__main__":
    main()
