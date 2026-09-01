//  ---------------------------------------------------------------------------

import Exchange from './abstract/wallex.js';
import type {
    Balances,
    Dict,
    Int,
    MarketInterface,
    OHLCV,
    Order,
    Str,
    Ticker,
} from './base/types.js';

//  ---------------------------------------------------------------------------

export default class wallex extends Exchange {
    override describe (): any {
        return this.deepExtend (super.describe (), {
            'id': 'wallex',
            'name': 'Wallex',
            'countries': [ 'IR' ],
            'version': 'v1',
            'rateLimit': 200,

            'has': {
                'CORS': undefined,
                'spot': true,
                'margin': false,
                'swap': false,
                'future': false,
                'option': false,
                'cancelOrder': true,
                'createOrder': true,
                'fetchBalance': true,
                'fetchClosedOrders': false,
                'fetchMarkets': true,
                'fetchMyTrades': false,
                'fetchOHLCV': true,
                'fetchOpenOrders': true,
                'fetchOrder': true,
                'fetchOrderBook': false,
                'fetchTicker': true,
                'fetchTickers': false,
                'fetchTrades': false,
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
                'logo': '',
                'api': {
                    'public': 'https://api.wallex.ir',
                    'private': 'https://api.wallex.ir',
                },
                'www': 'https://wallex.ir',
                'doc': [
                    'https://developers.wallex.ir/',
                    'https://api-docs.wallex.ir/',
                ],
            },

            'api': {
                'public': {
                    'get': {
                        'v1/markets': 1,
                        'v1/udf/history': 1,
                    },
                },
                'private': {
                    'get': {
                        'v1/account/balances': 1,
                        'v1/account/openOrders': 1,
                        'v1/account/orders/{clientOrderId}': 1,
                    },
                    'post': {
                        'v1/account/orders': 1,
                    },
                    'delete': {
                        'v1/account/orders': 1,
                    },
                },
            },

            'requiredCredentials': {
                'apiKey': true,
                'secret': false,
                'uid': false,
                'password': false,
            },

            'options': {
                'defaultType': 'spot',
            },
        });
    }

    override async fetchMarkets (params = {}): Promise<MarketInterface[]> {
        const response = await this['publicGetV1Markets'] (params);
        const result = this.safeDict (response, 'result', {});
        const symbols = this.safeDict (result, 'symbols', {});
        const ids = Object.keys (symbols);
        const markets: MarketInterface[] = [];
        for (let i = 0; i < ids.length; i++) {
            const id = ids[i];
            const market = this.safeDict (symbols, id, {});
            const base = this.safeString (market, 'baseAsset');
            const quote = this.safeString (market, 'quoteAsset');
            if ((base === undefined) || (quote === undefined)) {
                continue;
            }
            markets.push ({
                'id': id,
                'lowercaseId': id.toLowerCase (),

                'symbol': base + '/' + quote,
                'base': base,
                'quote': quote,

                'settle': undefined,

                'baseId': base,
                'quoteId': quote,
                'settleId': undefined,

                'type': 'spot',
                'spot': true,
                'margin': false,
                'swap': false,
                'future': false,
                'option': false,

                'active': true,
                'contract': false,
                'linear': undefined,
                'inverse': undefined,
                'subType': undefined,

                'taker': undefined,
                'maker': undefined,

                'contractSize': undefined,

                'expiry': undefined,
                'expiryDatetime': undefined,
                'strike': undefined,
                'optionType': undefined,

                'precision': {
                    'amount': this.safeInteger (market, 'stepSize'),
                    'price': this.safeInteger (market, 'tickSize'),
                    'cost': undefined,
                },

                'limits': {
                    'leverage': {
                        'min': undefined,
                        'max': undefined,
                    },
                    'amount': {
                        'min': this.safeNumber (market, 'minQty'),
                        'max': this.safeNumber (market, 'maxQty'),
                    },
                    'price': {
                        'min': undefined,
                        'max': undefined,
                    },
                    'cost': {
                        'min': this.safeNumber (market, 'minNotional'),
                        'max': undefined,
                    },
                },

                'marginModes': {
                    'isolated': false,
                    'cross': false,
                },

                'created': undefined,
                'info': market,
            });
        }
        return markets;
    }

