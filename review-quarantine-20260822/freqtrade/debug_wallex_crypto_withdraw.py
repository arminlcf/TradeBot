import os
import sys
import json
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
    
    # مسیرهای احتمالی منطقی برای برداشت ارز دیجیتال
    paths_to_test = [
        'v1/account/wallets/usdt/withdraw',
        'v1/account/wallets/USDT/withdraw',
        'v1/account/crypto/withdraw',
        'v1/account/withdraw/crypto',
        'v1/account/withdraw/usdt',
        'v1/withdraw',
        'v1/account/wallet/withdraw',
        'v1/account/withdrawal'
    ]

    for path in paths_to_test:
        print(f"\n--- Testing POST /{path} ---")
        try:
            # ارسال یک بدنه خالی برای تست مسیر
            resp = exchange.request(path, 'private', 'POST', {})
            print(f"✅ SUCCESS! Path found: /{path}")
            print(json.dumps(resp, indent=2, ensure_ascii=False)[:300])
        except Exception as e:
            err_str = str(e)
            # اگه ارور 404 نبود، یعنی مسیر درسته ولی والlex ارور دیتا داده (مثل موجودی ناکافی)
            if "404" in err_str:
                print("404 Not Found")
            else:
                print(f"✅ PATH EXISTS! (Wallex responded with): {err_str[:200]}")

except Exception as e:
    print(f"\nError: {e}")
