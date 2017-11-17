#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 13:01:33 2017

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
    k_line = api.get_k_line(symbol_value, '15min', 10)
    last_close_value = k_line[0]['close']
    ma_line = api.get_ma_line(k_line, 5)
    last_ma_value = ma_line[0]
    slope_list = api.get_slope_line(ma_line)
    slope_sum = 0
    for slope in slope_list:
        slope_sum = slope_sum + slope
    slope_sum = round(slope_sum, 4)
    
    condition1 = operationType == 'sell'
    condition2 = last_close_value > last_ma_value #true为买入机会，false为卖出机会
    condition3 = slope_sum > 0 #true为斜率之和大于0，目前趋势向上，反之向下
    condition4 = abs(slope_sum) > (float(last_close_value) * 0.0075) #true为波动幅度大于市价的100.75%，波动幅度较大，非横盘震荡、谷底、山顶
    print('均线 =',last_ma_value,'\n市价 =',last_close_value,'\n斜率之和 =',slope_sum,'\n斜率波动幅度要求 = ',round((float(last_close_value) * 0.0075)))
    print('最后一次操作为卖出 =',condition1,'\n市价高于均线 =',condition2,'\n斜率之和大于0 =',condition3,'\n波动幅度足够大 =', condition4)
    return condition1, condition2, condition3, condition4

def main():
    print(misc.getTimeStr())
    
    condition1, condition2, condition3, condition4 = get_condition()
    order_id = None
    
    global buy_signal
    global sell_signal
    if condition1 and condition2 and condition4:
        print('买入信号+1')
        buy_signal = buy_signal + 1
    else:
        buy_signal = 0
    
    if not condition1 and not condition2 and condition4:
        print('卖出信号+1')
        sell_signal = sell_signal + 1
    else:
        sell_signal = 0
    
    if buy_signal >= buy_signal_max:
        #买入操作
        amount = misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'usdt')
        order_id = api.do_place(account_id, amount, symbol_value, 'buy-market')
        buy_signal = 0
    
    if sell_signal >= sell_signal_max:
        #卖出操作
        amount = api.get_balance(account_id, coin_name)
        order_id = api.do_place(account_id, amount, symbol_value, 'sell-market')
        sell_signal = 0
        
    if order_id:
        time.sleep(10)
        order_detail = api.get_order_detail(order_id)[0]
        content='<html>'
        content+='<p>symbol(交易对)=%s</p>' % order_detail['symbol']
        content+='<p>price(成交价格)=%s</p>' % order_detail['price']
        content+='<p>filled-amount(订单数量)=%s</p>' % order_detail['filled-amount']
        content+='<p>filled-fees(已成交手续费)=%s</p>' % order_detail['filled-fees']
        content+='<p>type(订单类型（buy-market：市价买, sell-market：市价卖）)=%s</p>' % order_detail['type']
        content+='<p>created-at(交易时间)=%s</p>' % misc.getTimeStrWithUnixTimestamp(int(order_detail['created-at'][0:10]))
        content+='<p>%s</p>' % str(order_detail)
        content+='</html>'
        misc.sendEmail(mail_host, mail_user, mail_pass, receivers, '%s_%s_交易报告' % (symbol_value, order_detail['type']), content)
        if order_detail['type'] == 'buy-market':
            misc.setConfigKeyValue('config.ini', symbol_value, 'type', 'buy')
        if order_detail['type'] == 'sell-market':
            misc.setConfigKeyValue('config.ini', symbol_value, 'type', 'sell')
            usdt = misc.get_float_str(float(order_detail['filled-amount']) - float(order_detail['filled-fees']))
            misc.setConfigKeyValue('config.ini',symbol_value,'usdt',usdt)
        
while True:
    try:
        main()
        print()
        time.sleep(15)
    except Exception as e:
         print(e)


