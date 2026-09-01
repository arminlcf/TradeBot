import Exchange from './abstract/wallex.js';
import type { Balances, Dict, Int, MarketInterface, OHLCV, Order, Str, Ticker } from './base/types.js';
export default class wallex extends Exchange {
    describe(): any;
    fetchMarkets(params?: {}): Promise<MarketInterface[]>;
    fetchTicker(symbol: string, params?: {}): Promise<Ticker>;
    fetchOHLCV(symbol: string, timeframe?: string, since?: Int, limit?: Int, params?: {}): Promise<OHLCV[]>;
    fetchBalance(params?: {}): Promise<Balances>;
    createOrder(symbol: string, type: string, side: string, amount: number, price?: number | undefined, params?: {}): Promise<Order>;
    parseOrder(order: Dict, market?: MarketInterface | undefined): Order;
    fetchOrder(id: string, symbol?: string, params?: {}): Promise<Order>;
    fetchOpenOrders(symbol?: string, since?: Int, limit?: Int, params?: {}): Promise<Order[]>;
    cancelOrder(id: string, symbol?: string, params?: {}): Promise<Order>;
    sign(path: string, api?: string, method?: string, params?: Dict, headers?: Dict, body?: Str): Dict;
}
