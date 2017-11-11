#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 13:01:33 2017

@author: Marco
"""

from person import API_KEY, API_SECRET, mailPass
import huoBiApi, misc
import time

mailHost = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'mailHost')
mailUser = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'mailUser')
receivers = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'receivers').split(',')
#交易对
symbolValue='btcusdt'
moneyName='usdt'
coinName='btc'
client = huoBiApi.ApiClient(API_KEY, API_SECRET)
accs = client.get('/v1/account/accounts')
accountIdValue = accs[0].id

#创建并执行一个新订单，返回订单ID
def place(amount,typeValue):
    params={}
    params['account-id']=accountIdValue
    params['amount']=amount#限价单表示下单数量，市价买单时表示买多少钱，市价卖单时表示卖多少币
    params['symbol']=symbolValue
    params['type']=typeValue
    print(params)
    return client.post('/v1/order/orders/place',params)

def getBlance(currency):
    subaccs = client.get('/v1/account/accounts/%s/balance' % accountIdValue)
    for sub in subaccs['list']:
        if sub['currency'] == currency and sub['type'] == 'trade':
            return sub['balance']

#

balance='143.2222222222'
pointIndex=balance.index('.')
mmm=float(balance[0:5+pointIndex])
print(balance.__class__)
print(pointIndex)
print(balance[0:5+pointIndex])
print(mmm)