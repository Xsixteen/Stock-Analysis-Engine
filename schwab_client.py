"""
Schwab API Client Wrapper
Centralizes authentication and provides reusable client instances
"""
import os
import sys
from dotenv import load_dotenv
from schwab import auth

load_dotenv()


def get_schwab_client():
    """
    Create and return authenticated Schwab HTTP client

    Returns:
        schwab.client.Client: Authenticated Schwab API client

    Raises:
        SystemExit: If required environment variables are missing
    """
    api_key = os.getenv("SCHWAB_API_KEY")
    app_secret = os.getenv("SCHWAB_APP_SECRET")
    callback_url = os.getenv("SCHWAB_CALLBACK_URL", "https://127.0.0.1:8182/")
    token_path = os.getenv("SCHWAB_TOKEN_PATH", "./schwab_token.json")

    if not api_key or not app_secret:
        print("❌ Missing Schwab API credentials in environment variables")
        print("\nRequired in .env:")
        print("  SCHWAB_API_KEY=your_app_key")
        print("  SCHWAB_APP_SECRET=your_app_secret")
        print("\nGet credentials at: https://developer.schwab.com/")
        sys.exit(1)

    try:
        # easy_client handles OAuth flow and token management
        # First run: Opens browser for login, saves token
        # Subsequent runs: Reuses token, auto-refreshes when needed
        client = auth.easy_client(
            api_key=api_key,
            app_secret=app_secret,
            callback_url=callback_url,
            token_path=token_path
        )
        return client

    except Exception as e:
        print(f"❌ Failed to authenticate with Schwab API: {e}")
        print("\nTroubleshooting:")
        print("1. Verify credentials in .env are correct")
        print("2. Check that app is approved at https://developer.schwab.com/")
        print("3. If token is older than 7 days, delete schwab_token.json and re-authenticate")
        sys.exit(1)


def get_account_id():
    """
    Get Schwab account ID from environment

    Returns:
        int: Account ID (0 for market data only, no account needed)
    """
    return int(os.getenv("SCHWAB_ACCOUNT_ID", "0"))


def test_connection():
    """Test Schwab API connection and print account info"""
    print("="*60)
    print("Testing Schwab API Connection")
    print("="*60)

    print("\n📡 Authenticating...")
    client = get_schwab_client()
    print("✅ Authentication successful!")

    print("\n📊 Testing market data access...")
    try:
        # Test quote retrieval
        response = client.get_quote('AAPL')
        response.raise_for_status()

        quote_data = response.json()
        if 'AAPL' in quote_data:
            aapl = quote_data['AAPL']['quote']
            print(f"✅ AAPL Quote:")
            print(f"   Bid: ${aapl.get('bidPrice', 'N/A')}")
            print(f"   Ask: ${aapl.get('askPrice', 'N/A')}")
            print(f"   Last: ${aapl.get('lastPrice', 'N/A')}")

    except Exception as e:
        print(f"❌ Market data test failed: {e}")
        sys.exit(1)

    print("\n🎯 Testing option chain access...")
    try:
        from schwab.client import Client

        response = client.get_option_chain(
            'AAPL',
            contract_type=Client.Options.ContractType.CALL,
            strike_count=5
        )
        response.raise_for_status()

        chain_data = response.json()
        if 'callExpDateMap' in chain_data:
            num_expirations = len(chain_data['callExpDateMap'])
            print(f"✅ Option chain retrieved: {num_expirations} expirations")

    except Exception as e:
        print(f"❌ Option chain test failed: {e}")
        sys.exit(1)

    print("\n" + "="*60)
    print("✅ All tests passed! Schwab API is ready to use.")
    print("="*60)


if __name__ == "__main__":
    """Run connection test when executed directly"""
    test_connection()
