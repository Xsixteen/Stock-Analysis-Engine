"""
Get Stock Prices: Real prices from Charles Schwab API
Enhanced with better error handling and diagnostics
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


def check_prerequisites():
    """Check if everything is set up correctly"""
    # Check if data directory exists
    if not os.path.exists("data"):
        print("📁 Creating data directory...")
        os.makedirs("data", exist_ok=True)

    # Try to import stocks
    try:
        sys.path.insert(0, 'data')
        from stocks import STOCKS
        return STOCKS
    except ImportError:
        print("❌ data/stocks.py not found - run step 00e first")
        sys.exit(1)


def get_real_prices():
    """Get real stock prices from Schwab API"""
    print("💰 Getting real stock prices from Charles Schwab...")

    STOCKS = check_prerequisites()
    client = get_schwab_client()

    prices = {}
    failed = []

    try:
        # Get all quotes in one request (Schwab supports up to 500 symbols)
        symbols_str = ','.join(STOCKS)

        print(f"📡 Fetching quotes for {len(STOCKS)} stocks...")
        response = client.get_quotes(symbols_str)
        response.raise_for_status()

        quotes = response.json()
        print("✅ Quotes received successfully")

        for ticker in STOCKS:
            if ticker in quotes and 'quote' in quotes[ticker]:
                quote = quotes[ticker]['quote']

                bid = quote.get('bidPrice', 0)
                ask = quote.get('askPrice', 0)

                if bid > 0 and ask > 0:
                    mid = (bid + ask) / 2
                    prices[ticker] = {
                        "ticker": ticker,
                        "bid": round(bid, 2),
                        "ask": round(ask, 2),
                        "mid": round(mid, 2),
                        "spread": round(ask - bid, 2),
                        "timestamp": datetime.now().isoformat()
                    }
                    print(f"   ✅ {ticker}: ${mid:.2f} (bid: ${bid:.2f}, ask: ${ask:.2f})")
                else:
                    failed.append(ticker)
                    print(f"   ❌ {ticker}: Invalid bid/ask")
            else:
                failed.append(ticker)
                print(f"   ❌ {ticker}: No data received")

    except Exception as e:
        print(f"❌ Schwab API error: {e}")
        print("This could be:")
        print("1. Invalid API credentials")
        print("2. Expired token (delete schwab_token.json and re-authenticate)")
        print("3. Network issues")
        print("4. Schwab API problems")
        sys.exit(1)

    return prices, failed


def save_prices(prices, failed):
    """Save price data"""
    # Import stocks again to get the original list
    sys.path.insert(0, 'data')
    from stocks import STOCKS

    output = {
        "timestamp": datetime.now().isoformat(),
        "requested": len(STOCKS),
        "success": len(prices),
        "failed": len(failed),
        "prices": prices,
        "missing_tickers": failed
    }

    with open("data/stock_prices.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n📊 Results:")
    print(f"   Success: {len(prices)}/{len(STOCKS)} ({len(prices)/len(STOCKS)*100:.1f}%)")
    print(f"   Failed: {len(failed)}")

    if len(prices) == 0:
        print("❌ FATAL: No prices collected")
        print("Check your Schwab API credentials and network connection")
        sys.exit(1)
    elif len(prices) < len(STOCKS) * 0.5:
        print("⚠️ WARNING: Less than 50% success rate")
        print("Pipeline will continue but may have limited results")


def main():
    """Main execution"""
    print("="*60)
    print("STEP 01: Get Real Stock Prices (Schwab API)")
    print("="*60)

    # Get prices
    prices, failed = get_real_prices()

    # Save results
    save_prices(prices, failed)

    print("✅ Step 01 complete: stock_prices.json created")


if __name__ == "__main__":
    main()
