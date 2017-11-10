#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 21:50:31 2017

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

#获取五日均线斜率
def getMA5SlopeList():
    kLine = client.get('/market/history/kline',symbol=symbolValue,period='60min',size='9')
    '''五日均线'''
    ma5 = misc.getMALine(kLine,5)
    '''五日均线斜率'''
    ma5Slope = misc.getSlope(ma5)
    return ma5Slope

#判断是否要买入
def isBuy(slopeList):
    condition1=slopeList[0] > 1 and 0 > slopeList[1] and slopeList[1] > slopeList[2] and slopeList[2] > slopeList[3]
    condition2=slopeList[0] > 2
    if condition1 or condition2:
        '''调用买入'''
        result = place(getBlance(moneyName),'buy-market')
        if result['status'] == 'ok':
            '''当status为ok时，返回订单id'''
            return result['data']

#判断是否要卖出
def isSell(slopeList):
    condition1=slopeList[0] < -1
    condition2=(slopeList[1]+slopeList[2]+slopeList[3]) < -1
    condition3=slopeList[0] < -1 and 0 < slopeList[1] and slopeList[1] < slopeList[2] and slopeList[2] < slopeList[3]
    condition4=slopeList[0] < -1 and 0 < slopeList[1] and 0 < slopeList[2] and 0 < slopeList[3]
    if condition3 or condition4:
        '''调用卖出'''
        result = place(getBlance(coinName),'sell-market')
        if result['status'] == 'ok':
            '''当status为ok时，返回订单id'''
            return result['data']

#查询当前成交、历史成交
def getMatchResults():
    matchResults = client.get('/v1/order/matchresults',symbol=symbolValue)
    return matchResults

#查询当前委托、历史委托
def getOrders():
    orders = client.get('/v1/order/orders',symbol=symbolValue,states='filled')
    return orders

#判断最后一个API订单是买入，还是卖出，成交价格，手续费
def lastMatchResultIsWhatAndPriceAndFees(matchResults):
    for i in range(len(matchResults)):
        matchResult = matchResults[i]
        source = matchResult['source']
        symbol = matchResult['symbol']
        typeValue = matchResult['type']
        price = matchResult['price']
        fees = matchResult['filled-fees']
        if not source == 'web':
            continue
        if not symbol == symbolValue:
            continue
        if typeValue == 'buy-market' or typeValue == 'buy-limit':
            return 'buy',price,fees
        if typeValue == 'sell-market' or typeValue == 'sell-limit':
            return 'sell',price,fees

#创建并执行一个新订单，返回订单ID
def place(amount,typeValue):
    params={}
    params['account-id']=accountIdValue
    params['amount']=amount#限价单表示下单数量，市价买单时表示买多少钱，市价卖单时表示卖多少币
    params['symbol']=symbolValue
    params['type']=typeValue
    return client.post('/v1/order/orders/place',params)

#查询某个订单详情
def getOrderInfo(orderId):
    return client.get('/v1/order/orders/%s' % orderId)

#获取可用余额，usdt或btc
def getBlance(currency):
    subaccs = client.get('/v1/account/accounts/%s/balance' % accountIdValue)
    for sub in subaccs['list']:
        if sub['currency'] == currency and sub['type'] == 'trade':
            return float(sub['balance'])


'''main'''
#获取最后一次操作的类型，buy、sell
operationType=misc.getConfigKeyValueByKeyName('config.ini','operationLog','type')
isTrue=True
while isTrue:
    #获取均线斜率
    slopeList = getMA5SlopeList()
    print(slopeList)
    if operationType == 'sell':
        orderId=isBuy(slopeList)
        if orderId:
            orderInfo=getOrderInfo(orderId)
            print(misc.getTimeStr())
            print(orderInfo)
            misc.sendEmail(mailHost, mailUser, mailPass, receivers, 'BTC_USDT交易报告', str(orderInfo))
            misc.setConfigKeyValue('config.ini','operationLog','type','buy')
        pass
    if operationType == 'buy':
        orderId=isSell(slopeList)
        if orderId:
            orderInfo=getOrderInfo(orderId)
            print(misc.getTimeStr())
            print(orderInfo)
            misc.sendEmail(mailHost, mailUser, mailPass, receivers, 'BTC_USDT交易报告', str(orderInfo))
            misc.setConfigKeyValue('config.ini','operationLog','type','sell')
        pass
    #isTrue=False
    time.sleep(5)
    pass

