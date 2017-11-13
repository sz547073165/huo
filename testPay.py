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

#查询最后一个买入订单的成交均价*1.005的价格
def getLastBuyOrderPrice():
    matchResults=getMatchResults()
    for match in matchResults:
        if match['type']=='buy-market' and match['symbol']==symbolValue:
            print(match)
            return round(float(match['price']) * 1.01,4)

print(getLastBuyOrderPrice())


