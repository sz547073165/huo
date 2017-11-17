#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 22:22:26 2017

@author: Marco
"""

import huo_bi_api as api
import misc
import time
from person import mailPass as mail_pass

mail_host = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'mailHost')
mail_user = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'mailUser')
receivers = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'receivers').split(',')
#交易对
symbol_value = 'btcusdt'
money_name = 'usdt'
coin_name = 'btc'
account_id = api.get_account_id()
global buy_signal
global sell_signal
buy_signal = 0
sell_signal = 0
buy_signal_max = 4
sell_signal_max = 4

def get_condition():
    operationType = misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'type')
    k_line = api.get_k_line(symbol_value, '15min')
    
    

k_line = api.get_k_line(symbol_value, '15min', 10)
#print(k_line)
ma_line = api.get_ma_line(k_line, 5)
#print(ma_line)
slope_line = api.get_slope_line(ma_line)
print(slope_line)
slope_sum = 0
for slope in slope_line:
    slope_sum = slope_sum + slope
print(slope_sum)
close_value = k_line[0]['close']
print('close_value =',close_value)
print('close_value * 0.5% =',float(close_value) * 0.005)