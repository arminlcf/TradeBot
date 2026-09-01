import os
import sys, json
sys.path.insert(0, '/opt/ccxt-new/python')
from ccxt.nobitex import nobitex

exchange = nobitex({'apiKey': os.getenv('NOBITEX_API_KEY', ''), 'enableRateLimit': True})

try:
    exchange.load_markets()
    response = exchange.request('users/transactions-history', 'private', 'GET', {})
    transactions = exchange.safe_value(response, 'transactions', [])
    if transactions:
        print("Raw Transaction Data:")
        print(json.dumps(transactions[0], indent=2, ensure_ascii=False))
    else:
        print("No transactions found.")
except Exception as e:
    print(f"Error: {e}")
