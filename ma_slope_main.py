# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 16:13:03 2017

@author: Administrator
"""

import huo_bi_api as api
import misc
import time
from person import mailPass as mail_pass

mail_host = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'mailHost')
mail_user = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'mailUser')
receivers = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'receivers').split(',')
#交易对
symbol_value = 'bccbtc'
money_name = 'btc'
coin_name = 'bcc'
period_value = '60min'
account_id = api.get_account_id()
global buy_signal
global sell_signal
buy_signal = 0
sell_signal = 0
buy_signal_max = 5
sell_signal_max = 5

k_line = api.get_k_line(symbol_value,period_value,10)
print(k_line)