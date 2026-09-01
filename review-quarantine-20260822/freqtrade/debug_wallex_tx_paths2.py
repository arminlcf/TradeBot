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
    
    # تست مسیرهای احتمالی دیگر
    paths_to_test = [
        'v1/account/deposits',
        'v1/account/withdrawals',
        'v1/account/deposit',
        'v1/account/withdrawal',
        'v1/deposit',
        'v1/withdraw',
        'v1/account/wallet/deposits',
        'v1/account/wallet/withdrawals'
    ]

    for path in paths_to_test:
        print(f"\n--- Testing /{path} ---")
        try:
            # استفاده از متد request با مسیرهای تستی
            resp = exchange.request(path, 'private', 'GET', {})
            # اگر ارور ندهد، یعنی مسیر پیدا شده است
            print(f"✅ SUCCESS! Path found: /{path}")
            print(json.dumps(resp, indent=2, ensure_ascii=False)[:500])
            break # اگر پیدا شد، دیگه نیاز به تست بقیه نیست
        except Exception as e:
            # فقط کد ارور را چاپ میکنیم تا تمیز باشد
            err_str = str(e)
            if "404" in err_str:
                print("404 Not Found")
            else:
                print(f"Failed with different error: {err_str[:100]}")

except Exception as e:
    print(f"\nError: {e}")
