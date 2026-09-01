import asyncio
import unittest

from ccxt.base.errors import AuthenticationError, ExchangeError, NotSupported
from ccxt.async_support.nobitex import nobitex as AsyncNobitex
from ccxt.async_support.wallex import wallex as AsyncWallex
from ccxt.nobitex import nobitex as Nobitex
from ccxt.wallex import wallex as Wallex

MARKET = {'id': 'BTCUSDT', 'symbol': 'BTC/USDT', 'base': 'BTC', 'quote': 'USDT',
          'baseId': 'BTC', 'quoteId': 'USDT', 'type': 'spot', 'spot': True,
          'active': True, 'precision': {'amount': 8, 'price': 2},
          'limits': {'amount': {'min': 1e-8}, 'price': {'min': 1e-8}, 'cost': {}},
          'info': {}}

class StubWallex(Wallex):
    def load_markets(self, reload=False, params={}):
        self.markets = {'BTC/USDT': MARKET}; self.markets_by_id = {'BTCUSDT': MARKET}; return self.markets
    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        self.last_request = (path, api, method, params)
        return {'result': {'id': 'o1', 'clientOrderId': 'c1', 'status': 'NEW', 'type': 'LIMIT',
                           'side': 'BUY', 'price': '100', 'origQty': '1', 'executedQty': '0'}}

class StubAsyncWallex(AsyncWallex):
    async def load_markets(self, reload=False, params={}):
        self.markets = {'BTC/USDT': MARKET}; self.markets_by_id = {'BTCUSDT': MARKET}; return self.markets
    async def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        self.last_request = (path, api, method, params)
        return {'result': {'id': 'o1', 'clientOrderId': 'c1', 'status': 'NEW', 'type': 'LIMIT',
                           'side': 'BUY', 'price': '100', 'origQty': '1', 'executedQty': '0'}}

class AdapterReview(unittest.TestCase):
    def test_wallex_order_validation(self):
        exchange = StubWallex({'apiKey': 'test'})
        self.assertEqual(exchange.create_order('BTC/USDT', 'limit', 'buy', 1, 100)['id'], 'c1')
        self.assertEqual(exchange.last_request[3]['quantity'], '1')
        with self.assertRaises(ValueError): exchange.create_order('BTC/USDT', 'limit', 'buy', 1)
        with self.assertRaises(NotSupported): exchange.create_order('BTC/USDT', 'stop', 'buy', 1, 100)

    def test_sign_requires_credentials(self):
        with self.assertRaises(AuthenticationError): Wallex().sign('v1/account/balances', 'private')
        with self.assertRaises(AuthenticationError): Nobitex().sign('users/profile', 'private')

    def test_nobitex_uses_exchange_error(self):
        exchange = Nobitex({'apiKey': 'test'})
        exchange.load_markets = lambda reload=False, params={}: {'BTC/USDT': MARKET}
        exchange.request = lambda *args, **kwargs: {'status': 'error', 'code': 'bad', 'message': 'invalid'}
        with self.assertRaises(ExchangeError): exchange.create_order('BTC/USDT', 'limit', 'buy', 1, 100)

    def test_async_paths_await(self):
        async def run():
            wallex = StubAsyncWallex({'apiKey': 'test'})
            self.assertEqual((await wallex.create_order('BTC/USDT', 'limit', 'buy', 1, 100))['id'], 'c1')
            nobitex = AsyncNobitex({'apiKey': 'test'})
            async def load_markets(reload=False, params={}):
                nobitex.markets = {'BTC/USDT': MARKET}; nobitex.markets_by_id = {'BTCUSDT': MARKET}; return nobitex.markets
            async def request(path, *args, **kwargs):
                if path == 'market/orders/add':
                    return {'status': 'ok', 'order': {'id': 'n1', 'status': 'done', 'createdAt': 1,
                            'amount': '1', 'filledAmount': '1', 'type': 'limit', 'side': 'buy', 'price': '100'}}
                return {'status': 'ok', 'orders': []}
            nobitex.load_markets = load_markets; nobitex.request = request
            self.assertEqual((await nobitex.create_order('BTC/USDT', 'limit', 'buy', 1, 100))['id'], 'n1')
            self.assertEqual(await nobitex.fetch_open_orders('BTC/USDT'), [])
        asyncio.run(run())

if __name__ == '__main__': unittest.main(verbosity=2)
