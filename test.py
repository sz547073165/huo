#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 21:50:31 2017

@author: Marco
"""

from person import API_KEY
from person import API_SECRET
import huoBiApi, misc

def getMA5SlopeList(client):
    kLine = client.get('/market/history/kline',symbol='bccusdt',period='60min',size='9')
    '''五日均线'''
    ma5 = misc.getMALine(kLine,5)
    '''五日均线斜率'''
    ma5Slope = misc.getSlope(ma5)
    return ma5Slope

def isBuy(client, slopeList):
    if slopeList[0] > 1 and 0 > slopeList[1] and slopeList[1] > slopeList[2] and slopeList[2] > slopeList[3]:
        '''调用买入'''

def isSell(client, slopeList):
    if slopeList[0] < -1:
        '''调用卖出'''

'''main'''
client = huoBiApi.ApiClient(API_KEY, API_SECRET)

while True:
    pass
    