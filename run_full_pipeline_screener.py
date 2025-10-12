#!/usr/bin/env python3
"""
Stock Screener Pipeline - Extendable Architecture
Analyzes a custom set of up to 8 ticker symbols with company overview data

Add new pipeline steps to the 'steps' list below to extend functionality
"""
import subprocess
import sys
import time
from datetime import datetime

def run_step(step_name, script_path, description):
    """
    Execute a pipeline step

    Args:
        step_name: Short identifier for the step
        script_path: Path to the Python script
        description: Human-readable description

    Returns:
        bool: True if step succeeded, False if it failed
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
    print("█" + "  STOCK SCREENER - FULL PIPELINE".center(78) + "█")
    print("█" + f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(78) + "█")
    print("█"*80)

    start = time.time()

    # ============================================================================
    # PIPELINE STEPS - Add new steps here to extend the pipeline
    # ============================================================================
    steps = [
        ("01", "pipeline/screener_01_check_config.py", "Check/Create Screener Config"),
        ("02", "pipeline/screener_02_company_overview.py", "Get Company Overview (Alpha Vantage)"),
        ("03", "pipeline/screener_03_gpt_analysis.py", "AI Stock Analysis (Gemini 2.5 Pro)"),
        # Add additional steps here:
        # ("04", "pipeline/screener_04_another.py", "Another Step Description"),
    ]

    # Execute pipeline steps
    completed = 0
    for step_name, script, desc in steps:
        if run_step(step_name, script, desc):
            completed += 1
            time.sleep(0.3)  # Brief pause between steps
        else:
            print("\n⚠️  Pipeline stopped due to error")
            break

    # Summary
    elapsed = time.time() - start
    print("\n" + "="*80)
    status = '✅ COMPLETE' if completed == len(steps) else '❌ STOPPED'
    print(f"{status}: {completed}/{len(steps)} steps ({elapsed:.1f}s)")
    print("="*80)

    # Exit with error code if pipeline didn't complete
    if completed != len(steps):
        sys.exit(1)

if __name__ == "__main__":
    main()
