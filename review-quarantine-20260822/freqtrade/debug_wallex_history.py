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
    
    print("\n--- Fetching Raw Order History (Status=FILLED) ---")
    # ارسال پارامتر status برای گرفتن سفارشات انجام شده
    response = exchange.request('v1/account/orders', 'private', 'GET', {
        'status': 'FILLED'
    })
    
    # چاپ کردن زیبای خروجی خام
    print(json.dumps(response, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"\n❌ Error: {e}")
