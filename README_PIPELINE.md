# Pipeline Overview - Schwab API Version

## Quick Start

```bash
# Full pipeline (all steps)
python3 run_full_pipeline.py

# Or use the master pipeline script
python3 pipeline/10_run_pipeline.py
```

---

## Pipeline Steps

### 📊 **Phase 1: Build Portfolio (Steps 00A-00F)**

**00A - Get S&P 500 Tickers**
```bash
python3 pipeline/00a_get_sp500.py
```
- Downloads S&P 500 companies from GitHub
- Extracts 503 ticker symbols
- Saves to `data/sp500.json`

**00B - Filter by Price (Schwab API)** ⭐ *Uses Schwab*
```bash
python3 pipeline/00b_filter_price_schwab.py
```
- Gets real-time quotes from Schwab API
- Filters: $30-400 price range, <2% bid/ask spread
- Saves liquid stocks to `data/filter1_passed.json`

**00C - Filter by Options (Schwab API)** ⭐ *Uses Schwab*
```bash
python3 pipeline/00c_filter_options_schwab.py
```
- Gets option chains from Schwab API
- Filters: 15-45 DTE, 20+ strikes
- Saves to `data/filter2_passed.json`

**00D - Filter by IV (Schwab API)** ⭐ *Uses Schwab*
```bash
python3 pipeline/00d_filter_iv_schwab.py
```
- Gets Greeks/IV from Schwab option chains
- Filters: IV 15-80%
- Saves to `data/filter3_passed.json`

**00E - Select Top 22**
```bash
python3 pipeline/00e_select_22.py
```
- Scores by IV (40pts), strikes (30pts), expirations (20pts), spread (10pts)
- Selects top 22 tickers
- Saves to `data/stocks.py`

**00F - Get News**
```bash
python3 pipeline/00f_get_news.py
```
- Fetches 3 days of news from Finnhub.io
- Up to 10 articles per stock
- Saves to `data/finnhub_news.json`

---

### ⚙️ **Phase 2: Build Credit Spreads (Steps 01-04)**

**01 - Get Stock Prices (Schwab API)** ⭐ *Uses Schwab*
```bash
python3 pipeline/01_get_prices_schwab.py
```
- Gets real-time bid/ask quotes from Schwab
- For top 22 stocks from step 00E
- Saves to `data/stock_prices.json`

**02 - Get Options Chains (Schwab API)** ⭐ *Uses Schwab*
```bash
python3 pipeline/02_get_chains_schwab.py
```
- Gets full option chains from Schwab
- Filters: 0-45 DTE, 70-130% strikes
- Saves strikes, symbols, quotes to `data/chains.json`

**03 - Check Liquidity**
```bash
python3 pipeline/03_check_liquidity.py
```
- Checks each strike's bid/ask
- Filters: mid >= $0.30, spread <10%
- Saves liquid strikes to `data/liquid_chains.json`

**04 - Get Greeks (Schwab API)** ⭐ *Uses Schwab*
```bash
python3 pipeline/04_get_greeks_schwab.py
```
- Gets Greeks from Schwab option chains
- Embeds IV/delta/theta/gamma/vega into chain structure
- Saves to `data/chains_with_greeks.json`

---

### 🧮 **Phase 3: Calculate & Rank (Steps 05-07)**

**05 - Calculate Spreads**
```bash
python3 pipeline/05_calculate_spreads.py
```
- Pairs strikes into Bull Put and Bear Call spreads
- Filters: short delta 15-35%, ROI 5-50%, PoP ≥60%
- Uses Black-Scholes for PoP calculation
- Saves to `data/spreads.json`

**06 - Rank Spreads**
```bash
python3 pipeline/06_rank_spreads.py
```
- Scores: (ROI × PoP) / 100
- Keeps best spread per ticker (22 total)
- Categories: ENTER (PoP≥70% + ROI≥20%), WATCH, SKIP
- Saves to `data/ranked_spreads.json`

**07 - Build Report**
```bash
python3 pipeline/07_build_report.py
```
- Selects top 9 by rank
- Adds sector mapping
- Formats report table
- Saves to `data/report_table.json`

---

### 🤖 **Phase 4: Analysis & Output (Steps 08-09)**

