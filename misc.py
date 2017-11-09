#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 23:52:09 2017

@author: Marco
"""
import time

'''获取当前时间'''
def getTimeStr():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

'''获取当前时间'''
def getTimeStrWithUnixTimestamp(unixTimestamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(unixTimestamp))

'''获取均线，默认获取五日均线'''
def getMALine(kLine, typeStr=5):
    if len(kLine) < typeStr:
        return
    ma5Line = []
    for i in range(len(kLine)-typeStr+1):
        closePriceSum = 0
        for j in range(i, i + typeStr):
            closePriceSum += float(kLine[j]['close'])
        ma5Line.append(round(closePriceSum / typeStr, 4))
    return ma5Line

'''获取斜率'''
def getSlope(MALine):
    if len(MALine) < 2:
        return
    slope = []
    for i in range(len(MALine)-1):
        slope.append(round(MALine[i]-MALine[i+1],4))
    return slope