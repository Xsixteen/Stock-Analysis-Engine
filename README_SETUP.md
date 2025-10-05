# Environment Setup Guide

## Prerequisites
- Python 3.9+
- TastyTrade account
- OpenAI API key
- Finnhub API key

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**

Copy the example file:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```bash
# TastyTrade API Credentials
TASTYTRADE_USERNAME=your_tastytrade_username
TASTYTRADE_PASSWORD=your_tastytrade_password

# OpenAI API Key (for GPT-4 news analysis)
OPENAI_API_KEY=sk-your-openai-api-key

# Finnhub API Key (for news headlines)
FINNHUB_API_KEY=your_finnhub_api_key
```

## Security Notes

- **Never commit `.env` to git** - it's already in `.gitignore`
- The `.env` file contains sensitive credentials
- Share `.env.example` with your team, not `.env`
- All API keys should be kept secret

## Running the Pipeline

After setting up environment variables:
```bash
python3 pipeline/10_run_pipeline.py
```

Or run individual steps:
```bash
python3 pipeline/00a_get_sp500.py
python3 pipeline/00b_filter_price.py
# etc...
```
