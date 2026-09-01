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
    
    print("\n--- Testing Crypto Withdrawal (USDT, BSC) ---")
    
    # تنظیمات برداشت
    currency = 'USDT'
    amount = 1.0  # مقدار برداشت (مثلاً 1 تتر)
    
    # آدرس مقصد (برای تست می‌توانید آدرس کیف پول خودتان یا یک آدرس تستی بگذارید)
    # در اینجا از همان آدرس واریز خودتان استفاده می‌کنیم
    destination_address = '0x126262fd2a0b3ae3c2fc62caf865dc800f545245'
    network = 'BSC'
    
    print(f"Attempting to withdraw {amount} {currency} to {destination_address} via {network}...")
    
    # فراخوانی متد برداشت
    withdraw_response = exchange.withdraw(currency, amount, destination_address, None, {'network': network})
    
    print("\n✅ Withdraw Request Processed!")
    print(f"  Currency: {currency}")
    print(f"  Amount: {withdraw_response.get('amount')}")
    print(f"  Fee: {withdraw_response.get('fee')}")
    print(f"  Status: {withdraw_response.get('status')}")
    print(f"  Tracking ID: {withdraw_response.get('id')}")

except Exception as e:
    print(f"\n❌ API Response: {e}")
    print("ℹ️ Analysis: If you see '404 Not Found', Wallex blocks crypto withdrawals via API. If you see 'Insufficient Balance' or 'Invalid Address', the code works perfectly!")
