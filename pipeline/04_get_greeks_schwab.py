"""
Get Greeks - Schwab API version
Greeks (delta, gamma, theta, vega, IV) are included in option chain data
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


def get_greeks():
    """Embed Greeks into chains data structure"""
    print("="*60)
    print("STEP 04: Get Greeks (Schwab API)")
    print("="*60)

    # Load chains from step 02
    with open("data/chains.json", "r") as f:
        chains_data = json.load(f)

    client = get_schwab_client()
    chains = chains_data["chains"]

    print(f"\n🧮 Fetching Greeks for {len(chains)} tickers...")

    chains_with_greeks = {}

    for ticker, expirations in chains.items():
        print(f"\n{ticker}...", end=" ")

        try:
            # Get full option chain with Greeks
            response = client.get_option_chain(
                ticker,
                contract_type=Client.Options.ContractType.ALL,
                include_underlying_quote=False
            )
            response.raise_for_status()

            chain_data = response.json()

            # Create lookup maps for Greeks by symbol
            greeks_map = {}

            # Extract Greeks from calls
            for exp_str, strikes in chain_data.get('callExpDateMap', {}).items():
                for strike_str, options in strikes.items():
                    if options:
                        opt = options[0]
                        symbol = opt.get('symbol', '')
                        if symbol:
                            greeks_map[symbol] = {
                                'delta': opt.get('delta', 0),
                                'gamma': opt.get('gamma', 0),
                                'theta': opt.get('theta', 0),
                                'vega': opt.get('vega', 0),
                                'rho': opt.get('rho', 0),
                                'iv': opt.get('volatility', 0)
                            }

            # Extract Greeks from puts
            for exp_str, strikes in chain_data.get('putExpDateMap', {}).items():
                for strike_str, options in strikes.items():
                    if options:
                        opt = options[0]
                        symbol = opt.get('symbol', '')
                        if symbol:
                            greeks_map[symbol] = {
                                'delta': opt.get('delta', 0),
                                'gamma': opt.get('gamma', 0),
                                'theta': opt.get('theta', 0),
                                'vega': opt.get('vega', 0),
                                'rho': opt.get('rho', 0),
                                'iv': opt.get('volatility', 0)
                            }

            # Embed Greeks into existing chain structure
            ticker_expirations_with_greeks = []

            for exp_data in expirations:
                strikes_with_greeks = []

                for strike in exp_data['strikes']:
                    strike_with_greeks = strike.copy()

                    # Add call Greeks
                    if 'call_symbol' in strike and strike['call_symbol']:
                        call_symbol = strike['call_symbol']
                        if call_symbol in greeks_map:
                            strike_with_greeks['call_greeks'] = greeks_map[call_symbol]

                    # Add put Greeks
                    if 'put_symbol' in strike and strike['put_symbol']:
                        put_symbol = strike['put_symbol']
                        if put_symbol in greeks_map:
                            strike_with_greeks['put_greeks'] = greeks_map[put_symbol]

                    strikes_with_greeks.append(strike_with_greeks)

                ticker_expirations_with_greeks.append({
                    **exp_data,
                    'strikes': strikes_with_greeks
                })

            chains_with_greeks[ticker] = ticker_expirations_with_greeks

            # Count strikes with Greeks
            total_strikes = sum(len(exp['strikes']) for exp in ticker_expirations_with_greeks)
            strikes_with_greeks_count = sum(
                1 for exp in ticker_expirations_with_greeks
                for strike in exp['strikes']
                if 'call_greeks' in strike or 'put_greeks' in strike
            )

            print(f"✅ {strikes_with_greeks_count}/{total_strikes} strikes with Greeks")

        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}")
            # Keep original data without Greeks
            chains_with_greeks[ticker] = expirations

    # Save output
    output = {
        "timestamp": datetime.now().isoformat(),
        "total_tickers": len(chains_with_greeks),
        "chains_with_greeks": chains_with_greeks
    }

    with open("data/chains_with_greeks.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Greeks embedded for {len(chains_with_greeks)} tickers")
    print(f"   Saved to data/chains_with_greeks.json")


def main():
    get_greeks()
    print("Step 04 complete")


if __name__ == "__main__":
    main()
