#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 02:45:53 2017

@author: Marco
"""

import huo_bi_api as api
from huo_bi_utils import ApiError, ApiNetworkError
import misc
import time
from person import mailPass as mail_pass

mail_host = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'mailHost')
mail_user = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'mailUser')
receivers = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'receivers').split(',')

def get_buy_condition(symbol_value):
    period_value = misc.getConfigKeyValueByKeyName('config.ini', 'config', 'period_value')
    k_line = api.get_k_line(symbol_value, period_value, 8)
    last_close_value = k_line[0]['close']
    ma_line = api.get_ma_line(k_line, 4)
    last_ma_value = ma_line[0]
    slope_list = api.get_slope_line(ma_line)
    print(slope_list)
    slope_sum = 0
    for slope in slope_list:
        slope_sum = slope_sum + slope
    slope_sum = round(slope_sum, 6)
    slope_sum_last = slope_list[0] + slope_list[1]
    slope_sum_early = slope_list[3] + slope_list[2]

    condition1 = last_close_value > last_ma_value #市价在均线之上
    condition2 = last_close_value > k_line[0]['open'] #true收盘价大于开盘价，阳线
    condition3 = slope_sum_last > slope_sum_early and slope_sum_last > 0 #斜率后半段大于前半段，且大于0
    print('市价在均线之上 = %s' % condition1)
    print('阳线 = %s' % condition2)
    print('斜率后半段大于前半段，且大于0 = %s' % condition3)
    return condition1, condition2, condition3

def get_sell_condition(symbol_value):
    period_value = misc.getConfigKeyValueByKeyName('config.ini', 'config', 'period_value')
    price_buy = float(misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'price_buy'))
    price_max = float(misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'price_max'))
    k_line = api.get_k_line(symbol_value, period_value, 11)
    k_line_0_close = k_line[0]['close']
    price_low = price_max * (1 - down_perscent)
    price_min = price_buy * (1 - down_perscent)
    print('price_buy = %s' % price_buy)
    print('price_max = %s' % price_max)
    print('price_low = %s' % price_low)
    print('price_min = %s' % price_min)
    print('close = %s' % k_line_0_close)
    condition1 = k_line_0_close < k_line[0]['open']#阴线
    print('阴线 = %s' % condition1)
    if k_line_0_close > price_max:
        misc.setConfigKeyValue('config.ini', symbol_value, 'price_max', k_line_0_close)
        price_max = k_line_0_close
    if price_min > k_line_0_close:
        return True and condition1
    if price_low > k_line_0_close and k_line_0_close > price_buy * (1 + 0.01):
        return True and condition1
    else:
        return False

def main(symbol_value):
    print(misc.getTimeStr())
    print(symbol_value)
    operationType = misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'type')
    buy_signal = int(misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'buy_signal'))
    sell_signal = int(misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'sell_signal'))
    buy_signal_max = int(misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'buy_signal_max'))
    sell_signal_max = int(misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'sell_signal_max'))
    condition = operationType == 'sell'
    order_id = None
    if condition:#买入判断
        condition1, condition2, condition3 = get_buy_condition(symbol_value)
        if condition1 and condition2 and condition3:
            print('买入信号+1')
            buy_signal = buy_signal + 1
            misc.setConfigKeyValue('config.ini', symbol_value, 'buy_signal', buy_signal)
        else:
            misc.setConfigKeyValue('config.ini', symbol_value, 'buy_signal', 0)
    else:#卖出判断
        condition = get_sell_condition(symbol_value)
        if condition:
            print('卖出信号+1')
            sell_signal = sell_signal + 1
            misc.setConfigKeyValue('config.ini', symbol_value, 'sell_signal', sell_signal)
        else:
            misc.setConfigKeyValue('config.ini', symbol_value, 'sell_signal', 0)

    if buy_signal >= buy_signal_max:
        #买入操作
        amount = misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'money_value')
        #amount = api.get_balance(account_id, money_name)
        order_id = api.do_place(account_id, amount, symbol_value, 'buy-market')
        misc.setConfigKeyValue('config.ini', symbol_value, 'buy_signal', 0)
        
    if sell_signal >= sell_signal_max:
        #卖出操作
        coin_name = misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'coin_name')
        amount = api.get_balance(account_id, coin_name)
        order_id = api.do_place(account_id, amount, symbol_value, 'sell-market')
        misc.setConfigKeyValue('config.ini', symbol_value, 'sell_signal', 0)
        
    if order_id:
        time.sleep(2)
        order_detail = api.get_order_detail(order_id)[0]
        if order_detail['type'] == 'buy-market':
            misc.setConfigKeyValue('config.ini', symbol_value, 'type', 'buy')
            misc.setConfigKeyValue('config.ini', symbol_value, 'price_buy', order_detail['price'])
            misc.setConfigKeyValue('config.ini', symbol_value, 'price_max', order_detail['price'])
            coin_value = misc.get_float_str(str(float(order_detail['filled-amount']) - float(order_detail['filled-fees'])))
            misc.setConfigKeyValue('config.ini', symbol_value, 'coin_value', coin_value)
        if order_detail['type'] == 'sell-market':
            misc.setConfigKeyValue('config.ini', symbol_value, 'type', 'sell')
            misc.setConfigKeyValue('config.ini', symbol_value, 'price_sell', order_detail['price'])
            money_value = misc.get_float_str(str(float(order_detail['filled-amount']) - float(order_detail['filled-fees'])))
            misc.setConfigKeyValue('config.ini', symbol_value, 'money_value', money_value)
        content='<html>'
        if order_detail['type'] == 'sell-market':
            price_buy = float(misc.getConfigKeyValueByKeyName('config.ini',symbol_value,'price_buy'))
            price_sell = float(misc.getConfigKeyValueByKeyName('config.ini', symbol_value,'price_sell'))
            content+='<p>盈亏=%.4f%%</p>' % ((price_sell / price_buy - 1 - 0.005) * 100)
        content+='<p>created-at(交易时间)=%s</p>' % misc.getTimeStrWithUnixTimestamp(int(order_detail['created-at']/1000))
        content+='<p>symbol(交易对)=%s</p>' % order_detail['symbol']
        content+='<p>price(成交价格)=%s</p>' % order_detail['price']
        #content+='<p>filled-amount(订单数量)=%s</p>' % order_detail['filled-amount']
        #content+='<p>filled-fees(已成交手续费)=%s</p>' % order_detail['filled-fees']
        content+='<p>type(订单类型)=%s</p>' % order_detail['type']
        content+='<p>%s</p>' % str(order_detail)
        content+='</html>'
        misc.sendEmail(mail_host, mail_user, mail_pass, receivers, '%s_%s_transaction_report' % (symbol_value, order_detail['type']), content)


#交易对
symbol_value_list = ['bccbtc','ethbtc','ltcbtc','dashbtc','etcbtc']
account_id = api.get_account_id()
down_perscent = float(misc.getConfigKeyValueByKeyName('config.ini', 'config', 'down_perscent'))
for symbol_value in symbol_value_list:
    misc.setConfigKeyValue('config.ini', symbol_value, 'buy_signal', '0')
    misc.setConfigKeyValue('config.ini', symbol_value, 'sell_signal', '0')
while True:
    try:
        for symbol_value in symbol_value_list:
            main(symbol_value)
            print()
        time.sleep(60)
    except Exception as e:
        print(e)
    except ApiError as e:
        print(e)
    except ApiNetworkError as e:
        print(e)
