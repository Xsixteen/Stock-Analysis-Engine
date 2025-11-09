# Migration Summary: TastyTrade → Charles Schwab API

## ✅ Migration Complete - Files Ready

### What Was Created:

#### 1. **Core Infrastructure**
- ✅ `schwab_client.py` - Authentication helper with connection testing
- ✅ Updated `.env` / `.env.example` - New Schwab credentials format
- ✅ Updated `.gitignore` - Added `schwab_token.json`
- ✅ Updated `requirements.txt` - Replaced `tastytrade` with `schwab-py`

#### 2. **Migrated Pipeline Files** (Schwab versions created)
- ✅ `pipeline/00b_filter_price_schwab.py` - Stock quote filtering
- ✅ `pipeline/01_get_prices_schwab.py` - Real-time stock prices
- ✅ `pipeline/00c_filter_options_schwab.py` - Options availability filter
- ✅ `pipeline/02_get_chains_schwab.py` - Options chain retrieval
- ✅ `pipeline/00d_filter_iv_schwab.py` - IV filtering with Greeks
- ✅ `pipeline/04_get_greeks_schwab.py` - Greeks embedding

#### 3. **Documentation**
- ✅ `MIGRATION_GUIDE.md` - Complete migration instructions
- ✅ `MIGRATION_SUMMARY.md` - This file

---

## 📋 Next Steps (You Need To Do):

### Step 1: Register Schwab Developer Account
1. Go to https://developer.schwab.com/
2. Create developer account
3. Create new app with these settings:
   - **Callback URL:** `https://127.0.0.1:8182/`
   - **App Name:** Credit Spread Finder
4. Save your **App Key** and **App Secret**
5. **Wait 2-3 days** for approval

### Step 2: Configure Environment
Edit `.env` and add your Schwab credentials:
```bash
SCHWAB_API_KEY=your_app_key_here
SCHWAB_APP_SECRET=your_app_secret_here
```

### Step 3: Install Dependencies
```bash
pip install schwab-py>=1.5.0
```

### Step 4: Test Authentication
```bash
python3 schwab_client.py
```
- Opens browser for OAuth login
- Saves token to `schwab_token.json`
- Tests quote and option chain access

### Step 5: Test Individual Steps
```bash
# Test stock quotes
python3 pipeline/00b_filter_price_schwab.py

# Test options chains
python3 pipeline/00c_filter_options_schwab.py

# Test Greeks/IV
python3 pipeline/00d_filter_iv_schwab.py
```

---

## 🔄 File Comparison: Old vs New

### Stock Quotes (00b, 01)

**OLD (TastyTrade):**
- Uses `DXLinkStreamer` for async streaming
- Processes batches of 50 symbols
- 5-second collection window per batch
- Requires username/password

**NEW (Schwab):**
- Uses `get_quotes()` for batch requests
- Processes batches of 100 symbols
- Single API call per batch (faster)
- OAuth2 authentication

### Options Chains (00c, 02)

**OLD (TastyTrade):**
```python
chain = get_option_chain(sess, 'AAPL')
# Returns: {datetime.date: [Option objects]}
```

**NEW (Schwab):**
```python
response = client.get_option_chain('AAPL')
chain = response.json()
# Returns: {"callExpDateMap": {...}, "putExpDateMap": {...}}
```

### Greeks (00d, 04)

**OLD (TastyTrade):**
- Separate streaming call for Greeks
- Subscribe to option symbols
- Async event loop
- Greeks in separate data stream

**NEW (Schwab):**
- Greeks **included in option chain response**
- Single API call gets quotes + Greeks
- No separate streaming needed
- More efficient (fewer API calls)

---

## 🔑 Key Improvements