    override async fetchTicker (
        symbol: string,
        params = {}
    ): Promise<Ticker> {
        await this.loadMarkets ();
        const market = this.market (symbol);
        const response = await this['publicGetV1Markets'] (params);
        const result = this.safeDict (response, 'result', {});
        const symbols = this.safeDict (result, 'symbols', {});
        const data = this.safeDict (symbols, market['id'], {});
        const stats = this.safeDict (data, 'stats', {});
        const timestamp = this.milliseconds ();
        const last = this.safeNumber (stats, 'lastPrice');
        return this.safeTicker ({
            'symbol': market['symbol'],
            'timestamp': timestamp,
            'datetime': this.iso8601 (timestamp),

            'high': this.safeNumber (stats, '24h_highPrice'),
            'low': this.safeNumber (stats, '24h_lowPrice'),

            'bid': this.safeNumber (stats, 'bidPrice'),
            'bidVolume': this.safeNumber (stats, 'bidVolume'),

            'ask': this.safeNumber (stats, 'askPrice'),
            'askVolume': this.safeNumber (stats, 'askVolume'),

            'last': last,
            'close': last,

            'change': undefined,
            'percentage': this.safeNumber (stats, '24h_ch'),
            'average': undefined,
            'vwap': undefined,

            'baseVolume': this.safeNumber (stats, '24h_volume'),
            'quoteVolume': this.safeNumber (stats, '24h_quoteVolume'),

            'previousClose': undefined,

            'info': data,
        }, market);
    }

    override async fetchOHLCV (
        symbol: string,
        timeframe = '1h',
        since: Int = undefined,
        limit: Int = undefined,
        params = {}
    ): Promise<OHLCV[]> {
        await this.loadMarkets ();
        const market = this.market (symbol);
        const resolutions: Dict = {
            '1m': '1',
            '15m': '15',
            '1h': '60',
            '4h': '240',
            '8h': '480',
            '12h': '720',
            '1d': '1D',
            '2d': '2D',
            '3d': '3D',
        };
        const resolution = this.safeString (
            resolutions,
            timeframe
        );
        if (resolution === undefined) {
            throw new Error (
                this.id + ' fetchOHLCV() does not support timeframe ' +
                timeframe
            );
        }
        const now = this.seconds ();
        const candleLimit = limit || 500;
        const timeframeSeconds = this.parseTimeframe (timeframe);
        let from: number;
        if (since !== undefined) {
            from = Math.floor (since / 1000);
        } else {
            from = now - (timeframeSeconds * candleLimit);
        }
        const request: Dict = {
            'symbol': market['id'],
            'resolution': resolution,
            'from': from,
            'to': now,
        };
        const response = await this['publicGetV1UdfHistory'] (
            this.extend (request, params)
        );
        const status = this.safeString (response, 's');
        if ((status !== undefined) && (status !== 'ok')) {
            if (status === 'no_data') {
                return [];
            }
            throw new Error (
                this.id + ' fetchOHLCV() returned status: ' + status
            );
        }
        const timestamps = this.safeList (response, 't', []);
        const opens = this.safeList (response, 'o', []);
        const highs = this.safeList (response, 'h', []);
        const lows = this.safeList (response, 'l', []);
        const closes = this.safeList (response, 'c', []);
        const volumes = this.safeList (response, 'v', []);
        const candles: OHLCV[] = [];
        for (let i = 0; i < timestamps.length; i++) {
            const timestamp = this.safeInteger (timestamps, i);
            if (timestamp === undefined) {
                continue;
            }
            candles.push ([
                timestamp * 1000,
                this.safeNumber (opens, i),
                this.safeNumber (highs, i),
                this.safeNumber (lows, i),
                this.safeNumber (closes, i),
                this.safeNumber (volumes, i),
            ]);
        }
        return candles;
    }

