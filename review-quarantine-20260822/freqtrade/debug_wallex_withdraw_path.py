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
    
    # مسیرهای احتمالی برای برداشت ارز دیجیتال در والکس
    paths_to_test = [
        'v1/account/withdraw/crypto',
        'v1/account/crypto/withdraw',
        'v1/account/wallet/withdraw',
        'v1/account/withdrawRequest',
        'v1/withdraw',
        'v1/account/withdraw/usdt'
    ]

    for path in paths_to_test:
        print(f"\n--- Testing POST /{path} ---")
        try:
            # ارسال یک درخواست خالی برای تست مسیر
            resp = exchange.request(path, 'private', 'POST', {})
            print(f"✅ SUCCESS! Path found: /{path}")
            print(json.dumps(resp, indent=2, ensure_ascii=False)[:300])
        except Exception as e:
            err_str = str(e)
            # اگه ارور 404 نبود، یعنی مسیر درسته ولی دیتا کمه
            if "404" in err_str:
                print("404 Not Found")
            else:
                print(f"✅ PATH EXISTS! (Wallex responded with): {err_str[:200]}")

except Exception as e:
    print(f"\nError: {e}")