| Feature | TastyTrade | Schwab |
|---------|------------|--------|
| **Market Data** | Via Polygon.io (3rd party) | Native Schwab data |
| **API Calls** | Multiple streaming calls | Fewer batch calls |
| **Greeks** | Separate stream | Included in chains |
| **Auth** | Username/password | OAuth2 (more secure) |
| **Futures** | ❌ No market data | ✅ Full support |
| **Read-Only** | Not enforced | ✅ API permissions |

---

## 📁 Files You Can Delete (After Testing)

Once Schwab migration is confirmed working:
- ❌ `pipeline/00b_filter_price.py` (old TastyTrade)
- ❌ `pipeline/01_get_prices.py` (old TastyTrade)
- ❌ `pipeline/00c_filter_options.py` (old TastyTrade)
- ❌ `pipeline/02_get_chains.py` (old TastyTrade)
- ❌ `pipeline/00d_filter_iv.py` (old TastyTrade)
- ❌ `pipeline/04_get_greeks.py` (old TastyTrade)

**Rename Schwab files to replace them:**
```bash
mv pipeline/00b_filter_price_schwab.py pipeline/00b_filter_price.py
mv pipeline/01_get_prices_schwab.py pipeline/01_get_prices.py
mv pipeline/00c_filter_options_schwab.py pipeline/00c_filter_options.py
mv pipeline/02_get_chains_schwab.py pipeline/02_get_chains.py
mv pipeline/00d_filter_iv_schwab.py pipeline/00d_filter_iv.py
mv pipeline/04_get_greeks_schwab.py pipeline/04_get_greeks.py
```

---

## 🧪 Testing Checklist

- [ ] Schwab developer account created
- [ ] App registered and approved (2-3 days)
- [ ] Credentials added to `.env`
- [ ] `pip install schwab-py` completed
- [ ] `python3 schwab_client.py` - Auth test passed
- [ ] Step 00a: S&P 500 tickers (no changes needed)
- [ ] Step 00b: Price filter with Schwab
- [ ] Step 00c: Options filter with Schwab
- [ ] Step 00d: IV filter with Schwab
- [ ] Step 00e: Select 22 (no changes needed)
- [ ] Step 00f: News (no changes needed)
- [ ] Step 01: Stock prices with Schwab
- [ ] Step 02: Options chains with Schwab
- [ ] Step 03: Liquidity check (no changes needed)
- [ ] Step 04: Greeks with Schwab
- [ ] Steps 05-09: Calculations (no changes needed)
- [ ] Full pipeline: `python3 pipeline/10_run_pipeline.py`

---

## ⚠️ Important Notes

### Token Management
- Token stored in `schwab_token.json` (gitignored)
- Auto-refreshes every 30 minutes
- Expires after 7 days of inactivity
- Delete and re-authenticate if expired

### Data Format Changes
- **Option chains** now in JSON format (was Python objects)
- **Greeks** embedded in chains (was separate stream)
- **Symbols** may have different format
- All downstream steps (05-09) should work unchanged

### No Changes Needed
These steps work with both TastyTrade and Schwab data:
- ✅ Step 00a: Get S&P 500 tickers
- ✅ Step 00e: Select top 22
- ✅ Step 00f: Get news
- ✅ Step 03: Check liquidity
- ✅ Steps 05-09: Calculations and reporting

---

## 🆘 Troubleshooting

**OAuth login fails:**
- Check callback URL matches exactly: `https://127.0.0.1:8182/`
- Ensure app is approved (not "Pending")

**"Invalid token" error:**
- Delete `schwab_token.json` and re-authenticate
- Tokens expire after 7 days

**"No data" errors:**
- Verify Schwab account has market data permissions
- Some data may have 15-min delay (check agreement)

**API rate limits:**
- Schwab: 120 requests/minute
- Add delays if hitting limits

---

## 📚 Resources

- **Schwab Dev Portal:** https://developer.schwab.com/
- **schwab-py Docs:** https://schwab-py.readthedocs.io/
- **schwab-py GitHub:** https://github.com/alexgolec/schwab-py
- **Migration Guide:** See `MIGRATION_GUIDE.md`
