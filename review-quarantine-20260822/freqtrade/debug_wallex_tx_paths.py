import os
import sys, json
sys.path.insert(0, '/opt/ccxt-new/python')
from ccxt.wallex import wallex

API_KEY = os.getenv('WALLEX_API_KEY', '')

exchange = wallex({
    'apiKey': API_KEY,
    'enableRateLimit': True
})

try:
    print("Connecting to Wallex...")
    exchange.load_markets()
    
    # تست مسیر اول: transactions
    print("\n--- Testing /v1/account/transactions ---")
    try:
        resp1 = exchange.request('v1/account/transactions', 'private', 'GET', {})
        print(json.dumps(resp1, indent=2, ensure_ascii=False)[:500])
    except Exception as e:
        print(f"Failed: {e}")

    # تست مسیر دوم: deposits
    print("\n--- Testing /v1/account/deposits ---")
    try:
        resp2 = exchange.request('v1/account/deposits', 'private', 'GET', {})
        print(json.dumps(resp2, indent=2, ensure_ascii=False)[:500])
    except Exception as e:
        print(f"Failed: {e}")

    # تست مسیر سوم: withdraws
    print("\n--- Testing /v1/account/withdraws ---")
    try:
        resp3 = exchange.request('v1/account/withdraws', 'private', 'GET', {})
        print(json.dumps(resp3, indent=2, ensure_ascii=False)[:500])
    except Exception as e:
        print(f"Failed: {e}")

except Exception as e:
    print(f"\nError: {e}")
