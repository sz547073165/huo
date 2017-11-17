#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 00:46:24 2017

@author: Marco
"""

from person import API_KEY, API_SECRET, mailPass
import huoBiApi, misc
import time

mailHost = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'mailHost')
mailUser = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'mailUser')
receivers = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'receivers').split(',')
#交易对
symbolValue='bccusdt'
moneyName='usdt'
coinName='bcc'
client = huoBiApi.ApiClient(API_KEY, API_SECRET)
accs = client.get('/v1/account/accounts')
accountIdValue = accs[0].id
global buySignal
buySignal=0
global sellSignal
sellSignal=0
buySignalMax=1
sellSignalMax=1

#查询当前成交、历史成交
def getMatchResults():
    matchResults = client.get('/v1/order/matchresults',symbol=symbolValue)
    return matchResults
#查询某个订单详情
def getOrderInfo(orderId):
    return client.get('/v1/order/orders/%s' % orderId)
#字符串截取的方式获取小数点后保留4位的数字
def getFloatStr(numberStr):
    pointIndex=numberStr.index('.')
    flaotStr=numberStr[0:5+pointIndex]
    return flaotStr
#创建并执行一个新订单，返回订单ID
def place(amount,typeValue):
    params={}
    params['account-id']=accountIdValue
    params['amount']=amount#限价单表示下单数量，市价买单时表示买多少钱，市价卖单时表示卖多少币
    params['symbol']=symbolValue
    params['type']=typeValue
    print(params)
    return client.post('/v1/order/orders/place',params)

#获取可用余额，usdt或bcc
def getBlance(currency):
    subaccs = client.get('/v1/account/accounts/%s/balance' % accountIdValue)
    for sub in subaccs['list']:
        if sub['currency'] == currency and sub['type'] == 'trade':
            return sub['balance']
        
def getKLine(periodStr,dayStr):
    return client.get('/market/history/kline',symbol=symbolValue,period=periodStr,size=str(int(dayStr)+1))

def getMa(kLine,dayStr):
    ma = misc.getMALine(kLine,dayStr)
    return ma

def checkCross(operationType,kLine,smallMa,bigMa):
    condition1 = operationType == 'sell'
    condition2 = operationType == 'buy'
    condition3 = bigMa[1] > smallMa[1] and smallMa[0] > bigMa[0] and float(kLine['close']) > float(kLine['open'])
    condition4 = bigMa[2] > smallMa[2] and smallMa[0] > bigMa[0] and float(kLine['close']) > float(kLine['open'])
    if condition1 and (condition3 or condition4):
        print('买入信号+1')
        global buySignal
        buySignal = buySignal+1
    elif condition2 and smallMa[1] > bigMa[1] and bigMa[0] > smallMa[0]:
        print('卖出信号+1')
        global sellSignal
        sellSignal = sellSignal+1
    else:
        print('无交叉，信号清0')
        buySignal=0
        sellSignal=0

def doBuy():
    #买入操作
    amount=misc.getConfigKeyValueByKeyName('config.ini',symbolValue,'usdt')
    orderId = place(amount,'buy-market')
    return 'buy', orderId

def doSell():
    #卖出操作
    balanceStr=getBlance(coinName)
    pointIndex=balanceStr.index('.')
    amount=balanceStr[0:5+pointIndex]
    orderId = place(amount,'sell-market')
    return 'sell', orderId

def checkSignal():
    global buySignal
    global sellSignal
    if buySignal >= buySignalMax:
        return doBuy()
    elif sellSignal >= sellSignalMax:
        return doSell()
    else:
        return None, None

def tactics1(operationType):
    print(misc.getTimeStr())
    periodStr = '30min'
    kLine = getKLine(periodStr,'15')
    smallMa = getMa(kLine,3)
    bigMa = getMa(kLine,14)
    checkCross(operationType,kLine[0],smallMa,bigMa)
    operation,orderId = checkSignal()
    if orderId:
        misc.setConfigKeyValue('config.ini',symbolValue,'type',operation)
        global buySignal
        buySignal=0
        global sellSignal
        sellSignal=0
        time.sleep(10)
        if operation == 'sell':
            tempOrder=getOrderInfo(orderId)
            fieldCashAmount=float(tempOrder['field-cash-amount'])
            fieldFees=float(tempOrder['field-fees'])
            usdt=getFloatStr(str(fieldCashAmount-fieldFees))
            misc.setConfigKeyValue('config.ini',symbolValue,'usdt',usdt)
        orderInfo=getMatchResults()[0]
        print(orderInfo)
        content='<html>'
        content+='<p>symbol(交易对)=%s</p>' % orderInfo['symbol']
        content+='<p>type(订单类型)=%s</p>' % orderInfo['type']
        content+='<p>price(成交价格)=%s</p>' % orderInfo['price']
        content+='<p>filled-amount(订单数量)=%s</p>' % orderInfo['filled-amount']
        content+='<p>filled-fees(已成交手续费)=%s</p>' % orderInfo['filled-fees']
        content+='<p>%s</p>' % str(orderInfo)
        content+='</html>'
        misc.sendEmail(mailHost, mailUser, mailPass, receivers, '交易报告', content)

isTrue = True
while isTrue:
    #获取最后一次操作的类型，buy、sell
    try:
        operationType=misc.getConfigKeyValueByKeyName('config.ini',symbolValue,'type')
        tactics1(operationType)
        sleepTime=300
        time.sleep(sleepTime)
    except Exception as e:
        print(e)