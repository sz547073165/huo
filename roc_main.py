# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 13:42:27 2018

@author: Administrator
"""

import huo_bi_api as api
import misc
import datetime
from person import mailPass as mail_pass
import numpy as np

mail_host = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'mailHost')
mail_user = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'mailUser')
receivers = misc.getConfigKeyValueByKeyName('config.ini', 'mail', 'receivers').split(',')

#交易对
symbol_value = 'btcusdt'
money_name = 'usdt'
coin_name = 'btc'
period_value = '1day' #60min/1day
n = 20 #回看时间窗口
j = 100 #缩小倍数

k_line = api.get_k_line(symbol_value,period_value,200)

roc_list = []
time_list = []
close_list = []
ma_list = []

for index in np.arange(0,len(k_line) - n):
    roc = (k_line[index].close - k_line[index + n].close) / k_line[index + n].close * 100
    roc_list.append(roc)

#print(roc_list[::-1])

for index in np.arange(0,len(k_line) - n):
    timestamp = k_line[index].id
    temp = datetime.datetime.fromtimestamp(timestamp + 8 * 3600)
    #time_list.append(time.strftime("%Y-%m-%d %H:%M:%S", temp))
    time_list.append(temp)

#print(time_list[::-1])

for index in np.arange(0,len(k_line) - n):
    close_list.append(k_line[index].close / j)

#print(close_list)

for index in np.arange(0,len(k_line) - n):
    ma_list.append(misc.getMALine(k_line,n)[index] / j)

#绘制
import plotly
import plotly.graph_objs as go
#roc线
roc = go.Scatter(x=time_list[::-1],y=roc_list[::-1],name="roc({})".format(n))
#收盘价
close = go.Scatter(x=time_list[::-1],y=close_list[::-1],name="收盘价")
#均线
ma = go.Scatter(x=time_list[::-1],y=ma_list[::-1],name="均线({})".format(n))

data = [close, roc, ma]
layout = go.Layout(xaxis = dict(
                   range = [time_list[-1].timestamp() * 1000,
                            time_list[0].timestamp() * 1000]),
                    title=symbol_value)
fig = go.Figure(data = data, layout = layout)
plotly.offline.plot(fig)


