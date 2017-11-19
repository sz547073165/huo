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
symbol_value = 'bccbtc'
money_name = 'btc'
coin_name = 'bcc'
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

order_list = api.get_match_results(symbol_value)
print(order_list[0])
print(order_list[1])

price_buy = float(misc.getConfigKeyValueByKeyName('config.ini',symbol_value,'price_buy'))
price_sell = float(misc.getConfigKeyValueByKeyName('config.ini', symbol_value,'price_sell'))
content='<p>盈亏=%.4f%%</p>' % ((price_sell / price_buy - 1 - 0.005) * 100)
print(content)