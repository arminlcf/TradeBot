import sys
sys.path.insert(0, '/opt/ccxt-new/python')
from ccxt.wallex import wallex

# API Key والکس خود را اینجا قرار دهید
API_KEY = '19838|KANnKDYKOMyoUtfYnOPm7A38sMiOGonZsmy5hhHx'

exchange = wallex({
    'apiKey': API_KEY,
    'enableRateLimit': True
})

try:
    print("Connecting to Wallex...")
    exchange.load_markets()
    
    symbol = 'PEPE/TMN'
    # گرفتن نام دقیق نماد از خود والکس (مثلا PEPETMN)
    market = exchange.market(symbol)
    wallex_symbol = market['id']
    
    budget_tmn = 60000  # بودجه شما به تومان
    
    print(f"\n--- Fetching {symbol} Live Price ---")
    ticker = exchange.fetch_ticker(symbol)
    live_price = float(ticker['last'])
    print(f"Live price for {symbol}: {live_price} TMN")
    
    # محاسبه قیمت خرید (1% بالاتر از بازار تا فورا پر شود)
    buy_price = live_price * 1.01
    
    # محاسبه مقدار پپه (به صورت عدد صحیح)
    buy_amount = int(budget_tmn / buy_price)
    
    # محدود کردن قیمت به 4 رقم اعشار (طبق قوانین والکس)
    buy_price_rounded = round(buy_price, 4)
    
    # تبدیل به فرمت متنی
    price_str = str(buy_price_rounded)
    amount_str = str(buy_amount)
    
    print(f"\nWallex Symbol: {wallex_symbol}")
    print(f"Calculated Buy Amount: {amount_str} PEPE")
    print(f"Placing REAL BUY order: {amount_str} {symbol} @ {price_str} TMN")
    
    # ارسال درخواست با نماد صحیح والکس
    request_body = {
        'symbol': wallex_symbol,
        'side': 'buy',
        'type': 'limit',
        'quantity': amount_str,
        'price': price_str
    }
    
    response = exchange.request('v1/account/orders', 'private', 'POST', request_body)
    
    print("\n✅ Order Success! Order ID:", response.get('result', {}).get('clientOrderId'))
    print("Check your Wallex account to see the PEPE balance!")

except Exception as e:
    print(f"\n❌ Error: {e}")
