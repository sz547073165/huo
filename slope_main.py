#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 21:33:35 2017

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
buySignalMax=6
sellSignalMax=6

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
    print(params)
    return client.post('/v1/order/orders/place',params)

#查询某个订单详情
def getOrderInfo(orderId):
    return client.get('/v1/order/orders/%s' % orderId)

#查询最后一个买入订单的成交均价*1.005的价格
def getLastBuyOrderPrice():
    matchResults=getMatchResults()
    for match in matchResults:
        if match['type']=='buy-market':
            return round(float(match['price']) * 1.01,4)

#获取可用余额，usdt或btc
def getBlance(currency):
    subaccs = client.get('/v1/account/accounts/%s/balance' % accountIdValue)
    for sub in subaccs['list']:
        if sub['currency'] == currency and sub['type'] == 'trade':
            return sub['balance']

#字符串截取的方式获取小数点后保留4位的数字
def getFloatStr(numberStr):
    pointIndex=numberStr.index('.')
    flaotStr=numberStr[0:5+pointIndex]
    return flaotStr

def getKLine(periodStr,dayStr):
    return client.get('/market/history/kline',symbol=symbolValue,period=periodStr,size=str(int(dayStr)+1))

def getLastMASlop(kLine,dayStr):
    '''均线'''
    ma = misc.getMALine(kLine,dayStr)
    '''均线斜率'''
    maSlope = misc.getSlope(ma)
    return maSlope[0]
#获取均线斜率
def getLastMASlope(periodStr,dayStr):
    kLine = client.get('/market/history/kline',symbol=symbolValue,period=periodStr,size=str(int(dayStr)+1))
    '''均线'''
    ma = misc.getMALine(kLine,dayStr)
    '''均线斜率'''
    maSlope = misc.getSlope(ma)
    return maSlope

def getLastClose(periodStr):
    kLine = client.get('/market/history/kline',symbol=symbolValue,period=periodStr,size='1')
    return float(kLine[0]['close'])

def getMa5AndCloseAndFatherMa5Slope():
    kLine = client.get('/market/history/kline',symbol=symbolValue,period='15min',size='5')
    '''五日均线'''
    ma5 = misc.getMALine(kLine,5)
    last = kLine[0]['close']
    
    fatherKLine = client.get('/market/history/kline',symbol=symbolValue,period='60min',size='6')
    fatherMa5 = misc.getMALine(fatherKLine,5)
    fatherMa5Slope = misc.getSlope(fatherMa5)
    return ma5[0], last, fatherMa5Slope[0]

#判断是否要买入
def buy(slopeList):
    condition1=slopeList[0] > abs(slopeList[2]) and 0 > slopeList[1] and slopeList[1] > slopeList[2] and slopeList[2] > slopeList[3]
    condition2=slopeList[0] > 3
    print('isBuy条件判断情况：','\t',condition1,'\t',condition2)
    if condition1 or condition2:
        '''调用买入'''
        result = place(getBlance(moneyName),'buy-market')
        if result['status'] == 'ok':
            '''当status为ok时，返回订单id'''
            return result['data']

#判断是否要卖出
def isSell(slopeList):
    condition1=slopeList[0] < -30
    condition2=(slopeList[1]+slopeList[2]+slopeList[3]) < -30
    condition3=slopeList[0] < -20 and 0 < slopeList[1] and slopeList[1] < slopeList[2] and slopeList[2] < slopeList[3]
    condition4=slopeList[0] < -40 and 0 < slopeList[1] and 0 < slopeList[2] and 0 < slopeList[3]
    print('isSell条件判断情况：','\t',condition3,'\t',condition4)
    if condition3 or condition4:
        '''调用卖出'''
        result = place(getBlance(coinName),'sell-market')
        if result['status'] == 'ok':
            '''当status为ok时，返回订单id'''
            return result['data']

