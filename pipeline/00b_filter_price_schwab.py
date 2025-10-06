"""
Filter by price and spread - Schwab API version
"""
import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schwab_client import get_schwab_client

load_dotenv()


def filter_price_liquidity():
    """Filter stocks by price range and bid/ask spread"""
    print("="*60)
    print("STEP 0B: Filter Price (Schwab API)")
    print("="*60)

    with open("data/sp500.json", "r") as f:
        tickers = json.load(f)["tickers"]

    print(f"Input: {len(tickers)} stocks")

    client = get_schwab_client()
    passed = []
    failed = []

    # Schwab allows up to 500 symbols per quote request
    # Process in batches of 100 for better performance
    batch_size = 100

    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        symbols_str = ','.join(batch)

        print(f"\nProcessing batch {i//batch_size + 1}/{(len(tickers)-1)//batch_size + 1}...")

        try:
            # Get quotes for batch
            response = client.get_quotes(symbols_str)
            response.raise_for_status()
            quotes = response.json()

            for ticker in batch:
                if ticker in quotes and 'quote' in quotes[ticker]:
                    quote = quotes[ticker]['quote']

                    bid = quote.get('bidPrice', 0)
                    ask = quote.get('askPrice', 0)

                    if bid > 0 and ask > 0:
                        mid = (bid + ask) / 2
                        spread_pct = ((ask - bid) / mid) * 100

                        # Filter: $30-400 price range, <2% spread
                        if 30 <= mid <= 400 and spread_pct < 2.0:
                            passed.append({
                                'ticker': ticker,
                                'bid': round(bid, 2),
                                'ask': round(ask, 2),
                                'mid': round(mid, 2),
                                'spread_pct': round(spread_pct, 2)
                            })
                            print(f"   ✅ {ticker}: ${mid:.2f} (spread: {spread_pct:.2f}%)")
                        else:
                            reason = "price out of range" if (mid < 30 or mid > 400) else f"spread {spread_pct:.2f}%"
                            failed.append({'ticker': ticker, 'reason': reason})
                            print(f"   ❌ {ticker}: {reason}")
                    else:
                        failed.append({'ticker': ticker, 'reason': 'invalid bid/ask'})
                        print(f"   ❌ {ticker}: invalid bid/ask")
                else:
                    failed.append({'ticker': ticker, 'reason': 'no quote data'})
                    print(f"   ❌ {ticker}: no quote data")

        except Exception as e:
            print(f"   ❌ Batch failed: {e}")
            for ticker in batch:
                failed.append({'ticker': ticker, 'reason': f'API error: {str(e)[:30]}'})

    return passed, failed


def save_results(passed, failed):
    """Save filtering results"""
    with open('data/filter1_passed.json', 'w') as f:
        json.dump(passed, f, indent=2)

    print(f"\nResults:")
    print(f"  Passed: {len(passed)}")
    print(f"  Failed: {len(failed)}")
    print(f"\nCriteria: $30-400, spread <2%")
    print(f"\n✅ Saved to data/filter1_passed.json")


def main():
    passed, failed = filter_price_liquidity()
    save_results(passed, failed)
    print("Step 0B complete")


if __name__ == "__main__":
    main()
