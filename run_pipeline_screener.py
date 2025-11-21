#!/usr/bin/env python3
"""
Stock Screener Pipeline - Interactive Mode Selection

Modes:
1. Full Pipeline - Runs all steps (initial setup + data collection + analysis)
2. Update Only - Refreshes daily data and re-runs analysis (faster daily updates)
3. Update Static Data - Refreshes financial statements (deletes & re-fetches static data)

Add new pipeline steps to the 'full_steps', 'update_steps', or 'static_steps' lists below
"""
import os
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

def get_user_choice():
    """
    Prompt user to select pipeline mode

    Returns:
        str: 'full', 'update', or 'static'
    """
    print("\n" + "█"*80)
    print("█" + "  STOCK SCREENER PIPELINE".center(78) + "█")
    print("█" + f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(78) + "█")
    print("█"*80)
    print()
    print("Select Pipeline Mode:")
    print()
    print("  [1] Full Pipeline")
    print("      • Runs all steps from scratch")
    print("      • Use for initial setup or complete refresh")
    print("      • Steps: Config → Overview → Financial Statements → Daily Data → AI Analysis → Report")
    print("      • Time: ~10-15 minutes (depends on API rate limits)")
    print()
    print("  [2] Update Only")
    print("      • Updates daily data and re-runs analysis")
    print("      • Use for daily updates with existing data")
    print("      • Steps: Daily Data → AI Analysis → Report")
    print("      • Time: ~2-3 minutes")
    print()
    print("  [3] Update Static Data")
    print("      • Refreshes financial statements (income, balance sheet, cash flow)")
    print("      • Use when you need to update fundamental company data")
    print("      • Steps: Financial Statements")
    print("      • Time: ~5-10 minutes (depends on number of tickers)")
    print()

    while True:
        choice = input("Enter your choice (1, 2, or 3): ").strip()
        if choice == "1":
            return "full"
        elif choice == "2":
            return "update"
        elif choice == "3":
            return "static"
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

def main():
    # Get user's choice
    mode = get_user_choice()

    # ============================================================================
    # PIPELINE STEPS CONFIGURATION
    # ============================================================================

    # Full pipeline - all steps
    full_steps = [
        ("01", "pipeline/screener_01_check_config.py", "Check/Create Screener Config"),
        ("02", "pipeline/screener_02_company_overview.py", "Get Company Overview (Alpha Vantage)"),
        ("02b", "pipeline/screener_02b_static_data.py", "Get Financial Statements (Alpha Vantage)"),
        ("02c", "pipeline/screener_02c_daily_data.py", "Get Latest Quote Data (Alpha Vantage)"),
        ("03", "pipeline/screener_03_gpt_analysis.py", "AI Stock Analysis (Gemini 2.5 Pro)"),
        ("04", "pipeline/screener_04_markdown_report.py", "Generate Markdown Report"),
    ]

    # Update only pipeline - daily refresh
    update_steps = [
        ("02c", "pipeline/screener_02c_daily_data.py", "Get Latest Quote Data (Alpha Vantage)"),
        ("03", "pipeline/screener_03_gpt_analysis.py", "AI Stock Analysis (Gemini 2.5 Pro)"),
        ("04", "pipeline/screener_04_markdown_report.py", "Generate Markdown Report"),
    ]

    # Static data update - refresh financial statements
    static_steps = [
        ("02b", "pipeline/screener_02b_static_data.py", "Get Financial Statements (Alpha Vantage)"),
    ]

    # Select steps based on mode
    if mode == "full":
        steps = full_steps
        mode_name = "FULL PIPELINE"
    elif mode == "update":
        steps = update_steps
        mode_name = "UPDATE ONLY"
    else:  # mode == "static"
        steps = static_steps
        mode_name = "UPDATE STATIC DATA"

        # Delete static_data.json if it exists
        static_data_path = "data/static_data.json"
        if os.path.exists(static_data_path):
            print("\n" + "="*80)
            print(f"Removing existing {static_data_path}...")
            os.remove(static_data_path)
            print(f"✓ {static_data_path} deleted")
            print("="*80)

    # Display selected mode
    print("\n" + "="*80)
    print(f"Running: {mode_name}")
    print(f"Steps: {len(steps)}")
    print("="*80)

    start = time.time()

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

    # Show time estimate
    minutes = int(elapsed / 60)
    seconds = int(elapsed % 60)
    print(f"Total Time: {minutes}m {seconds}s")
    print("="*80)

    # Exit with error code if pipeline didn't complete
    if completed != len(steps):
        sys.exit(1)

if __name__ == "__main__":
    main()
