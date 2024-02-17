import requests


def get_price_and_percent24h(list_symbol: list) -> dict:

    url_price = f'https://api3.binance.com/api/v3/ticker/price'
    url_price_24 = f'https://api3.binance.com/api/v3/ticker/24hr'
    params = {
        'symbols': '[' + ','.join([f'"{symbol}"' for symbol in list_symbol]) + ']'}
    response_price = requests.get(url_price, params=params)
    response_price_24 = requests.get(url_price_24, params=params)
    data_price = response_price.json()
    data_price_24 = response_price_24.json()
    dict_result = {}
    for symbol_price, symbol_24 in zip(data_price, data_price_24):
        price = round(float(symbol_price['price']), 10)
        price_change_percent = round(float(symbol_24['priceChangePercent']), 2)
        dict_result[symbol_price['symbol']] = {
            'price': price, 'price_change_percent': price_change_percent}
    return dict_result
