"""
Filter by options availability - Schwab API version
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


def filter_options():
    """Filter stocks by options chain availability"""
    print("="*60)
    print("STEP 0C: Filter Options (Schwab API)")
    print("="*60)

    with open("data/filter1_passed.json", "r") as f:
        stocks = json.load(f)

    print(f"Input: {len(stocks)} stocks")

    client = get_schwab_client()
    passed = []
    failed = []

    today = datetime.now().date()

    for stock_data in stocks:
        ticker = stock_data['ticker']
        print(f"\n{ticker}...", end=" ")

        try:
            # Get option chain for all expirations
            response = client.get_option_chain(
                ticker,
                contract_type=Client.Options.ContractType.ALL,
                include_underlying_quote=False
            )
            response.raise_for_status()

            chain_data = response.json()

            # Check if we have option data
            if 'callExpDateMap' not in chain_data or not chain_data['callExpDateMap']:
                failed.append({'ticker': ticker, 'reason': 'no chain'})
                print("❌ no chain")
                continue

            # Parse expirations and filter by DTE
            good_exps = []
            for exp_str in chain_data['callExpDateMap'].keys():
                # Format: "2025-01-17:45" (date:DTE)
                exp_date_str = exp_str.split(':')[0]
                exp_date = datetime.strptime(exp_date_str, '%Y-%m-%d').date()
                dte = (exp_date - today).days

                if 15 <= dte <= 45:
                    good_exps.append({'date': str(exp_date), 'dte': dte})

            if not good_exps:
                failed.append({'ticker': ticker, 'reason': 'no 15-45 DTE'})
                print("❌ no 15-45 DTE")
                continue

            # Check strike count for best expiration
            best_exp = good_exps[0]
            exp_key = f"{best_exp['date']}:{best_exp['dte']}"

            if exp_key in chain_data['callExpDateMap']:
                strikes = chain_data['callExpDateMap'][exp_key]
                strike_count = len(strikes)

                if strike_count < 20:
                    failed.append({'ticker': ticker, 'reason': f'only {strike_count} strikes'})
                    print(f"❌ only {strike_count} strikes")
                    continue

                passed.append({
                    **stock_data,
                    'expirations': len(good_exps),
                    'best_expiration': best_exp,
                    'strikes_count': strike_count
                })
                print(f"✅ {len(good_exps)} exps, {strike_count} strikes")

            else:
                failed.append({'ticker': ticker, 'reason': 'expiration key mismatch'})
                print("❌ expiration key mismatch")

        except Exception as e:
            error_msg = str(e)[:30]
            failed.append({'ticker': ticker, 'reason': error_msg})
            print(f"❌ {error_msg}")

    return passed, failed


def save_results(passed, failed):
    """Save filtering results"""
    with open('data/filter2_passed.json', 'w') as f:
        json.dump(passed, f, indent=2)

    print(f"\nResults:")
    print(f"  Passed: {len(passed)}")
    print(f"  Failed: {len(failed)}")
    print(f"\nCriteria: 20+ strikes, 15-45 DTE")
    print(f"\n✅ Saved to data/filter2_passed.json")


def main():
    passed, failed = filter_options()
    save_results(passed, failed)
    print("Step 0C complete")


if __name__ == "__main__":
    main()
