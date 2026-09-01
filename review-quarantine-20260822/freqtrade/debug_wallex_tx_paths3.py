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
    
    paths_to_test = [
        'v1/account/wallet/transactions',
        'v1/account/ledger',
        'v1/account/history',
        'v1/account/wallet/history',
        'v1/account/deposit/history',
        'v1/account/withdraw/history',
        'v1/account/transfers',
        'v1/account/deposit-address'
    ]

    for path in paths_to_test:
        print(f"\n--- Testing /{path} ---")
        try:
            resp = exchange.request(path, 'private', 'GET', {})
            print(f"✅ SUCCESS! Path found: /{path}")
            print(json.dumps(resp, indent=2, ensure_ascii=False)[:500])
        except Exception as e:
            err_str = str(e)
            if "404" in err_str:
                print("404 Not Found")
            else:
                print(f"Found but different error: {err_str[:150]}")

except Exception as e:
    print(f"\nError: {e}")
