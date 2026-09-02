# -*- coding: utf-8 -*-

from ccxt.base.exchange import Exchange
from ccxt.base.decimal_to_precision import DECIMAL_PLACES
from ccxt.base.errors import AuthenticationError, OrderNotFound, NotSupported


class wallex(Exchange):
    def describe(self):
        return self.deep_extend(super(wallex, self).describe(), {
            'id': 'wallex',
            'name': 'Wallex',
            'countries': ['IR'],
            'version': 'v1',
            'rateLimit': 200,
            'certified': False,
            'precisionMode': DECIMAL_PLACES,
            'has': {
                'CORS': None,
                'spot': True,
                'margin': False,
                'swap': False,
                'future': False,
                'fetchMarkets': True,
                'fetchTicker': True,
                'fetchTickers': True,
                'fetchOrderBook': True,
                'fetchOHLCV': True,
                'fetchTrades': True,
                'fetchBalance': True,
                'createOrder': True,
                'cancelOrder': True,
                'fetchOpenOrders': True,
                'fetchOrders': True,
                'fetchOrder': True,
                'fetchMyTrades': False,
                'fetchTradingFee': False,
                'fetchTradingFees': False,
            },
            'timeframes': {
                '1m': '1',
                '15m': '15',
                '1h': '60',
                '4h': '240',
                '8h': '480',
                '12h': '720',
                '1d': '1D',
                '2d': '2D',
                '3d': '3D',
            },
            'urls': {
                'logo': 'https://wallex.ir/assets/images/logo.svg',
                'api': {
                    'public': 'https://api.wallex.ir',
                    'private': 'https://api.wallex.ir',
                },
                'www': 'https://wallex.ir',
                'doc': ['https://developers.wallex.ir/'],
            },
            'api': {
                'public': {
                    'get': ['v1/markets', 'v1/udf/history', 'v1/depth'],
                },
                'private': {
                    'get': [
                        'v1/account/balances',
                        'v1/account/openOrders',
                        'v1/account/orders',
                        'v1/account/wallets/{asset}'
                    ],
                    'post': ['v1/account/orders', 'v1/account/withdraw', 'v1/account/money-withdrawal'],
                    'delete': ['v1/account/orders'],
                },
            },
            'requiredCredentials': {'apiKey': True, 'secret': False},
            'options': {'defaultType': 'spot'},
            'fees': {'trading': {'maker': 0.001, 'taker': 0.001}}
        })

    def calculate_fee(self, symbol, type, side, amount, price, takerOrMaker='maker', params={}):
        rate = 0.001
        return {
            'type': type,
            'currency': self.market(symbol)['quote'],
            'rate': rate,
            'cost': amount * price * rate
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if headers is None:
            headers = {}
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        if api == 'private':
            self.check_required_credentials()
            headers['x-api-key'] = self.apiKey
        if method == 'POST':
            if query:
                headers['Content-Type'] = 'application/json'
                body = self.json(query)
        else:
            if query:
                url += '?' + self.urlencode(query)
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def fetch_markets(self, params={}):
        response = self.request('v1/markets', 'public', 'GET', params)
        result = self.safe_value(response, 'result', {})
        symbols = self.safe_value(result, 'symbols', {})
        keys = list(symbols.keys())
        markets = []
        for i in range(0, len(keys)):
            id = keys[i]
            market = self.safe_value(symbols, id, {})
            base = self.safe_string(market, 'baseAsset')
            quote = self.safe_string(market, 'quoteAsset')
            if base is None or quote is None:
                continue
            markets.append({
                'id': id,
                'symbol': base + '/' + quote,
                'base': base,
                'quote': quote,
                'baseId': base,
                'quoteId': quote,
                'type': 'spot',
                'spot': True,
                'active': True,
                'precision': {
                    'amount': self.safe_integer(market, 'stepSize') or 8,
                    'price': self.safe_integer(market, 'tickSize') or self.safe_integer(market, 'quotePrecision') or 8,
                },
                'limits': {
                    'amount': {'min': 0.00000001, 'max': None},
                    'price': {'min': 0.00000001, 'max': None},
                    'cost': {'min': None, 'max': None},
                },
                'info': market,
            })
        return markets

    def parse_ticker(self, ticker, market=None):
        ts = self.milliseconds()
        return self.safe_ticker({
            'symbol': self.safe_string(market, 'symbol'),
            'timestamp': ts,
            'datetime': self.iso8601(ts),
            'high': self.safe_number(ticker, '24h_highPrice'),
            'low': self.safe_number(ticker, '24h_lowPrice'),
            'bid': self.safe_number(ticker, 'bidPrice'),
            'ask': self.safe_number(ticker, 'askPrice'),
            'last': self.safe_number(ticker, 'lastPrice'),
            'close': self.safe_number(ticker, 'lastPrice'),
            'baseVolume': self.safe_number(ticker, '24h_volume'),
            'quoteVolume': self.safe_number(ticker, '24h_quoteVolume'),
            'info': ticker
        }, market)

    def fetch_tickers(self, symbols=None, params={}):
        return {}

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        response = self.request('v1/markets', 'public', 'GET', params)
        result = self.safe_value(response, 'result', {})
        symbols = self.safe_value(result, 'symbols', {})
        data = self.safe_value(symbols, market['id'], {})
        return self.parse_ticker(data, market)

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        request = {'symbol': market['id']}
        if limit is not None:
            request['limit'] = limit
        response = self.request('v1/depth', 'public', 'GET', self.extend(request, params))
        result = self.safe_value(response, 'result', {})
        timestamp = self.safe_timestamp(result, 'timestamp') or self.milliseconds()
        return self.parse_order_book(result, market['symbol'], timestamp, 'bid', 'ask', 'price', 'quantity')

    def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        resolution = self.safe_string(self.timeframes, timeframe)
        if resolution is None:
            raise NotSupported(self.id + ' fetchOHLCV does not support timeframe ' + timeframe)
        now = self.seconds()
        duration = self.parse_timeframe(timeframe)
        candles_limit = 500 if limit is None else limit
        from_ts = (now - int(duration * candles_limit)) if since is None else int(since / 1000)
        request = {
            'symbol': market['id'],
            'resolution': resolution,
            'from': from_ts,
            'to': now
        }
        response = self.request('v1/udf/history', 'public', 'GET', self.extend(request, params))
        t = self.safe_list(response, 't', [])
        o = self.safe_list(response, 'o', [])
        h = self.safe_list(response, 'h', [])
        l = self.safe_list(response, 'l', [])
        c = self.safe_list(response, 'c', [])
        v = self.safe_list(response, 'v', [])
        result = []
        for i in range(0, len(t)):
            result.append([
                self.safe_timestamp(t, i),
                self.safe_number(o, i),
                self.safe_number(h, i),
                self.safe_number(l, i),
                self.safe_number(c, i),
                self.safe_number(v, i)
            ])
        return self.filter_by_since_limit(result, since, limit, 0)

    def fetch_balance(self, params={}):
        self.load_markets()
        response = self.request('v1/account/balances', 'private', 'GET', params)
        result = self.safe_value(response, 'result', {})
        balances_data = self.safe_value(result, 'balances', {})
        balances = {'info': response}
        keys = list(balances_data.keys())
        for i in range(0, len(keys)):
            code = keys[i]
            item = self.safe_value(balances_data, code, {})
            total = self.safe_number(item, 'value')
            used = self.safe_number(item, 'locked')
            free = total - used if total is not None and used is not None else total
            balances[code] = {'free': free, 'used': used, 'total': total}
        return self.safe_balance(balances)

    def parse_order_status(self, status):
        statuses = {
            'open': 'open',
            'active': 'open',
            'new': 'open',
            'done': 'closed',
            'filled': 'closed',
            'canceled': 'canceled',
            'cancelled': 'canceled'
        }
        return statuses.get(status, status)

    def parse_order(self, order, market=None):
        ts = self.safe_integer(order, 'transactTime') or self.safe_timestamp(order, 'time')

        # Fallbacks for amount
        amount = self.safe_number(order, 'origQty')
        if amount is None:
            amount = self.safe_number(order, 'quantity')
        if amount is None:
            amount = self.safe_number(order, 'amount')

        # Fallbacks for filled
        filled = self.safe_number(order, 'executedQty')
        if filled is None:
            filled = self.safe_number(order, 'executedQty')
        if filled is None:
            filled = 0

        # Calculate remaining safely
        remaining = amount - filled if amount is not None else None

        # Fallbacks for price
        price = self.safe_number(order, 'price')
        if price is None:
            price = self.safe_number(order, 'avgPrice')

        return self.safe_order({
            'id': self.safe_string(order, 'clientOrderId') or self.safe_string(order, 'id'),
            'clientOrderId': self.safe_string(order, 'clientOrderId'),
            'info': order,
            'timestamp': ts,
            'datetime': self.iso8601(ts) if ts is not None else None,
            'status': self.parse_order_status(self.safe_string(order, 'status')),
            'symbol': self.safe_string(market, 'symbol'),
            'type': self.safe_string_lower(order, 'type'),
            'side': self.safe_string_lower(order, 'side'),
            'price': price,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
        }, market)

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        amount_str = format(float(amount), '.2f') if market['quote'] == 'TMN' else self.amount_to_precision(symbol,
                                                                                                            amount)
        price_str = self.price_to_precision(symbol, price) if price is not None else None

        request = {
            'symbol': market['id'],
            'side': side.upper(),
            'type': type.upper(),
            'quantity': amount_str,
        }
        if price_str is not None:
            request['price'] = price_str

        response = self.request('v1/account/orders', 'private', 'POST', self.extend(request, params))
        order_data = self.safe_value(response, 'result', response)
        return self.parse_order(order_data, market)

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()
        market = self.market(symbol) if symbol else None
        response = self.request('v1/account/orders', 'private', 'GET', params)
        result = self.safe_value(response, 'result', {})
        orders = self.safe_value(result, 'orders', []) if isinstance(result, dict) else []
        for item in orders:
            item_id = self.safe_string(item, 'clientOrderId') or self.safe_string(item, 'id')
            if item_id == id:
                return self.parse_order(item, market)
        open_orders = self.fetch_open_orders(symbol, params=params)
        for order in open_orders:
            if order.get('id') == id:
                return order
        raise OrderNotFound(self.id + ' order ' + id + ' not found')

    def cancel_order(self, id, symbol=None, params={}):
        request = {'clientOrderId': id}
        return self.request('v1/account/orders', 'private', 'DELETE', self.extend(request, params))

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol) if symbol else None
        request = {}
        if market:
            request['market'] = market['id']
        response = self.request('v1/account/openOrders', 'private', 'GET', self.extend(request, params))
        result = self.safe_value(response, 'result', {})
        orders = self.safe_value(result, 'orders', [])
        return self.parse_orders(orders, market, since, limit)

    def fetch_deposit_address(self, code, params={}):
        self.load_markets()
        network = self.safe_string(params, 'network')
        request = {}
        if network:
            request['network'] = network
        response = self.request('v1/account/wallets/' + code.lower(), 'private', 'GET', request)
        result = self.safe_value(response, 'result', {})
        wallets = self.safe_value(result, 'wallets', {})

        address = None
        tag = None
        if network:
            wallet_data = self.safe_value(wallets, network.upper(), {})
            address = self.safe_string(wallet_data, 'address')
            tag = self.safe_string(wallet_data, 'memo') or self.safe_string(wallet_data, 'tag')
        else:
            first_wallet_key = next(iter(wallets), None)
            if first_wallet_key:
                wallet_data = self.safe_value(wallets, first_wallet_key, {})
                address = self.safe_string(wallet_data, 'address')
                tag = self.safe_string(wallet_data, 'memo') or self.safe_string(wallet_data, 'tag')
                network = first_wallet_key

        return {
            'currency': code,
            'address': address,
            'tag': tag,
            'network': network,
            'info': response
        }

    def withdraw(self, code, amount, address, tag=None, params={}):
        self.load_markets()
        request = {
            'asset': code.upper(),
            'amount': str(amount),
            'address': address,
        }
        if tag:
            request['memo'] = tag
        if 'network' in params:
            request['network'] = params['network']

        response = self.request('v1/account/withdraw', 'private', 'POST', self.extend(request, params))
        result = self.safe_value(response, 'result', response)

        return {
            'id': self.safe_string(result, 'tracking_code') or self.safe_string(result, 'id'),
            'info': response,
            'status': self.safe_string(result, 'status'),
            'amount': self.safe_number(result, 'amount'),
            'fee': self.safe_number(result, 'fee'),
        }