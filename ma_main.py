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
symbol_value = 'bccbtc'
money_name = 'btc'
coin_name = 'bcc'
period_value = '15min'
account_id = api.get_account_id()
global buy_signal
global sell_signal
buy_signal = 0
sell_signal = 0
buy_signal_max = 4
sell_signal_max = 8

def get_condition():
    operationType = misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'type')
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
    slope_sum_last = slope_list[0] + slope_list[1]# + slope_list[2]
    slope_sum_early = slope_list[3] + slope_list[2]# + slope_list[5]
    
    condition1 = operationType == 'sell'
    condition2 = last_close_value > last_ma_value #true为买入机会，false为卖出机会
    condition3 = slope_sum > 0 #true为斜率之和大于0，目前趋势向上，反之向下
    time_value = 0.0190
    condition4 = abs(slope_sum) > (float(last_close_value) * time_value) #true为波动幅度大于市价的100.75%，波动幅度较大，非横盘震荡、谷底、山顶
    condition5 = slope_sum_last > slope_sum_early#斜率后半段大于前半段
    condition6 = last_close_value > k_line[0]['open'] #true收盘价大于开盘价，阳线
    condition7 = slope_sum_last > 0 and condition5 #斜率后半段为正
    print('均线 = %s' % last_ma_value)
    print('市价 = %s' % last_close_value)
    print('斜率之和 = %s' % slope_sum)
    print('斜率之和（前半段） = %s' % slope_sum_early)
    print('斜率之和（后半段） = %s' % slope_sum_last)
    print('斜率波动幅度要求 = %s' % (last_close_value * time_value))
    print('1-最后一次操作为卖出 = %s' % condition1)
    print('2-市价高于均线 = %s' % condition2)
    print('3-斜率之和大于0 = %s' % condition3)
    print('4-波动幅度足够大 = %s' % condition4)
    print('5-后半段斜率之和大于前半段三斜率之和 = %s' % condition5)
    print('7-后半段斜率之和大于0 = %s' % condition7)
    print('6-是否阳线 = %s' % condition6)
    return condition1, condition2, condition3, condition4, condition5, condition6, condition7

def main():
    print(misc.getTimeStr())
    
    condition1, condition2, condition3, condition4, condition5, condition6, condition7 = get_condition()
    order_id = None
    
    global buy_signal
    global sell_signal
    if condition1 and condition2 and ((condition3 and condition4) or (not condition4 and condition7)) and condition6:
        print('买入信号+1')
        buy_signal = buy_signal + 1
    else:
        buy_signal = 0
    
    if not condition1 and not condition2 and not condition5: #(condition4 or (not condition4 and not condition5)):
        print('卖出信号+1')
        sell_signal = sell_signal + 1
    else:
        sell_signal = 0
    
    if buy_signal >= buy_signal_max:
        #买入操作
        #amount = misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'usdt')
        amount = api.get_balance(account_id, money_name)
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
        if order_detail['type'] == 'buy-market':
            misc.setConfigKeyValue('config.ini', symbol_value, 'type', 'buy')
        if order_detail['type'] == 'sell-market':
            misc.setConfigKeyValue('config.ini', symbol_value, 'type', 'sell')
        content='<html>'
        content+='<p>symbol(交易对)=%s</p>' % order_detail['symbol']
        content+='<p>price(成交价格)=%s</p>' % order_detail['price']
        content+='<p>filled-amount(订单数量)=%s</p>' % order_detail['filled-amount']
        content+='<p>filled-fees(已成交手续费)=%s</p>' % order_detail['filled-fees']
        content+='<p>type(订单类型（buy-market：市价买, sell-market：市价卖）)=%s</p>' % order_detail['type']
        content+='<p>created-at(交易时间)=%s</p>' % misc.getTimeStrWithUnixTimestamp(int(order_detail['created-at']/1000))
        content+='<p>%s</p>' % str(order_detail)
        content+='<p>1-最后一次操作为卖出 = %s</p>' % condition1
        content+='<p>2-市价高于均线 = %s</p>' % condition2
        content+='<p>3-斜率之和大于0 = %s</p>' % condition3
        content+='<p>4-波动幅度足够大 = %s</p>' % condition4
        content+='<p>5-后半段斜率之和大于前半段三斜率之和 = %s</p>' % condition5
        content+='<p>7-后半段斜率之和大于0 = %s</p>' % condition7
        content+='<p>6-是否阳线 = %s</p>' % condition6
        content+='</html>'
        misc.sendEmail(mail_host, mail_user, mail_pass, receivers, '%s_%s_交易报告' % (symbol_value, order_detail['type']), content)
        
while True:
    try:
        main()
        print()
        time.sleep(15)
    except Exception as e:
         print(e)

#main()