    override async fetchBalance (params = {}): Promise<Balances> {
        const response = await this['privateGetV1AccountBalances'] (params);
        const result = this.safeDict (response, 'result', {});
        const balances: Dict = {
            'info': response,
        };
        const resultValues = Object.values (result);
        for (let i = 0; i < resultValues.length; i++) {
            const item = resultValues[i];
            if ((item === null) || (typeof item !== 'object')) {
                continue;
            }
            const balance = item as Dict;
            const code = this.safeString2 (
                balance,
                'symbol',
                'asset'
            );
            if (code === undefined) {
                continue;
            }
            const total = this.safeNumber2 (
                balance,
                'total',
                'balance'
            );
            const free = this.safeNumber2 (
                balance,
                'available',
                'free'
            );
            const used = this.safeNumber2 (
                balance,
                'freeze',
                'locked'
            );
            balances[code] = {
                'free': free,
                'used': used,
                'total': total !== undefined
                    ? total
                    : ((free || 0) + (used || 0)),
            };
        }
        return this.safeBalance (balances);
    }

    override async createOrder (
        symbol: string,
        type: string,
        side: string,
        amount: number,
        price: number | undefined = undefined,
        params = {}
    ): Promise<Order> {
        await this.loadMarkets ();
        const market = this.market (symbol);
        const request: Dict = {
            'symbol': market['id'],
            'side': side.toUpperCase (),
            'type': type.toUpperCase (),
            'quantity': this.numberToString (amount),
        };
        if (price !== undefined) {
            request['price'] = this.numberToString (price);
        }
        const clientId = this.safeString2 (
            params,
            'clientOrderId',
            'client_id'
        );
        if (clientId !== undefined) {
            request['client_id'] = clientId;
        }
        const stopPrice = this.safeString2 (
            params,
            'stopPrice',
            'stop_Price'
        );
        if (stopPrice !== undefined) {
            request['stop_Price'] = stopPrice;
        }
        const extraParams = this.omit (
            params,
            [
                'clientOrderId',
                'client_id',
                'stopPrice',
                'stop_Price',
            ]
        );
        const response = await this['privatePostV1AccountOrders'] (
            this.extend (request, extraParams)
        );
        const result = this.safeDict (response, 'result', response);
        return this.parseOrder (result, market);
    }

    override parseOrder (
        order: Dict,
        market: MarketInterface | undefined = undefined
    ): Order {
        const orderId = this.safeString2 (
            order,
            'clientOrderId',
            'client_id'
        );
        const timestamp = this.safeInteger2 (
            order,
            'transactTime',
            'timestamp'
        );
        const rawStatus = this.safeStringLower (order, 'status');
        let status = rawStatus;
        if (rawStatus === 'filled') {
            status = 'closed';
        } else if (
            (rawStatus === 'cancelled') ||
            (rawStatus === 'canceled')
        ) {
            status = 'canceled';
        } else if (
            (rawStatus === 'new') ||
            (rawStatus === 'active')
        ) {
            status = 'open';
        }
        return {
            'id': orderId,
            'clientOrderId': orderId,

            'timestamp': timestamp,
            'datetime': this.iso8601 (timestamp),
            'lastTradeTimestamp': undefined,

            'status': status,
            'symbol': market !== undefined
                ? market['symbol']
                : this.safeString (order, 'symbol'),

            'type': this.safeStringLower (order, 'type'),
            'timeInForce': undefined,
            'side': this.safeStringLower (order, 'side'),

            'price': this.safeNumber2 (
                order,
                'price',
                'executedPrice'
            ),

            'triggerPrice': this.safeNumber2 (
                order,
                'stopPrice',
                'stop_Price'
            ),

            'average': this.safeNumber (order, 'executedPrice'),

            'amount': this.safeNumber2 (
                order,
                'origQty',
                'quantity'
            ),

            'filled': this.safeNumber (order, 'executedQty'),
            'remaining': undefined,

            'cost': this.safeNumber2 (
                order,
                'sum',
                'executedSum'
            ),

            'fee': undefined,
            'trades': undefined,
            'reduceOnly': undefined,
            'postOnly': undefined,

            'info': order,
        } as unknown as Order;
    }

