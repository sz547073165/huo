#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 21:50:31 2017

@author: Marco
"""

from person import API_KEY
from person import API_SECRET
import huoBiApi, misc

#交易对
symbolValue='bccusdt'
client = huoBiApi.ApiClient(API_KEY, API_SECRET)
accs = client.get('/v1/account/accounts')
accountIdValue = accs[0].id

#获取五日均线斜率
def getMA5SlopeList(client):
    kLine = client.get('/market/history/kline',symbol=symbolValue,period='60min',size='9')
    '''五日均线'''
    ma5 = misc.getMALine(kLine,5)
    '''五日均线斜率'''
    ma5Slope = misc.getSlope(ma5)
    return ma5Slope

#判断是否要买入
def isBuy(client, slopeList):
    if slopeList[0] > 1 and 0 > slopeList[1] and slopeList[1] > slopeList[2] and slopeList[2] > slopeList[3]:
        '''调用买入'''

#判断是否要卖出
def isSell(client, slopeList):
    if slopeList[0] < -1:
        '''调用卖出'''

#查询当前成交、历史成交
def getMatchResults(client):
    matchResults = client.get('/v1/order/matchresults',symbol=symbolValue,direct='prev')
    return matchResults

#判断最后一个API订单是买入，还是卖出，成交价格，手续费
def lastMatchResultIsWhatAndPriceAndFees(matchResults):
    for i in range(matchResults):
        matchResult = matchResults[i]
        source = matchResult['source']
        symbol = matchResult['symbol']
        typeValue = matchResult['type']
        price = matchResult['price']
        fees = matchResult['field-fees']
        if not source == 'api':
            continue
        if not symbol == symbolValue:
            continue
        if typeValue == 'buy-market' or typeValue == 'buy-limit':
            return 'buy',price,fees
        if typeValue == 'sell-market' or typeValue == 'sell-limit':
            return 'sell',price,fees

#创建并执行一个新订单，返回订单ID
def place(client,amount,typeValue):
    params={}
    params['account-id']=accountIdValue
    params['amount']=amount#限价单表示下单数量，市价买单时表示买多少钱，市价卖单时表示卖多少币
    params['symbol']=symbolValue
    params['type']=typeValue
    return client.post('/v1/order/orders/place',params)

#查询某个订单详情
def getOrderInfo(orderId):
    return client.get('/v1/order/orders/%s' % orderId)

#获取可用余额，usdt或bcc
def getUSDTBlance(currency):
    subaccs = client.get('/v1/account/accounts/%s/balance' % accountIdValue)
    for sub in subaccs['list']:
        if sub['currency'] == currency and sub['type'] == 'trade':
            return float(sub['balance'])


'''main'''
#while True:
    #pass


print(getUSDTBlance())