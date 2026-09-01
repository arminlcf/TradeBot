import os
import sys
import json
import argparse
from decimal import Decimal

sys.path.insert(0, '/opt/ccxt-new/python')
from ccxt.wallex import wallex

parser = argparse.ArgumentParser(description='Wallex Toman withdrawal')
parser.add_argument('--execute', action='store_true', help='ثبت واقعی درخواست برداشت')
args = parser.parse_args()

API_KEY = os.getenv('WALLEX_API_KEY')
if not API_KEY:
    print('❌ WALLEX_API_KEY is not set. Run: export WALLEX_API_KEY="YOUR_KEY"')
    sys.exit(1)

exchange = wallex({
    'apiKey': API_KEY,
    'enableRateLimit': True,
})

try:
    print("Connecting to Wallex...")
    exchange.load_markets()

    # ۱. دریافت موجودی‌ها (بدون چاپ کامل برای خلوت ماندن ترمینال)
    balances_response = exchange.request('v1/account/balances', 'private', 'GET', {})
    balances = balances_response.get('result', {}).get('balances', {})
    
    # پیدا کردن موجودی تومان (TMN)
    toman_balance = Decimal(str(balances.get('TMN', {}).get('value', '0')))
    toman_locked = Decimal(str(balances.get('TMN', {}).get('locked', '0')))
    toman_available = toman_balance - toman_locked

    print(f"\n💵 Toman Balance Info:")
    print(f"  Total: {toman_balance} TMN")
    print(f"  Locked: {toman_locked} TMN")
    print(f"  Available to Withdraw: {toman_available} TMN")

    # ۲. بررسی شبا
    ibans_response = exchange.request('v1/account/ibans', 'private', 'GET', {})
    iban_list = ibans_response.get('result') or []
    selected_iban_id = 868066  # بانک سامان شما

    selected_iban = next((item for item in iban_list if item.get('id') == selected_iban_id and item.get('status') == 'ACCEPTED'), None)
    if not selected_iban:
        print(f"\n❌ IBAN ID {selected_iban_id} not found or not ACCEPTED.")
        sys.exit(1)

    print(f"\n🏦 Target Bank Account: {selected_iban.get('bank_details', {}).get('label')} ({selected_iban.get('iban')})")

    # ۳. بررسی شرایط برداشت
    minimum_withdrawal = Decimal('15000') # حداقل برداشت والکس
    
    print("\n--- Withdrawal Preflight ---")
    print(f"  Available Limit: {toman_available} TMN")
    print(f"  Required Min: {minimum_withdrawal} TMN")

    if toman_available < minimum_withdrawal:
        print(f"\n❌ Error: Insufficient Balance. You have {toman_available} TMN, but Wallex requires at least {minimum_withdrawal} TMN to withdraw.")
        sys.exit(0)

    # تعیین مبلغ برداشت (به اندازه موجودی در دسترس یا حداقل)
    withdrawal_amount = minimum_withdrawal 

    request_body = {
        'iban': int(selected_iban['id']),
        'value': int(withdrawal_amount)
    }

    if not args.execute:
        print("\n✅ Preflight OK. To execute the real withdraw, run:")
        print("   python3 check_wallex_withdraw.py --execute")
        sys.exit(0)

    print(f"\n🚀 Executing withdrawal of {withdrawal_amount} TMN...")
    withdrawal_response = exchange.request('v1/account/money-withdrawal', 'private', 'POST', request_body)
    
    print("\n✅ Withdraw Request Processed by Wallex!")
    result = withdrawal_response.get('result', {})
    print(f"  Amount: {result.get('amount')} TMN")
    print(f"  Fee: {result.get('fee')} TMN")
    print(f"  Status: {result.get('status')}")
    print(f"  Tracking Code: {result.get('tracking_code')}")

except Exception as e:
    print(f"\n❌ API Error: {str(e)}")
    sys.exit(1)
