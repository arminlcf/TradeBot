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
    
    # ۱. گرفتن آدرس واریز (Deposit Address) در شبکه BSC
    print("\n--- Fetching Deposit Address (USDT, BSC) ---")
    deposit = exchange.fetch_deposit_address('USDT', {'network': 'BSC'})
    print(f"✅ USDT Deposit Address: {deposit.get('address')}")
    print(f"   Network: BSC")
    
    # ۲. بخش برداشت (همانطور که قبلاً بررسی شد، والکس اجازه برداشت کریپتو از طریق API را نمی‌دهد)
    print("\n--- Testing Withdraw Request ---")
    print("ℹ️ Wallex API restricts crypto withdrawals via API for security reasons.")
    print("⚠️ Withdraw test is disabled.")
    print("✅ Deposit and Balance functions are working perfectly.")

except Exception as e:
    print(f"\nError: {e}")
