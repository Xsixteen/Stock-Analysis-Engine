"""
Filter by IV - Schwab API version
Greeks and IV are included in option chain data
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


def get_iv_data():
    """Filter stocks by IV range using Greeks from option chain"""
    print("="*60)
    print("STEP 0D: Filter IV (Schwab API)")
    print("="*60)

    with open("data/filter2_passed.json", "r") as f:
        stocks = json.load(f)

    print(f"Input: {len(stocks)} stocks")

    client = get_schwab_client()
    passed = []
    failed = []

    for stock_data in stocks:
        ticker = stock_data['ticker']
        print(f"\n{ticker}...", end=" ")

        try:
            # Get option chain with Greeks
            response = client.get_option_chain(
                ticker,
                contract_type=Client.Options.ContractType.CALL,
                strike_count=5,  # Just get ATM strikes for IV check
                include_underlying_quote=True
            )
            response.raise_for_status()

            chain_data = response.json()

            # Get underlying price
            underlying_price = chain_data.get('underlyingPrice', stock_data['mid'])

            if 'callExpDateMap' not in chain_data or not chain_data['callExpDateMap']:
                failed.append({'ticker': ticker, 'reason': 'no chain'})
                print("❌ no chain")
                continue

            # Find ATM strike IV
            atm_iv = None

            for exp_str, strikes in chain_data['callExpDateMap'].items():
                for strike_str, options in strikes.items():
                    if options:
                        option = options[0]
                        strike = float(strike_str)

                        # Check if near ATM (within 5%)
                        if abs(strike - underlying_price) / underlying_price <= 0.05:
                            iv = option.get('volatility', 0)
                            if iv > 0:
                                atm_iv = iv * 100  # Convert to percentage
                                break
                if atm_iv:
                    break

            if atm_iv is None:
                failed.append({'ticker': ticker, 'reason': 'no IV data'})
                print("❌ no IV data")
                continue

            # Filter: IV 15-80%
            if 15 <= atm_iv <= 80:
                passed.append({
                    **stock_data,
                    'atm_iv': round(atm_iv, 1)
                })
                print(f"✅ IV: {atm_iv:.1f}%")
            else:
                failed.append({'ticker': ticker, 'reason': f'IV {atm_iv:.1f}% out of range'})
                print(f"❌ IV {atm_iv:.1f}% out of range")

        except Exception as e:
            error_msg = str(e)[:30]
            failed.append({'ticker': ticker, 'reason': error_msg})
            print(f"❌ {error_msg}")

    return passed, failed


def save_results(passed, failed):
    """Save filtering results"""
    with open('data/filter3_passed.json', 'w') as f:
        json.dump(passed, f, indent=2)

    print(f"\nResults:")
    print(f"  Passed: {len(passed)}")
    print(f"  Failed: {len(failed)}")
    print(f"\nCriteria: IV 15-80%")
    print(f"\n✅ Saved to data/filter3_passed.json")


def main():
    passed, failed = get_iv_data()
    save_results(passed, failed)
    print("Step 0D complete")


if __name__ == "__main__":
    main()
