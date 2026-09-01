from ccxt.async_support.base.exchange import Exchange
from ccxt.base.decimal_to_precision import DECIMAL_PLACES
from ccxt.base.errors import ExchangeError, NotSupported, OrderNotFound

class nobitex(Exchange):
    def describe(self):
        return self.deep_extend(super(nobitex, self).describe(), {
            'id': 'nobitex', 'name': 'Nobitex', 'countries': ['IR'], 'precisionMode': DECIMAL_PLACES, 'rateLimit': 100, 'certified': False,
            'has': {
                'CORS': None, 'spot': True, 'margin': False, 'swap': False, 'future': False,
                'fetchMarkets': True, 'fetchTicker': True, 'fetchTickers': True, 'fetchOrderBook': True,
                'fetchOHLCV': False, 'fetchTrades': False, 'fetchBalance': True, 'createOrder': True,
                'fetchOrder': True, 'cancelOrder': True, 'fetchOpenOrders': True, 'fetchClosedOrders': True,
                'fetchOrders': True, 'fetchMyTrades': True, 'fetchTransactions': True,
                'fetchTradingFee': False, 'fetchTradingFees': False,
            },
            'urls': {'logo': 'https://nobitex.ir/assets/images/logo.svg', 'api': {'public': 'https://apiv2.nobitex.ir', 'private': 'https://apiv2.nobitex.ir'}, 'www': 'https://nobitex.ir', 'doc': ['https://apidocs.nobitex.ir']},
            'api': {
                'public': {'get': ['market/stats', 'v2/trades/{symbol}', 'v3/orderbook/{symbol}', 'v2/orderbook/{symbol}', 'status']},
                'private': {
                    'get': ['users/profile', 'users/transactions-history', 'users/markets/favorite'],
                    'post': ['users/wallets/list', 'market/orders/add', 'market/orders/cancel', 'market/orders/list', 'market/orders/update-status', 'users/accounts-add']
                }
            },
            'requiredCredentials': {'apiKey': True, 'secret': False},
            'options': {'defaultType': 'spot'}
        })

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if headers is None: headers = {}
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        if api == 'private':
            self.check_required_credentials()
            headers['Authorization'] = 'Token ' + self.apiKey
            if method == 'POST': headers['Content-Type'] = 'application/json'; body = self.json(query)
        elif method == 'GET':
            if query: url += '?' + self.urlencode(query)
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    async def fetch_markets(self, params={}):
        response = await self.request('market/stats', 'public', 'GET', params)
        stats = self.safe_value(response, 'stats', {})
        result = []
        for id, market_data in stats.items():
            parts = id.split('-')
            if len(parts) != 2: continue
            base, quote = parts[0].upper(), parts[1].upper()
            result.append({
                'id': id, 'symbol': base + '/' + quote, 'base': base, 'quote': quote,
                'baseId': base, 'quoteId': quote, 'type': 'spot', 'spot': True, 'active': True,
                'precision': {'amount': 8, 'price': 1},
                'limits': {'amount': {'min': 0.00000001, 'max': None}, 'price': {'min': 0.00000001, 'max': None}, 'cost': {'min': None, 'max': None}},
                'info': market_data
            })
        return result

    def parse_ticker(self, ticker, market=None):
        ts = self.milliseconds()
        return self.safe_ticker({
            'symbol': self.safe_string(market, 'symbol'), 'timestamp': ts, 'datetime': self.iso8601(ts),
            'high': self.safe_number(ticker, 'dayHigh'), 'low': self.safe_number(ticker, 'dayLow'),
            'bid': self.safe_number(ticker, 'bestBuy'), 'ask': self.safe_number(ticker, 'bestSell'),
            'last': self.safe_number(ticker, 'latest'), 'close': self.safe_number(ticker, 'latest'),
            'baseVolume': self.safe_number(ticker, 'volumeSrc'), 'quoteVolume': self.safe_number(ticker, 'volumeDst'),
            'info': ticker
        }, market)

    async def fetch_order_book(self, symbol, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        quote_id = market['quoteId'].upper()
        endpoint_quote = 'IRT' if quote_id == 'RLS' else quote_id
        endpoint_symbol = market['baseId'].upper() + endpoint_quote
        response = await self.request('v3/orderbook/' + endpoint_symbol, 'public', 'GET', params)
        asks = self.safe_value(response, 'asks', []) or []
        bids = self.safe_value(response, 'bids', []) or []
        orderbook = {'asks': [[self.safe_number(x, 0), self.safe_number(x, 1)] for x in asks],
                     'bids': [[self.safe_number(x, 0), self.safe_number(x, 1)] for x in bids]}
        return self.parse_order_book(orderbook, market, self.safe_integer(response, 'lastUpdate'), limit)

    async def fetch_ticker(self, symbol, params={}):
        await self.load_markets()
        market = self.market(symbol)
        response = await self.request('market/stats', 'public', 'GET', self.extend({'srcCurrency': market['baseId'], 'dstCurrency': market['quoteId']}, params))
        return self.parse_ticker(self.safe_value(self.safe_value(response, 'stats', {}), market['baseId'] + '-' + market['quoteId'], {}), market)

    async def fetch_tickers(self, symbols=None, params={}):
        await self.load_markets()
        selected = symbols or list(self.markets.keys())
        result = {}
        for symbol in selected:
            market = self.market(symbol)
            ticker = self.safe_value(market, 'info')
            if ticker is None:
                response = await self.request('market/stats', 'public', 'GET', self.extend({'srcCurrency': market['baseId'], 'dstCurrency': market['quoteId']}, params))
                ticker = self.safe_value(self.safe_value(response, 'stats', {}), market['baseId'] + '-' + market['quoteId'], {})
            result[market['symbol']] = self.parse_ticker(ticker, market)
        return result

    async def fetch_ohlcv(self, symbol, timeframe='1d', since=None, limit=None, params={}):
        raise NotSupported('Nobitex API does not support OHLCV data.')

    async def fetch_balance(self, params={}):
        await self.load_markets()
        response = await self.request('users/wallets/list', 'private', 'POST', params)
        result = {'info': response}
        for w in self.safe_value(response, 'wallets', []):
            code = self.safe_currency_code(self.safe_string(w, 'currency'))
            total = self.safe_number(w, 'balance')
            free = self.safe_number(w, 'activeBalance')
            result[code] = {'free': free, 'used': (total - free if total is not None and free is not None else None), 'total': total}
        return self.safe_balance(result)

    def parse_order_status(self, status):
        return {'open':'open','active':'open','done':'closed','filled':'closed','canceled':'canceled','cancelled':'canceled'}.get(status, status)

    def parse_order(self, order, market=None):
        ts = self.safe_integer(order, 'createdAt')
        return self.safe_order({
            'id': self.safe_string(order, 'id'), 'clientOrderId': None, 'info': order, 'timestamp': ts, 'datetime': self.iso8601(ts),
            'status': self.parse_order_status(self.safe_string(order, 'status')), 'symbol': self.safe_string(market, 'symbol'),
            'type': self.safe_string(order, 'type'), 'side': self.safe_string_lower(order, 'side'), 'price': self.safe_number(order, 'price'),
            'amount': self.safe_number(order, 'amount'), 'filled': self.safe_number(order, 'filledAmount')
        }, market)

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        await self.load_markets()
        m = self.market(symbol)
        order_type = type.lower()
        if order_type not in ('limit', 'market'):
            raise NotSupported(self.id + ' createOrder does not support order type ' + type)
        if amount is None or amount <= 0:
            raise ValueError('Nobitex order amount must be positive')
        req = {'type': side.lower(), 'srcCurrency': m['baseId'], 'dstCurrency': m['quoteId'], 'amount': str(amount)}
        if order_type == 'limit':
            if price is None or price <= 0:
                raise ValueError('Nobitex limit orders require a positive price')
            req['price'] = str(price)
        else:
            req['mode'] = 'market'
        resp = await self.request('market/orders/add', 'private', 'POST', self.extend(req, params))
        if self.safe_string(resp, 'status') != 'ok':
            raise ExchangeError(f"Nobitex Error: {self.safe_string(resp, 'code')} - {self.safe_string(resp, 'message')}")
        return self.parse_order(self.safe_value(resp, 'order', resp), m)

    async def cancel_order(self, id, symbol=None, params={}):
        return await self.request('market/orders/update-status', 'private', 'POST', self.extend({'order': id, 'status': 'canceled'}, params))

    async def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
        await self.load_markets()
        m = self.market(symbol) if symbol else None
        req = {}
        if m: req.update({'srcCurrency': m['baseId'], 'dstCurrency': m['quoteId']})
        response = await self.request('market/orders/list', 'private', 'POST', self.extend(req, params))
        return self.parse_orders(self.safe_value(response, 'orders', []), m, since, limit)


    async def fetch_order(self, id, symbol=None, params={}):
        orders = await self.fetch_orders(symbol, params=params)
        for order in orders:
            if order['id'] == str(id):
                return order
        raise OrderNotFound(self.id + ' order ' + str(id) + ' not found')

    async def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        return await self.fetch_orders(symbol, since, limit, self.extend({'status': 'open'}, params))
    async def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        return await self.fetch_orders(symbol, since, limit, self.extend({'status': 'done'}, params))
    async def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        return await self.fetch_orders(symbol, since, limit, self.extend({'status': 'done'}, params))

    def parse_transaction(self, transaction, currency=None):
        timestamp = self.parse8601(self.safe_string(transaction, 'created_at'))
        type = self.safe_string(transaction, 'type')
        amount = self.safe_number(transaction, 'amount')
        currency_code = self.safe_currency_code(self.safe_string(transaction, 'currency'))
        return {
            'info': transaction,
            'id': self.safe_string(transaction, 'id'),
            'txid': self.safe_string(transaction, 'txHash'),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'type': type,
            'amount': amount,
            'currency': currency_code,
            'status': 'done',
            'fee': None,
            'address': None,
            'network': None,
        }

    


    async def fetch_transactions(self, code=None, since=None, limit=None, params={}):
        await self.load_markets()
        response = await self.request('users/transactions-history', 'private', 'GET', params)
        return self.parse_transactions(self.safe_value(response, 'transactions', []), code, since, limit)
