import urllib.parse
import json
import hashlib
import hmac
import numpy as np
from collections import OrderedDict
import http.client
import time

"""Url, Api-ключ и секретный ключ конкретно для Livecoin.net"""

server1 = "https://api.livecoin.net"
server = 'api.livecoin.net'
api_key = "****"
secret_key = '****'

"""Запросы"""


# GET-запрос
def _get_request(method, data, needsign):
    encoded_data = urllib.parse.urlencode(data)
    # если True, то делаем подпись
    if needsign:
        sign = hmac.new(secret_key.encode(), msg=encoded_data.encode(), digestmod=hashlib.sha256).hexdigest().upper()
        headers = {"Api-key": api_key, "Sign": sign}
    else:
        headers = {}

    conn = http.client.HTTPSConnection(server)
    conn.request("GET", method + '?' + encoded_data, '', headers)
    response = conn.getresponse().read().decode('utf-8')
    conn.close()

    return response

# POST-запрос
def _post_request(method, data):
    encoded_data = urllib.parse.urlencode(data)
    sign = hmac.new(secret_key.encode(), msg=encoded_data.encode(), digestmod=hashlib.sha256).hexdigest().upper()
    headers = {"Api-key": api_key, "Sign": sign, "Content-type": "application/x-www-form-urlencoded"}

    conn = http.client.HTTPSConnection(server)
    conn.request("POST", method, encoded_data, headers)
    response = conn.getresponse().read().decode('utf-8')
    conn.close()
    return response

"""Общие функции"""


# получить текущий прайс конкретной пары
def pair_cost_summary():
    # запрос
    method = '/exchange/order_book'
    data = OrderedDict([('currencyPair', 'BTC/USD')])
    response = _get_request(method, data, False)
    loads = json.loads(response)

    # цена
    costs = []
    costs += [float(loads['asks'][i][0]) for i in range(10)] + [float(loads['bids'][i][0]) for i in range(10)]
    price = [np.mean(costs)]

    # bid и ask
    ask = [float(loads['asks'][0][0])]
    bid = [float(loads['bids'][0][0])]

    # на вывод
    out = price + ask + bid
    return out


# получаем список открытых ордеров
def open_orders():
    method = '/exchange/client_orders'
    data = OrderedDict(sorted([('currencyPair', 'BTC/USD'), ('openClosed', 'OPEN')]))
    response = _get_request(method, data, True)
    loads = json.loads(response)
    return loads


# получаем список частично исполненных ордеров
def partially_orders():
    method = '/exchange/client_orders'
    data = OrderedDict(sorted([('currencyPair', 'BTC/USD'), ('openClosed', 'PARTIALLY'), ('openClosed', 'OPEN')]))
    response = _get_request(method, data, True)
    loads = json.loads(response)
    return loads


# доступный баланс
def available_balances(currency_1, currency_2):
    method = '/payment/balances'
    data = OrderedDict(sorted([('currency', str(currency_1)+','+str(currency_2))]))
    response = _get_request(method, data, True)
    # print(json.loads(response))
    loads_1 = []
    loads_2 = []
    for elem in json.loads(response):
        if elem['type'] == 'available' and elem['currency'] == currency_1:
            loads_1 = [elem['value']]
        if elem['type'] == 'available' and elem['currency'] == currency_2:
            loads_2 = [elem['value']]
    out = loads_1 + loads_2
    return out


def cancel_open_orders():
    a = open_orders()["data"]
    if len(a) != 0:
        for order in a:
            time.sleep(1)
            order_id = order['id']
            method = '/exchange/cancellimit'
            data = OrderedDict(sorted([('currencyPair', 'BTC/USD'), ('orderId', order_id)]))
            b = _post_request(method, data)
    return a


# открыть ордер на покупку
def buy_currency(price, quantity):
    method = '/exchange/buylimit'
    data = OrderedDict(sorted([('currencyPair', 'BTC/USD'), ('price', str(price)), ('quantity', str(quantity))]))
    b = _post_request(method, data)
    return b


def sell_currency(price, quantity):
    method = '/exchange/selllimit'
    data = OrderedDict(sorted([('currencyPair', 'BTC/USD'), ('price', str(price)), ('quantity', str(quantity))]))
    b = _post_request(method, data)
    return b