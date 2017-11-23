#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 23:52:09 2017

@author: Marco
"""
import time
import configparser
import smtplib
from email.mime.text import MIMEText
from email.header import Header

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

'''字符串截取的方式获取小数点后保留4位的数字，返回字符串'''
def get_float_str(number_str):
    point_index=number_str.index('.')
    float_str=number_str[0:5 + point_index]
    return float_str

'''读取配置文件的key所对应的value'''
def getConfigKeyValueByKeyName(fileName, section, keyName):
    conf = configparser.ConfigParser()
    conf.read(fileName, 'utf-8')
    keyValue = conf.get(section, keyName)
    if keyValue:
        return keyValue
    else:
        return

'''设置keyName和keyValue到配置文件，比较粗糙，暂时用try、catch检查'''
def setConfigKeyValue(fileName, section, keyName, keyValue):
    conf = configparser.ConfigParser()
    conf.read(fileName, 'utf-8')
    try:
        conf.add_section(section)
    except:
        pass
    conf.set(section, keyName, str(keyValue))
    conf.write(open(fileName,'w'))

'''发送邮件'''
def sendEmail(mailHost, mailUser, mailPass, receivers, subject, content):
    try:
        email_client = smtplib.SMTP(mailHost, 25)
        email_client.login(mailUser, mailPass)
        # create msg
        msg = MIMEText(content, 'HTML', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')  # subject
        msg['From'] = mailUser
        msg['To'] = ','.join(receivers)
        email_client.sendmail(mailUser, receivers, msg.as_string())
        print('邮件发送成功，目标：%s' % receivers)
    except Exception as e:
        print('邮件发送失败，原因：%s' % e)
    finally:
        email_client.quit()