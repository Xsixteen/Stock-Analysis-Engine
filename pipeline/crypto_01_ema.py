#!/usr/bin/env python3
"""
Crypto Pipeline - Step 01: Fetch Bitcoin EMA
Fetches EMA 13 and EMA 50 for BTC/USDT and saves to JSON.
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

def get_ema(symbol, interval, period, api_key):
    """
    Fetch EMA from taapi.io
    """
    url = f"https://api.taapi.io/ema"
    params = {
        'secret': api_key,
        'exchange': 'binance',
        'symbol': symbol,
        'interval': interval,
        'period': period
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error fetching EMA {period}: {response.text}")
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
    
    print(f"Fetching EMA data for {symbol} ({interval})...")
    
    # Fetch EMA 13
    ema_13 = get_ema(symbol, interval, 13, api_key)
    if ema_13 is None:
        return False
    print(f"SMA 13: {ema_13}")

    # Fetch EMA 50
    ema_50 = get_ema(symbol, interval, 50, api_key)
    if ema_50 is None:
        return False
    print(f"SMA 50: {ema_50}")
    
    # Prepare data
    data = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "interval": interval,
        "indicators": {
            "ema_13": ema_13,
            "ema_50": ema_50
        }
    }
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Append to history or create new file
    file_path = "data/btc_data.json"
    history = []
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                history = json.load(f)
                if not isinstance(history, list):
                    history = [history]
        except json.JSONDecodeError:
            pass # Start fresh if file is corrupt
            
    history.append(data)
    
    # Save to file
    with open(file_path, 'w') as f:
        json.dump(history, f, indent=2)
        
    print(f"\n✅ Data saved to {file_path}")
    return True

if __name__ == "__main__":
    if not main():
        exit(1)
