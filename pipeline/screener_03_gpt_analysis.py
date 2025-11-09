#!/usr/bin/env python3
"""
Screener Pipeline Step 03: AI Stock Analysis with Gemini 2.5 Pro
Analyzes each stock from overview.json using both fundamental and technical analysis
Includes RSI and SMA analysis to determine optimal entry points
Requires GEMINI_API_KEY in .env file
"""
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def load_overview_data():
    """Load stock overview data from overview.json"""
    with open("data/overview.json", "r") as f:
        data = json.load(f)
    return data["data"]

def load_static_data():
    """Load financial statement data from static_data.json"""
    try:
        with open("data/static_data.json", "r") as f:
            data = json.load(f)
            return data.get("data", {})
    except FileNotFoundError:
        print("⚠️  Warning: static_data.json not found. Analysis will proceed without financial statements.")
        return {}

def load_daily_data():
    """Load daily quote data from daily_data.json"""
    try:
        with open("data/daily_data.json", "r") as f:
            data = json.load(f)
            return data.get("data", {})
    except FileNotFoundError:
        print("⚠️  Warning: daily_data.json not found. Analysis will proceed without current price/volume data.")
        return {}

def analyze_stock_with_gemini(ticker, stock_data, static_data, daily_data, model):
    """
    Analyze a stock using Gemini 2.5 Pro

    Args:
        ticker: Stock symbol
        stock_data: Company overview data
        static_data: Financial statement data (income, balance sheet, cash flow)
        daily_data: Current quote data (price, volume, change)
        model: Gemini model instance

    Returns:
        dict: Analysis results from Gemini
    """
    # Skip stocks with errors
    if "error" in stock_data:
        return {"error": stock_data["error"]}

    # Extract technical indicators
    technical_indicators = stock_data.get('technical_indicators', {})
    sma_data = technical_indicators.get('SMA_50', {})
    rsi_data = technical_indicators.get('RSI_14', {})

    # Extract daily quote data
    ticker_daily = daily_data.get(ticker, {})
    current_price = ticker_daily.get('price', stock_data.get('50DayMovingAverage', 'N/A'))
    current_volume = ticker_daily.get('volume', 'N/A')
    price_change = ticker_daily.get('change', 'N/A')
    price_change_percent = ticker_daily.get('change_percent', 'N/A')
    trading_day = ticker_daily.get('latest_trading_day', 'N/A')
    day_open = ticker_daily.get('open', 'N/A')
    day_high = ticker_daily.get('high', 'N/A')
    day_low = ticker_daily.get('low', 'N/A')

    # Extract financial statement data
    ticker_static = static_data.get(ticker, {})
    income_statement = ticker_static.get('income_statement', {})
    balance_sheet = ticker_static.get('balance_sheet', {})
    cash_flow = ticker_static.get('cash_flow', {})

    # Get most recent annual reports (first item in array)
    recent_income_annual = {}
    recent_balance_annual = {}
    recent_cash_flow_annual = {}

    if not isinstance(income_statement, dict) or "error" not in income_statement:
        annual_reports = income_statement.get('annualReports', [])
        if annual_reports:
            recent_income_annual = annual_reports[0]

    if not isinstance(balance_sheet, dict) or "error" not in balance_sheet:
        annual_reports = balance_sheet.get('annualReports', [])
        if annual_reports:
            recent_balance_annual = annual_reports[0]

    if not isinstance(cash_flow, dict) or "error" not in cash_flow:
        annual_reports = cash_flow.get('annualReports', [])
        if annual_reports:
            recent_cash_flow_annual = annual_reports[0]

    # Prepare the analysis prompt with stock data
    prompt = f"""You are an expert stock analyst. Apply both fundamental and technical analysis to rate this stock from 1 to 10 where 10 is high quality and 1 is low quality. Determine strengths and weaknesses, if it is undervalued or overvalued, assess the company's financial health, and whether the current price is a good entry point.

Stock: {ticker}
Company: {stock_data.get('Name', 'N/A')}
Sector: {stock_data.get('Sector', 'N/A')}
Industry: {stock_data.get('Industry', 'N/A')}

Financial Metrics:
- Market Cap: ${stock_data.get('MarketCapitalization', 'N/A')}
- P/E Ratio: {stock_data.get('PERatio', 'N/A')}
- PEG Ratio: {stock_data.get('PEGRatio', 'N/A')}
- EPS: ${stock_data.get('EPS', 'N/A')}
- Revenue (TTM): ${stock_data.get('RevenueTTM', 'N/A')}
- Profit Margin: {stock_data.get('ProfitMargin', 'N/A')}
- Operating Margin: {stock_data.get('OperatingMarginTTM', 'N/A')}
- ROE: {stock_data.get('ReturnOnEquityTTM', 'N/A')}
- ROA: {stock_data.get('ReturnOnAssetsTTM', 'N/A')}
- Quarterly Revenue Growth YOY: {stock_data.get('QuarterlyRevenueGrowthYOY', 'N/A')}
- Quarterly Earnings Growth YOY: {stock_data.get('QuarterlyEarningsGrowthYOY', 'N/A')}

Valuation:
- Price to Book: {stock_data.get('PriceToBookRatio', 'N/A')}
- Price to Sales: {stock_data.get('PriceToSalesRatioTTM', 'N/A')}
- EV to Revenue: {stock_data.get('EVToRevenue', 'N/A')}
- EV to EBITDA: {stock_data.get('EVToEBITDA', 'N/A')}

Current Price & Volume Data (as of {trading_day}):
- Current Price: ${current_price}
- Day Open: ${day_open}
- Day High: ${day_high}
- Day Low: ${day_low}
- Volume: {current_volume}
- Price Change: ${price_change} ({price_change_percent})

Technical Indicators:
- SMA (50-day): ${sma_data.get('value', 'N/A')} (as of {sma_data.get('latest_date', 'N/A')})
- RSI (14-day): {rsi_data.get('value', 'N/A')} (as of {rsi_data.get('latest_date', 'N/A')})
- 52-Week High: ${stock_data.get('52WeekHigh', 'N/A')}
- 52-Week Low: ${stock_data.get('52WeekLow', 'N/A')}

Analyst Ratings:
- Strong Buy: {stock_data.get('AnalystRatingStrongBuy', 'N/A')}
- Buy: {stock_data.get('AnalystRatingBuy', 'N/A')}
- Hold: {stock_data.get('AnalystRatingHold', 'N/A')}
- Sell: {stock_data.get('AnalystRatingSell', 'N/A')}
- Target Price: ${stock_data.get('AnalystTargetPrice', 'N/A')}

Financial Statements (Most Recent Annual Report):
Income Statement (Fiscal Year Ending: {recent_income_annual.get('fiscalDateEnding', 'N/A')}):
- Total Revenue: ${recent_income_annual.get('totalRevenue', 'N/A')}
- Gross Profit: ${recent_income_annual.get('grossProfit', 'N/A')}
- Operating Income: ${recent_income_annual.get('operatingIncome', 'N/A')}
- Net Income: ${recent_income_annual.get('netIncome', 'N/A')}
- EBITDA: ${recent_income_annual.get('ebitda', 'N/A')}
- Research & Development: ${recent_income_annual.get('researchAndDevelopment', 'N/A')}

Balance Sheet (Fiscal Year Ending: {recent_balance_annual.get('fiscalDateEnding', 'N/A')}):
- Total Assets: ${recent_balance_annual.get('totalAssets', 'N/A')}
- Total Current Assets: ${recent_balance_annual.get('totalCurrentAssets', 'N/A')}
- Total Liabilities: ${recent_balance_annual.get('totalLiabilities', 'N/A')}
- Total Current Liabilities: ${recent_balance_annual.get('totalCurrentLiabilities', 'N/A')}
- Total Shareholder Equity: ${recent_balance_annual.get('totalShareholderEquity', 'N/A')}
- Cash and Cash Equivalents: ${recent_balance_annual.get('cashAndCashEquivalentsAtCarryingValue', 'N/A')}
- Short Term Debt: ${recent_balance_annual.get('shortTermDebt', 'N/A')}
- Long Term Debt: ${recent_balance_annual.get('longTermDebt', 'N/A')}

Cash Flow (Fiscal Year Ending: {recent_cash_flow_annual.get('fiscalDateEnding', 'N/A')}):
- Operating Cash Flow: ${recent_cash_flow_annual.get('operatingCashflow', 'N/A')}
- Capital Expenditures: ${recent_cash_flow_annual.get('capitalExpenditures', 'N/A')}
- Free Cash Flow: ${recent_cash_flow_annual.get('operatingCashflow', 'N/A')} - ${recent_cash_flow_annual.get('capitalExpenditures', 'N/A')}
- Dividend Payout: ${recent_cash_flow_annual.get('dividendPayout', 'N/A')}
- Change in Cash and Cash Equivalents: ${recent_cash_flow_annual.get('changeInCashAndCashEquivalents', 'N/A')}

ANALYSIS INSTRUCTIONS:
1. Use RSI to assess momentum (RSI < 30 = oversold, RSI > 70 = overbought, 30-70 = neutral)
2. Compare current price to SMA-50 (price above SMA = bullish, below = bearish)
3. Evaluate if current price is near 52-week high or low
4. Analyze current trading volume and intraday price action:
   - Compare current volume to average volume (high volume = strong interest/conviction)
   - Evaluate intraday range (high-low spread indicates volatility)
   - Assess price change and direction (positive/negative momentum)
5. Combine technical signals with fundamental valuation
6. Determine if this is a good entry point for buying
7. Assess company financial health using:
   - Liquidity ratios (current assets vs current liabilities)
   - Debt levels (short-term and long-term debt relative to equity)
   - Cash flow strength (operating cash flow and free cash flow)
   - Revenue and earnings trends
   - Profitability metrics (gross profit, operating income, net income margins)

Please provide your analysis in the following JSON format:
{{
  "rating": <number 1-10>,
  "valuation": "<undervalued|fairly_valued|overvalued>",
  "buy_signal": "<strong_buy|buy|hold|sell|strong_sell>",
  "entry_point_quality": "<excellent|good|fair|poor>",
  "company_health": "<excellent|good|fair|poor|concerning>",
  "strengths": ["<strength 1>", "<strength 2>", ...],
  "weaknesses": ["<weakness 1>", "<weakness 2>", ...],
  "technical_summary": "<brief assessment of RSI, SMA, and price action>",
  "financial_health_summary": "<brief assessment of balance sheet strength, debt levels, cash flow, and overall financial stability>",
  "summary": "<brief overall assessment including whether now is a good time to buy>"
}}"""

    try:
        response = model.generate_content(prompt)

        # Extract JSON from response
        response_text = response.text.strip()

        # Try to parse JSON from response
        # Sometimes the model wraps JSON in markdown code blocks
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()

        analysis = json.loads(response_text)
        return analysis

    except json.JSONDecodeError as e:
        return {
            "error": f"Failed to parse JSON response: {e}",
            "raw_response": response_text
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    print("="*60)
    print("SCREENER STEP 03: AI Stock Analysis (Gemini 2.5 Flash)")
    print("="*60)

    try:
        # Get API key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")

        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        # Load overview data
        overview_data = load_overview_data()

        # Load static data (financial statements)
        static_data = load_static_data()

        # Load daily data (current quotes)
        daily_data = load_daily_data()

        print(f"\n🤖 Analyzing {len(overview_data)} stocks with Gemini AI...")
        if static_data:
            print(f"   Including financial statement data for enhanced analysis...")
        if daily_data:
            print(f"   Including current price and volume data...")

        # Analyze each stock
        analyses = {}
        for i, (ticker, stock_data) in enumerate(overview_data.items(), 1):
            print(f"  [{i}/{len(overview_data)}] Analyzing {ticker}...", end=" ")

            analysis = analyze_stock_with_gemini(ticker, stock_data, static_data, daily_data, model)
            analyses[ticker] = analysis

            if "error" in analysis:
                print(f"✗ ({analysis['error']})")
            else:
                rating = analysis.get('rating', 'N/A')
                valuation = analysis.get('valuation', 'N/A')
                buy_signal = analysis.get('buy_signal', 'N/A')
                entry_quality = analysis.get('entry_point_quality', 'N/A')
                company_health = analysis.get('company_health', 'N/A')
                print(f"✓ (Rating: {rating}/10, {valuation}, {buy_signal}, Health: {company_health})")

        # Save results
        output = {
            "timestamp": datetime.now().isoformat(),
            "model": "gemini-2.5-flash",
            "count": len(overview_data),
            "analyses": analyses
        }

        with open("data/gpt_analysis.json", "w") as f:
            json.dump(output, f, indent=2)

        # Summary
        successful = sum(1 for v in analyses.values() if "error" not in v)
        print(f"\n✓ Completed: {successful}/{len(overview_data)} successful")
        print(f"  Saved to: data/gpt_analysis.json")
        print("\nStep 03 complete")

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        exit(1)

if __name__ == "__main__":
    main()
