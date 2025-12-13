#!/usr/bin/env python3
"""
Crypto Pipeline - Bitcoin EMA Tracker

Modes:
1. Run Pipeline - Fetches latest EMA data and updates history
"""
import os
import subprocess
import sys
import time
from datetime import datetime

def run_step(step_name, script_path, description):
    """
    Execute a pipeline step
    """
    print("\n" + "="*80)
    print(f"▶ {step_name}: {description}")
    print("="*80)

    start = time.time()
    result = subprocess.run([sys.executable, script_path], text=True)
    elapsed = time.time() - start

    if result.returncode == 0:
        print(f"\n✅ {step_name} complete ({elapsed:.1f}s)")
        return True
    else:
        print(f"\n❌ {step_name} FAILED ({elapsed:.1f}s)")
        return False

def main():
    print("\n" + "█"*80)
    print("█" + "  CRYPTO PIPELINE (BTC EMA)".center(78) + "█")
    print("█" + f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(78) + "█")
    print("█"*80)
    print()

    # Pipeline steps
    steps = [
        ("01", "pipeline/crypto_01_ema.py", "Fetch Bitcoin EMA (13d & 50d)"),
        ("02", "pipeline/crypto_02_currentprice.py", "Fetch Bitcoin Avg Price (1m)"),
        ("03", "pipeline/crypto_03_rsi.py", "Fetch Bitcoin RSI (14, 4h)"),
        ("04", "pipeline/crypto_04_report.py", "Generate Signal Report"),
    ]

    print(f"Steps: {len(steps)}")
    print("="*80)

    start = time.time()

    # Execute pipeline steps
    completed = 0
    for step_name, script, desc in steps:
        if run_step(step_name, script, desc):
            completed += 1
            time.sleep(0.3)
        else:
            print("\n⚠️  Pipeline stopped due to error")
            break

    # Summary
    elapsed = time.time() - start
    print("\n" + "="*80)
    status = '✅ COMPLETE' if completed == len(steps) else '❌ STOPPED'
    print(f"{status}: {completed}/{len(steps)} steps ({elapsed:.1f}s)")
    
    minutes = int(elapsed / 60)
    seconds = int(elapsed % 60)
    print(f"Total Time: {minutes}m {seconds}s")
    print("="*80)

    if completed != len(steps):
        sys.exit(1)

if __name__ == "__main__":
    main()