**08 - GPT Analysis**
```bash
python3 pipeline/08_gpt_analysis.py
```
- 5W1H analysis framework
- Heat scores 1-10 (catalyst risk)
- Trade/Wait/Skip recommendations
- Saves to `data/top9_analysis.json`

**09 - Format Trades**
```bash
python3 pipeline/09_format_trades.py
```
- Parses GPT output
- Formats table with rank, ticker, type, strikes, DTE, ROI, PoP, heat
- Saves CSV to `data/top9_trades_YYYYMMDD_HHMM.csv`

---

## Data Flow

```
S&P 500 (503)
   ↓ Price Filter (Schwab)
Liquid Stocks (~150)
   ↓ Options Filter (Schwab)
Good Chains (~80)
   ↓ IV Filter (Schwab)
IV Range (~66)
   ↓ Scoring
Top 22 Selected
   ↓ News + Chains (Schwab)
Spreads Built (~200+)
   ↓ Ranking
Top 22 (1 per ticker)
   ↓ Select Best
Top 9 for Analysis
   ↓ GPT Analysis
Final Trades
```

---

## Files Changed for Schwab Migration

### ⭐ **Schwab API Steps** (Updated):
- `pipeline/00b_filter_price_schwab.py` - Stock quotes
- `pipeline/00c_filter_options_schwab.py` - Options availability
- `pipeline/00d_filter_iv_schwab.py` - IV filtering
- `pipeline/01_get_prices_schwab.py` - Real-time prices
- `pipeline/02_get_chains_schwab.py` - Options chains
- `pipeline/04_get_greeks_schwab.py` - Greeks embedding

### ✅ **No Changes Needed**:
- `pipeline/00a_get_sp500.py` - Downloads from GitHub
- `pipeline/00e_select_22.py` - Scoring logic
- `pipeline/00f_get_news.py` - Finnhub API
- `pipeline/03_check_liquidity.py` - Math calculations
- `pipeline/05_calculate_spreads.py` - Black-Scholes
- `pipeline/06_rank_spreads.py` - Ranking logic
- `pipeline/07_build_report.py` - Formatting
- `pipeline/08_gpt_analysis.py` - OpenAI API
- `pipeline/09_format_trades.py` - Output formatting

---

## Key Differences: TastyTrade vs Schwab

| Feature | TastyTrade | Schwab |
|---------|------------|--------|
| **Quotes** | Streaming (5s batches) | Batch API (faster) |
| **Chains** | Separate streaming | Single API call |
| **Greeks** | Separate stream | Included in chains |
| **API Calls** | More, slower | Fewer, faster |
| **Data Source** | Polygon.io (stocks) | Native Schwab |

---

## Troubleshooting

**"Missing Schwab credentials"**
- Check `.env` has `SCHWAB_API_KEY` and `SCHWAB_APP_SECRET`

**"Token expired"**
- Delete `schwab_token.json` and re-authenticate
- Run `python3 schwab_client.py`

**"No data returned"**
- Verify app approved at developer.schwab.com
- Check API product is "Market Data Production"

**"Permission denied"**
- Ensure app has "Market Data Production" enabled
- Trading methods should fail (expected for read-only)

---

## Output Files

All data saved to `data/` directory:

| File | Description |
|------|-------------|
| `sp500.json` | S&P 500 tickers |
| `filter1_passed.json` | Price filter results |
| `filter2_passed.json` | Options filter results |
| `filter3_passed.json` | IV filter results |
| `stocks.py` | Top 22 selected |
| `finnhub_news.json` | News headlines |
| `stock_prices.json` | Real-time quotes |
| `chains.json` | Options chains |
| `liquid_chains.json` | Liquid strikes |
| `chains_with_greeks.json` | Chains + Greeks |
| `spreads.json` | All spreads |
| `ranked_spreads.json` | Top spreads |
| `report_table.json` | Top 9 report |
| `top9_analysis.json` | GPT analysis |
| `top9_trades_*.csv` | Final output |

---

## Performance

**Full Pipeline Time:** ~3-5 minutes
- Phase 1 (00A-00F): ~2 min
- Phase 2 (01-04): ~1 min (Schwab is faster!)
- Phase 3 (05-07): ~30 sec
- Phase 4 (08-09): ~1 min (GPT-4 call)

**Schwab vs TastyTrade Speed:**
- Schwab: ✅ Faster (batch API calls)
- TastyTrade: ⚠️ Slower (streaming + 5s windows)
