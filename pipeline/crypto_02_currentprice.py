#!/usr/bin/env python3
"""
Crypto Pipeline - Step 02: Fetch Bitcoin Average Price
Fetches Avg Price for BTC/USDT (1m) and appends to the latest data entry.
"""
import os
import json
import requests
from dotenv import load_dotenv

def get_avg_price(symbol, interval, api_key):
    """
    Fetch Avg Price from taapi.io
    """
    url = f"https://api.taapi.io/avgprice"
    params = {
        'secret': api_key,
        'exchange': 'binance',
        'symbol': symbol,
        'interval': interval
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error fetching Avg Price: {response.text}")
        return None
        
    return response.json().get('value')

def main():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("TAAPI_API_KEY")
    if not api_key:
        print("❌ Error: TAAPI_API_KEY not found in .env file")
        return False
        
    symbol = "BTC/USDT"
    interval = "1m"
    
    print(f"Fetching Avg Price data for {symbol} ({interval})...")
    
    # Fetch Avg Price
    avg_price = get_avg_price(symbol, interval, api_key)
    if avg_price is None:
        return False
    print(f"Avg Price (1m): {avg_price}")

    # Load existing data
    file_path = "data/btc_data.json"
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found. Run Step 01 first.")
        return False
        
    try:
        with open(file_path, 'r') as f:
            history = json.load(f)
            if not isinstance(history, list) or not history:
                print("❌ Error: Invalid data format in history file.")
                return False
    except json.JSONDecodeError:
        print("❌ Error: Corrupt history file.")
        return False

    # Update latest entry
    latest_entry = history[-1]
    
    # Ensure 'indicators' exists
    if 'indicators' not in latest_entry:
        latest_entry['indicators'] = {}
        
    latest_entry['indicators']['avg_price_1m'] = avg_price
    
    # Save back to file
    with open(file_path, 'w') as f:
        json.dump(history, f, indent=2)
        
    print(f"\n✅ Data updated in {file_path}")
    return True

if __name__ == "__main__":
    if not main():
        exit(1)
