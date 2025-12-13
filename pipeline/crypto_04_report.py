#!/usr/bin/env python3
"""
Crypto Pipeline - Step 04: Generate Report
Analyzes data and generates a markdown report with trade signals.
"""
import os
import json
from datetime import datetime

def main():
    print("Generating Crypto Report...")
    
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

    # Get latest entry
    data = history[-1]
    indicators = data.get('indicators', {})
    
    timestamp = data.get('timestamp')
    symbol = data.get('symbol', 'BTC/USDT')
    
    # Extract values
    ema_13 = indicators.get('ema_13')
    ema_50 = indicators.get('ema_50')
    current_price = indicators.get('avg_price_1m')
    rsi = indicators.get('rsi_14_4h')
    
    if None in [ema_13, ema_50, current_price, rsi]:
        print("❌ Error: Missing indicator data in latest entry.")
        return False
        
    # Trade Logic
    # Enter trade will be true ONLY if:
    # 1. EMA 13 is above EMA 50
    # 2. Bitcoin price is greater than EMA 13 and EMA 50
    # 3. RSI must be below 70
    
    condition_ema_cross = ema_13 > ema_50
    condition_price_above = current_price > ema_13 and current_price > ema_50
    condition_rsi_safe = rsi < 70
    
    enter_trade = condition_ema_cross and condition_price_above and condition_rsi_safe
    
    # Format Report
    report_path = "data/crypto_report.md"
    
    with open(report_path, 'w') as f:
        f.write(f"# Crypto Analysis Report: {symbol}\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Market Data\n")
        f.write(f"- **Current Price (1m Avg):** ${current_price:,.2f}\n")
        f.write(f"- **RSI (14, 4h):** {rsi:.2f}\n")
        f.write(f"- **EMA 13 (4h):** ${ema_13:,.2f}\n")
        f.write(f"- **EMA 50 (4h):** ${ema_50:,.2f}\n\n")
        
        f.write("## Trade Analysis\n")
        f.write("| Condition | Value | Status |\n")
        f.write("|-----------|-------|--------|\n")
        f.write(f"| EMA 13 > EMA 50 | {ema_13:.2f} > {ema_50:.2f} | {'✅' if condition_ema_cross else '❌'} |\n")
        f.write(f"| Price > EMAs | ${current_price:.2f} > Both | {'✅' if condition_price_above else '❌'} |\n")
        f.write(f"| RSI < 70 | {rsi:.2f} | {'✅' if condition_rsi_safe else '❌'} |\n\n")
        
        f.write("## Signal\n")
        if enter_trade:
            f.write("### 🟢 ENTER TRADE\n")
            f.write("All conditions met.\n")
        else:
            f.write("### 🔴 NO TRADE\n")
            f.write("Market conditions not favorable.\n")
            
    print(f"\n✅ Report generated: {report_path}")
    
    # Print summary to console
    print(f"Price: ${current_price:,.2f} | RSI: {rsi:.2f}")
    print(f"Signal: {'🟢 ENTER TRADE' if enter_trade else '🔴 NO TRADE'}")
    
    return True

if __name__ == "__main__":
    if not main():
        exit(1)
