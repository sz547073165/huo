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
symbol_value = 'btcusdt'
money_name = 'usdt'
coin_name = 'btc'
period_value = '60min'
account_id = api.get_account_id()
global buy_signal
global sell_signal
buy_signal = 0
sell_signal = 0
buy_signal_max = 3
sell_signal_max = 3
up_point = 1.01654
down_point = 0.99487929#0.991728

def get_buy_condition():
    k_line = api.get_k_line(symbol_value, period_value, 8)
    k_line_1_id = k_line[1]['id']
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
    return k_line_1_id, ma_line, slope_list, condition1, condition2, condition3

def get_sell_condition():
    k_line = api.get_k_line(symbol_value, period_value, 11)
    k_line_0_close = k_line[0]['close']
    condition1 = k_line_0_close < k_line[0]['open']#阴线
    k_line_1_close = k_line[1]['close']
    k_line_1_time = k_line[1]['id']
    k_line_time = int(misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'k_line_time'))
    x_value = (k_line_1_time - k_line_time) / 60 /60
    k_value = float(misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'k_value'))
    b_value = float(misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'b_value'))
    y_value = k_value * x_value + b_value
    if(k_line_1_close > y_value * up_point and x_value > 0):
        y_value_repair =y_value + (k_line_1_close - y_value) / 10
        k_value_repair = (y_value_repair - b_value) / x_value
        print('原始k k_value=%s' % k_value)
        print('斜率k修正 k_value_repair=%s' % k_value_repair)
        misc.setConfigKeyValue('config.ini', symbol_value, 'k_value', str(k_value_repair))
        #return False and condition1
    k_value = float(misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'k_value'))
    x_value = x_value + 1
    y_value = k_value * x_value + b_value
    print('k_line_1时间 x=%s' % x_value)
    print('直线斜率 k=%s' % k_value)
    print('常数项 b=%s' % b_value)
    print('理想市价 y=%s' % y_value)
    print('实际市价 close=%s' % k_line_0_close)
    if(k_line_0_close < y_value * down_point):
        return True and condition1
    else:
        return False and condition1
    
def main():
    print(misc.getTimeStr())
    operationType = misc.getConfigKeyValueByKeyName('config.ini', symbol_value, 'type')
    condition = operationType == 'sell'
    global buy_signal
    global sell_signal
    order_id = None
    if condition:#买入判断
        k_line_1_id, ma_line, slope_list, condition1, condition2, condition3 = get_buy_condition()
        if condition1 and condition2 and condition3:
            print('买入信号+1')
            buy_signal = buy_signal + 1
        else:
            buy_signal = 0
    else:#卖出判断
        condition = get_sell_condition()
        if condition:
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
            misc.setConfigKeyValue('config.ini', symbol_value, 'price_buy', order_detail['price'])
            misc.setConfigKeyValue('config.ini', symbol_value, 'b_value', float(order_detail['price'])-ma_line[0]-ma_line[1])
            misc.setConfigKeyValue('config.ini', symbol_value, 'k_value', ma_line[0]-ma_line[1])
            misc.setConfigKeyValue('config.ini', symbol_value, 'k_line_time', k_line_1_id)
        if order_detail['type'] == 'sell-market':
            misc.setConfigKeyValue('config.ini', symbol_value, 'type', 'sell')
            misc.setConfigKeyValue('config.ini', symbol_value, 'price_sell', order_detail['price'])
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
        content+='<p>type(订单类型（buy-market：市价买, sell-market：市价卖）)=%s</p>' % order_detail['type']
        content+='<p>%s</p>' % str(order_detail)
        content+='</html>'
        misc.sendEmail(mail_host, mail_user, mail_pass, receivers, '%s_%s_交易报告' % (symbol_value, order_detail['type']), content)

while True:
    try:
        main()
        print()
        time.sleep(60)
    except Exception as e:
         print(e)



        
    