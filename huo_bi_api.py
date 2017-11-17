#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 09:40:40 2017

@author: Marco
"""

from huo_bi_utils import ApiClient, ApiError
from person import API_KEY
from person import API_SECRET
import misc

client = ApiClient(API_KEY, API_SECRET)

def get_user_info():
    user_info = client.get('/v1/users/user')
    return user_info

def get_accounts():
    accounts = client.get('/v1/account/accounts')
    return accounts

def get_account_id():
    accounts = get_accounts()
    account = accounts[0]
    return account['id']

def get_k_line(symbol_value, period_value='15min', size_value=10):
    k_line = client.get('/market/history/kline', symbol=str(symbol_value), period=str(period_value), size=str(size_value))
    return k_line

def get_ma_line(k_line, period_value=5):
    if len(k_line) < period_value:
        return
    ma_line = []
    for i in range(len(k_line) - period_value + 1):
        close_price_sum = 0
        for j in range(i, i + period_value):
            close_price_sum += float(k_line[j]['close'])
        ma_line.append(round(close_price_sum / period_value, 4))
    return ma_line

def get_slope_line(ma_line):
    if len(ma_line) < 2:
        return
    slope_line = []
    for i in range(len(ma_line) - 1):
        slope_line.append(round(ma_line[i] - ma_line[i+1], 4))
    return slope_line

#创建并执行一个新订单，返回订单ID
def do_place(account_id, amount, symbol_value, type_value):
    params={}
    params['account-id']=account_id
    params['amount']=amount#限价单表示下单数量，市价买单时表示买多少钱，市价卖单时表示卖多少币
    params['symbol']=symbol_value
    params['type']=type_value#buy-market：市价买, sell-market：市价卖
    return client.post('/v1/order/orders/place',params)

#查询当前成交、历史成交
def get_match_results(symbol_value):
    match_results = client.get('/v1/order/matchresults',symbol=symbol_value)
    return match_results

#查询某个订单详情
    '''{
    "id": 59378,
    "symbol": "ethcny",
    "account-id": 100009,
    "amount": "10.1000000000",
    "price": "100.1000000000",
    "created-at": 1494901162595,
    "type": "buy-limit",
    "field-amount": "10.1000000000",
    "field-cash-amount": "1011.0100000000",
    "field-fees": "0.0202000000",
    "finished-at": 1494901400468,
    "user-id": 1000,
    "source": "api",
    "state": "filled",
    "canceled-at": 0,
    "exchange": "huobi",
    "batch": ""
    }'''
def get_order_info(order_id):
    order_info = client.get('/v1/order/orders/%s' % order_id)
    return order_info

#查询某个订单的成交明细
    '''{
     "id": 29553,
     "order-id": 59378,
     "match-id": 59335,
     "symbol": "ethcny",
     "type": "buy-limit",
     "source": "api",
     "price": "100.1000000000",
     "filled-amount": "9.1155000000",
     "filled-fees": "0.0182310000",
     "created-at": 1494901400435   
     }'''
def get_order_detail(order_id):
    order_detail = client.get('/v1/order/orders/%s/matchresults' % order_id)
    return order_detail

#获取可用余额，usdt或btc
def get_balance(account_id, currency):
    subaccs = client.get('/v1/account/accounts/%s/balance' % account_id)
    for sub in subaccs['list']:
        if sub['currency'] == currency and sub['type'] == 'trade':
            return misc.get_float_str(sub['balance'])
