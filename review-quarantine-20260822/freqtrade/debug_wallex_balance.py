import os
import sys
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
    
    print("--- Fetching Raw Balance ---")
    # گرفتن پاسخ خام سرور والکس
    response = exchange.request('v1/account/balances', 'private', 'GET', {})
    
    import json
    # چاپ کردن زیبای خروجی خام
    print(json.dumps(response, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"\n❌ Error: {e}")
