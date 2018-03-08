import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from plotly.graph_objs import *
import huo_bi_api as api
import misc
import numpy as np
import datetime

app = dash.Dash()

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Graph(id='btcusdt'),
        ], className='-'),
        dcc.Interval(id='btcusdt-update', interval=60 * 60 * 1000, n_intervals=0),
    ], className='-'),
    html.Div([
        html.Div([
            dcc.Graph(id='bchusdt'),
        ], className='-'),
        dcc.Interval(id='bchusdt-update', interval=60 * 60 * 1000, n_intervals=0),
    ], className='-'),
    html.Div([
        html.Div([
            dcc.Graph(id='ethusdt'),
        ], className='-'),
        dcc.Interval(id='ethusdt-update', interval=60 * 60 * 1000, n_intervals=0),
    ], className='-'),
    html.Div([
        html.Div([
            dcc.Graph(id='etcusdt'),
        ], className='-'),
        dcc.Interval(id='etcusdt-update', interval=60 * 60 * 1000, n_intervals=0),
    ], className='-'),
    html.Div([
        html.Div([
            dcc.Graph(id='ltcusdt'),
        ], className='-'),
        dcc.Interval(id='ltcusdt-update', interval=60 * 60 * 1000, n_intervals=0),
    ], className='-'),
    html.Div([
        html.Div([
            dcc.Graph(id='eosusdt'),
        ], className='-'),
        dcc.Interval(id='eosusdt-update', interval=60 * 60 * 1000, n_intervals=0),
    ], className='-'),
    html.Div([
        html.Div([
            dcc.Graph(id='xrpusdt'),
        ], className='-'),
        dcc.Interval(id='xrpusdt-update', interval=60 * 60 * 1000, n_intervals=0),
    ], className='-'),
    html.Div([
        html.Div([
            dcc.Graph(id='dashusdt'),
        ], className='-'),
        dcc.Interval(id='dashusdt-update', interval=60 * 60 * 1000, n_intervals=0),
    ], className='-'),
    html.Div([
        html.Div([
            dcc.Graph(id='htusdt'),
        ], className='-'),
        dcc.Interval(id='htusdt-update', interval=60 * 60 * 1000, n_intervals=0),
    ], className='-')
], style={'padding': '0px 10px 15px 10px',
          'marginLeft': 'auto', 'marginRight': 'auto', "width": "900px",
          'boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)'})

@app.callback(Output(component_id='btcusdt',component_property='figure'),
              [Input(component_id='btcusdt-update',component_property='n_intervals')])
def update_btcusdt(n_intervals):
    return base_fun('btcusdt')

@app.callback(Output(component_id='bchusdt',component_property='figure'),
              [Input(component_id='bchusdt-update',component_property='n_intervals')])
def update_btcusdt(n_intervals):
    return base_fun('bchusdt',j=10)

@app.callback(Output(component_id='ethusdt',component_property='figure'),
              [Input(component_id='ethusdt-update',component_property='n_intervals')])
def update_btcusdt(n_intervals):
    return base_fun('ethusdt',j=10)

@app.callback(Output(component_id='etcusdt',component_property='figure'),
              [Input(component_id='etcusdt-update',component_property='n_intervals')])
def update_btcusdt(n_intervals):
    return base_fun('etcusdt',j=0.1)

@app.callback(Output(component_id='ltcusdt',component_property='figure'),
              [Input(component_id='ltcusdt-update',component_property='n_intervals')])
def update_etcusdt(n_intervals):
    return base_fun('ltcusdt',j=1)

@app.callback(Output(component_id='eosusdt',component_property='figure'),
              [Input(component_id='eosusdt-update',component_property='n_intervals')])
def update_btcusdt(n_intervals):
    return base_fun('eosusdt',j=0.1)

@app.callback(Output(component_id='xrpusdt',component_property='figure'),
              [Input(component_id='xrpusdt-update',component_property='n_intervals')])
def update_btcusdt(n_intervals):
    return base_fun('xrpusdt',j=0.01)

@app.callback(Output(component_id='dashusdt',component_property='figure'),
              [Input(component_id='dashusdt-update',component_property='n_intervals')])
def update_btcusdt(n_intervals):
    return base_fun('dashusdt',j=10)

@app.callback(Output(component_id='htusdt',component_property='figure'),
              [Input(component_id='htusdt-update',component_property='n_intervals')])
def update_etcusdt(n_intervals):
    return base_fun('htusdt',j=0.01)

def base_fun(symbol_value,period_value='1day',n=20,j=100):
    k_line = api.get_k_line(symbol_value, period_value, 200)

    roc_list = []
    time_list = []
    close_list = []
    ma_list = []

    for index in np.arange(0, len(k_line) - n):
        roc = (k_line[index].close - k_line[index + n].close) / k_line[index + n].close * 100
        roc_list.append(roc * j)

    # print(roc_list[::-1])

    for index in np.arange(0, len(k_line) - n):
        timestamp = k_line[index].id
        temp = datetime.datetime.fromtimestamp(timestamp + 8 * 3600)
        # time_list.append(time.strftime("%Y-%m-%d %H:%M:%S", temp))
        time_list.append(temp)

    # print(time_list[::-1])

    for index in np.arange(0, len(k_line) - n):
        close_list.append(k_line[index].close)

    # print(close_list)

    for index in np.arange(0, len(k_line) - n):
        ma_list.append(misc.getMALine(k_line, n)[index])
    # 收盘价
    close = Scatter(x=time_list[::-1], y=close_list[::-1], name="收盘价")
    # 均线
    ma = Scatter(x=time_list[::-1], y=ma_list[::-1], name="均线({})".format(n))
    # roc线
    roc = Scatter(x=time_list[::-1], y=roc_list[::-1], name="roc({})".format(n))

    layout = Layout(xaxis=dict(
        range=[time_list[-1].timestamp() * 1000,
               time_list[0].timestamp() * 1000]),
        title=symbol_value)

    return Figure(data=[close, ma, roc], layout=layout)

if __name__ == '__main__':
    app.run_server()