def doOperation(operationType,ma5LastSlope,ma11LastSlope):
    if operationType == 'sell':
        if ma5LastSlope < 0 or ma11LastSlope < 0:
            print('条件不满足，不买入')
            return 10, 'sell', None
        #买入操作
        amount=misc.getConfigKeyValueByKeyName('config.ini',symbolValue,'usdt')
        orderId = place(amount,'buy-market')
        return 180, 'buy', orderId
    if operationType == 'buy':
        if ma5LastSlope > 0:
            print('条件不满足，不卖出')
            return 180, 'buy', None
        #卖出操作
        balanceStr=getBlance(coinName)
        pointIndex=balanceStr.index('.')
        amount=balanceStr[0:5+pointIndex]
        orderId = place(amount,'sell-market')
        return 10, 'sell', orderId

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

def checkOperation(operationType,ma4LastSlope,ma11LastSlope,ma2LastSlope,ma3LastSlope,ma5LastSlope,lastClose,price):
    if operationType == 'sell':
        if ma4LastSlope < 0 or ma2LastSlope < 0 or ma3LastSlope < 0 :
            print('条件不满足，不买入')
            global buySignal
            buySignal=0
            return
        print('满足买入条件，信号＋1')
        buySignal=buySignal+1
        return
    if operationType == 'buy':
        if price > closeValue:
            print('涨幅超过1%，立即卖出')
            global sellSignal
            sellSignal=sellSignalMax
            return
        if not((ma4LastSlope < 0 and ma3LastSlope < 0) or (ma2LastSlope < 0 and ma3LastSlope < 0)):
            print('条件不满足，不卖出')
            sellSignal=0
            return
        sellSignal=sellSignal+1
        print('满足卖出条件，信号＋1')
        return

def checkSignal():
    global buySignal
    print('buySignal=%s' % buySignal)
    global sellSignal
    print('sellSignal=%s' % sellSignal)
    if buySignal >= buySignalMax:
        return doBuy()
    if sellSignal >= sellSignalMax:
        return doSell()
    return None, None
    
def tactics1(operationType):
    #try:
    print(misc.getTimeStr())
    #获取均线斜率
    period='1min'
    ma4LastSlope = getLastMASlope(period,4)[0]
    ma11LastSlope = getLastMASlope(period,11)[0]
    ma2LastSlope = getLastMASlope(period,2)[0]
    ma3LastSlope = getLastMASlope(period,3)[0]
    ma5LastSlope = getLastMASlope(period,5)[0]
    lastClose = getLastClose(period)
    price=getLastBuyOrderPrice()
    print('ma2=',ma2LastSlope,'\tma3=',ma3LastSlope,'\tma4=',ma4LastSlope,'\tlastClose=',lastClose,'\tprice=',price)
    checkOperation(operationType,ma4LastSlope,ma11LastSlope,ma2LastSlope,ma3LastSlope,ma5LastSlope,lastClose,price)
    operation,orderId=checkSignal()
    if orderId:
        misc.setConfigKeyValue('config.ini',symbolValue,'type',operation)
        global buySignal
        buySignal=0
        global sellSignal
        sellSignal=0
        time.sleep(30)
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
        content+='<p>filled-amount(订单数量)=%s</p>' % orderInfo['filled-amount']
        content+='<p>filled-fees(已成交手续费)=%s</p>' % orderInfo['filled-fees']
        content+='<p>price(成交价格)=%s</p>' % orderInfo['price']
        content+='<p>type(订单类型（buy-market：市价买, sell-market：市价卖）)=%s</p>' % orderInfo['type']
        content+='<p>%s</p>' % str(orderInfo)
        content+='</html>'
        misc.sendEmail(mailHost, mailUser, mailPass, receivers, '交易报告', content)
    #except Exception as e:
    #    print(e)
    #    return 10

'''main'''
isTrue=True
while isTrue:
    #获取最后一次操作的类型，buy、sell
    try:
        operationType=misc.getConfigKeyValueByKeyName('config.ini',symbolValue,'type')
        tactics1(operationType)
        sleepTime=7
        time.sleep(sleepTime)
    except Exception as e:
        print(e)
    
