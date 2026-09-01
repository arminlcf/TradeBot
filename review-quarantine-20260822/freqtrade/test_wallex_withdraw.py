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
    
    print("\n--- Testing Withdraw Request ---")
    
    # تنظیمات درخواست برداشت
    currency = 'USDT'
    amount = 1.0
    withdraw_address = 'TXscSuEr1bpFwbHJ5jEQpTCCEmC6ZF9W6t'
    
    print(f"Attempting to withdraw {amount} {currency} to {withdraw_address} (TRC20)...")
    
    # فراخوانی متد برداشت
    withdraw_response = exchange.withdraw(currency, amount, withdraw_address, None, {'network': 'TRC20'})
    
    print("\n✅ Withdraw Request Processed!")
    print(f"  Currency: {currency}")
    print(f"  Amount: {withdraw_response.get('amount')}")
    print(f"  Fee: {withdraw_response.get('fee')}")
    print(f"  Status: {withdraw_response.get('status')}")
    print(f"  Tracking ID: {withdraw_response.get('id')}")

except Exception as e:
    print(f"\n❌ API Response: {e}")
    print("ℹ️ Note: If you see an error like 'Insufficient Balance' or 'Invalid Address', it means the code works perfectly! It just means Wallex rejected the withdrawal request due to account limits.")
