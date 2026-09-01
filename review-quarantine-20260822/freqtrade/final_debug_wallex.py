import os
import sys, json
sys.path.insert(0, '/opt/ccxt-new/python')
from ccxt.wallex import wallex

exchange = wallex({'apiKey': os.getenv('WALLEX_API_KEY', ''), 'enableRateLimit': True})

try:
    exchange.load_markets()
    print("--- Final Debug for Wallex History ---")
    
    # تست مسیرهای مختلف برای گرفتن تاریخچه واریز/برداشت یک ارز خاص
    paths = [
        'v1/account/wallets/usdt/transactions',
        'v1/account/wallets/usdt/history',
        'v1/account/orders/withdraw',
        'v1/account/withdraw/history'
    ]
    
    for p in paths:
        print(f"\nTesting GET /{p}")
        try:
            r = exchange.request(p, 'private', 'GET', {})
            print(f"✅ FOUND! {json.dumps(r, indent=2)[:200]}")
        except Exception as e:
            err = str(e)
            if "404" in err:
                print("❌ 404 Not Found (Route does not exist)")
            else:
                print(f"⚠️ Different Error: {err[:100]}")

except Exception as e:
    print(f"Error: {e}")
