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
period_value = '1day' #60min

k_line = api.get_k_line(symbol_value,period_value,200)

roc_list = []
time_list = []
n = 14
for index in np.arange(0,len(k_line) - n):
    roc = (k_line[index].close - k_line[index + n].close) / k_line[index + n].close * 100
    roc_list.append(roc)

print(roc_list[::-1])

for index in np.arange(0,len(k_line) - n):
    timestamp = k_line[index].id
    temp = datetime.datetime.fromtimestamp(timestamp + 8 * 3600)
    #time_list.append(time.strftime("%Y-%m-%d %H:%M:%S", temp))
    time_list.append(temp)

print(time_list[::-1])

'''
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange

fig = plt.figure()  
axes = fig.add_subplot(1,1,1)
    
startDate = time_list[-1]
endDate = time_list[0]
# 设置日期的间隔
delta = datetime.timedelta(hours=1)
# 生成一个matplotlib可以识别的日期对象
dates = drange(startDate , endDate, delta)
# 使用plot_date绘制日期图像
axes.plot_date(dates,  roc_list[::-1],  'm-',  marker='.',  linewidth=1)
# 设置日期的显示格式
axes.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))
# 日期的排列根据图像的大小自适应
fig.autofmt_xdate()

plt.show()
'''

import plotly
import plotly.graph_objs as go

data = [go.Scatter(x=time_list[::-1],y=roc_list[::-1])]
layout = go.Layout(xaxis = dict(
                   range = [time_list[-1].timestamp() * 1000,
                            time_list[0].timestamp() * 1000]),
                    title="btc-usdt roc")
fig = go.Figure(data = data, layout = layout)
plotly.offline.plot(fig)


