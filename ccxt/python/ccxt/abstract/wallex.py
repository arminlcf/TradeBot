from ccxt.base.types import Entry


class ImplicitAPI:
    public_get_v1_markets = publicGetV1Markets = Entry('v1/markets', 'public', 'GET', {'cost': 1})
    public_get_v1_udf_history = publicGetV1UdfHistory = Entry('v1/udf/history', 'public', 'GET', {'cost': 1})
    private_get_v1_account_balances = privateGetV1AccountBalances = Entry('v1/account/balances', 'private', 'GET', {'cost': 1})
    private_get_v1_account_openorders = privateGetV1AccountOpenOrders = Entry('v1/account/openOrders', 'private', 'GET', {'cost': 1})
    private_get_v1_account_orders_clientorderid = privateGetV1AccountOrdersClientOrderId = Entry('v1/account/orders/{clientOrderId}', 'private', 'GET', {'cost': 1})
    private_post_v1_account_orders = privatePostV1AccountOrders = Entry('v1/account/orders', 'private', 'POST', {'cost': 1})
    private_delete_v1_account_orders = privateDeleteV1AccountOrders = Entry('v1/account/orders', 'private', 'DELETE', {'cost': 1})
