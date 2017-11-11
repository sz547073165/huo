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
def isBuy(slopeList):
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

#获取可用余额，usdt或btc
def getBlance(currency):
    subaccs = client.get('/v1/account/accounts/%s/balance' % accountIdValue)
    for sub in subaccs['list']:
        if sub['currency'] == currency and sub['type'] == 'trade':
            return sub['balance']

def tactics1(operationType):
    try:
        print(misc.getTimeStr())
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
        if operationType == 'buy':
            orderId=isSell(slopeList)
            if orderId:
                orderInfo=getOrderInfo(orderId)
                print(misc.getTimeStr())
                print(orderInfo)
                misc.sendEmail(mailHost, mailUser, mailPass, receivers, 'BTC_USDT交易报告', str(orderInfo))
                misc.setConfigKeyValue('config.ini','operationLog','type','sell')
        #isTrue=False
        time.sleep(5)
    except Exception as e:
        print(e)

def isBuyOrSellByMa5ValueAndCloseValue(operationType,ma5Value,closeValue,fatherMa5Slope):
    condition1=ma5Value > closeValue #true为卖出机会，false为买入机会
    condition2=fatherMa5Slope > 0 #当true，为上升趋势，false为下跌趋势
    if condition1:
        if operationType == 'sell':
            print('已卖出，等待买入机会')
            return 'sell', None
        #卖出操作
        balanceStr=getBlance(coinName)
        pointIndex=balanceStr.index('.')
        amount=balanceStr[0:5+pointIndex]
        orderId = place(amount,'sell-market')
        return 'sell', orderId
    else:
        if operationType == 'buy':
            print('已买入，等待卖出机会')
            return 'buy', None
        if not condition2:
            print('下跌趋势不买入')
            return 'sell', None
        #买入操作
        balanceStr=getBlance(moneyName)
        pointIndex=balanceStr.index('.')
        amount=balanceStr[0:5+pointIndex]
        orderId = place(amount,'buy-market')
        return 'buy', orderId
        

def tactics2(operationType):
    try:
        print(misc.getTimeStr())
        ma5Value, closeValue, fatherMa5Slope= getMa5AndCloseAndFatherMa5Slope()
        operation,orderId=isBuyOrSellByMa5ValueAndCloseValue(operationType,ma5Value,closeValue,fatherMa5Slope)
        misc.setConfigKeyValue('config.ini','operationLog','type',operation)
        if orderId:
            time.sleep(30)
            orderInfo=getOrderInfo(orderId)
            print(orderInfo)
            content='<html>'
            content+='<p>symbol(交易对)=%s</p>' % orderInfo['symbol']
            content+='<p>amount(订单数量)=%s</p>' % orderInfo['amount']
            content+='<p>field-cash-amount(已成交总金额)=%s</p>' % orderInfo['field-cash-amount']
            content+='<p>field-fees(已成交手续费（买入为币，卖出为钱）)=%s</p>' % orderInfo['field-fees']
            content+='<p>price(订单价格)=%s</p>' % orderInfo['price']
            content+='<p>state(订单状态)=%s</p>' % orderInfo['state']
            content+='<p>type(订单类型（buy-market：市价买, sell-market：市价卖）)=%s</p>' % orderInfo['type']
            content+='<p>%s</p>' % str(orderInfo)
            content+='</html>'
            misc.sendEmail(mailHost, mailUser, mailPass, receivers, 'BTC_USDT交易报告', content)
    except Exception as e:
        print(e)
'''main'''
isTrue=True
while isTrue:
    #获取最后一次操作的类型，buy、sell
    operationType=misc.getConfigKeyValueByKeyName('config.ini','operationLog','type')
    tactics2(operationType)
    time.sleep(180)
    
