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

usdt = api.get_balance(account_id,'usdt')
btc = api.get_balance(account_id,'btc')
bcc = api.get_balance(account_id,'bcc')
print('usdt = %s' % usdt)
print('btc  = %s' % btc)
print('bcc  = %s' % bcc)


order_detail = api.get_order_detail(210157698)[0]
print(order_detail)

value = 0.1562
print(1.01654 * value)
print(0.99487929 * value)