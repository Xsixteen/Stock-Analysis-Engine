#!/usr/bin/env python3
"""
Crypto Pipeline - Step 03: Fetch Bitcoin RSI
Fetches RSI (14 periods) for BTC/USDT (4h) and appends to the latest data entry.
"""
import os
import json
import requests
from dotenv import load_dotenv

def get_rsi(symbol, interval, period, api_key):
    """
    Fetch RSI from taapi.io
    """
    url = f"https://api.taapi.io/rsi"
    params = {
        'secret': api_key,
        'exchange': 'binance',
        'symbol': symbol,
        'interval': interval,
        'period': period
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error fetching RSI: {response.text}")
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
    interval = "4h"
    period = 14
    
    print(f"Fetching RSI data for {symbol} ({interval}, {period})...")
    
    # Fetch RSI
    rsi_val = get_rsi(symbol, interval, period, api_key)
    if rsi_val is None:
        return False
    print(f"RSI (14, 4h): {rsi_val}")

    # Load existing data
    file_path = "data/btc_data.json"
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found. Run previous steps first.")
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
        
    latest_entry['indicators']['rsi_14_4h'] = rsi_val
    
    # Save back to file
    with open(file_path, 'w') as f:
        json.dump(history, f, indent=2)
        
    print(f"\n✅ Data updated in {file_path}")
    return True

if __name__ == "__main__":
    if not main():
        exit(1)
