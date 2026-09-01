import os
import sys, json
sys.path.insert(0, '/opt/ccxt-new/python')
from ccxt.wallex import wallex

# هشدار: توصیه می‌شود کلید API خود را در پنل والکس مجدداً بسازید تا کلید قبلی منقضی شود.
API_KEY = os.getenv('WALLEX_API_KEY', '')

exchange = wallex({
    'apiKey': API_KEY,
    'enableRateLimit': True
})

try:
    print("Connecting to Wallex and fetching registered IBANs...")
    exchange.load_markets()
    
    # فراخوانی متد دریافت شباها
    response = exchange.request('v1/account/ibans', 'private', 'GET', {})
    
    print("\n✅ IBAN List Retrieved:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    print("\n💡 Tip: Find the 'id' (integer) of the IBAN you want to withdraw to.")
    print("You must use this integer ID, not the IR... string, in the withdrawal script!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