    override async fetchOrder (
        id: string,
        symbol?: string,
        params = {}
    ): Promise<Order> {
        await this.loadMarkets ();
        const market = symbol !== undefined
            ? this.market (symbol)
            : undefined;
        const request: Dict = {
            'clientOrderId': id,
        };
        const response = await this[
            'privateGetV1AccountOrdersClientOrderId'
        ] (
            this.extend (request, params)
        );
        const result = this.safeDict (response, 'result', response);
        return this.parseOrder (result, market);
    }

    override async fetchOpenOrders (
        symbol?: string,
        since: Int = undefined,
        limit: Int = undefined,
        params = {}
    ): Promise<Order[]> {
        await this.loadMarkets ();
        const market = symbol !== undefined
            ? this.market (symbol)
            : undefined;
        const response = await this[
            'privateGetV1AccountOpenOrders'
        ] (params);
        const result = this.safeDict (response, 'result', {});
        const orders: Dict[] = [];
        if (Array.isArray (result)) {
            for (let i = 0; i < result.length; i++) {
                const order = this.safeDict (result, i, {});
                orders.push (order);
            }
        } else {
            const values = Object.values (result);
            for (let i = 0; i < values.length; i++) {
                const value = values[i];
                if ((value !== null) && (typeof value === 'object')) {
                    orders.push (value as Dict);
                }
            }
        }
        const parsed: Order[] = [];
        for (let i = 0; i < orders.length; i++) {
            const order = orders[i];
            const orderSymbol = this.safeString (order, 'symbol');
            if (
                (market !== undefined) &&
                (orderSymbol !== market['id']) &&
                (orderSymbol !== market['symbol'])
            ) {
                continue;
            }
            parsed.push (this.parseOrder (order, market));
        }
        return this.filterBySinceLimit (
            parsed,
            since,
            limit,
            'timestamp'
        );
    }

    override async cancelOrder (
        id: string,
        symbol?: string,
        params = {}
    ): Promise<Order> {
        const request: Dict = {
            'client_id': id,
        };
        const response = await this[
            'privateDeleteV1AccountOrders'
        ] (
            this.extend (request, params)
        );
        const result = this.safeDict (response, 'result', {});
        const market = symbol !== undefined
            ? this.market (symbol)
            : undefined;
        if (Object.keys (result).length === 0) {
            return {
                'id': id,
                'clientOrderId': id,
                'status': 'canceled',
                'symbol': market !== undefined
                    ? market['symbol']
                    : undefined,
                'info': response,
            } as Order;
        }
        return this.parseOrder (result, market);
    }

    override sign (
        path: string,
        api: string = 'public',
        method: string = 'GET',
        params: Dict = {},
        headers: Dict = {},
        body: Str = undefined
    ): Dict {
        const baseUrl = this.urls['api'][api];
        const requestPath = this.implodeParams (path, params);
        let url = baseUrl + '/' + requestPath;
        const query = this.omit (
            params,
            this.extractParams (path)
        );
        if (method === 'GET') {
            if (Object.keys (query).length > 0) {
                url += '?' + this.urlencode (query);
            }
        } else if (Object.keys (query).length > 0) {
            body = this.json (query);
        }
        if (api === 'private') {
            this.checkRequiredCredentials ();
            headers = {
                'x-api-key': this.apiKey,
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            };
        }
        return {
            'url': url,
            'method': method,
            'body': body,
            'headers': headers,
        };
    }
}
