import os
import sys, json
sys.path.insert(0, '/opt/ccxt-new/python')
from ccxt.wallex import wallex

# هشدار امنیتی مجدد: حتما کلید API را بعد از اتمام تست در پنل والکس عوض کنید.
API_KEY = os.getenv('WALLEX_API_KEY', '')

exchange = wallex({
    'apiKey': API_KEY,
    'enableRateLimit': True
})

try:
    print("Connecting to Wallex...")
    exchange.load_markets()
    
    print("\n--- Running Final Correct Test for Toman Withdrawal ---")
    
    # استفاده از شناسه واقعی که در مرحله قبل به دست آوردیم (بانک سامان شما)
    # شناسه 868066 مربوط به شبای IR840560611828005101661401 شماست
    iban_id = 868066 
    
    # مبلغ باید حداقل 15000 تومان باشد
    amount = 20000 
    
    print(f"Attempting to withdraw {amount} TMN to IBAN ID: {iban_id}...")
    
    request_body = {
        'iban': iban_id,
        'value': amount
    }
    
    # ارسال درخواست به اندپوینت رسمی
    response = exchange.request('v1/account/money-withdrawal', 'private', 'POST', request_body)
    
    print("\n✅ SUCCESS! Withdraw Request Created.")
    result = response.get('result', {})
    
    # نمایش خروجی تمیز
    print("-" * 30)
    print(f"Status: {response.get('message', 'N/A')}")
    print(f"Amount: {result.get('amount')} TMN")
    print(f"Fee: {result.get('fee')} TMN")
    print(f"Tracking Code: {result.get('tracking_code')}")
    print("-" * 30)
    print("\n💡 NOTE: Check your Email or Wallex Panel to CONFIRM the withdrawal,")
    print("as 'is_withdrawal_otp_enable' is active for this account.")

except Exception as e:
    # چاپ کامل پاسخ برای عیب یابی در صورت بروز خطای جدید
    print(f"\n❌ API Error: {str(e)}")
