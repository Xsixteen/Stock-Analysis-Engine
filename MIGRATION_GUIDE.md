# Migration Guide: TastyTrade → Charles Schwab API

## Table of Contents
1. [Overview](#overview)
2. [Why Migrate?](#why-migrate)
3. [Prerequisites](#prerequisites)
4. [API Comparison](#api-comparison)
5. [Migration Steps](#migration-steps)
6. [Code Changes](#code-changes)

---

## Overview

This guide details the migration from TastyTrade API to Charles Schwab API for read-only market data access.

**Timeline:** 2-3 hours of work + 2-3 days waiting for Schwab API approval

---

## Why Migrate?

### Charles Schwab Advantages:
✅ **Native market data** - No third-party dependencies (TastyTrade uses Polygon.io)
✅ **Read-only enforcement** - API permissions prevent accidental trades
✅ **Better coverage** - Stocks, options, AND futures (TastyTrade lacks futures data)
✅ **No minimum balance** - Free API access
✅ **Official support** - developer.schwab.com with documentation
✅ **OAuth2 security** - More secure than username/password

### Current TastyTrade Limitations:
⚠️ Stock quotes require third-party Polygon.io
⚠️ No futures market data through API
⚠️ Username/password authentication (less secure)

---

## Prerequisites

### 1. Create Schwab Developer Account

1. Go to https://developer.schwab.com/
2. Click "Register" and create a developer account (separate from brokerage account)
3. Create a new app:
   - **App Name:** Credit Spread Finder
   - **Callback URL:** `https://127.0.0.1:8182/`
   - **Description:** Options credit spread analysis tool
4. Save your credentials:
   - **App Key** (API Key)
   - **App Secret**
5. Wait 2-3 days for approval (status changes from "Approved - Pending" to "Ready For Use")

### 2. Link Schwab Brokerage Account (Optional)

- You can link your existing Schwab brokerage account for account data
- Not required for market data only

---

## API Comparison

### Authentication

| Feature | TastyTrade | Schwab |
|---------|------------|--------|
| Method | Username/Password | OAuth2 |
| Token Lifetime | Session-based | 30 min access + 7 day refresh |
| Auto-refresh | ✅ Yes | ✅ Yes |
| Security | Medium | High |

### Stock Quotes

**TastyTrade:**
```python
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Quote

sess = Session(username, password)
async with DXLinkStreamer(sess) as streamer:
    await streamer.subscribe(Quote, ['AAPL', 'MSFT'])
    quote = await streamer.get_event(Quote)
    bid = quote.bid_price
    ask = quote.ask_price
```

**Schwab:**
```python
from schwab import auth
from schwab.streaming import StreamClient

client = auth.easy_client(api_key, app_secret, callback_url, token_path)
stream = StreamClient(client, account_id=0)

await stream.login()
await stream.level_one_equity_subs(['AAPL', 'MSFT'])
# Handler receives: {'BID_PRICE': 150.25, 'ASK_PRICE': 150.30, ...}
```

### Options Chains

**TastyTrade:**
```python
from tastytrade.instruments import get_option_chain

chain = get_option_chain(sess, 'AAPL')
# Returns: {datetime.date: [Option objects]}
```

**Schwab:**
```python
from schwab.client import Client

response = client.get_option_chain('AAPL',
    contract_type=Client.Options.ContractType.ALL,
    strike_count=20)
chain = response.json()
# Returns: JSON with callExpDateMap, putExpDateMap
```

### Greeks & IV

**TastyTrade:**
```python
from tastytrade.dxfeed import Greeks

async with DXLinkStreamer(sess) as streamer:
    await streamer.subscribe(Greeks, ['.AAPL250117C150'])
    greeks = await streamer.get_event(Greeks)
    iv = greeks.volatility
    delta = greeks.delta
```

**Schwab:**
```python
# Greeks included in option chain response
response = client.get_option_chain('AAPL')
chain = response.json()
# Each option contains: delta, gamma, theta, vega, rho, volatility
```

---

## Migration Steps

### Step 1: Update Requirements

**File:** `requirements.txt`

**Remove:**
```
tastytrade>=10.0.0
```

**Add:**
```
schwab-py>=1.5.0
```

**Install:**
```bash
pip install schwab-py
```

### Step 2: Update Environment Variables

**File:** `.env`

**Remove:**
```bash
TASTYTRADE_USERNAME=
TASTYTRADE_PASSWORD=
```

**Add:**
```bash
# Charles Schwab API Credentials
SCHWAB_API_KEY=your_app_key_here
SCHWAB_APP_SECRET=your_app_secret_here
SCHWAB_CALLBACK_URL=https://127.0.0.1:8182/
SCHWAB_TOKEN_PATH=/Users/Eric/GitHub/News_Spread_Engine/schwab_token.json
SCHWAB_ACCOUNT_ID=0
```

**File:** `.env.example`

Update to match new variables.

### Step 3: Create Schwab Client Helper

**File:** `schwab_client.py` (NEW)

This module will centralize Schwab API authentication and provide reusable clients.

### Step 4: Migrate Pipeline Files

Update the following files in order:

1. ✅ `pipeline/00b_filter_price.py` - Stock quotes
2. ✅ `pipeline/01_get_prices.py` - Stock quotes
3. ✅ `pipeline/00c_filter_options.py` - Options chains
4. ✅ `pipeline/02_get_chains.py` - Options chains
5. ✅ `pipeline/00d_filter_iv.py` - Greeks/IV
6. ✅ `pipeline/04_get_greeks.py` - Greeks/IV

### Step 5: Test Authentication

```bash
python3 schwab_client.py
```

First run will:
1. Open browser for OAuth login
2. Redirect to localhost callback
3. Save token to `schwab_token.json`

Subsequent runs will reuse the token (auto-refreshes every 30 min).

### Step 6: Test Each Pipeline Step

```bash
python3 pipeline/00a_get_sp500.py
python3 pipeline/00b_filter_price.py  # First Schwab API call
# Verify output in data/filter1_passed.json
```

Continue testing each step sequentially.

---

## Code Changes

### Key Differences

| Aspect | TastyTrade | Schwab |
|--------|------------|--------|
| **Import** | `from tastytrade import Session` | `from schwab import auth` |
| **Auth** | `Session(user, pass)` | `auth.easy_client(key, secret, ...)` |
| **Streaming** | `DXLinkStreamer(session)` | `StreamClient(client, account_id)` |
| **Quote Subscribe** | `subscribe(Quote, symbols)` | `level_one_equity_subs(symbols)` |
| **Option Chain** | `get_option_chain(sess, ticker)` | `client.get_option_chain(ticker)` |
| **Greeks** | Streamed via `Greeks` events | Included in option chain JSON |
| **Data Format** | Python objects | JSON (need to parse) |

### Data Structure Changes

**TastyTrade Option Chain:**
```python
{
    datetime.date(2025, 1, 17): [
        Option(strike=150, symbol='.AAPL250117C150', ...),
        Option(strike=155, symbol='.AAPL250117C155', ...)
    ]
}
```

**Schwab Option Chain:**
```json
{
    "callExpDateMap": {
        "2025-01-17:45": {
            "150.0": [{
                "symbol": "AAPL_011725C150",
                "delta": 0.52,
                "gamma": 0.03,
                "theta": -0.15,
                "vega": 0.12,
                "volatility": 0.28,
                "bid": 5.20,
                "ask": 5.30
            }]
        }
    }
}
```

---

## Testing Checklist

- [ ] Schwab developer account approved
- [ ] OAuth authentication successful
- [ ] Token saved to `schwab_token.json`
- [ ] Step 00a: S&P 500 tickers (no change)
- [ ] Step 00b: Price filter with Schwab quotes
- [ ] Step 00c: Options filter with Schwab chains
- [ ] Step 00d: IV filter with Schwab Greeks
- [ ] Step 00e: Select 22 (no change)
- [ ] Step 00f: News (no change)
- [ ] Step 01: Stock prices with Schwab
- [ ] Step 02: Options chains with Schwab
- [ ] Step 03: Liquidity check (no change)
- [ ] Step 04: Greeks with Schwab
- [ ] Steps 05-09: Calculations (no change)
- [ ] Full pipeline run: `python3 pipeline/10_run_pipeline.py`

---

## Rollback Plan

If migration fails, restore TastyTrade:

```bash
git checkout .env
git checkout requirements.txt
git checkout pipeline/
pip install tastytrade>=10.0.0
```

---

## Support Resources

- **Schwab API Docs:** https://developer.schwab.com/
- **schwab-py Docs:** https://schwab-py.readthedocs.io/
- **schwab-py GitHub:** https://github.com/alexgolec/schwab-py
- **Discord:** schwab-py has a Discord for support

---

## Security Notes

🔒 **Important:**
- Token file (`schwab_token.json`) contains sensitive data - added to `.gitignore`
- Refresh tokens expire after 7 days of inactivity
- OAuth2 is more secure than username/password
- API can be configured as read-only (no trading permissions)
