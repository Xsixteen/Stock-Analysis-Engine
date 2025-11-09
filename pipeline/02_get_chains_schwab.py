"""
Get Options Chains - Schwab API version
Complete with symbols, strikes, and quotes
"""
import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
from schwab.client import Client

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schwab_client import get_schwab_client

load_dotenv()


def load_stock_prices():
    """Load stock prices from step 01"""
    try:
        with open("data/stock_prices.json", "r") as f:
            data = json.load(f)
        return data["prices"]
    except FileNotFoundError:
        print("❌ stock_prices.json not found")
        sys.exit(1)


def get_chains():
    """Get option chains for all stocks"""
    print("="*60)
    print("STEP 02: Get Options Chains (Schwab API)")
    print("="*60)

    prices = load_stock_prices()
    client = get_schwab_client()

    chains = {}
    today = datetime.now().date()

    print("\n📊 Collecting chains with symbols...")

    for ticker, price_data in prices.items():
        stock_price = price_data["mid"]
        print(f"\n{ticker}: ${stock_price:.2f}")

        try:
            # Get full option chain (0-45 DTE, 70-130% strikes)
            response = client.get_option_chain(
                ticker,
                contract_type=Client.Options.ContractType.ALL,
                strike_range=Client.Options.StrikeRange.ALL,
                from_date=today,
                include_underlying_quote=False
            )
            response.raise_for_status()

            chain_data = response.json()

            if 'callExpDateMap' not in chain_data or not chain_data['callExpDateMap']:
                print(f"   ❌ No option chain")
                continue

            ticker_expirations = []

            # Process each expiration
            for exp_str, call_strikes in chain_data['callExpDateMap'].items():
                # Format: "2025-01-17:45" (date:DTE)
                exp_date_str, dte_str = exp_str.split(':')
                exp_date = datetime.strptime(exp_date_str, '%Y-%m-%d').date()
                dte = int(dte_str)

                if not (0 <= dte <= 45):
                    continue

                # Get corresponding put strikes
                put_strikes = chain_data.get('putExpDateMap', {}).get(exp_str, {})

                strikes_list = []

                # Process each strike price
                for strike_str in call_strikes.keys():
                    strike = float(strike_str)

                    # Filter: 70-130% of stock price
                    if not (0.70 * stock_price <= strike <= 1.30 * stock_price):
                        continue

                    strike_data = {"strike": strike}

                    # Get call data
                    if strike_str in call_strikes and call_strikes[strike_str]:
                        call = call_strikes[strike_str][0]  # First contract
                        strike_data.update({
                            "call_symbol": call.get('symbol', ''),
                            "call_bid": call.get('bid', 0),
                            "call_ask": call.get('ask', 0)
                        })

                    # Get put data
                    if strike_str in put_strikes and put_strikes[strike_str]:
                        put = put_strikes[strike_str][0]  # First contract
                        strike_data.update({
                            "put_symbol": put.get('symbol', ''),
                            "put_bid": put.get('bid', 0),
                            "put_ask": put.get('ask', 0)
                        })

                    strikes_list.append(strike_data)

                if strikes_list:
                    ticker_expirations.append({
                        "expiration_date": exp_date_str,
                        "dte": dte,
                        "strikes": sorted(strikes_list, key=lambda x: x['strike'])
                    })

            if ticker_expirations:
                chains[ticker] = sorted(ticker_expirations, key=lambda x: x['dte'])
                total_strikes = sum(len(exp['strikes']) for exp in ticker_expirations)
                print(f"   ✅ {len(ticker_expirations)} expirations, {total_strikes} strikes")
            else:
                print(f"   ⚠️ No strikes in 70-130% range")

        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")

    # Save output
    output = {
        "timestamp": datetime.now().isoformat(),
        "total_tickers": len(chains),
        "chains": chains
    }

    with open("data/chains.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Chains collected for {len(chains)} tickers")
    print(f"   Saved to data/chains.json")


def main():
    get_chains()
    print("Step 02 complete")


if __name__ == "__main__":
    main()
